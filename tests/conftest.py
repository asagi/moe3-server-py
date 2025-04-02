from typing import Any, AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models.base_model import Base
from setup.load_models import load_cache
from setup.master_data_generator import generate_master_data


@pytest.fixture
async def db_session_memory() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session_file() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///db.sqlite3.test", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def master_data(db_session_memory: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    await generate_master_data(db_session_memory)
    await load_cache(db_session_memory)
    yield db_session_memory


@pytest.fixture
def mock_user() -> Generator[MagicMock, Any, None]:
    mock_response = MagicMock()
    mock_response.data = MagicMock()
    mock_response.data.id = 123
    mock_response.data.name = "dname"
    mock_response.data.username = "sname"
    yield mock_response
