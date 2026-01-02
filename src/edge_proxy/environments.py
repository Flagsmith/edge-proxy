from typing import Any
from datetime import datetime
from email.utils import formatdate
from functools import lru_cache

import httpx
import starlette.status
import structlog
from flag_engine.engine import get_evaluation_result
from flagsmith.mappers import (
    map_environment_document_to_context,
    map_context_and_identity_data_to_context,
)
from orjson import orjson

from edge_proxy.cache import BaseEnvironmentsCache, LocalMemEnvironmentsCache
from edge_proxy.exceptions import FeatureNotFoundError, FlagsmithUnknownKeyError
from edge_proxy.feature_utils import (
    build_feature_types_lookup,
    filter_disabled_flags,
    filter_out_server_key_only_flags,
)
from edge_proxy.mappers import (
    convert_traits_to_dict,
    map_flag_result_to_response_data,
    map_flag_results_to_response_data,
    map_traits_to_response_data,
)
from edge_proxy.models import IdentityWithTraits
from edge_proxy.settings import AppSettings, EnvironmentKeyPair

logger = structlog.get_logger(__name__)

SERVER_API_KEY_PREFIX = "ser."


def _get_hide_disabled_flags(environment_document: dict[str, Any]) -> bool:
    return environment_document.get("project", {}).get("hide_disabled_flags", False)


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
                environment_document = await self._fetch_document(key_pair)
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
        self, environment_key: str, feature: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        is_server_key = environment_key.startswith(SERVER_API_KEY_PREFIX)
        if is_server_key:
            environment_key = self._get_client_key_from_server_key(environment_key)

        environment_document = self.get_environment(environment_key=environment_key)
        server_key_only_feature_ids = environment_document.get("project", {}).get(
            "server_key_only_feature_ids", []
        )
        hide_disabled_flags = _get_hide_disabled_flags(environment_document)

        context = map_environment_document_to_context(environment_document)
        evaluation_result = get_evaluation_result(context)

        feature_types = self.cache.get_feature_types(environment_key)
        if feature_types is None:
            feature_types = build_feature_types_lookup(environment_document)

        if feature:
            if feature not in evaluation_result["flags"]:
                raise FeatureNotFoundError()

            flag_result = evaluation_result["flags"][feature]

            if not is_server_key:
                filtered = filter_out_server_key_only_flags(
                    [flag_result], server_key_only_feature_ids
                )
                if not filtered:
                    raise FeatureNotFoundError()

                if hide_disabled_flags and not flag_result.get("enabled", False):
                    raise FeatureNotFoundError()

            return map_flag_result_to_response_data(flag_result, feature_types)

        flags = list(evaluation_result["flags"].values())

        if not is_server_key:
            flags = filter_out_server_key_only_flags(flags, server_key_only_feature_ids)
            flags = filter_disabled_flags(flags, hide_disabled_flags)

        return map_flag_results_to_response_data(flags, feature_types)

    def get_identity_response_data(
        self, input_data: IdentityWithTraits, environment_key: str
    ) -> dict[str, Any]:
        is_server_key = environment_key.startswith(SERVER_API_KEY_PREFIX)
        if is_server_key:
            environment_key = self._get_client_key_from_server_key(environment_key)

        environment_document = self.get_environment(environment_key=environment_key)
        server_key_only_feature_ids = environment_document.get("project", {}).get(
            "server_key_only_feature_ids", []
        )
        hide_disabled_flags = _get_hide_disabled_flags(environment_document)

        environment_context = map_environment_document_to_context(environment_document)
        context = map_context_and_identity_data_to_context(
            context=environment_context,
            identifier=input_data.identifier,
            traits=convert_traits_to_dict(input_data.traits),
        )
        evaluation_result = get_evaluation_result(context)

        feature_types = self.cache.get_feature_types(environment_key)
        if feature_types is None:
            feature_types = build_feature_types_lookup(environment_document)

        flags = list(evaluation_result["flags"].values())
        if not is_server_key:
            flags = filter_out_server_key_only_flags(flags, server_key_only_feature_ids)
            flags = filter_disabled_flags(flags, hide_disabled_flags)

        return {
            "identifier": input_data.identifier,
            "traits": map_traits_to_response_data(input_data.traits),
            "flags": map_flag_results_to_response_data(flags, feature_types),
        }

    def get_environment(
        self,
        *,
        environment_key: str | None = None,
    ) -> dict[str, Any]:
        if environment_key and environment_key.startswith(SERVER_API_KEY_PREFIX):
            client_side_key = self._get_client_key_from_server_key(environment_key)
        else:
            client_side_key = environment_key

        if environment_document := self.cache.get_environment(client_side_key):
            return environment_document

        raise FlagsmithUnknownKeyError(environment_key)

    async def _fetch_document(self, key_pair: EnvironmentKeyPair) -> dict[str, Any]:
        headers = {
            "X-Environment-Key": key_pair.server_side_key,
        }
        environment_document = self.cache.get_environment(
            environment_api_key=key_pair.client_side_key
        )
        if environment_document:
            updated_at: str = environment_document.get("updated_at")
            if updated_at:
                try:
                    epoch_seconds = datetime.fromisoformat(updated_at).timestamp()
                    # Same implementation as https://docs.djangoproject.com/en/4.2/ref/utils/#django.utils.http.http_date
                    headers["If-Modified-Since"] = formatdate(
                        epoch_seconds, usegmt=True
                    )
                except ValueError:
                    logger.warning(
                        f"failed to parse updated_at, environment={key_pair.client_side_key} updated_at={updated_at}"
                    )
            else:
                logger.warning(
                    f"received environment with no updated_at: {key_pair.client_side_key}"
                )
        response = await self._client.get(
            url=f"{self.settings.api_url}/environment-document/",
            headers=headers,
        )
        if response.status_code == starlette.status.HTTP_304_NOT_MODIFIED:
            assert environment_document, (
                f"GET /environment-document returned 304 without a cached document. environment={key_pair.client_side_key}"
            )
            return environment_document
        response.raise_for_status()
        return orjson.loads(response.text)

    async def _clear_endpoint_caches(self):
        for func in (self.get_identity_response_data, self.get_flags_response_data):
            try:
                func.cache_clear()
            except AttributeError:
                pass

    def _get_client_key_from_server_key(self, server_key: str) -> str:
        for key_pair in self.settings.environment_key_pairs:
            if key_pair.server_side_key == server_key:
                return key_pair.client_side_key
        raise FlagsmithUnknownKeyError(server_key)
