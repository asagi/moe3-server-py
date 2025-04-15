from contextlib import ExitStack
from datetime import datetime
from typing import Any, AsyncGenerator, ContextManager, Generator
from unittest.mock import MagicMock, patch

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
def mock_user() -> Generator[dict[str, Any], None, None]:
    yield {
        "id": "123",
        "name": "gname",
        "picture": "picture",
    }


@pytest.fixture
def patched_user_service_factory(mock_user: dict[str, Any]) -> Generator[Any, None, None]:
    def _factory(dt_utc: datetime) -> ContextManager[ExitStack]:
        stack = ExitStack()
        _ = stack.enter_context(patch("google.oauth2.credentials.Credentials.__new__", return_value=None))
        mock_service = MagicMock()
        mock_service.userinfo.return_value.get.return_value.execute.return_value = mock_user
        _ = stack.enter_context(patch("services.user_service.build", return_value=mock_service))
        _ = stack.enter_context(patch("services.user_service._generate_access_key", return_value="accesskey"))
        _ = stack.enter_context(patch("services.user_service.get_current_time", return_value=dt_utc))
        return stack

    yield _factory
