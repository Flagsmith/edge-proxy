import json

from fastapi.testclient import TestClient

from src.main import app

from .fixtures.dynamodb import environment_1_document

client = TestClient(app)


def test_get_flags(mocker, environment_1_feature_states_response_list):
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1_document
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )
    assert response.json() == environment_1_feature_states_response_list
    mocked_cache_service.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature(mocker, environment_1_feature_states_response_list):
    environment_key = "test_environment_key"
    mocked_cache_service = mocker.patch("src.main.cache_service")
    mocked_cache_service.get_environment.return_value = environment_1_document
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
    mocked_cache_service.get_environment.return_value = environment_1_document
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
        "identifier": data["identifier"],
    }
    mocked_cache_service.get_environment.assert_called_with(environment_key)
