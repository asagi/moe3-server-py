from typing import Self, override

from sqlalchemy import Boolean, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.power_model import Power


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String)
    abbr: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    jname: Mapped[str] = mapped_column(String)
    suppliable: Mapped[bool] = mapped_column(Boolean, default=False)
    power_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("powers.id"))

    region: Mapped[Power | None] = relationship("Power", foreign_keys=[power_id], uselist=False, lazy="selectin")

    __mapper_args__ = {
        "polymorphic_identity": "province",
        "polymorphic_on": type,
    }

    @classmethod
    async def load_cache(cls, db: AsyncSession) -> None:
        cls._instances: set[Self] = set()
        for province in (await db.execute(select(cls))).scalars().all():
            setattr(cls, province.abbr.upper(), province)
            cls._instances.add(province)

    @classmethod
    def all(cls) -> set[Self]:
        return cls._instances

    @classmethod
    def same(cls, a: Self | None, b: Self | None) -> bool:
        if a is None:
            return b is None
        if b is None:
            return False
        return a.abbr[:3] == b.abbr[:3]

    def is_inland(self) -> bool:
        raise NotImplementedError("This method should not be called.")

    def is_coast(self) -> bool:
        raise NotImplementedError("This method should not be called.")

    def is_water(self) -> bool:
        raise NotImplementedError("This method should not be called.")


class Inland(Province):
    __mapper_args__ = {
        "polymorphic_identity": "inland",
    }

    @override
    def is_inland(self) -> bool:
        return True

    @override
    def is_coast(self) -> bool:
        return False

    @override
    def is_water(self) -> bool:
        return False


class Coast(Province):
    __mapper_args__ = {
        "polymorphic_identity": "coast",
    }

    @override
    def is_inland(self) -> bool:
        return False

    @override
    def is_coast(self) -> bool:
        return True

    @override
    def is_water(self) -> bool:
        return False


class Water(Province):
    __mapper_args__ = {
        "polymorphic_identity": "water",
    }

    @override
    def is_inland(self) -> bool:
        return False

    @override
    def is_coast(self) -> bool:
        return False

    @override
    def is_water(self) -> bool:
        return True
