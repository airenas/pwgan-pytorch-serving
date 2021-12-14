import os
from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service import service
from service.api import api


def __test_get_info() -> List[api.ModelInfo]:
    return [api.ModelInfo(name="olia", device="cpu")]


def __test_calc(text, model, priority):
    assert text == "in text"
    assert model == "m"
    assert priority == 0
    return "olia"


def init_test_app():
    app = FastAPI()
    service.setup_vars(app)
    service.setup_requests(app)
    service.setup_routes(app)
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


def test_calculate_pass_priority():
    client, app = init_test_app()

    def calc(text, model, priority):
        assert priority == 10000
        return "olia"

    app.calculate_func = calc
    response = client.post("/model", json={"data": "in text", "voice": "m", "priority": 10000})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_environment():
    os.environ["CONFIG_FILE"] = "/m1/c.yaml"
    os.environ["DEVICE"] = "cuda"
    os.environ["WORKERS"] = "12"
    os.environ["HTTP_WORKERS"] = "20"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.config.file == "/m1/c.yaml"
    assert ta.config.device == "cuda"
    assert ta.config.workers == 12
    assert ta.config.http_workers == 20


def test_env_fail():
    os.environ["WORKERS"] = "0"
    try:
        ta = FastAPI()
        with pytest.raises(Exception):
            service.setup_vars(ta)
    finally:
        os.environ["WORKERS"] = "1"


def test_env_http_fail():
    os.environ["HTTP_WORKERS"] = "0"
    try:
        ta = FastAPI()
        with pytest.raises(Exception):
            service.setup_vars(ta)
    finally:
        os.environ["HTTP_WORKERS"] = "20"


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
