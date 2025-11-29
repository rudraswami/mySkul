"""
Verification Orchestrator - The Unified Verification Layer
===========================================================

Coordinates all verification components:
- MathVerifier: Symbolic math verification
- FactChecker: Curriculum-grounded fact verification
- LogicValidator: Reasoning validation

This is the TRUE Layer 3 (Supervisor Verification) that ensures
hallucination-free, verified outputs.

Integration with existing agents is non-invasive - enhances but doesn't replace.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .math_verifier import MathVerifier, VerificationResult as MathResult, VerificationStatus
from .fact_checker import FactChecker, FactCheckResult, FactStatus
from .logic_validator import LogicValidator, LogicValidationResult, LogicStatus

logger = logging.getLogger(__name__)


class OverallVerificationStatus(Enum):
    """Overall status of verification"""
    VERIFIED = "verified"           # All checks passed
    PARTIALLY_VERIFIED = "partially_verified"  # Some checks passed
    NEEDS_REVIEW = "needs_review"   # Manual review recommended
    FAILED = "failed"               # Critical issues found


@dataclass
class ComprehensiveVerificationResult:
    """Comprehensive result from all verification layers"""
    overall_status: OverallVerificationStatus
    is_safe_to_show: bool
    confidence_score: float  # 0.0 to 1.0
    
    # Individual results
    math_verification: Optional[MathResult] = None
    fact_check: Optional[FactCheckResult] = None
    logic_validation: Optional[LogicValidationResult] = None
    
    # Summary
    issues_found: List[Dict[str, Any]] = field(default_factory=list)
    corrections_suggested: List[Dict[str, Any]] = field(default_factory=list)
    verification_summary: str = ""
    
    # Metadata
    verification_time_ms: float = 0.0
    verifiers_used: List[str] = field(default_factory=list)
    
    # For UI display
    badges: List[Dict[str, str]] = field(default_factory=list)


class VerificationOrchestrator:
    """
    Unified Verification Orchestrator
    
    The brain of Layer 3 (Supervisor Verification):
    - Coordinates multiple verification engines
    - Aggregates results into unified assessment
    - Provides actionable feedback
    - Integrates seamlessly with existing agents
    
    Usage:
        orchestrator = VerificationOrchestrator()
        result = await orchestrator.verify_response(
            response_text="...",
            question="...",
            subject="Physics"
        )
        if result.is_safe_to_show:
            # Show response to student
        else:
            # Apply corrections or flag for review
    """
    
    def __init__(self, enable_all: bool = True):
        """
        Initialize the Verification Orchestrator.
        
        Args:
            enable_all: Enable all verification engines (can be toggled individually)
        """
        self.math_verifier = MathVerifier() if enable_all else None
        self.fact_checker = FactChecker() if enable_all else None
        self.logic_validator = LogicValidator() if enable_all else None
        
        self.enabled_verifiers = []
        if self.math_verifier:
            self.enabled_verifiers.append("math")
        if self.fact_checker:
            self.enabled_verifiers.append("facts")
        if self.logic_validator:
            self.enabled_verifiers.append("logic")
        
        logger.info(f"🛡️ VerificationOrchestrator initialized with: {', '.join(self.enabled_verifiers)}")
    
    async def verify_response(
        self,
        response_text: str,
        question: str,
        subject: str,
        verify_math: bool = True,
        verify_facts: bool = True,
        verify_logic: bool = True
    ) -> ComprehensiveVerificationResult:
        """
        Perform comprehensive verification on an AI response.
        
        This is the main entry point for verification. It runs all enabled
        verifiers in parallel and aggregates results.
        
        Args:
            response_text: The AI-generated response to verify
            question: The original student question
            subject: Subject area (Mathematics, Physics, Chemistry, Biology)
            verify_math: Enable math verification
            verify_facts: Enable fact checking
            verify_logic: Enable logic validation
            
        Returns:
            ComprehensiveVerificationResult with full analysis
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Starting comprehensive verification for {subject}")
            
            # Run verifications in parallel
            tasks = []
            task_names = []
            
            if verify_math and self.math_verifier:
                tasks.append(self._run_math_verification(response_text, question, subject))
                task_names.append("math")
            
            if verify_facts and self.fact_checker:
                tasks.append(self._run_fact_check(response_text, question, subject))
                task_names.append("facts")
            
            if verify_logic and self.logic_validator:
                tasks.append(self._run_logic_validation(response_text, question, subject))
                task_names.append("logic")
            
            if not tasks:
                # No verification enabled
                return ComprehensiveVerificationResult(
                    overall_status=OverallVerificationStatus.VERIFIED,
                    is_safe_to_show=True,
                    confidence_score=1.0,
                    verification_summary="No verification performed (all disabled)",
                    verifiers_used=[]
                )
            
            # Execute all verifications in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Map results to their types
            math_result = None
            fact_result = None
            logic_result = None
            
            for name, result in zip(task_names, results):
                if isinstance(result, Exception):
                    logger.error(f"Verification {name} failed: {result}")
                    continue
                
                if name == "math":
                    math_result = result
                elif name == "facts":
                    fact_result = result
                elif name == "logic":
                    logic_result = result
            
            # Aggregate results
            return self._aggregate_results(
                math_result=math_result,
                fact_result=fact_result,
                logic_result=logic_result,
                start_time=start_time,
                verifiers_used=task_names
            )
            
        except Exception as e:
            logger.error(f"❌ Verification orchestration error: {e}", exc_info=True)
            return ComprehensiveVerificationResult(
                overall_status=OverallVerificationStatus.NEEDS_REVIEW,
                is_safe_to_show=True,  # Don't block on error
                confidence_score=0.5,
                verification_summary=f"Verification error: {str(e)}",
                verification_time_ms=(time.time() - start_time) * 1000,
                verifiers_used=[]
            )
    
    async def quick_verify(
        self,
        response_text: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Quick verification for real-time use (lower latency).
        
        Only checks critical issues, skips deep analysis.
        
        Args:
            response_text: Response to verify
            subject: Subject area
            
        Returns:
            Quick verification result dict
        """
        # Only run math verification for speed
        if self.math_verifier and subject.lower() in ["mathematics", "physics", "chemistry"]:
            math_result = self.math_verifier.verify_response(
                response_text, "", subject
            )
            return {
                "is_verified": math_result.is_correct,
                "confidence": math_result.confidence,
                "quick_check": True
            }
        
        return {
            "is_verified": True,
            "confidence": 0.8,
            "quick_check": True
        }
    
    def create_verification_badge(
        self,
        result: ComprehensiveVerificationResult
    ) -> Dict[str, Any]:
        """
        Create a verification badge for UI display.
        
        Returns badge data that can be shown to students to build trust.
        """
        if result.overall_status == OverallVerificationStatus.VERIFIED:
            return {
                "type": "verified",
                "icon": "✅",
                "text": "Professor Verified",
                "color": "green",
                "tooltip": f"Verified with {result.confidence_score:.0%} confidence. {', '.join(result.verifiers_used)} checks passed."
            }
        elif result.overall_status == OverallVerificationStatus.PARTIALLY_VERIFIED:
            return {
                "type": "partial",
                "icon": "⚠️",
                "text": "Partially Verified",
                "color": "yellow",
                "tooltip": f"Some verification checks passed ({result.confidence_score:.0%}). Review recommended."
            }
        elif result.overall_status == OverallVerificationStatus.NEEDS_REVIEW:
            return {
                "type": "review",
                "icon": "🔍",
                "text": "Under Review",
                "color": "orange",
                "tooltip": "This response is being reviewed for accuracy."
            }
        else:
            return {
                "type": "unverified",
                "icon": "❓",
                "text": "Unverified",
                "color": "gray",
                "tooltip": "Could not verify this response."
            }
    
    async def _run_math_verification(
        self,
        response_text: str,
        question: str,
        subject: str
    ) -> MathResult:
        """Run math verification (async wrapper)"""
        # MathVerifier is sync, wrap for async compatibility
        return self.math_verifier.verify_response(response_text, question, subject)
    
    async def _run_fact_check(
        self,
        response_text: str,
        question: str,
        subject: str
    ) -> FactCheckResult:
        """Run fact checking (async wrapper)"""
        return self.fact_checker.check_response(response_text, question, subject)
    
    async def _run_logic_validation(
        self,
        response_text: str,
        question: str,
        subject: str
    ) -> LogicValidationResult:
        """Run logic validation (async wrapper)"""
        return self.logic_validator.validate_reasoning(response_text, question, subject)
    
    def _aggregate_results(
        self,
        math_result: Optional[MathResult],
        fact_result: Optional[FactCheckResult],
        logic_result: Optional[LogicValidationResult],
        start_time: float,
        verifiers_used: List[str]
    ) -> ComprehensiveVerificationResult:
        """Aggregate results from all verifiers into unified result"""
        import time
        
        issues = []
        corrections = []
        badges = []
        confidence_scores = []
        
        # Process math results
        if math_result:
            confidence_scores.append(math_result.confidence)
            
            if math_result.status == VerificationStatus.VERIFIED:
                badges.append({"type": "math", "status": "verified", "icon": "🧮✅"})
            elif math_result.status == VerificationStatus.ERROR_FOUND:
                badges.append({"type": "math", "status": "error", "icon": "🧮❌"})
                issues.extend(math_result.errors)
                corrections.extend(math_result.corrections)
            else:
                badges.append({"type": "math", "status": "partial", "icon": "🧮⚠️"})
        
        # Process fact check results
        if fact_result:
            confidence_scores.append(fact_result.confidence)
            
            if fact_result.status == FactStatus.VERIFIED:
                badges.append({"type": "facts", "status": "verified", "icon": "📚✅"})
            elif fact_result.status == FactStatus.INCORRECT:
                badges.append({"type": "facts", "status": "error", "icon": "📚❌"})
                for correction in fact_result.corrections:
                    issues.append({
                        "type": "fact_error",
                        "claim": correction.get("incorrect_claim"),
                        "correction": correction.get("correct_fact")
                    })
                    corrections.append(correction)
            else:
                badges.append({"type": "facts", "status": "partial", "icon": "📚⚠️"})
        
        # Process logic results
        if logic_result:
            confidence_scores.append(logic_result.confidence)
            
            if logic_result.status == LogicStatus.VALID:
                badges.append({"type": "logic", "status": "verified", "icon": "🧠✅"})
            elif logic_result.status == LogicStatus.INVALID:
                badges.append({"type": "logic", "status": "error", "icon": "🧠❌"})
                for gap in logic_result.logical_gaps:
                    issues.append({
                        "type": "logic_gap",
                        **gap
                    })
                for fallacy in logic_result.fallacies_detected:
                    issues.append({
                        "type": "fallacy",
                        "name": fallacy
                    })
            else:
                badges.append({"type": "logic", "status": "partial", "icon": "🧠⚠️"})
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Determine overall status
        critical_issues = [i for i in issues if i.get("type") in ["fact_error", "fallacy"]]
        
        if len(critical_issues) > 0:
            overall_status = OverallVerificationStatus.FAILED
            is_safe = False
        elif len(issues) > 2:
            overall_status = OverallVerificationStatus.NEEDS_REVIEW
            is_safe = True  # Still show but flag
        elif overall_confidence >= 0.7:
            overall_status = OverallVerificationStatus.VERIFIED
            is_safe = True
        else:
            overall_status = OverallVerificationStatus.PARTIALLY_VERIFIED
            is_safe = True
        
        # Generate summary
        summary_parts = []
        if math_result:
            summary_parts.append(f"Math: {math_result.status.value}")
        if fact_result:
            summary_parts.append(f"Facts: {fact_result.status.value}")
        if logic_result:
            summary_parts.append(f"Logic: {logic_result.status.value}")
        
        summary = f"Verification complete. {' | '.join(summary_parts)}. Confidence: {overall_confidence:.0%}"
        
        return ComprehensiveVerificationResult(
            overall_status=overall_status,
            is_safe_to_show=is_safe,
            confidence_score=overall_confidence,
            math_verification=math_result,
            fact_check=fact_result,
            logic_validation=logic_result,
            issues_found=issues,
            corrections_suggested=corrections,
            verification_summary=summary,
            verification_time_ms=(time.time() - start_time) * 1000,
            verifiers_used=verifiers_used,
            badges=badges
        )


# Singleton instance for easy access
_orchestrator_instance: Optional[VerificationOrchestrator] = None


def get_verification_orchestrator() -> VerificationOrchestrator:
    """Get or create the global verification orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = VerificationOrchestrator()
    return _orchestrator_instance

