import asyncio

from app.database import AsyncSessionLocal, async_engine
from models.base_model import Base
from setup.load_models import (
    GameTable,
    Order,
    Path,
    Phase,
    Player,
    Power,
    Province,
    Territory,
    Unit,
    User,
)
from setup.master_data_generator import generate_master_data

__all__ = ["Order", "Path", "Phase", "Player", "Power", "Province", "GameTable", "Territory", "Unit", "User"]


async def main() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:  # 非同期エンジン
        await generate_master_data(db)


if __name__ == "__main__":
    asyncio.run(main())
