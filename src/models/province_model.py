from abc import abstractmethod
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base
from models.power_model import Power  # noqa


class Province(Base):
    __tablename__ = "provinces"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    type = Column("type", String)
    abbr = Column("abbr", String)
    ename = Column("ename", String)
    jname = Column("jname", String)

    __mapper_args__ = {
        "polymorphic_identity": "province",
        "polymorphic_on": type,
    }


class Land(Province):
    __mapper_args__ = {
        "polymorphic_identity": "land",
    }


class Coast(Province):
    __mapper_args__ = {
        "polymorphic_identity": "coast",
    }


class Sea(Province):
    __mapper_args__ = {
        "polymorphic_identity": "sea",
    }
