from sqlalchemy import Column, Integer, String
from models.base_model import Base


class Power(Base):
    __tablename__ = "powers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    name = Column(String)
    adjective = Column(String)
