import typing
from datetime import datetime
from functools import lru_cache

import httpx
import structlog
from flag_engine.engine import (
    get_environment_feature_state,
    get_environment_feature_states,
    get_identity_feature_states,
)
from flag_engine.environments.models import EnvironmentModel
from flag_engine.identities.models import IdentityModel
from orjson import orjson

from edge_proxy.cache import BaseEnvironmentsCache, LocalMemEnvironmentsCache
from edge_proxy.exceptions import FeatureNotFoundError, FlagsmithUnknownKeyError
from edge_proxy.feature_utils import filter_out_server_key_only_feature_states
from edge_proxy.mappers import (
    map_feature_state_to_response_data,
    map_feature_states_to_response_data,
    map_traits_to_response_data,
)
from edge_proxy.models import IdentityWithTraits
from edge_proxy.settings import AppSettings

logger = structlog.get_logger(__name__)


class EnvironmentService:
    def __init__(
        self,
        cache: BaseEnvironmentsCache = None,
        client: httpx.AsyncClient = None,
        settings: AppSettings = None,
    ):
        self.cache = cache or LocalMemEnvironmentsCache()
        self.settings = settings or AppSettings()
        self._client = client or httpx.AsyncClient(
            timeout=settings.api_poll_timeout_seconds,
        )
        self.last_updated_at = None

        if settings.endpoint_caches:
            if settings.endpoint_caches.flags.use_cache:
                self.get_flags_response_data = lru_cache(
                    maxsize=settings.endpoint_caches.flags.cache_max_size,
                )(self.get_flags_response_data)

            if settings.endpoint_caches.identities.use_cache:
                self.get_identity_response_data = lru_cache(
                    maxsize=settings.endpoint_caches.identities.cache_max_size,
                )(self.get_identity_response_data)

    async def refresh_environment_caches(self):
        received_error = False
        for key_pair in self.settings.environment_key_pairs:
            try:
                environment_document = await self._fetch_document(
                    key_pair.server_side_key
                )
                if self.cache.put_environment(
                    environment_api_key=key_pair.client_side_key,
                    environment_document=environment_document,
                ):
                    await self._clear_endpoint_caches()
            except (httpx.HTTPError, orjson.JSONDecodeError):
                logger.exception(
                    "error_fetching_document", client_side_key=key_pair.client_side_key
                )
                received_error = True
        if not received_error:
            self.last_updated_at = datetime.now()

    def get_flags_response_data(
        self, environment_key: str, feature: str = None
    ) -> dict[str, typing.Any]:
        environment_document = self.get_environment(environment_key)
        environment = EnvironmentModel.model_validate(environment_document)

        if feature:
            feature_state = get_environment_feature_state(environment, feature)

            if not filter_out_server_key_only_feature_states(
                feature_states=[feature_state],
                environment=environment,
            ):
                raise FeatureNotFoundError()

            data = map_feature_state_to_response_data(feature_state)

        else:
            feature_states = filter_out_server_key_only_feature_states(
                feature_states=get_environment_feature_states(environment),
                environment=environment,
            )
            data = map_feature_states_to_response_data(feature_states)

        return data

    def get_identity_response_data(
        self, input_data: IdentityWithTraits, environment_key: str
    ) -> dict[str, typing.Any]:
        environment_document = self.get_environment(environment_key)
        environment = EnvironmentModel.model_validate(environment_document)
        identity = IdentityModel.model_validate(
            self.cache.get_identity(
                environment_api_key=environment_key,
                identifier=input_data.identifier,
            )
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
        return data

    def get_environment(self, client_side_key: str) -> dict[str, typing.Any]:
        if environment_document := self.cache.get_environment(client_side_key):
            return environment_document
        raise FlagsmithUnknownKeyError(client_side_key)

    async def _fetch_document(self, server_side_key: str) -> dict[str, typing.Any]:
        response = await self._client.get(
            url=f"{self.settings.api_url}/environment-document/",
            headers={"X-Environment-Key": server_side_key},
        )
        response.raise_for_status()
        return orjson.loads(response.text)

    async def _clear_endpoint_caches(self):
        for func in (self.get_identity_response_data, self.get_flags_response_data):
            try:
                func.cache_clear()
            except AttributeError:
                pass
