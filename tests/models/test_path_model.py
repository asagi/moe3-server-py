from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.path_model import Path
from models.power_model import Power
from models.province_model import Province
from models.territory_model import Territory
from models.unit_model import Army, Fleet, Unit


async def test_is_adjacent(master_data: AsyncSession) -> None:
    assert Path.is_adjacent(Province.LON, Province.ENG) is True


async def test_check_master_data(master_data: AsyncSession) -> None:
    paths = (await master_data.execute(select(Path))).scalars().all()
    for path in paths:
        opposites = (
            (
                await master_data.execute(
                    select(Path).filter_by(
                        origin=path.dest,
                        dest=path.origin,
                        army=path.army,
                        fleet=path.fleet,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(opposites) == 1


async def test_get_units_sorted_by_supply_distance_00(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    territories: list[Territory] = []
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result) == 0


async def test_get_units_sorted_by_supply_distance_01(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 1
    assert str(result[Power.E][0]) == "f eng"


async def test_get_units_sorted_by_supply_distance_02(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    units.append(Fleet(Power.E, Province.IRI))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 2
    assert str(result[Power.E][0]) == "f iri"
    assert str(result[Power.E][1]) == "f eng"


async def test_get_units_sorted_by_supply_distance_03(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    units.append(Fleet(Power.E, Province.IRI))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    territories.append(Territory(Province.WAL, Power.E))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 2
    assert str(result[Power.E][0]) == "f iri"
    assert str(result[Power.E][1]) == "f eng"


async def test_get_units_sorted_by_supply_distance_04(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    units.append(Fleet(Power.E, Province.IRI))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    territories.append(Territory(Province.WAL, Power.E))
    territories.append(Territory(Province.LVP, Power.E))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 2
    assert str(result[Power.E][0]) == "f eng"
    assert str(result[Power.E][1]) == "f iri"


async def test_get_units_sorted_by_supply_distance_05(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Army(Power.R, Province.LVN))
    units.append(Fleet(Power.R, Province.BAR))
    territories: list[Territory] = []
    territories.append(Territory(Province.STP, Power.R))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.R]) == 2
    assert str(result[Power.R][0]) == "f bar"
    assert str(result[Power.R][1]) == "a lvn"


async def test_get_units_sorted_by_supply_distance_06(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    units.append(Fleet(Power.E, Province.NTH))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    territories.append(Territory(Province.EDI, Power.E))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 2
    assert str(result[Power.E][0]) == "f eng"
    assert str(result[Power.E][1]) == "f nth"


async def test_get_units_sorted_by_supply_distance_07(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Army(Power.R, Province.SPA))
    units.append(Fleet(Power.R, Province.LYO))
    territories: list[Territory] = []
    territories.append(Territory(Province.STP, Power.R))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.R]) == 2
    assert str(result[Power.R][0]) == "f lyo"
    assert str(result[Power.R][1]) == "a spa"


async def test_get_units_sorted_by_supply_distance_08(master_data: AsyncSession) -> None:
    units: list[Unit] = []
    units.append(Fleet(Power.E, Province.ENG))
    units.append(Fleet(Power.E, Province.NTH))
    units.append(Army(Power.R, Province.SPA))
    units.append(Fleet(Power.R, Province.LYO))
    territories: list[Territory] = []
    territories.append(Territory(Province.LON, Power.E))
    territories.append(Territory(Province.EDI, Power.E))
    territories.append(Territory(Province.STP, Power.R))
    result = Path.get_units_sorted_by_supply_distance(units, territories)
    assert len(result[Power.E]) == 2
    assert str(result[Power.E][0]) == "f eng"
    assert str(result[Power.E][1]) == "f nth"
    assert len(result[Power.R]) == 2
    assert str(result[Power.R][0]) == "f lyo"
    assert str(result[Power.R][1]) == "a spa"
