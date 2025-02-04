from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base

if TYPE_CHECKING:
    from models.game_table_model import GameTable
    from models.player_model import Player


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    xid: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    screen_name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String)
    access_key: Mapped[str | None] = mapped_column(String)

    tables: Mapped[list["GameTable"]] = relationship("GameTable", back_populates="owner")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="user")

    def __init__(self, xid: int, screen_name: str, display_name: str) -> None:
        self.xid = xid
        self.screen_name = screen_name
        self.display_name = display_name
        self.access_key = None
