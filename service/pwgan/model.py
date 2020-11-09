import base64
import io
import os
import time

import parallel_wavegan.models
import soundfile
import torch
import yaml
from fastapi.logger import logger


def as_string(data, sampling_rate):
    buffer = io.BytesIO()
    soundfile.write(buffer, data, sampling_rate, "PCM_16", format="WAV")
    buffer.seek(0)
    encoded_data = base64.b64encode(buffer.read())
    return encoded_data.decode('ascii')


class PWGANModel:
    def __init__(self, model_dir, name):
        logger.info("Model path: %s" % model_dir)
        logger.info("Model name: %s" % name)

        vocoder_conf = os.path.join(model_dir, "config.yml")
        model_path = os.path.join(model_dir, name)

        self.device = torch.device("cpu")
        with open(vocoder_conf) as f:
            self.config = yaml.load(f, Loader=yaml.Loader)
        vocoder_class = self.config.get("generator_type", "ParallelWaveGANGenerator")
        vocoder = getattr(parallel_wavegan.models, vocoder_class)(**self.config["generator_params"])
        vocoder.load_state_dict(torch.load(model_path, map_location="cpu")["model"]["generator"])
        vocoder.remove_weight_norm()
        self.vocoder = vocoder.eval().to(self.device)
        self.pad_fn = torch.nn.ReplicationPad1d(self.config["generator_params"].get("aux_context_window", 0))
        logger.info("Model loaded: %s" % model_path)

    def calculate(self, data):
        base64_bytes = data.encode('ascii')
        spectrogram_bytes = base64.b64decode(base64_bytes)

        with torch.no_grad():
            start = time.time()
            x = torch.load(io.BytesIO(spectrogram_bytes))
            c = self.pad_fn(x.unsqueeze(0).transpose(2, 1)).to(self.device)
            xx = (c,)
            z_size = (1, 1, (c.size(2) - sum(self.pad_fn.padding)) * self.config["hop_size"])
            z = torch.randn(z_size).to(self.device)
            xx = (z,) + xx
            y = self.vocoder(*xx).view(-1)
            voc_end = time.time()
            elapsed = (voc_end - start)
            logger.info(f"vocoder done: {elapsed:5f} s")
        audio_len = len(y) / self.config["sampling_rate"]
        rtf = elapsed / audio_len
        logger.info(f"RTF = {rtf:5f}")
        logger.info(f"Len = {audio_len:5f}")
        return as_string(y.cpu().numpy(), self.config["sampling_rate"])
