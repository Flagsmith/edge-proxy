import json

import requests
from fastapi.testclient import TestClient

from .fixtures.response_data import environment_1
from src.main import app

client = TestClient(app)


def test_health_check_returns_200_if_fetch_document_does_works(mocker):
    mocker.patch("src.main.cache_service")
    response = client.get("/proxy/health")
    assert response.status_code == 200


def test_health_check_deprecated_endpoint_returns_200_if_fetch_document_does_works(
    mocker,
):
    mocker.patch("src.main.cache_service")
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_500_if_fetch_document_raises_error(mocker):
    mocker.patch(
        "src.main.cache_service",
        **{"fetch_document.side_effect": requests.exceptions.HTTPError()},
    )

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
