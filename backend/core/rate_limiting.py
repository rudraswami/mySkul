"""
Rate Limiting Configuration
Protects API endpoints from abuse and DDoS attacks
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
# key_func: Function to identify clients (by IP address)
# Allow configuring storage via env; default to in-memory
_storage_uri = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default: 100 requests per minute per IP
    storage_uri=_storage_uri,  # In-memory by default; set Redis for production
    strategy="fixed-window"  # Count resets at fixed intervals
)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors
    Returns user-friendly error message with retry information
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "detail": exc.detail,
            "retry_after": "60 seconds"
        },
        headers={
            "Retry-After": "60"  # Suggest retry after 60 seconds
        }
    )

# Common rate limit presets
RATE_LIMITS = {
    # Authentication endpoints - strict limits to prevent brute force
    "auth_login": "5/minute",           # 5 login attempts per minute
    "auth_register": "3/minute",        # 3 registrations per minute
    "auth_password_reset": "3/minute",  # 3 password resets per minute
    
    # AI endpoints - moderate limits (resource intensive)
    "ai_chat": "30/minute",             # 30 AI chat messages per minute
    "ai_generate": "10/minute",         # 10 test generations per minute
    "ai_notes": "20/minute",            # 20 auto-note sessions per minute
    
    # General API - generous limits
    "api_read": "100/minute",           # 100 read requests per minute
    "api_write": "50/minute",           # 50 write requests per minute
    
    # Payment endpoints - strict limits
    "payment_create": "5/minute",       # 5 payment creations per minute
    "payment_verify": "10/minute",      # 10 payment verifications per minute
}

# Export limiter instance and handler
__all__ = ["limiter", "rate_limit_exceeded_handler", "RATE_LIMITS"]
