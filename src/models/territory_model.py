from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import Base
from models.power_model import Power  # noqa


class Territory(Base):
    __tablename__ = "territories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phase_id = Column(Integer, ForeignKey("phases.id"))
    province_id = Column(Integer, ForeignKey("provinces.id"))
    occupier_id = Column(Integer, ForeignKey("powers.id"))

    province = relationship("Province", uselist=False)
    occupier = relationship("Power", uselist=False)
