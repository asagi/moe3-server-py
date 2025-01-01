from models.phase_model import Phase


def test_ready_phase_creation(master_data):
    new_ready_phase = Phase.create_ready_phase(master_data)
    master_data.add(new_ready_phase)
    master_data.commit()
    ready_phase = master_data.query(Phase).first()
    assert ready_phase is not None
    assert len(ready_phase.territories) == 81


def test_phase_relation(master_data):
    new_first_phase = Phase.create_ready_phase(master_data)
    new_second_phase = Phase(prev_phase=new_first_phase)
    master_data.add(new_second_phase)
    master_data.commit()
    first_phase = master_data.query(Phase).filter_by(prev_phase=None).first()
    second_phase = master_data.query(Phase).filter_by(prev_phase=first_phase).first()
    assert first_phase is not None
    assert first_phase.prev_phase is None
    assert second_phase is not None
    assert second_phase.prev_phase == first_phase
    assert len(second_phase.territories) == 0
    assert len(second_phase.latest_territories) == 81
