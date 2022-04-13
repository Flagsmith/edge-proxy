import logging

import requests


class CacheService:
    def __init__(self, api_url: str, server_side_keys: str, api_keys: list):
        assert len(server_side_keys) == len(api_keys)
        self.api_url = api_url
        self.server_side_keys = server_side_keys
        self.api_keys = api_keys
        self._session = requests.Session()
        self._cache = {}

    def _fetch_document(self, server_side_key):
        url = f"{self.api_url}/environment-document/"
        response = self._session.get(
            url, headers={"X-Environment-Key": server_side_key}
        )
        response.raise_for_status()
        return response.json()

    def refresh(self):
        for index, api_key in enumerate(self.api_keys):
            try:
                self._cache[api_key] = self._fetch_document(
                    self.server_side_keys[index]
                )
            except requests.exceptions.HTTPError:
                logging.error(f"received non 200 response for {api_key}")

    def get_environment(self, api_key):
        return self._cache[api_key]
