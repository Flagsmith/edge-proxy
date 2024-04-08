import typing
from abc import ABC


class BaseEnvironmentsCache(ABC):
    def __init__(self, *args, **kwargs):
        self.last_updated_at = None

    def put_environment(
        self,
        environment_api_key: str,
        environment_document: typing.Dict[str, typing.Any],
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
        environment_document: typing.Dict[str, typing.Any],
    ) -> None:
        raise NotImplementedError()

    def get_environment(
        self, environment_api_key: str
    ) -> typing.Dict[str, typing.Any] | None:
        raise NotImplementedError()


class LocalMemEnvironmentsCache(BaseEnvironmentsCache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def _put_environment(
        self,
        environment_api_key: str,
        environment_document: typing.Dict[str, typing.Any],
    ) -> None:
        self._cache[environment_api_key] = environment_document

    def get_environment(
        self, environment_api_key
    ) -> typing.Dict[str, typing.Any] | None:
        return self._cache.get(environment_api_key)
