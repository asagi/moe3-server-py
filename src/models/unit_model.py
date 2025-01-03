from abc import abstractmethod
from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from models.base_model import Base
from models.power_model import Power
from models.province_model import Province


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    power_id = Column(Integer, ForeignKey("powers.id"))
    province_id = Column(Integer, ForeignKey("provinces.id"))
    phase_id = Column(Integer, ForeignKey("phases.id"))

    power = relationship("Power", uselist=False)
    province = relationship("Province", uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "unit",
        "polymorphic_on": type,
    }

    @classmethod
    def get_initial_units(cls, db: Session) -> List:
        powers = {power.symbol: power for power in db.query(Power).all()}
        provinces = {province.abbr: province for province in db.query(Province).all()}
        return [
            Army(province=provinces["vie"], power=powers["a"]),
            Army(province=provinces["bud"], power=powers["a"]),
            Fleet(province=provinces["tri"], power=powers["a"]),
            Army(province=provinces["lvp"], power=powers["e"]),
            Fleet(province=provinces["lon"], power=powers["e"]),
            Fleet(province=provinces["edi"], power=powers["e"]),
            Army(province=provinces["par"], power=powers["f"]),
            Army(province=provinces["mar"], power=powers["f"]),
            Fleet(province=provinces["bre"], power=powers["f"]),
            Army(province=provinces["ber"], power=powers["g"]),
            Army(province=provinces["mun"], power=powers["g"]),
            Fleet(province=provinces["kie"], power=powers["g"]),
            Army(province=provinces["rom"], power=powers["i"]),
            Army(province=provinces["ven"], power=powers["i"]),
            Fleet(province=provinces["nap"], power=powers["i"]),
            Army(province=provinces["mos"], power=powers["r"]),
            Army(province=provinces["war"], power=powers["r"]),
            Fleet(province=provinces["stp_sc"], power=powers["r"]),
            Fleet(province=provinces["sev"], power=powers["r"]),
            Army(province=provinces["con"], power=powers["t"]),
            Army(province=provinces["smy"], power=powers["t"]),
            Fleet(province=provinces["ank"], power=powers["t"]),
        ]

    @property
    @abstractmethod
    def symbol(self) -> str:
        raise NotImplementedError("This property should be overridden")


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
