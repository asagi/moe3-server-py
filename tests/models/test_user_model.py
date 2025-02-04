from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


async def test_user_creation(master_data: AsyncSession) -> None:
    new_user: User = User(xid=123, screen_name="abc", display_name="def")
    master_data.add(new_user)
    await master_data.commit()
    user: User | None = (await master_data.execute(select(User).filter_by(xid=123))).scalar_one_or_none()
    assert user is not None
    assert user.xid == 123
    assert user.screen_name == "abc"
    assert user.display_name == "def"
