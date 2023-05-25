import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.main import app

from .fixtures.response_data import environment_1

client = TestClient(app)


@pytest.mark.parametrize("endpoint", ["/proxy/health", "/health"])
def test_health_check_returns_200_if_cache_was_updated_recently(mocker, endpoint):
    cache_service = mocker.patch("src.main.cache_service")
    cache_service.last_updated_at = datetime.now()

    response = client.get(endpoint)
    assert response.status_code == 200


def test_health_check_returns_500_if_cache_was_not_updated(mocker):
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}


def test_health_check_returns_500_if_cache_is_stale(mocker):
    cache_service = mocker.patch("src.main.cache_service")
    cache_service.last_updated_at = datetime.now() - timedelta(days=10)
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}


def test_get_flags(mocker, environment_1_feature_states_response_list):
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )
    assert response.json() == environment_1_feature_states_response_list
    mocked_cache_service.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature(mocker, environment_1_feature_states_response_list):
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_1"},
    )
    assert response.json() == environment_1_feature_states_response_list[0]
    mocked_cache_service.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature__server_key_only_feature__return_expected(
    mocker: MockerFixture,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1

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


def test_post_identity_with_traits(
    mocker, environment_1_feature_states_response_list_response_with_segment_override
):
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1
    data = {
        "traits": [{"trait_value": "test", "trait_key": "first_name"}],
        "identifier": "do_it_all_in_one_go_identity",
    }
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        data=json.dumps(data),
    )
    assert response.json() == {
        "flags": environment_1_feature_states_response_list_response_with_segment_override,
        "traits": data["traits"],
    }
    mocked_cache_service.get_environment.assert_called_with(environment_key)
