from src.models.unit_model import Unit, Army, Fleet


def test_army_creation(db_session):
    new_unit = Army(province="lon")
    db_session.add(new_unit)
    db_session.commit()
    unit = db_session.query(Unit).filter_by(province="lon").first()
    assert unit is not None
    assert unit.type == "army"
    assert unit.symbol == "a"


def test_fleet_creation(db_session):
    new_unit = Fleet(province="lon")
    db_session.add(new_unit)
    db_session.commit()
    unit = db_session.query(Unit).filter_by(province="lon").first()
    assert unit is not None
    assert unit.type == "fleet"
    assert unit.symbol == "f"
