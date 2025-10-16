"""
Shared dependencies for FastAPI routers
Centralized dependency injection for services and database
"""
from fastapi import Depends, Request, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.unified_subscription_service import UnifiedSubscriptionService
from services.ai_service import AIService
from models.core import User

# =============================================================================
# GLOBAL SERVICE INSTANCES
# These are set by main.py during application startup
# =============================================================================

db: AsyncIOMotorDatabase = None
auth_service: AuthService = None
subscription_service: SubscriptionService = None  # Legacy - being phased out
unified_subscription_service: UnifiedSubscriptionService = None  # New unified service
ai_service: AIService = None


# =============================================================================
# DEPENDENCY INJECTION FUNCTIONS
# =============================================================================

def get_database() -> AsyncIOMotorDatabase:
    """
    Get database connection
    Used as: db = Depends(get_database)
    """
    if db is None:
        raise RuntimeError("Database not initialized")
    return db


def get_auth_service() -> AuthService:
    """
    Get authentication service
    Used as: auth_svc = Depends(get_auth_service)
    """
    if auth_service is None:
        raise RuntimeError("Auth service not initialized")
    return auth_service


def get_subscription_service() -> SubscriptionService:
    """
    Get subscription service (Legacy)
    Used as: sub_svc = Depends(get_subscription_service)
    """
    if subscription_service is None:
        raise RuntimeError("Subscription service not initialized")
    return subscription_service


def get_unified_subscription_service() -> UnifiedSubscriptionService:
    """
    Get unified subscription service (Recommended)
    Used as: sub_svc = Depends(get_unified_subscription_service)
    """
    if unified_subscription_service is None:
        raise RuntimeError("Unified subscription service not initialized")
    return unified_subscription_service


def get_ai_service() -> AIService:
    """
    Get AI service
    Used as: ai_svc = Depends(get_ai_service)
    """
    if ai_service is None:
        raise RuntimeError("AI service not initialized")
    return ai_service


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user (required)
    Raises HTTPException if not authenticated
    """
    return await service.get_current_user(request, authorization)


async def get_current_user_optional(
    request: Request,
    service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None
    Does not raise exception if not authenticated
    """
    return await service.get_current_user_optional(request)