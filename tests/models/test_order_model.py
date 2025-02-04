from sqlalchemy.ext.asyncio import AsyncSession

from models.power_model import Power
from models.province_model import Province
from models.unit_model import Army, Fleet


async def test_hold_order_to_string_01(master_data: AsyncSession) -> None:
    order = Army(Power.A, Province.VIE).hold()
    assert str(order) == "a vie-Holds"
    assert order.is_assumed() is False


async def test_hold_order_to_string_02(master_data: AsyncSession) -> None:
    order = Army(Power.A, Province.VIE).hold()
    assert str(order) == "a vie-Holds"
    assert order.is_assumed() is False


async def test_hold_order_to_string_03(master_data: AsyncSession) -> None:
    order = Army(Power.A, Province.VIE).hold().assumed_by(Power.E)
    assert str(order) == "Austrian a vie-Holds"
    assert order.is_assumed() is True


async def test_move_order_to_string_01(master_data: AsyncSession) -> None:
    order = Army(Power.A, Province.VIE).move_to(Province.BUD)
    assert str(order) == "a vie-bud"
    assert order.is_assumed() is False


async def test_support_order_to_string_01(master_data: AsyncSession) -> None:
    aa_vie_holds = Army(Power.A, Province.VIE).hold()
    aa_bud_supp = Army(Power.A, Province.BUD).support(aa_vie_holds)
    assert str(aa_bud_supp) == "a bud S a vie"


async def test_support_order_to_string_02(master_data: AsyncSession) -> None:
    aa_vie_tri = Army(Power.A, Province.VIE).move_to(Province.TRI)
    aa_bud_supp = Army(Power.A, Province.BUD).support(aa_vie_tri)
    assert str(aa_bud_supp) == "a bud S a vie-tri"


async def test_support_order_to_string_03(master_data: AsyncSession) -> None:
    ga_gal_holds = Army(Power.G, Province.GAL).hold()
    aa_mun_supp = Army(Power.A, Province.MUN).support(ga_gal_holds)
    assert str(aa_mun_supp) == "a mun S German a gal"


async def test_convoy_order_to_string_01(master_data: AsyncSession) -> None:
    ea_lon_par = Army(Power.E, Province.LON).move_to(Province.PAR)
    ef_eng_conv = Fleet(Power.E, Province.ENG).convoy(ea_lon_par)
    assert str(ef_eng_conv) == "f eng C a lon-par"


async def test_convoy_order_to_string_02(master_data: AsyncSession) -> None:
    ea_lon_par = Army(Power.E, Province.LON).move_to(Province.PAR)
    ef_eng_conv_assumed = Fleet(Power.E, Province.ENG).convoy(ea_lon_par).assumed_by(Power.F)
    assert str(ef_eng_conv_assumed) == "English f eng C English a lon-par"
