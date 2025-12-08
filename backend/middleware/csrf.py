"""
CSRF Protection Middleware
Provides Cross-Site Request Forgery protection for state-changing operations
"""
import logging
import secrets
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware
    - Generates CSRF tokens for GET requests
    - Validates CSRF tokens for POST, PUT, PATCH, DELETE requests
    """
    
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/api/auth/google/login",  # OAuth redirect
            "/api/auth/google/callback",  # OAuth callback
            "/api/auth/session",  # Session check
            "/api/auth/profile/complete",  # Onboarding completion
            "/api/auth/register",  # Registration
            "/api/auth/login",  # Login
            "/api/health",  # Health check
            "/docs",  # API docs
            "/openapi.json",  # OpenAPI spec
            "/api/mock-tests/",  # Mock test endpoints (submit, generate, etc.)
            "/api/ai/",  # AI endpoints (chat, neuro-symbolic, etc.)
            "/api/ai/teach-me-back",  # Teach Me Back feature
            "/api/subscription/",  # Subscription endpoints
            "/api/gamification/"  # Gamification endpoints
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection"""
        
        path = request.url.path
        
        # ALWAYS exempt teach-me-back (explicit check first)
        if '/teach-me-back' in path:
            logger.info(f"✅ CSRF exempting teach-me-back: {path}")
            return await call_next(request)
        
        # Skip CSRF check for exempt paths
        is_exempt = any(
            path.startswith(exempt_path) or 
            path.startswith(exempt_path.rstrip('/'))
            for exempt_path in self.exempt_paths
        )
        
        if is_exempt:
            return await call_next(request)
        
        # Skip CSRF check for safe methods (GET, HEAD, OPTIONS)
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            
            # Generate new CSRF token for GET requests
            csrf_token = self._generate_csrf_token()
            response.headers["X-CSRF-Token"] = csrf_token
            
            # Store token in session
            if "session" in request.scope:
                request.session["csrf_token"] = csrf_token
            
            return response
        
        # Validate CSRF token for state-changing methods
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Get token from header
            token_from_header = request.headers.get("X-CSRF-Token")
            
            # Get token from session
            token_from_session = None
            if "session" in request.scope:
                token_from_session = request.session.get("csrf_token")
            
            # Validate token
            if not token_from_header or not token_from_session:
                logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token missing. Please refresh the page and try again."
                )
            
            if not secrets.compare_digest(token_from_header, token_from_session):
                logger.warning(f"CSRF token mismatch for {request.method} {request.url.path}")
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token invalid. Please refresh the page and try again."
                )
        
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        """Generate a secure random CSRF token"""
        return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> Optional[str]:
    """
    Helper function to get CSRF token from request session
    Usage: token = get_csrf_token(request)
    """
    if "session" in request.scope:
        return request.session.get("csrf_token")
    return None
