"""Job orchestration manager providing enqueueing and worker execution."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable, Dict, Optional, Tuple

from .metrics import JOBS_COMPLETED, JOBS_ENQUEUED, JOB_DURATION, JOB_RETRIES
from .models import (
    DEFAULT_JOB_DEFINITIONS,
    JobDefinition,
    JobRecord,
    JobResponse,
    JobStatus,
    JobType,
)
from .storage import RedisJobStore


@dataclass
class JobContext:
    """Context object passed to handlers."""

    record: JobRecord
    logger: logging.Logger


JobHandler = Callable[[JobContext], Awaitable[Dict[str, object]]]


class JobOrchestrator:
    """Coordinates Redis-backed job queueing and execution."""

    def __init__(
        self,
        store: RedisJobStore,
        handlers: Dict[JobType, JobHandler],
        definitions: Optional[Dict[JobType, JobDefinition]] = None,
        *,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._store = store
        self._handlers = handlers
        self._definitions = definitions or DEFAULT_JOB_DEFINITIONS
        self._logger = logger or logging.getLogger("jobs.orchestrator")

    async def enqueue_job(
        self,
        job_type: JobType,
        *,
        payload: Dict[str, object],
        project_id: str,
        trace_id: Optional[str],
        idempotency_key: Optional[str] = None,
    ) -> Tuple[JobResponse, bool]:
        """Create or reuse a job for the given payload."""
        if job_type not in self._handlers:
            raise ValueError(f"No handler registered for job type {job_type}")

        fingerprint = self._fingerprint(job_type, project_id, payload, idempotency_key)
        reused = False

        existing_id = await self._store.get_dedupe(job_type.value, fingerprint)
        if existing_id:
            record = await self._store.get_job(existing_id)
            if record and record.status != JobStatus.DEAD:
                reused = True
                return self._serialize(record, reused=reused), reused

        definition = self._definitions[job_type]
        job_id = uuid.uuid4().hex
        record = JobRecord(
            id=job_id,
            job_type=job_type,
            payload=json.loads(json.dumps(payload, sort_keys=True)),
            project_id=project_id,
            trace_id=trace_id,
            max_attempts=definition.max_attempts,
            fingerprint=fingerprint,
        )
        await self._store.save_job(record)
        await self._store.set_dedupe(job_type.value, fingerprint, job_id)
        await self._store.enqueue(job_id)

        JOBS_ENQUEUED.labels(job_type=job_type.value, reused=str(reused)).inc()
        self._logger.info(
            "queued_job",
            extra={
                "job_id": job_id,
                "job_type": job_type.value,
                "project_id": project_id,
                "trace_id": trace_id,
                "fingerprint": fingerprint,
            },
        )
        return self._serialize(record, reused=reused), reused

    async def get_job(self, job_id: str) -> Optional[JobResponse]:
        record = await self._store.get_job(job_id)
        if not record:
            return None
        reused = False
        return self._serialize(record, reused=reused)

    async def run_worker(self, *, poll_interval: float = 0.5) -> None:
        """Continuously process jobs until cancelled."""
        self._logger.info("job_worker_started")
        try:
            while True:
                job_id = await self._next_job_id()
                if not job_id:
                    await asyncio.sleep(poll_interval)
                    continue
                await self._process_job(job_id)
        except asyncio.CancelledError:
            self._logger.info("job_worker_stopped")
            raise

    async def _next_job_id(self) -> Optional[str]:
        job_id = await self._store.pop_next(timeout=1)
        if job_id:
            return job_id
        return await self._store.poll_scheduled()

    async def _process_job(self, job_id: str) -> None:
        record = await self._store.get_job(job_id)
        if not record:
            self._logger.warning("job_missing", extra={"job_id": job_id})
            return
        if record.status in {JobStatus.RUNNING, JobStatus.SUCCESS}:
            return

        handler = self._handlers.get(record.job_type)
        if not handler:
            await self._store.update_status(job_id, status=JobStatus.DEAD, error="Handler missing")
            self._logger.error("handler_missing", extra={"job_id": job_id, "job_type": record.job_type.value})
            return

        attempts = record.attempts + 1
        record.attempts = attempts
        record.status = JobStatus.RUNNING
        record.updated_at = datetime.now(timezone.utc)
        await self._store.save_job(record)

        context = JobContext(record=record, logger=self._logger)
        start_time = time.perf_counter()
        try:
            result = await asyncio.wait_for(handler(context), timeout=self._definitions[record.job_type].timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            duration = time.perf_counter() - start_time
            JOB_DURATION.labels(job_type=record.job_type.value).observe(duration)
            await self._handle_failure(record, exc)
            return

        duration = time.perf_counter() - start_time
        record.status = JobStatus.SUCCESS
        record.result = result
        record.error = None
        record.updated_at = datetime.now(timezone.utc)
        await self._store.save_job(record)

        JOB_DURATION.labels(job_type=record.job_type.value).observe(duration)
        JOBS_COMPLETED.labels(job_type=record.job_type.value, status=JobStatus.SUCCESS.value).inc()
        self._logger.info(
            "job_completed",
            extra={
                "job_id": record.id,
                "job_type": record.job_type.value,
                "attempts": record.attempts,
                "duration": duration,
            },
        )

    async def _handle_failure(self, record: JobRecord, exc: Exception) -> None:
        record.error = str(exc)
        definition = self._definitions[record.job_type]
        if record.attempts < definition.max_attempts:
            record.status = JobStatus.RETRYING
            record.updated_at = datetime.now(timezone.utc)
            await self._store.save_job(record)
            delay = definition.backoff_start_seconds * (2 ** (record.attempts - 1))
            await self._store.schedule_retry(record.id, delay_seconds=delay)
            JOB_RETRIES.labels(job_type=record.job_type.value).inc()
            JOBS_COMPLETED.labels(job_type=record.job_type.value, status=JobStatus.RETRYING.value).inc()
            self._logger.warning(
                "job_retry_scheduled",
                extra={
                    "job_id": record.id,
                    "job_type": record.job_type.value,
                    "attempts": record.attempts,
                    "delay": delay,
                    "error": record.error,
                },
            )
            return

        record.status = JobStatus.DEAD
        record.updated_at = datetime.now(timezone.utc)
        await self._store.save_job(record)
        await self._store.add_dead_letter(record)
        JOBS_COMPLETED.labels(job_type=record.job_type.value, status=JobStatus.DEAD.value).inc()
        self._logger.error(
            "job_dead_lettered",
            extra={
                "job_id": record.id,
                "job_type": record.job_type.value,
                "attempts": record.attempts,
                "error": record.error,
            },
        )

    async def drain_all(self, *, stop_when_idle: bool = True) -> None:
        """Utility for tests to process all queued jobs until idle."""
        while True:
            job_id = await self._next_job_id()
            if not job_id:
                if stop_when_idle:
                    return
                await asyncio.sleep(0.1)
                continue
            await self._process_job(job_id)

    def _serialize(self, record: JobRecord, *, reused: bool) -> JobResponse:
        return JobResponse(
            job_id=record.id,
            job_type=record.job_type,
            status=record.status,
            project_id=record.project_id,
            attempts=record.attempts,
            max_attempts=record.max_attempts,
            queued_at=record.created_at,
            updated_at=record.updated_at,
            result=record.result,
            error=record.error,
            fingerprint=record.fingerprint,
            reused=reused,
        )

    @staticmethod
    def _fingerprint(
        job_type: JobType,
        project_id: str,
        payload: Dict[str, object],
        idempotency_key: Optional[str],
    ) -> str:
        normalized_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        base = f"{job_type.value}:{project_id}:{normalized_payload}:{idempotency_key or ''}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()


def build_orchestrator(store: RedisJobStore, handlers: Dict[JobType, JobHandler]) -> JobOrchestrator:
    return JobOrchestrator(store=store, handlers=handlers)
