from models.phase_model import Phase, ReadyPhase


def test_ready_phase_creation(master_data):
    new_ready_phase = ReadyPhase(master_data)
    master_data.add(new_ready_phase)
    master_data.commit()
    ready_phase = master_data.query(Phase).first()
    assert ready_phase is not None
    assert ready_phase.year == 0
    assert len(ready_phase.territories) == 42


def test_phase_relation(master_data):
    new_first_phase = ReadyPhase(master_data)
    new_second_phase = new_first_phase.create_next_phase()
    master_data.add(new_second_phase)
    master_data.commit()
    first_phase = master_data.query(Phase).filter_by(prev_phase=None).first()
    second_phase = master_data.query(Phase).filter_by(prev_phase=first_phase).first()
    assert first_phase is not None
    assert first_phase.prev_phase is None
    assert second_phase is not None
    assert second_phase.prev_phase == first_phase
    assert second_phase.year == 1901
    assert len(second_phase.territories) == 0
    assert len(second_phase.latest_territories) == 42


def test_phase_status(master_data):
    new_first_phase = ReadyPhase(master_data)
    master_data.add(new_first_phase)
    master_data.commit()
    first_phase = master_data.query(Phase).filter_by(prev_phase=None).first()
    assert first_phase.status == Phase.Status.OPEN

    new_second_phase = new_first_phase.create_next_phase()
    master_data.add(new_second_phase)
    master_data.commit()
    second_phase = master_data.query(Phase).filter_by(prev_phase=first_phase).first()
    assert first_phase.status == Phase.Status.CLOSED
    assert second_phase.status == Phase.Status.OPEN
