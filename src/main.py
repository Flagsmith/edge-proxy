import logging
from contextlib import suppress
from datetime import datetime
from cachetools.func import ttl_cache

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from flag_engine.engine import (
    get_environment_feature_state,
    get_environment_feature_states,
    get_identity_feature_states,
)
from flag_engine.environments.builders import build_environment_model
from flag_engine.identities.models import IdentityModel

from fastapi_utils.tasks import repeat_every

from .cache import CacheService
from .exceptions import FlagsmithUnknownKeyError
from .features import filter_out_server_key_only_feature_states
from .mappers import (
    map_feature_state_to_response_data,
    map_feature_states_to_response_data,
    map_traits_to_response_data,
)
from .models import IdentityWithTraits
from .settings import Settings
from .sse import router as sse_router

app = FastAPI()
settings = Settings()
cache_service = CacheService(settings)


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
        last_updated = datetime.now() - cache_service.last_updated_at
        buffer = 30 * len(settings.environment_key_pairs)  # 30s per environment
        if last_updated.total_seconds() <= settings.api_poll_frequency + buffer:
            return ORJSONResponse(status_code=200, content={"status": "ok"})

    return ORJSONResponse(status_code=500, content={"status": "error"})


@app.get("/api/v1/flags/", response_class=ORJSONResponse)
async def flags(feature: str = None, x_environment_key: str = Header(None)):
    return _get_flags_response_data(x_environment_key, feature)


@ttl_cache(ttl=settings.cache_ttl)
def _get_flags_response_data(environment_key: str, feature: str = None) -> ORJSONResponse:
    environment_document = cache_service.get_environment(environment_key)
    environment = build_environment_model(environment_document)

    if feature:
        feature_state = get_environment_feature_state(environment, feature)

        if not filter_out_server_key_only_feature_states(
            feature_states=[feature_state],
            environment=environment,
        ):
            return ORJSONResponse(
                status_code=404,
                content={
                    "status": "not_found",
                    "message": f"feature '{feature}' not found",
                },
            )

        data = map_feature_state_to_response_data(feature_state)

    else:
        feature_states = filter_out_server_key_only_feature_states(
            feature_states=get_environment_feature_states(environment),
            environment=environment,
        )
        data = map_feature_states_to_response_data(feature_states)

    return ORJSONResponse(data)


@app.post("/api/v1/identities/", response_class=ORJSONResponse)
async def identity(
    input_data: IdentityWithTraits,
    x_environment_key: str = Header(None),
):
    return _get_identity_response_data(input_data, x_environment_key)


@ttl_cache(maxsize=settings.cache_max_size, ttl=settings.cache_ttl)
def _get_identity_response_data(input_data: IdentityWithTraits, environment_key: str) -> ORJSONResponse:
    environment_document = cache_service.get_environment(environment_key)
    environment = build_environment_model(environment_document)
    identity = IdentityModel(
        identifier=input_data.identifier, environment_api_key=environment_key
    )
    trait_models = input_data.traits
    flags = filter_out_server_key_only_feature_states(
        feature_states=get_identity_feature_states(
            environment,
            identity,
            override_traits=trait_models,
        ),
        environment=environment,
    )
    data = {
        "traits": map_traits_to_response_data(trait_models),
        "flags": map_feature_states_to_response_data(
            flags,
            identity_hash_key=identity.composite_key,
        ),
    }
    return ORJSONResponse(data)


@app.on_event("startup")
@repeat_every(
    seconds=settings.api_poll_frequency,
    raise_exceptions=True,
    logger=logging.getLogger(__name__),
)
async def refresh_cache():
    await cache_service.refresh()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(sse_router)
