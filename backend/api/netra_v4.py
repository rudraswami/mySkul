"""
🎬 NETRA v5.0 API - Scene-Based Visual Intelligence
====================================================

Scene-based visual rendering API. NO AI image generation (DALL-E disabled).
Returns scene data for frontend SceneRenderer to render.

The frontend uses:
- SceneObjectResolver: Converts entities → scene objects
- ScenePrimitives: Rich visual components (environments, actors, surfaces)
- SceneRenderer: Renders SVG scenes (NOT boxes!)

Endpoints:
    POST /api/netra/v4/generate - Returns scene data for frontend rendering
    POST /api/netra/v4/analyze - Analyze question (lightweight)
    GET  /api/netra/v4/health - Health check
    GET  /api/netra/v4/metrics - Metrics

NOTE: DALL-E 3 image generation is DISABLED.
      Frontend renders scenes using SceneRenderer.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/netra/v4", tags=["NETRA v5 Scene-Based Visual"])

# ============================================
# NOTE: OLD DALL-E 3 ORCHESTRATOR IS DISABLED
# Frontend now renders scenes using SceneRenderer
# ============================================


# ============================================
# REQUEST/RESPONSE MODELS (Scene-Based API)
# ============================================

class GenerateRequest(BaseModel):
    """Request for scene-based visual generation"""
    question: str = Field(..., min_length=3, max_length=1000, description="Student's question")
    user_level: str = Field(default="intermediate", description="beginner/intermediate/advanced")
    language: str = Field(default="en", description="Language preference")
    previous_questions: list = Field(default_factory=list, description="Previous questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Explain friction",
                "user_level": "intermediate",
                "language": "en"
            }
        }


class AnalyzeRequest(BaseModel):
    """Request for question analysis"""
    question: str = Field(..., min_length=3, max_length=1000)
    user_level: str = Field(default="intermediate")


# ============================================
# API ENDPOINTS
# ============================================

@router.post("/generate")
async def generate_visual(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    🎬 Generate scene data for frontend SceneRenderer.
    
    This endpoint:
    1. Analyzes the question to determine intent
    2. Returns scene data for frontend rendering
    3. Does NOT generate AI images (DALL-E disabled)
    
    The frontend will:
    - Use SceneObjectResolver to create scene objects
    - Use SceneRenderer to render SVG scenes
    - Create rich visual environments, actors, surfaces
    """
    logger.info(f"🎬 [API] Scene request: {request.question[:50]}...")
    
    try:
        q_lower = request.question.lower()
        
        # Detect intent (matches frontend IntentClassifier)
        intent = "conceptual"
        if "why" in q_lower or "how come" in q_lower or "what causes" in q_lower:
            intent = "causal_inquiry"
        elif "what if" in q_lower or "without" in q_lower or "imagine no" in q_lower:
            intent = "counterfactual"
        elif "compare" in q_lower or " vs " in q_lower or "difference" in q_lower:
            intent = "comparative"
        elif "intuitively" in q_lower or "simply" in q_lower:
            intent = "intuitive"
        elif "how does" in q_lower or "mechanism" in q_lower:
            intent = "mechanistic"
        elif "types of" in q_lower or "kinds of" in q_lower:
            intent = "classificatory"
        elif "calculate" in q_lower or "formula" in q_lower:
            intent = "quantitative"
        
        # Extract topic
        topic = request.question.replace("?", "").strip()
        if len(topic) > 60:
            topic = topic[:60] + "..."
        
        # Detect domain from question
        domain = "physics"  # default
        domain_keywords = {
            "physics": ["force", "motion", "friction", "gravity", "energy", "momentum", "wave", "light"],
            "chemistry": ["atom", "molecule", "bond", "reaction", "element", "compound", "acid", "base"],
            "biology": ["cell", "dna", "gene", "organism", "photosynthesis", "respiration", "protein"],
            "math": ["equation", "graph", "function", "theorem", "formula", "angle", "geometry"],
        }
        for d, keywords in domain_keywords.items():
            if any(kw in q_lower for kw in keywords):
                domain = d
                break
        
        # Return scene data for frontend SceneRenderer
        response = {
            "success": True,
            "type": "scene_based",
            "use_scene_renderer": True,
            "scene_data": {
                "question": request.question,
                "intent": intent,
                "domain": domain,
                "topic": topic,
                "user_level": request.user_level,
            },
            "metadata": {
                "concept": topic,
                "intent": intent,
                "domain": domain,
                "style": "scene",
                "render_mode": "scene_renderer",
            },
            "teaching": {
                "title": f"Understanding: {topic[:40]}",
                "summary": f"Visual explanation of {topic}",
                "steps": [],
                "key_takeaways": [],
            },
            "visual": None,  # No AI image - frontend renders scene
        }
        
        logger.info(f"✅ [API] Scene data: intent={intent}, domain={domain}")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"❌ [API] Scene error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    """
    🧠 Analyze a question for scene-based rendering.
    
    Returns:
    - Detected intent
    - Domain classification
    - Suggested visual form
    """
    logger.info(f"🧠 [API] Analyze request: {request.question[:50]}...")
    
    try:
        q_lower = request.question.lower()
        
        # Detect intent
        intent = "conceptual"
        if "why" in q_lower or "what causes" in q_lower:
            intent = "causal_inquiry"
        elif "what if" in q_lower or "without" in q_lower:
            intent = "counterfactual"
        elif "compare" in q_lower or " vs " in q_lower:
            intent = "comparative"
        elif "intuitively" in q_lower or "simply" in q_lower:
            intent = "intuitive"
        elif "how does" in q_lower:
            intent = "mechanistic"
        
        # Detect domain
        domain = "physics"
        domain_keywords = {
            "physics": ["force", "motion", "friction", "gravity", "energy"],
            "chemistry": ["atom", "molecule", "bond", "reaction"],
            "biology": ["cell", "dna", "photosynthesis", "organism"],
            "math": ["equation", "graph", "function", "theorem"],
        }
        for d, keywords in domain_keywords.items():
            if any(kw in q_lower for kw in keywords):
                domain = d
                break
        
        # Extract key entities (simple extraction)
        topic = request.question.replace("?", "").strip()
        
        response = {
            "success": True,
            "concept": topic[:50],
            "sub_concepts": [],
            "key_entities": [],
            "relationships": [],
            "suggested_intent": intent,
            "suggested_style": "scene",
            "complexity": "medium",
            "detected_domain": domain,
            "render_mode": "scene_renderer",
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"❌ [API] Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    🏥 Health check for NETRA v5 Scene-Based service.
    
    NOTE: DALL-E 3 is DISABLED. Frontend renders scenes.
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "NETRA v5 Scene-Based Visual",
        "version": "5.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "scene_resolver": "healthy",
            "intent_classifier": "healthy",
            "dall_e_3": "disabled",  # DALL-E is disabled!
        },
        "render_mode": "frontend_scene_renderer",
        "note": "AI image generation disabled. Frontend renders SVG scenes."
    })


@router.get("/metrics")
async def get_metrics():
    """
    📊 Metrics for NETRA v5 Scene-Based service.
    """
    return JSONResponse(content={
        "total_generations": 0,
        "unique_count": 0,
        "unique_ratio": 1.0,
        "recent_concepts": [],
        "render_mode": "scene_renderer",
        "dall_e_disabled": True,
    })


@router.post("/generate-simple")
async def generate_simple(question: str):
    """
    🚀 Simplified generation - returns scene data.
    """
    request = GenerateRequest(question=question)
    return await generate_visual(request, BackgroundTasks())


# ============================================
# NOTE: Exception handlers are registered at app level in main.py
# This router relies on the global HTTPException handling
# ============================================

