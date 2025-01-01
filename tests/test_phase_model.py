from models.phase_model import Phase


def test_phase_creation(db_session):
    new_first_phase = Phase.create_ready_phase()
    new_second_phase = Phase(prev_phase=new_first_phase)
    db_session.add(new_second_phase)
    db_session.commit()
    first_phase = db_session.query(Phase).filter_by(prev_phase=None).first()
    second_phase = db_session.query(Phase).filter_by(prev_phase=first_phase).first()
    assert first_phase is not None
    assert second_phase is not None
    assert second_phase.prev_phase == first_phase
