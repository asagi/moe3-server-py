from enum import Enum as PyEnum
from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from typing import Self, List
from models.base_model import Base
from models.province_model import Province
from models.table_model import Table  # noqa
from models.territory_model import Territory
from models.unit_model import Army, Fleet
from models.power_model import Power


class Phase(Base):
    __tablename__ = "phases"

    class Status(PyEnum):
        OPEN = "open"
        CLOSED = "closed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("game_tables.id"))
    prev_phase_id = Column(Integer, ForeignKey("phases.id"))
    status = Column(Enum(Status), nullable=False, default=Status.OPEN)

    table = relationship("Table", back_populates="phases", uselist=False)
    prev_phase = relationship("Phase", uselist=False)
    territories = relationship("Territory")
    units = relationship("Unit")

    @classmethod
    def create_ready_phase(cls, db: Session) -> Self:
        phase = cls()
        for province in db.query(Province):
            territory = Territory(province=province, occupier=province.region)
            phase.territories.append(territory)

        # fmt: off
        powers = {symbol: db.query(Power).filter_by(symbol=symbol).first() for symbol in ["a", "e", "f", "g", "i", "r", "t"]}
        provinces = {
            abbr: db.query(Province).filter_by(abbr=abbr).first()
            for abbr in [
                "vie", "bud", "tri", "lvp", "lon", "edi", "par", "mar", "bre", "ber", "mun", "kie",
                "rom", "ven", "nap", "mos", "war", "stp_sc", "sev", "con", "smy", "ank",
            ]
        }
        # fmt: on
        units = [
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
        for unit in units:
            phase.units.append(unit)

        return phase

    @property
    def latest_territories(self) -> List:
        if self.territories:
            return self.territories
        if self.prev_phase:
            return self.prev_phase.latest_territories
        return []

    def create_next_phase(self) -> Self:
        new_phase = Phase(prev_phase=self)
        self.status = Phase.Status.CLOSED
        return new_phase
