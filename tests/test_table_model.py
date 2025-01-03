from models.table_model import Table
from models.user_model import User


def test_table_creation(master_data):
    new_user = User(xid=123, sname="abc")
    new_table = Table(master_data)
    new_user.tables.append(new_table)
    master_data.add(new_user)
    master_data.commit()
    user = master_data.query(User).filter_by(xid=123).first()
    table = master_data.query(Table).filter_by(user_id=user.id).first()
    assert table is not None
    assert table.user_id == user.id
    assert user.tables[0].id == table.id
    assert len(table.phases) == 1
