from sqlalchemy import Boolean, Column, Integer, String
from models.base_model import Base


class Path(Base):
    __tablename__ = "paths"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    origin = Column("origin", String)
    dest = Column("dest", String)
    army = Column("army", Boolean, default=False)
    fleet = Column("fleet", Boolean, default=False)
