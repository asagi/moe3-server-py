from sqlalchemy import Column, Integer, String

from models.base_model import Base
from setup.settings import engine


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    userid = Column("userid", Integer, unique=True, index=True, nullable=False)
    sname = Column("sname", String(200), nullable=False)
    dname = Column("dname", String(200))
    accesskey = Column("accesskey", String(200))


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
