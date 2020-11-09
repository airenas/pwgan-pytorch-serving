from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
async def calculate(data: api.Input, request: Request):
    if data.data == "":
        raise HTTPException(status_code=400, detail="No spectrogram")

    res_data = request.app.calculate(data.data, data.model)
    res = api.Output(data=res_data)
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
async def get_info(request: Request):
    """Returns models info."""
    res = api.Info(name=request.app.model_name, loaded=request.app.model_loaded)
    return res
