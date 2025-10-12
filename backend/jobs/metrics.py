"""Prometheus metrics for job orchestration."""
from prometheus_client import Counter, Histogram


JOBS_ENQUEUED = Counter(
    "jobs_enqueued_total",
    "Number of jobs enqueued by type",
    labelnames=("job_type", "reused"),
)

JOBS_COMPLETED = Counter(
    "jobs_completed_total",
    "Number of jobs completed by status",
    labelnames=("job_type", "status"),
)

JOB_DURATION = Histogram(
    "job_duration_seconds",
    "Observed runtime for pipeline jobs",
    labelnames=("job_type",),
    buckets=(0.1, 0.5, 1, 2, 5, 10, 20, 60, 120, 300, 600),
)

JOB_RETRIES = Counter(
    "job_retries_total",
    "Number of job retries by type",
    labelnames=("job_type",),
)
