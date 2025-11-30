"""
Metaphor/Visual Generation API (V3.0)
POST /api/metaphors/generate
Generates visual blueprints using Whiteboard Engine.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/metaphors", tags=["Metaphors"])


class GenerateRequest(BaseModel):
    question: str
    student_dna: Optional[Dict[str, Any]] = None
    subject: Optional[str] = None


class VisualBeat(BaseModel):
    beat_type: str
    label: str
    emoji: str
    insight: str
    duration_ms: int


class GenerateResponse(BaseModel):
    success: bool
    concept: str
    title: str
    title_hindi: str
    beats: List[Dict[str, Any]]
    total_duration_ms: int
    indian_context: str
    memory_hook: str
    template: str


def _extract_marks(text: str) -> int:
    import re
    m = re.search(r"(\d+)\s*marks?", text.lower())
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass
    return 3


@router.post("/generate", response_model=GenerateResponse)
async def generate_metaphors(req: GenerateRequest):
    """Generate visual blueprint using Whiteboard Engine V3.0."""
    try:
        from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine

        # Extract concept from question
        concept = whiteboard_engine.extract_concept(req.question)
        
        if not concept:
            raise HTTPException(
                status_code=400,
                detail="No visual concept detected. Available concepts: " + 
                       ", ".join(whiteboard_engine.get_available_concepts()[:10])
            )

        # Get subject
        subject = req.subject or "physics"
        if req.student_dna and "subject" in req.student_dna:
            subject = req.student_dna["subject"]

        # Generate visual
        visual = generate_whiteboard_visual(
            concept=concept,
            subject=subject,
            question=req.question
        )

        return GenerateResponse(
            success=True,
            concept=concept,
            title=visual.get("title", ""),
            title_hindi=visual.get("title_hindi", ""),
            beats=visual.get("beats", []),
            total_duration_ms=visual.get("total_duration_ms", 10000),
            indian_context=visual.get("indian_context", ""),
            memory_hook=visual.get("encouragement", {}).get("end", ""),
            template=visual.get("template", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/metaphors/generate failed: {e}")


@router.get("/concepts")
async def get_concepts(subject: Optional[str] = None):
    """Get available visual concepts."""
    from services.whiteboard_engine import whiteboard_engine
    
    concepts = whiteboard_engine.get_available_concepts(subject)
    stats = whiteboard_engine.get_stats()
    
    return {
        "success": True,
        "subject": subject or "all",
        "concepts": concepts,
        "count": len(concepts),
        "stats": stats
    }


@router.get("/health")
async def health_check():
    """Health check for metaphor API."""
    from services.whiteboard_engine import whiteboard_engine
    
    return {
        "status": "healthy",
        "version": "3.0",
        "engine": "whiteboard_engine",
        "stats": whiteboard_engine.get_stats()
    }
