import asyncio
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sse_starlette.sse import EventSourceResponse

from .settings import Settings
from .sse_models import Base
from .sse_models import Environment

engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

router = APIRouter()


@lru_cache()
def get_settings():
    return Settings()


@router.on_event("startup")
async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@router.on_event("shutdown")
async def drop_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@router.post("/sse/environments/{environment_key}/queue-change")
async def queue_environment_changes(environment_key: str):
    async with AsyncSession(engine, autoflush=True) as session:
        statement = text(
            """INSERT OR REPLACE INTO environment(key) VALUES(:environment_key)"""
        )
        await session.execute(statement, {"environment_key": environment_key})
        await session.commit()
    return JSONResponse(status_code=200)


@router.get("/sse/environments/{environment_key}/stream")
async def stream_environment_changes(
    request: Request, environment_key: str, settings: Settings = Depends(get_settings)
):
    session = AsyncSession(engine)
    started_at = datetime.now()

    async def did_environment_change():
        environment_updated = False
        environment = await session.get(Environment, environment_key)
        if environment:
            environment_updated = True
            await session.delete(environment)

        await session.commit()
        return environment_updated

    async def event_generator():
        while True:
            # If client closes connection, or the stream is open for more than `MAX_AGE` seconds
            # stop sending events
            if (
                await request.is_disconnected()
                or (datetime.now() - started_at).total_seconds()
                > settings.max_stream_age
            ):
                await session.close()
                break
            if await did_environment_change():
                yield {
                    "event": "environment_updated",
                    "retry": settings.retry_timeout,
                }

            await asyncio.sleep(settings.stream_delay)

    return EventSourceResponse(
        event_generator(), headers={"Cache-Control": "public, max-age=29"}
    )
