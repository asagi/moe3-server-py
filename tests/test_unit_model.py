from models.power_model import Power
from models.province_model import Province
from models.unit_model import Unit, Army, Fleet


def test_army_creation(master_data):
    power = master_data.query(Power).filter_by(symbol="a").first()
    province = master_data.query(Province).filter_by(abbr="lon").first()
    new_unit = Army(province=province, power=power)
    master_data.add(new_unit)
    master_data.commit()
    unit = master_data.get(Unit, new_unit.id)
    assert unit is not None
    assert unit.type == "army"
    assert unit.symbol == "a"
    assert unit.power.name == "Austria"


def test_fleet_creation(master_data):
    power = master_data.query(Power).filter_by(symbol="g").first()
    province = master_data.query(Province).filter_by(abbr="lon").first()
    new_unit = Fleet(province=province, power=power)
    master_data.add(new_unit)
    master_data.commit()
    unit = master_data.get(Unit, new_unit.id)
    assert unit is not None
    assert unit.type == "fleet"
    assert unit.symbol == "f"
    assert unit.power.name == "Germany"
