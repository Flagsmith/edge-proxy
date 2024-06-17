import json
import logging
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

from pydantic import AliasChoices, BaseModel, HttpUrl, IPvAnyAddress, Field

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


CONFIG_PATH = os.environ.get(
    "CONFIG_PATH",
    default="config.json",
)


logger = structlog.get_logger()


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
        defaults_json = defaults.model_dump_json(indent=4, exclude_none=True)
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


def json_config_settings_source() -> dict[str, Any]:
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
    log_filename: str | None = None
    override: dict[str, Any] = Field(default_factory=dict)


class ServerSettings(BaseModel):
    host: IPvAnyAddress = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    log_config: dict[str, Any] | str | None = None


class AppSettings(BaseModel):
    environment_key_pairs: list[EnvironmentKeyPair] = Field(
        default_factory=lambda: [
            EnvironmentKeyPair(
                server_side_key="ser.environment_key",
                client_side_key="environment_key",
            )
        ]
    )
    api_url: HttpUrl = "https://edge.api.flagsmith.com/api/v1"
    api_poll_frequency_seconds: int = Field(
        default=10,
        validation_alias=AliasChoices(
            "api_poll_frequency_seconds",
            "api_poll_frequency",
        ),
    )
    api_poll_timeout_seconds: int = Field(
        default=5,
        validation_alias=AliasChoices(
            "api_poll_timeout_seconds",
            "api_poll_timeout",
        ),
    )
    endpoint_caches: EndpointCachesSettings | None = None
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    logging: LoggingSettings = LoggingSettings()
    server: ServerSettings = ServerSettings()


class AppConfig(AppSettings, BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, env_settings, json_config_settings_source


def get_settings() -> AppConfig:
    return AppConfig()
