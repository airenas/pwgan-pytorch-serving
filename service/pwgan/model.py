import base64
import io
import os
import time

import soundfile
import torch
import yaml
from fastapi.logger import logger
from parallel_wavegan.utils import load_model


def as_string(data, sampling_rate):
    buffer = io.BytesIO()
    soundfile.write(buffer, data, sampling_rate, "PCM_16", format="WAV")
    buffer.seek(0)
    encoded_data = base64.b64encode(buffer.read())
    return encoded_data.decode('ascii')


class PWGANModel:
    def __init__(self, model_dir, name, device):
        logger.info("Model path: %s" % model_dir)
        logger.info("Model name: %s" % name)
        logger.info("Device    : %s" % device)

        vocoder_conf = os.path.join(model_dir, "config.yml")
        model_path = os.path.join(model_dir, name)
        with open(vocoder_conf) as f:
            self.config = yaml.load(f, Loader=yaml.Loader)
        self.device = torch.device(device)
        self.vocoder = load_model(model_path).to(device).eval()
        logger.info("Model loaded: %s" % model_path)

    def calculate(self, data):
        base64_bytes = data.encode('ascii')
        spectrogram_bytes = base64.b64decode(base64_bytes)

        with torch.no_grad():
            start = time.time()

            x = torch.load(io.BytesIO(spectrogram_bytes))
            y = self.vocoder.inference(x)

            voc_end = time.time()
            elapsed = (voc_end - start)
            logger.info(f"vocoder done: {elapsed:5f} s")

        audio_len = len(y) / self.config["sampling_rate"]
        rtf = elapsed / audio_len
        logger.info(f"RTF = {rtf:5f}")
        logger.info(f"Len = {audio_len:5f}")

        return as_string(y.cpu().numpy(), self.config["sampling_rate"])
