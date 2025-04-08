from sqlalchemy.ext.asyncio import AsyncSession

from models.power_model import Power
from models.province_model import Province
from models.territory_model import Territory


async def test_delegator_suppliable_01(master_data: AsyncSession) -> None:
    territory = Territory(Province.LON, Power.E)
    assert territory is not None
    assert territory.suppliable is True


async def test_delegator_suppliable_02(master_data: AsyncSession) -> None:
    territory = Territory(Province.WAL, Power.E)
    assert territory is not None
    assert territory.suppliable is False
