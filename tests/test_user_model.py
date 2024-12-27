from src.models.user_model import User


def test_user_creation(db_session):
    new_user = User(userid=123, sname="abc")
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(userid=123).first()
    assert user is not None
    assert user.userid == 123
    assert user.sname == "abc"
