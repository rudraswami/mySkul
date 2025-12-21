"""
🧮 Symbolic Verification Layer - Auto-enable when math/logic needed
===================================================================

INTENT: Enable HybridReasoningEngine automatically when query needs it.

This layer:
1. Detects if query requires symbolic verification (lightweight)
2. Verifies/corrects math in agent responses
3. Does NOT change routing - works as enhancement layer

INTEGRATION POINT: UnifiedAIOrchestrator.process() after pipeline execution

NO CHANGES TO:
- Routing logic
- Agent behavior
- Tool schemas
"""

import logging
import re
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Environment flag for debug logging
SYMBOLIC_DEBUG = os.getenv("SYMBOLIC_DEBUG", "false").lower() == "true"


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class SymbolicReason(Enum):
    """Reason why symbolic verification was enabled"""
    NUMERICAL = "numerical"           # Numbers, calculations
    UNITS = "units"                   # Physical units (m, kg, N, J, etc.)
    EQUATION = "equation"             # Mathematical equations
    DERIVATION = "derivation"         # Derivation/proof requested
    FORMULA = "formula"               # Formula application
    LOGIC = "logic"                   # Logical reasoning
    NONE = "none"                     # Not needed


class HybridMode(Enum):
    """Hybrid reasoning mode used"""
    HYBRID = "hybrid"                 # Both neural + symbolic
    SYMBOLIC_ONLY = "symbolic_only"   # Pure math/logic
    NEURAL_ONLY = "neural_only"       # No verification needed
    VERIFICATION = "verification"     # Post-hoc verification only


@dataclass
class SymbolicIntentResult:
    """Result of symbolic intent detection"""
    requires_verification: bool
    reason: SymbolicReason
    confidence: float
    detected_patterns: List[str]


@dataclass
class SymbolicVerificationResult:
    """Result of symbolic verification"""
    original_response: str
    verified_response: str
    hybrid_enabled: bool
    hybrid_mode: HybridMode
    verifier_passed: bool
    reason_for_enable: SymbolicReason
    corrections_made: List[str]
    symbolic_proof: Optional[str]


# =============================================================================
# SYMBOLIC INTENT DETECTOR (Lightweight)
# =============================================================================

class SymbolicIntentDetector:
    """
    Lightweight detector for queries requiring symbolic verification.
    
    Uses structured heuristics (not just keyword matching).
    FAST: O(n) single pass over query.
    """
    
    # Pattern categories with weights
    NUMERICAL_PATTERNS = [
        (r'\b\d+(?:\.\d+)?\s*[+\-*/^]\s*\d+', 0.9, "arithmetic"),
        (r'\b\d+(?:\.\d+)?\s*(kg|m|s|N|J|W|V|A|Hz|mol|°C|K|Pa|atm)\b', 0.95, "units"),
        (r'\b(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)', 0.8, "numeric_equation"),
        (r'\b\d{2,}\b', 0.5, "large_number"),  # Numbers > 9
    ]
    
    EQUATION_PATTERNS = [
        (r'\b[a-z]\s*=\s*[a-z0-9+\-*/^()]+', 0.85, "variable_equation"),
        (r'f\s*\(\s*[a-z]\s*\)', 0.9, "function_notation"),
        (r'\b(dy|dx|d[a-z])\s*/\s*(d[a-z])', 0.95, "derivative"),
        (r'∫|integral|∑|summation', 0.95, "calculus"),
        (r'\b(sin|cos|tan|log|ln|exp|sqrt)\s*\(', 0.85, "math_function"),
    ]
    
    DERIVATION_PATTERNS = [
        (r'\b(derive|derivation|prove|proof|show\s+that)\b', 0.95, "derivation"),
        (r'\b(step\s+by\s+step|steps?|working)\b', 0.7, "steps_requested"),
        (r'\b(simplify|factor|expand|solve\s+for)\b', 0.9, "algebraic"),
    ]
    
    PHYSICS_PATTERNS = [
        (r'\b(force|velocity|acceleration|momentum|energy|work|power)\b', 0.7, "physics_concept"),
        (r'\b(F\s*=\s*m\s*a|v\s*=\s*u\s*\+\s*a\s*t|E\s*=\s*m\s*c)', 0.95, "physics_formula"),
        (r'\b(newton|coulomb|ohm|joule|watt)\b', 0.8, "physics_unit_name"),
        (r'\b(\d+)\s*(m/s|m/s²|kg·m|N·m|J/s)\b', 0.95, "compound_unit"),
    ]
    
    CHEMISTRY_PATTERNS = [
        (r'\b(mol|molar|molarity|concentration)\b', 0.8, "chemistry_concept"),
        (r'\b[A-Z][a-z]?\d*\s*\+\s*[A-Z][a-z]?\d*\s*→', 0.95, "chemical_equation"),
        (r'\b(pH|pOH|Ka|Kb|Kw)\s*=', 0.9, "chemistry_formula"),
    ]
    
    LOGIC_PATTERNS = [
        (r'\b(if\s+and\s+only\s+if|implies|therefore|hence)\b', 0.85, "logical_connector"),
        (r'\b(valid|invalid|contradiction|tautology)\b', 0.8, "logic_term"),
        (r'\b(∀|∃|¬|∧|∨|→|↔)', 0.95, "logic_symbol"),
    ]
    
    # Keywords that suggest calculation/verification needed
    CALCULATION_KEYWORDS = {
        "calculate", "compute", "find", "solve", "evaluate",
        "determine", "what is the value", "how much", "how many"
    }
    
    def __init__(self):
        # Pre-compile all patterns
        self._patterns = []
        
        for category, patterns in [
            (SymbolicReason.NUMERICAL, self.NUMERICAL_PATTERNS),
            (SymbolicReason.EQUATION, self.EQUATION_PATTERNS),
            (SymbolicReason.DERIVATION, self.DERIVATION_PATTERNS),
            (SymbolicReason.FORMULA, self.PHYSICS_PATTERNS + self.CHEMISTRY_PATTERNS),
            (SymbolicReason.LOGIC, self.LOGIC_PATTERNS),
        ]:
            for pattern, weight, name in patterns:
                self._patterns.append((
                    re.compile(pattern, re.IGNORECASE),
                    weight,
                    category,
                    name
                ))
    
    def detect(self, query: str, response: str = None) -> SymbolicIntentResult:
        """
        Detect if query (and optionally response) requires symbolic verification.
        
        Returns:
            SymbolicIntentResult with requires_verification flag
        """
        query_lower = query.lower()
        detected = []
        max_confidence = 0.0
        primary_reason = SymbolicReason.NONE
        
        # Check all patterns
        for pattern, weight, category, name in self._patterns:
            if pattern.search(query):
                detected.append(name)
                if weight > max_confidence:
                    max_confidence = weight
                    primary_reason = category
        
        # Check calculation keywords (additive boost)
        for keyword in self.CALCULATION_KEYWORDS:
            if keyword in query_lower:
                max_confidence = min(1.0, max_confidence + 0.2)
                if primary_reason == SymbolicReason.NONE:
                    primary_reason = SymbolicReason.NUMERICAL
                detected.append(f"keyword:{keyword}")
                break
        
        # Also check response for math content if provided
        if response and max_confidence < 0.7:
            response_confidence = self._check_response_for_math(response)
            if response_confidence > max_confidence:
                max_confidence = response_confidence
                primary_reason = SymbolicReason.EQUATION
                detected.append("response_contains_math")
        
        # Threshold: require >= 0.6 confidence to enable verification
        requires_verification = max_confidence >= 0.6
        
        if requires_verification and SYMBOLIC_DEBUG:
            logger.info(f"🧮 Symbolic intent detected: reason={primary_reason.value}, "
                       f"confidence={max_confidence:.2f}, patterns={detected}")
        
        return SymbolicIntentResult(
            requires_verification=requires_verification,
            reason=primary_reason,
            confidence=max_confidence,
            detected_patterns=detected
        )
    
    def _check_response_for_math(self, response: str) -> float:
        """Check if response contains math that needs verification"""
        # Quick patterns for math in response
        math_indicators = [
            (r'\b\d+(?:\.\d+)?\s*[+\-*/=]\s*\d+', 0.7),
            (r'\b[a-z]\s*=\s*\d', 0.6),
            (r'therefore|hence|thus|so,?\s*\d', 0.65),
        ]
        
        for pattern, weight in math_indicators:
            if re.search(pattern, response, re.IGNORECASE):
                return weight
        
        return 0.0


# =============================================================================
# SYMBOLIC VERIFICATION EXECUTOR
# =============================================================================

class SymbolicVerificationExecutor:
    """
    Executes symbolic verification on responses.
    
    Uses existing MathVerifier + HybridReasoningEngine.
    """
    
    def __init__(self):
        self._math_verifier = None
        self._hybrid_engine = None
        self._intent_detector = SymbolicIntentDetector()
    
    def _get_math_verifier(self):
        """Lazy load math verifier"""
        if self._math_verifier is None:
            try:
                from services.verification.math_verifier import MathVerifier
                self._math_verifier = MathVerifier()
            except ImportError as e:
                logger.warning(f"MathVerifier not available: {e}")
        return self._math_verifier
    
    def _get_hybrid_engine(self):
        """Lazy load hybrid reasoning engine"""
        if self._hybrid_engine is None:
            try:
                from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine
                self._hybrid_engine = get_hybrid_reasoning_engine()
            except ImportError as e:
                logger.warning(f"HybridReasoningEngine not available: {e}")
        return self._hybrid_engine
    
    async def verify_and_enhance(
        self,
        query: str,
        response: str,
        context: Dict[str, Any] = None
    ) -> SymbolicVerificationResult:
        """
        Verify response and enhance if needed.
        
        POLICY:
        - If requires_symbolic_verification == true:
          - Verify math in response
          - If errors found: correct OR state uncertainty
          - Add symbolic proof if available
        
        Returns:
            SymbolicVerificationResult with verified/enhanced response
        """
        context = context or {}
        
        # Step 1: Detect if verification needed
        intent = self._intent_detector.detect(query, response)
        
        if not intent.requires_verification:
            # No verification needed - pass through
            return SymbolicVerificationResult(
                original_response=response,
                verified_response=response,
                hybrid_enabled=False,
                hybrid_mode=HybridMode.NEURAL_ONLY,
                verifier_passed=True,
                reason_for_enable=SymbolicReason.NONE,
                corrections_made=[],
                symbolic_proof=None
            )
        
        logger.info(f"🧮 Symbolic verification enabled: reason={intent.reason.value}")
        
        # Step 2: Verify math in response
        verifier = self._get_math_verifier()
        verifier_passed = True
        corrections = []
        
        if verifier:
            try:
                from services.verification.math_verifier import VerificationStatus
                
                verification_result = verifier.verify_response(
                    response,
                    question=query,
                    subject=context.get("subject", "Mathematics")
                )
                
                if verification_result.status == VerificationStatus.ERROR_FOUND:
                    verifier_passed = False
                    corrections = [e.description for e in verification_result.errors[:3]]
                    logger.warning(f"⚠️ Math errors found: {len(verification_result.errors)}")
                elif verification_result.status == VerificationStatus.VERIFIED:
                    logger.info("✅ Math verification passed")
                    
            except Exception as e:
                logger.warning(f"Math verification error: {e}")
        
        # Step 3: Get symbolic enhancement if available
        symbolic_proof = None
        enhanced_response = response
        hybrid_mode = HybridMode.VERIFICATION
        
        hybrid_engine = self._get_hybrid_engine()
        
        if hybrid_engine and intent.reason in [SymbolicReason.DERIVATION, SymbolicReason.EQUATION]:
            try:
                hybrid_result = await hybrid_engine.reason(query, context)
                
                if hybrid_result.symbolic_proof:
                    symbolic_proof = hybrid_result.symbolic_proof
                    hybrid_mode = HybridMode.HYBRID
                    
                    # Enhance response with symbolic proof if verification failed
                    if not verifier_passed and hybrid_result.verification_passed:
                        enhanced_response = self._merge_symbolic_into_response(
                            response, symbolic_proof
                        )
                        corrections.append("Added verified symbolic solution")
                        
            except Exception as e:
                logger.warning(f"Hybrid reasoning error: {e}")
        
        # Step 4: Handle verification failure
        if not verifier_passed and not symbolic_proof:
            # State uncertainty - don't propagate errors
            enhanced_response = self._add_uncertainty_note(response, corrections)
        
        # Log result
        self._log_verification_result(
            intent=intent,
            verifier_passed=verifier_passed,
            hybrid_mode=hybrid_mode,
            corrections=corrections
        )
        
        return SymbolicVerificationResult(
            original_response=response,
            verified_response=enhanced_response,
            hybrid_enabled=True,
            hybrid_mode=hybrid_mode,
            verifier_passed=verifier_passed,
            reason_for_enable=intent.reason,
            corrections_made=corrections,
            symbolic_proof=symbolic_proof
        )
    
    def _merge_symbolic_into_response(self, response: str, symbolic_proof: str) -> str:
        """Merge symbolic proof into neural response"""
        if not symbolic_proof:
            return response
        
        return (
            f"{response}\n\n"
            f"---\n"
            f"**📐 Verified Solution:**\n"
            f"{symbolic_proof}"
        )
    
    def _add_uncertainty_note(self, response: str, errors: List[str]) -> str:
        """Add uncertainty note when verification failed"""
        error_hints = ""
        if errors:
            error_hints = f" ({', '.join(errors[:2])})"
        
        return (
            f"{response}\n\n"
            f"⚠️ *Note: Please verify calculations with your textbook. "
            f"Some steps may need checking{error_hints}.*"
        )
    
    def _log_verification_result(
        self,
        intent: SymbolicIntentResult,
        verifier_passed: bool,
        hybrid_mode: HybridMode,
        corrections: List[str]
    ):
        """Log verification for observability"""
        log_data = {
            "hybrid_enabled": True,
            "hybrid_mode": hybrid_mode.value,
            "verifier_passed": verifier_passed,
            "reason_for_enable": intent.reason.value,
            "confidence": intent.confidence,
            "patterns_detected": len(intent.detected_patterns),
            "corrections_count": len(corrections)
        }
        
        logger.info(f"🧮 Symbolic: {log_data}")


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_executor_instance: Optional[SymbolicVerificationExecutor] = None


def get_symbolic_executor() -> SymbolicVerificationExecutor:
    """Get or create the global symbolic verification executor"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SymbolicVerificationExecutor()
    return _executor_instance


# =============================================================================
# HELPER: Apply Verification to Result
# =============================================================================

async def apply_symbolic_verification(
    query: str,
    result: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Apply symbolic verification to orchestrator result.
    
    This is the main entry point for integration with UnifiedAIOrchestrator.
    """
    context = context or {}
    
    try:
        executor = get_symbolic_executor()
        
        # Extract response text
        response_text = result.get("main_response", "")
        if not response_text:
            response_text = result.get("response", {}).get("default_view", {}).get(
                "main_content", {}
            ).get("content", "")
        
        if not response_text:
            return result
        
        # Verify and enhance
        verification_result = await executor.verify_and_enhance(
            query=query,
            response=response_text,
            context=context
        )
        
        # Update result if response was modified
        if verification_result.verified_response != verification_result.original_response:
            result["main_response"] = verification_result.verified_response
            
            # Update nested response structure
            if "response" in result and "default_view" in result["response"]:
                if "main_content" in result["response"]["default_view"]:
                    result["response"]["default_view"]["main_content"]["content"] = (
                        verification_result.verified_response
                    )
        
        # Add verification metadata
        result["_symbolic"] = {
            "hybrid_enabled": verification_result.hybrid_enabled,
            "hybrid_mode": verification_result.hybrid_mode.value,
            "verifier_passed": verification_result.verifier_passed,
            "reason_for_enable": verification_result.reason_for_enable.value,
            "corrections_count": len(verification_result.corrections_made),
        }
        
        if verification_result.symbolic_proof:
            result["_symbolic"]["has_proof"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Symbolic verification error: {e}")
        # Non-blocking - return original result
        return result
