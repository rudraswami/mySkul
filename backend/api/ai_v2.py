"""
🧠 AI Sathi v2.0 API - Intelligent Multi-Agent Pipeline
========================================================

REPLACES: USE_UNIFIED_FIRST = True (the flawed default path)

This endpoint uses the new UnifiedAIOrchestrator which:
1. Intelligently routes queries based on complexity
2. Uses multi-agent collaboration by DEFAULT (not as fallback)
3. Includes in-loop verification
4. Provides synchronized visual reasoning
5. Uses chain-of-thought for complex queries

This is the recommended endpoint for production.
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from dependencies import get_current_user, get_database
from models.core import User

logger = logging.getLogger(__name__)

# Router for v2 endpoints
router = APIRouter(prefix="/ai/v2", tags=["ai-v2"])


class ChatRequestV2(BaseModel):
    """Request model for v2 chat endpoint"""
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    subject: Optional[str] = Field(None, description="Subject area")
    exam_mode: Optional[str] = Field("General", description="Exam type")
    request_visual: bool = Field(False, description="Request visual explanation")
    enable_cot: bool = Field(True, description="Enable chain-of-thought reasoning")


class ChatResponseV2(BaseModel):
    """Response model for v2 chat endpoint"""
    success: bool
    response: Dict[str, Any]
    pipeline_used: str
    complexity: str
    agents_involved: List[str]
    generation_time: float
    orchestration: Dict[str, Any]
    visual_data: Optional[Dict[str, Any]] = None
    reasoning_chain: Optional[List[Dict[str, Any]]] = None


@router.post("/chat", response_model=ChatResponseV2)
async def chat_v2(
    request: ChatRequestV2,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🧠 AI Sathi v2.0 Chat Endpoint
    
    This endpoint provides intelligent, multi-agent AI tutoring with:
    - Smart routing based on query complexity
    - Multi-agent collaboration (not single LLM)
    - In-loop verification for accuracy
    - Synchronized visual reasoning
    - Chain-of-thought for complex queries
    
    ALWAYS uses the advanced pipeline - no bypassing.
    """
    start_time = datetime.now()
    
    logger.info(f"🧠 v2 Chat: {request.message[:60]}...")
    
    try:
        # Get LLM key
        llm_key = os.environ.get('OPENAI_API_KEY')
        if not llm_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Import the new orchestrator
        from services.unified_ai_orchestrator import get_unified_orchestrator
        
        orchestrator = get_unified_orchestrator(db, llm_key)
        
        # Get message history if session exists
        message_history = []
        if request.session_id:
            try:
                from services.ai_service import AIService
                ai_service = AIService(db, llm_key, db)
                history = await ai_service.get_session_messages(request.session_id, user.user_id)
                message_history = history[-10:] if history else []
            except Exception as e:
                logger.warning(f"Could not get message history: {e}")
        
        # Build context
        context = {
            "request_visual": request.request_visual,
            "enable_cot": request.enable_cot,
            "user_name": user.full_name.split()[0] if user.full_name else ""
        }
        
        # Process through orchestrator
        result = await orchestrator.process(
            user_id=user.user_id,
            session_id=request.session_id or f"temp_{user.user_id}_{datetime.now().timestamp()}",
            message=request.message,
            subject=request.subject,
            exam_mode=request.exam_mode or "General",
            message_history=message_history,
            context=context
        )
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Extract orchestration info
        orchestration = result.get("orchestration", {})
        
        return ChatResponseV2(
            success=True,
            response=result.get("response", {}),
            pipeline_used=orchestration.get("pipeline", "unknown"),
            complexity=orchestration.get("complexity", "unknown"),
            agents_involved=orchestration.get("agents_activated", []),
            generation_time=generation_time,
            orchestration=orchestration,
            visual_data=result.get("visual_data"),
            reasoning_chain=result.get("reasoning_chain")
        )
        
    except Exception as e:
        logger.error(f"❌ v2 Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/cot")
async def chat_with_cot(
    request: ChatRequestV2,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🧠 Chain of Thought Chat Endpoint
    
    Uses explicit chain-of-thought reasoning with verification.
    Best for complex mathematical or logical problems.
    """
    logger.info(f"🧠 CoT Chat: {request.message[:60]}...")
    
    try:
        llm_key = os.environ.get('OPENAI_API_KEY')
        
        from services.chain_of_thought_engine import get_chain_of_thought_engine
        
        cot_engine = get_chain_of_thought_engine({
            "emergent_llm_key": llm_key,
            "max_steps": 15,
            "timeout": 45
        })
        
        # Run chain of thought
        cot_result = await cot_engine.reason(
            query=request.message,
            subject=request.subject or "General",
            context={
                "user_id": user.user_id,
                "session_id": request.session_id
            }
        )
        
        return {
            "success": True,
            "response": {
                "content": cot_result.final_answer,
                "reasoning_steps": [s.to_dict() for s in cot_result.steps],
                "confidence": cot_result.overall_confidence
            },
            "verification": cot_result.verification_summary,
            "generation_time": cot_result.to_dict().get("duration_ms", 0) / 1000,
            "total_steps": cot_result.total_steps,
            "warnings": cot_result.warnings
        }
        
    except Exception as e:
        logger.error(f"❌ CoT Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/status")
async def get_agents_status(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get status of all AI agents and components.
    """
    status = {
        "routing_engine": False,
        "enhanced_composer": False,
        "supervisor": False,
        "agent_negotiator": False,
        "cot_engine": False,
        "visual_engine": False,
        "knowledge_graph": False
    }
    
    # Check each component
    try:
        from services.intelligent_routing_engine import get_routing_engine
        get_routing_engine(db)
        status["routing_engine"] = True
    except Exception:
        pass
    
    try:
        llm_key = os.environ.get('OPENAI_API_KEY')
        from services.enhanced_response_composer import get_enhanced_composer
        get_enhanced_composer(db, llm_key)
        status["enhanced_composer"] = True
    except Exception:
        pass
    
    try:
        from agents.enhanced_supervisor import EnhancedSupervisor
        status["supervisor"] = True
    except Exception:
        pass
    
    try:
        from services.cognitive_model.agent_negotiation import get_agent_negotiator
        get_agent_negotiator()
        status["agent_negotiator"] = True
    except Exception:
        pass
    
    try:
        from services.chain_of_thought_engine import get_chain_of_thought_engine
        get_chain_of_thought_engine()
        status["cot_engine"] = True
    except Exception:
        pass
    
    try:
        from services.synchronized_visual_engine import get_synchronized_visual_engine
        get_synchronized_visual_engine()
        status["visual_engine"] = True
    except Exception:
        pass
    
    try:
        from services.knowledge_base.ncert_curriculum_loader import init_curriculum
        status["knowledge_graph"] = True
    except Exception:
        pass
    
    # Calculate overall health
    active = sum(1 for v in status.values() if v)
    total = len(status)
    health = "healthy" if active == total else "degraded" if active > total // 2 else "critical"
    
    return {
        "components": status,
        "active": active,
        "total": total,
        "health": health,
        "version": "2.0.0"
    }


@router.post("/knowledge/load")
async def load_knowledge_graph(
    user: User = Depends(get_current_user)
):
    """
    Load NCERT curriculum into knowledge graph.
    Admin endpoint to initialize/refresh knowledge.
    """
    try:
        from services.knowledge_base.ncert_curriculum_loader import load_curriculum_to_graph
        
        graph = load_curriculum_to_graph()
        
        if graph:
            return {
                "success": True,
                "message": "Knowledge graph loaded successfully",
                "concepts_loaded": len(graph.nodes) if hasattr(graph, 'nodes') else 0,
                "relationships": len(graph.edges) if hasattr(graph, 'edges') else 0
            }
        else:
            return {
                "success": False,
                "message": "Failed to load knowledge graph"
            }
            
    except Exception as e:
        logger.error(f"Knowledge load error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complexity/{message}")
async def analyze_complexity(
    message: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Analyze query complexity and get routing decision.
    Useful for debugging and understanding the system.
    """
    try:
        from services.intelligent_routing_engine import get_routing_engine
        
        engine = get_routing_engine(db)
        decision = await engine.route(message, {"subject": "General"})
        
        return {
            "message": message,
            "complexity": decision.complexity.value,
            "pipeline": decision.pipeline.value,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "agents_to_activate": decision.agents_to_activate,
            "tools_to_enable": decision.tools_to_enable,
            "max_iterations": decision.max_iterations,
            "timeout_seconds": decision.timeout_seconds
        }
        
    except Exception as e:
        logger.error(f"Complexity analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

