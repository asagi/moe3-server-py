from sqlalchemy.orm import Session
from models.user_model import User
from schemas.user_schema import UserCreate


def create_user_entity(db: Session, user: UserCreate) -> User:
    db_user = User(
        userid=user.userid,
        sname=user.sname,
        dname=user.dname,
        acceesskey=user.accesskey,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
