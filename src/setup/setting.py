from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

DATABASE = "sqlite:///db.sqlite3"
Engine = create_engine(DATABASE, echo=False)
sesion_local = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()
Base.query = scoped_session(sesion_local).query_property()


def get_db():
    db = scoped_session(sesion_local)
    try:
        yield db
    finally:
        db.remove()
