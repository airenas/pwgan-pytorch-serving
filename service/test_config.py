from service.api.api import ModelInfo
from service.config import Config


def extract_test(s):
    return "-> " + s.dir


def test_parse_one():
    c = Config(yaml_data="voices:\n  - name: olia\n    dir: /dir", device="cpu", extract_func=extract_test)

    assert len(c.voices) == 1
    assert c.get("olia").name == "olia"
    assert c.get("olia").dir == "/dir"
    assert c.get("olia").device == "cpu"
    assert c.get("olia").file == "-> /dir"


def test_parse_several():
    c = Config(
        yaml_data="voices:\n  - name: olia\n    dir: file.zip\n  - name: olia1\n    dir: file1.zip\n    device: cuda:1",
        device="cpu", extract_func=extract_test)

    assert len(c.voices) == 2
    assert c.get("olia").name == "olia"
    assert c.get("olia").dir == "file.zip"
    assert c.get("olia").device == "cpu"
    assert c.get("olia").file == "-> file.zip"

    assert c.get("olia1").name == "olia1"
    assert c.get("olia1").dir == "file1.zip"
    assert c.get("olia1").device == "cuda:1"
    assert c.get("olia1").file == "-> file1.zip"


def test_parse_device():
    c = Config(
        yaml_data="voices:\n  - name: olia\n    dir: file.zip\n    device: \"{{device}}\"",
        device="cuda:0", extract_func=extract_test)

    assert len(c.voices) == 1
    assert c.get("olia").device == "cuda:0"


def test_get_info():
    c = Config(
        yaml_data="voices:\n  - name: olia\n    dir: file.zip\n  - name: olia1\n    dir: file1.zip\n    device: cuda:1",
        device="cpu", extract_func=extract_test)

    assert c.get_info() == [ModelInfo(name='olia', device='cpu'), ModelInfo(name='olia1', device='cuda:1')]
