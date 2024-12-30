import pytest
from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base_model import Base
from setup.master_data_generator import generate_master_data


@pytest.fixture
def db_session() -> Generator[Any, Any, None]:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_maker()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def master_data(db_session) -> Generator[Any, Any, None]:
    generate_master_data(db_session)
    yield db_session
