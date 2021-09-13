import os
from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service import service
from service.api import api


def __test_get_info() -> List[api.ModelInfo]:
    return [api.ModelInfo(name="olia", device="cpu")]


def __test_calc(text, model):
    assert text == "in text"
    assert model == "m"
    return "olia"


def init_test_app():
    app = FastAPI()
    service.setup_requests(app)
    service.setup_routes(app)
    service.setup_vars(app)
    client = TestClient(app)
    app.get_info_func = __test_get_info
    app.calculate_func = __test_calc
    return client, app


def test_read_main():
    client, _ = init_test_app()

    response = client.get("/")
    assert response.status_code == 404


def test_info():
    client, app = init_test_app()

    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'models': [{'device': 'cpu', 'name': 'olia'}], 'workers': 1}

    app.config.workers = 2
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'models': [{'device': 'cpu', 'name': 'olia'}], 'workers': 2}


def test_calculate_fail():
    client, _ = init_test_app()
    response = client.get("/model")
    assert response.status_code == 405

    response = client.post("/model", json={"olia": "olia"})
    assert response.status_code == 422


def test_calculate_fail_empty():
    client, _ = init_test_app()
    response = client.post("/model", json={"data": "", "voice": "a"})
    assert response.status_code == 400
    response = client.post("/model", json={"data": "data", "voice": ""})
    assert response.status_code == 400


def test_calculate():
    client, _ = init_test_app()
    response = client.post("/model", json={"data": "in text", "voice": "m"})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_environment():
    os.environ["CONFIG_FILE"] = "/m1/c.yaml"
    os.environ["DEVICE"] = "cuda"
    os.environ["WORKERS"] = "12"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.config.file == "/m1/c.yaml"
    assert ta.config.device == "cuda"
    assert ta.config.workers == 12


def test_env_fail():
    os.environ["WORKERS"] = "0"
    try:
        ta = FastAPI()
        with pytest.raises(Exception):
            service.setup_vars(ta)
    finally:
        os.environ["WORKERS"] = "1"


def test_live():
    client, app = init_test_app()

    app.live = True
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {'ok': True}

    app.live = False
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {'ok': False}
