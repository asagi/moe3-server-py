from sqlalchemy.ext.asyncio import AsyncSession

from models.game_table_model import GameTable
from models.order_model import Order
from models.path_model import Path
from models.phase_model import Phase
from models.player_model import Player
from models.power_model import Power
from models.province_model import Province
from models.standoff_model import Standoff
from models.territory_model import Territory
from models.unit_model import Unit
from models.user_model import User

__all__ = ["GameTable", "Order", "Path", "Phase", "Player", "Power", "Province", "Standoff", "Territory", "Unit", "User"]


async def load_cache(db: AsyncSession) -> None:
    await Power.load_cache(db)
    await Province.load_cache(db)
    await Path.load_cache(db)
