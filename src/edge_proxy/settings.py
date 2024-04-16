import json
import logging
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

import structlog

from pydantic import BaseModel, BaseSettings, HttpUrl, IPvAnyAddress, Field
from pydantic.env_settings import SettingsSourceCallable


class LogFormat(Enum):
    GENERIC = "generic"
    JSON = "json"


class LogLevel(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"

    def to_logging_log_level(self) -> int:
        return getattr(logging, self.value)


def get_config_path() -> str:
    return os.environ.get("CONFIG_PATH", "config.json")


def ensure_defaults() -> None:
    config_path = get_config_path()

    if not os.path.exists(config_path):
        defaults = _Settings()
        defaults_json = defaults.json(indent=4, exclude_none=True)
        print(defaults_json, file=sys.stdout)
        try:
            with open(config_path, "w") as fp:
                fp.write(defaults_json)
        except OSError:
            structlog.get_logger().warning(
                "error_writing_config_defaults",
                config_path=config_path,
                exc_info=True,
            )


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.
    """
    config_path = get_config_path()
    encoding = "utf-8"
    return json.loads(Path(config_path).read_text(encoding))


class EnvironmentKeyPair(BaseModel):
    server_side_key: str
    client_side_key: str


class EndpointCacheSettings(BaseModel):
    use_cache: bool = False
    cache_max_size: int = 128


class EndpointCachesSettings(BaseModel):
    flags: EndpointCacheSettings = EndpointCacheSettings(use_cache=False)
    identities: EndpointCacheSettings = EndpointCacheSettings(use_cache=False)


class LoggingSettings(BaseModel):
    enable_access_log: bool = False
    log_format: LogFormat = LogFormat.GENERIC
    log_level: LogLevel = LogLevel.INFO
    log_event_field_name: str = "message"


class ServerSettings(BaseModel):
    host: IPvAnyAddress = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class _Settings(BaseModel):
    environment_key_pairs: List[EnvironmentKeyPair] = [
        EnvironmentKeyPair(
            server_side_key="ser.environment_key",
            client_side_key="environment_key",
        )
    ]
    api_url: HttpUrl = "https://edge.api.flagsmith.com/api/v1"
    api_poll_frequency_seconds: int = Field(
        default=10,
        aliases=["api_poll_frequency_seconds", "api_poll_frequency"],
    )
    api_poll_timeout_seconds: int = Field(
        default=5,
        aliases=["api_poll_timeout_seconds", "api_poll_timeout"],
    )
    endpoint_caches: EndpointCachesSettings | None = None
    allow_origins: List[str] = ["*"]
    logging: LoggingSettings = LoggingSettings()
    server: ServerSettings = ServerSettings()


class Settings(_Settings, BaseSettings):
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source


def get_settings() -> Settings:
    return Settings()
