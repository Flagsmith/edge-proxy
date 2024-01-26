from datetime import datetime, timedelta

import orjson
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.main import app

from .fixtures.response_data import environment_1

client = TestClient(app)


@pytest.mark.parametrize("endpoint", ["/proxy/health", "/health"])
def test_health_check_returns_200_if_cache_was_updated_recently(
    mocker: MockerFixture, endpoint: str
) -> None:
    mocked_environment_service = mocker.patch("src.main.environment_service")
    mocked_environment_service.last_updated_at = datetime.now()

    response = client.get(endpoint)
    assert response.status_code == 200


def test_health_check_returns_500_if_cache_was_not_updated() -> None:
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}


def test_health_check_returns_500_if_cache_is_stale(mocker) -> None:
    mocked_environment_service = mocker.patch("src.main.environment_service")
    mocked_environment_service.last_updated_at = datetime.now() - timedelta(days=10)
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}


def test_get_flags(
    mocker: MockerFixture, environment_1_feature_states_response_list: list[dict]
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )
    assert response.json() == environment_1_feature_states_response_list
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature(
    mocker: MockerFixture, environment_1_feature_states_response_list: list[dict]
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_1"},
    )
    assert response.json() == environment_1_feature_states_response_list[0]
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature__server_key_only_feature__return_expected(
    mocker: MockerFixture,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = environment_1

    # When
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_3"},
    )

    # Then
    assert response.status_code == 404
    assert response.json() == {
        "message": "feature 'feature_3' not found",
        "status": "not_found",
    }


def test_get_flags_unknown_key(mocker):
    environment_key = "unknown_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = None
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_1"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "unauthorized",
        "message": "unknown key 'unknown_environment_key'",
    }


def test_post_identity_with_traits(
    mocker, environment_1_feature_states_response_list_response_with_segment_override
):
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = environment_1
    data = {
        "traits": [{"trait_value": "test", "trait_key": "first_name"}],
        "identifier": "do_it_all_in_one_go_identity",
    }
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        content=orjson.dumps(data),
    )
    assert response.json() == {
        "flags": environment_1_feature_states_response_list_response_with_segment_override,
        "traits": data["traits"],
    }
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_post_identity__invalid_trait_data__expected_response(
    mocker: MockerFixture,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch("src.main.environment_service.cache")
    mocked_environment_cache.get_environment.return_value = environment_1
    data = {
        "traits": [{"trait_value": "a" * 2001, "trait_key": "first_name"}],
        "identifier": "do_it_all_in_one_go_identity",
    }

    # When
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        content=orjson.dumps(data),
    )

    # Then
    assert response.status_code == 422
    assert response.json()["detail"][-1]["loc"] == ["body", "traits", 0, "trait_value"]
    assert response.json()["detail"][-1]["type"] == "value_error.any_str.max_length"
