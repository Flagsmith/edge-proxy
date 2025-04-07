import json
import logging
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog

from pydantic import AliasChoices, BaseModel, HttpUrl, IPvAnyAddress, Field, constr

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
    try:
        config = json.loads(Path(CONFIG_PATH).read_text(encoding))
        logger.info(f"Loaded configuration from {CONFIG_PATH}")
        return config
    except FileNotFoundError:
        logger.info(f"Configuration file at {CONFIG_PATH} not found")
        return {}


class EnvironmentKeyPair(BaseModel):
    server_side_key: constr(pattern=r"ser\.*", strip_whitespace=True)
    client_side_key: constr(min_length=1, strip_whitespace=True)


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
    colours: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "colours",
            "colors",
        ),
    )
    override: dict[str, Any] = Field(default_factory=dict)


class ServerSettings(BaseModel):
    host: IPvAnyAddress = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    proxy_headers: bool = False


class HealthCheckSettings(BaseModel):
    environment_update_grace_period_seconds: Optional[int] = 30


class AppSettings(BaseModel):
    environment_key_pairs: list[EnvironmentKeyPair]
    api_url: HttpUrl = HttpUrl("https://edge.api.flagsmith.com/api/v1")
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
    health_check: HealthCheckSettings = HealthCheckSettings()


class AppConfig(AppSettings, BaseSettings):
    class Config:
        extra = "ignore"

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
