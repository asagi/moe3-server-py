from abc import abstractmethod
from typing import TYPE_CHECKING, Self, override

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.power_model import Power
from models.province_model import Province

if TYPE_CHECKING:
    from models.order_model import Order
    from models.phase_model import Phase


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String)
    power_id: Mapped[int] = mapped_column(Integer, ForeignKey("powers.id"))
    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    phase_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("phases.id"))
    dislodged_from_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("provinces.id"))

    power: Mapped[Power] = relationship("Power", foreign_keys=[power_id], uselist=False)
    province: Mapped[Province] = relationship("Province", foreign_keys=[province_id], uselist=False)
    phase: Mapped["Phase | None"] = relationship("Phase", foreign_keys=[phase_id], back_populates="units", uselist=False)
    dislodged_from: Mapped[Province | None] = relationship("Province", foreign_keys=[dislodged_from_id], uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "unit",
        "polymorphic_on": type,
    }

    @classmethod
    def get_initial_units(cls) -> list[Self]:
        return [
            # fmt:off
            Army(Power.A, Province.VIE), Army(Power.A, Province.BUD),  Fleet(Power.A, Province.TRI),
            Army(Power.E, Province.LVP), Fleet(Power.E, Province.LON), Fleet(Power.E, Province.EDI),
            Army(Power.F, Province.PAR), Army(Power.F, Province.MAR),  Fleet(Power.F, Province.BRE),
            Army(Power.G, Province.BER), Army(Power.G, Province.MUN),  Fleet(Power.G, Province.KIE),
            Army(Power.I, Province.ROM), Army(Power.I, Province.VEN),  Fleet(Power.I, Province.NAP),
            Army(Power.R, Province.MOS), Army(Power.R, Province.WAR),  Fleet(Power.R, Province.STP_SC), Fleet(Power.R, Province.SEV),
            Army(Power.T, Province.CON), Army(Power.T, Province.SMY),  Fleet(Power.T, Province.ANK),
            # fmt:on
        ]

    @property
    @abstractmethod
    def symbol(self) -> str:
        raise NotImplementedError("This property should be overridden")

    def __init__(self, power: Power, province: Province, dislodged_from: Province | None = None) -> None:
        self.power = power
        self.province = province
        self.dislodged_from = dislodged_from

    @override
    def __str__(self) -> str:
        return f"{self.symbol} {self.province.abbr}"

    def hold(self) -> "Order":
        from models.order_model import HoldOrder

        return HoldOrder(self)

    def move_to(self, dest: Province) -> "Order":
        from models.order_model import MoveOrder

        return MoveOrder(self, dest)

    def support(self, target: "Order") -> "Order":
        from models.order_model import SupportOrder

        return SupportOrder(self, target)

    def convoy(self, target: "Order") -> "Order":
        from models.order_model import ConvoyOrder

        return ConvoyOrder(self, target)

    def disband(self) -> "Order":
        from models.order_model import DisbandOrder

        return DisbandOrder(self)

    def lose(self) -> "Order":
        from models.order_model import LoseOrder

        return LoseOrder(self)

    def is_army(self) -> bool:
        return False

    def is_fleet(self) -> bool:
        return False

    def is_dislodged(self) -> bool:
        return self.dislodged_from is not None


class Army(Unit):
    __mapper_args__ = {
        "polymorphic_identity": "army",
    }

    @property
    @override
    def symbol(self) -> str:
        return "a"

    @override
    def is_army(self) -> bool:
        return True


class Fleet(Unit):
    __mapper_args__ = {
        "polymorphic_identity": "fleet",
    }

    @property
    @override
    def symbol(self) -> str:
        return "f"

    @override
    def is_fleet(self) -> bool:
        return True
