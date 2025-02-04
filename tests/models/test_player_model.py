from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.game_table_model import GameTable
from models.player_model import Player
from models.user_model import User


async def test_player_creation(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    new_user.tables.append(new_table)
    master_data.add(new_table)
    await master_data.commit()
    new_player = Player(user=new_user, table=new_table)
    master_data.add(new_player)
    await master_data.commit()
    player = (await master_data.execute(select(Player))).scalar_one_or_none()
    user = (await master_data.execute(select(User))).scalar_one_or_none()
    table = (await master_data.execute(select(GameTable))).scalar_one_or_none()
    assert player is not None
    assert player.user is user
    assert player.table is table
