import importlib
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
from .task import repeat_every

fs_schema = APIFeatureStateSchema(exclude=["multivariate_feature_state_values"])
app = FastAPI()
# TODO: should we move fast api to edge api?
# should we create a diff repo for service of edge-api?
cache_service = CacheService(
    api_url=os.environ.get("FLAGSMITH_API_URL"),
    api_token=os.environ.get("FLAGSMITH_API_TOKEN"),
    api_keys=os.environ.get("ENVIRONMENT_API_KEYS").split(","),
)


class LambdaStub:
    def track_api_usage(*args, **kwargs):
        pass


environment = importlib.import_module(".edge-api.src.environment", package="src")

environment_service = environment.EnvironmentService(cache_service, LambdaStub())

identity = importlib.import_module(".edge-api.src.identity", package="src")

identity_service = identity.IdentityService(cache_service, LambdaStub())
trait_schema = APITraitSchema()


class RequestEventStub:
    def __init__(self, api_key: str, feature_name: str = None, host: str = None):
        self.api_key = api_key
        self.feature_name = feature_name
        self._host = host  # for some reason I can't use host

    @property
    def environment_key(self):
        return self.api_key

    @property
    def resource(self):
        return ""

    @property
    def host(self):
        return self._host

    @property
    def query_params(self):
        return {"feature_name": self.feature_name}


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
    feature_name: str = None,
    x_environment_key: str = Header(None),
):
    environment_document = cache_service.get_environment(x_environment_key)
    environment = build_environment_model(environment_document)
    identity = IdentityModel(
        identifier=input_data.identifier, environment_api_key=x_environment_key
    )
    traits = input_data.dict()["traits"]
    trait_models = trait_schema.load(traits, many=True)
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
