from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base


DATABASE = "sqlite:///db.sqlite3"
engine = create_engine(DATABASE, echo=False)
sesion_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.query = scoped_session(sesion_local).query_property()


def get_db() -> Generator[Any, Any, Any]:
    db = scoped_session(sesion_local)
    try:
        yield db
    finally:
        db.remove()
