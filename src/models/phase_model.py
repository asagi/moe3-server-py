from enum import Enum as PyEnum
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from typing import List
from models.base_model import Base
from models.province_model import Province
from models.table_model import Table  # noqa
from models.territory_model import Territory
from models.unit_model import Unit


class Phase(Base):
    __tablename__ = "phases"

    class Status(PyEnum):
        OPEN = "open"
        CLOSED = "closed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    table_id = Column(Integer, ForeignKey("game_tables.id"))
    prev_phase_id = Column(Integer, ForeignKey("phases.id"))
    status = Column(Enum(Status), nullable=False, default=Status.OPEN)
    year = Column(Integer, default=0)

    table = relationship("Table", back_populates="phases", uselist=False)
    prev_phase = relationship("Phase", uselist=False)
    territories = relationship("Territory")
    units = relationship("Unit")

    @property
    def latest_territories(self) -> List:
        if self.territories:
            return self.territories
        if self.prev_phase:
            return self.prev_phase.latest_territories
        return []

    @property
    def latest_units(self) -> List:
        if self.units:
            return self.units
        if self.prev_phase:
            return self.prev_phase.latest_units
        return []

    __mapper_args__ = {
        "polymorphic_identity": "phase",
        "polymorphic_on": type,
    }


class ReadyPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "ready",
    }

    def __init__(self, db: Session) -> None:
        for province in db.query(Province):
            if province.region is None:
                continue
            territory = Territory(province=province, occupier=province.region)
            self.territories.append(territory)

        units = Unit.get_initial_units(db)
        self.units.extend(units)

    def create_next_phase(self) -> Phase:
        new_phase = SpringOrderPhase(prev_phase=self, year=1901)
        self.status = Phase.Status.CLOSED
        return new_phase


class SpringOrderPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "spring_order",
    }

    def create_next_phase(self) -> Phase:
        new_phase = SpringRetreatPhase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase


class SpringRetreatPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "spring_retreat",
    }

    def create_next_phase(self) -> Phase:
        new_phase = FallOrderPhase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase


class FallOrderPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "fall_order",
    }

    def create_next_phase(self) -> Phase:
        new_phase = FallRetreatPhase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase


class FallRetreatPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "fall_retreat",
    }

    def create_next_phase(self) -> Phase:
        new_phase = AdjusntmentPhase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase


class AdjusntmentPhase(Phase):
    __mapper_args__ = {
        "polymorphic_identity": "adjustment",
    }

    def create_next_phase(self) -> Phase:
        new_phase = SpringOrderPhase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase
