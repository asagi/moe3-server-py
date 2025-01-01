from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from typing import Self
from models.base_model import Base


class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("game_tables.id"))
    prev_phase_id = Column(Integer, ForeignKey("phases.id"))

    table = relationship("Table", back_populates="phases", uselist=False)
    prev_phase = relationship("Phase", uselist=False)

    @classmethod
    def create_ready_phase(cls) -> Self:
        return cls()
