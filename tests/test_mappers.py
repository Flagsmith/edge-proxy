from typing import Any

import pytest

from edge_proxy.mappers import (
    map_flag_result_to_response_data,
    map_flag_results_to_response_data,
    map_traits_to_response_data,
)


@pytest.fixture()
def flag_result() -> dict[str, Any]:
    """Flag result from the new engine API."""
    return {
        "name": "feature_1",
        "enabled": False,
        "value": "feature_1_value",
        "metadata": {"id": 1},
    }


@pytest.fixture()
def multivariate_flag_result() -> dict[str, Any]:
    """Multivariate flag result from the new engine API."""
    return {
        "name": "multivariate_feature",
        "enabled": False,
        "value": None,
        "metadata": {"id": 4},
    }


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
def traits_dict() -> dict[str, Any]:
    """Traits as dict (new format)."""
    return {
        "phIndex": 7.4,
        "email": "notarealemail@fictitiousdomain.xyz",
        "userCategoryId": 12,
    }


def test_map_flag_result_to_response_data__return_expected(
    multivariate_flag_result: dict[str, Any],
) -> None:
    # When
    result = map_flag_result_to_response_data(multivariate_flag_result)

    # Then
    assert result == {
        "enabled": False,
        "feature": {
            "id": 4,
            "name": "multivariate_feature",
            "type": "STANDARD",
        },
        "feature_state_value": None,
    }


def test_map_flag_result_to_response_data__with_feature_types__return_expected(
    multivariate_flag_result: dict[str, Any],
) -> None:
    # Given
    feature_types = {4: "MULTIVARIATE"}

    # When
    result = map_flag_result_to_response_data(multivariate_flag_result, feature_types)

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


def test_map_flag_results_to_response_data__return_expected(
    flag_result: dict[str, Any],
    multivariate_flag_result: dict[str, Any],
) -> None:
    # Given
    flag_results = [flag_result, multivariate_flag_result]

    # When
    result = map_flag_results_to_response_data(flag_results)

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
                "type": "STANDARD",
            },
            "feature_state_value": None,
        },
    ]


def test_map_flag_results_to_response_data__with_feature_types__return_expected(
    flag_result: dict[str, Any],
    multivariate_flag_result: dict[str, Any],
) -> None:
    # Given
    flag_results = [flag_result, multivariate_flag_result]
    feature_types = {1: "STANDARD", 4: "MULTIVARIATE"}

    # When
    result = map_flag_results_to_response_data(flag_results, feature_types)

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
    traits_dict: dict[str, Any],
    traits_data: list[dict[str, Any]],
) -> None:
    # When
    result = map_traits_to_response_data(traits_dict)

    # Then
    assert result == traits_data
