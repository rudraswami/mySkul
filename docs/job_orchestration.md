# Job Orchestration Overview

The job orchestration layer introduces a Redis-backed queue used to execute media
pipeline steps asynchronously. Every job is idempotent and keyed by a
fingerprint derived from the job type, project, and payload contents. When the
same request is enqueued multiple times, the orchestrator reuses the previous
job record and avoids recomputing the artifact.

## Architecture

- **Redis** stores job metadata, the ready queue, delayed retries, and a
  dead-letter list for jobs that exceed the retry budget.
- **Job handlers** live in `backend/jobs/handlers.py` and run inside the worker
  (`backend/workers/job_worker.py`). They are deterministic so they can safely
  retry without producing divergent artifacts.
- **FastAPI router** exposes `POST /api/jobs` to enqueue work and
  `GET /api/jobs/{id}` to fetch status.
- **Metrics** are exported via `prometheus_client` counters and histograms to
  observe enqueue, retry, and completion rates plus job durations.

## Running the worker locally

```bash
export REDIS_URL=redis://localhost:6379/0
python -m backend.workers.job_worker
```

The API requires the same `REDIS_URL` environment variable. In tests we use
`fakeredis` to avoid depending on an external service.
