# pyright: reportPrivateUsage=false
"""
https://www.playdiplomacy.com/game_play_details.php?game_id=223930
"""

from sqlalchemy.ext.asyncio import AsyncSession

from models.order_model import Order
from models.phase_model import FallOrderPhase, SpringOrderPhase
from models.power_model import Power
from models.province_model import Province
from models.unit_model import Army, Fleet


async def test_01__resolve_marching_orders_1901_spring(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    phase.year = 1901
    aa_vie_gal = Army(Power.A, Province.VIE).move_to(Province.GAL)
    af_tri_hold = Fleet(Power.A, Province.TRI).hold()
    aa_bud_ser = Army(Power.A, Province.BUD).move_to(Province.SER)
    phase.orders.extend([aa_vie_gal, af_tri_hold, aa_bud_ser])
    ea_lvp_edi = Army(Power.E, Province.LVP).move_to(Province.EDI)
    ef_lon_nth = Fleet(Power.E, Province.LON).move_to(Province.NTH)
    ef_edi_nwg = Fleet(Power.E, Province.EDI).move_to(Province.NWG)
    phase.orders.extend([ea_lvp_edi, ef_lon_nth, ef_edi_nwg])
    ff_bre_mao = Fleet(Power.F, Province.BRE).move_to(Province.MAO)
    fa_par_bur = Army(Power.F, Province.PAR).move_to(Province.BUR)
    fa_mar_supp = Army(Power.F, Province.MAR).support(fa_par_bur)
    phase.orders.extend([ff_bre_mao, fa_par_bur, fa_mar_supp])
    ga_mun_sil = Army(Power.G, Province.MUN).move_to(Province.SIL)
    ga_ber_kie = Army(Power.G, Province.BER).move_to(Province.KIE)
    gf_kie_den = Fleet(Power.G, Province.KIE).move_to(Province.DEN)
    phase.orders.extend([ga_mun_sil, ga_ber_kie, gf_kie_den])
    ia_ven_tyr = Army(Power.I, Province.VEN).move_to(Province.TYR)
    ia_rom_ven = Army(Power.I, Province.ROM).move_to(Province.VEN)
    if_nap_ion = Fleet(Power.I, Province.NAP).move_to(Province.ION)
    phase.orders.extend([ia_ven_tyr, ia_rom_ven, if_nap_ion])
    ra_mos_ukr = Army(Power.R, Province.MOS).move_to(Province.UKR)
    rf_stp_bot = Fleet(Power.R, Province.STP_SC).move_to(Province.BOT)
    ra_war_gal = Army(Power.R, Province.BER).move_to(Province.GAL)
    rf_sev_bla = Fleet(Power.R, Province.SEV).move_to(Province.BLA)
    phase.orders.extend([ra_mos_ukr, rf_stp_bot, ra_war_gal, rf_sev_bla])
    ta_smy_con = Army(Power.T, Province.SMY).move_to(Province.CON)
    tf_ank_bla = Fleet(Power.T, Province.ANK).move_to(Province.BLA)
    ta_con_bul = Army(Power.T, Province.CON).move_to(Province.BUL)
    phase.orders.extend([ta_smy_con, tf_ank_bla, ta_con_bul])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "fall_order"
    assert new_phase.year == 1901
    assert aa_vie_gal.status == Order.Status.FAILURE
    assert af_tri_hold.status == Order.Status.SUCCESS
    assert aa_bud_ser.status == Order.Status.SUCCESS
    assert ea_lvp_edi.status == Order.Status.SUCCESS
    assert ef_lon_nth.status == Order.Status.SUCCESS
    assert ef_edi_nwg.status == Order.Status.SUCCESS
    assert ff_bre_mao.status == Order.Status.SUCCESS
    assert fa_par_bur.status == Order.Status.SUCCESS
    assert fa_mar_supp.status == Order.Status.VALID
    assert ga_mun_sil.status == Order.Status.SUCCESS
    assert ga_ber_kie.status == Order.Status.SUCCESS
    assert gf_kie_den.status == Order.Status.SUCCESS
    assert ia_ven_tyr.status == Order.Status.SUCCESS
    assert ia_rom_ven.status == Order.Status.SUCCESS
    assert if_nap_ion.status == Order.Status.SUCCESS
    assert ra_mos_ukr.status == Order.Status.SUCCESS
    assert rf_stp_bot.status == Order.Status.SUCCESS
    assert ra_war_gal.status == Order.Status.FAILURE
    assert rf_sev_bla.status == Order.Status.FAILURE
    assert ta_smy_con.status == Order.Status.SUCCESS
    assert tf_ank_bla.status == Order.Status.FAILURE
    assert ta_con_bul.status == Order.Status.SUCCESS


async def test_02__resolve_marching_orders_1901_fall(master_data: AsyncSession) -> None:
    phase = FallOrderPhase()
    phase.year = 1901
    aa_vie_tyr = Army(Power.A, Province.VIE).move_to(Province.TYR)
    af_tri_ven = Fleet(Power.A, Province.TRI).move_to(Province.VEN)
    aa_ser_hold = Army(Power.A, Province.SER).hold()
    phase.orders.extend([aa_vie_tyr, af_tri_ven, aa_ser_hold])
    ea_edi_nwy = Army(Power.E, Province.EDI).move_to(Province.NWY)
    ef_nth_bel = Fleet(Power.E, Province.NTH).move_to(Province.BEL)
    ef_nwg_conv = Fleet(Power.E, Province.NWG).convoy(ea_edi_nwy)
    phase.orders.extend([ea_edi_nwy, ef_nth_bel, ef_nwg_conv])
    ff_mao_por = Fleet(Power.F, Province.MAO).move_to(Province.POR)
    fa_bur_bel = Army(Power.F, Province.BUR).move_to(Province.BEL)
    fa_mar_spa = Army(Power.F, Province.MAR).move_to(Province.SPA)
    phase.orders.extend([ff_mao_por, fa_bur_bel, fa_mar_spa])
    ga_sil_mun = Army(Power.G, Province.SIL).move_to(Province.MUN)
    ga_kie_hol = Army(Power.G, Province.KIE).move_to(Province.HOL)
    gf_den_swe = Fleet(Power.G, Province.DEN).move_to(Province.SWE)
    phase.orders.extend([ga_sil_mun, ga_kie_hol, gf_den_swe])
    ia_tyr_mun = Army(Power.I, Province.TYR).move_to(Province.MUN)
    ia_ven_tri = Army(Power.I, Province.VEN).move_to(Province.TRI)
    if_ion_gre = Fleet(Power.I, Province.ION).move_to(Province.GRE)
    phase.orders.extend([ia_tyr_mun, ia_ven_tri, if_ion_gre])
    ra_ukr_rum = Army(Power.R, Province.UKR).move_to(Province.RUM)
    rf_bot_swe = Fleet(Power.R, Province.BOT).move_to(Province.SWE)
    ra_war_hold = Army(Power.R, Province.WAR).hold()
    rf_sev_supp = Fleet(Power.R, Province.SEV).support(ra_ukr_rum)
    phase.orders.extend([ra_ukr_rum, rf_bot_swe, ra_war_hold, rf_sev_supp])
    ta_con_bul = Army(Power.T, Province.CON).move_to(Province.BUL)
    tf_ank_bla = Fleet(Power.T, Province.ANK).move_to(Province.BLA)
    ta_bul_gre = Army(Power.T, Province.BUL).move_to(Province.GRE)
    phase.orders.extend([ta_con_bul, tf_ank_bla, ta_bul_gre])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "adjustment"
    assert new_phase.year == 1901
    assert aa_vie_tyr.status == Order.Status.FAILURE
    assert af_tri_ven.status == Order.Status.FAILURE
    assert aa_ser_hold.status == Order.Status.SUCCESS
    assert ea_edi_nwy.status == Order.Status.SUCCESS
    assert ef_nth_bel.status == Order.Status.FAILURE
    assert ef_nwg_conv.status == Order.Status.VALID
    assert ff_mao_por.status == Order.Status.SUCCESS
    assert fa_bur_bel.status == Order.Status.FAILURE
    assert fa_mar_spa.status == Order.Status.SUCCESS
    assert ga_sil_mun.status == Order.Status.FAILURE
    assert ga_kie_hol.status == Order.Status.SUCCESS
    assert gf_den_swe.status == Order.Status.FAILURE
    assert ia_tyr_mun.status == Order.Status.FAILURE
    assert ia_ven_tri.status == Order.Status.FAILURE
    assert if_ion_gre.status == Order.Status.FAILURE
    assert ra_ukr_rum.status == Order.Status.SUCCESS
    assert rf_bot_swe.status == Order.Status.FAILURE
    assert ra_war_hold.status == Order.Status.SUCCESS
    assert rf_sev_supp.status == Order.Status.VALID
    assert ta_con_bul.status == Order.Status.FAILURE
    assert tf_ank_bla.status == Order.Status.SUCCESS
    assert ta_bul_gre.status == Order.Status.FAILURE


async def test_03__resolve_marching_orders_1902_spring(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    phase.year = 1902
    af_tri_ven = Fleet(Power.A, Province.TRI).move_to(Province.VEN)
    aa_ser_rum = Army(Power.A, Province.SER).move_to(Province.RUM)
    aa_vie_tyr = Army(Power.A, Province.VIE).move_to(Province.TYR)
    aa_bud_supp = Army(Power.A, Province.BUD).support(aa_ser_rum)
    phase.orders.extend([af_tri_ven, aa_ser_rum, aa_vie_tyr, aa_bud_supp])
    ea_nwy_swe = Army(Power.E, Province.NWY).move_to(Province.SWE)
    ef_lon_eng = Fleet(Power.E, Province.LON).move_to(Province.ENG)
    ef_nwg_bar = Fleet(Power.E, Province.NWG).move_to(Province.BAR)
    ga_hol_bel_asm = Army(Power.G, Province.HOL).move_to(Province.BEL).assumed_by(Power.E)
    ef_nth_supp = Fleet(Power.E, Province.NTH).support(ga_hol_bel_asm)
    phase.orders.extend([ea_nwy_swe, ef_lon_eng, ef_nwg_bar, ga_hol_bel_asm, ef_nth_supp])
    fa_bur_bel = Army(Power.F, Province.BUR).move_to(Province.BEL)
    fa_spa_mar = Army(Power.F, Province.SPA).move_to(Province.MAR)
    fa_mar_lyo = Fleet(Power.F, Province.MAR).move_to(Province.LYO)
    ff_por_mao = Fleet(Power.F, Province.POR).move_to(Province.MAO)
    fa_par_pic = Army(Power.F, Province.PAR).move_to(Province.PIC)
    phase.orders.extend([fa_bur_bel, fa_spa_mar, fa_mar_lyo, ff_por_mao, fa_par_pic])
    ea_nwy_swe_asm = Army(Power.E, Province.NWY).move_to(Province.SWE).assumed_by(Power.G)
    gf_den_supp = Fleet(Power.G, Province.DEN).support(ea_nwy_swe_asm)
    ga_hol_bel = Army(Power.G, Province.HOL).move_to(Province.BEL)
    ga_sil_war = Army(Power.G, Province.SIL).move_to(Province.WAR)
    aa_vie_tyr_asm = Army(Power.A, Province.VIE).move_to(Province.TYR).assumed_by(Power.G)
    ga_mun_supp = Army(Power.G, Province.MUN).support(aa_vie_tyr_asm)
    ga_bel_pru = Army(Power.G, Province.BER).move_to(Province.PRU)
    phase.orders.extend([ea_nwy_swe_asm, gf_den_supp, ga_hol_bel, ga_sil_war, aa_vie_tyr_asm, ga_mun_supp, ga_bel_pru])
    ia_tyr_vie = Army(Power.I, Province.TYR).move_to(Province.VIE)
    ia_ven_tri = Army(Power.I, Province.VEN).move_to(Province.TRI)
    if_ion_gre = Fleet(Power.I, Province.ION).move_to(Province.GRE)
    phase.orders.extend([ia_tyr_vie, ia_ven_tri, if_ion_gre])
    ra_war_gal = Army(Power.R, Province.WAR).move_to(Province.GAL)
    ra_rum_supp = Army(Power.R, Province.RUM).support(ra_war_gal)
    rf_sev_supp = Fleet(Power.R, Province.SEV).support(ra_rum_supp)
    rf_bot_swe = Fleet(Power.R, Province.BOT).move_to(Province.SWE)
    ra_mos_war = Army(Power.R, Province.MOS).move_to(Province.WAR)
    phase.orders.extend([ra_war_gal, ra_rum_supp, rf_sev_supp, rf_bot_swe, ra_mos_war])
    tf_smy_aeg = Fleet(Power.T, Province.SMY).move_to(Province.AEG)
    ta_con_bul = Army(Power.T, Province.CON).move_to(Province.BUL)
    ta_bul_gre = Army(Power.T, Province.BUL).move_to(Province.GRE)
    tf_bla_rum = Fleet(Power.T, Province.BLA).move_to(Province.RUM)
    phase.orders.extend([tf_smy_aeg, ta_con_bul, ta_bul_gre, tf_bla_rum])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "spring_retreat"
    assert new_phase.year == 1902
    assert af_tri_ven.status == Order.Status.FAILURE
    assert aa_bud_supp.status == Order.Status.VALID
    assert aa_ser_rum.status == Order.Status.FAILURE
    assert aa_vie_tyr.status == Order.Status.SUCCESS
    assert ea_nwy_swe.status == Order.Status.SUCCESS
    assert ef_lon_eng.status == Order.Status.SUCCESS
    assert ef_nwg_bar.status == Order.Status.SUCCESS
    assert ga_hol_bel_asm.status == Order.Status.UNRESOLVED
    assert ef_nth_supp.status == Order.Status.VALID
    assert fa_bur_bel.status == Order.Status.FAILURE
    assert fa_spa_mar.status == Order.Status.SUCCESS
    assert fa_mar_lyo.status == Order.Status.SUCCESS
    assert ff_por_mao.status == Order.Status.SUCCESS
    assert fa_par_pic.status == Order.Status.SUCCESS
    assert ea_nwy_swe_asm.status == Order.Status.UNRESOLVED
    assert gf_den_supp.status == Order.Status.VALID
    assert ga_hol_bel.status == Order.Status.SUCCESS
    assert ga_sil_war.status == Order.Status.FAILURE
    assert aa_vie_tyr_asm.status == Order.Status.UNRESOLVED
    assert ga_mun_supp.status == Order.Status.VALID
    assert ga_bel_pru.status == Order.Status.SUCCESS
    assert ia_tyr_vie.status == Order.Status.DISLODGED
    assert ia_ven_tri.status == Order.Status.FAILURE
    assert if_ion_gre.status == Order.Status.FAILURE
    assert ra_war_gal.status == Order.Status.SUCCESS
    assert ra_rum_supp.status == Order.Status.CUT
    assert rf_sev_supp.status == Order.Status.VALID
    assert rf_bot_swe.status == Order.Status.FAILURE
    assert ra_mos_war.status == Order.Status.FAILURE
    assert tf_smy_aeg.status == Order.Status.SUCCESS
    assert ta_con_bul.status == Order.Status.FAILURE
    assert ta_bul_gre.status == Order.Status.FAILURE
    assert tf_bla_rum.status == Order.Status.FAILURE


async def test_04__resolve_marching_orders_1902_fall(master_data: AsyncSession) -> None:
    phase = FallOrderPhase()
    phase.year = 1902
    aa_tyr_ven = Army(Power.A, Province.TYR).move_to(Province.VEN)
    af_tri_supp = Fleet(Power.A, Province.TRI).support(aa_tyr_ven)
    aa_bud_supp = Army(Power.A, Province.BUD).support(Army(Power.A, Province.SER).hold())
    aa_ser_supp = Army(Power.A, Province.SER).support(aa_bud_supp)
    phase.orders.extend([aa_tyr_ven, af_tri_supp, aa_bud_supp, aa_ser_supp])
    ea_swe_hold = Army(Power.E, Province.SWE).hold()
    ef_eng_bre = Fleet(Power.E, Province.ENG).move_to(Province.BRE)
    ef_bar_stpnc = Fleet(Power.E, Province.BAR).move_to(Province.STP_NC)
    ef_nth_eng = Fleet(Power.E, Province.NTH).move_to(Province.ENG)
    phase.orders.extend([ea_swe_hold, ef_eng_bre, ef_bar_stpnc, ef_nth_eng])
    fa_bur_bel = Army(Power.F, Province.BUR).move_to(Province.BEL)
    fa_mar_pie = Army(Power.F, Province.MAR).move_to(Province.PIE)
    ff_lyo_wes = Fleet(Power.F, Province.LYO).move_to(Province.WES)
    ff_mao_bre = Fleet(Power.F, Province.MAO).move_to(Province.BRE)
    fa_pic_supp = Army(Power.F, Province.PIC).support(fa_bur_bel)
    phase.orders.extend([fa_bur_bel, fa_mar_pie, ff_lyo_wes, ff_mao_bre, fa_pic_supp])
    gf_den_bal = Fleet(Power.G, Province.DEN).move_to(Province.BAL)
    ga_mun_bur = Army(Power.G, Province.MUN).move_to(Province.BUR)
    ga_bel_supp = Army(Power.G, Province.BEL).support(ga_mun_bur)
    ga_sil_gal = Army(Power.G, Province.SIL).move_to(Province.GAL)
    ga_pru_war = Army(Power.G, Province.PRU).move_to(Province.WAR)
    phase.orders.extend([gf_den_bal, ga_mun_bur, ga_bel_supp, ga_sil_gal, ga_pru_war])
    ia_boh_vie = Army(Power.I, Province.BOH).move_to(Province.VIE)
    ia_ven_tyr = Army(Power.I, Province.VEN).move_to(Province.TYR)
    if_ion_tun = Fleet(Power.I, Province.ION).move_to(Province.TUN)
    phase.orders.extend([ia_boh_vie, ia_ven_tyr, if_ion_tun])
    rf_sev_rum = Fleet(Power.R, Province.SEV).move_to(Province.RUM)
    rf_bot_sptsc = Fleet(Power.R, Province.BOT).move_to(Province.STP_SC)
    ra_mos_war = Army(Power.R, Province.MOS).move_to(Province.WAR)
    ra_rum_bud = Army(Power.R, Province.RUM).move_to(Province.BUD)
    ra_gal_supp = Army(Power.R, Province.GAL).support(ra_rum_bud)
    phase.orders.extend([rf_sev_rum, rf_bot_sptsc, ra_mos_war, ra_rum_bud, ra_gal_supp])
    ta_bul_gre = Army(Power.T, Province.BUL).move_to(Province.GRE)
    tf_aeg_supp = Fleet(Power.T, Province.ION).support(ta_bul_gre)
    ta_con_bul = Army(Power.T, Province.CON).move_to(Province.BUL)
    tf_bla_rum = Fleet(Power.T, Province.BLA).move_to(Province.RUM)
    phase.orders.extend([ta_bul_gre, tf_aeg_supp, ta_con_bul, tf_bla_rum])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "fall_retreat"
    assert new_phase.year == 1902
    assert aa_tyr_ven.status == Order.Status.SUCCESS
    assert af_tri_supp.status == Order.Status.VALID
    assert aa_bud_supp.status == Order.Status.CUT
    assert aa_ser_supp.status == Order.Status.VALID
    assert ea_swe_hold.status == Order.Status.SUCCESS
    assert ef_eng_bre.status == Order.Status.FAILURE
    assert ef_bar_stpnc.status == Order.Status.FAILURE
    assert ef_nth_eng.status == Order.Status.FAILURE
    assert fa_bur_bel.status == Order.Status.SUCCESS
    assert fa_mar_pie.status == Order.Status.SUCCESS
    assert ff_lyo_wes.status == Order.Status.SUCCESS
    assert ff_mao_bre.status == Order.Status.FAILURE
    assert fa_pic_supp.status == Order.Status.VALID
    assert gf_den_bal.status == Order.Status.SUCCESS
    assert ga_mun_bur.status == Order.Status.SUCCESS
    assert ga_bel_supp.status == Order.Status.DISLODGED
    assert ga_sil_gal.status == Order.Status.FAILURE
    assert ga_pru_war.status == Order.Status.FAILURE
    assert ia_boh_vie.status == Order.Status.SUCCESS
    assert ia_ven_tyr.status == Order.Status.DISLODGED
    assert if_ion_tun.status == Order.Status.SUCCESS
    assert rf_sev_rum.status == Order.Status.FAILURE
    assert rf_bot_sptsc.status == Order.Status.FAILURE
    assert ra_mos_war.status == Order.Status.FAILURE
    assert ra_rum_bud.status == Order.Status.FAILURE
    assert ra_gal_supp.status == Order.Status.CUT
    assert ta_bul_gre.status == Order.Status.SUCCESS
    assert tf_aeg_supp.status == Order.Status.VALID
    assert ta_con_bul.status == Order.Status.SUCCESS
    assert tf_bla_rum.status == Order.Status.FAILURE


async def test_05__resolve_marching_orders_1903_spring(master_data: AsyncSession) -> None:
    phase = SpringOrderPhase()
    phase.year = 1903
    aa_ser_tri = Army(Power.A, Province.SER).move_to(Province.TRI)
    af_tri_adr = Fleet(Power.A, Province.TRI).move_to(Province.ADR)
    aa_bud_gal = Army(Power.A, Province.BUD).move_to(Province.GAL)
    aa_ven_pie = Army(Power.A, Province.VEN).move_to(Province.PIE)
    phase.orders.extend([aa_ser_tri, af_tri_adr, aa_bud_gal, aa_ven_pie])
    ea_swe_nwy = Army(Power.E, Province.SWE).move_to(Province.NWY)
    ef_lvp_iri = Fleet(Power.E, Province.LVP).move_to(Province.IRI)
    ef_eng_supp = Fleet(Power.E, Province.ENG).support(ef_lvp_iri)
    ef_nth_supp = Fleet(Power.E, Province.NTH).support(ef_eng_supp)
    ef_bar_stpnc = Fleet(Power.E, Province.BAR).move_to(Province.STP_NC)
    phase.orders.extend([ea_swe_nwy, ef_lvp_iri, ef_eng_supp, ef_nth_supp, ef_bar_stpnc])
    fa_bel_hold = Army(Power.F, Province.BEL).hold()
    fa_pie_mar = Army(Power.F, Province.PIE).move_to(Province.MAR)
    fa_pic_par = Army(Power.F, Province.PIC).move_to(Province.PAR)
    ff_wes_tys = Fleet(Power.F, Province.WES).move_to(Province.TYS)
    ff_mao_supp = Fleet(Power.F, Province.MAO).support(Fleet(Power.F, Province.BRE).hold())
    ff_bre_supp = Fleet(Power.F, Province.BRE).support(ff_mao_supp)
    phase.orders.extend([fa_bel_hold, fa_pie_mar, fa_pic_par, ff_wes_tys, ff_mao_supp, ff_bre_supp])
    ga_hol_hold = Army(Power.G, Province.HOL).hold()
    ga_pru_war = Army(Power.G, Province.PRU).move_to(Province.WAR)
    ga_bur_gas = Army(Power.G, Province.BUR).move_to(Province.GAS)
    gf_bal_swe = Fleet(Power.G, Province.BAL).move_to(Province.SWE)
    ga_sil_supp = Army(Power.G, Province.SIL).support(ga_pru_war)
    phase.orders.extend([ga_hol_hold, ga_pru_war, ga_bur_gas, gf_bal_swe, ga_sil_supp])
    ia_vie_hold = Army(Power.I, Province.VIE).hold()
    ia_rom_hold = Army(Power.I, Province.ROM).hold()
    if_tun_hold = Fleet(Power.I, Province.TUN).hold()
    ia_nap_hold = Army(Power.I, Province.NAP).hold()
    phase.orders.extend([ia_vie_hold, ia_rom_hold, if_tun_hold, ia_nap_hold])
    rf_sev_hold = Fleet(Power.R, Province.SEV).hold()
    rf_bot_hold = Fleet(Power.R, Province.BOT).hold()
    ra_mos_hold = Army(Power.R, Province.MOS).hold()
    ra_rum_hold = Army(Power.R, Province.RUM).hold()
    ra_gal_hold = Army(Power.R, Province.GAL).hold()
    phase.orders.extend([rf_sev_hold, rf_bot_hold, ra_mos_hold, ra_rum_hold, ra_gal_hold])
    tf_aeg_ion = Fleet(Power.T, Province.AEG).move_to(Province.ION)
    tf_smy_eas = Fleet(Power.T, Province.SMY).move_to(Province.EAS)
    ta_gre_ser = Army(Power.T, Province.GRE).move_to(Province.SER)
    ta_bul_supp = Army(Power.T, Province.BUL).support(ta_gre_ser)
    tf_bla_supp = Fleet(Power.T, Province.BLA).support(ta_bul_supp)
    phase.orders.extend([tf_aeg_ion, tf_smy_eas, ta_gre_ser, ta_bul_supp, tf_bla_supp])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "fall_order"
    assert new_phase.year == 1903
    assert aa_ser_tri.status == Order.Status.SUCCESS
    assert af_tri_adr.status == Order.Status.SUCCESS
    assert aa_bud_gal.status == Order.Status.FAILURE
    assert aa_ven_pie.status == Order.Status.SUCCESS
    assert ea_swe_nwy.status == Order.Status.SUCCESS
    assert ef_lvp_iri.status == Order.Status.SUCCESS
    assert ef_eng_supp.status == Order.Status.VALID
    assert ef_nth_supp.status == Order.Status.VALID
    assert ef_bar_stpnc.status == Order.Status.SUCCESS
    assert fa_bel_hold.status == Order.Status.SUCCESS
    assert fa_pie_mar.status == Order.Status.SUCCESS
    assert fa_pic_par.status == Order.Status.SUCCESS
    assert ff_wes_tys.status == Order.Status.SUCCESS
    assert ff_mao_supp.status == Order.Status.VALID
    assert ff_bre_supp.status == Order.Status.VALID
    assert ga_hol_hold.status == Order.Status.SUCCESS
    assert ga_pru_war.status == Order.Status.SUCCESS
    assert ga_bur_gas.status == Order.Status.SUCCESS
    assert gf_bal_swe.status == Order.Status.SUCCESS
    assert ga_sil_supp.status == Order.Status.VALID
    assert ia_vie_hold.status == Order.Status.SUCCESS
    assert ia_rom_hold.status == Order.Status.SUCCESS
    assert if_tun_hold.status == Order.Status.SUCCESS
    assert ia_nap_hold.status == Order.Status.SUCCESS
    assert rf_sev_hold.status == Order.Status.SUCCESS
    assert rf_bot_hold.status == Order.Status.SUCCESS
    assert ra_mos_hold.status == Order.Status.SUCCESS
    assert ra_rum_hold.status == Order.Status.SUCCESS
    assert ra_gal_hold.status == Order.Status.SUCCESS
    assert tf_aeg_ion.status == Order.Status.SUCCESS
    assert tf_smy_eas.status == Order.Status.SUCCESS
    assert ta_gre_ser.status == Order.Status.SUCCESS
    assert ta_bul_supp.status == Order.Status.VALID
    assert tf_bla_supp.status == Order.Status.VALID


async def test_06__resolve_marching_orders_1903_fall(master_data: AsyncSession) -> None:
    phase = FallOrderPhase()
    phase.year = 1903
    af_adr_ven = Fleet(Power.A, Province.ADR).move_to(Province.VEN)
    aa_bud_vie = Army(Power.A, Province.BUD).move_to(Province.VIE)
    aa_tri_supp = Army(Power.A, Province.TRI).support(aa_bud_vie)
    ga_gas_mar_asm = Army(Power.G, Province.GAS).move_to(Province.MAR).assumed_by(Power.A)
    aa_pie_supp = Army(Power.A, Province.PIE).support(ga_gas_mar_asm)
    phase.orders.extend([af_adr_ven, aa_bud_vie, aa_tri_supp, ga_gas_mar_asm, aa_pie_supp])
    ef_stpnc_hold = Fleet(Power.E, Province.STP_NC).hold()
    ef_iri_mao = Fleet(Power.E, Province.IRI).move_to(Province.MAO)
    ef_nth_bel = Fleet(Power.E, Province.NTH).move_to(Province.BEL)
    ef_eng_supp = Fleet(Power.E, Province.ENG).support(ef_iri_mao)
    ea_nwy_supp = Army(Power.E, Province.NWY).support(ef_stpnc_hold)
    phase.orders.extend([ef_stpnc_hold, ef_iri_mao, ef_nth_bel, ef_eng_supp, ea_nwy_supp])
    fa_bel_hold = Army(Power.F, Province.BEL).hold()
    ff_tys_hold = Fleet(Power.F, Province.TYS).hold()
    ff_mao_spanc = Fleet(Power.F, Province.MAO).move_to(Province.SPA_NC)
    fa_par_gas = Army(Power.F, Province.PAR).move_to(Province.GAS)
    fa_mar_supp = Army(Power.F, Province.MAR).support(fa_par_gas)
    ff_bre_supp = Fleet(Power.F, Province.BRE).support(fa_par_gas)
    phase.orders.extend([fa_bel_hold, ff_tys_hold, ff_mao_spanc, fa_par_gas, fa_mar_supp, ff_bre_supp])
    gf_swe_hold = Fleet(Power.G, Province.SWE).hold()
    ga_war_mos = Army(Power.G, Province.WAR).move_to(Province.MOS)
    ga_gas_mar = Army(Power.G, Province.GAS).move_to(Province.MAR)
    ga_sil_gal = Army(Power.G, Province.SIL).move_to(Province.GAL)
    ef_nth_bel_asm = Fleet(Power.E, Province.NTH).move_to(Province.BEL).assumed_by(Power.G)
    ga_hol_supp = Army(Power.G, Province.HOL).support(ef_nth_bel_asm)
    phase.orders.extend([gf_swe_hold, ga_war_mos, ga_gas_mar, ga_sil_gal, ef_nth_bel_asm, ga_hol_supp])
    ia_nap_hold = Army(Power.I, Province.NAP).hold()
    if_tun_hold = Fleet(Power.I, Province.TUN).hold()
    ia_rom_ven = Army(Power.I, Province.ROM).move_to(Province.VEN)
    ra_gal_sev_asm = Army(Power.R, Province.GAL).move_to(Province.SEV).assumed_by(Power.I)
    ia_vie_supp = Army(Power.I, Province.VIE).support(ra_gal_sev_asm)
    phase.orders.extend([ia_nap_hold, if_tun_hold, ia_rom_ven, ra_gal_sev_asm, ia_vie_supp])
    rf_sev_hold = Fleet(Power.R, Province.SEV).hold()
    ra_mos_hold = Army(Power.R, Province.MOS).hold()
    ra_rum_hold = Army(Power.R, Province.RUM).hold()
    ra_gal_bud = Army(Power.R, Province.GAL).move_to(Province.BUD)
    rf_bot_bal = Fleet(Power.R, Province.BOT).move_to(Province.BAL)
    phase.orders.extend([rf_sev_hold, ra_mos_hold, ra_rum_hold, ra_gal_bud, rf_bot_bal])
    tf_ion_hold = Fleet(Power.T, Province.ION).hold()
    tf_eas_supp = Fleet(Power.T, Province.EAS).support(tf_ion_hold)
    ta_ser_supp = Army(Power.T, Province.SER).support(Army(Power.T, Province.BUL).hold())
    tf_bla_supp = Fleet(Power.T, Province.BLA).support(Army(Power.T, Province.BUL).hold())
    ta_bul_supp = Army(Power.T, Province.BUL).support(ta_ser_supp)
    phase.orders.extend([tf_ion_hold, tf_eas_supp, ta_ser_supp, tf_bla_supp, ta_bul_supp])

    new_phase = phase.end()
    assert new_phase is not None
    assert new_phase.type == "fall_retreat"
    assert new_phase.year == 1903
    assert af_adr_ven.status == Order.Status.FAILURE
    assert aa_bud_vie.status == Order.Status.SUCCESS
    assert aa_tri_supp.status == Order.Status.VALID
    assert ga_gas_mar_asm.status == Order.Status.UNRESOLVED
    assert aa_pie_supp.status == Order.Status.VALID
    assert ef_stpnc_hold.status == Order.Status.SUCCESS
    assert ef_iri_mao.status == Order.Status.SUCCESS
    assert ef_nth_bel.status == Order.Status.SUCCESS
    assert ef_eng_supp.status == Order.Status.VALID
    assert ea_nwy_supp.status == Order.Status.VALID
    assert fa_bel_hold.status == Order.Status.DISLODGED
    assert ff_tys_hold.status == Order.Status.SUCCESS
    assert ff_mao_spanc.status == Order.Status.SUCCESS
    assert fa_par_gas.status == Order.Status.SUCCESS
    assert fa_mar_supp.status == Order.Status.DISLODGED
    assert ff_bre_supp.status == Order.Status.VALID
    assert gf_swe_hold.status == Order.Status.SUCCESS
    assert ga_war_mos.status == Order.Status.FAILURE
    assert ga_gas_mar.status == Order.Status.SUCCESS
    assert ga_sil_gal.status == Order.Status.SUCCESS
    assert ef_nth_bel_asm.status == Order.Status.UNRESOLVED
    assert ga_hol_supp.status == Order.Status.VALID
    assert ia_nap_hold.status == Order.Status.SUCCESS
    assert if_tun_hold.status == Order.Status.SUCCESS
    assert ia_rom_ven.status == Order.Status.FAILURE
    assert ra_gal_sev_asm.status == Order.Status.UNRESOLVED
    assert ia_vie_supp.status == Order.Status.DISLODGED
    assert rf_sev_hold.status == Order.Status.SUCCESS
    assert ra_mos_hold.status == Order.Status.SUCCESS
    assert ra_rum_hold.status == Order.Status.SUCCESS
    assert ra_gal_bud.status == Order.Status.SUCCESS
    assert rf_bot_bal.status == Order.Status.SUCCESS
    assert tf_ion_hold.status == Order.Status.SUCCESS
    assert tf_eas_supp.status == Order.Status.VALID
    assert ta_ser_supp.status == Order.Status.VALID
    assert tf_bla_supp.status == Order.Status.VALID
    assert ta_bul_supp.status == Order.Status.VALID
