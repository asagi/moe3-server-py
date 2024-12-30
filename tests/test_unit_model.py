from models.power_model import Power
from models.province_model import Coast
from models.unit_model import Unit, Army, Fleet


def test_army_creation(master_data):
    power = master_data.query(Power).filter_by(symbol="a").first()
    province = Coast(abbr="lon")
    new_unit = Army(province=province, power=power)
    master_data.add(new_unit)
    master_data.commit()
    unit = master_data.query(Unit).filter_by(province=province).first()
    assert unit is not None
    assert unit.type == "army"
    assert unit.symbol == "a"
    assert unit.power.name == "Austria"


def test_fleet_creation(master_data):
    power = master_data.query(Power).filter_by(symbol="g").first()
    province = Coast(abbr="lon")
    new_unit = Fleet(province=province, power=power)
    master_data.add(new_unit)
    master_data.commit()
    unit = master_data.query(Unit).filter_by(province=province).first()
    assert unit is not None
    assert unit.type == "fleet"
    assert unit.symbol == "f"
    assert unit.power.name == "Germany"
