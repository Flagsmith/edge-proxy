import asyncio
from datetime import datetime
from datetime import timezone

import pytest
from httpx import AsyncClient

from src.main import app
from src.settings import Settings
from src.sse import get_settings
from src.sse import redis_connection


def get_settings_override():
    return Settings(
        max_stream_age=3, stream_delay=0.2, sse_authentication_token=auth_token
    )


auth_token = "test_token"
auth_header = {"authorization": f"Token {auth_token}"}

app.dependency_overrides[get_settings] = get_settings_override


def test_health_check_returns_200(client):
    response = client.get("/sse/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_queue_environment_changes_creates_environment_in_db(client):
    # Given
    environment_key = "some_key"
    payload = {"updated_at": datetime.now(tz=timezone.utc).isoformat()}

    # When
    response = client.post(
        f"/sse/environments/{environment_key}/queue-change",
        headers=auth_header,
        json=payload,
    )

    # Then
    assert response.status_code == 200
    assert redis_connection.exists(environment_key) == 1


@pytest.mark.asyncio
async def test_queue_environment_changes_returns_401_if_token_is_not_valid(
    client,
):
    # Given
    environment_key = "some_key"
    payload = {"updated_at": datetime.now(tz=timezone.utc).isoformat()}

    # When
    response = client.post(
        f"/sse/environments/{environment_key}/queue-change",
        headers={"authorization": "not_a_valid_token"},
        json=payload,
    )
    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authorization header"


@pytest.mark.asyncio
async def test_stream_changes(client):
    # Given
    environment_key = "environment_key"

    async with AsyncClient(app=app, base_url="http://test", headers=auth_header) as ac:
        # First, let's create a task that makes a request to /stream endpoint
        stream_response_task = asyncio.create_task(
            ac.get(f"/sse/environments/{environment_key}/stream")
        )
        # Now, let's yield control back to event loop so that it can run our task
        await asyncio.sleep(0.1)
        first_last_updated_at = datetime.now()
        # Next, let's update the environment
        await ac.post(
            f"/sse/environments/{environment_key}/queue-change",
            json={"updated_at": first_last_updated_at.isoformat()},
        )

        # Now, let's wait for the change to be streamed
        await asyncio.sleep(1)

        second_last_updated_at = datetime.now()

        # Next, let's update the environment once again
        await ac.post(
            f"/sse/environments/{environment_key}/queue-change",
            json={"updated_at": second_last_updated_at.isoformat()},
        )

        # Finally, let's wait for the stream to finish
        response = await stream_response_task

        # Then - we only got two messages
        expected_response = (
            'event: environment_updated\r\ndata: {"updated_at": %0.6f}\r\nretry: 15000\r\n\r\nevent:'
            ' environment_updated\r\ndata: {"updated_at": %0.6f}\r\nretry: 15000\r\n\r\n'
            % (first_last_updated_at.timestamp(), second_last_updated_at.timestamp())
        )
    assert response.status_code == 200
    assert response.text == expected_response
