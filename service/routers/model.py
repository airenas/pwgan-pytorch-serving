import asyncio
import base64

import msgpack
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import Response

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
async def calculate(request: Request):
    try:
        data: api.Input = await decode_input(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not data.data:
        raise HTTPException(status_code=400, detail="No spectrogram")
    if not data.voice:
        raise HTTPException(status_code=400, detail="No voice")

    app = request.app

    def calc() -> bytes:
        return app.calculate_func(data.data, data.voice, data.priority)

    res_data: bytes = await asyncio.get_event_loop().run_in_executor(app.http_executor, calc)

    accept = request.headers.get("accept", "").lower()
    if "application/msgpack" in accept:
        res = api.OutputBin(data=res_data)
        packed = msgpack.packb(res.dict(), use_bin_type=True)
        return Response(content=packed, media_type="application/msgpack")

    encoded_data = base64.b64encode(res_data)
    res = api.Output(data=encoded_data.decode('ascii'))
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


async def decode_input(request: Request) -> api.Input:
    content_type = request.headers.get("content-type", "").lower()
    if "application/msgpack" in content_type:
        body = await request.body()
        unpacked = msgpack.unpackb(body, raw=False)
        return api.Input(**unpacked)
    else:
        json_data = await request.json()
        json_data["data"] = to_bytes(json_data.get("data", ""))
        return api.Input(**json_data)


def to_bytes(data):
    base64_bytes = data.encode('ascii')
    return base64.b64decode(base64_bytes)
