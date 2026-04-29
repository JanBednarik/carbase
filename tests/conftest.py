import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from app.database import get_session
from app.main import app
from tests.factories import BrandFactory, CarModelFactory

load_dotenv()

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def factory_session(session: Session):
    BrandFactory._meta.sqlalchemy_session = session
    CarModelFactory._meta.sqlalchemy_session = session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(JSONSnapshotExtension)
