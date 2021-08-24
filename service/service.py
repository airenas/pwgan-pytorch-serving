import os

import requests
import urllib3
from service.metrics import MetricsKeeper
from fastapi import FastAPI
from fastapi.logger import logger

from service.pwgan.model import PWGANModel


def create_service():
    app = FastAPI(
        title="PWGAN Pytorch serving",
        version="0.2",
    )
    setup_prometheus(app)
    setup_requests(app)
    setup_routes(app)
    setup_vars(app)
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
    logger.info("Loading model")
    app.model_name = os.environ.get("MODEL_NAME", "checkpoint-700000steps.pkl")
    app.model_path = os.environ.get("MODEL_PATH", "/model")
    app.device = os.environ.get("DEVICE", "cpu")
    app.model_loaded = False


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
