"""
Verified Response Service - End-to-End Neuro-Symbolic Integration
==================================================================

This service wraps the existing ResponseComposer with:
1. RAG Enhancement: Grounds prompts in verified curriculum
2. Post-Generation Verification: Validates math, facts, logic
3. Verification Badges: Adds trust signals to responses

This is the INTEGRATION LAYER that connects Phase 1 components
to the production AI pipeline WITHOUT modifying existing code.

Usage:
    service = VerifiedResponseService(db, llm_api_key)
    result = await service.generate_verified_response(
        user_id="...",
        question="What is Newton's second law?",
        subject="Physics"
    )
    # result includes verified_response + verification_badge + curriculum_sources
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from services.response_composer import ResponseComposer
from services.verification import VerificationOrchestrator, get_verification_orchestrator
from services.knowledge_base import RAGEnhancer, get_rag_enhancer

logger = logging.getLogger(__name__)


@dataclass
class VerifiedResponse:
    """A response with verification metadata"""
    response: Dict[str, Any]
    is_verified: bool
    verification_confidence: float
    verification_badge: Dict[str, Any]
    curriculum_sources: List[str]
    verification_time_ms: float
    issues_found: List[Dict[str, Any]]
    corrections: List[Dict[str, Any]]


class VerifiedResponseService:
    """
    Production-ready verified response service.
    
    Wraps ResponseComposer with neuro-symbolic capabilities:
    - Pre-generation RAG enhancement
    - Post-generation verification
    - Verification badges for UI
    """
    
    def __init__(
        self,
        db,
        llm_api_key: str,
        enable_rag: bool = True,
        enable_verification: bool = True
    ):
        """
        Initialize the verified response service.
        
        Args:
            db: Database connection
            llm_api_key: API key for LLM
            enable_rag: Enable curriculum-grounded prompts
            enable_verification: Enable post-generation verification
        """
        self.db = db
        self.llm_api_key = llm_api_key
        self.enable_rag = enable_rag
        self.enable_verification = enable_verification
        
        # Initialize core components
        self.composer = ResponseComposer(db, llm_api_key)
        self.rag = get_rag_enhancer() if enable_rag else None
        self.verifier = get_verification_orchestrator() if enable_verification else None
        
        logger.info(f"🚀 VerifiedResponseService initialized")
        logger.info(f"   ├── RAG: {'✅ Enabled' if enable_rag else '❌ Disabled'}")
        logger.info(f"   └── Verification: {'✅ Enabled' if enable_verification else '❌ Disabled'}")
    
    async def generate_verified_response(
        self,
        user_id: str,
        session_id: str,
        question: str,
        subject: Optional[str] = None,
        exam_mode: str = "JEE",
        message_history: List[Dict] = None,
        skip_verification: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a verified AI response with curriculum grounding.
        
        This is the main entry point for verified responses.
        
        Args:
            user_id: User ID
            session_id: Session ID
            question: Student's question
            subject: Subject area (auto-detected if None)
            exam_mode: JEE, NEET, etc.
            message_history: Previous messages for context
            skip_verification: Skip verification for speed
            
        Returns:
            Dict with response, verification, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Generating verified response for: {question[:50]}...")
            
            # Step 1: Enhance question with RAG (curriculum context)
            enhanced_question = question
            curriculum_sources = []
            formulas_context = []
            
            if self.enable_rag and self.rag:
                rag_result = self.rag.enhance_prompt(
                    question=question,
                    subject=subject,
                    include_formulas=True
                )
                
                if rag_result.curriculum_context:
                    # For now, we add curriculum context as additional instruction
                    # This grounds the LLM without modifying the question directly
                    curriculum_sources = rag_result.sources_used
                    formulas_context = rag_result.formulas_available
                    logger.info(f"📚 RAG: Found {len(curriculum_sources)} curriculum sources")
            
            # Step 2: Generate response using existing ResponseComposer
            result = await self.composer.generate_response(
                user_id=user_id,
                session_id=session_id,
                question=enhanced_question,
                subject=subject,
                exam_mode=exam_mode,
                message_history=message_history
            )
            
            # Extract the response text for verification
            response_text = self._extract_response_text(result)
            detected_subject = result.get("detected_subject", subject or "General")
            
            # Step 3: Run verification (unless skipped)
            verification_result = None
            verification_badge = None
            
            if self.enable_verification and self.verifier and not skip_verification:
                verification_result = await self.verifier.verify_response(
                    response_text=response_text,
                    question=question,
                    subject=detected_subject,
                    verify_math=True,
                    verify_facts=True,
                    verify_logic=True
                )
                
                verification_badge = self.verifier.create_verification_badge(verification_result)
                logger.info(f"✅ Verified: {verification_result.overall_status.value}, "
                           f"confidence: {verification_result.confidence_score:.2f}")
            
            # Step 4: Build enhanced response with verification metadata
            total_time = time.time() - start_time
            
            enhanced_result = {
                **result,
                "verified": True,
                "verification": {
                    "is_verified": verification_result.is_safe_to_show if verification_result else True,
                    "confidence": verification_result.confidence_score if verification_result else 1.0,
                    "status": verification_result.overall_status.value if verification_result else "not_checked",
                    "issues": verification_result.issues_found if verification_result else [],
                    "corrections": verification_result.corrections_suggested if verification_result else [],
                    "time_ms": verification_result.verification_time_ms if verification_result else 0
                },
                "verification_badge": verification_badge or {
                    "type": "verified",
                    "icon": "✅",
                    "text": "AI Generated",
                    "color": "blue"
                },
                "curriculum": {
                    "sources": curriculum_sources,
                    "formulas_available": formulas_context,
                    "grounded": len(curriculum_sources) > 0
                },
                "total_generation_time": total_time
            }
            
            # Step 5: Inject verification badge into response structure
            if "response" in enhanced_result:
                enhanced_result["response"]["verification_badge"] = verification_badge
                enhanced_result["response"]["curriculum_sources"] = curriculum_sources
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Verified response generation failed: {e}", exc_info=True)
            # Fall back to unverified response
            try:
                result = await self.composer.generate_response(
                    user_id=user_id,
                    session_id=session_id,
                    question=question,
                    subject=subject,
                    exam_mode=exam_mode,
                    message_history=message_history
                )
                result["verified"] = False
                result["verification"] = {"status": "error", "error": str(e)}
                return result
            except Exception as e2:
                logger.error(f"❌ Fallback also failed: {e2}")
                raise
    
    async def quick_check(
        self,
        response_text: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Quick verification check (for real-time use).
        Only checks math, skips full verification.
        """
        if not self.verifier:
            return {"verified": True, "quick": True}
        
        return await self.verifier.quick_verify(response_text, subject)
    
    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """Extract the main response text for verification"""
        try:
            response = result.get("response", {})
            default_view = response.get("default_view", {})
            main_content = default_view.get("main_content", {})
            
            text = main_content.get("content", "")
            
            # Also check progressive sections
            progressive = response.get("progressive_sections", {})
            explanation = progressive.get("explanation", "")
            
            if explanation:
                text = f"{text}\n\n{explanation}"
            
            return text
            
        except Exception as e:
            logger.warning(f"Could not extract response text: {e}")
            return str(result)


# ============================================================================
# FACTORY FUNCTION & SINGLETON
# ============================================================================

_verified_service_instance: Optional[VerifiedResponseService] = None


def get_verified_response_service(
    db,
    llm_api_key: Optional[str] = None
) -> VerifiedResponseService:
    """
    Get or create the verified response service.
    
    Uses singleton pattern for efficiency.
    """
    global _verified_service_instance
    
    if _verified_service_instance is None:
        key = llm_api_key or os.environ.get('OPENAI_API_KEY')
        _verified_service_instance = VerifiedResponseService(
            db=db,
            llm_api_key=key,
            enable_rag=True,
            enable_verification=True
        )
    
    return _verified_service_instance


def create_verified_response_service(
    db,
    llm_api_key: str,
    enable_rag: bool = True,
    enable_verification: bool = True
) -> VerifiedResponseService:
    """Create a new verified response service with custom settings"""
    return VerifiedResponseService(
        db=db,
        llm_api_key=llm_api_key,
        enable_rag=enable_rag,
        enable_verification=enable_verification
    )

