import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.settings import Settings
from src.sse import engine
from src.sse import get_settings
from src.sse_models import Environment


def get_settings_override():
    return Settings(max_stream_age=5, stream_delay=1)


app.dependency_overrides[get_settings] = get_settings_override


@pytest.mark.asyncio
async def test_queue_environment_changes_creates_environment_in_db(client):
    # Given
    environment_key = "some_key"

    # When
    response = client.post(f"/sse/environments/{environment_key}/queue-change")

    # Then
    async with AsyncSession(engine) as session:
        environment = await session.get(Environment, environment_key)
        assert environment.key == environment_key

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_stream_environment_changes(client):
    # Given
    environment_key = "some_key"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, let's create a task that makes a request to /stream endpoint
        stream_response_task = asyncio.create_task(
            ac.get(f"/sse/environments/{environment_key}/stream")
        )
        # Now, let's yield control back to event loop so that it can run our task
        await asyncio.sleep(0.1)

        # Next, let's update the environment
        await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Now, let's wait for the change to be streamed
        await asyncio.sleep(2)

        # Next, let's update the environment once again
        await ac.post(f"/sse/environments/{environment_key}/queue-change")

        # Finally, let's wait for the stream to finish
        response = await stream_response_task

        # Then
        expected_response = (
            "event: environment_updated\r\ndata: None\r\nretry: 15000\r\n\r\nevent:"
            " environment_updated\r\ndata: None\r\nretry: 15000\r\n\r\n"
        )

    assert response.status_code == 200
    assert response.text == expected_response
