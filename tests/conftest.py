import typing

import pytest
from pytest_mock import MockerFixture
from fastapi.testclient import TestClient


if typing.TYPE_CHECKING:
    from edge_proxy.environments import EnvironmentService


@pytest.fixture
def environment_1_feature_states_response_list() -> typing.List[dict]:
    return [
        {
            "feature_state_value": "feature_1_value",
            "feature": {"name": "feature_1", "type": "STANDARD", "id": 1},
            "enabled": False,
        },
        {
            "feature_state_value": "2.3",
            "feature": {
                "name": "feature_2",
                "type": "STANDARD",
                "id": 2,
            },
            "enabled": True,
        },
    ]


@pytest.fixture
def environment_1_feature_states_response_list_response_with_segment_override(
    environment_1_feature_states_response_list,
):
    environment_1_feature_states_response_list[1]["feature_state_value"] = (
        "segment_override"
    )
    return environment_1_feature_states_response_list


@pytest.fixture
def environment_1_feature_states_response_list_response_with_identity_override(
    environment_1_feature_states_response_list: list[dict[str, typing.Any]],
) -> list[dict[str, typing.Any]]:
    environment_1_feature_states_response_list[0]["feature_state_value"] = (
        "identity_override"
    )
    environment_1_feature_states_response_list[0]["enabled"] = True
    return environment_1_feature_states_response_list


@pytest.fixture(autouse=True)
def mock_settings(mocker: MockerFixture) -> None:
    mock_config = {
        "environment_key_pairs": [
            {"server_side_key": "ser.abc123", "client_side_key": "def456"}
        ]
    }
    mocker.patch(
        "edge_proxy.settings.json_config_settings_source", return_value=mock_config
    )


@pytest.fixture
def environment_service() -> "EnvironmentService":
    from edge_proxy.server import environment_service

    return environment_service


@pytest.fixture
def client():
    from edge_proxy.server import app

    with TestClient(app) as c:
        yield c
