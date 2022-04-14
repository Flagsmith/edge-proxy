import logging

import requests

from .settings import Settings


class CacheService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._session = requests.Session()
        self._cache = {}

    def _fetch_document(self, server_side_key):
        url = f"{self.settings.api_url}/environment-document/"
        response = self._session.get(
            url, headers={"X-Environment-Key": server_side_key}
        )
        response.raise_for_status()
        return response.json()

    def refresh(self):
        for key_pair in self.settings.environment_key_pair:
            try:
                self._cache[key_pair.client_side_key] = self._fetch_document(
                    key_pair.server_side_key
                )
            except requests.exceptions.HTTPError:
                logging.error(
                    f"received non 200 response for {key_pair.client_side_key}"
                )

    def get_environment(self, client_side_key):
        return self._cache[client_side_key]
