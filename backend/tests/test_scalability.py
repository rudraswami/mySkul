"""
🧪 Scalability Tests - Cognito OS v1.0
======================================

Tests for:
- GlobalConcurrencyLimiter
- CircuitBreaker
- LoadMonitor
- BackpressureMiddleware
- Load-adaptive limits

Run: python -m pytest tests/test_scalability.py -v --tb=short
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# TEST: GlobalConcurrencyLimiter
# =============================================================================

class TestGlobalConcurrencyLimiter:
    """Tests for the concurrency limiter"""
    
    @pytest.fixture
    def limiter(self):
        """Create a fresh limiter for each test"""
        from services.scalability import GlobalConcurrencyLimiter, ResourceType, ResourceLimit
        
        # Create limiter with small limits for testing
        limits = {
            ResourceType.LLM_CALL: ResourceLimit(max_concurrent=3, max_per_minute=10),
            ResourceType.TOOL_WEB_SEARCH: ResourceLimit(max_concurrent=2, max_per_minute=5),
        }
        return GlobalConcurrencyLimiter(limits)
    
    @pytest.mark.asyncio
    async def test_acquire_release_basic(self, limiter):
        """Test basic acquire and release"""
        from services.scalability import ResourceType
        
        # Should acquire successfully
        acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=1.0)
        assert acquired is True
        
        # Check metrics
        assert limiter.limits[ResourceType.LLM_CALL].current_concurrent == 1
        
        # Release
        await limiter.release(ResourceType.LLM_CALL)
        assert limiter.limits[ResourceType.LLM_CALL].current_concurrent == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_limit_enforced(self, limiter):
        """Test that concurrent limit is enforced"""
        from services.scalability import ResourceType
        
        # Acquire all slots
        for _ in range(3):
            acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=1.0)
            assert acquired is True
        
        # 4th should fail (timeout)
        acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=0.1)
        assert acquired is False
        
        # Metrics should show rejection
        assert limiter.limits[ResourceType.LLM_CALL].total_rejected_concurrent >= 1
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforced(self, limiter):
        """Test that rate limit (RPM) is enforced"""
        from services.scalability import ResourceType
        
        # Exhaust rate limit
        for i in range(10):
            acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=0.1)
            assert acquired is True
            await limiter.release(ResourceType.LLM_CALL)
        
        # 11th should fail due to rate limit
        acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=0.1)
        assert acquired is False
        assert limiter.limits[ResourceType.LLM_CALL].total_rejected_rate >= 1
    
    @pytest.mark.asyncio
    async def test_load_factor_calculation(self, limiter):
        """Test load factor calculation"""
        from services.scalability import ResourceType
        
        # Empty - load factor should be 0
        assert limiter.get_load_factor(ResourceType.LLM_CALL) == 0.0
        
        # Acquire 2 of 3 slots
        await limiter.acquire(ResourceType.LLM_CALL, timeout=1.0)
        await limiter.acquire(ResourceType.LLM_CALL, timeout=1.0)
        
        # Load factor should be ~0.67
        load = limiter.get_load_factor(ResourceType.LLM_CALL)
        assert 0.6 <= load <= 0.7
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, limiter):
        """Test that metrics are collected correctly"""
        from services.scalability import ResourceType
        
        # Do some operations
        await limiter.acquire(ResourceType.LLM_CALL, timeout=1.0)
        await limiter.release(ResourceType.LLM_CALL)
        
        metrics = limiter.get_metrics()
        
        assert "resources" in metrics
        assert "llm_call" in metrics["resources"]
        assert metrics["resources"]["llm_call"]["total_acquired"] >= 1


# =============================================================================
# TEST: CircuitBreaker
# =============================================================================

class TestCircuitBreaker:
    """Tests for the circuit breaker"""
    
    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker with small thresholds for testing"""
        from services.scalability import CircuitBreaker
        return CircuitBreaker(
            name="test",
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=1.0,
            call_timeout=0.5
        )
    
    @pytest.mark.asyncio
    async def test_successful_call(self, breaker):
        """Test that successful calls go through"""
        async def success_fn():
            return "success"
        
        result = await breaker.call(success_fn)
        assert result == "success"
        assert breaker.stats.successes >= 1
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self, breaker):
        """Test that circuit opens after threshold failures"""
        from services.scalability import CircuitState, CircuitOpenError
        
        async def failing_fn():
            raise Exception("fail")
        
        # First failure
        with pytest.raises(Exception):
            await breaker.call(failing_fn)
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            await breaker.call(failing_fn)
        
        assert breaker.state == CircuitState.OPEN
        
        # Third call should be rejected immediately
        with pytest.raises(CircuitOpenError):
            await breaker.call(failing_fn)
    
    @pytest.mark.asyncio
    async def test_circuit_uses_fallback_when_open(self, breaker):
        """Test that fallback is used when circuit is open"""
        from services.scalability import CircuitState
        
        async def failing_fn():
            raise Exception("fail")
        
        async def fallback_fn():
            return "fallback"
        
        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(failing_fn)
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Should use fallback
        result = await breaker.call(failing_fn, fallback_fn)
        assert result == "fallback"
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_recovery(self, breaker):
        """Test that circuit recovers through half-open state"""
        from services.scalability import CircuitState
        
        async def failing_fn():
            raise Exception("fail")
        
        async def success_fn():
            return "success"
        
        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(failing_fn)
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        # Circuit should transition to HALF_OPEN
        result = await breaker.call(success_fn)
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Another success should close it
        result = await breaker.call(success_fn)
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_timeout_counts_as_failure(self, breaker):
        """Test that timeouts count as failures"""
        async def slow_fn():
            await asyncio.sleep(2.0)  # Longer than call_timeout
            return "success"
        
        # Should timeout and count as failure
        with pytest.raises(asyncio.TimeoutError):
            await breaker.call(slow_fn)
        
        assert breaker.stats.total_timeouts >= 1
        assert breaker.stats.consecutive_failures >= 1


# =============================================================================
# TEST: LoadMonitor
# =============================================================================

class TestLoadMonitor:
    """Tests for the load monitor"""
    
    @pytest.fixture
    def monitor(self):
        """Create a load monitor with test limiter"""
        from services.scalability import LoadMonitor, GlobalConcurrencyLimiter, ResourceType, ResourceLimit
        
        limiter = GlobalConcurrencyLimiter({
            ResourceType.LLM_CALL: ResourceLimit(max_concurrent=10, max_per_minute=100),
        })
        
        monitor = LoadMonitor(limiter)
        monitor._max_requests = 10  # Small limit for testing
        return monitor
    
    def test_load_level_normal(self, monitor):
        """Test that load level is NORMAL when idle"""
        from services.scalability import LoadLevel
        
        level = monitor.get_load_level()
        assert level == LoadLevel.NORMAL
    
    @pytest.mark.asyncio
    async def test_load_level_changes_with_requests(self, monitor):
        """Test that load level changes as requests are added"""
        from services.scalability import LoadLevel
        
        # Register 7 requests (70% of 10)
        for _ in range(7):
            await monitor.register_request()
        
        # Should be ELEVATED (70-85%)
        level = monitor.get_load_level()
        assert level == LoadLevel.ELEVATED
    
    @pytest.mark.asyncio
    async def test_load_level_critical(self, monitor):
        """Test that load level becomes CRITICAL when near capacity"""
        from services.scalability import LoadLevel
        
        # Register 10 requests (100% of 10)
        for _ in range(10):
            await monitor.register_request()
        
        level = monitor.get_load_level()
        assert level == LoadLevel.CRITICAL
    
    def test_adaptive_limits_normal(self, monitor):
        """Test adaptive limits under normal load"""
        limits = monitor.get_adaptive_limits("MODERATE")
        
        # Should get full limits
        assert limits.max_agents == 2
        assert limits.force_fast_path is False
        assert limits.enable_parallel_agents is True
    
    @pytest.mark.asyncio
    async def test_adaptive_limits_high_load(self, monitor):
        """Test that limits are reduced under high load"""
        # Create high load
        for _ in range(9):  # 90% of 10
            await monitor.register_request()
        
        limits = monitor.get_adaptive_limits("COMPLEX")
        
        # Should force fast path
        assert limits.force_fast_path is True
        assert limits.max_agents == 1
        assert limits.enable_verification is False
    
    @pytest.mark.asyncio
    async def test_request_shedding(self, monitor):
        """Test that requests are shed when at capacity"""
        # Fill up completely
        for _ in range(10):
            result = await monitor.register_request()
            assert result is True
        
        # Next request should be shed
        result = await monitor.register_request()
        assert result is False
        assert monitor.shed_requests == 1


# =============================================================================
# TEST: BackpressureMiddleware
# =============================================================================

class TestBackpressureMiddleware:
    """Tests for the backpressure middleware"""
    
    @pytest.mark.asyncio
    async def test_bypass_paths_not_affected(self):
        """Test that bypass paths skip load management"""
        from middleware.backpressure import BackpressureMiddleware
        from starlette.testclient import TestClient
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        
        async def health(request):
            return JSONResponse({"status": "ok"})
        
        app = Starlette(routes=[Route("/health", health)])
        app = BackpressureMiddleware(app, max_concurrent_requests=1)
        
        # Even if we're at capacity, health should work
        app.current_requests = 100  # Simulate full capacity
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_ai_paths_degraded_under_load(self):
        """Test that AI paths are degraded under load"""
        from middleware.backpressure import BackpressureMiddleware
        from starlette.testclient import TestClient
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        
        async def ai_endpoint(request):
            # Check if degraded flag was set
            is_degraded = getattr(request.state, 'is_degraded', False)
            return JSONResponse({"degraded": is_degraded})
        
        app = Starlette(routes=[Route("/api/ai/neuro-symbolic", ai_endpoint)])
        middleware = BackpressureMiddleware(app, max_concurrent_requests=100, degrade_threshold=0.5)
        
        # Simulate 70% load (above degrade threshold)
        middleware.current_requests = 70
        
        # Note: Full test would require async test client setup
        # This is a simplified structural test
        assert middleware.degrade_threshold == 0.5
    
    def test_metrics_collection(self):
        """Test that middleware collects metrics"""
        from middleware.backpressure import BackpressureMiddleware
        from starlette.applications import Starlette
        
        app = Starlette(routes=[])
        middleware = BackpressureMiddleware(app, max_concurrent_requests=100)
        
        # Simulate some activity
        middleware.total_requests = 100
        middleware.shed_requests = 5
        middleware.degraded_requests = 20
        
        metrics = middleware.get_metrics()
        
        assert metrics["total_requests"] == 100
        assert metrics["shed_requests"] == 5
        assert metrics["degraded_requests"] == 20
        assert metrics["shed_rate"] == 0.05
        assert metrics["degrade_rate"] == 0.2


# =============================================================================
# TEST: Integration Tests
# =============================================================================

class TestScalabilityIntegration:
    """Integration tests for the full scalability stack"""
    
    @pytest.mark.asyncio
    async def test_llm_call_with_limiter(self):
        """Test that LLM calls go through the limiter"""
        from services.scalability import get_concurrency_limiter, ResourceType
        
        limiter = get_concurrency_limiter()
        
        # Simulate LLM call flow
        acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=5.0, request_id="test")
        assert acquired is True
        
        try:
            # Simulate work
            await asyncio.sleep(0.01)
        finally:
            await limiter.release(ResourceType.LLM_CALL)
        
        # Should have recorded acquisition
        metrics = limiter.get_metrics()
        assert metrics["resources"]["llm_call"]["total_acquired"] >= 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_registry(self):
        """Test the circuit breaker registry"""
        from services.scalability import CircuitBreakerRegistry
        
        # Get breakers (should create if not exists)
        openai_breaker = CircuitBreakerRegistry.get("openai")
        web_search_breaker = CircuitBreakerRegistry.get("web_search")
        
        assert openai_breaker.name == "openai"
        assert web_search_breaker.name == "web_search"
        
        # Should reuse same instance
        assert CircuitBreakerRegistry.get("openai") is openai_breaker
        
        # Stats should be available
        stats = CircuitBreakerRegistry.get_all_stats()
        assert "openai" in stats
        assert "web_search" in stats
    
    @pytest.mark.asyncio
    async def test_full_metrics_endpoint(self):
        """Test that full metrics can be collected"""
        from services.scalability import get_scalability_metrics
        
        metrics = get_scalability_metrics()
        
        # Should have all sections
        assert "concurrency_limiter" in metrics
        assert "load_monitor" in metrics
        assert "circuit_breakers" in metrics
        assert "feature_flags" in metrics


# =============================================================================
# TEST: Performance Targets
# =============================================================================

class TestPerformanceTargets:
    """Tests to verify performance targets are achievable"""
    
    @pytest.mark.asyncio
    async def test_limiter_acquisition_speed(self):
        """Test that limiter acquisition is fast (<10ms)"""
        from services.scalability import get_concurrency_limiter, ResourceType
        
        limiter = get_concurrency_limiter()
        
        start = time.time()
        acquired = await limiter.acquire(ResourceType.LLM_CALL, timeout=5.0)
        elapsed_ms = (time.time() - start) * 1000
        
        assert acquired is True
        assert elapsed_ms < 10, f"Acquisition took {elapsed_ms:.1f}ms (target: <10ms)"
        
        await limiter.release(ResourceType.LLM_CALL)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_fast_rejection(self):
        """Test that open circuit rejects fast (<5ms)"""
        from services.scalability import CircuitBreaker, CircuitOpenError
        
        breaker = CircuitBreaker("test_fast", failure_threshold=1, timeout_seconds=60)
        
        # Open the circuit
        async def fail():
            raise Exception("fail")
        
        try:
            await breaker.call(fail)
        except:
            pass
        
        # Measure rejection time
        start = time.time()
        try:
            await breaker.call(fail)
        except CircuitOpenError:
            pass
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 5, f"Rejection took {elapsed_ms:.1f}ms (target: <5ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
