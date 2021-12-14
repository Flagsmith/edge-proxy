import logging

import requests

import requests


class CacheService:
    def __init__(self, api_url: str, api_token: str, api_keys: list):
        self.api_url = api_url
        self.api_token = api_token
        self.api_keys = api_keys

        self._cache = {}

    def _fetch_document(self, api_key):
        url = f"{self.api_url}/environments/{api_key}/document/"
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }
        response = requests.request(
            "GET",
            url,
            headers=headers,
        )

        # TODO handle retry and error
        if not response.status_code == 200:
            logging.error(f"received non 200 response for {api_key}")
            return {}

        return response.json()

    def refresh(self):
        for api_key in self.api_keys:
            self._cache[api_key] = self._fetch_document(api_key)

    def get_environment(self, api_key):
        return self._cache[api_key]

    # interface for dynamodb
    def update_identity(self, identity_dict: dict):
        pass

    def get_environment_and_identity(self, api_key, *args):
        return self.get_environment(api_key), None
