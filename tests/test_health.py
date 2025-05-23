from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from edge_proxy.settings import HealthCheckSettings

READINESS_ENDPOINTS = [
    "/proxy/health/readiness",
    "/proxy/health",
    "/health",
]


def test_liveness_check(client: TestClient) -> None:
    response = client.get("/proxy/health/liveness")
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", READINESS_ENDPOINTS)
def test_health_check_returns_200_if_cache_was_updated_recently(
    mocker: MockerFixture,
    client: TestClient,
    endpoint: str,
) -> None:
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = datetime.now()

    response = client.get(endpoint)
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", READINESS_ENDPOINTS)
def test_health_check_returns_503_if_cache_was_not_updated(
    client: TestClient,
    endpoint: str,
) -> None:
    response = client.get(endpoint)
    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "reason": "environment document(s) not updated.",
        "last_successful_update": None,
    }


@pytest.mark.parametrize("endpoint", READINESS_ENDPOINTS)
def test_health_check_returns_503_if_cache_is_stale(
    mocker: MockerFixture,
    client: TestClient,
    endpoint: str,
) -> None:
    last_updated_at = datetime.now() - timedelta(days=10)
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = last_updated_at

    response = client.get(endpoint)

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "reason": "environment document(s) stale.",
        "last_successful_update": last_updated_at.isoformat(),
    }


@pytest.mark.parametrize("endpoint", READINESS_ENDPOINTS)
def test_health_check_returns_200_if_cache_is_never_stale(
    mocker: MockerFixture,
    client: TestClient,
    endpoint: str,
) -> None:
    # Given
    health_check = HealthCheckSettings(environment_update_grace_period_seconds=None)
    mocker.patch("edge_proxy.server.settings.health_check", health_check)

    last_updated_at = datetime.now() - timedelta(days=10)
    mocked_environment_service = mocker.patch("edge_proxy.server.environment_service")
    mocked_environment_service.last_updated_at = last_updated_at

    # When
    response = client.get(endpoint)

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "reason": None,
        "last_successful_update": last_updated_at.isoformat(),
    }
