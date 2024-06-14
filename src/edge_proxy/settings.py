import json
import logging
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

import structlog

from pydantic import BaseModel, BaseSettings, HttpUrl, IPvAnyAddress, Field
from pydantic.env_settings import SettingsSourceCallable


CONFIG_PATH = os.environ.get(
    "CONFIG_PATH",
    default="config.json",
)


logger = structlog.get_logger()


class LogHandler(Enum):
    STREAM = "stream"
    FILE = "file"


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


def ensure_defaults() -> None:
    if not os.path.exists(CONFIG_PATH):
        defaults = AppSettings()
        defaults_json = defaults.json(indent=4, exclude_none=True)
        print(defaults_json, file=sys.stdout)
        try:
            with open(CONFIG_PATH, "w") as fp:
                fp.write(defaults_json)
        except OSError:
            logger.warning(
                "error_writing_config_defaults",
                config_path=CONFIG_PATH,
                exc_info=True,
            )


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.
    """
    encoding = "utf-8"
    return json.loads(Path(CONFIG_PATH).read_text(encoding))


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
    log_handler: LogHandler = LogHandler.STREAM
    log_file_path: str = "/var/log/edge_proxy.log"


class ServerSettings(BaseModel):
    host: IPvAnyAddress = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class AppSettings(BaseModel):
    environment_key_pairs: List[EnvironmentKeyPair] = [
        EnvironmentKeyPair(
            server_side_key="ser.environment_key",
            client_side_key="environment_key",
        )
    ]
    api_url: HttpUrl = "https://edge.api.flagsmith.com/api/v1"
    api_poll_frequency: int = Field(default=10)
    api_poll_timeout: int = Field(default=5)
    endpoint_caches: EndpointCachesSettings | None = None
    allow_origins: List[str] = ["*"]
    logging: LoggingSettings = LoggingSettings()
    server: ServerSettings = ServerSettings()


class AppConfig(AppSettings, BaseSettings):
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source


def get_settings() -> AppConfig:
    return AppConfig()
