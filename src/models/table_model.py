from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from models.base_model import Base
from models.user_model import User  # noqa


class Table(Base):
    __tablename__ = "game_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tables")
    players = relationship("Player", back_populates="table")
    phases = relationship("Phase", back_populates="table")

    def __init__(self, db: Session) -> None:
        from models.phase_model import Phase

        self.phases.append(Phase.create_ready_phase(db))
