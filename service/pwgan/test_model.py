import base64

import numpy as np

from service.pwgan import model


def test_as_string():
    res = model.as_string(np.random.rand(16000, 1), 16000)
    assert len(res) > 0
    data = res.encode('ascii')
    data = base64.b64decode(data)
    str = data[0:4].decode("ascii")
    assert str == "RIFF"
