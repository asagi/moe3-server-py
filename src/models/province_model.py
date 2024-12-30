from sqlalchemy import Column, Integer, String
from models.base_model import Base


class Province(Base):
    __tablename__ = "provinces"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    type = Column("type", String)
    abbr = Column("abbr", String)
    name = Column("name", String)
    jname = Column("jname", String)

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
