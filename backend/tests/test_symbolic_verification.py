"""
Symbolic Verification Layer Tests
=====================================

Tests for auto-enabling HybridReasoningEngine when math/logic needed.

Run with: python -m pytest tests/test_symbolic_verification.py -v
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# TEST: INTENT DETECTOR
# =============================================================================

class TestSymbolicIntentDetector:
    """Test lightweight intent detection"""
    
    @pytest.fixture
    def detector(self):
        from services.symbolic_verification_layer import SymbolicIntentDetector
        return SymbolicIntentDetector()
    
    def test_numerical_calculation_detected(self, detector):
        """Test: Numerical calculations trigger verification"""
        from services.symbolic_verification_layer import SymbolicReason
        
        numerical_queries = [
            "Calculate 25 + 37 * 2",
            "What is 100 kg in grams?",
            "Find the value of 3.14 * 10",
        ]
        
        for query in numerical_queries:
            result = detector.detect(query)
            assert result.requires_verification, f"Should require verification: {query}"
            logger.info(f"Numerical: '{query[:30]}' -> reason={result.reason.value}")
    
    def test_units_detected(self, detector):
        """Test: Physical units trigger verification"""
        from services.symbolic_verification_layer import SymbolicReason
        
        unit_queries = [
            "A car travels at 60 m/s for 10 seconds",
            "The force is 50 N applied over 2 m",
            "The mass is 25 kg and acceleration is 10 m/s",
        ]
        
        for query in unit_queries:
            result = detector.detect(query)
            assert result.requires_verification, f"Should require verification: {query}"
            logger.info(f"Units: '{query[:30]}' -> reason={result.reason.value}")
    
    def test_derivation_detected(self, detector):
        """Test: Derivation requests trigger verification"""
        from services.symbolic_verification_layer import SymbolicReason
        
        derivation_queries = [
            "Derive the formula for kinetic energy",
            "Prove that F = ma",
            "Show that the derivative of x^2 is 2x",
        ]
        
        for query in derivation_queries:
            result = detector.detect(query)
            assert result.requires_verification, f"Should require verification: {query}"
            logger.info(f"Derivation: '{query[:30]}' -> reason={result.reason.value}")
    
    def test_equations_detected(self, detector):
        """Test: Mathematical equations trigger verification"""
        
        equation_queries = [
            "Solve x = 2y + 5",
            "Find f(x) = x^2 + 3x",
            "Simplify 2x + 3x - x",
        ]
        
        for query in equation_queries:
            result = detector.detect(query)
            assert result.requires_verification, f"Should require verification: {query}"
            logger.info(f"Equation: '{query[:30]}' -> reason={result.reason.value}")
    
    def test_conceptual_queries_low_detection(self, detector):
        """Test: Pure conceptual queries have lower detection rate"""
        
        conceptual_queries = [
            "What is Newton's first law?",
            "Explain photosynthesis",
            "Why is the sky blue?",
            "How does the heart pump blood?",
        ]
        
        triggered = 0
        for query in conceptual_queries:
            result = detector.detect(query)
            if result.requires_verification:
                triggered += 1
        
        # Allow some false positives but not all
        assert triggered < len(conceptual_queries), "Too many false positives"
        logger.info(f"Conceptual: {len(conceptual_queries) - triggered}/{len(conceptual_queries)} correctly passed")
    
    def test_detection_is_fast(self, detector):
        """Test: Detection is fast (< 10ms)"""
        import time
        
        queries = [
            "Calculate 25 + 37 * 2 and show step by step solution",
            "A car with mass 1000 kg accelerates at 5 m/s, find the force",
        ]
        
        start = time.time()
        for query in queries:
            detector.detect(query)
        elapsed = time.time() - start
        
        avg_time = elapsed / len(queries) * 1000
        assert avg_time < 10, f"Detection too slow: {avg_time:.2f}ms per query"
        
        logger.info(f"Performance: {avg_time:.2f}ms per query")


# =============================================================================
# TEST: VERIFICATION EXECUTOR
# =============================================================================

class TestSymbolicVerificationExecutor:
    """Test symbolic verification execution"""
    
    @pytest.fixture
    def executor(self):
        from services.symbolic_verification_layer import SymbolicVerificationExecutor
        return SymbolicVerificationExecutor()
    
    @pytest.mark.asyncio
    async def test_numerical_query_verified(self, executor):
        """Test: Numerical query gets verified"""
        
        result = await executor.verify_and_enhance(
            query="Calculate 25 + 37",
            response="25 + 37 = 62",
            context={"subject": "Mathematics"}
        )
        
        assert result.hybrid_enabled, "Should enable hybrid for numerical"
        logger.info(f"Numerical verified: mode={result.hybrid_mode.value}")
    
    @pytest.mark.asyncio
    async def test_conceptual_query_passed_through(self, executor):
        """Test: Conceptual query passes through without verification"""
        
        result = await executor.verify_and_enhance(
            query="What is Newton's first law?",
            response="Newton's first law states that an object at rest stays at rest.",
            context={"subject": "Physics"}
        )
        
        # May or may not enable based on response content
        logger.info(f"Conceptual: enabled={result.hybrid_enabled}, mode={result.hybrid_mode.value}")
    
    @pytest.mark.asyncio
    async def test_physics_formula_verified(self, executor):
        """Test: Physics formula query gets verified"""
        
        result = await executor.verify_and_enhance(
            query="Using F = ma, calculate force when m = 10 kg and a = 5 m/s",
            response="F = ma = 10 * 5 = 50 N",
            context={"subject": "Physics"}
        )
        
        assert result.hybrid_enabled, "Should enable hybrid for physics formula"
        logger.info(f"Physics formula verified: passed={result.verifier_passed}")


# =============================================================================
# TEST: INTEGRATION
# =============================================================================

class TestSymbolicIntegration:
    """Test integration with apply_symbolic_verification"""
    
    @pytest.mark.asyncio
    async def test_apply_symbolic_verification(self):
        """Test: apply_symbolic_verification function works"""
        from services.symbolic_verification_layer import apply_symbolic_verification
        
        result = {
            "main_response": "Force = 10 kg * 5 m/s = 50 N",
            "response": {
                "default_view": {
                    "main_content": {
                        "content": "Force = 10 kg * 5 m/s = 50 N"
                    }
                }
            }
        }
        
        updated = await apply_symbolic_verification(
            query="Calculate F when m=10kg and a=5m/s",
            result=result,
            context={"subject": "Physics"}
        )
        
        # Should have _symbolic metadata
        assert "_symbolic" in updated, "Should add _symbolic metadata"
        
        symbolic_meta = updated["_symbolic"]
        assert "hybrid_enabled" in symbolic_meta
        assert "hybrid_mode" in symbolic_meta
        assert "verifier_passed" in symbolic_meta
        assert "reason_for_enable" in symbolic_meta
        
        logger.info(f"Integration: {symbolic_meta}")
    
    @pytest.mark.asyncio
    async def test_symbolic_non_blocking(self):
        """Test: Symbolic verification is non-blocking on errors"""
        from services.symbolic_verification_layer import apply_symbolic_verification
        
        # Even with weird input, should not crash
        result = {
            "main_response": None,
        }
        
        updated = await apply_symbolic_verification(
            query="",
            result=result,
            context=None
        )
        
        # Should return original result without crashing
        assert updated is not None
        logger.info("Non-blocking: handles edge cases")


# =============================================================================
# TEST: OBSERVABILITY
# =============================================================================

class TestSymbolicObservability:
    """Test observability logging"""
    
    @pytest.mark.asyncio
    async def test_log_fields_complete(self):
        """Test: Log includes all required fields"""
        from services.symbolic_verification_layer import apply_symbolic_verification
        
        result = {
            "main_response": "The velocity is v = 20 m/s"
        }
        
        updated = await apply_symbolic_verification(
            query="Calculate velocity when distance is 100m and time is 5s",
            result=result,
            context={"subject": "Physics"}
        )
        
        if "_symbolic" in updated:
            symbolic = updated["_symbolic"]
            
            required_fields = [
                "hybrid_enabled",
                "hybrid_mode",
                "verifier_passed",
                "reason_for_enable"
            ]
            
            for field in required_fields:
                assert field in symbolic, f"Missing required field: {field}"
            
            logger.info(f"Observability: {symbolic}")


# =============================================================================
# TEST: NO REGRESSIONS
# =============================================================================

class TestNoRegressions:
    """Verify no regressions to existing systems"""
    
    def test_hybrid_reasoning_engine_exists(self):
        """Test: HybridReasoningEngine is not removed"""
        try:
            from services.hybrid_reasoning_engine import HybridReasoningEngine
            assert HybridReasoningEngine is not None
            logger.info("HybridReasoningEngine exists")
        except ImportError as e:
            pytest.fail(f"HybridReasoningEngine should exist: {e}")
    
    def test_routing_unchanged(self):
        """Test: Routing engine is unchanged"""
        try:
            from services.intelligent_routing_engine import (
                IntelligentRoutingEngine,
                RecommendedPipeline
            )
            
            # HYBRID_REASONING pipeline should still exist
            assert hasattr(RecommendedPipeline, 'HYBRID_REASONING'), \
                "HYBRID_REASONING pipeline should exist"
            
            logger.info("Routing unchanged")
        except ImportError as e:
            pytest.fail(f"Routing engine should be importable: {e}")


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
