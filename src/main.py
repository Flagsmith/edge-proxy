import os

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from flag_engine.engine import (
    get_environment_feature_state,
    get_environment_feature_states,
    get_identity_feature_states,
)
from flag_engine.environments.builders import build_environment_model
from flag_engine.identities.models import IdentityModel

from .cache import CacheService
from .models import IdentityWithTraits
from .schemas import APIFeatureStateSchema, APITraitSchema
from .utils.tasks import repeat_every

fs_schema = APIFeatureStateSchema(exclude=["multivariate_feature_state_values"])
app = FastAPI()
cache_service = CacheService(
    api_url=os.environ.get("FLAGSMITH_API_URL"),
    api_token=os.environ.get("FLAGSMITH_API_TOKEN"),
    api_keys=os.environ.get("ENVIRONMENT_API_KEYS").split(","),
)


trait_schema = APITraitSchema()


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

    return JSONResponse(content=data)


def _get_fs_schema(identity_model: IdentityModel):
    return APIFeatureStateSchema(
        exclude=["multivariate_feature_state_values"],
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
        "identifier": identity.identifier,
        "traits": trait_schema.dump(trait_models, many=True),
        "flags": fs_schema.dump(flags, many=True),
    }
    return JSONResponse(content=data)


@app.on_event("startup")
@repeat_every(
    seconds=int(os.environ.get("API_POLL_FREQUENCY", 10)), raise_exceptions=True
)
def refresh_cache():
    cache_service.refresh()
