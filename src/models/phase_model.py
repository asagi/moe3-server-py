from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import Base


class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("game_tables.id"))

    table = relationship("Table", back_populates="phases", uselist=False)
