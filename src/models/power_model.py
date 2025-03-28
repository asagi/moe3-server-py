from typing import Self

from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import Base


class Power(Base):
    __tablename__ = "powers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    adjective: Mapped[str] = mapped_column(String)

    @classmethod
    async def load_cache(cls, db: AsyncSession) -> None:
        cls._all: set[Power] = set()
        for power in (await db.execute(select(cls))).scalars().all():
            setattr(cls, power.symbol.upper(), power)
            cls._all.add(power)

    @classmethod
    def all(cls) -> set[Self]:
        return cls._all
