import asyncio
from hashlib import sha1

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.settings import Settings
from src.sse import engine
from src.sse import get_settings
from src.sse_models import Environment
from src.sse_models import Identity


def get_settings_override():
    return Settings(max_stream_age=5, stream_delay=1, authentication_token=auth_token)


auth_token = "test_token"
auth_header = {"authorization": f"Token {auth_token}"}

app.dependency_overrides[get_settings] = get_settings_override


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
    identifier = "some_identity"

    async with AsyncClient(app=app, base_url="http://test", headers=auth_header) as ac:
        # First, let's create a task that makes a request to /stream endpoint
        stream_response_task = asyncio.create_task(
            ac.get(f"/sse/environments/{environment_key}/stream")
        )
        # Now, let's yield control back to event loop so that it can run our task
        await asyncio.sleep(0.1)

        # Next, let's update the environment
        await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Now, let's wait for the change to be streamed
        await asyncio.sleep(1)

        # Next, let's update the identity
        await ac.post(
            f"/sse/environments/{environment_key}/identities/queue-change",
            json={"identifier": identifier},
        )
        # again wait for it to be streamed
        await asyncio.sleep(1)

        # Next, let's update the environment once again
        await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Finally, let's wait for the stream to finish
        response = await stream_response_task

        # Then
        expected_response = (
            "event: environment_updated\r\ndata: None\r\nretry: 15000\r\n\r\nevent:"
            " identity_updated\r\ndata: {'hashed_identifier': '%s'}\r\n\r\nevent:"
            " environment_updated\r\ndata: None\r\nretry: 15000\r\n\r\n"
            % sha1(identifier.encode()).hexdigest()
        )

    assert response.status_code == 200
    assert response.text == expected_response
