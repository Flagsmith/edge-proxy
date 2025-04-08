from datetime import datetime, timedelta
import asyncio

import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, Response

from edge_proxy.health_check.responses import HealthCheckResponse

from edge_proxy.cache import LocalMemEnvironmentsCache
from edge_proxy.environments import EnvironmentService
from edge_proxy.exceptions import FeatureNotFoundError, FlagsmithUnknownKeyError
from edge_proxy.logging import setup_logging
from edge_proxy.models import IdentityWithTraits
from edge_proxy.settings import get_settings

settings = get_settings()
setup_logging(settings.logging)
environment_service = EnvironmentService(
    LocalMemEnvironmentsCache(),
    httpx.AsyncClient(timeout=settings.api_poll_timeout_seconds),
    settings,
)


async def poll_environments():
    while True:
        await environment_service.refresh_environment_caches()
        await asyncio.sleep(settings.api_poll_frequency_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await environment_service.refresh_environment_caches()
    poll = asyncio.create_task(poll_environments())
    yield
    poll.cancel()


app = FastAPI(lifespan=lifespan)


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
@app.get("/proxy/health/readiness", response_class=ORJSONResponse)
async def health_check():
    last_updated_at = environment_service.last_updated_at
    if not last_updated_at:
        return HealthCheckResponse(
            status_code=503,
            status="error",
            reason="environment document(s) not updated.",
            last_successful_update=None,
        )

    grace_period = settings.health_check.environment_update_grace_period_seconds
    if grace_period is not None:
        buffer = grace_period * len(settings.environment_key_pairs)
        threshold = datetime.now() - timedelta(
            seconds=settings.api_poll_frequency_seconds + buffer
        )
        if last_updated_at < threshold:
            return HealthCheckResponse(
                status_code=503,
                status="error",
                reason="environment document(s) stale.",
                last_successful_update=last_updated_at,
            )

    return HealthCheckResponse(last_successful_update=last_updated_at)


@app.get("/proxy/health/liveness")
async def liveness_check():
    return Response(status_code=200)


@app.get("/api/v1/flags/", response_class=ORJSONResponse)
async def flags(feature: str = None, x_environment_key: str = Header(None)):
    try:
        data = environment_service.get_flags_response_data(x_environment_key, feature)
    except FeatureNotFoundError:
        return ORJSONResponse(
            status_code=404,
            content={
                "status": "not_found",
                "message": f"feature '{feature}' not found",
            },
        )

    return ORJSONResponse(data)


@app.post("/api/v1/identities/", response_class=ORJSONResponse)
async def identity(
    input_data: IdentityWithTraits,
    x_environment_key: str = Header(None),
):
    data = environment_service.get_identity_response_data(input_data, x_environment_key)
    return ORJSONResponse(data)


@app.get("/api/v1/identities/", response_class=ORJSONResponse)
async def get_identities(
    identifier: str,
    x_environment_key: str = Header(None),
) -> ORJSONResponse:
    data = environment_service.get_identity_response_data(
        IdentityWithTraits(identifier=identifier), x_environment_key
    )
    return ORJSONResponse(data)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
