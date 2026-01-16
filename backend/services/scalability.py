"""
🚀 Scalability Infrastructure - Cognito OS v1.0
================================================

Enterprise-grade scalability components:
- GlobalConcurrencyLimiter: Server-wide resource limits (LLM, tools, agents)
- CircuitBreaker: Fault tolerance for external services
- LoadMonitor: Real-time load tracking and adaptive limits

DESIGN PRINCIPLES:
1. Never block - reject fast when overloaded
2. Graceful degradation - reduce features under load, don't fail
3. Observable - all operations emit metrics
4. Zero-allocation hot path - pre-allocated semaphores

FEATURE FLAGS:
- ENABLE_CONCURRENCY_LIMITER: Enable/disable limiter (default: true)
- ENABLE_CIRCUIT_BREAKER: Enable/disable circuit breakers (default: true)
- MAX_CONCURRENT_REQUESTS: Server-wide request limit (default: 200)
- LLM_MAX_CONCURRENT: Max concurrent LLM calls (default: 50)
- LLM_MAX_RPM: Max LLM calls per minute (default: 500)
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class CircuitOpenError(Exception):
    """Raised when circuit breaker is OPEN and no fallback is provided"""
    pass


class ResourceLimitExceeded(Exception):
    """Raised when concurrency limit is exceeded"""
    pass


# =============================================================================
# FEATURE FLAGS
# =============================================================================

ENABLE_CONCURRENCY_LIMITER = os.getenv("ENABLE_CONCURRENCY_LIMITER", "true").lower() == "true"
ENABLE_CIRCUIT_BREAKER = os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"

# =============================================================================
# RESOURCE TYPES
# =============================================================================

class ResourceType(Enum):
    """Types of limited resources"""
    LLM_CALL = "llm_call"
    AGENT_EXECUTION = "agent_execution"
    TOOL_WEB_SEARCH = "tool_web_search"
    TOOL_KNOWLEDGE = "tool_knowledge"
    TOOL_CALCULATOR = "tool_calculator"
    DB_CONNECTION = "db_connection"


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CircuitStats:
    """Statistics for a circuit breaker"""
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0
    last_success_time: float = 0
    total_calls: int = 0
    total_timeouts: int = 0
    consecutive_failures: int = 0


class CircuitBreaker:
    """
    Circuit breaker for external service calls.
    
    States:
    - CLOSED: Normal operation, calls go through
    - OPEN: Too many failures, calls rejected immediately (fail-fast)
    - HALF_OPEN: Testing if service recovered
    
    Usage:
        breaker = CircuitBreaker("openai", failure_threshold=5)
        result = await breaker.call(async_function, fallback_fn, *args, **kwargs)
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 30.0,
        call_timeout: float = 20.0
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.call_timeout = call_timeout
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._lock = asyncio.Lock()
        
        logger.info(f"⚡ CircuitBreaker '{name}' initialized (threshold={failure_threshold})")
    
    async def call(
        self,
        fn: Callable,
        fallback: Callable = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            fn: Async function to call
            fallback: Fallback function if circuit is open or call fails
            *args, **kwargs: Arguments for fn
        
        Returns:
            Result from fn or fallback
        
        Raises:
            CircuitOpenError if open and no fallback provided
        """
        if not ENABLE_CIRCUIT_BREAKER:
            return await fn(*args, **kwargs)
        
        async with self._lock:
            self.stats.total_calls += 1
            
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if time.time() - self.stats.last_failure_time > self.timeout_seconds:
                    logger.info(f"🔄 Circuit '{self.name}': OPEN → HALF_OPEN (testing)")
                    self.state = CircuitState.HALF_OPEN
                    self.stats.consecutive_failures = 0
                else:
                    # Still open, use fallback or reject
                    logger.warning(f"⛔ Circuit '{self.name}': OPEN, rejecting call")
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit '{self.name}' is OPEN")
        
        # Execute the call
        try:
            result = await asyncio.wait_for(
                fn(*args, **kwargs),
                timeout=self.call_timeout
            )
            await self._record_success()
            return result
            
        except asyncio.TimeoutError:
            self.stats.total_timeouts += 1
            await self._record_failure("timeout")
            if fallback:
                return await fallback(*args, **kwargs)
            raise
            
        except Exception as e:
            await self._record_failure(str(e))
            if fallback:
                return await fallback(*args, **kwargs)
            raise
    
    async def _record_success(self):
        """Record a successful call"""
        async with self._lock:
            self.stats.successes += 1
            self.stats.last_success_time = time.time()
            self.stats.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                # Count successes in half-open state
                if self.stats.successes >= self.success_threshold:
                    logger.info(f"✅ Circuit '{self.name}': HALF_OPEN → CLOSED (recovered)")
                    self.state = CircuitState.CLOSED
                    self.stats.failures = 0
    
    async def _record_failure(self, reason: str = ""):
        """Record a failed call"""
        async with self._lock:
            self.stats.failures += 1
            self.stats.consecutive_failures += 1
            self.stats.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(f"❌ Circuit '{self.name}': HALF_OPEN → OPEN (still failing: {reason})")
                self.state = CircuitState.OPEN
                self.stats.successes = 0
                
            elif self.state == CircuitState.CLOSED:
                if self.stats.consecutive_failures >= self.failure_threshold:
                    logger.warning(f"🔴 Circuit '{self.name}': CLOSED → OPEN ({self.stats.consecutive_failures} failures)")
                    self.state = CircuitState.OPEN
                    self.stats.successes = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.stats.failures,
            "successes": self.stats.successes,
            "consecutive_failures": self.stats.consecutive_failures,
            "total_calls": self.stats.total_calls,
            "total_timeouts": self.stats.total_timeouts,
            "last_failure": self.stats.last_failure_time,
            "last_success": self.stats.last_success_time
        }
    
    def is_available(self) -> bool:
        """Check if circuit is available for calls"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.stats.last_failure_time > self.timeout_seconds:
                return True  # Will transition to half-open
            return False
        return True


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# =============================================================================
# GLOBAL CONCURRENCY LIMITER
# =============================================================================

@dataclass
class ResourceLimit:
    """Configuration for a single resource limit"""
    max_concurrent: int
    max_per_minute: int
    current_concurrent: int = 0
    minute_count: int = 0
    minute_start: float = field(default_factory=time.time)
    _semaphore: asyncio.Semaphore = None
    
    # Metrics
    total_acquired: int = 0
    total_rejected_concurrent: int = 0
    total_rejected_rate: int = 0
    total_wait_time_ms: float = 0
    
    @property
    def semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore


class GlobalConcurrencyLimiter:
    """
    Server-wide concurrency limiter to prevent resource exhaustion.
    
    Features:
    - Per-resource semaphores (concurrent limit)
    - Per-resource rate limiting (RPM limit)
    - Wait timeout with rejection
    - Metrics for monitoring
    
    Usage:
        limiter = get_concurrency_limiter()
        if await limiter.acquire(ResourceType.LLM_CALL, timeout=5.0):
            try:
                # Do LLM call
            finally:
                await limiter.release(ResourceType.LLM_CALL)
    """
    
    # Default limits - tune based on API tier and server capacity
    DEFAULT_LIMITS = {
        ResourceType.LLM_CALL: ResourceLimit(
            max_concurrent=int(os.getenv("LLM_MAX_CONCURRENT", "50")),
            max_per_minute=int(os.getenv("LLM_MAX_RPM", "500"))
        ),
        ResourceType.AGENT_EXECUTION: ResourceLimit(
            max_concurrent=int(os.getenv("AGENT_MAX_CONCURRENT", "100")),
            max_per_minute=int(os.getenv("AGENT_MAX_RPM", "1000"))
        ),
        ResourceType.TOOL_WEB_SEARCH: ResourceLimit(
            max_concurrent=int(os.getenv("WEB_SEARCH_MAX_CONCURRENT", "10")),
            max_per_minute=int(os.getenv("WEB_SEARCH_MAX_RPM", "60"))
        ),
        ResourceType.TOOL_KNOWLEDGE: ResourceLimit(
            max_concurrent=int(os.getenv("KNOWLEDGE_MAX_CONCURRENT", "30")),
            max_per_minute=int(os.getenv("KNOWLEDGE_MAX_RPM", "300"))
        ),
        ResourceType.TOOL_CALCULATOR: ResourceLimit(
            max_concurrent=50,
            max_per_minute=1000  # Calculator is cheap
        ),
        ResourceType.DB_CONNECTION: ResourceLimit(
            max_concurrent=int(os.getenv("DB_MAX_CONCURRENT", "40")),
            max_per_minute=2000
        )
    }
    
    def __init__(self, limits: Dict[ResourceType, ResourceLimit] = None):
        self.limits = limits or {k: ResourceLimit(v.max_concurrent, v.max_per_minute) 
                                  for k, v in self.DEFAULT_LIMITS.items()}
        self._lock = asyncio.Lock()
        self._initialized = False
        
        logger.info("🚀 GlobalConcurrencyLimiter initialized")
        for resource, limit in self.limits.items():
            logger.info(f"   ├── {resource.value}: {limit.max_concurrent} concurrent, {limit.max_per_minute} RPM")
    
    async def acquire(
        self,
        resource: ResourceType,
        timeout: float = 5.0,
        request_id: str = None
    ) -> bool:
        """
        Acquire a resource slot.
        
        Args:
            resource: Type of resource to acquire
            timeout: Max time to wait for slot (seconds)
            request_id: For logging
        
        Returns:
            True if acquired, False if rejected
        """
        if not ENABLE_CONCURRENCY_LIMITER:
            return True
        
        limit = self.limits.get(resource)
        if not limit:
            return True
        
        start = time.time()
        
        # Check rate limit (RPM)
        async with self._lock:
            now = time.time()
            if now - limit.minute_start >= 60:
                # Reset minute counter
                limit.minute_count = 0
                limit.minute_start = now
            
            if limit.minute_count >= limit.max_per_minute:
                limit.total_rejected_rate += 1
                logger.warning(
                    f"[{request_id}] 🚫 Rate limit: {resource.value} "
                    f"({limit.minute_count}/{limit.max_per_minute} RPM)"
                )
                return False
        
        # Try to acquire semaphore (concurrent limit)
        try:
            acquired = await asyncio.wait_for(
                limit.semaphore.acquire(),
                timeout=timeout
            )
            
            if acquired:
                async with self._lock:
                    limit.current_concurrent += 1
                    limit.minute_count += 1
                    limit.total_acquired += 1
                    
                wait_ms = (time.time() - start) * 1000
                limit.total_wait_time_ms += wait_ms
                
                if wait_ms > 100:
                    logger.debug(f"[{request_id}] ⏳ Slow acquire: {resource.value} ({wait_ms:.0f}ms)")
                
                return True
                
        except asyncio.TimeoutError:
            async with self._lock:
                limit.total_rejected_concurrent += 1
            logger.warning(
                f"[{request_id}] ⛔ Concurrency limit: {resource.value} "
                f"({limit.current_concurrent}/{limit.max_concurrent})"
            )
            return False
        
        return False
    
    async def release(self, resource: ResourceType):
        """Release a resource slot"""
        if not ENABLE_CONCURRENCY_LIMITER:
            return
        
        limit = self.limits.get(resource)
        if not limit:
            return
        
        limit.semaphore.release()
        async with self._lock:
            limit.current_concurrent = max(0, limit.current_concurrent - 1)
    
    def get_load_factor(self, resource: ResourceType = None) -> float:
        """
        Get current load factor (0.0 to 1.0).
        If resource is None, returns average across all resources.
        """
        if resource:
            limit = self.limits.get(resource)
            if limit:
                return limit.current_concurrent / limit.max_concurrent
            return 0.0
        
        # Average load across all resources
        total_load = sum(
            limit.current_concurrent / limit.max_concurrent
            for limit in self.limits.values()
        )
        return total_load / len(self.limits)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics for monitoring"""
        return {
            "resources": {
                resource.value: {
                    "current_concurrent": limit.current_concurrent,
                    "max_concurrent": limit.max_concurrent,
                    "minute_count": limit.minute_count,
                    "max_per_minute": limit.max_per_minute,
                    "load_factor": limit.current_concurrent / limit.max_concurrent,
                    "total_acquired": limit.total_acquired,
                    "total_rejected_concurrent": limit.total_rejected_concurrent,
                    "total_rejected_rate": limit.total_rejected_rate,
                    "avg_wait_ms": (limit.total_wait_time_ms / max(1, limit.total_acquired))
                }
                for resource, limit in self.limits.items()
            },
            "overall_load_factor": self.get_load_factor()
        }


# =============================================================================
# LOAD MONITOR
# =============================================================================

class LoadLevel(Enum):
    """Server load levels for adaptive behavior"""
    NORMAL = "normal"       # < 50% - Full features
    ELEVATED = "elevated"   # 50-70% - Reduce parallel agents
    HIGH = "high"          # 70-85% - Force fast path
    CRITICAL = "critical"   # > 85% - Shed load


@dataclass
class LoadAdaptiveLimits:
    """Limits adjusted based on current load"""
    max_agents: int
    max_llm_calls: int
    max_tool_calls: int
    max_iterations: int
    force_fast_path: bool
    enable_verification: bool
    enable_parallel_agents: bool


class LoadMonitor:
    """
    Real-time load monitoring with adaptive limits.
    
    Monitors server load and adjusts behavior:
    - NORMAL: Full features
    - ELEVATED: Reduce agent count
    - HIGH: Force fast path for new requests
    - CRITICAL: Reject new requests (503)
    """
    
    THRESHOLDS = {
        LoadLevel.NORMAL: 0.50,
        LoadLevel.ELEVATED: 0.70,
        LoadLevel.HIGH: 0.85,
        LoadLevel.CRITICAL: 0.95
    }
    
    # Base limits per complexity
    BASE_LIMITS = {
        'TRIVIAL': LoadAdaptiveLimits(1, 1, 0, 1, True, False, False),
        'SIMPLE': LoadAdaptiveLimits(1, 2, 1, 2, True, False, False),
        'MODERATE': LoadAdaptiveLimits(2, 6, 2, 3, False, True, True),
        'COMPLEX': LoadAdaptiveLimits(3, 10, 3, 5, False, True, True),
        'DEEP_REASONING': LoadAdaptiveLimits(3, 15, 4, 7, False, True, True)
    }
    
    def __init__(self, limiter: GlobalConcurrencyLimiter):
        self.limiter = limiter
        self._current_requests = 0
        self._max_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "200"))
        self._lock = asyncio.Lock()
        
        # Metrics
        self.total_requests = 0
        self.shed_requests = 0
        self.degraded_requests = 0
    
    def get_load_level(self) -> LoadLevel:
        """Get current load level"""
        load = self.limiter.get_load_factor()
        request_load = self._current_requests / self._max_requests
        
        # Use max of resource load and request load
        effective_load = max(load, request_load)
        
        if effective_load >= self.THRESHOLDS[LoadLevel.CRITICAL]:
            return LoadLevel.CRITICAL
        elif effective_load >= self.THRESHOLDS[LoadLevel.HIGH]:
            return LoadLevel.HIGH
        elif effective_load >= self.THRESHOLDS[LoadLevel.ELEVATED]:
            return LoadLevel.ELEVATED
        return LoadLevel.NORMAL
    
    def get_adaptive_limits(self, complexity: str) -> LoadAdaptiveLimits:
        """
        Get limits adjusted for current load.
        
        Args:
            complexity: Query complexity (TRIVIAL, SIMPLE, MODERATE, COMPLEX, DEEP_REASONING)
        
        Returns:
            Adjusted limits based on current load
        """
        base = self.BASE_LIMITS.get(complexity, self.BASE_LIMITS['SIMPLE'])
        load_level = self.get_load_level()
        
        if load_level == LoadLevel.NORMAL:
            return base
        
        elif load_level == LoadLevel.ELEVATED:
            # Reduce agents by 1, disable parallel
            return LoadAdaptiveLimits(
                max_agents=max(1, base.max_agents - 1),
                max_llm_calls=max(2, base.max_llm_calls - 2),
                max_tool_calls=max(1, base.max_tool_calls - 1),
                max_iterations=max(2, base.max_iterations - 1),
                force_fast_path=False,
                enable_verification=base.enable_verification,
                enable_parallel_agents=False  # Sequential under elevated load
            )
        
        elif load_level == LoadLevel.HIGH:
            # Force fast path, single agent
            return LoadAdaptiveLimits(
                max_agents=1,
                max_llm_calls=2,
                max_tool_calls=1,
                max_iterations=2,
                force_fast_path=True,
                enable_verification=False,
                enable_parallel_agents=False
            )
        
        else:  # CRITICAL
            # Minimal processing
            return LoadAdaptiveLimits(
                max_agents=1,
                max_llm_calls=1,
                max_tool_calls=0,
                max_iterations=1,
                force_fast_path=True,
                enable_verification=False,
                enable_parallel_agents=False
            )
    
    async def register_request(self) -> bool:
        """
        Register a new request. Returns False if should be shed.
        """
        async with self._lock:
            self.total_requests += 1
            
            if self._current_requests >= self._max_requests:
                self.shed_requests += 1
                return False
            
            self._current_requests += 1
            return True
    
    async def unregister_request(self):
        """Unregister a completed request"""
        async with self._lock:
            self._current_requests = max(0, self._current_requests - 1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get load monitor metrics"""
        return {
            "current_requests": self._current_requests,
            "max_requests": self._max_requests,
            "request_load_factor": self._current_requests / self._max_requests,
            "resource_load_factor": self.limiter.get_load_factor(),
            "load_level": self.get_load_level().value,
            "total_requests": self.total_requests,
            "shed_requests": self.shed_requests,
            "degraded_requests": self.degraded_requests,
            "shed_rate": self.shed_requests / max(1, self.total_requests)
        }


# =============================================================================
# CIRCUIT BREAKER REGISTRY
# =============================================================================

class CircuitBreakerRegistry:
    """
    Registry of circuit breakers for different services.
    Provides pre-configured breakers for common services.
    """
    
    _breakers: Dict[str, CircuitBreaker] = {}
    _lock = asyncio.Lock()
    
    # Pre-configured settings per service
    CONFIGS = {
        'openai': {
            'failure_threshold': 5,
            'success_threshold': 3,
            'timeout_seconds': 30.0,
            'call_timeout': 25.0
        },
        'gemini': {
            'failure_threshold': 5,
            'success_threshold': 3,
            'timeout_seconds': 30.0,
            'call_timeout': 25.0
        },
        'web_search': {
            'failure_threshold': 3,
            'success_threshold': 2,
            'timeout_seconds': 60.0,
            'call_timeout': 3.0
        },
        'mongodb': {
            'failure_threshold': 10,
            'success_threshold': 5,
            'timeout_seconds': 15.0,
            'call_timeout': 5.0
        },
        'default': {
            'failure_threshold': 5,
            'success_threshold': 2,
            'timeout_seconds': 30.0,
            'call_timeout': 10.0
        }
    }
    
    @classmethod
    def get(cls, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker by name"""
        if name not in cls._breakers:
            config = cls.CONFIGS.get(name, cls.CONFIGS['default'])
            cls._breakers[name] = CircuitBreaker(name, **config)
        return cls._breakers[name]
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Any]:
        """Get stats for all circuit breakers"""
        return {
            name: breaker.get_stats()
            for name, breaker in cls._breakers.items()
        }


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

_concurrency_limiter: Optional[GlobalConcurrencyLimiter] = None
_load_monitor: Optional[LoadMonitor] = None


def get_concurrency_limiter() -> GlobalConcurrencyLimiter:
    """Get or create the global concurrency limiter"""
    global _concurrency_limiter
    if _concurrency_limiter is None:
        _concurrency_limiter = GlobalConcurrencyLimiter()
    return _concurrency_limiter


def get_load_monitor() -> LoadMonitor:
    """Get or create the load monitor"""
    global _load_monitor
    if _load_monitor is None:
        _load_monitor = LoadMonitor(get_concurrency_limiter())
    return _load_monitor


def reset_singletons():
    """Reset singletons (for testing or worker fork)"""
    global _concurrency_limiter, _load_monitor
    _concurrency_limiter = None
    _load_monitor = None


# =============================================================================
# DECORATOR HELPERS
# =============================================================================

def with_concurrency_limit(resource: ResourceType, timeout: float = 5.0):
    """
    Decorator to apply concurrency limit to an async function.
    
    Usage:
        @with_concurrency_limit(ResourceType.LLM_CALL)
        async def call_openai(prompt):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            limiter = get_concurrency_limiter()
            request_id = kwargs.get('request_id', 'unknown')
            
            if not await limiter.acquire(resource, timeout=timeout, request_id=request_id):
                raise ResourceLimitExceeded(f"Concurrency limit exceeded for {resource.value}")
            
            try:
                return await fn(*args, **kwargs)
            finally:
                await limiter.release(resource)
        
        return wrapper
    return decorator


def with_circuit_breaker(service_name: str, fallback: Callable = None):
    """
    Decorator to apply circuit breaker to an async function.
    
    Usage:
        @with_circuit_breaker('openai', fallback=fallback_fn)
        async def call_openai(prompt):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            breaker = CircuitBreakerRegistry.get(service_name)
            return await breaker.call(fn, fallback, *args, **kwargs)
        return wrapper
    return decorator


class ResourceLimitExceeded(Exception):
    """Raised when resource limit is exceeded"""
    pass


# =============================================================================
# METRICS ENDPOINT DATA
# =============================================================================

def get_scalability_metrics() -> Dict[str, Any]:
    """Get all scalability metrics for the /metrics endpoint"""
    return {
        "concurrency_limiter": get_concurrency_limiter().get_metrics(),
        "load_monitor": get_load_monitor().get_metrics(),
        "circuit_breakers": CircuitBreakerRegistry.get_all_stats(),
        "feature_flags": {
            "concurrency_limiter_enabled": ENABLE_CONCURRENCY_LIMITER,
            "circuit_breaker_enabled": ENABLE_CIRCUIT_BREAKER
        }
    }
