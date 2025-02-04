# pyright: reportPrivateUsage=false
from sqlalchemy.ext.asyncio import AsyncSession

from models.order_model import Order, SupportOrder
from models.phase_model import SpringOrderPhase
from models.power_model import Power
from models.province_model import Province
from models.unit_model import Army, Fleet

"""
集合戦闘解決
"""


async def test_00__handle_conflict_move_orders_to_dest_01(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    phase.orders.extend([])
    winner = phase._handle_conflicting(phase.orders, Province.BUD, set())
    assert winner is None


async def test_00__handle_conflict_move_orders_to_dest_02(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bur_par = Army(Power.F, Province.BUR).move_to(Province.PAR)
    phase.orders.extend([fa_bur_par])
    winner = phase._handle_conflicting(phase.orders, Province.PAR, set())
    assert winner == fa_bur_par


async def test_00__handle_conflict_move_orders_to_dest_03(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bur_par = Army(Power.F, Province.BUR).move_to(Province.PAR)
    fa_gas_par = Army(Power.F, Province.GAS).move_to(Province.PAR)
    phase.orders.extend([fa_bur_par, fa_gas_par])
    winner = phase._handle_conflicting(phase.orders, Province.PAR, set())
    assert winner is None


async def test_00__handle_conflict_move_orders_to_dest_04(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bur_par = Army(Power.F, Province.BUR).move_to(Province.PAR)
    fa_gas_par = Army(Power.F, Province.GAS).move_to(Province.PAR)
    fa_pic_supp = Army(Power.F, Province.PIC).support(fa_bur_par)
    phase.orders.extend([fa_bur_par, fa_gas_par, fa_pic_supp])
    winner = phase._handle_conflicting(phase.orders, Province.PAR, set())
    assert winner == fa_bur_par


"""
支援命令検証
"""


async def test_02__validate_support_orders_01(master_data: AsyncSession) -> None:
    """前提： そもそも支援命令がなければ処理終了"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_hold = Army(Power.A, Province.VIE).hold()
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_hold])
    phase._validate_support_orders(phase.orders)
    assert all(order.status == Order.Status.UNRESOLVED for order in phase.orders)


async def test_02__validate_support_orders_02(master_data: AsyncSession) -> None:
    """個別： マッチする支援対象がなければ支援失敗"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_supp = Army(Power.A, Province.VIE).support(aa_bud_hold)
    aa_vie_supp.target_dest = Province.TRI
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_supp])
    phase._validate_support_orders(phase.orders)
    assert aa_vie_supp.status == SupportOrder.Status.INVALID


async def test_02__validate_support_orders_03(master_data: AsyncSession) -> None:
    """個別： マッチする支援対象があれば未処理のまま"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_supp = Army(Power.A, Province.VIE).support(aa_bud_hold)
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_supp])
    phase._validate_support_orders(phase.orders)
    assert aa_vie_supp.status == SupportOrder.Status.VALID


"""
輸送命令検証
"""


async def test_03__validate_convoy_orders_01(master_data: AsyncSession) -> None:
    """前提： そもそも輸送命令がなければ処理終了"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_hold = Army(Power.A, Province.VIE).hold()
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_hold])
    phase._validate_convoy_orders(phase.orders)
    assert all(order.status == Order.Status.UNRESOLVED for order in phase.orders)


async def test_03__validate_convoy_orders_02(master_data: AsyncSession) -> None:
    """前提： そもそも移動命令がなければ全て無効"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_conv = Fleet(Power.A, Province.TRI).convoy(aa_bud_hold)
    aa_vie_conv = Army(Power.A, Province.VIE).convoy(aa_bud_hold)
    phase.orders.extend([aa_bud_hold, af_tri_conv, aa_vie_conv])
    phase._validate_convoy_orders(phase.orders)
    assert aa_bud_hold.status == Order.Status.UNRESOLVED
    assert af_tri_conv.status == Order.Status.INVALID
    assert aa_vie_conv.status == Order.Status.INVALID


async def test_03__validate_convoy_orders_04(master_data: AsyncSession) -> None:
    """個別： 輸送対象が存在すれば有効（存在しなければ無効）"""
    phase = SpringOrderPhase()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.BRE)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bre)
    ea_lon_bel_assumed = Army(Power.E, Province.LON).move_to(Province.BEL).assumed_by(Power.F)
    ff_nth_conv = Fleet(Power.F, Province.NTH).convoy(ea_lon_bel_assumed)
    phase.orders.extend([ea_lon_bre, ef_eng_conv, ff_nth_conv])
    phase._validate_convoy_orders(phase.orders)
    assert ea_lon_bre.status == Order.Status.UNRESOLVED
    assert ef_eng_conv.status == Order.Status.VALID
    assert ff_nth_conv.status == Order.Status.INVALID


"""
支援命令のカット
"""


async def test_04__handle_cutting_support_orders_01(master_data: AsyncSession) -> None:
    """前提： そもそもカットされる支援命令がなければ処理終了"""
    phase = SpringOrderPhase()
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_hold = Army(Power.A, Province.VIE).hold()
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_hold])
    phase._handle_cutting_support_orders(phase.orders)
    assert all(order.status == Order.Status.UNRESOLVED for order in phase.orders)


async def test_04__handle_cutting_support_orders_02(master_data: AsyncSession) -> None:
    """前提： そもそもカットする移動命令がなければ処理終了"""
    phase = SpringOrderPhase()
    af_bre_hold = Fleet(Power.F, Province.BRE).hold()
    aa_par_supp = Army(Power.F, Province.PAR).support(af_bre_hold)
    phase.orders.extend([af_bre_hold, aa_par_supp])
    phase._handle_cutting_support_orders(phase.orders)
    assert aa_par_supp.status == Order.Status.UNRESOLVED


async def test_04__handle_cutting_support_orders_03(master_data: AsyncSession) -> None:
    """個別 step.01： 自分に向かってくる移動命令がなければカットされない"""
    phase = SpringOrderPhase()
    ff_bre_hold = Fleet(Power.F, Province.BRE).hold()
    fa_par_supp = Army(Power.F, Province.PAR).support(ff_bre_hold)
    ga_mun_bur = Army(Power.G, Province.MUN).move_to(Province.BUR)
    phase.orders.extend([ff_bre_hold, fa_par_supp, ga_mun_bur])
    phase._handle_cutting_support_orders(phase.orders)
    assert fa_par_supp.status == Order.Status.UNRESOLVED


async def test_04__handle_cutting_support_orders_04(master_data: AsyncSession) -> None:
    """個別 step.02： 自分に向かってくる移動命令が 2 つ以上ならカット"""
    phase = SpringOrderPhase()
    ff_bre_hold = Fleet(Power.F, Province.BRE).hold()
    fa_par_supp = Army(Power.F, Province.PAR).support(ff_bre_hold).valid()
    ga_bur_par = Army(Power.G, Province.BUR).move_to(Province.PAR)
    ga_pic_par = Army(Power.G, Province.PIC).move_to(Province.PAR)
    phase.orders.extend([ff_bre_hold, fa_par_supp, ga_bur_par, ga_pic_par])
    phase._handle_cutting_support_orders(phase.orders)
    assert fa_par_supp.status == Order.Status.CUT


async def test_04__handle_cutting_support_orders_05(master_data: AsyncSession) -> None:
    """個別 step.03： 自分の支援対象が移動命令でなければカット"""
    phase = SpringOrderPhase()
    ff_bre_hold = Fleet(Power.F, Province.BRE).hold()
    fa_par_supp = Army(Power.F, Province.PAR).support(ff_bre_hold).valid()
    ga_bur_par = Army(Power.G, Province.BUR).move_to(Province.PAR)
    phase.orders.extend([ff_bre_hold, fa_par_supp, ga_bur_par])
    phase._handle_cutting_support_orders(phase.orders)
    assert fa_par_supp.status == Order.Status.CUT


async def test_04__handle_cutting_support_orders_06(master_data: AsyncSession) -> None:
    """個別 step.04： 自分への攻撃が被輸送攻撃でなければカット"""
    phase = SpringOrderPhase()
    fa_bre_pic = Army(Power.F, Province.BRE).move_to(Province.PIC)
    fa_par_supp = Army(Power.F, Province.PAR).support(fa_bre_pic).valid()
    ga_bur_par = Army(Power.G, Province.BUR).move_to(Province.PAR)
    phase.orders.extend([fa_bre_pic, fa_par_supp, ga_bur_par])
    phase._handle_cutting_support_orders(phase.orders)
    assert fa_par_supp.status == Order.Status.CUT


async def test_04__handle_cutting_support_orders_07(master_data: AsyncSession) -> None:
    """個別 step.05： 被輸送攻撃と合致する輸送命令がなければカット判定終了"""
    phase = SpringOrderPhase()
    ff_iri_eng = Fleet(Power.F, Province.IRI).move_to(Province.ENG)
    ff_par_supp = Fleet(Power.F, Province.PAR).support(ff_iri_eng)
    ea_lon_par = Army(Power.E, Province.LON).move_to(Province.PAR)
    phase.orders.extend([ff_iri_eng, ff_par_supp, ea_lon_par])
    phase._handle_cutting_support_orders(phase.orders)
    assert ff_par_supp.status == Order.Status.UNRESOLVED


async def test_04__handle_cutting_support_orders_08(master_data: AsyncSession) -> None:
    """個別 step.06： 輸送経路が成立していなければカット判定終了"""
    phase = SpringOrderPhase()
    ff_iri_eng = Fleet(Power.F, Province.IRI).move_to(Province.ENG)
    ff_bre_supp = Fleet(Power.F, Province.BRE).support(ff_iri_eng)
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.BRE)
    ef_mao_conv = Fleet(Power.E, Province.MAO).convoy(ea_lon_bre)
    phase.orders.extend([ff_iri_eng, ff_bre_supp, ea_lon_bre, ef_mao_conv])
    phase._handle_cutting_support_orders(phase.orders)
    assert ff_bre_supp.status == Order.Status.UNRESOLVED


async def test_04__handle_cutting_support_orders_09(master_data: AsyncSession) -> None:
    """個別 step.07： 支援対象の移動先が輸送海軍かつ輸送先が自身でなければカット"""
    phase = SpringOrderPhase()
    ff_mao_gas = Fleet(Power.F, Province.MAO).move_to(Province.GAS)
    ff_bre_supp = Fleet(Power.F, Province.BRE).support(ff_mao_gas).valid()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.BRE)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bre)
    phase.orders.extend([ff_mao_gas, ff_bre_supp, ea_lon_bre, ef_eng_conv])
    phase._handle_cutting_support_orders(phase.orders)
    assert ff_bre_supp.status == Order.Status.CUT


async def test_04__handle_cutting_support_orders_10(master_data: AsyncSession) -> None:
    """個別 step.08： 支援対象の移動先の輸送海軍を除去して輸送経路が寸断されればカットされない"""
    phase = SpringOrderPhase()
    ff_iri_eng = Fleet(Power.F, Province.IRI).move_to(Province.ENG)
    ff_bel_supp = Fleet(Power.F, Province.BEL).support(ff_iri_eng).valid()
    ea_lon_bel = Army(Power.E, Province.LON).move_to(Province.BEL)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bel)
    phase.orders.extend([ff_iri_eng, ff_bel_supp, ea_lon_bel, ef_eng_conv])
    phase._handle_cutting_support_orders(phase.orders)
    assert ff_bel_supp.status == Order.Status.VALID


async def test_04__handle_cutting_support_orders_11(master_data: AsyncSession) -> None:
    """個別 step.09： 支援対象の移動先の輸送海軍を除去しても輸送経路が寸断されなければカット"""
    phase = SpringOrderPhase()
    ff_iri_eng = Fleet(Power.F, Province.IRI).move_to(Province.ENG)
    ff_bel_supp = Fleet(Power.F, Province.BEL).support(ff_iri_eng).valid()
    ea_lon_bel = Army(Power.E, Province.LON).move_to(Province.BEL)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bel)
    ef_nth_conv = Fleet(Power.E, Province.NTH).convoy(ea_lon_bel)
    phase.orders.extend([ff_iri_eng, ff_bel_supp, ea_lon_bel, ef_eng_conv, ef_nth_conv])
    phase._handle_cutting_support_orders(phase.orders)
    assert ff_bel_supp.status == Order.Status.CUT


"""
輸送妨害の優先解決
"""


async def test_05__handle_disruption_convoy_order_01(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.PIC)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bre).valid()
    ff_bre_eng = Fleet(Power.F, Province.BRE).move_to(Province.ENG)
    ff_pic_supp = Fleet(Power.F, Province.PIC).support(ff_bre_eng).valid()
    phase.orders.extend([ea_lon_bre, ef_eng_conv, ff_bre_eng, ff_pic_supp])
    phase._handle_disruption_convoy_order(phase.orders, set())
    assert ea_lon_bre.status == Order.Status.FAILURE
    assert ef_eng_conv.status == Order.Status.DISLODGED
    assert ff_bre_eng.status == Order.Status.SUCCESS
    assert ff_pic_supp.status == Order.Status.VALID


async def test_05__handle_disruption_convoy_order_02(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.PIC)
    ff_eng_conv = Fleet(Power.F, Province.ENG).convoy(ea_lon_bre).valid()
    ff_bre_eng = Fleet(Power.F, Province.BRE).move_to(Province.ENG)
    ff_pic_supp = Fleet(Power.F, Province.PIC).support(ff_bre_eng).invalid()
    phase.orders.extend([ea_lon_bre, ff_eng_conv, ff_bre_eng, ff_pic_supp])
    phase._handle_disruption_convoy_order(phase.orders, set())
    assert ea_lon_bre.status == Order.Status.UNRESOLVED
    assert ff_eng_conv.status == Order.Status.VALID
    assert ff_bre_eng.status == Order.Status.FAILURE
    assert ff_pic_supp.status == Order.Status.INVALID


async def test_05__handle_disruption_convoy_order_03(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.PIC)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bre).valid()
    ff_bre_eng = Fleet(Power.F, Province.BRE).move_to(Province.ENG)
    phase.orders.extend([ea_lon_bre, ef_eng_conv, ff_bre_eng])
    phase._handle_disruption_convoy_order(phase.orders, set())
    assert ea_lon_bre.status == Order.Status.UNRESOLVED
    assert ef_eng_conv.status == Order.Status.VALID
    assert ff_bre_eng.status == Order.Status.FAILURE


async def test_05__handle_disruption_convoy_order_04(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ea_lon_bre = Army(Power.E, Province.LON).move_to(Province.PIC)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_bre).valid()
    ff_bre_eng = Fleet(Power.F, Province.BRE).move_to(Province.ENG)
    gf_nth_eng = Fleet(Power.G, Province.NTH).move_to(Province.ENG)
    phase.orders.extend([ea_lon_bre, ef_eng_conv, ff_bre_eng, gf_nth_eng])
    phase._handle_disruption_convoy_order(phase.orders, set())
    assert ea_lon_bre.status == Order.Status.UNRESOLVED
    assert ef_eng_conv.status == Order.Status.VALID
    assert ff_bre_eng.status == Order.Status.FAILURE
    assert gf_nth_eng.status == Order.Status.FAILURE


"""
交換移動命令解決
"""


async def test_06__handle_switch_orders_01(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    phase.orders.extend([fa_bel_hol])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.UNRESOLVED


async def test_06__handle_switch_orders_02(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_ruh = Army(Power.G, Province.HOL).move_to(Province.RUH)
    phase.orders.extend([fa_bel_hol, ga_hol_ruh])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.UNRESOLVED
    assert ga_hol_ruh.status == Order.Status.UNRESOLVED


async def test_06__handle_switch_orders_03(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    phase.orders.extend([fa_bel_hol, ga_hol_bel])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_04(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    gf_nth_conv = Fleet(Power.G, Province.NTH).convoy(ga_hol_bel).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, gf_nth_conv])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS
    assert ga_hol_bel.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_05(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    fa_hol_bel = Army(Power.F, Province.HOL).move_to(Province.BEL)
    phase.orders.extend([fa_bel_hol, fa_hol_bel])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert fa_hol_bel.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_06(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ga_ruh_supp = Army(Power.G, Province.RUH).support(ga_hol_bel).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ga_ruh_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.DISLODGED
    assert ga_hol_bel.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_07(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    fa_ruh_supp = Army(Power.F, Province.RUH).support(fa_bel_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, fa_ruh_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS
    assert ga_hol_bel.status == Order.Status.DISLODGED


async def test_06__handle_switch_orders_08(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ga_ruh_bel = Army(Power.G, Province.RUH).move_to(Province.BEL)
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ga_ruh_bel])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.FAILURE
    assert ga_ruh_bel.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_09(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    fa_ruh_hol = Army(Power.F, Province.RUH).move_to(Province.HOL)
    phase.orders.extend([fa_bel_hol, ga_hol_bel, fa_ruh_hol])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.FAILURE
    assert fa_ruh_hol.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_10(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ea_pic_bel = Army(Power.E, Province.PIC).move_to(Province.BEL)
    ea_bur_supp = Army(Power.E, Province.BUR).support(ea_pic_bel).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ea_pic_bel, ea_bur_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.DISLODGED
    assert ga_hol_bel.status == Order.Status.FAILURE
    assert ea_pic_bel.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_11(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ea_pic_bel = Army(Power.E, Province.PIC).move_to(Province.BEL)
    ea_bur_supp = Army(Power.E, Province.BUR).support(ea_pic_bel).valid()
    ra_ruh_hol = Army(Power.R, Province.RUH).move_to(Province.HOL)
    ra_kie_supp = Army(Power.R, Province.KIE).support(ra_ruh_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ea_pic_bel, ea_bur_supp, ra_ruh_hol, ra_kie_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.DISLODGED
    assert ga_hol_bel.status == Order.Status.DISLODGED
    assert ea_pic_bel.status == Order.Status.SUCCESS
    assert ra_ruh_hol.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_12(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ea_pic_bel = Army(Power.E, Province.PIC).move_to(Province.BEL)
    ea_bur_supp = Army(Power.E, Province.BUR).support(ea_pic_bel).valid()
    ra_kie_supp = Army(Power.R, Province.KIE).support(fa_bel_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ea_pic_bel, ea_bur_supp, ra_kie_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS
    assert ga_hol_bel.status == Order.Status.DISLODGED
    assert ea_pic_bel.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_13(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ea_bur_supp = Army(Power.E, Province.BUR).support(ga_hol_bel).valid()
    ra_ruh_hol = Army(Power.R, Province.RUH).move_to(Province.HOL)
    ra_kie_supp = Army(Power.R, Province.KIE).support(ra_ruh_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ea_bur_supp, ra_ruh_hol, ra_kie_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.DISLODGED
    assert ga_hol_bel.status == Order.Status.SUCCESS
    assert ra_ruh_hol.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_14(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ra_ruh_hol = Army(Power.R, Province.RUH).move_to(Province.HOL)
    ra_kie_supp = Army(Power.R, Province.KIE).support(ra_ruh_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ra_ruh_hol, ra_kie_supp])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.DISLODGED
    assert ra_ruh_hol.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_15(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ia_tus_tun = Army(Power.I, Province.TUS).move_to(Province.TUN)
    ta_tun_tus = Army(Power.T, Province.TUN).move_to(Province.TUS)
    if_lyo_conv = Fleet(Power.I, Province.LYO).convoy(ia_tus_tun).valid()
    if_wes_conv = Fleet(Power.I, Province.WES).convoy(ia_tus_tun).valid()
    tf_tys_conv = Fleet(Power.T, Province.TYS).convoy(ta_tun_tus).valid()
    phase.orders.extend([ia_tus_tun, ta_tun_tus, if_lyo_conv, if_wes_conv, tf_tys_conv])
    phase._handle_switch_orders(phase.orders, set())
    assert ia_tus_tun.status == Order.Status.SUCCESS
    assert ta_tun_tus.status == Order.Status.SUCCESS


async def test_06__handle_switch_orders_16(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ia_tus_tun = Army(Power.I, Province.TUS).move_to(Province.TUN)
    ta_tun_tus = Army(Power.T, Province.TUN).move_to(Province.TUS)
    if_lyo_conv = Fleet(Power.I, Province.LYO).convoy(ia_tus_tun).valid()
    if_wes_conv = Fleet(Power.I, Province.WES).convoy(ia_tus_tun).valid()
    phase.orders.extend([ia_tus_tun, ta_tun_tus, if_lyo_conv, if_wes_conv])
    phase._handle_switch_orders(phase.orders, set())
    assert ia_tus_tun.status == Order.Status.FAILURE
    assert ta_tun_tus.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_17(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ia_tus_tun = Army(Power.I, Province.TUS).move_to(Province.TUN)
    ta_tun_tus = Army(Power.T, Province.TUN).move_to(Province.TUS)
    if_lyo_conv = Fleet(Power.I, Province.LYO).convoy(ia_tus_tun).valid()
    tf_tys_conv = Fleet(Power.T, Province.TYS).convoy(ta_tun_tus).valid()
    phase.orders.extend([ia_tus_tun, ta_tun_tus, if_lyo_conv, tf_tys_conv])
    phase._handle_switch_orders(phase.orders, set())
    assert ia_tus_tun.status == Order.Status.FAILURE
    assert ta_tun_tus.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_18(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    ia_tus_tun = Army(Power.I, Province.TUS).move_to(Province.TUN)
    ta_tun_tus = Army(Power.T, Province.TUN).move_to(Province.TUS)
    if_lyo_conv = Fleet(Power.I, Province.LYO).convoy(ia_tus_tun).valid()
    phase.orders.extend([ia_tus_tun, ta_tun_tus, if_lyo_conv])
    phase._handle_switch_orders(phase.orders, set())
    assert ia_tus_tun.status == Order.Status.FAILURE
    assert ta_tun_tus.status == Order.Status.FAILURE


async def test_06__handle_switch_orders_19(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ea_pic_bel = Army(Power.E, Province.PIC).move_to(Province.BEL)
    aa_kie_hol = Army(Power.A, Province.KIE).move_to(Province.HOL)
    phase.orders.extend([fa_bel_hol, ga_hol_bel, ea_pic_bel, aa_kie_hol])
    phase._handle_switch_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.FAILURE
    assert ea_pic_bel.status == Order.Status.FAILURE
    assert aa_kie_hol.status == Order.Status.FAILURE


"""
未解決移動命令解決
"""


async def test_07__handle_remaining_move_orders_01(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    phase.orders.extend([])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert True


async def test_07__handle_remaining_move_orders_02(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_bel = Army(Power.G, Province.RUH).move_to(Province.HOL)
    phase.orders.extend([fa_bel_hol, ga_hol_bel])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE
    assert ga_hol_bel.status == Order.Status.FAILURE


async def test_07__handle_remaining_move_orders_03(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    phase.orders.extend([fa_bel_hol])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS


async def test_07__handle_remaining_move_orders_04(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_kie = Army(Power.G, Province.HOL).move_to(Province.KIE).success()
    phase.orders.extend([fa_bel_hol, ga_hol_kie])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS


async def test_07__handle_remaining_move_orders_05(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_kie = Army(Power.G, Province.HOL).move_to(Province.KIE).fail()
    phase.orders.extend([fa_bel_hol, ga_hol_kie])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE


async def test_07__handle_remaining_move_orders_06(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_kie = Army(Power.G, Province.HOL).move_to(Province.KIE).fail()
    fa_ruh_supp = Army(Power.F, Province.RUH).support(fa_bel_hol).valid()
    phase.orders.extend([fa_bel_hol, ga_hol_kie, fa_ruh_supp])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.SUCCESS


async def test_07__handle_remaining_move_orders_09(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_hold = Army(Power.G, Province.HOL).hold()
    phase.orders.extend([fa_bel_hol, ga_hol_hold])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.FAILURE


async def test_07__handle_remaining_move_orders_10(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_ruh = Army(Power.G, Province.HOL).move_to(Province.RUH)
    ga_ruh_bel = Army(Power.G, Province.RUH).move_to(Province.BEL)
    phase.orders.extend([fa_bel_hol, ga_hol_ruh, ga_ruh_bel])
    phase._handle_remaining_move_orders(phase.orders, set())
    assert fa_bel_hol.status == Order.Status.UNRESOLVED
    assert ga_hol_ruh.status == Order.Status.UNRESOLVED
    assert ga_ruh_bel.status == Order.Status.UNRESOLVED


"""
未処理の命令を成功判定
"""


async def test_08__succeed_remaining_orders_01(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    """最後まで残った維持命令はすべて成功にする"""
    phase.orders.extend([])
    phase._succeed_remaining_orders(phase.orders)
    assert True


async def test_08__succeed_remaining_orders_02(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    """最後まで残った維持命令はすべて成功にする"""
    aa_bud_hold = Army(Power.A, Province.BUD).hold()
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_vie_hold = Army(Power.A, Province.VIE).hold()
    phase.orders.extend([aa_bud_hold, af_tri_hold, aa_vie_hold])
    phase._succeed_remaining_orders(phase.orders)
    assert all(order.status == Order.Status.SUCCESS for order in phase.orders)


async def test_08__succeed_remaining_orders_03(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    """最後まで残った移動命令はすべて成功にする"""
    fa_bel_hol = Army(Power.F, Province.BEL).move_to(Province.HOL)
    ga_hol_ruh = Army(Power.G, Province.HOL).move_to(Province.RUH)
    ga_ruh_bel = Army(Power.G, Province.RUH).move_to(Province.BEL)
    phase.orders.extend([fa_bel_hol, ga_hol_ruh, ga_ruh_bel])
    phase._succeed_remaining_orders(phase.orders)
    assert all(order.status == Order.Status.SUCCESS for order in phase.orders)
