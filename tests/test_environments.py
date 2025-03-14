import copy
import unittest.mock
from datetime import datetime

import httpx
import pytest
from freezegun import freeze_time
from orjson import orjson
from pytest_mock import MockerFixture

from edge_proxy.environments import EnvironmentService
from edge_proxy.exceptions import (
    FeatureNotFoundError,
    UnknownEnvironmentKeyError,
)
from edge_proxy.models import IdentityWithTraits
from edge_proxy.settings import (
    EndpointCacheSettings,
    EndpointCachesSettings,
    AppSettings,
)
from tests.fixtures.response_data import environment_1, environment_1_api_key

client_key_2 = "test_env_key_2"

settings = AppSettings(
    api_url="http://127.0.0.1:8000/api/v1",
    environment_key_pairs=[
        {"server_side_key": "ser.key1", "client_side_key": environment_1_api_key},
        {"server_side_key": "ser.key2", "client_side_key": client_key_2},
    ],
)
now = datetime.now()


@pytest.mark.asyncio
async def test_refresh_makes_correct_http_call(mocker: MockerFixture):
    # Given
    mock_client = mocker.AsyncMock()
    mock_client.get.side_effect = [
        unittest.mock.Mock(text='{"key1": "value1"}'),
        unittest.mock.Mock(text='{"key2": "value2"}'),
    ]

    environment_service = EnvironmentService(client=mock_client, settings=settings)

    # When
    with freeze_time(now):
        await environment_service.refresh_environment_caches()

    # Then
    mock_client.get.assert_has_calls(
        [
            mocker.call(
                url=f"{settings.api_url}/environment-document/",
                headers={
                    "X-Environment-Key": settings.environment_key_pairs[
                        0
                    ].server_side_key
                },
            ),
            mocker.call(
                url=f"{settings.api_url}/environment-document/",
                headers={
                    "X-Environment-Key": settings.environment_key_pairs[
                        1
                    ].server_side_key
                },
            ),
        ]
    )
    assert environment_service.last_updated_at == now


@pytest.mark.asyncio
async def test_refresh_does_not_update_last_updated_at_if_any_request_fails(
    mocker: MockerFixture,
):
    # Given
    mock_client = mocker.AsyncMock()
    mock_client.get.side_effect = [
        httpx.ConnectTimeout("timeout"),
        unittest.mock.Mock(text='{"key2": "value2"}'),
    ]
    environment_service = EnvironmentService(client=mock_client, settings=settings)

    # When
    await environment_service.refresh_environment_caches()

    # Then
    assert environment_service.last_updated_at is None


@pytest.mark.asyncio
async def test_get_environment_works_correctly(mocker: MockerFixture):
    # Given
    mock_client = mocker.AsyncMock()
    doc_1 = {"key1": "value1"}
    doc_2 = {"key2": "value2"}

    mock_client.get.side_effect = [
        mocker.MagicMock(text=orjson.dumps(doc_1), raise_for_status=lambda: None),
        mocker.MagicMock(text=orjson.dumps(doc_2), raise_for_status=lambda: None),
    ]

    environment_service = EnvironmentService(settings=settings, client=mock_client)

    # When
    await environment_service.refresh_environment_caches()

    # Next, test that get environment return correct document
    assert (
        environment_service.get_environment(
            settings.environment_key_pairs[0].client_side_key
        )
        == doc_1
    )
    assert (
        environment_service.get_environment(
            settings.environment_key_pairs[1].client_side_key
        )
        == doc_2
    )
    assert mock_client.get.call_count == 2

    # Next, let's verify that any additional call to get_environment does not call fetch document
    environment_service.get_environment(
        settings.environment_key_pairs[0].client_side_key
    )
    environment_service.get_environment(
        settings.environment_key_pairs[1].client_side_key
    )
    assert mock_client.get.call_count == 2


def test_get_environment_raises_for_unknown_keys():
    environment_service = EnvironmentService(settings=settings)
    with pytest.raises(UnknownEnvironmentKeyError):
        environment_service.get_environment("test_env_key_unknown")


@pytest.mark.asyncio
async def test_refresh_environment_caches_clears_endpoint_caches_if_environment_changes(
    mocker: MockerFixture,
) -> None:
    # Given
    # we create a new settings object which includes caching settings
    _settings = AppSettings(
        environment_key_pairs=[
            {"client_side_key": environment_1_api_key, "server_side_key": "ser.key"}
        ],
        endpoint_caches=EndpointCachesSettings(
            flags=EndpointCacheSettings(use_cache=True),
            identities=EndpointCacheSettings(use_cache=True),
        ),
    )

    # let's create a modified environment document
    modified_document = copy.deepcopy(environment_1)
    modified_document["feature_states"].pop()

    # and set up the client to return the initial document twice and
    # subsequently the modified one
    mocked_client = mocker.AsyncMock()
    mocked_client.get.side_effect = [
        mocker.MagicMock(
            text=orjson.dumps(environment_1), raise_for_status=lambda: None
        ),
        mocker.MagicMock(
            text=orjson.dumps(environment_1), raise_for_status=lambda: None
        ),
        mocker.MagicMock(
            text=orjson.dumps(modified_document), raise_for_status=lambda: None
        ),
    ]

    # Now let's create the environment service, refresh the environment caches and
    # make a call to get_flags_response_data method. This will initialise the LRU
    # cache on the get_flags_response_data method.
    environment_service = EnvironmentService(settings=_settings, client=mocked_client)
    await environment_service.refresh_environment_caches()
    environment_service.get_flags_response_data(environment_1_api_key)
    assert environment_service.get_flags_response_data.cache_info().currsize == 1

    # Refreshing the environment caches a second time shouldn't clear the cache
    # since the environment document is the same as what's in the environment cache.
    await environment_service.refresh_environment_caches()
    assert environment_service.get_flags_response_data.cache_info().currsize == 1

    # When
    # We refresh the environment caches again (which should return a modified environment)
    await environment_service.refresh_environment_caches()

    # Then
    # The LRU cache on the get_flags_response_data method has been reset.
    assert environment_service.get_flags_response_data.cache_info().currsize == 0


@pytest.mark.asyncio
async def test_get_identity_flags_response_skips_cache_for_different_identity(
    mocker: MockerFixture,
) -> None:
    # Given
    # we create a new settings object which includes caching settings
    _settings = AppSettings(
        environment_key_pairs=[
            {"client_side_key": environment_1_api_key, "server_side_key": "ser.key"}
        ],
        endpoint_caches=EndpointCachesSettings(
            identities=EndpointCacheSettings(use_cache=True),
        ),
    )

    mocked_client = mocker.AsyncMock()
    mocked_client.get.return_value = mocker.MagicMock(
        text=orjson.dumps(environment_1), raise_for_status=lambda: None
    )

    environment_service = EnvironmentService(settings=_settings, client=mocked_client)
    await environment_service.refresh_environment_caches()

    # When
    # We retrieve the flags for 2 separate identities
    environment_service.get_identity_response_data(
        IdentityWithTraits(identifier="foo"), environment_1_api_key
    )
    environment_service.get_identity_response_data(
        IdentityWithTraits(identifier="bar"), environment_1_api_key
    )

    # Then
    # we get 2 cache misses
    assert environment_service.get_identity_response_data.cache_info().currsize == 2
    assert environment_service.get_identity_response_data.cache_info().misses == 2
    assert environment_service.get_identity_response_data.cache_info().hits == 0


@pytest.mark.asyncio
async def test_get_flags_response_data_skips_filter_for_server_key(
    mocker: MockerFixture,
) -> None:
    # Given
    # We create a new settings object that contains a server key as a client_side_key
    api_key = "ser." + environment_1_api_key
    _settings = AppSettings(
        environment_key_pairs=[
            {"client_side_key": api_key, "server_side_key": "ser.key"}
        ]
    )

    mocked_client = mocker.AsyncMock()
    mocked_client.get.return_value = mocker.MagicMock(
        text=orjson.dumps(environment_1), raise_for_status=lambda: None
    )

    environment_service = EnvironmentService(settings=_settings, client=mocked_client)
    await environment_service.refresh_environment_caches()

    # When
    # We retrieve the flag response data
    flags = environment_service.get_flags_response_data(api_key)
    specific_flag = environment_service.get_flags_response_data(api_key, "feature_3")

    # Then
    # we get the server-side only flag
    assert len(flags) == 3
    assert flags[2].get("feature").get("name") == "feature_3"
    assert specific_flag.get("feature").get("name") == "feature_3"


@pytest.mark.asyncio
async def test_get_flags_response_data_filters_server_side_features_for_client_key(
    mocker: MockerFixture,
) -> None:
    # Given
    # We create a new settings object that contains a client side key
    _settings = AppSettings(
        environment_key_pairs=[
            {"client_side_key": environment_1_api_key, "server_side_key": "ser.key"}
        ]
    )

    mocked_client = mocker.AsyncMock()
    mocked_client.get.return_value = mocker.MagicMock(
        text=orjson.dumps(environment_1), raise_for_status=lambda: None
    )

    environment_service = EnvironmentService(settings=_settings, client=mocked_client)
    await environment_service.refresh_environment_caches()

    # When
    # We retrieve the flag response data
    flags = environment_service.get_flags_response_data(environment_1_api_key)
    with pytest.raises(FeatureNotFoundError):
        environment_service.get_flags_response_data(environment_1_api_key, "feature_3")

    # Then
    # we only get the two client side flags
    assert len(flags) == 2


@pytest.mark.asyncio
async def test_get_identity_flags_response_skips_filter_for_server_key(
    mocker: MockerFixture,
) -> None:
    # Given
    # We create a new settings object that contains a server key as a client_side_key
    api_key = "ser." + environment_1_api_key
    _settings = AppSettings(
        environment_key_pairs=[
            {"client_side_key": api_key, "server_side_key": "ser.key"}
        ]
    )

    mocked_client = mocker.AsyncMock()
    mocked_client.get.return_value = mocker.MagicMock(
        text=orjson.dumps(environment_1), raise_for_status=lambda: None
    )

    environment_service = EnvironmentService(settings=_settings, client=mocked_client)
    await environment_service.refresh_environment_caches()

    # When
    # We retrieve the flags for an identity
    result = environment_service.get_identity_response_data(
        IdentityWithTraits(identifier="foo"), api_key
    )

    # Then
    # we get the server-side only flag
    flags = result.get("flags")
    assert len(flags) == 3
    assert flags[2].get("feature").get("name") == "feature_3"
