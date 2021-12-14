import asyncio

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
async def calculate(data: api.Input, request: Request):
    if not data.data:
        raise HTTPException(status_code=400, detail="No spectrogram")
    if not data.voice:
        raise HTTPException(status_code=400, detail="No voice")

    app = request.app

    def calc():
        return app.calculate_func(data.data, data.voice, data.priority)

    res_data = await asyncio.get_event_loop().run_in_executor(app.http_executor, calc)
    res = api.Output(data=res_data)
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
async def get_info(request: Request):
    """Returns models info."""
    res = api.Info(models=request.app.get_info_func(), workers=request.app.config.workers)
    return res


@router.get("/live", tags=["service"], response_model=api.Live)
async def get_live(request: Request):
    """Returns service health state."""
    res = api.Live(ok=request.app.live)
    return res
