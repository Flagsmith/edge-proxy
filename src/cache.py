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
        self._client = httpx.AsyncClient(timeout=30)

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
                self._cache[key_pair.client_side_key] = await self.fetch_document(
                    key_pair.server_side_key
                )
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
