"""Shared dependencies for FastAPI routers."""
from __future__ import annotations

from fastapi import Depends, Header, Request
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from jobs.manager import JobOrchestrator
from models.core import User
from services.auth_service import AuthService

# Global variables that will be set by main.py
db: AsyncIOMotorClient = None
auth_service: AuthService = None
job_orchestrator: JobOrchestrator | None = None


def get_database() -> AsyncIOMotorClient:
    """Get database connection"""
    return db


def get_auth_service() -> AuthService:
    """Get authentication service"""
    return auth_service


def get_job_orchestrator() -> JobOrchestrator:
    """Expose the shared job orchestrator instance."""
    if job_orchestrator is None:
        raise RuntimeError("Job orchestrator not initialized")
    return job_orchestrator


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user"""
    return await service.get_current_user(request, authorization)


async def get_current_user_optional(
    request: Request,
    service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    return await service.get_current_user_optional(request)