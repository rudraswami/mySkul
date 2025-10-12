"""Pydantic models and enums for the asynchronous job orchestration system."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class JobType(str, Enum):
    """Supported pipeline job types."""

    ANALYZE = "analyze"
    ANALYZE_SCENES = "analyze_scenes"
    GENERATE_SCRIPT = "generate_script"
    GENERATE_STORYBOARD = "generate_storyboard"
    GENERATE_AUDIO = "generate_audio"
    GENERATE_VIDEO = "generate_video"
    GENERATE_CINEMATIC = "generate_cinematic"


class JobStatus(str, Enum):
    """Lifecycle state of a job."""

    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD = "dead"


class JobRecord(BaseModel):
    """Job metadata stored in Redis."""

    id: str
    job_type: JobType
    status: JobStatus = JobStatus.QUEUED
    payload: Dict[str, Any] = Field(default_factory=dict)
    project_id: Optional[str] = None
    trace_id: Optional[str] = None
    attempts: int = 0
    max_attempts: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {datetime: lambda value: value.isoformat()}


class JobCreateRequest(BaseModel):
    """Request schema for enqueueing jobs via the API."""

    job_type: JobType
    payload: Dict[str, Any] = Field(default_factory=dict)
    project_id: str
    idempotency_key: Optional[str] = None
    trace_id: Optional[str] = None


class JobResponse(BaseModel):
    """Serialized job payload returned to API consumers."""

    job_id: str
    job_type: JobType
    status: JobStatus
    project_id: Optional[str]
    attempts: int
    max_attempts: int
    queued_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    fingerprint: str
    reused: bool = False


class JobStatusResponse(BaseModel):
    """Response envelope for status endpoint."""

    job: JobResponse


@dataclass(frozen=True)
class JobDefinition:
    """Configuration parameters for a job type."""

    job_type: JobType
    max_attempts: int
    backoff_start_seconds: float
    timeout_seconds: float


DEFAULT_JOB_DEFINITIONS = {
    JobType.ANALYZE: JobDefinition(JobType.ANALYZE, max_attempts=3, backoff_start_seconds=1.0, timeout_seconds=180.0),
    JobType.ANALYZE_SCENES: JobDefinition(JobType.ANALYZE_SCENES, max_attempts=3, backoff_start_seconds=1.0, timeout_seconds=180.0),
    JobType.GENERATE_SCRIPT: JobDefinition(JobType.GENERATE_SCRIPT, max_attempts=3, backoff_start_seconds=1.5, timeout_seconds=240.0),
    JobType.GENERATE_STORYBOARD: JobDefinition(JobType.GENERATE_STORYBOARD, max_attempts=3, backoff_start_seconds=1.5, timeout_seconds=240.0),
    JobType.GENERATE_AUDIO: JobDefinition(JobType.GENERATE_AUDIO, max_attempts=4, backoff_start_seconds=2.0, timeout_seconds=300.0),
    JobType.GENERATE_VIDEO: JobDefinition(JobType.GENERATE_VIDEO, max_attempts=4, backoff_start_seconds=3.0, timeout_seconds=360.0),
    JobType.GENERATE_CINEMATIC: JobDefinition(JobType.GENERATE_CINEMATIC, max_attempts=4, backoff_start_seconds=3.0, timeout_seconds=420.0),
}
