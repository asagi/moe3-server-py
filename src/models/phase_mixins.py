from typing import TYPE_CHECKING

from models.path_model import Path
from models.power_model import Power
from models.province_model import Province, Water
from models.standoff_model import Standoff
from models.territory_model import Territory
from models.unit_model import Unit

if TYPE_CHECKING:
    from models.order_model import Order


def is_unresolved_move(order: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_move(),
            order.status == Order.Status.UNRESOLVED,
        ]
    )


def is_opposite_move(order: "Order", other: "Order") -> bool:
    return all(
        [
            order.is_move(),
            order.origin == other.dest,
            order.dest == other.origin,
        ]
    )


def is_attack(order: "Order", target: "Order") -> bool:
    return all(
        [
            order.power != target.power,
            Province.same(order.dest, target.origin),
        ]
    )


def is_unresolved_support(order: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_support(),
            order.status == Order.Status.UNRESOLVED,
        ]
    )


def is_valid_support(order: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_support(),
            order.status == Order.Status.VALID,
        ]
    )


def is_effective_support(order: "Order", target: "Order", exclude_power: Power | None = None) -> bool:
    from models.order_model import Order

    return all(
        [
            target.status != Order.Status.FAILURE,
            order.is_support() and order.match(target),
            order.power != exclude_power,
        ]
    )


def is_unresolved_convoy(order: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_convoy(),
            order.status == Order.Status.UNRESOLVED,
        ]
    )


def is_valid_convoy(order: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_convoy(),
            order.origin.is_water(),
            order.status == Order.Status.VALID,
        ]
    )


def is_effective_convoy(order: "Order", target: "Order") -> bool:
    from models.order_model import Order

    return all(
        [
            order.is_convoy() and order.match(target),
            order.status != Order.Status.DISLODGED,
        ]
    )


class BeforeOrderPhaseMixin:
    def initialize_next_hold_orders(self, units: list[Unit]) -> list["Order"]:
        from models.order_model import Order

        orders: list[Order] = []
        for unit in units:
            orders.append(unit.hold())

        return orders


class BeforeAdjustmentPhaseMixin:
    def initialize_next_disband_orders(self, units: list[Unit], territories: list[Territory]) -> list["Order"]:
        orders: list[Order] = []
        units_sorted_by_supply_distance: dict[Power, list[Unit]] = Path.get_units_sorted_by_supply_distance(units, territories)

        for power in Power.all():
            units_of_power: list[Unit] = [u for u in units if u.power == power]
            unit_count: int = len(units_of_power)
            supplycenters_of_power: list[Province] = [t.province for t in territories if t.occupier == power and t.suppliable]
            capacity: int = len(supplycenters_of_power)

            if unit_count > capacity:
                for unit in units_sorted_by_supply_distance[power][: unit_count - capacity]:
                    orders.append(unit.lose())

        return orders

    def should_skip_next_adjustment_phase(self, active_powers: set[Power], units: list[Unit], territories: list[Territory]) -> bool:
        powers: set[Power] = active_powers if active_powers else Power.all()
        for power in powers:
            units_of_power: list[Unit] = [u for u in units if u.power == power]
            unit_count: int = len(units_of_power)
            suppliable_provinces_of_power: list[Province] = [t.province for t in territories if t.occupier == power and t.suppliable]
            supplycenter_count: int = len(suppliable_provinces_of_power)

            if supplycenter_count == 0:
                # 滅亡のためスキップ可
                continue

            if unit_count == supplycenter_count:
                # 調整不要のためスキップ可
                continue

            if unit_count < supplycenter_count:
                if all(any(u.province == p for u in units) for p in suppliable_provinces_of_power):
                    # 全ての補給都市が塞がっている場合は増設指示不能のためスキップ可
                    continue

                # 増設指定が必要なためスキップ不可
                break

            # 要解体のためスキップ不可
            break

        else:  # nobreak
            return True

        return False


class OrderPhaseMixin:
    def initialize_next_disband_orders(self, units: list[Unit]) -> list["Order"]:
        from models.order_model import Order

        orders: list[Order] = []
        for unit in filter(lambda u: u.is_dislodged, units):
            orders.append(unit.disband())

        return orders

    def should_skip_next_retreat_phase(self, active_powers: set[Power], units: list[Unit], standoffs: list[Standoff]) -> bool:
        dislodged_units: list[Unit] = list(filter(lambda u: u.is_dislodged(), units))
        if len(dislodged_units) == 0:
            # 敗退ユニットがなければ True
            return True

        # 撤退禁止エリア
        invalid_destinations: set[Province] = set()
        invalid_destinations.update([u.province for u in units])
        invalid_destinations.update([s.province for s in standoffs])

        for unit in dislodged_units:
            if len(active_powers) > 0 and unit.power not in active_powers:
                # 非活性国のユニットは考慮しない
                continue

            valid_destinations = Path.get_available_retreat_destinations(unit, invalid_destinations.union({unit.dislodged_from}))
            if len(valid_destinations) > 0:
                # ひとつでも撤退可能な活性国のユニットがあれば False
                return False

        # 全ての敗退ユニットに撤退先がなければ True
        return True

    def resolve_marching_orders(self, unresolved_orders: list["Order"], standoffs: set[Province]) -> None:
        """行軍命令解決"""
        orders = list(filter(lambda o: not o.is_assumed(), unresolved_orders))

        # 01. 移動命令検証
        self._validate_move_orders(orders)

        # 02. 支援命令検証
        self._validate_support_orders(orders)

        # 03. 輸送命令検証
        self._validate_convoy_orders(orders)

        # 04. 支援命令のカット
        self._handle_cutting_support_orders(orders)

        # 05 . 輸送妨害の優先解決
        self._handle_disruption_convoy_order(orders, standoffs)

        # 06. 交換移動命令解決
        self._handle_switch_orders(orders, standoffs)

        # 07. 未解決移動命令解決
        self._handle_remaining_move_orders(orders, standoffs)

        # 08. 未処理の命令を全て成功判定
        self._succeed_remaining_orders(orders)

    def _handle_conflicting(self, orders: list["Order"], dest: Province, standoffs: set[Province]) -> "Order | None":
        """集合戦闘解決"""
        from models.order_model import Order

        move_orders = list(filter(lambda o: o.is_move() and Province.same(o.dest, dest), orders))
        if len(move_orders) == 0:
            # 移動命令がなければ勝者なしで終了
            return None

        if len(move_orders) == 1:
            # 移動命令が 1 つなら即勝者確定で終了
            return move_orders[0]

        # 核戦力集計
        conflict_orders: set[tuple[int, Order]] = set()
        for move_order in move_orders:
            move_order_supports: int = sum(1 for o in orders if is_effective_support(o, move_order))
            conflict_orders.add((move_order_supports, move_order))

        # 戦闘解決： 単独勝利以外は移動失敗
        max_move_order_support: int = max(t[0] for t in conflict_orders)
        if sum(1 for t in conflict_orders if t[0] == max_move_order_support) > 1:
            # 戦力トップが複数なら勝者なしで終了
            for move_order in move_orders:
                _ = move_order.fail()

            standoffs.add(move_orders[0].dest)
            return None

        # 戦力トップが複数でなければ勝者確定で終了
        winner: Order = next((t[1] for t in conflict_orders if t[0] == max_move_order_support), None)
        for move_order in move_orders:
            if move_order != winner:
                _ = move_order.fail()

        return winner

    def _handle_attacking(self, move_order: "Order", target: "Order", orders: list["Order"]) -> "Order.Status":
        """攻撃判定"""
        from models.order_model import Order

        if move_order.power == target.power:
            # 対象が自国軍なら戦闘回避により移動失敗
            _ = move_order.fail()
            return Order.Status.FAILURE

        # 支援集計
        support_count: int = sum(1 for o in orders if is_effective_support(o, move_order, target.power))
        target_support_count: int = sum(1 for o in orders if is_effective_support(o, target, move_order.power))

        # 交戦
        if support_count > target_support_count:
            # 撃退成功
            _ = move_order.success()
            _ = target.dislodged_by(move_order)
            return Order.Status.SUCCESS

        # 撃退失敗
        _ = move_order.fail()
        return Order.Status.FAILURE

    def _validate_move_orders(self, orders: list["Order"]) -> None:
        """移動命令検証"""
        from models.order_model import Order

        for move_order in filter(is_unresolved_move, orders):
            if move_order.dest is None:
                # 命令不全（異常系）
                _ = move_order.invalid()
                continue

            if move_order.unit.is_fleet():
                # 海軍移動検証
                if not Path.is_adjacent(move_order.origin, move_order.dest):
                    # 海軍の遠隔地移動は無効
                    _ = move_order.invalid()
                    continue

                if move_order.dest.is_inland():
                    # 海軍の内陸への移動は無効
                    _ = move_order.invalid()
                    continue

                continue

            if move_order.unit.is_army():
                # 陸軍移動命令検証
                if move_order.dest.is_water():
                    # 陸軍の水域への移動は無効
                    _ = move_order.invalid()
                    continue

                if not Path.is_adjacent(move_order.origin, move_order.dest):
                    effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, move_order), orders))
                    allowed_waters: set[Water] = {order.origin for order in effective_convoy_orders if order.origin.is_water()}
                    if not Path.is_reachable_by_sea(move_order.origin, move_order.dest, allowed_waters):
                        # 輸送経路の成立していない陸軍の遠隔地移動は失敗
                        _ = move_order.invalid()

                continue

    def _validate_support_orders(self, orders: list["Order"]) -> None:
        """01. 支援命令検証"""
        from models.order_model import Order

        support_orders: list[Order] = list(filter(is_unresolved_support, orders))
        if len(support_orders) == 0:
            # 支援命令がなければ終了
            return

        # 支援対象が存在する支援命令を有効判定
        for support_order in support_orders:
            for order in orders:
                if order == support_order:
                    continue
                if support_order.match(order):
                    _ = support_order.valid()
                    break
            else:  # nobreak
                _ = support_order.invalid()

    def _handle_cutting_support_orders(self, orders: list["Order"]) -> None:
        """02. 支援命令のカット"""
        from models.order_model import Order

        support_orders: list[Order] = list(filter(is_valid_support, orders))
        if len(support_orders) == 0:
            # 支援命令がなければ終了
            return

        move_orders: list[Order] = list(filter(lambda o: o.is_move(), orders))
        if len(move_orders) == 0:
            # 支援命令をカットし得る移動命令がなければ終了
            return

        for support_order in support_orders:
            if support_order.dest is not None or support_order.target_unit is None:
                # 支援命令に不備があれば無効処理（異常系）
                _ = support_order.invalid()
                continue

            attack_orders: list[Order] = list(filter(lambda o: is_attack(o, support_order), move_orders))
            if len(attack_orders) == 0:
                # 支援命令をカットし得る移動命令がなければスキップ
                continue

            if len(attack_orders) > 1:
                # 複数個所からの攻撃は即カット
                _ = support_order.cut()
                continue

            attack_order: Order = attack_orders[0]

            if support_order.target_dest is None:
                # 移動命令の支援でなければ攻撃を受けた時点でカット
                _ = support_order.cut()
                continue

            if Path.is_adjacent(support_order.origin, attack_order.origin):
                # 被輸送攻撃でなければカット
                _ = support_order.cut()
                continue

            effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, attack_order), orders))
            if len(effective_convoy_orders) == 0:
                # 被輸送攻撃と合致する輸送命令がなければカット判定終了
                continue

            allowed_waters: set[Water] = {order.origin for order in effective_convoy_orders if order.origin.is_water()}
            if not allowed_waters:
                # 被輸送攻撃と合致する輸送命令が海上になければカット判定終了（異常系）
                continue

            if not Path.is_reachable_by_sea(attack_order.origin, attack_order.dest, allowed_waters):
                # 輸送経路が成立していなければカット判定終了
                continue

            target_convoy_order: Order = next((o for o in effective_convoy_orders if Province.same(o.origin, support_order.target_dest)), None)
            if not target_convoy_order:
                # 支援対象の移動先が輸送海軍かつ輸送先が自身でなければカット
                _ = support_order.cut()
                continue

            if Path.is_reachable_by_sea(attack_order.origin, attack_order.dest, allowed_waters, target_convoy_order.origin):
                # 支援対象の移動先の輸送海軍を除去しても輸送経路が寸断されなければカット
                _ = support_order.cut()
                continue

    def _validate_convoy_orders(self, orders: list["Order"]) -> None:
        """03. 輸送命令検証"""
        from models.order_model import Order

        convoy_orders: list[Order] = list(filter(is_unresolved_convoy, orders))
        if len(convoy_orders) == 0:
            # 輸送命令がなければ終了
            return

        move_orders: list[Order] = list(filter(lambda o: o.is_move(), orders))
        if len(move_orders) == 0:
            # 輸送対象となり得る移動命令がなければ終了
            for convoy_order in convoy_orders:
                _ = convoy_order.invalid()
            return

        for convoy_order in convoy_orders:
            # 寄港中海軍の受領した輸送命令は無効（異常系）
            if not convoy_order.origin.is_water():
                _ = convoy_order.invalid()
                continue

            # 輸送対象が存在する輸送命令を有効判定
            for move_order in move_orders:
                if convoy_order.match(move_order):
                    _ = convoy_order.valid()
                    break
            else:  # nobreak
                _ = convoy_order.invalid()

    def _handle_disruption_convoy_order(self, orders: list["Order"], standoffs: set[Province]) -> None:
        """04 . 輸送妨害の優先解決"""
        from models.order_model import Order

        for convoy_order in filter(is_valid_convoy, orders):
            # 輸送命令に対する攻撃競争の勝者を取得
            winner: Order | None = self._handle_conflicting(orders, convoy_order.origin, standoffs)
            if not winner:
                # 勝者がいなければスキップ
                continue

            if winner.power == convoy_order.power:
                # 勝者が自国軍であればその移動は無条件失敗となりスキップ
                _ = winner.fail()
                continue

            # 戦闘解決
            convoy_supports: int = sum(1 for o in orders if is_effective_support(o, convoy_order))
            winner_supports: int = sum(1 for o in orders if is_effective_support(o, winner, convoy_order.power))
            if convoy_supports >= winner_supports:
                # 輸送勝利
                _ = winner.fail()
                continue

            # 輸送敗退
            _ = winner.success()
            _ = convoy_order.dislodged_by(winner)

            # 輸送路切断判定
            move_order: Order | None = next((o for o in orders if convoy_order.match(o)), None)
            if move_order is None:
                # 輸送対象なし（異常系）
                continue

            effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, move_order), orders))
            allowed_waters: set[Water] = {order.origin for order in effective_convoy_orders if order.origin.is_water()}
            if not Path.is_reachable_by_sea(move_order.origin, move_order.dest, allowed_waters):
                # 海路寸断
                if not Path.is_adjacent(move_order.origin, move_order.dest):
                    # 陸路なし
                    _ = move_order.fail()

            continue

        # 輸送経路の成立していない陸軍の遠隔地移動は失敗
        for move_order in filter(lambda o: is_unresolved_move(o) and o.unit.is_army(), orders):
            if Path.is_adjacent(move_order.origin, move_order.dest):
                continue

            effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, move_order), orders))
            allowed_waters: set[Water] = {order.origin for order in effective_convoy_orders if order.origin.is_water()}
            if not Path.is_reachable_by_sea(move_order.origin, move_order.dest, allowed_waters):
                _ = move_order.fail()

    def _handle_switch_orders(self, orders: list["Order"], standoffs: set[Province]) -> None:
        """05. 交換移動命令解決"""
        from models.order_model import Order

        move_orders: list[Order] = list(filter(is_unresolved_move, orders))
        if len(move_orders) < 2:
            # 移動命令が 2 つ以上なければ終了
            return

        for move_order in move_orders:
            if move_order.status != Order.Status.UNRESOLVED:
                # 対向命令の判定時に同時に処理済みであればスキップ
                continue

            opposite_move_order: Order | None = next((o for o in move_orders if is_opposite_move(o, move_order)), None)
            if not opposite_move_order:
                # 対向命令がなければスキップ
                continue

            # 自身の移動競争判定
            winner: Order | None = self._handle_conflicting(orders, move_order.dest, standoffs)
            # 対向命令を含む自身への攻撃競争判定
            opposite_winner: Order | None = self._handle_conflicting(orders, opposite_move_order.dest, standoffs)

            if winner is None and opposite_winner is None:
                # 双方移動失敗
                continue

            if winner == move_order and opposite_winner != opposite_move_order:
                # 自軍進軍判定
                status: Order.Status = self._handle_attacking(move_order, opposite_move_order, orders)
                if opposite_winner is not None:
                    if status == Order.Status.SUCCESS:
                        # 自軍進軍成功により opposite_winner の進軍も成功
                        _ = opposite_winner.success()
                    else:
                        # 進軍に失敗した自軍の防衛処理
                        _ = self._handle_attacking(opposite_winner, move_order, orders)
                    continue

            if winner != move_order and opposite_winner == opposite_move_order:
                # 対向進軍判定
                status: Order.Status = self._handle_attacking(opposite_winner, move_order, orders)
                if winner is not None:
                    if status == Order.Status.SUCCESS:
                        # 対向進軍成功により winner の進軍も成功
                        _ = winner.success()
                    else:
                        # 進軍に失敗した対向の防衛処理
                        _ = self._handle_attacking(winner, opposite_move_order, orders)
                    continue

            if winner != move_order and opposite_winner != opposite_move_order:
                # 双方進軍に失敗した場合のそれぞれの防衛処理
                _ = self._handle_attacking(opposite_winner, move_order, orders)
                _ = self._handle_attacking(winner, opposite_move_order, orders)
                continue

            # 海路判定
            effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, move_order), orders))
            allowed_waters: set[Water] = {order.origin for order in effective_convoy_orders if order.origin.is_water()}
            move_order_has_sea_route = Path.is_reachable_by_sea(move_order.origin, move_order.dest, allowed_waters)

            opposite_effective_convoy_orders: list[Order] = list(filter(lambda o: is_effective_convoy(o, opposite_move_order), orders))
            opposite_allowed_waters: set[Water] = {order.origin for order in opposite_effective_convoy_orders if order.origin.is_water()}
            opposite_move_order_has_sea_route = Path.is_reachable_by_sea(move_order.origin, move_order.dest, opposite_allowed_waters)

            if Path.is_adjacent(move_order.origin, move_order.dest):
                if move_order_has_sea_route or opposite_move_order_has_sea_route:
                    # 隣接地交換の場合は一方に海路ルートが存在すれば双方移動成功
                    _ = move_order.success()
                    _ = opposite_move_order.success()
                    continue
            else:
                # 海上交換は双方に海路ルートが必要
                if not move_order_has_sea_route and not opposite_move_order_has_sea_route:
                    _ = move_order.fail()
                    _ = opposite_move_order.fail()
                    continue
                if not move_order_has_sea_route:
                    _ = move_order.fail()
                    _ = self._handle_attacking(opposite_move_order, move_order, orders)
                    continue
                if not opposite_move_order_has_sea_route:
                    _ = opposite_move_order.fail()
                    _ = self._handle_attacking(move_order, opposite_move_order, orders)
                    continue

                _ = move_order.success()
                _ = opposite_move_order.success()
                continue

            # 自国軍衝突
            if move_order.power == opposite_move_order.power:
                _ = move_order.fail()
                _ = opposite_move_order.fail()
                continue

            # 直接衝突
            move_order_supports: int = sum(1 for o in orders if is_effective_support(o, move_order, opposite_move_order.power))
            opposite_move_order_supports: int = sum(1 for o in orders if is_effective_support(o, opposite_move_order, move_order.power))
            if move_order_supports == opposite_move_order_supports:
                _ = move_order.fail()
                _ = opposite_move_order.fail()
            elif move_order_supports > opposite_move_order_supports:
                _ = move_order.success()
                _ = opposite_move_order.dislodged_by(move_order)
            else:
                _ = move_order.dislodged_by(opposite_move_order)
                _ = opposite_move_order.success()
            continue

    def _handle_remaining_move_orders(self, orders: list["Order"], standoffs: set[Province]) -> None:
        """06. 未解決移動命令解決"""
        from models.order_model import Order

        while True:
            for move_order in filter(is_unresolved_move, orders):
                winner: Order | None = self._handle_conflicting(orders, move_order.dest, standoffs)
                if winner is None:
                    # 同一地点に対する全移動命令失敗確定
                    break  # jump to continue

                dest_order = next((o for o in orders if o.origin == winner.dest), None)
                if dest_order is None:
                    # 移動先に障害物なし
                    _ = winner.success()
                    break  # jump to continue

                if dest_order.is_move() and dest_order.status == Order.Status.SUCCESS:
                    # 移動先に障害物なし（移動済み）
                    _ = winner.success()
                    break  # jump to continue

                if dest_order.is_move() and dest_order.status == Order.Status.FAILURE:
                    # 移動先障害物（移動失敗移動命令）排除判定
                    _ = self._handle_attacking(winner, dest_order, orders)
                    break  # jump to continue

                if not dest_order.is_move():
                    # 移動先障害物（非移動命令）排除判定
                    _ = self._handle_attacking(winner, dest_order, orders)
                    break  # jump to continue

            else:  # nobreak
                # 未処理の移動命令がなくなるか移動先が未解決移動命令のみとなったら終了
                break

            continue

    def _succeed_remaining_orders(self, orders: list["Order"]) -> None:
        from models.order_model import Order

        unresolved_orders: list["Order"] = list(filter(lambda o: o.status == Order.Status.UNRESOLVED, orders))
        if len(unresolved_orders) == 0:
            return

        for order in unresolved_orders:
            if order.status == Order.Status.UNRESOLVED:
                _ = order.success()
