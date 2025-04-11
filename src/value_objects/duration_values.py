import enum
from typing import NamedTuple


class DueMode(enum.Enum):
    FIXED = 1
    FLEXIBLE = 2


class Duration(NamedTuple):
    due_mode: DueMode
    order_phase: int
    retreat_phase: int
    adjustment_phase: int
    debrief_phase: int


flex_short_duration = Duration(
    due_mode=DueMode.FLEXIBLE,
    order_phase=60,
    retreat_phase=10,
    adjustment_phase=10,
    debrief_phase=60 * 24,
)

fixed_middle_duration = Duration(
    due_mode=DueMode.FLEXIBLE,
    order_phase=60 * 24,
    retreat_phase=60,
    adjustment_phase=60,
    debrief_phase=60 * 24,
)
