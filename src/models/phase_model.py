import enum
from typing import TYPE_CHECKING, Self, override

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import INITIAL_YEAR
from models.base_model import Base
from models.game_table_model import GameTable
from models.phase_mixins import BeforeOrderPhase, OrderPhase
from models.province_model import Province
from models.standoff_model import Standoff

if TYPE_CHECKING:
    from models.order_model import Order
    from models.territory_model import Territory
    from models.unit_model import Unit


class Phase(Base):
    __tablename__ = "phases"

    class Status(enum.Enum):
        OPEN = "open"
        CLOSED = "closed"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String)
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_tables.id"))
    prev_phase_id: Mapped[Self | None] = mapped_column(Integer, ForeignKey("phases.id"))
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False, default=Status.OPEN)
    year: Mapped[int] = mapped_column(Integer, default=0)
    period: Mapped[DateTime | None] = mapped_column(DateTime)

    table: Mapped[GameTable] = relationship("GameTable", foreign_keys=[table_id], back_populates="phases", uselist=False)
    prev_phase: Mapped[Self | None] = relationship("Phase", remote_side=[id], foreign_keys=[prev_phase_id])
    territories: Mapped[list["Territory"]] = relationship("Territory", back_populates="phase", lazy="selectin")
    units: Mapped[list["Unit"]] = relationship("Unit")
    orders: Mapped[list["Order"]] = relationship("Order")
    standoffs: Mapped[list[Standoff]] = relationship("Standoff")

    __mapper_args__ = {
        "polymorphic_identity": "phase",
        "polymorphic_on": type,
    }

    @classmethod
    def create_ready_phase(cls) -> Self:
        from models.province_model import Province
        from models.territory_model import Territory
        from models.unit_model import Unit

        ready_phase = ReadyPhase()
        for province in filter(lambda p: p.region is not None, Province.all()):
            ready_phase.territories.append(Territory(province, province.region))
        ready_phase.units.extend(Unit.get_initial_units())
        return ready_phase._open()

    @property
    def latest_territories(self) -> list["Territory"]:
        if len(self.territories) > 0:
            return self.territories
        if self.prev_phase:
            return self.prev_phase.latest_territories
        return []

    @property
    def latest_units(self) -> list["Unit"]:
        if len(self.units) > 0:
            return self.units
        if self.prev_phase:
            return self.prev_phase.latest_units
        return []

    def __init__(self, prev_phase: Self | None = None) -> None:
        self.table = prev_phase.table if prev_phase else None
        self.prev_phase = prev_phase
        self.year = 0
        self.territories = []
        self.units = []
        self.orders = []

    def _initialize_next_orders(self) -> list["Order"]:
        raise NotImplementedError("This property should be overridden")

    def _open(self) -> Self:
        self.status = Phase.Status.OPEN
        return self

    def _close(self) -> Self:
        self.status = Phase.Status.CLOSED
        return self

    def resolve_orders(self) -> None:
        raise NotImplementedError("This property should be overridden")

    def create_next_phase(self) -> Self:
        raise NotImplementedError("This property should be overridden")


class ReadyPhase(Phase, BeforeOrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "ready",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = SpringOrderPhase(prev_phase=self)
        new_phase.year = INITIAL_YEAR
        new_phase.orders.extend(self._initialize_next_orders())
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()


class SpringOrderPhase(Phase, OrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "spring_order",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_disband_orders(self.latest_units)

    @override
    def resolve_orders(self) -> None:
        standoffs: set[Province] = set()
        self.resolve_marching_orders(self.orders, standoffs)
        for order in filter(lambda o: not o.is_assumed(), self.orders):
            self.units.append(order.create_unit())
        # TODO: スタンドオフ地域保存

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = SpringRetreatPhase(prev_phase=self)
        new_phase.year = self.year
        new_phase.orders.extend(self._initialize_next_orders())
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()


class SpringRetreatPhase(Phase, BeforeOrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "spring_retreat",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = FallOrderPhase(prev_phase=self)
        new_phase.year = self.year
        new_phase.orders.extend(self._initialize_next_orders())
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()


class FallOrderPhase(Phase, OrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "fall_order",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_disband_orders(self.latest_units)

    @override
    def resolve_orders(self) -> None:
        standoffs: set[Province] = set()
        self.resolve_marching_orders(self.orders, standoffs)
        for order in filter(lambda o: not o.is_assumed(), self.orders):
            self.units.append(order.create_unit())
        # TODO: スタンドオフ地域保存

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = FallRetreatPhase(prev_phase=self)
        new_phase.year = self.year
        new_phase.orders.extend(self._initialize_next_orders())
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()


class FallRetreatPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "fall_retreat",
    }

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = AdjusntmentPhase(prev_phase=self)
        new_phase.year = self.year
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()


class AdjusntmentPhase(Phase, BeforeOrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "adjustment",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def create_next_phase(self) -> Phase:
        _ = self._close()
        new_phase = SpringOrderPhase(prev_phase=self)
        new_phase.year = self.year + 1
        new_phase.orders.extend(self._initialize_next_orders())
        # TODO: new_phase.period = get_next_period()
        return new_phase._open()
