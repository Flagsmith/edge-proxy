import asyncio
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.settings import Settings
from src.sse import engine
from src.sse import get_settings
from src.sse_models import Environment
from src.sse_models import Identity


def get_settings_override():
    return Settings(
        max_stream_age=3, stream_delay=1, sse_authentication_token=auth_token
    )


auth_token = "test_token"
auth_header = {"authorization": f"Token {auth_token}"}

app.dependency_overrides[get_settings] = get_settings_override


def test_health_check_returns_200_if_db_is_configured(client):
    response = client.get("/sse/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_returns_500_if_db_is_not_configured():
    client = TestClient(app)
    response = client.get("/sse/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}


@pytest.mark.asyncio
async def test_queue_environment_changes_creates_environment_in_db(client):
    # Given
    environment_key = "some_key"

    # When
    response = client.post(
        f"/sse/environments/{environment_key}/queue-change",
        headers=auth_header,
    )

    # Then
    assert response.status_code == 200
    async with AsyncSession(engine) as session:
        environment = await session.get(Environment, environment_key)
        assert environment.key == environment_key


@pytest.mark.asyncio
async def test_queue_environment_changes_returns_401_if_token_is_not_valid(
    client,
):
    # Given
    environment_key = "some_key"

    # When
    response = client.post(
        f"/sse/environments/{environment_key}/queue-change",
        headers={"authorization": "not_a_valid_token"},
    )
    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authorization header"


@pytest.mark.asyncio
async def test_queue_identity_changes_creates_identity_in_db(client):
    # Given
    environment_key = "some_key"
    identifier = "some_identity"
    # When
    response = client.post(
        f"/sse/environments/{environment_key}/identities/queue-change",
        json={"identifier": identifier},
        headers=auth_header,
    )

    # Then
    assert response.status_code == 200

    async with AsyncSession(engine) as session:
        identity = await session.get(Identity, identifier)
        assert identity.identifier == identifier
        assert identity.environment_key == environment_key


@pytest.mark.asyncio
async def test_queue_identity_changes_bulk_creates_identities_in_db(client):
    # Given
    environment_key = "some_key"
    identifier_1 = "some_identity"
    identifier_2 = "some_other_identity"
    payload = {"identifiers": [identifier_1, identifier_2]}

    # When
    response = client.post(
        f"/sse/environments/{environment_key}/identities/queue-change/bulk",
        json=payload,
        headers=auth_header,
    )

    # Then
    assert response.status_code == 200

    async with AsyncSession(engine) as session:
        identity_1 = await session.get(Identity, identifier_1)
        assert identity_1.identifier == identifier_1
        assert identity_1.environment_key == environment_key

        identity_2 = await session.get(Identity, identifier_2)
        assert identity_2.identifier == identifier_2
        assert identity_2.environment_key == environment_key


@pytest.mark.asyncio
async def test_queue_identity_changes_returns_401_if_token_is_not_valid(client):
    # Given
    environment_key = "some_key"
    identifier = "some_identity"
    # When
    response = client.post(
        f"/sse/environments/{environment_key}/identities/queue-change",
        json={"identifier": identifier},
        headers={"authorization": "not_a_valid_token"},
    )

    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authorization header"


@pytest.mark.asyncio
async def test_stream_changes(client):
    # Given
    environment_key = "some_key"

    async with AsyncClient(app=app, base_url="http://test", headers=auth_header) as ac:
        # First, let's create a task that makes a request to /stream endpoint
        stream_response_task = asyncio.create_task(
            ac.get(f"/sse/environments/{environment_key}/stream")
        )
        # Now, let's yield control back to event loop so that it can run our task
        await asyncio.sleep(0.1)
        first_last_updated_at = datetime.now()
        print("first_last_updated_at", first_last_updated_at)
        with freeze_time(first_last_updated_at, ignore=["asyncio"]):
            # Next, let's update the environment
            await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Now, let's wait for the change to be streamed
        await asyncio.sleep(1)

        second_last_updated_at = datetime.now()
        with freeze_time(second_last_updated_at, ignore=["asyncio"]):
            # Next, let's update the environment once again
            await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Finally, let's wait for the stream to finish
        response = await stream_response_task

        # Then
        expected_response = (
            "event: environment_updated\r\ndata: {'last_updated_at': %0.6f}\r\nretry: 15000\r\n\r\nevent:"
            " environment_updated\r\ndata: {'last_updated_at': %0.6f}\r\nretry: 15000\r\n\r\n"
            % (first_last_updated_at.timestamp(), second_last_updated_at.timestamp())
        )
    assert response.status_code == 200
    assert response.text == expected_response
