from models.table_model import Table
from models.user_model import User


def test_table_creation(db_session):
    new_user = User(xid=123, sname="abc")
    new_table = Table(db_session)
    new_user.tables.append(new_table)
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(xid=123).first()
    table = db_session.query(Table).filter_by(user_id=user.id).first()
    assert table is not None
    assert table.user_id == user.id
    assert user.tables[0].id == table.id
    assert len(table.phases) == 1
