from sqlalchemy.ext.asyncio import AsyncSession

from models.power_model import Power
from models.province_model import Province
from models.unit_model import Army, Fleet, Unit


async def test_army_creation(master_data: AsyncSession) -> None:
    new_unit = Army(Power.A, Province.LON)
    master_data.add(new_unit)
    await master_data.commit()
    unit = await master_data.get(Unit, new_unit.id)
    assert unit is not None
    assert unit.type == "army"
    assert unit.symbol == "a"
    assert unit.power.name == "Austria"


async def test_fleet_creation(master_data: AsyncSession) -> None:
    new_unit = Fleet(Power.G, Province.LON)
    master_data.add(new_unit)
    await master_data.commit()
    unit = await master_data.get(Unit, new_unit.id)
    assert unit is not None
    assert unit.type == "fleet"
    assert unit.symbol == "f"
    assert unit.power.name == "Germany"
