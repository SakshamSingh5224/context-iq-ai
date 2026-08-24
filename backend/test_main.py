"""
Basic pytest case for POST /api/v1/operations.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from models import Base

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_operation_success():
    payload = {
        "title": "Inspect cold-storage unit 4",
        "description": "Routine temperature and seal check.",
        "status": "open",
        "priority": "high",
        "latitude": 26.8467,
        "longitude": 80.9462,
    }

    response = client.post("/api/v1/operations", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["status"] == payload["status"]
    assert body["priority"] == payload["priority"]
    assert body["latitude"] == pytest.approx(payload["latitude"])
    assert body["longitude"] == pytest.approx(payload["longitude"])
    assert "id" in body
    assert "created_at" in body
