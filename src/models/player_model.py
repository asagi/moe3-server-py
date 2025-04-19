from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.game_table_model import GameTable
from models.power_model import Power
from models.user_model import User


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_tables.id"))
    power_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("powers.id"))
    is_progress_agreed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_draw_agreed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="players", uselist=False)
    table: Mapped[GameTable] = relationship("GameTable", foreign_keys=[table_id], back_populates="players", uselist=False)
    power: Mapped["Power | None"] = relationship("Power", foreign_keys=[power_id], uselist=False)

    def __init__(self, user: User, table: GameTable) -> None:
        self.user = user
        self.table = table
