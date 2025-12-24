import typing

import orjson
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from edge_proxy.main import serve
from edge_proxy.settings import EnvironmentKeyPair
from tests.fixtures.response_data import (
    environment_1,
    environment_with_hide_disabled_flags,
    environment_with_multivariate_feature,
)

if typing.TYPE_CHECKING:
    from edge_proxy.environments import EnvironmentService


def test_get_flags(
    mocked_environment_cache,
    environment_1_feature_states_response_list: list[dict],
    client: TestClient,
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )
    assert response.json() == environment_1_feature_states_response_list
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature(
    mocked_environment_cache,
    environment_1_feature_states_response_list: list[dict],
    client: TestClient,
) -> None:
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = environment_1
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_1"},
    )
    assert response.json() == environment_1_feature_states_response_list[0]
    mocked_environment_cache.get_environment.assert_called_with(environment_key)


def test_get_flags_single_feature__server_key_only_feature__return_expected(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
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
    mocked_environment_cache,
    client: TestClient,
):
    environment_key = "unknown_environment_key"
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
    mocked_environment_cache,
    environment_1_feature_states_response_list_response_with_segment_override,
    client: TestClient,
):
    environment_key = "test_environment_key"
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
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
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
    ]
    assert response.json()["detail"][-1]["type"] == "string_too_long"


def test_get_identities(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    x_environment_key = "test_environment_key"
    identifier = "test_identifier"

    mocked_environment_cache.get_environment.return_value = environment_1

    response = client.get(
        "/api/v1/identities/",
        headers={"x-environment-key": x_environment_key},
        params={"identifier": identifier},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["traits"] == []
    assert data["flags"]


def test_serve_passes_proxy_headers_setting(mocker: MockerFixture) -> None:
    # Given
    mock_settings = mocker.patch("edge_proxy.main.get_settings")
    mock_settings.return_value.server.proxy_headers = True

    mock_uvicorn = mocker.patch("edge_proxy.main.uvicorn.run")

    # When
    serve()

    # Then
    _, kwargs = mock_uvicorn.call_args
    assert kwargs.get("proxy_headers") is True


def test_get_environment_document(
    mocker: MockerFixture,
    client: TestClient,
) -> None:
    # Given
    environment_key_pairs = [
        EnvironmentKeyPair(server_side_key="ser.good", client_side_key="foo")
    ]
    mocker.patch(
        "edge_proxy.server.settings.environment_key_pairs", environment_key_pairs
    )
    mocker.patch(
        "edge_proxy.server.environment_service.cache"
    ).get_environment.return_value = environment_1

    # When
    response = client.get(
        "/api/v1/environment-document",
        headers={"X-Environment-Key": environment_key_pairs[0].server_side_key},
    )

    # Then
    assert response.status_code == 200
    assert response.json() == environment_1


def test_get_environment_document_missing_key(
    client: TestClient,
) -> None:
    # When
    response = client.get(
        "/api/v1/environment-document",
    )
    # Then
    assert response.status_code == 401


def test_get_environment_document_wrong_key(
    client: TestClient,
) -> None:
    # When
    response = client.get(
        "/api/v1/environment-document", headers={"X-Environment-Key": "ser.bad"}
    )
    # Then
    assert response.status_code == 401


def test_get_flags__client_key__hide_disabled_flags_enabled__only_returns_enabled_flags(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = (
        environment_with_hide_disabled_flags
    )

    # When
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )

    # Then
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) == 1
    assert flags[0]["feature"]["name"] == "feature_2"
    assert flags[0]["enabled"] is True


def test_get_flags__client_key__hide_disabled_flags_disabled__returns_all_flags(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = environment_1

    # When
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )

    # Then
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) == 2


def test_get_flags__server_key__hide_disabled_flags_enabled__returns_all_flags(
    mocker: MockerFixture,
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    server_key = "ser.test_server_key"
    client_key = "test_client_key"
    mocked_environment_cache.get_environment.return_value = (
        environment_with_hide_disabled_flags
    )
    mocker.patch(
        "edge_proxy.server.environment_service._get_client_key_from_server_key",
        return_value=client_key,
    )

    # When
    response = client.get("/api/v1/flags", headers={"X-Environment-Key": server_key})

    # Then
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) == 3
    # Verify disabled flags are included (bypasses hide_disabled_flags for server keys)
    flag_names = {f["feature"]["name"] for f in flags}
    assert "feature_1" in flag_names  # disabled flag
    assert "feature_2" in flag_names  # enabled flag
    assert "feature_3" in flag_names  # disabled flag


def test_get_flags__client_key__hide_disabled_flags_enabled__single_disabled_feature__returns_404(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = (
        environment_with_hide_disabled_flags
    )

    # When
    response = client.get(
        "/api/v1/flags",
        headers={"X-Environment-Key": environment_key},
        params={"feature": "feature_1"},
    )

    # Then
    assert response.status_code == 404


def test_post_identity__client_key__hide_disabled_flags_enabled__only_returns_enabled_flags(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = (
        environment_with_hide_disabled_flags
    )
    data = {
        "identifier": "test_identifier",
        "traits": [],
    }

    # When
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        content=orjson.dumps(data),
    )

    # Then
    assert response.status_code == 200
    response_data = response.json()
    flags = response_data["flags"]
    assert len(flags) == 1
    assert flags[0]["feature"]["name"] == "feature_2"
    assert flags[0]["enabled"] is True


def test_post_identity__client_key__hide_disabled_flags_disabled__returns_all_flags(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = environment_1
    data = {
        "identifier": "test_identifier",
        "traits": [],
    }

    # When
    response = client.post(
        "/api/v1/identities/",
        headers={"X-Environment-Key": environment_key},
        content=orjson.dumps(data),
    )

    # Then
    assert response.status_code == 200
    response_data = response.json()
    flags = response_data["flags"]
    assert len(flags) == 2


def test_get_flags__multivariate_feature__returns_correct_type(
    mocked_environment_cache,
    client: TestClient,
) -> None:
    # Given
    environment_key = "test_environment_key"
    mocked_environment_cache.get_environment.return_value = (
        environment_with_multivariate_feature
    )

    # When
    response = client.get(
        "/api/v1/flags", headers={"X-Environment-Key": environment_key}
    )

    # Then
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) == 2

    mv_flag = next(f for f in flags if f["feature"]["name"] == "mv_feature")
    assert mv_flag["feature"]["type"] == "MULTIVARIATE"
    assert mv_flag["feature"]["id"] == 4
    assert mv_flag["enabled"] is True

    standard_flag = next(f for f in flags if f["feature"]["name"] == "feature_1")
    assert standard_flag["feature"]["type"] == "STANDARD"
