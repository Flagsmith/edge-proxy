import logging
from datetime import datetime

import httpx
import orjson

from .exceptions import FlagsmithUnknownKeyError
from .settings import Settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.last_updated_at = None
        self._cache = {}
        self._client = httpx.AsyncClient(timeout=settings.api_poll_timeout)

    async def fetch_document(self, server_side_key):
        response = await self._client.get(
            url=f"{self.settings.api_url}/environment-document/",
            headers={"X-Environment-Key": server_side_key},
        )
        response.raise_for_status()
        return orjson.loads(response.text)

    async def refresh(self):
        received_error = False
        for key_pair in self.settings.environment_key_pairs:
            try:
                environment_document = await self.fetch_document(
                    key_pair.server_side_key
                )
                if environment_document != self._cache.get(key_pair.client_side_key):
                    self._cache[key_pair.client_side_key] = environment_document
                    self._clear_endpoint_caches()
            except (httpx.HTTPError, orjson.JSONDecodeError):
                received_error = True
                logger.exception(
                    f"Failed to fetch document for {key_pair.client_side_key}"
                )
        if not received_error:
            self.last_updated_at = datetime.now()

    def get_environment(self, client_side_key):
        try:
            return self._cache[client_side_key]
        except KeyError:
            raise FlagsmithUnknownKeyError(client_side_key)

    def _clear_endpoint_caches(self) -> None:
        from .main import _get_flags_response_data, _get_identity_response_data

        if self.settings.endpoint_caches:
            if self.settings.endpoint_caches.flags.use_cache:
                _get_flags_response_data.cache_clear()
            if self.settings.endpoint_caches.identities.use_cache:
                _get_identity_response_data.cache_clear()
