import typing

import pytest
from pytest_mock import MockerFixture
from pydantic import ValidationError

from edge_proxy.settings import get_settings, AppSettings


def test_client_side_key_validation() -> None:
    """
    Test that client_side_key is properly validated.
    """
    # Valid
    AppSettings(
        environment_key_pairs=[
            {"server_side_key": "ser.abc123", "client_side_key": "def456"}
        ]
    )

    # Missing client_side_key
    with pytest.raises(ValidationError):
        AppSettings(
            environment_key_pairs=[
                {"server_side_key": "ser.abc123", "client_side_key": ""}
            ]
        )

    # Invalid server_side_key
    with pytest.raises(ValidationError):
        AppSettings(
            environment_key_pairs=[
                {"server_side_key": "abc123", "client_side_key": "abc123"}
            ]
        )


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
    config_file_json: dict[str, typing.Any],
    expected_config: dict[str, typing.Any],
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
