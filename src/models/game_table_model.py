from datetime import datetime
from typing import TYPE_CHECKING, Self

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.power_model import Power
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
        ready_phase: Phase = Phase.create_ready_phase()
        instance.phases.append(ready_phase)
        return instance

    def __init__(self, owner: User) -> None:
        self.owner = owner

    def proceed(self, active_powers: set[Power] | None = None) -> bool:
        if not self.phases:
            return False

        current_phase = self.phases[-1]
        if not current_phase.due_time:
            return False

        now = datetime.now()
        # TODO: 早回し条件が成立していた場合
        #   current_phase.due_time = now を設定（ReadyPhase, DebriefPhase 除く）

        if now >= current_phase.due_time:
            _ = current_phase.end(active_powers)
            return True
        return False
