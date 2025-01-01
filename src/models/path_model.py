from sqlalchemy import Boolean, Column, Integer, String
from models.base_model import Base


class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String)
    dest = Column(String)
    army = Column(Boolean, default=False)
    fleet = Column(Boolean, default=False)
