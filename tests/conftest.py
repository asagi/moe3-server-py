import pytest
from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base_model import Base


@pytest.fixture
def db_session() -> Generator[Any, Any, None]:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_maker()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
