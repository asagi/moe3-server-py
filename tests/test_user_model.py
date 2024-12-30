from models.user_model import User


def test_user_creation(db_session):
    new_user = User(xid=123, sname="abc")
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(xid=123).first()
    assert user is not None
    assert user.xid == 123
    assert user.sname == "abc"
