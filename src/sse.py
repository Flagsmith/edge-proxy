import asyncio
from datetime import datetime
from functools import lru_cache
from hashlib import sha1

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Request
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sse_starlette.sse import EventSourceResponse

from .settings import Settings
from .sse_models import Base
from .sse_models import Environment
from .sse_models import Identity

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
    return


@router.post("/sse/environments/{environment_key}/identities/queue-change")
async def queue_identity_changes(
    environment_key: str, identifier: str = Body(embed=True)
):
    async with AsyncSession(engine, autoflush=True) as session:
        statement = text(
            """INSERT OR REPLACE INTO identity(identifier, environment_key) VALUES(:identifier, :environment_key)"""
        )
        await session.execute(
            statement, {"identifier": identifier, "environment_key": environment_key}
        )
        await session.commit()
    return


@router.get("/sse/environments/{environment_key}/stream")
async def stream_environment_changes(
    request: Request, environment_key: str, settings: Settings = Depends(get_settings)
):
    async with AsyncSession(engine, autoflush=True) as session:
        started_at = datetime.now()

        async def did_environment_change():
            environment_updated = False
            environment = await session.get(Environment, environment_key)
            if environment:
                environment_updated = True
                await session.delete(environment)

                # Clear identity updates if the environment was updated
                await session.execute(
                    delete(Identity).where(Identity.environment_key == environment_key)
                )
            await session.commit()
            return environment_updated

        async def get_updated_identities():
            identities = await session.execute(
                select(Identity.identifier).where(
                    Identity.environment_key == environment_key
                )
            )
            hashed_identities = [
                sha1(identity[0].encode()).hexdigest() for identity in identities
            ]
            await session.execute(
                delete(Identity).where(Identity.environment_key == environment_key)
            )
            await session.commit()

            return hashed_identities

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
                elif hashed_identities := await get_updated_identities():
                    for identity in hashed_identities:
                        yield {
                            "event": "identity_updated",
                            "data": {"identifier_hash": identity},
                        }

                await asyncio.sleep(settings.stream_delay)

        return EventSourceResponse(
            event_generator(), headers={"Cache-Control": "public, max-age=29"}
        )
