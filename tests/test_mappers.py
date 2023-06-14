from typing import Any

import pytest
from flag_engine.features.models import FeatureStateModel
from flag_engine.identities.traits.models import TraitModel

from src.mappers import (
    map_feature_state_to_response_data,
    map_feature_states_to_response_data,
    map_traits_to_response_data,
)


@pytest.fixture()
def feature_state_model() -> FeatureStateModel:
    return FeatureStateModel.parse_obj(
        {
            "multivariate_feature_state_values": [],
            "feature_state_value": "feature_1_value",
            "id": 1,
            "featurestate_uuid": "2d1831b9-4642-4474-8b09-cdf3872cdc99",
            "feature_segment": None,
            "feature": {
                "name": "feature_1",
                "type": "STANDARD",
                "id": 1,
            },
            "enabled": False,
        },
    )


@pytest.fixture()
def multivariate_feature_state_model() -> FeatureStateModel:
    return FeatureStateModel.parse_obj(
        {
            "multivariate_feature_state_values": [
                {
                    "mv_fs_value_uuid": "bf83bedd-d9c0-4b47-97f2-84a2559303e9",
                    "percentage_allocation": 50,
                    "multivariate_feature_option": {"value": "50_percent", "id": 1},
                    "id": 1,
                },
                {
                    "mv_fs_value_uuid": "a9c2aba9-ce3a-4333-87f3-d9fa4c5cb9a5",
                    "percentage_allocation": 10,
                    "multivariate_feature_option": {"value": "1_percent", "id": 2},
                    "id": 2,
                },
            ],
            "feature_state_value": None,
            "featurestate_uuid": "a74bcb0f-b6a3-4636-866e-13e326c80b51",
            "feature_segment": None,
            "id": 4,
            "feature": {
                "name": "multivariate_feature",
                "type": "MULTIVARIATE",
                "id": 4,
            },
            "enabled": False,
        }
    )


@pytest.fixture()
def trait_model() -> TraitModel:
    return TraitModel(trait_key="phIndex", trait_value=7.4)


@pytest.fixture()
def trait_data() -> dict[str, float]:
    return {"trait_key": "phIndex", "trait_value": 7.4}


@pytest.fixture()
def traits_data(
    trait_data: dict[str, float],
) -> list[dict[str, Any]]:
    return [
        trait_data,
        {"trait_key": "email", "trait_value": "notarealemail@fictitiousdomain.xyz"},
        {"trait_key": "userCategoryId", "trait_value": 12},
    ]


@pytest.fixture()
def trait_models(trait_model: TraitModel) -> list[TraitModel]:
    return [
        trait_model,
        TraitModel(
            trait_key="email",
            trait_value="notarealemail@fictitiousdomain.xyz",
        ),
        TraitModel(trait_key="userCategoryId", trait_value=12),
    ]


def test_map_feature_state_to_response_data__return_expected(
    multivariate_feature_state_model: FeatureStateModel,
) -> None:
    # When
    result = map_feature_state_to_response_data(multivariate_feature_state_model)

    # Then
    assert result == {
        "enabled": False,
        "feature": {
            "id": 4,
            "name": "multivariate_feature",
            "type": "MULTIVARIATE",
        },
        "feature_state_value": None,
    }


def test_map_feature_states_to_response_data__return_expected(
    feature_state_model: FeatureStateModel,
    multivariate_feature_state_model: FeatureStateModel,
) -> None:
    # Given
    feature_states = [feature_state_model, multivariate_feature_state_model]

    # When
    result = map_feature_states_to_response_data(feature_states)

    # Then
    assert result == [
        {
            "enabled": False,
            "feature": {
                "id": 1,
                "name": "feature_1",
                "type": "STANDARD",
            },
            "feature_state_value": "feature_1_value",
        },
        {
            "enabled": False,
            "feature": {
                "id": 4,
                "name": "multivariate_feature",
                "type": "MULTIVARIATE",
            },
            "feature_state_value": None,
        },
    ]


def test_map_traits_to_response_data__return_expected(
    trait_models: list[TraitModel],
    traits_data: list[dict[str, Any]],
) -> None:
    # When
    result = map_traits_to_response_data(trait_models)

    # Then
    assert result == traits_data
