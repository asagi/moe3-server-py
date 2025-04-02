from contextlib import ExitStack
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import tweepy  # type:ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User
from schemas.user_schema import UserLogin
from services.user_service import login_user


async def test_login_new_user(master_data: AsyncSession, mock_user: MagicMock) -> None:
    time_string = "2025-03-31T03:54:50.166954Z"
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt_utc = dt.replace(tzinfo=timezone.utc)

    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(tweepy.Client, "get_me", return_value=mock_user))
        _ = stack.enter_context(patch("services.user_service._generate_access_key", return_value="accesskey"))
        _ = stack.enter_context(patch("services.user_service._get_current_time", return_value=dt_utc))
        param: UserLogin = UserLogin(access_token="abc")
        user: User = await login_user(master_data, param)

    assert user.id is not None
    assert user.xid == 123
    assert user.screen_name == "sname"
    assert user.display_name == "dname"
    assert user.access_key == "accesskey"
    assert user.last_access_time == dt_utc


async def test_login_exist_user(master_data: AsyncSession, mock_user: MagicMock) -> None:
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

    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(tweepy.Client, "get_me", return_value=mock_user))
        _ = stack.enter_context(patch("services.user_service._generate_access_key", return_value="accesskey"))
        _ = stack.enter_context(patch("services.user_service._get_current_time", return_value=dt_utc))
        param: UserLogin = UserLogin(access_token="abc")
        user: User = await login_user(master_data, param)

    assert user.id is not None
    assert user.xid == 123
    assert user.screen_name == "sname"
    assert user.display_name == "dname"
    assert user.access_key == "accesskey"
    assert user.last_access_time == dt_utc
