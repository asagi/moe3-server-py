from datetime import datetime, timezone
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
import tweepy  # type:ignore
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


@pytest.fixture
def mock_user() -> Generator[MagicMock, Any, None]:
    mock_response = MagicMock()
    mock_response.data = MagicMock()
    mock_response.data.id = 123
    mock_response.data.name = "dname"
    mock_response.data.username = "sname"
    yield mock_response


async def test_read_hello(client: TestClient) -> None:
    response: Response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"Hello": "7 powers"}


async def test_login_new_user(client: TestClient, mock_user: MagicMock) -> None:
    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)

    with patch.object(tweepy.Client, "get_me", return_value=mock_user):
        with patch("services.user_service._generate_access_key", return_value="accesskey"):
            with patch("services.user_service._get_current_time", return_value=dt_utc):
                response: Response = client.post("/users", json={"access_token": "abc"})

    assert response.status_code == 200
    assert response.json() == {
        "xid": 123,
        "screen_name": "sname",
        "display_name": "dname",
        "access_key": "accesskey",
        "last_access_time": "2025-03-31T03:54:50.166954Z",
    }


async def test_login_exist_user(client: TestClient, master_data: AsyncSession, mock_user: MagicMock) -> None:
    new_user: User = User(xid=123, screen_name="username", display_name="name")
    new_user.access_key = "accesskey"
    master_data.add(new_user)
    await master_data.commit()

    exist_user: User | None = (await master_data.execute(select(User).filter_by(xid=123))).scalar_one_or_none()
    assert exist_user is not None
    assert exist_user.screen_name == "username"
    assert exist_user.display_name == "name"
    assert exist_user.access_key == "accesskey"

    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)

    with patch.object(tweepy.Client, "get_me", return_value=mock_user):
        with patch("services.user_service._generate_access_key", return_value="accesskey"):
            with patch("services.user_service._get_current_time", return_value=dt_utc):
                response: Response = client.post("/users", json={"access_token": "abc"})
    assert response.status_code == 200
    assert response.json() == {
        "xid": 123,
        "screen_name": "sname",
        "display_name": "dname",
        "access_key": "accesskey",
        "last_access_time": "2025-03-31T03:54:50.166954Z",
    }

    updated_user: User | None = (await master_data.execute(select(User).filter_by(xid=123))).scalar_one_or_none()
    assert updated_user is not None
    assert updated_user.screen_name == "sname"
    assert updated_user.display_name == "dname"
    assert updated_user.access_key == "accesskey"
