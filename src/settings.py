import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, BaseSettings, HttpUrl
from pydantic.env_settings import SettingsSourceCallable


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.
    """
    encoding = "utf-8"
    env_file = "config.json"
    return json.loads(Path(env_file).read_text(encoding))


class EnvironmentKeyPair(BaseModel):
    server_side_key: str
    client_side_key: str


class EndpointCacheSettings(BaseModel):
    use_cache: bool = False
    cache_max_size: int = 128


class EndpointCachesSettings(BaseModel):
    flags: EndpointCacheSettings = EndpointCacheSettings(use_cache=False)
    identities: EndpointCacheSettings = EndpointCacheSettings(use_cache=False)


class Settings(BaseSettings):
    environment_key_pairs: List[EnvironmentKeyPair]
    api_url: HttpUrl = "https://edge.api.flagsmith.com/api/v1"
    api_poll_frequency: int = 10  # seconds
    api_poll_timeout: int = 5  # seconds
    endpoint_caches: EndpointCachesSettings | None = None
    allow_origins: List[str] = ["*"]

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source
