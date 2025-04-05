from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base

if TYPE_CHECKING:
    from models.game_table_model import GameTable
    from models.player_model import Player


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    gname: Mapped[str] = mapped_column(String, nullable=False)
    picture: Mapped[str] = mapped_column(String, nullable=False)
    access_key: Mapped[str | None] = mapped_column(String, index=True)
    last_access_time: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    tables: Mapped[list["GameTable"]] = relationship("GameTable", back_populates="owner")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="user")

    def __init__(self, gid: str, gname: str, picture: str) -> None:
        self.gid = gid
        self.gname = gname
        self.picture = picture
        self.access_key = None
        self.last_access_time = None
