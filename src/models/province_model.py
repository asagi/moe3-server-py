from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base


class Province(Base):
    __tablename__ = "provinces"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    type = Column("type", String)
    abbr = Column("abbr", String)
    name = Column("name", String)
    jname = Column("jname", String)
    supply_center = Column("supply_center", Boolean, default=False)
    power_id = Column(Integer, ForeignKey("powers.id"))

    region = relationship("Power", uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "province",
        "polymorphic_on": type,
    }


class Inland(Province):
    __mapper_args__ = {
        "polymorphic_identity": "inland",
    }


class Coast(Province):
    __mapper_args__ = {
        "polymorphic_identity": "coast",
    }


class Water(Province):
    __mapper_args__ = {
        "polymorphic_identity": "water",
    }
