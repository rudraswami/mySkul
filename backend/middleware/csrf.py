"""
CSRF Protection Middleware - Double-Submit Cookie Pattern
Provides Cross-Site Request Forgery protection for state-changing operations

Pattern: Double-Submit Cookie
- Server sets csrf_token cookie via /api/auth/csrf-token endpoint
- Client reads cookie and sends token in X-CSRF-Token header
- Middleware validates: header token == cookie token

BUGFIX: Using JSONResponse instead of raising HTTPException inside dispatch()
to avoid Starlette's TaskGroup causing unhandled ExceptionGroup (500 errors).
"""
import logging
import os
import secrets
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)

# Configuration
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_HEADER_ALTERNATIVES = ["X-XSRF-TOKEN", "X-CSRFToken"]  # Backward compat


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware using Double-Submit Cookie pattern.
    
    Contract:
    - Cookie name: csrf_token
    - Header name: X-CSRF-Token (primary), X-XSRF-TOKEN/X-CSRFToken (fallback)
    - Validation: header token == cookie token
    """
    
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or []
        self.is_debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection"""
        
        path = request.url.path
        method = request.method
        
        # ALWAYS exempt teach-me-back (explicit check first)
        if '/teach-me-back' in path:
            return await call_next(request)
        
        # ALWAYS exempt visual-engine (explicit check)
        if '/visual-engine/' in path:
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
        if method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            
            # Generate and set CSRF token for GET requests (cookie + header)
            csrf_token = self._generate_csrf_token()
            response.headers[CSRF_HEADER_NAME] = csrf_token
            
            # Store token in session (backward compatibility)
            if "session" in request.scope:
                request.session["csrf_token"] = csrf_token
            
            # Note: Cookie is set by /api/auth/csrf-token endpoint
            # This header allows clients to read token from any GET response
            
            return response
        
        # Validate CSRF token for state-changing methods (POST, PUT, PATCH, DELETE)
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            validation_result = self._validate_csrf_token(request)
            
            if not validation_result["valid"]:
                logger.warning(
                    f"CSRF validation failed for {method} {path}: {validation_result['reason']}"
                )
                
                error_content = {
                    "detail": validation_result["message"]
                }
                
                # Add debug info in development mode
                if self.is_debug:
                    error_content["debug"] = {
                        "expected_header": CSRF_HEADER_NAME,
                        "expected_cookie": CSRF_COOKIE_NAME,
                        "header_received": validation_result.get("header_received", False),
                        "cookie_received": validation_result.get("cookie_received", False),
                        "reason": validation_result["reason"]
                    }
                
                return JSONResponse(
                    status_code=403,
                    content=error_content
                )
        
        return await call_next(request)
    
    def _validate_csrf_token(self, request: Request) -> dict:
        """
        Validate CSRF token using Double-Submit Cookie pattern.
        
        Returns:
            dict with keys: valid (bool), reason (str), message (str)
        """
        # Get token from header (try primary, then alternatives)
        token_from_header = request.headers.get(CSRF_HEADER_NAME)
        header_used = CSRF_HEADER_NAME
        
        if not token_from_header:
            for alt_header in CSRF_HEADER_ALTERNATIVES:
                token_from_header = request.headers.get(alt_header)
                if token_from_header:
                    header_used = alt_header
                    logger.info(f"CSRF: Using alternative header {alt_header} (consider using {CSRF_HEADER_NAME})")
                    break
        
        # Get token from cookie
        token_from_cookie = request.cookies.get(CSRF_COOKIE_NAME)
        
        # Fallback: Also check session for backward compatibility
        token_from_session = None
        if "session" in request.scope:
            token_from_session = request.session.get("csrf_token")
        
        # Use cookie token if available, otherwise fall back to session
        expected_token = token_from_cookie or token_from_session
        
        # Validation
        if not token_from_header:
            return {
                "valid": False,
                "reason": "header_missing",
                "message": f"CSRF token missing. Include {CSRF_HEADER_NAME} header.",
                "header_received": False,
                "cookie_received": bool(token_from_cookie)
            }
        
        if not expected_token:
            return {
                "valid": False,
                "reason": "cookie_missing",
                "message": "CSRF cookie missing. Call GET /api/auth/csrf-token first.",
                "header_received": True,
                "cookie_received": False
            }
        
        # Compare tokens securely
        if not secrets.compare_digest(token_from_header, expected_token):
            return {
                "valid": False,
                "reason": "token_mismatch",
                "message": "CSRF token invalid. Please refresh the page and try again.",
                "header_received": True,
                "cookie_received": True
            }
        
        return {
            "valid": True,
            "reason": "ok",
            "message": "Token valid",
            "header_received": True,
            "cookie_received": True
        }
    
    def _generate_csrf_token(self) -> str:
        """Generate a secure random CSRF token"""
        return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> Optional[str]:
    """
    Helper function to get CSRF token from request.
    Checks cookie first (double-submit), then session (backward compat).
    
    Usage: token = get_csrf_token(request)
    """
    # Try cookie first (double-submit pattern)
    token = request.cookies.get(CSRF_COOKIE_NAME)
    if token:
        return token
    
    # Fallback to session
    if "session" in request.scope:
        return request.session.get("csrf_token")
    
    return None
