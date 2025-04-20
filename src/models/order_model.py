import enum
from typing import Self, override

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.phase_model import Phase
from models.power_model import Power
from models.province_model import Province
from models.unit_model import Army, Fleet, Unit


class Order(Base):
    __tablename__ = "orders"

    class Status(enum.Enum):
        UNRESOLVED = "unresolved"
        FAILURE = "failure"
        SUCCESS = "success"
        DISLODGED = "dislodged"
        CUT = "cut"
        VALID = "valid"
        INVALID = "invalid"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String)
    phase_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("phases.id"))
    power_id: Mapped[int] = mapped_column(Integer, ForeignKey("powers.id"))
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"))
    dest_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("provinces.id"))
    target_unit_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("units.id"))
    target_dest_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("provinces.id"))
    dislodger_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id"))
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False, default=Status.UNRESOLVED)

    phase: Mapped[Phase | None] = relationship("Phase", foreign_keys=[phase_id], back_populates="orders", uselist=False)
    power: Mapped[Power] = relationship("Power", foreign_keys=[power_id], uselist=False)
    unit: Mapped[Unit] = relationship("Unit", foreign_keys=[unit_id], uselist=False)
    dest: Mapped[Province | None] = relationship("Province", foreign_keys=[dest_id], uselist=False)
    target_unit: Mapped[Unit | None] = relationship("Unit", foreign_keys=[target_unit_id], uselist=False)
    target_dest: Mapped[Province | None] = relationship("Province", foreign_keys=[target_dest_id], uselist=False)
    dislodger: Mapped[Self | None] = relationship("MoveOrder", foreign_keys=[dislodger_id], uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "order",
        "polymorphic_on": type,
    }

    @property
    def origin(self) -> Province:
        return self.unit.province

    @property
    def target_origin(self) -> Province:
        if self.target_unit is None:
            raise NotImplementedError("This method should not be called.")
        return self.target_unit.province

    def __init__(self, unit: Unit) -> None:
        self.status = Order.Status.UNRESOLVED
        self.power = unit.power
        self.unit = unit
        self.dest = None
        self.target_unit = None
        self.target_dest = None

    @override
    def __str__(self) -> str:
        adjective_str = f"{self.unit.power.adjective} " if self.is_assumed() else ""
        return f"{adjective_str}{self.unit}"

    def create_unit(self) -> Unit:
        unit = Army(self.power, self.origin) if self.unit.is_army() else Fleet(self.power, self.origin)
        if self.status == Order.Status.DISLODGED and self.dislodger:
            unit.dislodged_from = self.dislodger.origin
        return unit

    def is_assumed(self) -> bool:
        return self.power.symbol != self.unit.power.symbol

    def is_hold(self) -> bool:
        return isinstance(self, HoldOrder)

    def is_move(self) -> bool:
        return isinstance(self, MoveOrder)

    def is_support(self) -> bool:
        return isinstance(self, SupportOrder)

    def is_convoy(self) -> bool:
        return isinstance(self, ConvoyOrder)

    def is_gain(self) -> bool:
        return isinstance(self, GainOrder)

    def is_lose(self) -> bool:
        return isinstance(self, LoseOrder)

    def match(self, other: Self) -> bool:
        if other.is_assumed():
            return False
        if self.target_unit is None:
            return False
        if self.target_unit.symbol != other.unit.symbol:
            return False
        if not Province.same(self.target_origin, other.origin):
            return False
        return Province.same(self.target_dest, other.dest)

    def assumed_by(self, power: Power) -> Self:
        self.power = power
        return self

    def success(self) -> Self:
        self.status = Order.Status.SUCCESS
        return self

    def cut(self) -> Self:
        raise NotImplementedError("This method should not be called.")

    def fail(self) -> Self:
        self.status = Order.Status.FAILURE
        return self

    def valid(self) -> Self:
        self.status = Order.Status.VALID
        return self

    def invalid(self) -> Self:
        self.status = Order.Status.INVALID
        return self

    def dislodged_by(self, other: Self) -> Self:
        self.status = Order.Status.DISLODGED
        self.dislodger = other
        return self


class HoldOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "hold",
    }

    @override
    def __str__(self) -> str:
        unit_str = super().__str__()
        return f"{unit_str}-Holds"

    @override
    def match(self, other: Order) -> bool:
        raise NotImplementedError("This method should not be called.")


class MoveOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "move",
    }

    @override
    def __init__(self, unit: Unit, dest: Province) -> None:
        super().__init__(unit)
        self.dest = dest
        self.target_unit = None
        self.target_dest = None

    @override
    def __str__(self) -> str:
        assert self.dest is not None
        unit_str = super().__str__()
        return f"{unit_str}-{self.dest.abbr}"

    @override
    def create_unit(self) -> Unit:
        if self.status == Order.Status.SUCCESS:
            return Army(self.power, self.dest) if self.unit.is_army() else Fleet(self.power, self.dest)

        unit = Army(self.power, self.origin) if self.unit.is_army() else Fleet(self.power, self.origin)
        if self.status == Order.Status.DISLODGED and self.dislodger:
            unit.dislodged_from = self.dislodger.origin
        return unit

    @override
    def match(self, other: Self) -> bool:
        raise NotImplementedError("This method should not be called.")


class SupportOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "support",
    }

    @override
    def __init__(self, unit: Unit, target: Order) -> None:
        super().__init__(unit)
        self.target_unit = target.unit
        self.target_dest = target.dest

    def __support_other__(self) -> bool:
        assert self.target_unit is not None
        return self.power.symbol != self.target_unit.power.symbol

    @override
    def __str__(self) -> str:
        assert self.target_unit is not None
        unit_str = super().__str__()
        target_dest_str = f"-{self.target_dest.abbr}" if self.target_dest else ""
        target_adjective_str = f"{self.target_unit.power.adjective} " if self.__support_other__() else ""
        return f"{unit_str} S {target_adjective_str}{self.target_unit}{target_dest_str}"

    @override
    def cut(self) -> Self:
        self.status = Order.Status.CUT
        return self


class ConvoyOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "convoy",
    }

    @override
    def __init__(self, unit: Unit, target: Order) -> None:
        super().__init__(unit)
        self.target_unit = target.unit
        self.target_dest = target.dest

    def __convoy_other__(self) -> bool:
        assert self.target_unit is not None
        return self.power.symbol != self.target_unit.power.symbol

    @override
    def __str__(self) -> str:
        assert self.target_unit is not None
        assert self.target_dest is not None
        unit_str = super().__str__()
        target_dest_str = f"-{self.target_dest.abbr}"
        target_adjective_str = f"{self.target_unit.power.adjective} " if self.__convoy_other__() else ""
        return f"{unit_str} C {target_adjective_str}{self.target_unit}{target_dest_str}"


class RetreatOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "retreat",
    }

    @override
    def match(self, other: Order) -> bool:
        raise NotImplementedError("This method should not be called.")


class DisbandOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "disband",
    }

    @override
    def match(self, other: Order) -> bool:
        raise NotImplementedError("This method should not be called.")


class GainOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "gain",
    }

    @override
    def match(self, other: Order) -> bool:
        raise NotImplementedError("This method should not be called.")


class GainArmyOrder(GainOrder):
    __mapper_args__ = {
        "polymorphic_identity": "gain_army",
    }

    @override
    def create_unit(self) -> Unit:
        return Army(self.power, self.origin)


class GainFleetOrder(GainOrder):
    __mapper_args__ = {
        "polymorphic_identity": "gain_fleet",
    }

    @override
    def create_unit(self) -> Unit:
        return Fleet(self.power, self.origin)


class LoseOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "lose",
    }

    @override
    def match(self, other: Order) -> bool:
        raise NotImplementedError("This method should not be called.")
