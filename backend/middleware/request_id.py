"""
Request ID Middleware
=====================

Adds unique request ID to every API request for tracing and debugging.

Features:
- Generates UUID for each request
- Adds X-Request-ID header to response
- Stores in request.state for logging
- Enables correlation across services
"""

import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to every request.
    
    The request ID is:
    1. Generated as UUID
    2. Stored in request.state.request_id
    3. Added to response headers as X-Request-ID
    4. Can be used in logging for request tracing
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add request ID.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response with X-Request-ID header
        """
        # Check if client provided request ID (for distributed tracing)
        request_id = request.headers.get("X-Request-ID")
        
        # Generate new ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store in request state for access in handlers
        request.state.request_id = request_id
        
        # Log request with ID
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            logger.info(f"[{request_id}] Response: {response.status_code}")
            
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing request: {e}", exc_info=True)
            raise


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Request ID string
    
    Usage:
        from fastapi import Request
        from middleware.request_id import get_request_id
        
        @router.get("/example")
        async def example(request: Request):
            request_id = get_request_id(request)
            logger.info(f"[{request_id}] Processing example request")
    """
    return getattr(request.state, 'request_id', 'unknown')


