from typing import Any, Optional

import pytest
from pytest_mock import MockerFixture
from pydantic import ValidationError

from edge_proxy.settings import get_settings, AppSettings


@pytest.mark.parametrize(
    "client_side_key,server_side_key,expected_exception",
    [
        ("abc123", "ser.456", None),
        ("abc123", "456", ValidationError),
        ("abc123", "", ValidationError),
        ("", "ser.456", ValidationError),
    ],
)
def test_client_side_key_validation(
    client_side_key: str, server_side_key: str, expected_exception: Optional[Exception]
) -> None:
    try:
        AppSettings(
            environment_key_pairs=[
                {"server_side_key": server_side_key, "client_side_key": client_side_key}
            ]
        )
    except expected_exception:
        pass


@pytest.mark.parametrize(
    "config_file_json, expected_config",
    (
        (
            {
                "environment_key_pairs": [
                    {"server_side_key": "ser.abc123", "client_side_key": "def456"}
                ],
                "api_poll_frequency": 10,
                "api_poll_timeout": 10,
                "api_url": "https://api.flagsmith.com/api/v1",
            },
            {"api_poll_frequency_seconds": 10, "api_poll_timeout_seconds": 10},
        ),
        (
            {
                "environment_key_pairs": [
                    {"server_side_key": "ser.abc123", "client_side_key": "def456"}
                ],
                "api_poll_frequency_seconds": 10,
                "api_poll_timeout_seconds": 10,
                "api_url": "https://api.flagsmith.com/api/v1",
            },
            {"api_poll_frequency_seconds": 10, "api_poll_timeout_seconds": 10},
        ),
    ),
)
def test_settings_are_loaded_correctly(
    mocker: MockerFixture,
    config_file_json: dict[str, Any],
    expected_config: dict[str, Any],
) -> None:
    """
    Parametrized test which accepts a raw json config file, and a dictionary representing the
    specific tests that are required against the resulting config.
    """

    # Given
    mocker.patch(
        "edge_proxy.settings.json_config_settings_source",
        return_value=config_file_json,
    )

    # When
    config = get_settings()

    # Then
    for key, value in expected_config.items():
        assert getattr(config, key) == value
