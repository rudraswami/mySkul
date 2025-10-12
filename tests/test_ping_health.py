"""Tests for the lightweight /ping health endpoint and startup instrumentation."""

import asyncio
import importlib
import sys

import pytest

fakeredis_aioredis = pytest.importorskip("fakeredis.aioredis")

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
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    # Ensure we reload the module to apply patched environment variables consistently
    if "backend.server" in sys.modules:
        del sys.modules["backend.server"]

    from backend.jobs import config as jobs_config
    from backend.jobs import bootstrap as jobs_bootstrap

    jobs_config.get_redis_client.cache_clear()
    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)

    def _fake_client():
        return fake_redis

    monkeypatch.setattr(jobs_config, "get_redis_client", _fake_client)
    jobs_bootstrap.get_orchestrator.cache_clear()

    server_module = importlib.import_module("backend.server")
    yield server_module.app

    # Ensure the Mongo client is closed after tests to avoid warnings
    server_module.client.close()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(fake_redis.flushall())
    loop.run_until_complete(fake_redis.close())
    loop.close()


def test_ping_endpoint_returns_ok_status(fastapi_app):
    """Verify the /ping route responds instantly with a JSON payload."""
    with TestClient(fastapi_app) as client:
        response = client.get("/ping")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "mongo" in payload["startup"]
    assert "embedding" in payload["startup"]
