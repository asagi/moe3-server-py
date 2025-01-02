from enum import Enum as PyEnum
from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from typing import Self, List
from models.base_model import Base
from models.province_model import Province
from models.table_model import Table  # noqa
from models.territory_model import Territory


class Phase(Base):
    __tablename__ = "phases"

    class Status(PyEnum):
        OPEN = "open"
        CLOSED = "closed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("game_tables.id"))
    prev_phase_id = Column(Integer, ForeignKey("phases.id"))
    status = Column(Enum(Status), nullable=False, default=Status.OPEN)

    table = relationship("Table", back_populates="phases", uselist=False)
    prev_phase = relationship("Phase", uselist=False)
    territories = relationship("Territory")

    @classmethod
    def create_ready_phase(cls, db: Session) -> Self:
        phase = cls()
        for province in db.query(Province):
            territory = Territory(province=province, occupier=province.region)
            phase.territories.append(territory)
        return phase

    @property
    def latest_territories(self) -> List:
        if self.territories:
            return self.territories
        if self.prev_phase:
            return self.prev_phase.latest_territories
        return []

    def create_next_phase(self) -> Self:
        new_phase = Phase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase
