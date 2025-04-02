import uuid
from datetime import datetime, timezone
from typing import Any, cast

import tweepy  # type:ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User
from schemas.user_schema import UserLogin


def _generate_access_key():
    return str(uuid.uuid4())


def _get_current_time():
    return datetime.now(timezone.utc)


async def login_user(db: AsyncSession, param: UserLogin) -> User:
    client: Any = tweepy.Client(param.access_token)
    response: Any = client.get_me(user_auth=False)

    xid: int = cast(int, response.data.id)
    sname: str = cast(str, response.data.username)
    dname: str = cast(str, response.data.name)

    user = (await db.execute(select(User).filter_by(xid=xid))).scalar_one_or_none()
    if user:
        user.screen_name = sname
        user.display_name = dname
        user.access_key = _generate_access_key()
        user.last_access_time = _get_current_time()
        await db.commit()
        return user

    new_user = User(xid=xid, screen_name=sname, display_name=dname)
    new_user.access_key = _generate_access_key()
    new_user.last_access_time = _get_current_time()
    db.add(new_user)
    await db.commit()
    return new_user


async def update_last_access_time(db: AsyncSession, token: str) -> None:
    user: User = (await db.execute(select(User).filter_by(access_key=token))).scalar_one_or_none()
    if user:
        user.last_access_time = _get_current_time()
        await db.commit()
    else:
        raise Exception("User not found")
