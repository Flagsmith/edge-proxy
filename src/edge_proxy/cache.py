from abc import ABC
from collections import defaultdict
from typing import Any
from edge_proxy.feature_utils import build_feature_types_lookup


class BaseEnvironmentsCache(ABC):
    def __init__(self, *args, **kwargs):
        self.last_updated_at = None

    def put_environment(
        self,
        environment_api_key: str,
        environment_document: dict[str, Any],
    ) -> bool:
        """
        Update the environment cache for the given key with the given environment document.

        Returns a boolean confirming if the cache was updated or not (i.e. if the environment document
        was different from the one already in the cache).
        """
        # TODO: can we use the environment header here instead of comparing the document?
        if environment_document != self.get_environment(environment_api_key):
            self._put_environment(environment_api_key, environment_document)
            return True
        return False

    def _put_environment(
        self,
        environment_api_key: str,
        environment_document: dict[str, Any],
    ) -> None:
        raise NotImplementedError()

    def get_environment(self, environment_api_key: str) -> dict[str, Any] | None:
        raise NotImplementedError()

    def get_feature_types(self, environment_api_key: str) -> dict[int, str] | None:
        return None

    def get_identity(
        self,
        environment_api_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        raise NotImplementedError()


_LocalCacheDict = dict[str, dict[str, Any]]


class LocalMemEnvironmentsCache(BaseEnvironmentsCache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._environment_cache: _LocalCacheDict = {}
        self._feature_types_cache: dict[str, dict[int, str]] = {}
        self._identity_override_cache = defaultdict[str, _LocalCacheDict](dict)

    def _put_environment(
        self,
        environment_api_key: str,
        environment_document: dict[str, Any],
    ) -> None:
        self._environment_cache[environment_api_key] = environment_document

        self._feature_types_cache[environment_api_key] = build_feature_types_lookup(
            environment_document
        )

        new_overrides = environment_document.get("identity_overrides") or []
        self._identity_override_cache[environment_api_key] = {
            identifier: identity_document
            for identity_document in new_overrides
            if (identifier := identity_document.get("identifier"))
        }

    def get_environment(
        self,
        environment_api_key: str,
    ) -> dict[str, Any] | None:
        return self._environment_cache.get(environment_api_key)

    def get_feature_types(self, environment_api_key: str) -> dict[int, str] | None:
        return self._feature_types_cache.get(environment_api_key)

    def get_identity(
        self,
        environment_api_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        return self._identity_override_cache[environment_api_key].get(identifier) or {
            "environment_api_key": environment_api_key,
            "identifier": identifier,
        }
