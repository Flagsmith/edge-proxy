from typing import List

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text

Base = declarative_base()


class Environment(Base):
    __tablename__ = "environment"
    key = Column(String, primary_key=True)
    last_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    def __repr__(self):
        return f"Environment(key={self.key!r})"


class Identity(Base):
    __tablename__ = "identity"
    identifier = Column(String, primary_key=True)
    environment_key = Column(String)

    def __repr__(self):
        return f"Identity(identifier={self.identifier!r})"

    @staticmethod
    async def put_identities(
        engine: AsyncEngine, environment_key: str, identifiers: List[str]
    ):
        async with AsyncSession(engine, autoflush=True) as session:
            statement = text(
                """INSERT OR REPLACE INTO identity(identifier, environment_key) VALUES(:identifier, :environment_key)"""
            )
            for identifier in identifiers:
                await session.execute(
                    statement,
                    {"identifier": identifier, "environment_key": environment_key},
                )
