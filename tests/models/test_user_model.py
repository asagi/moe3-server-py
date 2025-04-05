from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


async def test_user_creation(master_data: AsyncSession) -> None:
    new_user: User = User(gid="123", gname="test", picture="https://example.com")
    master_data.add(new_user)
    await master_data.commit()
    user: User | None = (await master_data.execute(select(User).filter_by(gid=123))).scalar_one_or_none()
    assert user is not None
    assert user.gid == "123"
    assert user.gname == "test"
    assert user.picture == "https://example.com"
