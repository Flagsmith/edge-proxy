from datetime import datetime, timedelta
import typing

import orjson
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from edge_proxy.settings import AppSettings, HealthCheckSettings
from tests.fixtures.response_data import environment_1

if typing.TYPE_CHECKING:
    from edge_proxy.environments import EnvironmentService


@pytest.mark.parametrize("endpoint", ["/proxy/health", "/health"])
def test_health_check_returns_200_if_cache_was_updated_recently(
    mocker: MockerFixture,
    endpoint: str,
    client: TestClient,
) -> None:
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = datetime.now()

    response = client.get(endpoint)
    assert response.status_code == 200


def test_health_check_returns_500_if_cache_was_not_updated(
    client: TestClient,
) -> None:
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {
        "status": "error",
        "reason": "environment document(s) not updated.",
        "last_successful_update": None,
    }


def test_health_check_returns_500_if_cache_is_stale(
    mocker: MockerFixture,
    client: TestClient,
) -> None:
    last_updated_at = datetime.now() - timedelta(days=10)
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = last_updated_at
    response = client.get("/proxy/health")
    assert response.status_code == 500
    assert response.json() == {
        "status": "error",
        "reason": "environment document(s) stale.",
        "last_successful_update": last_updated_at.isoformat(),
    }


def test_health_check_returns_200_if_cache_is_stale_and_health_check_configured_correctly(
    mocker: MockerFixture,
    client: TestClient,
) -> None:
    # Given
    settings = AppSettings(
        health_check=HealthCheckSettings(count_stale_documents_as_failing=False)
    )
    mocker.patch("edge_proxy.server.settings", settings)

    last_updated_at = datetime.now() - timedelta(days=10)
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = last_updated_at

    # When
    response = client.get("/proxy/health")

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "reason": None,
        "last_successful_update": last_updated_at.isoformat(),
    }


def test_get_flags(
    mocker: MockerFixture,
    environment_1_feature_states_response_list: list[dict],
    client: TestClient,
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
    mocked_environment_cache.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )
    assert response.json() == environment_1_feature_states_response_list
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature(
    mocker: MockerFixture,
    environment_1_feature_states_response_list: list[dict],
    client: TestClient,
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
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
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
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


def test_get_flags_unknown_key(
    mocker: MockerFixture,
    client: TestClient,
):
    environment_key = "unknown_environment_key"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
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
    mocker,
    environment_1_feature_states_response_list_response_with_segment_override,
    client: TestClient,
):
    environment_key = "test_environment_key"
    identifier = "do_it_all_in_one_go_identity"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
    mocked_environment_cache.get_environment.return_value = environment_1
    mocked_environment_cache.get_identity.return_value = {
        "environment_api_key": environment_key,
        "identifier": identifier,
    }
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
    mocked_environment_cache.get_identity.assert_called_with(
        environment_api_key=environment_key,
        identifier=identifier,
    )


def test_post_identity__environment_with_overrides__expected_response(
    environment_service: "EnvironmentService",
    environment_1_feature_states_response_list_response_with_identity_override: list[
        dict[str, typing.Any]
    ],
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    identifier = "overridden-id"

    environment_service.cache.put_environment(environment_key, environment_1)

    data = {"identifier": identifier}

    # When
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        content=orjson.dumps(data),
    )

    # Then
    assert response.json() == {
        "flags": environment_1_feature_states_response_list_response_with_identity_override,
        "traits": [],
    }


def test_post_identity__invalid_trait_data__expected_response(
    mocker: MockerFixture,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache = mocker.patch(
        "edge_proxy.server.environment_service.cache"
    )
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
    assert response.json()["detail"][-1]["loc"] == [
        "body",
        "traits",
        0,
        "trait_value",
        "constrained-str",
    ]
    assert response.json()["detail"][-1]["type"] == "string_too_long"
