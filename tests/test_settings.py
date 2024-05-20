import json
import typing

import pytest

from src.edge_proxy.settings import AppConfig


@pytest.mark.parametrize(
    "config_file_raw_json, settings_tests",
    (
        (
            json.dumps(
                {
                    "environment_key_pairs": [
                        {"server_side_key": "abc123", "client_side_key": "ser.def456"}
                    ],
                    "api_poll_frequency": 10,
                    "api_poll_timeout": 10,
                    "api_url": "https://api.flagsmith.com/api/v1",
                },
            ),
            {"api_poll_frequency_seconds": 10, "api_poll_timeout_seconds": 10},
        ),
        (
            json.dumps(
                {
                    "environment_key_pairs": [
                        {"server_side_key": "abc123", "client_side_key": "ser.def456"}
                    ],
                    "api_poll_frequency_seconds": 10,
                    "api_poll_timeout_seconds": 10,
                    "api_url": "https://api.flagsmith.com/api/v1",
                }
            ),
            {"api_poll_frequency_seconds": 10, "api_poll_timeout_seconds": 10},
        ),
    ),
)
def test_settings_are_loaded_correctly(
    mock_json_config_file: typing.Callable[[str], None],
    config_file_raw_json: str,
    settings_tests: dict[str, typing.Any],
) -> None:
    """
    Parametrized test which accepts a raw json config file, and a dictionary representing the
    specific tests that are required against the resulting config.
    """

    # Given
    mock_json_config_file(config_file_raw_json)

    # When
    config = AppConfig()

    # Then
    for key, value in settings_tests.items():
        assert getattr(config, key) == value
