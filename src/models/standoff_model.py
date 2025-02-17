from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.province_model import Province


class Standoff(Base):
    __tablename__ = "standoffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(Integer, ForeignKey("phases.id"))
    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))

    province: Mapped[Province] = relationship("Province", foreign_keys=[province_id], uselist=False)

    def __init__(self, province: Province) -> None:
        self.province = province
