import asyncio
from datetime import datetime
from datetime import timezone
from functools import lru_cache
from typing import List

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sse_starlette.sse import EventSourceResponse

from .settings import Settings
from .sse_models import Base
from .sse_models import Environment
from .sse_models import Identity

engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

engine.update_execution_options(isolation_level="AUTOCOMMIT")

router = APIRouter()


@lru_cache()
def get_settings():
    return Settings()


async def is_authenticated(
    authorization: str = Header(), settings: Settings = Depends(get_settings)
):
    if authorization != f"Token {settings.sse_authentication_token}":
        raise HTTPException(status_code=401, detail="Invalid authorization header")


@router.on_event("startup")
async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@router.on_event("shutdown")
async def drop_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@router.get("/sse/health")
async def health_check():
    "Returns 200 if the database is properly configured(have required tables)"
    async with AsyncSession(engine, autoflush=True) as session:
        environment_stmt = select(Environment).limit(1)
        identity_stmt = select(Identity).limit(1)
        try:
            await session.execute(environment_stmt)
            await session.execute(identity_stmt)
        except OperationalError:
            return JSONResponse(status_code=500, content={"status": "error"})
        return {"status": "ok"}


@router.post(
    "/sse/environments/{environment_key}/queue-change",
    dependencies=[Depends(is_authenticated)],
)
async def queue_environment_changes(environment_key: str):
    async with AsyncSession(engine, autoflush=True) as session:
        statement = text(
            """INSERT OR REPLACE INTO environment(key, last_updated_at) VALUES(:environment_key, :last_updated_at)"""
        )
        await session.execute(
            statement,
            {
                "environment_key": environment_key,
                "last_updated_at": datetime.now(tz=timezone.utc),
            },
        )


@router.post(
    "/sse/environments/{environment_key}/identities/queue-change",
    dependencies=[Depends(is_authenticated)],
)
async def queue_identity_changes(
    environment_key: str, identifier: str = Body(embed=True)
):
    await Identity.put_identities(engine, environment_key, [identifier])


@router.post(
    "/sse/environments/{environment_key}/identities/queue-change/bulk",
    dependencies=[Depends(is_authenticated)],
)
async def queue_identity_changes_bulk(
    environment_key: str, identifiers: List[str] = Body(embed=True)
):

    await Identity.put_identities(engine, environment_key, identifiers)


@router.get("/sse/environments/{environment_key}/stream")
async def stream_environment_changes(
    request: Request, environment_key: str, settings: Settings = Depends(get_settings)
):
    async with AsyncSession(engine, autoflush=True) as session:
        started_at = datetime.now()

        async def get_last_updated_at() -> int:  # optional
            environment = await session.get(Environment, environment_key)
            if environment:
                return environment.last_updated_at.timestamp()

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

                if last_updated_at := await get_last_updated_at():
                    yield {
                        "event": "environment_updated",
                        "data": {"last_updated_at": last_updated_at},
                        "retry": settings.retry_timeout,
                    }
                await asyncio.sleep(settings.stream_delay)

        return EventSourceResponse(
            event_generator(), headers={"Cache-Control": "public, max-age=29"}
        )
