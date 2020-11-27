# pwgan-pytorch-serving

![Python](https://github.com/airenas/pwgan-pytorch-serving/workflows/Python/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/airenas/pwgan-pytorch-serving/badge.svg?branch=main)](https://coveralls.io/github/airenas/pwgan-pytorch-serving?branch=main) ![CodeQL](https://github.com/airenas/pwgan-pytorch-serving/workflows/CodeQL/badge.svg)

Serves [ParallelWaveGan](https://github.com/kan-bayashi/ParallelWaveGAN) Pytorch model. It packs the python code into a docker container for running pytorch on CPU/GPU. Input is a base64 encoded spectrogram: `{"data":"T5CE ...<truncated>... AAA=="}`. See [espnet-tts-serving](https://github.com/airenas/espnet-tts-serving). An output is a based64 encoded *wav* bytes: `{"data":"UklGR ...<truncated>... AAwA="}`.

See [deploy/cpu](deploy/cpu) or [deploy/gpu](deploy/gpu) for deployment and testing samples.

---

## License

Copyright © 2020, [Airenas Vaičiūnas](https://github.com/airenas).

Released under the [The 3-Clause BSD License](LICENSE).

---