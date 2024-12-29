from src.models.table_model import Table
from src.models.user_model import User


def test_table_creation(db_session):
    new_user = User(userid=123, sname="abc")
    new_table = Table()
    new_user.tables.append(new_table)
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(userid=123).first()
    table = db_session.query(Table).filter_by(user_id=user.id).first()
    assert table is not None
    assert table.user_id == user.id
    assert user.tables[0].id == table.id
