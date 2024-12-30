from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base


class Power(Base):
    __tablename__ = "powers"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    symbol = Column("symbol", String)
    name = Column("name", String)
    adjective = Column("adjective", String)

    units = relationship("Unit", back_populates="power")
