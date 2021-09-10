import logging
import os
from typing import List

import yaml

from service.api.api import ModelInfo

logger = logging.getLogger(__name__)


class AppConfig:
    pass


def _load_yaml(stream):
    return yaml.safe_load(stream)


def _find_pkl(_dir: str) -> str:
    res = ""
    for file in os.listdir(_dir):
        if file.endswith(".pkl"):
            if res:
                logger.warning("Several .pkl files in %s" % _dir)
            res = file
    if not res:
        raise Exception("No pkl file in %s" % _dir)
    logger.info("Found %s in %s" % (res, _dir))
    return res


def _find_file(c) -> str:
    if c.file:
        return c.file
    return _find_pkl(c.dir)


class VoiceConfig:
    def __init__(self, name, device, _dir, file):
        self.name = name
        self.device = device
        self.dir = _dir
        self.file = file


def parse(data_loaded, def_device="cpu") -> dict:
    res = dict()
    for c in data_loaded["voices"]:
        vc = VoiceConfig(c["name"], c.get("device"), c.get("dir"), c.get("file"))
        if not vc.device:
            vc.device = def_device
        vc.device = vc.device.replace("{{device}}", def_device)
        res[c["name"]] = vc
    return res


class Config:
    def __init__(self, yaml_data, device="cpu", extract_func=_find_file):
        data = _load_yaml(yaml_data)
        self.voices = parse(data, device)
        for k in self.voices:
            vc = self.voices[k]
            vc.file = extract_func(vc)

    def get(self, name) -> VoiceConfig:
        return self.voices.get(name)

    def get_info(self) -> List[ModelInfo]:
        res = list()
        for k in self.voices:
            vc = self.voices[k]
            res.append(ModelInfo(name=vc.name, device=vc.device))
        return res
