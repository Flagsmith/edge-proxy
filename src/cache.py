import logging
from datetime import datetime

import requests

from .settings import Settings


class CacheService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.last_updated_at = None
        self._session = requests.Session()
        self._cache = {}

    def fetch_document(self, server_side_key):
        url = f"{self.settings.api_url}/environment-document/"
        response = self._session.get(
            url, headers={"X-Environment-Key": server_side_key}
        )
        response.raise_for_status()
        return response.json()

    def refresh(self):
        received_error = False
        for key_pair in self.settings.environment_key_pairs:
            try:
                self._cache[key_pair.client_side_key] = self.fetch_document(
                    key_pair.server_side_key
                )
            except requests.exceptions.HTTPError:
                received_error = True
                logging.error(
                    f"received non 200 response for {key_pair.client_side_key}"
                )
        if not received_error:
            self.last_updated_at = datetime.now()

    def get_environment(self, client_side_key):
        return self._cache[client_side_key]
