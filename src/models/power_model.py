from sqlalchemy import Column, Integer, String
from models.base_model import Base


class Power(Base):
    __tablename__ = "powers"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    symbol = Column("symbol", String)
    name = Column("name", String)
    adjective = Column("adjective", String)
