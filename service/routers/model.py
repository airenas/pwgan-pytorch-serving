from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
def calculate(data: api.Input, request: Request):
    if not data.data:
        raise HTTPException(status_code=400, detail="No spectrogram")
    if not data.voice:
        raise HTTPException(status_code=400, detail="No voice")

    res_data = request.app.calculate_func(data.data, data.voice)
    res = api.Output(data=res_data)
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
def get_info(request: Request):
    """Returns models info."""
    res = api.Info(models=request.app.get_info_func(), workers=request.app.config.workers)
    return res


@router.get("/live", tags=["service"], response_model=api.Live)
def get_live(request: Request):
    """Returns service health state."""
    res = api.Live(ok=request.app.live)
    return res
