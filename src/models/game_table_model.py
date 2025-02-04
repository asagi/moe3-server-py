from typing import TYPE_CHECKING, Self

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.user_model import User

if TYPE_CHECKING:
    from models.phase_model import Phase
    from models.player_model import Player


class GameTable(Base):
    __tablename__ = "game_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    owner: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="tables")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="table")
    phases: Mapped[list["Phase"]] = relationship("Phase", back_populates="table")

    @classmethod
    async def create_with_phases(cls, owner: User) -> Self:
        from models.phase_model import Phase

        instance = cls(owner)
        ready_phase: Phase = await Phase.create_ready_phase()
        instance.phases.append(ready_phase)
        return instance

    def __init__(self, owner: User) -> None:
        self.owner = owner
