from datetime import datetime
from typing import TYPE_CHECKING, Self

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.regularion_model import Regulation
from models.user_model import User
from value_objects.duration_values import DueMode

if TYPE_CHECKING:
    from models.phase_model import Phase
    from models.player_model import Player


class GameTable(Base):
    __tablename__ = "game_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    regulation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("regulations.id"), nullable=True)

    owner: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="tables")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="table")
    phases: Mapped[list["Phase"]] = relationship("Phase", back_populates="table")
    regulation: Mapped[Regulation | None] = relationship("Regulation", back_populates="table", uselist=False)

    @classmethod
    async def create_with_phases(cls, owner: User) -> Self:
        from models.phase_model import Phase

        instance = cls(owner)
        ready_phase: Phase = Phase.create_ready_phase()
        instance.phases.append(ready_phase)
        return instance

    def __init__(self, owner: User) -> None:
        self.owner = owner

    @property
    def due_mode(self) -> DueMode | None:
        if not self.regulation:
            return None
        return self.regulation.duration.due_mode

    @property
    def start_time(self) -> datetime | None:
        if not self.regulation:
            return None
        return self.regulation.start_time

    def get_order_phase_duration(self) -> int:
        if not self.regulation:
            return 0
        return self.regulation.duration.order_phase
