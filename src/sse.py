import asyncio
from datetime import datetime

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sse_starlette.sse import EventSourceResponse

from .settings import Settings
from .sse_models import Base
from .sse_models import Environment

settings = Settings()
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True, future=True)

router = APIRouter()


@router.on_event("startup")
async def migrate_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@router.post("/sse/environments/{environment_key}/queue-change")
async def environment_updated(environment_key: str):
    async with AsyncSession(engine) as session:
        environment = Environment(key=environment_key)
        await session.merge(environment)
        await session.commit()
    return JSONResponse(status_code=200)


@router.get("/sse/environments/{environment_key}/stream")
async def message_stream(request: Request, environment_key: str):
    session = AsyncSession(engine)
    started_at = datetime.now()

    async def new_messages():
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
            # Checks for new messages and return them to client if any
            if await new_messages():
                yield {
                    "event": "environment_updated",
                    "retry": settings.retry_timeout,
                }

            await asyncio.sleep(settings.stream_delay)

    return EventSourceResponse(
        event_generator(), headers={"Cache-Control": "public, max-age=29"}
    )
