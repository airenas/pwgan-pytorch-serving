import logging
import os

import requests
import urllib3
from fastapi import FastAPI

from service.config import AppConfig, Config
from service.metrics import MetricsKeeper
from service.pwgan.model import PWGANModel

logger = logging.getLogger(__name__)


def create_service():
    app = FastAPI(
        title="PWGAN Pytorch serving",
        version="0.3",
    )
    setup_vars(app)
    setup_config(app)
    setup_prometheus(app)
    setup_requests(app)
    setup_routes(app)
    setup_model(app)
    return app


def setup_prometheus(app):
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    app.add_middleware(PrometheusMiddleware, app_name="pwgan-pytorch-serving", group_paths=True, prefix="model")
    app.metrics = MetricsKeeper()
    app.add_route("/metrics", handle_metrics)


def setup_routes(app):
    """Register routes."""
    from service.routers import model
    app.include_router(model.router, prefix="")


def setup_vars(app):
    app.config = AppConfig()
    app.config.file = os.environ.get("CONFIG_FILE", "/models/config.yaml")
    app.config.device = os.environ.get("DEVICE", "cpu")
    app.config.device = os.environ.get("DEVICE", "cpu")
    app.config.workers = int(os.environ.get("WORKERS", "1"))
    if app.config.workers == 0:
        raise Exception("No workers configured env.WORKERS")
    app.live = False


def setup_config(app):
    with open(app.config.file, 'r') as data:
        app.voices = Config(data, app.config.device)
    app.get_info_func = app.voices.get_info


def setup_model(app):
    with app.metrics.load_metric.time():
        pwgan_model = PWGANModel(app.model_path, app.model_name, app.device)

    def calc(data, model):
        with app.metrics.calc_metric.time():
            return pwgan_model.calculate(data)

    app.calculate = calc
    app.model_loaded = True
    logger.info("Loaded")


def setup_requests(app):
    """Set up a session for making HTTP requests."""
    session = requests.Session()
    session.headers["Content-Type"] = "application/json"
    retry = urllib3.util.Retry(total=5, status=2, backoff_factor=0.3)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry)

    session.mount("http://", retry_adapter)

    app.requests = session
