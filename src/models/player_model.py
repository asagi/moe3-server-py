from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import Base


class Player(Base):
    __tablename__ = "players"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    table_id = Column(Integer, ForeignKey("game_tables.id"))

    user = relationship("User", back_populates="players", uselist=False)
    table = relationship("Table", back_populates="players", uselist=False)
