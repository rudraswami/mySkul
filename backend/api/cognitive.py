"""
Cognitive Model API - Student Intelligence Endpoints
=====================================================

Exposes the Student Cognitive Model for:
- Getting personalized learning recommendations
- Tracking knowledge and mastery
- Recording assessments and interactions
- Session management

These endpoints power the adaptive learning experience.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from dependencies import get_current_user, get_database
from models.core import User
from services.cognitive_model import AdaptiveEngine, get_adaptive_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cognitive", tags=["Cognitive Model"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class KnowledgeRequest(BaseModel):
    """Request for knowledge state"""
    subject: Optional[str] = None


class InteractionRequest(BaseModel):
    """Record a learning interaction"""
    subject: str
    topic: str
    concepts: List[str]
    response_type: str = "explanation"  # explanation, example, visual, practice
    engagement: Optional[Dict[str, Any]] = None


class AssessmentRequest(BaseModel):
    """Record an assessment result"""
    subject: str
    topic: str
    concept: str
    correct: bool
    mistake_type: Optional[str] = None  # calculation_error, conceptual_confusion, etc.


class SessionRequest(BaseModel):
    """Record session completion"""
    topics_covered: List[str]
    duration_minutes: int


class AdaptiveContextRequest(BaseModel):
    """Request for adaptive context"""
    subject: str
    topic: str
    session_length_minutes: int = 0


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/knowledge")
async def get_student_knowledge(
    subject: Optional[str] = None,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get comprehensive knowledge state for the student.
    
    Returns:
    - Overall mastery level
    - Subject-by-subject breakdown
    - Topic mastery within each subject
    - Knowledge gaps and recommendations
    
    Use this to show student their learning dashboard.
    """
    try:
        engine = get_adaptive_engine(db)
        knowledge = await engine.knowledge_tracker.get_student_knowledge(
            user_id=user.user_id,
            subject=subject
        )
        
        return {
            "success": True,
            "data": knowledge
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mastery/{subject}")
async def get_subject_mastery(
    subject: str,
    topic: Optional[str] = None,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get mastery level for a specific subject/topic.
    
    Returns:
    - Mastery score (0.0 to 1.0)
    - Confidence in the estimate
    - Related topic mastery
    """
    try:
        engine = get_adaptive_engine(db)
        
        mastery = await engine.knowledge_tracker.get_mastery_level(
            user_id=user.user_id,
            subject=subject,
            topic=topic
        )
        
        weak_areas = await engine.knowledge_tracker.get_weak_areas(
            user_id=user.user_id,
            subject=subject,
            limit=5
        )
        
        return {
            "success": True,
            "subject": subject,
            "topic": topic,
            "mastery": mastery,
            "weak_areas": weak_areas
        }
        
    except Exception as e:
        logger.error(f"Failed to get mastery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_learning_recommendations(
    subject: Optional[str] = None,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get personalized learning recommendations.
    
    Returns:
    - Topics to study next
    - Concepts needing review
    - Knowledge gaps to address
    - Study suggestions
    """
    try:
        engine = get_adaptive_engine(db)
        
        recommendations = await engine.get_recommended_content(
            user_id=user.user_id,
            subject=subject
        )
        
        return {
            "success": True,
            "data": recommendations
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review-queue")
async def get_review_queue(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get concepts that need review (spaced repetition).
    
    Returns prioritized list of concepts to review
    based on forgetting curve and mastery level.
    """
    try:
        engine = get_adaptive_engine(db)
        
        queue = await engine.knowledge_tracker.get_review_queue(
            user_id=user.user_id,
            limit=limit
        )
        
        return {
            "success": True,
            "review_items": queue,
            "count": len(queue)
        }
        
    except Exception as e:
        logger.error(f"Failed to get review queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context")
async def get_adaptive_context(
    request: AdaptiveContextRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get adaptive context for personalizing a response.
    
    Call this before generating AI responses to get
    personalization parameters for the student.
    
    Returns:
    - Learning style preferences
    - Current mastery level
    - Knowledge gaps
    - Difficulty recommendations
    - Engagement status
    """
    try:
        engine = get_adaptive_engine(db)
        
        context = await engine.get_adaptive_context(
            user_id=user.user_id,
            subject=request.subject,
            topic=request.topic,
            current_session_length=request.session_length_minutes
        )
        
        return {
            "success": True,
            "context": {
                "user_id": context.user_id,
                "current_topic_mastery": context.current_topic_mastery,
                "primary_learning_style": context.primary_learning_style,
                "include_visuals": context.include_visuals,
                "include_examples": context.include_examples,
                "include_practice": context.include_practice,
                "explanation_depth": context.explanation_depth,
                "difficulty_level": context.difficulty_level,
                "focus_areas": context.focus_areas,
                "engagement_status": context.engagement_status,
                "recommended_next_topics": context.recommended_next_topics,
                "review_needed": context.review_needed
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get adaptive context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction")
async def record_interaction(
    request: InteractionRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Record a learning interaction.
    
    Call this after every AI response to update the
    student's cognitive model with what they learned.
    """
    try:
        engine = get_adaptive_engine(db)
        
        await engine.record_response_interaction(
            user_id=user.user_id,
            subject=request.subject,
            topic=request.topic,
            concepts_covered=request.concepts,
            response_type=request.response_type,
            engagement_signals=request.engagement
        )
        
        return {
            "success": True,
            "message": "Interaction recorded",
            "concepts_tracked": len(request.concepts)
        }
        
    except Exception as e:
        logger.error(f"Failed to record interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assessment")
async def record_assessment(
    request: AssessmentRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Record an assessment result (quiz, practice problem).
    
    This is the primary way to update mastery -
    actual performance data from quizzes/problems.
    
    Returns updated mastery for the concept.
    """
    try:
        engine = get_adaptive_engine(db)
        
        result = await engine.record_assessment(
            user_id=user.user_id,
            subject=request.subject,
            topic=request.topic,
            concept=request.concept,
            correct=request.correct,
            mistake_type=request.mistake_type
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to record assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/complete")
async def complete_session(
    request: SessionRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Record session completion and get summary.
    
    Call this when the student ends a study session
    to get a summary and update learning patterns.
    """
    try:
        engine = get_adaptive_engine(db)
        
        summary = await engine.get_session_summary(
            user_id=user.user_id,
            session_topics=request.topics_covered,
            session_duration=request.duration_minutes
        )
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_learning_profile(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get the student's learning profile.
    
    Returns:
    - Learning style preferences
    - Best study times
    - Common mistake patterns
    - Personalization recommendations
    """
    try:
        engine = get_adaptive_engine(db)
        
        profile = await engine.learning_analyzer.get_learning_profile(user.user_id)
        adaptations = await engine.learning_analyzer.get_adaptation_recommendations(user.user_id)
        
        return {
            "success": True,
            "profile": {
                "primary_style": profile.primary_learning_style.value,
                "visual_preference": profile.visual_preference,
                "textual_preference": profile.textual_preference,
                "interactive_preference": profile.interactive_preference,
                "example_preference": profile.example_preference,
                "conceptual_preference": profile.conceptual_preference,
                "best_hours": profile.best_hours,
                "optimal_session_duration": profile.optimal_session_duration,
                "common_mistakes": profile.common_mistake_types,
                "prefers_hinglish": profile.prefers_hinglish
            },
            "adaptations": adaptations
        }
        
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INTERNAL INTEGRATION ENDPOINT
# ============================================================================

@router.get("/adapt-prompt")
async def get_prompt_adaptations(
    subject: str,
    topic: str,
    session_minutes: int = 0,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Internal endpoint: Get prompt adaptations for AI pipeline.
    
    Used by the verified response service to personalize prompts.
    """
    try:
        engine = get_adaptive_engine(db)
        
        context = await engine.get_adaptive_context(
            user_id=user.user_id,
            subject=subject,
            topic=topic,
            current_session_length=session_minutes
        )
        
        # Return just the adaptation instructions
        adaptations = []
        
        if context.primary_learning_style == "visual":
            adaptations.append("Include visual descriptions and suggest diagrams")
        elif context.primary_learning_style == "example":
            adaptations.append("Lead with concrete examples before theory")
        
        if context.difficulty_level == "easier":
            adaptations.append("Use simpler language and smaller steps")
        elif context.difficulty_level == "challenging":
            adaptations.append("Include advanced applications")
        
        if context.focus_areas:
            adaptations.append(f"Connect to: {', '.join(context.focus_areas[:2])}")
        
        return {
            "success": True,
            "adaptations": adaptations,
            "mastery": context.current_topic_mastery,
            "style": context.primary_learning_style,
            "depth": context.explanation_depth
        }
        
    except Exception as e:
        logger.error(f"Failed to get adaptations: {e}")
        return {"success": False, "adaptations": [], "error": str(e)}

