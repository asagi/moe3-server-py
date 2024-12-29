from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    xid = Column("xid", Integer, unique=True, index=True, nullable=False)
    sname = Column("sname", String(200), nullable=False)
    dname = Column("dname", String(200))
    accesskey = Column("accesskey", String(200))

    tables = relationship("Table", back_populates="user")
    players = relationship("Player", back_populates="user")
