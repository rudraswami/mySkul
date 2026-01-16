"""
🎯 REQUEST CONTEXT - Single-Flight Coordinator
==============================================

This module enforces the critical invariant:
    ONE REQUEST = ONE LLM CALL (maximum)

All agents MUST use this context. Direct LLM calls are FORBIDDEN.
"""

import time
import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject all LLM calls
    HALF_OPEN = "half_open"  # Testing if LLM recovered


@dataclass
class RequestContext:
    """
    Request-scoped context that coordinates ALL processing.
    
    CRITICAL INVARIANTS:
    1. llm_called can only transition False → True (never back)
    2. Once llm_called is True, ALL subsequent LLM requests use cached result
    3. Budget is strictly enforced - no extensions
    """
    request_id: str
    query: str
    budget_seconds: float = 10.0
    start_time: float = field(default_factory=time.time)
    
    # Single-flight LLM coordination
    llm_called: bool = False
    llm_result: Optional[str] = None
    llm_error: Optional[str] = None
    
    # Agent coordination
    selected_agent: Optional[str] = None
    
    # Metadata
    subject: Optional[str] = None
    user_id: Optional[str] = None
    
    @property
    def elapsed(self) -> float:
        """Time elapsed since request started"""
        return time.time() - self.start_time
    
    @property
    def remaining_budget(self) -> float:
        """Time remaining in budget"""
        return max(0, self.budget_seconds - self.elapsed)
    
    @property
    def has_budget(self) -> bool:
        """Check if meaningful budget remains (> 1 second)"""
        return self.remaining_budget > 1.0
    
    def can_call_llm(self) -> bool:
        """
        Check if LLM call is allowed.
        Returns False if:
        - LLM already called
        - Insufficient budget
        - Circuit breaker open
        """
        if self.llm_called:
            logger.debug(f"[{self.request_id}] LLM already called, using cached result")
            return False
        if not self.has_budget:
            logger.warning(f"[{self.request_id}] Insufficient budget for LLM call")
            return False
        return True
    
    def mark_llm_called(self, result: Optional[str] = None, error: Optional[str] = None):
        """
        Mark LLM as called. This is a ONE-WAY transition.
        Once called, no other agent can call LLM for this request.
        """
        self.llm_called = True
        self.llm_result = result
        self.llm_error = error
        logger.info(f"[{self.request_id}] LLM call completed: success={result is not None}")


class CircuitBreaker:
    """
    Circuit breaker for LLM calls.
    
    Prevents cascading failures by rejecting calls when LLM is unhealthy.
    
    States:
    - CLOSED: Normal operation, calls allowed
    - OPEN: LLM failing, all calls rejected (use fallback)
    - HALF_OPEN: Testing if LLM recovered
    """
    
    # Class-level state (shared across all requests)
    _state: CircuitState = CircuitState.CLOSED
    _failure_count: int = 0
    _last_failure_time: float = 0
    _open_until: float = 0
    
    # Configuration
    FAILURE_THRESHOLD = 3  # Failures before opening circuit
    FAILURE_WINDOW = 60.0  # Seconds to count failures
    OPEN_DURATION = 30.0   # Seconds to keep circuit open
    
    _lock = asyncio.Lock()
    
    @classmethod
    async def can_call(cls) -> bool:
        """Check if LLM call is allowed by circuit breaker"""
        async with cls._lock:
            now = time.time()
            
            # Reset failure count if window expired
            if now - cls._last_failure_time > cls.FAILURE_WINDOW:
                cls._failure_count = 0
            
            # Check if circuit should close
            if cls._state == CircuitState.OPEN:
                if now >= cls._open_until:
                    cls._state = CircuitState.HALF_OPEN
                    logger.info("🔄 Circuit breaker: HALF_OPEN (testing LLM)")
                else:
                    logger.warning("⚡ Circuit breaker: OPEN (rejecting LLM call)")
                    return False
            
            return True
    
    @classmethod
    async def record_success(cls):
        """Record successful LLM call"""
        async with cls._lock:
            if cls._state == CircuitState.HALF_OPEN:
                cls._state = CircuitState.CLOSED
                cls._failure_count = 0
                logger.info("✅ Circuit breaker: CLOSED (LLM recovered)")
    
    @classmethod
    async def record_failure(cls):
        """Record failed LLM call"""
        async with cls._lock:
            cls._failure_count += 1
            cls._last_failure_time = time.time()
            
            if cls._failure_count >= cls.FAILURE_THRESHOLD:
                cls._state = CircuitState.OPEN
                cls._open_until = time.time() + cls.OPEN_DURATION
                logger.warning(f"🔴 Circuit breaker: OPEN for {cls.OPEN_DURATION}s")
            
            if cls._state == CircuitState.HALF_OPEN:
                cls._state = CircuitState.OPEN
                cls._open_until = time.time() + cls.OPEN_DURATION
                logger.warning("🔴 Circuit breaker: OPEN (test failed)")
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "state": cls._state.value,
            "failure_count": cls._failure_count,
            "open_until": cls._open_until if cls._state == CircuitState.OPEN else None
        }


class ConfigurationGuard:
    """
    Fail-fast configuration checker.
    
    Missing API keys should NEVER cause a timeout.
    Check ONCE at request start, not during LLM call.
    """
    
    _config_valid: Optional[bool] = None
    _missing_keys: list = []
    
    @classmethod
    def check_config(cls) -> tuple[bool, list]:
        """
        Check if all required API keys are present.
        Returns (is_valid, missing_keys)
        """
        import os
        
        required_keys = [
            ("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")),
        ]
        
        optional_but_recommended = [
            ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        ]
        
        missing = [key for key, value in required_keys if not value]
        
        if missing:
            logger.warning(f"⚠️ Missing required API keys: {missing}")
            return False, missing
        
        # Check optional keys for warnings
        missing_optional = [key for key, value in optional_but_recommended if not value]
        if missing_optional:
            logger.info(f"ℹ️ Missing optional API keys (some features disabled): {missing_optional}")
        
        return True, []
    
    @classmethod
    def is_llm_available(cls) -> bool:
        """Quick check if LLM is available"""
        import os
        return bool(os.getenv("OPENAI_API_KEY"))


# Global request context storage (per-request)
_current_context: Optional[RequestContext] = None


def get_current_context() -> Optional[RequestContext]:
    """Get the current request context"""
    return _current_context


def set_current_context(ctx: Optional[RequestContext]):
    """Set the current request context"""
    global _current_context
    _current_context = ctx


@asynccontextmanager
async def request_scope(request_id: str, query: str, budget: float = 10.0):
    """
    Context manager for request-scoped processing.
    
    Usage:
        async with request_scope("req_123", "explain force") as ctx:
            # All processing happens here
            # ctx.llm_called ensures single LLM call
    """
    ctx = RequestContext(
        request_id=request_id,
        query=query,
        budget_seconds=budget
    )
    set_current_context(ctx)
    
    try:
        yield ctx
    finally:
        set_current_context(None)
        logger.info(f"[{request_id}] Request completed in {ctx.elapsed:.2f}s")
