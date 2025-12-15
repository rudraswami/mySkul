"""
🔮 NETRA v4.0 API - Visual Intelligence Endpoints
=================================================

Production-grade API for the Visual Intelligence Orchestrator.
Generates unique, modern, edtech-grade visuals for any educational question.

Endpoints:
    POST /api/netra/v4/generate - Generate visual for a question
    POST /api/netra/v4/analyze - Analyze question without generation
    GET  /api/netra/v4/health - Health check
    GET  /api/netra/v4/metrics - Quality metrics

Security:
    - API key stored in backend ENV only
    - Never exposed to frontend
    - Rate limited per user
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.netra_v4 import (
    VisualRequest,
    VisualResponse,
    UserContext,
    create_orchestrator_from_settings,
    NetraOrchestrator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/netra/v4", tags=["NETRA v4 Visual Intelligence"])

# ============================================
# SINGLETON ORCHESTRATOR
# ============================================

_orchestrator: Optional[NetraOrchestrator] = None


def get_orchestrator() -> NetraOrchestrator:
    """
    Get or create the Netra orchestrator singleton.
    Uses settings from core.config.
    """
    global _orchestrator
    
    if _orchestrator is None:
        try:
            _orchestrator = create_orchestrator_from_settings()
            logger.info("🔮 NETRA v4 Orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize NETRA orchestrator: {e}")
            raise HTTPException(
                status_code=500,
                detail="Visual engine not configured. Check GEMINI_API_KEY."
            )
    
    return _orchestrator


# ============================================
# REQUEST/RESPONSE MODELS (API Layer)
# ============================================

class GenerateRequest(BaseModel):
    """API request for visual generation"""
    question: str = Field(..., min_length=3, max_length=1000, description="Student's question")
    user_level: str = Field(default="intermediate", description="beginner/intermediate/advanced")
    language: str = Field(default="en", description="Language preference")
    previous_questions: list[str] = Field(default_factory=list, description="Previous questions in session")
    
    # Optional overrides
    force_style: Optional[str] = Field(None, description="Force specific visual style")
    force_intent: Optional[str] = Field(None, description="Force specific teaching intent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Explain how photosynthesis works in plants",
                "user_level": "intermediate",
                "language": "en"
            }
        }


class AnalyzeRequest(BaseModel):
    """API request for question analysis without generation"""
    question: str = Field(..., min_length=3, max_length=1000)
    user_level: str = Field(default="intermediate")


class AnalyzeResponse(BaseModel):
    """Response from question analysis"""
    success: bool
    concept: str
    sub_concepts: list[str]
    key_entities: list[str]
    relationships: list[str]
    suggested_intent: str
    suggested_style: str
    complexity: str
    detected_domain: Optional[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    components: dict


class MetricsResponse(BaseModel):
    """Quality metrics response"""
    total_generations: int
    unique_count: int
    unique_ratio: float
    recent_concepts: list[str]


# ============================================
# API ENDPOINTS
# ============================================

@router.post("/generate", response_model=VisualResponse)
async def generate_visual(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
) -> VisualResponse:
    """
    🔮 Generate a unique educational visual for a question.
    
    This endpoint:
    1. Analyzes the question to understand the concept
    2. Determines the optimal visual strategy
    3. Generates a unique image using Imagen
    4. Adds teaching metadata (hotspots, steps, annotations)
    5. Returns a complete visual package
    
    The visual is guaranteed to be:
    - Unique to this specific question
    - Modern, edtech-grade quality
    - Not a generic template or repeated pattern
    """
    logger.info(f"🔮 [API] Generate request: {request.question[:50]}...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Convert API request to internal contract
        visual_request = VisualRequest(
            question=request.question,
            context=UserContext(
                previous_questions=request.previous_questions,
                user_level=request.user_level,
                language=request.language
            ),
            force_style=request.force_style,
            force_intent=request.force_intent
        )
        
        # Generate visual
        response = await orchestrator.generate(visual_request)
        
        if response.success:
            logger.info(f"✅ [API] Visual generated successfully")
        else:
            logger.warning(f"⚠️ [API] Generation failed: {response.error}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [API] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_question(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    🧠 Analyze a question without generating a visual.
    
    Useful for:
    - Understanding what visual would be generated
    - Debugging the strategy selection
    - Pre-flight checks before generation
    """
    logger.info(f"🧠 [API] Analyze request: {request.question[:50]}...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Create minimal request
        visual_request = VisualRequest(
            question=request.question,
            context=UserContext(user_level=request.user_level)
        )
        
        # Run analysis only (no image generation)
        concept, strategy, _ = await orchestrator.strategy_resolver.resolve_complete(visual_request)
        
        return AnalyzeResponse(
            success=True,
            concept=concept.core_concept,
            sub_concepts=concept.sub_concepts,
            key_entities=concept.key_entities,
            relationships=concept.relationships,
            suggested_intent=strategy.intent.value,
            suggested_style=strategy.style.value,
            complexity=concept.complexity.value,
            detected_domain=concept.detected_domain
        )
        
    except Exception as e:
        logger.error(f"❌ [API] Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    🏥 Health check for NETRA v4 service.
    
    Checks:
    - Orchestrator initialization
    - Gemini API connectivity
    - Imagen availability
    """
    components = {
        "orchestrator": "unknown",
        "gemini": "unknown",
        "imagen": "unknown"
    }
    
    overall_status = "healthy"
    
    try:
        orchestrator = get_orchestrator()
        components["orchestrator"] = "healthy"
        
        # Test Gemini connectivity
        try:
            client = await orchestrator.strategy_resolver._get_client()
            components["gemini"] = "healthy"
        except Exception as e:
            components["gemini"] = f"unhealthy: {str(e)[:50]}"
            overall_status = "degraded"
        
        # Test Imagen connectivity
        try:
            await orchestrator.imagen_client._get_client()
            components["imagen"] = "healthy"
        except Exception as e:
            components["imagen"] = f"unhealthy: {str(e)[:50]}"
            overall_status = "degraded"
            
    except Exception as e:
        components["orchestrator"] = f"unhealthy: {str(e)[:50]}"
        overall_status = "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        service="NETRA v4 Visual Intelligence",
        version="4.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components=components
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    📊 Get quality metrics for NETRA v4.
    
    Returns:
    - Total generations
    - Unique visual count
    - Uniqueness ratio
    - Recent concepts
    """
    try:
        orchestrator = get_orchestrator()
        metrics = orchestrator.get_quality_metrics()
        
        return MetricsResponse(
            total_generations=metrics.get("total", 0),
            unique_count=metrics.get("unique_count", 0),
            unique_ratio=metrics.get("unique_ratio", 1.0),
            recent_concepts=metrics.get("recent_concepts", [])
        )
        
    except Exception as e:
        logger.error(f"❌ [API] Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-simple")
async def generate_simple(question: str) -> VisualResponse:
    """
    🚀 Simplified generation endpoint - just pass a question.
    
    Useful for quick testing and simple integrations.
    """
    request = GenerateRequest(question=question)
    return await generate_visual(request, BackgroundTasks())


# ============================================
# ERROR HANDLERS
# ============================================

@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )

