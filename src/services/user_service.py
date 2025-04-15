import uuid
from typing import cast

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.util import get_current_time
from models.user_model import User
from schemas.user_schema import UserLogin


def _generate_access_key():
    return str(uuid.uuid4())


async def login_user(db: AsyncSession, param: UserLogin) -> User:
    credentials = Credentials(token=param.access_token)
    service = build("oauth2", "v2", credentials=credentials)  # type: ignore
    response = service.userinfo().get().execute()  # type: ignore

    gid: str = cast(str, response["id"])
    gname: str = cast(str, response["name"])
    picture: str = cast(str, response["picture"])

    exist_user = (await db.execute(select(User).filter_by(gid=gid))).scalar_one_or_none()
    if exist_user:
        exist_user.picture = picture
        exist_user.gname = gname
        exist_user.access_key = _generate_access_key()
        exist_user.last_access_time = get_current_time()
        await db.commit()
        return exist_user

    new_user = User(gid=gid, gname=gname, picture=picture)
    new_user.access_key = _generate_access_key()
    new_user.last_access_time = get_current_time()
    db.add(new_user)
    await db.commit()
    return new_user


async def update_last_access_time(db: AsyncSession, token: str) -> None:
    user: User = (await db.execute(select(User).filter_by(access_key=token))).scalar_one_or_none()
    if user:
        user.last_access_time = get_current_time()
        await db.commit()
    else:
        raise Exception("User not found")
