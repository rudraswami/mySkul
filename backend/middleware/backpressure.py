"""
🛡️ Backpressure Middleware - Cognito OS v1.0
=============================================

Protects the server from overload by:
1. Load shedding: Reject requests with 503 when overloaded
2. Graceful degradation: Force fast path under high load
3. Request tracking: Monitor concurrent request count
4. Retry-After: Tell clients when to retry

BEHAVIOR:
- < 70% load: Normal operation
- 70-85% load: Degraded mode (fast path forced for AI endpoints)
- 85-95% load: More aggressive degradation
- > 95% load: Load shedding (503 Service Unavailable)

FEATURE FLAGS:
- ENABLE_BACKPRESSURE: Enable/disable middleware (default: true)
- MAX_CONCURRENT_REQUESTS: Server-wide limit (default: 200)
- BACKPRESSURE_SHED_THRESHOLD: Load % to start shedding (default: 0.95)
- BACKPRESSURE_DEGRADE_THRESHOLD: Load % to start degrading (default: 0.70)
"""

import asyncio
import logging
import os
import time
from typing import Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)

# Feature flags
ENABLE_BACKPRESSURE = os.getenv("ENABLE_BACKPRESSURE", "true").lower() == "true"
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "200"))
SHED_THRESHOLD = float(os.getenv("BACKPRESSURE_SHED_THRESHOLD", "0.95"))
DEGRADE_THRESHOLD = float(os.getenv("BACKPRESSURE_DEGRADE_THRESHOLD", "0.70"))


class BackpressureMiddleware(BaseHTTPMiddleware):
    """
    Middleware that implements backpressure and graceful degradation.
    
    When server is overloaded:
    1. Returns 503 for new requests (load shedding)
    2. Downgrades complexity for accepted requests (degradation)
    3. Adds Retry-After header to help clients back off
    
    Thread-safe request counting with asyncio locks.
    """
    
    # Paths that bypass load shedding (health checks, etc.)
    BYPASS_PATHS: Set[str] = {
        '/health',
        '/metrics', 
        '/api/health',
        '/api/auth/me',
        '/docs',
        '/openapi.json',
        '/favicon.ico'
    }
    
    # AI endpoints that should be load-managed
    AI_PATHS: Set[str] = {
        '/api/ai/neuro-symbolic',
        '/api/ai/mentor-only',
        '/api/ai/professor-only',
        '/api/ai/dual-response',
        '/api/ai/tutor',
        '/api/agentic/query',
        '/api/agentic/doubt'
    }
    
    def __init__(
        self, 
        app, 
        max_concurrent_requests: int = None,
        shed_threshold: float = None,
        degrade_threshold: float = None
    ):
        super().__init__(app)
        self.max_concurrent_requests = max_concurrent_requests or MAX_CONCURRENT_REQUESTS
        self.shed_threshold = shed_threshold or SHED_THRESHOLD
        self.degrade_threshold = degrade_threshold or DEGRADE_THRESHOLD
        
        self.current_requests = 0
        self._lock = asyncio.Lock()
        
        # Metrics
        self.total_requests = 0
        self.shed_requests = 0
        self.degraded_requests = 0
        self.bypassed_requests = 0
        
        logger.info(f"🛡️ BackpressureMiddleware initialized")
        logger.info(f"   ├── max_concurrent: {self.max_concurrent_requests}")
        logger.info(f"   ├── shed_threshold: {self.shed_threshold:.0%}")
        logger.info(f"   └── degrade_threshold: {self.degrade_threshold:.0%}")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with backpressure control.
        """
        # Feature flag check
        if not ENABLE_BACKPRESSURE:
            return await call_next(request)
        
        path = request.url.path
        
        # Bypass paths skip load management entirely
        if path in self.BYPASS_PATHS or path.startswith('/static'):
            async with self._lock:
                self.bypassed_requests += 1
            return await call_next(request)
        
        # Calculate load factor
        async with self._lock:
            self.total_requests += 1
            load_factor = self.current_requests / self.max_concurrent_requests
            
            # CRITICAL LOAD: Reject request (load shedding)
            if load_factor >= self.shed_threshold:
                self.shed_requests += 1
                logger.warning(
                    f"🚫 Load shedding: {self.current_requests}/{self.max_concurrent_requests} "
                    f"({load_factor:.1%}) - {path}"
                )
                return self._shed_response(load_factor)
            
            # Increment request counter
            self.current_requests += 1
        
        try:
            # Determine if request should be degraded
            should_degrade = False
            if load_factor >= self.degrade_threshold and path in self.AI_PATHS:
                should_degrade = True
                async with self._lock:
                    self.degraded_requests += 1
            
            # Store state on request for downstream access
            request.state.load_factor = load_factor
            request.state.force_fast_path = should_degrade
            request.state.is_degraded = should_degrade
            request.state.backpressure_enabled = True
            
            # Process request
            start_time = time.time()
            response = await call_next(request)
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Add observability headers
            response.headers["X-Load-Factor"] = f"{load_factor:.2f}"
            response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.0f}"
            if should_degrade:
                response.headers["X-Degraded"] = "true"
            
            return response
            
        finally:
            # Always decrement counter
            async with self._lock:
                self.current_requests = max(0, self.current_requests - 1)
    
    def _shed_response(self, load_factor: float) -> JSONResponse:
        """Generate 503 response for load shedding"""
        # Calculate retry delay based on load
        retry_seconds = min(30, max(5, int((load_factor - 0.9) * 100)))
        
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Server temporarily overloaded. Please retry.",
                "code": "SERVICE_OVERLOADED",
                "retry_after_seconds": retry_seconds,
                "load_factor": round(load_factor, 2)
            },
            headers={
                "Retry-After": str(retry_seconds),
                "X-Load-Factor": f"{load_factor:.2f}",
                "X-Shed": "true"
            }
        )
    
    def get_metrics(self) -> dict:
        """Get middleware metrics for monitoring"""
        load_factor = self.current_requests / self.max_concurrent_requests
        return {
            "enabled": ENABLE_BACKPRESSURE,
            "current_requests": self.current_requests,
            "max_concurrent_requests": self.max_concurrent_requests,
            "load_factor": round(load_factor, 3),
            "total_requests": self.total_requests,
            "shed_requests": self.shed_requests,
            "degraded_requests": self.degraded_requests,
            "bypassed_requests": self.bypassed_requests,
            "shed_rate": round(self.shed_requests / max(1, self.total_requests), 4),
            "degrade_rate": round(self.degraded_requests / max(1, self.total_requests), 4),
            "thresholds": {
                "shed": self.shed_threshold,
                "degrade": self.degrade_threshold
            }
        }


# Singleton for metrics access
_backpressure_middleware: BackpressureMiddleware = None


def get_backpressure_metrics() -> dict:
    """Get backpressure metrics (for /metrics endpoint)"""
    if _backpressure_middleware:
        return _backpressure_middleware.get_metrics()
    return {"enabled": False, "message": "Middleware not initialized"}


def set_backpressure_middleware(middleware: BackpressureMiddleware):
    """Set the middleware instance for metrics access"""
    global _backpressure_middleware
    _backpressure_middleware = middleware
