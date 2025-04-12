import enum
from datetime import datetime

from sqlalchemy import Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import Base
from value_objects.duration_values import (
    Duration,
    fixed_middle_duration,
    flex_short_duration,
)


class Regulation(Base):
    __tablename__ = "table_regulations"

    class FaceType(enum.Enum):
        GIRLS = 1
        FLAGS = 2

    class DurationType(enum.Enum):
        FIXED_MIDDLE = 1
        FLEX_SHORT = 2

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    face_type: Mapped[FaceType] = mapped_column(Enum(FaceType), nullable=False)
    duration_type: Mapped[DurationType] = mapped_column(Enum(DurationType), nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)

    def __init__(self, face_type: FaceType, duration_type: DurationType, start_time: datetime) -> None:
        if face_type not in self.FaceType:
            raise ValueError(f"Invalid face type: {face_type}")

        if duration_type not in self.DurationType:
            raise ValueError(f"Invalid duration type: {duration_type}")

        self.face_type = Regulation.FaceType(face_type)
        self.duration_type = Regulation.DurationType(duration_type)
        self.start_time = start_time

        match self.duration_type:
            case Regulation.DurationType.FIXED_MIDDLE:
                self._duration: Duration = fixed_middle_duration
            case Regulation.DurationType.FLEX_SHORT:
                self._duration: Duration = flex_short_duration
