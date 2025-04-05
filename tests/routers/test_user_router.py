from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


async def test_login_new_user(client: TestClient, testdb: AsyncSession, patched_user_service_factory: Any) -> None:
    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    stack = patched_user_service_factory(dt_utc)

    with stack:
        response: Response = client.post("/users", json={"access_token": "abc"})

    assert response.status_code == 200
    assert response.json() == {
        "gid": "123",
        "gname": "gname",
        "picture": "picture",
        "access_key": "accesskey",
        "last_access_time": "2025-03-31T03:54:50.166954Z",
    }


async def test_login_exist_user(client: TestClient, testdb: AsyncSession, patched_user_service_factory: Any) -> None:
    new_user: User = User(gid="123", gname="gname", picture="picture")
    new_user.access_key = "accesskey"
    testdb.add(new_user)
    await testdb.commit()

    exist_user: User | None = (await testdb.execute(select(User).filter_by(gid=123))).scalar_one_or_none()
    assert exist_user is not None
    assert exist_user.gname == "gname"
    assert exist_user.picture == "picture"
    assert exist_user.access_key == "accesskey"

    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    stack = patched_user_service_factory(dt_utc)

    with stack:
        response: Response = client.post("/users", json={"access_token": "abc"})

    assert response.status_code == 200
    assert response.json() == {
        "gid": "123",
        "gname": "gname",
        "picture": "picture",
        "access_key": "accesskey",
        "last_access_time": "2025-03-31T03:54:50.166954Z",
    }

    updated_user: User | None = (await testdb.execute(select(User).filter_by(gid=123))).scalar_one_or_none()
    assert updated_user is not None
    assert updated_user.gname == "gname"
    assert updated_user.picture == "picture"
    assert updated_user.access_key == "accesskey"
