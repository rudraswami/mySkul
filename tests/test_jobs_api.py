"""End-to-end tests for the asynchronous job API."""
import importlib
import sys

import pytest

httpx = pytest.importorskip("httpx")
AsyncClient = httpx.AsyncClient
fakeredis_aioredis = pytest.importorskip("fakeredis.aioredis")

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def fastapi_app(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("EMERGENT_LLM_KEY", "test-key")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("MONGO_PING_TIMEOUT_SECONDS", "0.1")
    monkeypatch.setenv("MONGO_CONNECT_TIMEOUT_MS", "100")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

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

    redis_client = _fake_client()
    await redis_client.flushall()
    await redis_client.close()


async def test_enqueue_and_process_job(fastapi_app):
    from backend.jobs import bootstrap as jobs_bootstrap

    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        body = {
            "job_type": "analyze",
            "project_id": "proj-123",
            "payload": {"text": "This is a synthetic storyboard."},
            "trace_id": "trace-1",
        }
        response = await client.post("/api/jobs", json=body)
        assert response.status_code == 202
        job_data = response.json()["job"]
        job_id = job_data["job_id"]
        assert job_data["status"] == "queued"
        assert job_data["reused"] is False

        orchestrator = jobs_bootstrap.get_orchestrator()
        await orchestrator.drain_all()

        status_response = await client.get(f"/api/jobs/{job_id}")
        assert status_response.status_code == 200
        status_payload = status_response.json()["job"]
        assert status_payload["status"] == "success"
        assert status_payload["result"]["summary"].startswith("This is a synthetic")

        second = await client.post("/api/jobs", json=body)
        assert second.json()["job"]["job_id"] == job_id
        assert second.json()["job"]["reused"] is True


async def test_job_dead_letter_on_repeated_failure(fastapi_app):
    from backend.jobs import bootstrap as jobs_bootstrap
    from backend.jobs import handlers
    from backend.jobs.models import JobType
    from backend import dependencies as deps

    original_handler = handlers.HANDLERS[JobType.GENERATE_AUDIO]

    call_state = {"count": 0}

    async def failing_handler(ctx):
        call_state["count"] += 1
        raise RuntimeError("planned failure")

    handlers.HANDLERS[JobType.GENERATE_AUDIO] = failing_handler
    jobs_bootstrap.get_orchestrator.cache_clear()
    deps.job_orchestrator = jobs_bootstrap.get_orchestrator()

    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        body = {
            "job_type": "generate_audio",
            "project_id": "proj-err",
            "payload": {"script": [{"line": "Hello"}]},
        }
        response = await client.post("/api/jobs", json=body)
        assert response.status_code == 202
        job_id = response.json()["job"]["job_id"]

        orchestrator = jobs_bootstrap.get_orchestrator()
        await orchestrator.drain_all()

        status_response = await client.get(f"/api/jobs/{job_id}")
        assert status_response.status_code == 200
        assert status_response.json()["job"]["status"] == "dead"
        orchestrator = jobs_bootstrap.get_orchestrator()
        max_attempts = orchestrator._definitions[JobType.GENERATE_AUDIO].max_attempts
        assert call_state["count"] == max_attempts

    handlers.HANDLERS[JobType.GENERATE_AUDIO] = original_handler
    jobs_bootstrap.get_orchestrator.cache_clear()
    deps.job_orchestrator = jobs_bootstrap.get_orchestrator()
