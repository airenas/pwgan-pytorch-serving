import base64
import io
import logging
import os
import time

import soundfile
import torch
import yaml
from parallel_wavegan.utils import load_model

from service.metrics import ElapsedLogger

logger = logging.getLogger(__name__)


def as_string(data, sampling_rate):
    buffer = io.BytesIO()
    soundfile.write(buffer, data, sampling_rate, "PCM_16", format="WAV")
    buffer.seek(0)
    encoded_data = base64.b64encode(buffer.read())
    return encoded_data.decode('ascii')


def to_bytes(data):
    base64_bytes = data.encode('ascii')
    return base64.b64decode(base64_bytes)


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
        spectrogram_bytes = to_bytes(data)
        y, rate = self.calculate_bytes(spectrogram_bytes)
        return as_string(y, rate)

    def calculate_bytes(self, spectrogram_bytes):
        with torch.no_grad():
            start = time.time()

            x = torch.load(io.BytesIO(spectrogram_bytes), map_location=self.device)
            y = self.vocoder.inference(x)
            if self.device.type != "cpu":
                torch.cuda.synchronize()

            voc_end = time.time()
            elapsed = (voc_end - start)
            logger.info(f"vocoder done: {elapsed:5f} s")

        audio_len = len(y) / self.config["sampling_rate"]
        rtf = elapsed / audio_len
        logger.info(f"RTF = {rtf:5f}")
        logger.info(f"Len = {audio_len:5f}")

        with ElapsedLogger(logger.info, "to numpy"):
            return y.cpu().numpy(), self.config["sampling_rate"]
