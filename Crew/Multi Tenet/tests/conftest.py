import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:3000"]'
os.environ["AI_ENGINE"] = "fallback"
os.environ["EMBEDDINGS_PROVIDER"] = "hash"
os.environ["VECTOR_STORE"] = "numpy"
os.environ["STORAGE_DIR"] = "/tmp/opencode/td-test-storage"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.services.vector import reset_vector_store

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    reset_vector_store()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    reset_vector_store()


def register(client: TestClient, email: str, workspace: str | None = None) -> dict:
    payload = {
        "full_name": "Test User",
        "email": email,
        "password": "strong-pass-123",
    }
    if workspace:
        payload["workspace_name"] = workspace
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
