import logging
from contextlib import suppress
from datetime import datetime

import httpx
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from fastapi_utils.tasks import repeat_every

from .cache import LocalMemEnvironmentsCache
from .environments import EnvironmentService
from .exceptions import FlagsmithUnknownKeyError
from .models import IdentityWithTraits
from .settings import Settings
from .sse import router as sse_router

app = FastAPI()
settings = Settings()
environment_service = EnvironmentService(
    LocalMemEnvironmentsCache(),
    httpx.AsyncClient(timeout=settings.api_poll_timeout),
    settings
)


@app.exception_handler(FlagsmithUnknownKeyError)
async def unknown_key_error(request, exc):
    return ORJSONResponse(
        status_code=401,
        content={
            "status": "unauthorized",
            "message": f"unknown key {exc}",
        },
    )


@app.get("/health", response_class=ORJSONResponse, deprecated=True)
@app.get("/proxy/health", response_class=ORJSONResponse)
async def health_check():
    with suppress(TypeError):
        last_updated = datetime.now() - environment_service.last_updated_at
        buffer = 30 * len(settings.environment_key_pairs)  # 30s per environment
        if last_updated.total_seconds() <= settings.api_poll_frequency + buffer:
            return ORJSONResponse(status_code=200, content={"status": "ok"})

    return ORJSONResponse(status_code=500, content={"status": "error"})


@app.get("/api/v1/flags/", response_class=ORJSONResponse)
async def flags(feature: str = None, x_environment_key: str = Header(None)):
    return environment_service.get_flags_response_data(x_environment_key, feature)


@app.post("/api/v1/identities/", response_class=ORJSONResponse)
async def identity(
    input_data: IdentityWithTraits,
    x_environment_key: str = Header(None),
):
    return environment_service.get_identity_response_data(input_data, x_environment_key)


@app.on_event("startup")
@repeat_every(
    seconds=settings.api_poll_frequency,
    raise_exceptions=True,
    logger=logging.getLogger(__name__),
)
async def refresh_cache():
    await environment_service.refresh_environment_caches()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(sse_router)
