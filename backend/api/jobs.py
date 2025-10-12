"""API routes for asynchronous job orchestration."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from jobs.manager import JobOrchestrator
from jobs.models import JobCreateRequest, JobStatusResponse

from dependencies import get_job_orchestrator

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_job(
    request: JobCreateRequest,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
) -> JobStatusResponse:
    """Enqueue a new pipeline job or reuse an existing one."""
    job, reused = await orchestrator.enqueue_job(
        request.job_type,
        payload=request.payload,
        project_id=request.project_id,
        trace_id=request.trace_id,
        idempotency_key=request.idempotency_key,
    )
    job.reused = reused
    return JobStatusResponse(job=job)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
) -> JobStatusResponse:
    """Return the latest status for a job."""
    job = await orchestrator.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobStatusResponse(job=job)
