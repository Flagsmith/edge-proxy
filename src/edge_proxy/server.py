from datetime import datetime, timedelta

import httpx
import structlog
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from edge_proxy.health_check.responses import HealthCheckResponse
from fastapi_utils.tasks import repeat_every

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
app = FastAPI()


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
    last_updated_at = environment_service.last_updated_at
    if not last_updated_at:
        return HealthCheckResponse(
            status_code=500,
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
                status_code=500,
                status="error",
                reason="environment document(s) stale.",
                last_successful_update=last_updated_at,
            )

    return HealthCheckResponse(last_successful_update=last_updated_at)


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


@app.on_event("startup")
@repeat_every(
    seconds=settings.api_poll_frequency_seconds,
    raise_exceptions=True,
    logger=structlog.get_logger(__name__),
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
