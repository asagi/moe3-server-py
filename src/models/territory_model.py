from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.power_model import Power
from models.province_model import Province

if TYPE_CHECKING:
    from models.phase_model import Phase


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(Integer, ForeignKey("phases.id"))
    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    occupier_id: Mapped[int] = mapped_column(Integer, ForeignKey("powers.id"))

    province: Mapped[Province] = relationship("Province", foreign_keys=[province_id], uselist=False)
    occupier: Mapped[Power] = relationship("Power", foreign_keys=[occupier_id], uselist=False)
    phase: Mapped["Phase"] = relationship("Phase", foreign_keys=[phase_id], back_populates="territories", uselist=False)

    def __init__(self, province: Province, occupier: Power) -> None:
        self.province = province
        self.occupier = occupier
