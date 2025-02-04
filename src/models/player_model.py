from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.game_table_model import GameTable
from models.user_model import User


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_tables.id"))

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="players", uselist=False)
    table: Mapped[GameTable] = relationship("GameTable", foreign_keys=[table_id], back_populates="players", uselist=False)

    def __init__(self, user: User, table: GameTable) -> None:
        self.user = user
        self.table = table
