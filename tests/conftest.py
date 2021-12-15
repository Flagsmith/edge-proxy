import typing

import pytest


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
        {
            "feature_state_value": None,
            "feature": {"name": "feature_3", "type": "STANDARD", "id": 3},
            "enabled": False,
        },
    ]


@pytest.fixture
def environment_1_feature_states_response_list_response_with_segment_override(
    environment_1_feature_states_response_list,
):
    environment_1_feature_states_response_list[1][
        "feature_state_value"
    ] = "segment_override"
    return environment_1_feature_states_response_list
