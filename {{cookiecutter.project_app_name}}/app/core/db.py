"""
SQLAlchemy async engine and sessions tools

https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import AsyncIterator, Self

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    AsyncConnection,
)
from sqlmodel import SQLModel

from app import settings, Settings

if settings.ENVIRONMENT == "PYTEST":
    sqlalchemy_database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
else:
    sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI


async_engine = create_async_engine(url=sqlalchemy_database_uri, pool_pre_ping=True)
async_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


class AsyncDatabaseContext:
    __engine: AsyncEngine
    __session: AsyncSession

    def __init__(self, engine: AsyncEngine):
        self.__engine = engine
        self.__session = sessionmaker(
            bind=self.__engine, class_=AsyncSession, expire_on_commit=False
        )

    @classmethod
    def with_config(cls, settings: Settings) -> Self:
        if settings.ENVIRONMENT == "PYTEST":
            database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
        else:
            database_uri = settings.SQLALCHEMY_DATABASE_URI
        return cls(
            engine=create_async_engine(
                url=database_uri,
                pool_pre_ping=True,
                echo=settings.DEBUG,
            )
        )

    async def check_connection(self) -> None:
        async with self.__engine.connect() as db_conn:
            await db_conn.execute(text("SELECT 1"))

    async def close(self) -> None:
        await self.__engine.dispose()

    async def create_all(self) -> None:
        async with self.__engine.begin() as db_conn:
            await db_conn.run_sync(SQLModel.metadata.drop_all())
            await db_conn.run_sync(SQLModel.metadata.create_all())

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[AsyncConnection]:
        async with self.__engine.begin() as db_conn:
            yield db_conn

    @asynccontextmanager
    async def in_transaction(self) -> AsyncIterator[AsyncConnection]:
        async with self.begin() as db_conn:
            yield sessionmaker(
                bind=db_conn, class_=AsyncSession, expire_on_commit=False
            )

    @asynccontextmanager
    async def nested(self) -> AsyncIterator[AsyncConnection]:
        async with self.in_transaction() as nested:
            yield nested

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.__session() as async_session:
            yield async_session
