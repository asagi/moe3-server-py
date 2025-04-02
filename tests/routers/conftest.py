from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[Any, Any]:
    client: TestClient = TestClient(app)
    yield client


@pytest.fixture
async def testdb(master_data: AsyncSession) -> AsyncGenerator[Any, Any]:
    with patch("app.main.get_db", return_value=AsyncMock(__anext__=AsyncMock(return_value=master_data))):
        yield master_data
