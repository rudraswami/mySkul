"""
SketchSense API Endpoints (V3.0)
================================
REST API for generating visual blueprints using the Whiteboard Engine.

Updated to use whiteboard_engine instead of legacy sketchsense_v2.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging

from services.whiteboard_engine import (
    generate_whiteboard_visual,
    whiteboard_engine
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sketchsense", tags=["Visual Engine V3"])


class BlueprintRequest(BaseModel):
    """Request model for blueprint generation."""
    concept: str = Field(..., description="Concept to visualize")
    subject: str = Field(..., description="Subject area")
    question: Optional[str] = Field(None, description="Original student question")
    student_context: Optional[Dict[str, Any]] = Field(None, description="Student profile")
    config: Optional[Dict[str, Any]] = Field(None, description="Style config options")


class BlueprintResponse(BaseModel):
    """Response model for blueprint generation."""
    success: bool
    blueprint: Dict[str, Any]
    concept: str
    subject: str
    version: str = "3.0"


class EnhanceRequest(BaseModel):
    """Request model for enhancing existing visuals."""
    existing_visual: Dict[str, Any] = Field(..., description="Existing visual to enhance")
    concept: str = Field(..., description="Concept being visualized")
    subject: str = Field(..., description="Subject area")


class EnhanceResponse(BaseModel):
    """Response model for enhanced visuals."""
    success: bool
    enhanced_visual: Dict[str, Any]
    enhancement_applied: bool


@router.post("/blueprint", response_model=BlueprintResponse)
async def generate_blueprint(request: BlueprintRequest) -> BlueprintResponse:
    """Generate a visual blueprint for a concept using Whiteboard Engine."""
    try:
        logger.info(f"Generating visual blueprint for: {request.concept}")
        
        blueprint = generate_whiteboard_visual(
            concept=request.concept,
            subject=request.subject,
            question=request.question
        )
        
        return BlueprintResponse(
            success=True,
            blueprint=blueprint,
            concept=request.concept,
            subject=request.subject,
            version="3.0"
        )
    
    except Exception as e:
        logger.error(f"Error generating blueprint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_visual(request: EnhanceRequest) -> EnhanceResponse:
    """Enhance existing visual with additional whiteboard features."""
    try:
        # Generate new visual for the concept
        enhanced = generate_whiteboard_visual(
            concept=request.concept,
            subject=request.subject
        )
        
        # Merge with existing visual
        if request.existing_visual:
            enhanced["original_visual"] = request.existing_visual
            enhanced["enhanced"] = True
        
        return EnhanceResponse(
            success=True,
            enhanced_visual=enhanced,
            enhancement_applied=True
        )
    
    except Exception as e:
        logger.error(f"Error enhancing visual: {e}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.get("/concepts")
async def get_available_concepts():
    """Get all available visual concepts."""
    return {
        "success": True,
        "concepts": whiteboard_engine.get_available_concepts(),
        "stats": whiteboard_engine.get_stats()
    }


@router.get("/concepts/{subject}")
async def get_concepts_by_subject(subject: str):
    """Get available concepts for a specific subject."""
    concepts = whiteboard_engine.get_available_concepts(subject)
    return {
        "success": True,
        "subject": subject,
        "concepts": concepts,
        "count": len(concepts)
    }


@router.get("/health")
async def health_check():
    """Health check for Visual Engine API."""
    return {
        "status": "healthy",
        "version": "3.0",
        "service": "Whiteboard Visual Engine",
        "stats": whiteboard_engine.get_stats()
    }
