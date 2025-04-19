import enum
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Self, override

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import INITIAL_YEAR
from app.util import get_current_time
from models.base_model import Base
from models.game_table_model import GameTable
from models.phase_mixins import (
    BeforeAdjustmentPhaseMixin,
    BeforeOrderPhaseMixin,
    OrderPhaseMixin,
)
from models.power_model import Power
from models.province_model import Province
from models.standoff_model import Standoff
from value_objects.duration_values import DueMode

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
    due_time: Mapped[datetime | None] = mapped_column(DateTime)

    table: Mapped[GameTable] = relationship("GameTable", foreign_keys=[table_id], back_populates="phases", uselist=False)
    prev_phase: Mapped[Self | None] = relationship("Phase", remote_side=[id], foreign_keys=[prev_phase_id])
    territories: Mapped[list["Territory"]] = relationship("Territory", back_populates="phase", lazy="selectin")
    units: Mapped[list["Unit"]] = relationship("Unit", lazy="selectin")
    orders: Mapped[list["Order"]] = relationship("Order", lazy="selectin")
    standoffs: Mapped[list[Standoff]] = relationship("Standoff", lazy="selectin")

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
        raise NotImplementedError("This method should be overridden")

    def _open(self) -> Self:
        self.status = Phase.Status.OPEN
        return self

    def _close(self) -> Self:
        self.status = Phase.Status.CLOSED
        return self

    def _get_next_phase(self) -> Self:
        raise NotImplementedError("This method should be overridden")

    def _get_next_due_time(self) -> datetime | None:
        raise NotImplementedError("This method should be overridden")

    def _resolve_orders(self) -> None:
        pass

    def _occupy(self) -> None:
        pass

    def _create_next_phase(self) -> Self:
        _ = self._close()
        new_phase = self._get_next_phase()
        new_phase.due_time = self._get_next_due_time()
        new_phase.year = self.year
        new_phase.orders.extend(self._initialize_next_orders())
        return new_phase

    def _create_debrief_phase(self, due_time: datetime | None = None) -> Self:
        _ = self._close()
        debrief_phase = DebriefPhase(self)
        if due_time is not None:
            debrief_phase.due_time = due_time
        return debrief_phase._open()

    def _should_skip_next_phase(self, _active_powers: set[Power]) -> bool:
        return False

    def _check_draw_condition(self, active_powers: set[Power]) -> bool:
        if not self.table:
            return False

        if not isinstance(self, OrderPhase):
            return False

        powers = active_powers if active_powers else Power.all()
        draw_agreed_players = [p for p in self.table.players if p.power in powers and p.is_draw_agreed]
        return len(draw_agreed_players) / len(powers) > 0.5

    def end(self, active_powers: set[Power] | None = None) -> Self | None:
        if active_powers is None:
            active_powers = set()

        if self._check_draw_condition(active_powers):
            if not self.due_time:
                return self._create_debrief_phase()._open()

            now = get_current_time()
            if self.table.due_mode == DueMode.FIXED or now >= self.due_time:
                due_time = self.due_time + timedelta(minutes=self.table.get_debrief_phase_duration())
            else:
                due_time = now + timedelta(minutes=self.table.get_debrief_phase_duration())
            return self._create_debrief_phase(due_time)._open()

        self._resolve_orders()
        self._occupy()

        # TODO: 制覇判定
        # 誰かが制覇勝利したら感想戦フェイズを生成して返却

        new_phase = self._create_next_phase()

        if not self._should_skip_next_phase(active_powers):
            # TODO: アクティブ国の早回しおよび和平同意フラグオフ
            return new_phase._open()

        return new_phase.end(active_powers)


class ReadyPhase(Phase, BeforeOrderPhaseMixin):
    __mapper_args__ = {
        "polymorphic_identity": "ready",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def _get_next_phase(self) -> Self:
        return SpringOrderPhase(prev_phase=self)

    @override
    def _get_next_due_time(self) -> datetime | None:
        if self.table.start_time is None:
            return None
        return self.table.start_time + timedelta(minutes=self.table.get_order_phase_duration())

    @override
    def _create_next_phase(self) -> Phase:
        new_phase = super()._create_next_phase()
        new_phase.year = INITIAL_YEAR
        return new_phase._open()


class OrderPhase(Phase, OrderPhaseMixin):
    __mapper_args__ = {
        "polymorphic_identity": "order",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_disband_orders(self.latest_units)

    @override
    def _get_next_due_time(self) -> datetime | None:
        if self.due_time is None:
            return None

        now = get_current_time()
        if self.table.due_mode == DueMode.FIXED or now >= self.due_time:
            return self.due_time + timedelta(minutes=self.table.get_retreat_phase_duration())
        else:
            return now + timedelta(minutes=self.table.get_retreat_phase_duration())

    @override
    def _resolve_orders(self) -> None:
        standoffs: set[Province] = set()
        self.resolve_marching_orders(self.orders, standoffs)

        for order in filter(lambda o: not o.is_assumed(), self.orders):
            self.units.append(order.create_unit())

        for province in standoffs:
            self.standoffs.append(Standoff(province))

    @override
    def _should_skip_next_phase(self, active_powers: set[Power]) -> bool:
        if self.table and self.table.due_mode == DueMode.FIXED:
            return False
        return self.should_skip_next_retreat_phase(active_powers, self.units, self.standoffs)


class RetreatPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "retreat",
    }

    @override
    def _create_next_phase(self) -> Phase:
        return super()._create_next_phase()._open()

    @override
    def _resolve_orders(self) -> None:
        # TODO: 撤退命令の解決
        ...


class SpringOrderPhase(OrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "spring_order",
    }

    @override
    def _get_next_phase(self) -> Self:
        return SpringRetreatPhase(prev_phase=self)


class SpringRetreatPhase(RetreatPhase, BeforeOrderPhaseMixin):
    __mapper_args__ = {
        "polymorphic_identity": "spring_retreat",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def _get_next_phase(self) -> Self:
        return FallOrderPhase(prev_phase=self)

    @override
    def _get_next_due_time(self) -> datetime | None:
        if self.due_time is None:
            return None

        now = get_current_time()
        if self.table.due_mode == DueMode.FIXED:
            # fmt: off
            return (
                self.due_time
                + timedelta(minutes=self.table.get_order_phase_duration())
                - timedelta(minutes=self.table.get_retreat_phase_duration())
            )
            # fmt: on
        elif self.table.due_mode == DueMode.FLEXIBLE and now >= self.due_time:
            return self.due_time + timedelta(minutes=self.table.get_order_phase_duration())
        else:
            return now + timedelta(minutes=self.table.get_order_phase_duration())


class FallOrderPhase(OrderPhase):
    __mapper_args__ = {
        "polymorphic_identity": "fall_order",
    }

    @override
    def _get_next_phase(self) -> Self:
        return FallRetreatPhase(prev_phase=self)


class FallRetreatPhase(RetreatPhase, BeforeAdjustmentPhaseMixin):
    __mapper_args__ = {
        "polymorphic_identity": "fall_retreat",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_disband_orders(self.latest_units, self.latest_territories)

    @override
    def _get_next_phase(self) -> Self:
        return AdjusntmentPhase(prev_phase=self)

    @override
    def _get_next_due_time(self) -> datetime | None:
        if self.due_time is None:
            return None

        now = get_current_time()
        if self.table.due_mode == DueMode.FIXED or now >= self.due_time:
            return self.due_time + timedelta(minutes=self.table.get_adjustment_phase_duration())
        else:
            return now + timedelta(minutes=self.table.get_adjustment_phase_duration())

    @override
    def _occupy(self) -> None:
        from models.territory_model import Territory

        # 既存領地の更新
        for t in self.latest_territories:
            occupier: Power = next((u.power for u in self.latest_units if u.province == t.province), t.occupier)
            self.territories.append(Territory(t.province, occupier))

        # 新規占領
        for u in self.latest_units:
            if not any(u.province == t.province for t in self.territories):
                self.territories.append(Territory(u.province, u.power))

    @override
    def _should_skip_next_phase(self, active_powers: set[Power]) -> bool:
        if self.table and self.table.due_mode == DueMode.FIXED:
            return False
        return self.should_skip_next_adjustment_phase(active_powers, self.latest_units, self.latest_territories)


class AdjusntmentPhase(Phase, BeforeOrderPhaseMixin):
    __mapper_args__ = {
        "polymorphic_identity": "adjustment",
    }

    @override
    def _initialize_next_orders(self) -> list["Order"]:
        return self.initialize_next_hold_orders(self.latest_units)

    @override
    def _get_next_phase(self) -> Self:
        return SpringOrderPhase(prev_phase=self)

    @override
    def _get_next_due_time(self) -> datetime | None:
        if self.due_time is None:
            return None

        now = get_current_time()
        if self.table.due_mode == DueMode.FIXED:
            # fmt: off
            return (
                self.due_time
                + timedelta(minutes=self.table.get_order_phase_duration())
                - timedelta(minutes=self.table.get_retreat_phase_duration())
                - timedelta(minutes=self.table.get_adjustment_phase_duration())
            )
            # fmt: on
        elif self.table.due_mode == DueMode.FLEXIBLE and now >= self.due_time:
            return self.due_time + timedelta(minutes=self.table.get_order_phase_duration())
        else:
            return now + timedelta(minutes=self.table.get_order_phase_duration())

    @override
    def _resolve_orders(self) -> None:
        # TODO: 増設解体実行
        ...

    @override
    def _create_next_phase(self) -> Phase:
        new_phase = super()._create_next_phase()
        new_phase.year += 1
        return new_phase._open()

    @override
    def _occupy(self) -> None:
        for p in Power.all():
            supplycenters_of_power: list[Territory] = [t for t in self.latest_territories if t.occupier == p and t.suppliable]
            if len(supplycenters_of_power) > 0:
                continue

            # 滅亡国の領地開放
            for t in self.latest_territories[:]:
                if t.occupier == p:
                    self.latest_territories.remove(t)


class DebriefPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "debrief",
    }

    @override
    def end(self, active_powers: set[Power] | None = None) -> Self | None:
        return None
