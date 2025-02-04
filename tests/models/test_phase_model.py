from sqlalchemy.ext.asyncio import AsyncSession

from models.game_table_model import GameTable
from models.order_model import Order
from models.phase_model import Phase
from models.user_model import User


async def test_ready_phase_creation(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    ready_phase = new_table.phases[0]
    assert ready_phase is not None
    assert ready_phase.year == 0
    assert len(ready_phase.territories) == 42
    assert len(ready_phase.units) == 22


async def test_phase_relation(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    first_phase = new_table.phases[0]
    assert first_phase is not None
    assert first_phase.prev_phase is None
    second_phase = first_phase.create_next_phase()
    assert second_phase is not None
    assert second_phase.prev_phase == first_phase
    assert second_phase.year == 1901
    assert len(second_phase.territories) == 0
    assert len(second_phase.latest_territories) == 42


async def test_phase_status(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    first_phase = new_table.phases[0]
    assert first_phase is not None
    assert first_phase.status == Phase.Status.OPEN
    second_phase = first_phase.create_next_phase()
    assert first_phase is not None
    assert first_phase.status == Phase.Status.CLOSED
    assert second_phase is not None
    assert second_phase.status == Phase.Status.OPEN


async def test_phase_year(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    first_phase = new_table.phases[0]
    assert first_phase is not None
    assert first_phase.year == 0
    second_phase = first_phase.create_next_phase()
    assert second_phase is not None
    assert second_phase.year == 1901
    third_phase = second_phase.create_next_phase()
    fourth_phase = third_phase.create_next_phase()
    fifth_phase = fourth_phase.create_next_phase()
    sixth_phase = fifth_phase.create_next_phase()
    assert sixth_phase is not None
    assert sixth_phase.year == 1901
    seventh_phase = sixth_phase.create_next_phase()
    assert seventh_phase is not None
    assert seventh_phase.type == "spring_order"
    assert seventh_phase.year == 1902


async def test_phase_order_initialization(master_data: AsyncSession) -> None:
    new_user = User(xid=123, screen_name="test", display_name="test")
    new_table = await GameTable.create_with_phases(new_user)
    first_phase = new_table.phases[0]
    assert first_phase is not None
    second_phase = first_phase.create_next_phase()
    assert second_phase is not None
    assert len(first_phase.latest_units) == 22
    assert len(first_phase.orders) == 0
    assert len(second_phase.latest_units) == 22
    assert len(second_phase.orders) == 22
    assert all(order.status == Order.Status.UNRESOLVED for order in second_phase.orders)
