"""
Shared dependencies for FastAPI routers
"""
from fastapi import Depends, Request, Header
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

from services.auth_service import AuthService
from models.core import User

# Global variables that will be set by main.py
db: AsyncIOMotorClient = None
auth_service: AuthService = None


def get_database() -> AsyncIOMotorClient:
    """Get database connection"""
    return db


def get_auth_service() -> AuthService:
    """Get authentication service"""
    return auth_service


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