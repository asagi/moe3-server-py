from datetime import datetime
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.regularion_model import Regulation


async def test_create_table_regulation_01(master_data: AsyncSession) -> None:
    face_type = Regulation.FaceType(1)
    duration_type = Regulation.DurationType(1)
    start_time = datetime(2025, 4, 11, 13, 0, 0)
    regulation = Regulation(face_type, duration_type, start_time)
    assert regulation is not None


async def test_create_table_regulation_02(master_data: AsyncSession) -> None:
    face_type = Regulation.FaceType(2)
    duration_type = Regulation.DurationType(2)
    start_time = datetime(2025, 4, 11, 13, 0, 0)
    regulation = Regulation(face_type, duration_type, start_time)
    assert regulation is not None


async def test_create_table_regulation_03(master_data: AsyncSession) -> None:
    face_type = cast(Regulation.FaceType, 3)  # Invalid value for FaceType
    duration_type = Regulation.DurationType(1)
    start_time = datetime(2025, 4, 11, 13, 0, 0)

    with pytest.raises(ValueError):
        _ = Regulation(face_type, duration_type, start_time)


async def test_create_table_regulation_04(master_data: AsyncSession) -> None:
    face_type = Regulation.FaceType(1)
    duration_type = cast(Regulation.DurationType, 3)  # Invalid value for DurationType
    start_time = datetime(2025, 4, 11, 13, 0, 0)

    with pytest.raises(ValueError):
        _ = Regulation(face_type, duration_type, start_time)
