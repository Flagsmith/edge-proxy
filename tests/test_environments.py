import json
import unittest.mock
from datetime import datetime

import httpx
import pytest
from freezegun import freeze_time
from orjson import orjson
from pytest_mock import MockerFixture

from src.cache import LocalMemEnvironmentsCache
from src.environments import EnvironmentService
from src.exceptions import FlagsmithUnknownKeyError
from src.settings import Settings

settings = Settings(
    api_url="http://127.0.0.1:8000/api/v1",
    environment_key_pairs=[
        {"server_side_key": "ser.key1", "client_side_key": "test_env_key_1"},
        {"server_side_key": "ser.key2", "client_side_key": "test_env_key_2"},
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
async def test_refresh_does_not_update_last_updated_at_if_any_request_fails(mocker: MockerFixture):
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
        mocker.MagicMock(text=orjson.dumps(doc_2), raise_for_status=lambda: None)
    ]

    environment_service = EnvironmentService(settings=settings, client=mock_client)

    # When
    await environment_service.refresh_environment_caches()

    # Next, test that get environment return correct document
    assert (
        environment_service.get_environment(settings.environment_key_pairs[0].client_side_key)
        == doc_1
    )
    assert (
        environment_service.get_environment(settings.environment_key_pairs[1].client_side_key)
        == doc_2
    )
    assert mock_client.get.call_count == 2

    # Next, let's verify that any additional call to get_environment does not call fetch document
    environment_service.get_environment(settings.environment_key_pairs[0].client_side_key)
    environment_service.get_environment(settings.environment_key_pairs[1].client_side_key)
    assert mock_client.get.call_count == 2


def test_get_environment_raises_for_unknown_keys():
    environment_service = EnvironmentService(settings=settings)
    with pytest.raises(FlagsmithUnknownKeyError):
        environment_service.get_environment("test_env_key_unknown")
