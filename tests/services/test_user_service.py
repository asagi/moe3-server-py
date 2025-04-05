from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User
from schemas.user_schema import UserLogin
from services.user_service import login_user


async def test_login_new_user(master_data: AsyncSession, patched_user_service_factory: Any) -> None:
    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    stack = patched_user_service_factory(dt_utc)

    with stack:
        param: UserLogin = UserLogin(access_token="mock_access_token")
        user: User = await login_user(master_data, param)

    assert user.id is not None
    assert user.gid == "123"
    assert user.gname == "gname"
    assert user.picture == "picture"
    assert user.access_key == "accesskey"
    assert user.last_access_time == dt_utc


async def test_login_exist_user(master_data: AsyncSession, patched_user_service_factory: Any) -> None:
    new_user: User = User(gid="123", gname="name", picture="picture")
    new_user.access_key = "accesskey"
    master_data.add(new_user)
    await master_data.commit()

    exist_user: User | None = (await master_data.execute(select(User).filter_by(gid=123))).scalar_one_or_none()
    assert exist_user is not None
    assert exist_user.gname == "name"
    assert exist_user.picture == "picture"
    assert exist_user.access_key == "accesskey"

    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    stack = patched_user_service_factory(dt_utc)

    with stack:
        param: UserLogin = UserLogin(access_token="abc")
        user: User = await login_user(master_data, param)

    assert user.id is not None
    assert user.gid == "123"
    assert user.gname == "gname"
    assert user.picture == "picture"
    assert user.access_key == "accesskey"
    assert user.last_access_time == dt_utc
