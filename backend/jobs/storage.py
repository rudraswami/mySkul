"""Redis-backed persistence for the job orchestration layer."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from redis.asyncio import Redis

from .models import JobRecord, JobStatus


class RedisJobStore:
    """Persist job metadata and queue state inside Redis."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def _job_key(job_id: str) -> str:
        return f"jobs:record:{job_id}"

    @staticmethod
    def _dedupe_key(job_type: str, fingerprint: str) -> str:
        return f"jobs:dedupe:{job_type}:{fingerprint}"

    @staticmethod
    def _queue_key() -> str:
        return "jobs:queue"

    @staticmethod
    def _delayed_key() -> str:
        return "jobs:delayed"

    @staticmethod
    def _dead_letter_key() -> str:
        return "jobs:dead_letter"

    async def save_job(self, record: JobRecord) -> JobRecord:
        """Persist the full job record."""
        await self._redis.set(self._job_key(record.id), record.model_dump_json())
        return record

    async def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Fetch a job record."""
        raw = await self._redis.get(self._job_key(job_id))
        if not raw:
            return None
        return JobRecord.model_validate_json(raw)

    async def set_dedupe(self, job_type: str, fingerprint: str, job_id: str) -> None:
        await self._redis.set(self._dedupe_key(job_type, fingerprint), job_id)

    async def get_dedupe(self, job_type: str, fingerprint: str) -> Optional[str]:
        return await self._redis.get(self._dedupe_key(job_type, fingerprint))

    async def enqueue(self, job_id: str) -> None:
        await self._redis.rpush(self._queue_key(), job_id)

    async def pop_next(self, timeout: int = 1) -> Optional[str]:
        item = await self._redis.blpop(self._queue_key(), timeout=timeout)
        if not item:
            return None
        _, job_id = item
        return job_id

    async def schedule_retry(self, job_id: str, delay_seconds: float) -> None:
        run_at = datetime.now(timezone.utc).timestamp() + delay_seconds
        await self._redis.zadd(self._delayed_key(), {job_id: run_at})

    async def poll_scheduled(self) -> Optional[str]:
        now = datetime.now(timezone.utc).timestamp()
        items = await self._redis.zrangebyscore(self._delayed_key(), 0, now, start=0, num=1)
        if not items:
            return None
        job_id = items[0]
        await self._redis.zrem(self._delayed_key(), job_id)
        return job_id

    async def add_dead_letter(self, record: JobRecord) -> None:
        payload = {
            "id": record.id,
            "job_type": record.job_type.value,
            "status": record.status.value,
            "error": record.error,
            "attempts": record.attempts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._redis.lpush(self._dead_letter_key(), json.dumps(payload))

    async def update_status(self, job_id: str, *, status: JobStatus, **fields) -> Optional[JobRecord]:
        record = await self.get_job(job_id)
        if not record:
            return None
        data = record.model_dump()
        data.update(fields)
        data["status"] = status
        data["updated_at"] = datetime.now(timezone.utc)
        updated = JobRecord(**data)
        await self.save_job(updated)
        return updated
