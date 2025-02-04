from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.path_model import Path
from models.province_model import Province


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
