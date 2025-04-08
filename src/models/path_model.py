import sys
from collections import defaultdict
from typing import Self, cast

from sqlalchemy import Boolean, ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base
from models.power_model import Power
from models.province_model import Province, Water
from models.territory_model import Territory
from models.unit_model import Unit


class Path(Base):
    __tablename__ = "paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    dest_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    army: Mapped[bool] = mapped_column(Boolean, default=False)
    fleet: Mapped[bool] = mapped_column(Boolean, default=False)

    origin: Mapped[Province] = relationship("Province", foreign_keys=[origin_id], uselist=False, lazy="selectin")
    dest: Mapped[Province] = relationship("Province", foreign_keys=[dest_id], uselist=False, lazy="selectin")

    @classmethod
    async def load_cache(cls, db: AsyncSession) -> None:
        cls._cache: list[Self] = cast(list[Self], (await db.execute(select(cls))).scalars().all())

    @classmethod
    def is_adjacent(cls, origin: Province, dest: Province) -> bool:
        if not hasattr(Path, "_cache"):
            raise ValueError("Cache is not loaded. Call `load_cache` first.")

        return next((path for path in Path._cache if path.origin_id == origin.id and path.dest_id == dest.id), None) is not None

    @classmethod
    def is_reachable_by_sea(
        cls,
        origin: Province,
        dest: Province,
        allowed_waters: set[Water],
        exclude_water: Water | None = None,
    ) -> bool:
        if not origin.is_coast() or not dest.is_coast():
            return False

        visited: set[Water] = set()
        if exclude_water:
            visited.add(exclude_water)

        return cls._is_reachable_by_sea_recursive(
            current=origin,
            dest=dest,
            visited=visited,
            allowed_waters=allowed_waters,
        )

    @classmethod
    def _is_reachable_by_sea_recursive(
        cls,
        current: Province,
        dest: Province,
        visited: set[Water],
        allowed_waters: set[Water],
    ) -> bool:
        # すでに訪問した地点は再訪問しない
        if current in visited:
            return False
        visited.add(current)

        # 海路で隣接するPathを取得
        paths = [path for path in Path._cache if path.origin == current and path.fleet]
        for path in paths:
            next_dest = path.dest

            # 同じ地点（abbr先頭3文字）が一致する場合に到達したとみなす
            if current.is_water() and Province.same(next_dest, dest):
                return True

            # 次探索地点が通行可能な Water であることを確認
            if not next_dest.is_water() or next_dest not in allowed_waters:
                continue

            # 再帰的に到達可能かを確認
            if cls._is_reachable_by_sea_recursive(
                current=next_dest,
                dest=dest,
                visited=visited,
                allowed_waters=allowed_waters,
            ):
                return True

        return False

    @classmethod
    def get_available_retreat_destinations(cls, unit: Unit, invalid_destinations: set[Province]) -> set[Province]:
        return {
            path.dest
            for path in Path._cache
            if path.origin == unit.province and path.dest not in invalid_destinations and (path.army if unit.is_army() else path.fleet)
        }

    @classmethod
    def get_units_sorted_by_supply_distance(cls, units: list[Unit], territories: list[Territory]) -> dict[Power, list[Unit]]:
        # 各国補給都市
        supply_centers: dict[Power, set[str]] = defaultdict(set)  # abbrの先頭3文字で格納
        for territory in territories:
            if territory.suppliable and territory.occupier:
                supply_centers[territory.occupier].add(territory.province.abbr[:3])

        # 各ユニットの最短距離を計算
        unit_distances: list[tuple[Unit, int]] = []
        for unit in units:
            if unit.power not in supply_centers:
                continue  # 自国の補給都市がない場合はスキップ

            # BFS で最短距離を求める (Province は abbreviation 3 文字で管理)
            queue: list[tuple[str, int]] = [(province, 0) for province in supply_centers[unit.power]]
            visited: set[str] = set(province for province, _ in queue)

            min_distance: int = sys.maxsize
            while queue:
                current, dist = queue.pop(0)
                if current == unit.province.abbr[:3]:
                    min_distance = dist
                    break

                for path in cls._cache:
                    if path.origin.abbr[:3] == current and path.dest.abbr[:3] not in visited:  # abbrの先頭3文字で比較
                        queue.append((path.dest.abbr[:3], dist + 1))
                        visited.add(path.dest.abbr[:3])

            unit_distances.append((unit, min_distance))

        # ソート: 距離降順 → Fleet優先 → abbr昇順
        unit_distances.sort(key=lambda x: (-x[1], x[0].is_army(), x[0].province.abbr))

        # Power 別にまとめる
        sorted_units_by_power: dict[Power, list[Unit]] = defaultdict(list)
        for unit, _ in unit_distances:
            sorted_units_by_power[unit.power].append(unit)

        return sorted_units_by_power
