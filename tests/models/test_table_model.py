from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.game_table_model import GameTable
from models.user_model import User


async def test_table_creation(master_data: AsyncSession) -> None:
    new_user = User(gid="123", gname="test", picture="https://lh3.googleusercontent.com/a/default-user")
    new_table = await GameTable.create_with_phases(new_user)
    master_data.add(new_table)
    await master_data.commit()
    user: User | None = (await master_data.execute(select(User).filter_by(gid=123))).scalar_one_or_none()
    assert user is not None
    table: GameTable | None = (await master_data.execute(select(GameTable).filter_by(user_id=user.id))).scalar_one_or_none()
    assert table is not None
    assert table.user_id == user.id
    assert user.tables[0].id == table.id
    assert len(table.phases) == 1
