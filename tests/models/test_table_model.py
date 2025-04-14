from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import pytest
from dateutil import parser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.game_table_model import GameTable
from models.phase_model import Phase
from models.regularion_model import Regulation
from models.user_model import User


@pytest.fixture
async def table01(master_data: AsyncSession) -> GameTable:
    new_user = User(gid="123", gname="test", picture="picture")
    new_table = await GameTable.create_with_phases(new_user)
    master_data.add(new_table)
    await master_data.commit()
    return new_table


@pytest.fixture
async def table02(master_data: AsyncSession) -> GameTable:
    face_type = Regulation.FaceType.GIRLS
    duration_type = Regulation.DurationType.FIXED_MIDDLE
    satrt_time = parser.isoparse("2025-04-13T11:00:00.000Z").replace(tzinfo=None)
    regulation = Regulation(face_type, duration_type, satrt_time)
    new_table = await GameTable.create_with_phases(None, regulation)
    master_data.add(new_table)
    await master_data.commit()
    return new_table


@pytest.fixture
async def table03(master_data: AsyncSession) -> GameTable:
    new_user = User(gid="123", gname="test", picture="picture")
    face_type = Regulation.FaceType.FLAGS
    duration_type = Regulation.DurationType.FLEX_SHORT
    satrt_time = parser.isoparse("2025-04-13T11:00:00.000Z").replace(tzinfo=None)
    regulation = Regulation(face_type, duration_type, satrt_time)
    new_table = await GameTable.create_with_phases(new_user, regulation)
    master_data.add(new_table)
    await master_data.commit()
    return new_table


async def test_table_creation_01(master_data: AsyncSession, table01: GameTable) -> None:
    table: GameTable | None = (await master_data.execute(select(GameTable).filter_by(id=table01.id))).scalar_one_or_none()
    assert table is not None
    assert len(table.phases) == 1
    phase = table.phases[-1]
    assert phase is not None
    assert phase.type == "ready"
    assert phase.status == Phase.Status.OPEN
    assert table.owner is not None
    assert table.owner.gid == "123"


async def test_table_creation_02(master_data: AsyncSession, table02: GameTable) -> None:
    table: GameTable | None = (await master_data.execute(select(GameTable).filter_by(id=table02.id))).scalar_one_or_none()
    assert table is not None
    assert len(table.phases) == 1
    phase = table.phases[-1]
    assert phase is not None
    assert phase.type == "ready"
    assert phase.status == Phase.Status.OPEN
    assert table.regulation is not None
    assert table.regulation.face_type == Regulation.FaceType.GIRLS
    assert table.regulation.duration_type == Regulation.DurationType.FIXED_MIDDLE


async def test_table_creation_03(master_data: AsyncSession, table03: GameTable) -> None:
    table: GameTable | None = (await master_data.execute(select(GameTable).filter_by(id=table03.id))).scalar_one_or_none()
    assert table is not None
    assert len(table.phases) == 1
    phase = table.phases[-1]
    assert phase is not None
    assert phase.type == "ready"
    assert phase.status == Phase.Status.OPEN
    assert table.owner is not None
    assert table.owner.gid == "123"
    assert table.regulation is not None
    assert table.regulation.face_type == Regulation.FaceType.FLAGS
    assert table.regulation.duration_type == Regulation.DurationType.FLEX_SHORT


async def test_table_regulation_fixed_middle_01(master_data: AsyncSession, table02: GameTable) -> None:
    ready_phase = table02.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.type == "spring_order"
    assert spring_order_1901.due_time == datetime(2025, 4, 14, 11, 0)


async def test_table_regulation_fixed_middle_02(master_data: AsyncSession, table02: GameTable) -> None:
    ready_phase = table02.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 14, 11, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.type == "spring_retreat"
        assert spring_retreat_1901.due_time == datetime(2025, 4, 14, 12, 0)


async def test_table_regulation_fixed_middle_03(master_data: AsyncSession, table02: GameTable) -> None:
    ready_phase = table02.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 14, 11, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.due_time == datetime(2025, 4, 14, 12, 0)

        _ = stack.enter_context(patch.object(spring_retreat_1901, "_should_skip_next_phase", return_value=False))
        fall_order_1901 = spring_retreat_1901.end()
        assert fall_order_1901 is not None
        assert fall_order_1901.type == "fall_order"
        assert fall_order_1901.due_time == datetime(2025, 4, 15, 11, 0)


async def test_table_regulation_flex_short_01(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.type == "spring_order"
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)


async def test_table_regulation_flex_short_02_01(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 0)))
        next_phase = spring_order_1901.end()
        assert next_phase is not None
        assert next_phase.type == "spring_retreat"
        assert next_phase.due_time == datetime(2025, 4, 13, 12, 10)


async def test_table_regulation_flex_short_02_02(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 3)))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.type == "spring_retreat"
        assert spring_retreat_1901.due_time == datetime(2025, 4, 13, 12, 10)


async def test_table_regulation_flex_short_02_03(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()

    # Phase#end() で生成されたインスタンスを commit() 前にセッションに追加する必要がある
    # GameTable のインスタンスを再度 add() することで関連付けられた新インスタンスも cascade により追加される
    master_data.add(table03)
    await master_data.commit()

    # new_phase を疑似的にリロード
    # 元は TZ が消えることの確認の為だったが内部的に UTC かつ TZ なしで統一する方針を採用（2025/04/14）
    await master_data.refresh(spring_order_1901)

    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 11, 45)))
        spring_retreat_1901 = spring_order_1901.end()
        master_data.add(table03)
        await master_data.commit()
        await master_data.refresh(spring_order_1901)
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.type == "spring_retreat"
        assert spring_retreat_1901.due_time == datetime(2025, 4, 13, 11, 55)


async def test_table_regulation_flex_short_03_01(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 0)))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.due_time == datetime(2025, 4, 13, 12, 10)

        _ = stack.enter_context(patch.object(spring_retreat_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 10)))
        fall_order_1901 = spring_retreat_1901.end()
        assert fall_order_1901 is not None
        assert fall_order_1901.type == "fall_order"
        assert fall_order_1901.due_time == datetime(2025, 4, 13, 13, 10)


async def test_table_regulation_flex_short_03_02(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 3)))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.type == "spring_retreat"
        assert spring_retreat_1901.due_time == datetime(2025, 4, 13, 12, 10)

        _ = stack.enter_context(patch.object(spring_retreat_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 12, 13)))
        fall_order_1901 = spring_retreat_1901.end()
        assert fall_order_1901 is not None
        assert fall_order_1901.type == "fall_order"
        assert fall_order_1901.due_time == datetime(2025, 4, 13, 13, 10)


async def test_table_regulation_flex_short_03_03(master_data: AsyncSession, table03: GameTable) -> None:
    ready_phase = table03.phases[-1]
    spring_order_1901 = ready_phase.end()
    assert spring_order_1901 is not None
    assert spring_order_1901.due_time == datetime(2025, 4, 13, 12, 0)
    with ExitStack() as stack:
        _ = stack.enter_context(patch.object(spring_order_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 11, 45)))
        spring_retreat_1901 = spring_order_1901.end()
        assert spring_retreat_1901 is not None
        assert spring_retreat_1901.type == "spring_retreat"
        assert spring_retreat_1901.due_time == datetime(2025, 4, 13, 11, 55)

        _ = stack.enter_context(patch.object(spring_retreat_1901, "_should_skip_next_phase", return_value=False))
        _ = stack.enter_context(patch("models.phase_model.get_current_time", return_value=datetime(2025, 4, 13, 11, 50)))
        fall_order_1901 = spring_retreat_1901.end()
        assert fall_order_1901 is not None
        assert fall_order_1901.type == "fall_order"
        assert fall_order_1901.due_time == datetime(2025, 4, 13, 12, 50)
