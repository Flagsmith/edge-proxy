from contextlib import suppress
from datetime import datetime

import sentry_sdk
from fastapi import FastAPI
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from flag_engine.engine import get_environment_feature_state
from flag_engine.engine import get_environment_feature_states
from flag_engine.engine import get_identity_feature_states
from flag_engine.environments.builders import build_environment_model
from flag_engine.identities.models import IdentityModel

from .cache import CacheService
from .models import IdentityWithTraits
from .schemas import APIFeatureStateSchema
from .schemas import APITraitSchema
from .sentry_sampler import traces_sampler
from .settings import Settings
from .sse import router as sse_router
from fastapi_utils.tasks import repeat_every

settings = Settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        debug=True,
        traces_sampler=traces_sampler,
        environment=settings.environment,
    )

app = FastAPI()
cache_service = CacheService(settings)

fs_schema = APIFeatureStateSchema()
trait_schema = APITraitSchema()


@app.get("/health", deprecated=True)
@app.get("/proxy/health")
def health_check():
    with suppress(TypeError):
        if (
            datetime.now() - cache_service.last_updated_at
        ).total_seconds() <= settings.api_poll_frequency:
            return {"status": "ok"}

    return JSONResponse(status_code=500, content={"status": "error"})


@app.get("/api/v1/flags/")
def flags(feature: str = None, x_environment_key: str = Header(None)):
    environment_document = cache_service.get_environment(x_environment_key)
    environment = build_environment_model(environment_document)

    if feature:
        feature_state = get_environment_feature_state(environment, feature)
        data = fs_schema.dump(feature_state)
    else:
        feature_states = get_environment_feature_states(environment)
        data = fs_schema.dump(feature_states, many=True)

    return data


def _get_fs_schema(identity_model: IdentityModel):
    return APIFeatureStateSchema(
        context={"identity_identifier": identity_model.identifier},
    )


@app.post("/api/v1/identities/")
def identity(
    input_data: IdentityWithTraits,
    x_environment_key: str = Header(None),
):
    environment_document = cache_service.get_environment(x_environment_key)
    environment = build_environment_model(environment_document)
    identity = IdentityModel(
        identifier=input_data.identifier, environment_api_key=x_environment_key
    )
    trait_models = trait_schema.load(input_data.dict()["traits"], many=True)
    fs_schema = _get_fs_schema(identity)
    flags = get_identity_feature_states(
        environment, identity, override_traits=trait_models
    )
    data = {
        "traits": trait_schema.dump(trait_models, many=True),
        "flags": fs_schema.dump(flags, many=True),
    }
    return data


@app.on_event("startup")
@repeat_every(seconds=settings.api_poll_frequency, raise_exceptions=True)
def refresh_cache():
    if settings.refresh_environment_cache:
        cache_service.refresh()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(sse_router)
