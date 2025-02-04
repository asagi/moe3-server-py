from typing import cast

import tweepy  # type:ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User
from schemas.user_schema import UserLogin


def _generate_access_key():
    # TODO: アクセスキーを生成する
    return "accesskey"


async def login_user(db: AsyncSession, param: UserLogin) -> User:
    client = tweepy.Client(param.access_token)
    response = client.get_me(user_auth=False)  # type:ignore
    response_data: dict = response.data  # type:ignore

    if not response_data:
        # TODO: エラー処理
        pass

    xid: int = cast(int, response_data.id)  # type:ignore
    sname: str = cast(str, response_data.username)  # type:ignore
    dname: str = cast(str, response_data.name)  # type:ignore

    user = (await db.execute(select(User).filter_by(xid=xid))).scalar_one_or_none()
    if user:
        user.screen_name = sname
        user.display_name = dname
        await db.commit()
        return user

    new_user = User(xid=xid, screen_name=sname, display_name=dname)
    new_user.access_key = _generate_access_key()
    db.add(new_user)
    await db.commit()
    return new_user
