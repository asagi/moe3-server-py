from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import Base


class Table(Base):
    __tablename__ = "game_tables"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tables")
    players = relationship("Player", back_populates="table")
