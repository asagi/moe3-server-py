from typing import Any, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app
from setup.master_data_generator import generate_master_data


@pytest.fixture
async def override_db_session(db_session_memory: AsyncSession) -> AsyncGenerator[Any, Any]:
    await generate_master_data(db_session_memory)
    app.dependency_overrides[get_db] = lambda: db_session_memory
    yield db_session_memory
    del app.dependency_overrides[get_db]


@pytest.fixture
async def client(override_db_session: AsyncSession) -> AsyncGenerator[Any, Any]:
    client: TestClient = TestClient(app)
    yield client
