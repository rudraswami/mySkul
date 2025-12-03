"""
Standardized Error Response Format
===================================

Provides consistent error response structure across all API endpoints.
Makes frontend error handling predictable and reliable.

Standard Format:
{
    "success": false,
    "error_code": "FEATURE_LIMIT_REACHED",
    "message": "User-friendly message",
    "details": {...},  # Optional debug info
    "trace_id": "uuid",
    "timestamp": "ISO8601"
}
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorCode:
    """Standard error codes for the application"""
    
    # Authentication errors (401)
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    
    # Authorization errors (403)
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Payment required (402)
    FEATURE_LIMIT_REACHED = "FEATURE_LIMIT_REACHED"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    UPGRADE_REQUIRED = "UPGRADE_REQUIRED"
    
    # Bad request (400)
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Not found (404)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    
    # Rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Server errors (500)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error_code: Error code from ErrorCode class
        message: User-friendly error message
        status_code: HTTP status code
        details: Optional additional details for debugging
        trace_id: Optional trace ID for request tracking
    
    Returns:
        Standardized error dict
    
    Example:
        >>> create_error_response(
        ...     ErrorCode.FEATURE_LIMIT_REACHED,
        ...     "You've used all 10 free AI questions today",
        ...     status_code=402,
        ...     details={"limit": 10, "used": 10}
        ... )
    """
    if not trace_id:
        trace_id = str(uuid.uuid4())
    
    response = {
        "success": False,
        "error_code": error_code,
        "message": message,
        "trace_id": trace_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response["details"] = details
    
    # Log error for monitoring
    logger.warning(
        f"Error response: {error_code} - {message} "
        f"(trace_id: {trace_id}, status: {status_code})"
    )
    
    return response


def create_success_response(
    data: Any,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        meta: Optional metadata (pagination, etc.)
    
    Returns:
        Standardized success dict
    
    Example:
        >>> create_success_response(
        ...     data={"response": "Great question!"},
        ...     message="AI response generated successfully"
        ... )
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if message:
        response["message"] = message
    
    if meta:
        response["meta"] = meta
    
    return response


class StandardHTTPException(HTTPException):
    """
    Enhanced HTTPException with standardized error format.
    
    Usage:
        raise StandardHTTPException(
            status_code=402,
            error_code=ErrorCode.FEATURE_LIMIT_REACHED,
            message="You've reached your daily limit",
            details={"limit": 10, "used": 10}
        )
    """
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ):
        detail = create_error_response(
            error_code=error_code,
            message=message,
            status_code=status_code,
            details=details,
            trace_id=trace_id
        )
        super().__init__(status_code=status_code, detail=detail)


# Convenience functions for common errors

def unauthorized_error(message: str = "Authentication required") -> StandardHTTPException:
    """401 Unauthorized"""
    return StandardHTTPException(
        status_code=401,
        error_code=ErrorCode.UNAUTHORIZED,
        message=message
    )


def forbidden_error(message: str = "Access denied") -> StandardHTTPException:
    """403 Forbidden"""
    return StandardHTTPException(
        status_code=403,
        error_code=ErrorCode.FORBIDDEN,
        message=message
    )


def subscription_required_error(
    message: str = "Upgrade required",
    details: Optional[Dict] = None
) -> StandardHTTPException:
    """402 Payment Required"""
    return StandardHTTPException(
        status_code=402,
        error_code=ErrorCode.SUBSCRIPTION_REQUIRED,
        message=message,
        details=details
    )


def validation_error(message: str, details: Optional[Dict] = None) -> StandardHTTPException:
    """400 Bad Request"""
    return StandardHTTPException(
        status_code=400,
        error_code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details
    )


def not_found_error(message: str = "Resource not found") -> StandardHTTPException:
    """404 Not Found"""
    return StandardHTTPException(
        status_code=404,
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
        message=message
    )


def internal_server_error(
    message: str = "Internal server error",
    details: Optional[Dict] = None
) -> StandardHTTPException:
    """500 Internal Server Error"""
    return StandardHTTPException(
        status_code=500,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message=message,
        details=details
    )


