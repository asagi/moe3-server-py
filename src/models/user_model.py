from sqlalchemy import Column, Integer, String

from setup.setting import Engine
from setup.setting import Base


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    userid = Column("userid", Integer, unique=True, index=True, nullable=False)
    sname = Column("sname", String(200))
    dname = Column("dname", String(200))
    accesskey = Column("accesskey", String(200))


if __name__ == "__main__":
    Base.metadata.create_all(bind=Engine)
