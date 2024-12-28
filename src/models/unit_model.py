from abc import abstractmethod
from typing import Any
from sqlalchemy import Column, Integer, String
from models.base_model import Base


class Unit(Base):
    __tablename__ = "units"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    province = Column("province", String)

    @property
    @abstractmethod
    def symbol(self) -> str:
        raise NotImplementedError("This property should be overridden")

    __mapper_args__ = {
        "polymorphic_identity": "unit",
        "polymorphic_on": type,
    }


class Army(Unit):
    __mapper_args__ = {
        "polymorphic_identity": "army",
    }

    @property
    def symbol(self) -> str:
        return "a"


class Fleet(Unit):
    __mapper_args__ = {
        "polymorphic_identity": "fleet",
    }

    @property
    def symbol(self) -> str:
        return "f"
