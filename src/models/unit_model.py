from abc import abstractmethod
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base
from models.power_model import Power  # noqa
from models.province_model import Province  # noqa


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    power_id = Column(Integer, ForeignKey("powers.id"))
    province_id = Column(Integer, ForeignKey("provinces.id"))
    phase_id = Column(Integer, ForeignKey("phases.id"))

    power = relationship("Power", uselist=False)
    province = relationship("Province", uselist=False)

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
