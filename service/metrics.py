from prometheus_client import Summary


class MetricsKeeper:
    def __init__(self):
        self.load_metric = Summary('pwgan_model_load_seconds', 'The model load time')
        self.calc_metric = Summary('pwgan_model_calc_seconds', 'The model interference time')
