
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from decouple import config
from decouple import Csv
from dotenv import load_dotenv


from pydantic import BaseModel, BaseSettings, HttpUrl
from pydantic.env_settings import SettingsSourceCallable


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.
    """
    encoding = settings.__config__.env_file_encoding
    env_file = settings.__config__.env_file
    return json.loads(Path(env_file).read_text(encoding))


class EnvironmentKeyPair(BaseModel):
    server_side_key: str
    client_side_key: str


class Settings(BaseSettings):
    environment_key_pair: List[EnvironmentKeyPair]
    api_url: HttpUrl = "https://api.flagsmith.com/api/v1/"
    api_poll_frequency: int = 10

    class Config:
        env_file = "config.json"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source
