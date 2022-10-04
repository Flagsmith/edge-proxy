import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import HttpUrl
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


class Settings(BaseSettings):
    environment_key_pairs: List[EnvironmentKeyPair]
    api_url: HttpUrl = "https://edge.api.flagsmith.com/api/v1"
    api_poll_frequency: int = 10

    # sse settings
    stream_delay: int = 1  # seconds
    retry_timeout: int = 15000  # milliseconds
    max_stream_age: int = 30  # seconds
    allow_origins: List[str] = ["*"]
    sse_authentication_token: str = ""

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source
