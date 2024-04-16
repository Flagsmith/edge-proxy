import typing

import pytest
from pytest_mock import MockerFixture
from fastapi.testclient import TestClient


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


@pytest.fixture(autouse=True)
def skip_json_config_settings_source(mocker: MockerFixture) -> None:
    mocker.patch("edge_proxy.settings.json_config_settings_source", lambda _: {})


@pytest.fixture
def client():
    from edge_proxy.server import app

    with TestClient(app) as c:
        yield c
