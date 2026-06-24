import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
os.chdir(BACKEND_DIR)
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import main


@pytest.fixture
def test_engine(monkeypatch):
    """An isolated in-memory database, swapped in for main.engine.

    main.create_db_and_seed is also disabled here so tests start from an
    empty schema instead of inheriting the app's demo seed data.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "create_db_and_seed", lambda: None)
    return engine


@pytest.fixture
def client(test_engine):
    with TestClient(main.app) as test_client:
        yield test_client
