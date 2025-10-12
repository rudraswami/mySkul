"""Tests for the lightweight /ping health endpoint and startup instrumentation."""

import importlib
import sys

import pytest

testclient_module = pytest.importorskip("fastapi.testclient")
TestClient = testclient_module.TestClient


@pytest.fixture
def fastapi_app(monkeypatch):
    """Load the FastAPI app with required environment variables configured."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("EMERGENT_LLM_KEY", "test-key")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("MONGO_PING_TIMEOUT_SECONDS", "0.1")
    monkeypatch.setenv("MONGO_CONNECT_TIMEOUT_MS", "100")

    # Ensure we reload the module to apply patched environment variables consistently
    if "backend.server" in sys.modules:
        del sys.modules["backend.server"]

    server_module = importlib.import_module("backend.server")
    yield server_module.app

    # Ensure the Mongo client is closed after tests to avoid warnings
    server_module.client.close()


def test_ping_endpoint_returns_ok_status(fastapi_app):
    """Verify the /ping route responds instantly with a JSON payload."""
    with TestClient(fastapi_app) as client:
        response = client.get("/ping")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "mongo" in payload["startup"]
    assert "embedding" in payload["startup"]
