import time

from prometheus_client import Summary


class MetricsKeeper:
    def __init__(self):
        self.load_metric = Summary('pwgan_model_load_seconds', 'The model load time')
        self.calc_metric = Summary('pwgan_model_calc_seconds', 'The model interference time')


class ElapsedLogger(object):
    def __init__(self, logger_func, msg):
        self.logger_func = logger_func
        self.msg = msg

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args, **kwargs):
        end = time.time()
        elapsed = (end - self.start)
        self.logger_func(self.msg + f": {elapsed:5f} s")
