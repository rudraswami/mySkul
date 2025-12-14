"""
🧠 Agentic AI API Endpoints
===========================

API endpoints for the true agentic AI system.
These endpoints use the ReAct reasoning loop with:
- Tool usage (calculator, search, fact-check)
- Memory (student patterns)
- Planning (task decomposition)
- Self-verification

Endpoints:
- POST /agentic/query - Main agentic query endpoint
- POST /agentic/doubt - Specialized doubt resolver
- GET /agentic/tools - List available tools
- GET /agentic/health - Health check
"""

import logging
import os
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agentic", tags=["Agentic AI"])


# ===================== REQUEST/RESPONSE MODELS =====================

class AgenticQueryRequest(BaseModel):
    """Request for agentic query"""
    question: str = Field(..., description="The student's question")
    subject: Optional[str] = Field(None, description="Subject (auto-detected if not provided)")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    include_reasoning: bool = Field(True, description="Include reasoning chain in response")
    max_iterations: int = Field(10, description="Max reasoning iterations")


class AgenticDoubtRequest(BaseModel):
    """Request for agentic doubt resolution"""
    doubt: str = Field(..., description="The student's doubt/confusion")
    topic: Optional[str] = Field(None, description="Topic the doubt is about")
    subject: Optional[str] = Field(None, description="Subject area")
    session_id: Optional[str] = Field(None, description="Session ID")
    preferred_style: Optional[str] = Field(None, description="Preferred explanation style: simple, detailed, analogy, step-by-step")


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain"""
    step: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None


class AgenticResponse(BaseModel):
    """Response from agentic system"""
    success: bool
    answer: str
    confidence: float = Field(..., ge=0, le=1)
    reasoning_chain: Optional[List[ReasoningStep]] = None
    tools_used: List[str] = []
    iterations: int
    verified: bool = False
    verification_details: Optional[str] = None
    execution_time_ms: float
    agent: str


class ToolInfo(BaseModel):
    """Information about an available tool"""
    name: str
    description: str
    parameters: Dict[str, str]


# ===================== ENDPOINTS =====================

@router.post("/query", response_model=AgenticResponse)
async def agentic_query(
    request: AgenticQueryRequest,
    user = Depends(get_current_user)
):
    """
    🧠 Main Agentic Query Endpoint
    
    This endpoint uses the full agentic system with:
    - ReAct reasoning loop (Think → Act → Observe)
    - Tool usage (calculator, knowledge search, etc.)
    - Memory (remembers student patterns)
    - Self-verification
    
    Example:
    ```
    POST /agentic/query
    {
        "question": "Calculate the velocity of a ball dropped from 100m",
        "subject": "Physics"
    }
    ```
    """
    start_time = datetime.now()
    
    try:
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        # Get LLM key
        llm_key = os.environ.get('OPENAI_API_KEY')
        
        if not llm_key:
            raise HTTPException(status_code=500, detail="LLM API key not configured")
        
        # Create agent
        agent = create_agentic_doubt_resolver({
            'emergent_llm_key': llm_key,
            'max_iterations': request.max_iterations,
            'verbose': True
        })
        
        # Build context
        context = {
            "subject": request.subject or "General",
            "session_id": request.session_id or f"agentic_{user.user_id}_{datetime.now().timestamp()}",
            "user_id": user.user_id,
            "student_profile": {
                "user_name": getattr(user, 'full_name', 'Student').split()[0] if hasattr(user, 'full_name') else 'Student',
                "exam": "JEE",
                "language": "en"
            }
        }
        
        # Run agent
        logger.info(f"🧠 Agentic query from {user.user_id}: {request.question[:50]}...")
        result = await agent.run(request.question, context)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Format reasoning chain
        reasoning_chain = None
        if request.include_reasoning and result.get('reasoning_chain'):
            reasoning_chain = [
                ReasoningStep(
                    step=r['step'],
                    thought=r['thought'],
                    action=r.get('action'),
                    action_input=r.get('action_input'),
                    observation=r.get('observation')
                )
                for r in result['reasoning_chain']
            ]
        
        # Check verification
        verified = False
        verification_details = None
        if result.get('verification'):
            verified = result['verification'].get('status') == 'verified'
            verification_details = result['verification'].get('details')
        
        return AgenticResponse(
            success=result.get('success', False),
            answer=result.get('content', 'Unable to generate response'),
            confidence=result.get('confidence', 0.5),
            reasoning_chain=reasoning_chain,
            tools_used=result.get('tools_used', []),
            iterations=result.get('iterations', 0),
            verified=verified,
            verification_details=verification_details,
            execution_time_ms=execution_time,
            agent=result.get('agent', 'AgenticDoubtResolver')
        )
        
    except Exception as e:
        logger.error(f"❌ Agentic query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doubt", response_model=AgenticResponse)
async def resolve_doubt_agentically(
    request: AgenticDoubtRequest,
    user = Depends(get_current_user)
):
    """
    🤔 Agentic Doubt Resolution
    
    Specialized endpoint for resolving student doubts using
    the full agentic system. Optimized for confusion/clarification requests.
    
    The agent will:
    1. Understand the specific confusion
    2. Look up relevant concepts
    3. Find appropriate analogies
    4. Verify its explanation
    5. Adapt to student's preferred style
    
    Example:
    ```
    POST /agentic/doubt
    {
        "doubt": "I don't understand why momentum is conserved",
        "topic": "Conservation Laws",
        "subject": "Physics",
        "preferred_style": "analogy"
    }
    ```
    """
    # Enhance the doubt with topic context
    enhanced_query = request.doubt
    if request.topic:
        enhanced_query = f"[Topic: {request.topic}] {request.doubt}"
    if request.preferred_style:
        enhanced_query += f" (Please explain using {request.preferred_style})"
    
    # Use main query endpoint
    query_request = AgenticQueryRequest(
        question=enhanced_query,
        subject=request.subject,
        session_id=request.session_id,
        include_reasoning=True,
        max_iterations=8  # Fewer iterations for doubt resolution
    )
    
    return await agentic_query(query_request, user)


@router.get("/tools", response_model=List[ToolInfo])
async def list_available_tools():
    """
    🔧 List Available Tools
    
    Returns all tools available to agentic agents.
    Tools allow agents to:
    - Perform calculations
    - Search knowledge bases
    - Verify facts
    - Execute code
    """
    try:
        from agents.core.tool_registry import create_tool_registry
        
        registry = create_tool_registry(include_default=True)
        tools = []
        
        for name in registry.get_tool_names():
            tool = registry.get_tool(name)
            if tool:
                tools.append(ToolInfo(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.parameters
                ))
        
        return tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agentic_health_check():
    """
    ❤️ Agentic System Health Check
    
    Verifies all components of the agentic system are working:
    - Tool registry
    - Memory system
    - Verifier
    - Planner
    """
    health = {
        "status": "healthy",
        "components": {},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Check tool registry
        from agents.core.tool_registry import create_tool_registry
        registry = create_tool_registry(include_default=True)
        tool_count = len(registry.get_tool_names())
        health["components"]["tool_registry"] = {
            "status": "ok",
            "tools_available": tool_count
        }
    except Exception as e:
        health["components"]["tool_registry"] = {"status": "error", "error": str(e)}
        health["status"] = "degraded"
    
    try:
        # Check memory system
        from agents.core.memory import MemorySystem
        memory = MemorySystem("health_check")
        health["components"]["memory_system"] = {"status": "ok"}
    except Exception as e:
        health["components"]["memory_system"] = {"status": "error", "error": str(e)}
        health["status"] = "degraded"
    
    try:
        # Check verifier
        from agents.core.verifier import Verifier
        verifier = Verifier()
        result = verifier.verify_calculation("2 + 2 = 4")
        health["components"]["verifier"] = {
            "status": "ok",
            "test_result": result.status.value
        }
    except Exception as e:
        health["components"]["verifier"] = {"status": "error", "error": str(e)}
        health["status"] = "degraded"
    
    try:
        # Check planner
        from agents.core.planner import Planner
        planner = Planner()
        plan = planner.create_plan("Test query", {})
        health["components"]["planner"] = {
            "status": "ok",
            "test_tasks": len(plan.subtasks)
        }
    except Exception as e:
        health["components"]["planner"] = {"status": "error", "error": str(e)}
        health["status"] = "degraded"
    
    # Check LLM key
    llm_key = os.environ.get('OPENAI_API_KEY')
    health["components"]["llm_key"] = {
        "status": "ok" if llm_key else "missing",
        "configured": bool(llm_key)
    }
    if not llm_key:
        health["status"] = "degraded"
    
    return health


@router.post("/test-tool/{tool_name}")
async def test_tool(
    tool_name: str,
    params: Dict[str, Any],
    user = Depends(get_current_user)
):
    """
    🧪 Test a Specific Tool
    
    Directly test a tool without going through the full agent.
    Useful for debugging and verification.
    
    Example:
    ```
    POST /agentic/test-tool/calculator
    {
        "expression": "sqrt(16) + 2^3"
    }
    ```
    """
    try:
        from agents.core.tool_registry import create_tool_registry
        
        registry = create_tool_registry(include_default=True)
        result = await registry.execute_tool(tool_name, context={}, **params)
        
        return {
            "tool": tool_name,
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Tool test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

