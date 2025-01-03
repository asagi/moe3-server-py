from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    xid = Column(Integer, unique=True, index=True, nullable=False)
    sname = Column(String(200), nullable=False)
    dname = Column(String(200))
    accesskey = Column(String(200))

    tables = relationship("Table", back_populates="user")
    players = relationship("Player", back_populates="user")
