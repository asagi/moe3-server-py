from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import Base
from models.phase_model import Phase  # noqa


class Table(Base):
    __tablename__ = "game_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tables")
    players = relationship("Player", back_populates="table")
    phases = relationship("Phase", back_populates="table")
