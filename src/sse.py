import asyncio
import json
from datetime import datetime
from functools import lru_cache
from typing import Optional

import redis
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from redis.exceptions import ConnectionError
from sse_starlette.sse import EventSourceResponse

from .settings import Settings

router = APIRouter()


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
redis_connection = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
)


async def is_authenticated(
    authorization: str = Header(), settings: Settings = Depends(get_settings)
):
    if authorization != f"Token {settings.sse_authentication_token}":
        raise HTTPException(status_code=401, detail="Invalid authorization header")


@router.get("/sse/health")
async def health_check():
    "Returns 200 if we can ping redis"
    try:
        redis_connection.ping()
    except ConnectionError:
        return JSONResponse(
            status_code=500, content={"status": "Unable to connect to redis"}
        )
    return {"status": "ok"}


@router.post(
    "/sse/environments/{environment_key}/queue-change",
    dependencies=[Depends(is_authenticated)],
)
async def queue_environment_changes(
    environment_key: str, updated_at: datetime = Body(embed=True)
):
    redis_connection.set(environment_key, updated_at.timestamp())


@router.get("/sse/environments/{environment_key}/stream")
async def stream_environment_changes(
    request: Request, environment_key: str, settings: Settings = Depends(get_settings)
):
    started_at = datetime.now()
    last_updated_at = None

    async def get_updated_at() -> Optional[int]:
        nonlocal last_updated_at
        updated_at = redis_connection.get(environment_key)
        if last_updated_at == updated_at:
            return None

        last_updated_at = updated_at
        return updated_at

    async def event_generator():
        while True:
            # If client closes the connection, or the stream is open for more than `MAX_AGE` seconds
            # stop sending events
            if (
                await request.is_disconnected()
                or (datetime.now() - started_at).total_seconds()
                > settings.max_stream_age
            ):
                break

            if updated_at := await get_updated_at():
                yield {
                    "event": "environment_updated",
                    "data": json.dumps({"updated_at": float(updated_at)}),
                    "retry": settings.retry_timeout,
                }
            await asyncio.sleep(settings.stream_delay)

    return EventSourceResponse(
        event_generator(), headers={"Cache-Control": "public, max-age=29"}
    )
