"""
Visual Teaching API Endpoints (V3.0)
Serves animated teaching visuals using Whiteboard Engine
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from dependencies import get_current_user, get_ai_service
from models.core import User
from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine
from services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/visual-teaching", tags=["visual-teaching"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TeachingVisualRequest(BaseModel):
    """Request for generating a teaching visual"""
    question: str
    subject: Optional[str] = None
    complexity: Optional[str] = None
    student_profile: Optional[Dict[str, Any]] = None
    interaction_level: Optional[str] = "medium"


class TeachingVisualResponse(BaseModel):
    """Response containing the animated teaching visual"""
    success: bool
    visual_id: str
    type: str
    beats: List[Dict[str, Any]]
    total_duration_ms: int
    metadata: Dict[str, Any]


class InteractionFeedbackRequest(BaseModel):
    """Request for submitting interaction feedback"""
    visual_id: str
    stage_index: int
    interaction_type: str
    user_response: Dict[str, Any]
    timestamp: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=TeachingVisualResponse)
async def generate_teaching_visual(
    request: TeachingVisualRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Generate an animated teaching visual using Whiteboard Engine V3.0.
    """
    try:
        # Extract concept from question
        concept = whiteboard_engine.extract_concept(request.question)
        subject = request.subject or "physics"
        
        if not concept:
            raise HTTPException(
                status_code=400,
                detail="Could not detect a visual concept from the question"
            )

        # Generate visual using whiteboard engine
        visual = generate_whiteboard_visual(
            concept=concept,
            subject=subject,
            question=request.question
        )

        response = TeachingVisualResponse(
            success=True,
            visual_id=f"wb_{concept}_{visual.get('version', '3.0')}",
            type="whiteboard",
            beats=visual.get("beats", []),
            total_duration_ms=visual.get("total_duration_ms", 10000),
            metadata={
                "concept": concept,
                "subject": subject,
                "title": visual.get("title", ""),
                "title_hindi": visual.get("title_hindi", ""),
                "template": visual.get("template", ""),
                "color_theme": visual.get("color_theme", {}),
                "indian_context": visual.get("indian_context", ""),
                "encouragement": visual.get("encouragement", {})
            }
        )

        # Log usage for analytics
        await ai_service.db.visual_analytics.insert_one({
            'user_id': user.user_id,
            'visual_id': response.visual_id,
            'question': request.question,
            'concept': concept,
            'subject': subject,
            'visual_type': 'whiteboard',
            'total_duration_ms': response.total_duration_ms,
            'num_beats': len(response.beats),
            'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        })

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visual teaching generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate teaching visual: {str(e)}"
        )


@router.post("/feedback")
async def submit_interaction_feedback(
    request: InteractionFeedbackRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Submit feedback from student interactions."""
    try:
        await ai_service.db.visual_interactions.insert_one({
            'user_id': user.user_id,
            'visual_id': request.visual_id,
            'stage_index': request.stage_index,
            'interaction_type': request.interaction_type,
            'user_response': request.user_response,
            'timestamp': request.timestamp,
            'server_timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        })

        is_correct = None
        if request.interaction_type == 'quiz' and 'correct' in request.user_response:
            is_correct = request.user_response['correct']

        return {
            'success': True,
            'feedback_stored': True,
            'is_correct': is_correct
        }

    except Exception as e:
        logger.error(f"Interaction feedback error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@router.get("/concepts")
async def get_available_concepts(subject: Optional[str] = None):
    """Get list of available visual concepts."""
    concepts = whiteboard_engine.get_available_concepts(subject)
    stats = whiteboard_engine.get_stats()
    
    return {
        'success': True,
        'subject': subject or 'all',
        'concepts': concepts,
        'count': len(concepts),
        'stats': stats
    }


@router.get("/analytics/{user_id}")
async def get_visual_analytics(
    user_id: str,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get visual learning analytics for a user."""
    try:
        if user.user_id != user_id and not getattr(user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Access denied")

        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$subject',
                'total_visuals': {'$sum': 1},
                'total_duration_ms': {'$sum': '$total_duration_ms'},
                'avg_duration_ms': {'$avg': '$total_duration_ms'},
                'concepts_used': {'$addToSet': '$concept'}
            }},
            {'$sort': {'total_visuals': -1}}
        ]

        subject_stats = await ai_service.db.visual_analytics.aggregate(pipeline).to_list(length=None)

        total_visuals = sum(stat['total_visuals'] for stat in subject_stats)
        total_duration = sum(stat['total_duration_ms'] for stat in subject_stats)

        return {
            'user_id': user_id,
            'overall_stats': {
                'total_visuals_viewed': total_visuals,
                'total_learning_time_seconds': total_duration / 1000,
                'subjects_covered': len(subject_stats)
            },
            'subject_breakdown': subject_stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.post("/quick-generate")
async def quick_generate_visual(
    question: str,
    subject: Optional[str] = None
):
    """Quick endpoint for generating visuals without authentication."""
    try:
        concept = whiteboard_engine.extract_concept(question)
        
        if not concept:
            return {
                'success': False,
                'error': 'No visual concept detected',
                'available_concepts': whiteboard_engine.get_available_concepts(subject)[:10]
            }
        
        visual = generate_whiteboard_visual(concept, subject or "physics", question)

        return {
            'success': True,
            'concept': concept,
            'visual': visual
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
