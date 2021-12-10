import os
import importlib
from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse

from models import IdentityWithTraits
from cache import CacheService

app = FastAPI()
# TODO: should we move fast api to edge api?
# should we create a diff repo for service of edge-api?
cache_service = CacheService(
    api_url=os.environ.get("FLAGSMITH_API_URL"),
    api_token=os.environ.get("FLAGSMITH_API_TOKEN"),
    api_keys=os.environ.get("ENVIRONMENT_API_KEYS").split(","),
    poll_frequency=int(os.environ.get("API_POLL_FREQUENCY", 10)),
)


class LambdaStub:
    def track_api_usage(*args, **kwargs):
        pass


environment = importlib.import_module("edge-api.src.environment")

environment_service = environment.EnvironmentService(cache_service, LambdaStub())

identity = importlib.import_module("edge-api.src.identity")

identity_service = identity.IdentityService(cache_service, LambdaStub())


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


@app.get("/api/v1/flags")
def flags(feature_name: str = None, x_environment_key: str = Header(None)):
    print(x_environment_key)
    request_wrapper = RequestEventStub(x_environment_key, feature_name=feature_name)
    data = environment_service.get_flags_response(request_wrapper)
    return JSONResponse(content=data)


@app.post("/api/v1/identity")
def identity(
    input_data: IdentityWithTraits,
    feature_name: str = None,
    x_environment_key: str = Header(None),
):
    request_wrapper = RequestEventStub(x_environment_key)
    data = identity_service.get_identify_with_traits_response(
        request_wrapper, input_data.identifier, traits=input_data.dict()["traits"]
    )
    return JSONResponse(content=data)
