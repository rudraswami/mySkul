"""
Neuro-Symbolic API Endpoints
============================

Test and diagnostic endpoints for the neuro-symbolic system:
- Verification testing
- RAG retrieval testing
- Enhanced supervisor testing

These endpoints allow testing the new capabilities without
affecting the production AI endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.verification import (
    MathVerifier,
    FactChecker,
    LogicValidator,
    VerificationOrchestrator,
    get_verification_orchestrator
)
from services.knowledge_base import (
    CurriculumRetriever,
    RAGEnhancer,
    get_rag_enhancer
)
from services.knowledge_base.curriculum_store import get_curriculum_store
from agents import create_enhanced_supervisor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/neuro-symbolic", tags=["Neuro-Symbolic"])


# Request/Response Models
class VerifyMathRequest(BaseModel):
    expression: str
    expected_result: Optional[str] = None
    subject: str = "Mathematics"


class VerifyFactRequest(BaseModel):
    claim: str
    subject: str


class VerifyResponseRequest(BaseModel):
    response_text: str
    question: str
    subject: str = "Mathematics"


class RAGSearchRequest(BaseModel):
    query: str
    subject: Optional[str] = None
    max_results: int = 5


class EnhancedQueryRequest(BaseModel):
    question: str
    subject: str = "Mathematics"
    user_id: str = "test_user"
    enable_rag: bool = True
    enable_verification: bool = True


# Endpoints
@router.post("/verify/math")
async def verify_math_expression(request: VerifyMathRequest):
    """
    Test the symbolic math verification engine.
    
    Example:
    ```
    POST /neuro-symbolic/verify/math
    {
        "expression": "2 + 2 = 4",
        "subject": "Mathematics"
    }
    ```
    """
    try:
        verifier = MathVerifier()
        
        if request.expected_result:
            is_correct, actual, error = verifier.verify_calculation(
                request.expression,
                request.expected_result
            )
            return {
                "expression": request.expression,
                "expected": request.expected_result,
                "actual": actual,
                "is_correct": is_correct,
                "error": error
            }
        else:
            is_valid, error = verifier.verify_equation(request.expression)
            return {
                "expression": request.expression,
                "is_valid": is_valid,
                "error": error
            }
            
    except Exception as e:
        logger.error(f"Math verification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify/fact")
async def verify_fact(request: VerifyFactRequest):
    """
    Test the fact checking engine against curriculum.
    
    Example:
    ```
    POST /neuro-symbolic/verify/fact
    {
        "claim": "The speed of light is 3×10^8 m/s",
        "subject": "Physics"
    }
    ```
    """
    try:
        checker = FactChecker()
        result = checker.check_response(
            request.claim,
            request.claim,
            request.subject
        )
        
        return {
            "claim": request.claim,
            "status": result.status.value,
            "confidence": result.confidence,
            "verified_facts": result.verified_facts,
            "corrections": result.corrections,
            "sources": result.sources
        }
        
    except Exception as e:
        logger.error(f"Fact check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify/response")
async def verify_response(request: VerifyResponseRequest):
    """
    Run comprehensive verification on a response.
    
    This tests all verification layers:
    - Math verification
    - Fact checking
    - Logic validation
    
    Example:
    ```
    POST /neuro-symbolic/verify/response
    {
        "response_text": "Newton's second law states F = ma...",
        "question": "Explain Newton's second law",
        "subject": "Physics"
    }
    ```
    """
    try:
        orchestrator = get_verification_orchestrator()
        result = await orchestrator.verify_response(
            response_text=request.response_text,
            question=request.question,
            subject=request.subject
        )
        
        return {
            "status": result.overall_status.value,
            "is_safe_to_show": result.is_safe_to_show,
            "confidence": result.confidence_score,
            "issues": result.issues_found,
            "corrections": result.corrections_suggested,
            "summary": result.verification_summary,
            "time_ms": result.verification_time_ms,
            "verifiers_used": result.verifiers_used,
            "badges": result.badges
        }
        
    except Exception as e:
        logger.error(f"Response verification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/search")
async def search_curriculum(request: RAGSearchRequest):
    """
    Test RAG retrieval from curriculum knowledge base.
    
    Example:
    ```
    POST /neuro-symbolic/rag/search
    {
        "query": "What is Newton's second law?",
        "subject": "Physics",
        "max_results": 3
    }
    ```
    """
    try:
        retriever = CurriculumRetriever()
        result = retriever.retrieve(
            request.query,
            request.subject,
            request.max_results
        )
        
        chunks = []
        for chunk in result.chunks:
            chunks.append({
                "topic": chunk.topic,
                "content": chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                "source": chunk.source,
                "formulas": chunk.formulas,
                "key_concepts": chunk.key_concepts
            })
        
        return {
            "query": request.query,
            "subject": request.subject,
            "total_matches": result.total_matches,
            "keywords_extracted": result.query_keywords,
            "chunks": chunks
        }
        
    except Exception as e:
        logger.error(f"RAG search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/enhance")
async def enhance_prompt(request: RAGSearchRequest):
    """
    Test RAG prompt enhancement.
    
    Shows how a prompt would be enhanced with curriculum context.
    """
    try:
        enhancer = get_rag_enhancer()
        result = enhancer.enhance_prompt(
            request.query,
            request.subject
        )
        
        return {
            "original_prompt": result.original_prompt,
            "enhanced_prompt": result.enhanced_prompt,
            "sources_used": result.sources_used,
            "formulas_available": result.formulas_available
        }
        
    except Exception as e:
        logger.error(f"RAG enhancement error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curriculum/stats")
async def get_curriculum_stats():
    """
    Get statistics about the curriculum knowledge base.
    """
    try:
        store = get_curriculum_store()
        
        subjects = list(store.subject_index.keys())
        topics_per_subject = {
            subj: len(chunk_ids) 
            for subj, chunk_ids in store.subject_index.items()
        }
        
        total_formulas = 0
        for chunk in store.chunks.values():
            total_formulas += len(chunk.formulas)
        
        return {
            "total_chunks": len(store.chunks),
            "subjects": subjects,
            "topics_per_subject": topics_per_subject,
            "total_formulas": total_formulas,
            "total_keywords": len(store.keyword_index)
        }
        
    except Exception as e:
        logger.error(f"Curriculum stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced-query")
async def run_enhanced_query(request: EnhancedQueryRequest):
    """
    Test the full enhanced supervisor pipeline.
    
    This runs the complete neuro-symbolic AI:
    1. RAG enhancement
    2. Multi-agent response
    3. Verification
    
    Example:
    ```
    POST /neuro-symbolic/enhanced-query
    {
        "question": "Explain the difference between permutations and combinations",
        "subject": "Mathematics"
    }
    ```
    """
    try:
        # Create enhanced supervisor
        supervisor = create_enhanced_supervisor()
        supervisor.configure(
            enable_rag=request.enable_rag,
            enable_verification=request.enable_verification
        )
        
        # Build context
        context = {
            "subject": request.subject,
            "user_id": request.user_id,
            "session_id": f"test_{request.user_id}",
            "exam_mode": "JEE"
        }
        
        # Run enhanced orchestration
        result = await supervisor.run_enhanced(request.question, context)
        
        # Format response for display
        return {
            "success": result.get('success', False),
            "enhanced": result.get('enhanced', False),
            "intent": result.get('intent'),
            "verification": result.get('verification', {}),
            "rag": result.get('rag', {}),
            "badge": result.get('badge'),
            "mentor_response": result.get('mentor', {}).get('content', '')[:500] if result.get('mentor') else None,
            "professor_response": result.get('professor', {}).get('content', '')[:500] if result.get('professor') else None,
            "metadata": result.get('metadata', {})
        }
        
    except Exception as e:
        logger.error(f"Enhanced query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def neuro_symbolic_health():
    """
    Health check for neuro-symbolic system.
    """
    try:
        # Check all components
        store = get_curriculum_store()
        orchestrator = get_verification_orchestrator()
        enhancer = get_rag_enhancer()
        
        return {
            "status": "healthy",
            "components": {
                "curriculum_store": {
                    "status": "active",
                    "chunks": len(store.chunks)
                },
                "verification_orchestrator": {
                    "status": "active",
                    "verifiers": orchestrator.enabled_verifiers
                },
                "rag_enhancer": {
                    "status": "active"
                }
            },
            "version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

