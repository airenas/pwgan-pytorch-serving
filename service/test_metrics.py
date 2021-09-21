import time

from prometheus_client import REGISTRY

from service.metrics import MetricsKeeper, ElapsedLogger


def test_metrics():
    metrics = MetricsKeeper()
    metrics.calc_metric.labels("test").observe(1)
    metrics.load_metric.labels("test").observe(2)
    assert REGISTRY.get_sample_value("pwgan_model_calc_seconds_sum", labels={"voice": "test"}) == 1
    assert REGISTRY.get_sample_value("pwgan_model_load_seconds_sum", labels={"voice": "test"}) == 2


def test_elapsed_logger():
    def func(msg: str, *args, **kwargs):
        assert msg.startswith("test: 0.1")

    with ElapsedLogger(func, "test"):
        time.sleep(0.1)
