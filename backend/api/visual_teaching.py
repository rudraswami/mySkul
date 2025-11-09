"""
Visual Teaching API Endpoints
Serves animated teaching visuals for any concept
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from dependencies import get_current_user, get_ai_service
from models.core import User
from services.visual_teaching_engine import (
    VisualTeachingEngine,
    generate_teaching_animation
)
from services.ai_service import AIService
from services.grammar_visual_templates import get_grammar_visual_template

router = APIRouter(prefix="/api/visual-teaching", tags=["visual-teaching"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TeachingVisualRequest(BaseModel):
    """Request for generating a teaching visual"""
    question: str
    subject: Optional[str] = None
    complexity: Optional[str] = None  # simple, medium, complex
    student_profile: Optional[Dict[str, Any]] = None
    interaction_level: Optional[str] = "medium"  # low, medium, high

class TeachingVisualResponse(BaseModel):
    """Response containing the animated teaching visual"""
    success: bool
    visual_id: str
    type: str
    stages: List[Dict[str, Any]]
    total_duration_ms: int
    interaction_points: List[int]
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
    Generate an animated teaching visual for any concept

    This endpoint:
    1. Analyzes the question to understand teaching intent
    2. Maps to appropriate visual pattern
    3. Generates animated stages with narration
    4. Includes interactive elements
    5. Returns complete teaching visual data
    """
    try:
        # Check if we have a pre-built template for common topics
        template_visual = None
        question_lower = request.question.lower()

        # Check for grammar templates
        if any(keyword in question_lower for keyword in ['active', 'passive', 'voice']):
            template_visual = get_grammar_visual_template("active_passive_voice")
        elif any(keyword in question_lower for keyword in ['subject verb agreement', 'subject-verb']):
            template_visual = get_grammar_visual_template("subject_verb_agreement")
        elif any(keyword in question_lower for keyword in ['tense', 'past present future']):
            template_visual = get_grammar_visual_template("tenses")

        # If we have a template, use it directly
        if template_visual:
            visual = template_visual
        else:
            # Initialize teaching engine for dynamic generation
            engine = VisualTeachingEngine()

            # Add user context to student profile
            if not request.student_profile:
                request.student_profile = {}

            request.student_profile.update({
                'user_id': user.user_id,
                'grade': getattr(user, 'grade', 'class_12'),
                'board': getattr(user, 'board', 'CBSE'),
                'preferred_language': getattr(user, 'preferred_language', 'en'),
                'region': getattr(user, 'region', 'North')
            })

            # Generate teaching visual dynamically
            visual = await engine.generate_teaching_visual(
                question=request.question,
                subject=request.subject,
                student_profile=request.student_profile
            )

        # Convert to response format
        # Handle both dict (from template) and object (from engine)
        if isinstance(visual, dict):
            # Template visual is already in dict format
            visual_dict = visual
            stages_data = [
                {
                    'stage_id': stage.stage_id if hasattr(stage, 'stage_id') else str(stage.get('stage_id', '')),
                    'duration_ms': stage.duration_ms if hasattr(stage, 'duration_ms') else stage.get('duration_ms', 0),
                    'narration': stage.narration if hasattr(stage, 'narration') else stage.get('narration', ''),
                    'animations': stage.animations if hasattr(stage, 'animations') else stage.get('animations', []),
                    'interactions': stage.interactions if hasattr(stage, 'interactions') else stage.get('interactions'),
                    'emphasis': stage.emphasis if hasattr(stage, 'emphasis') else stage.get('emphasis')
                }
                for stage in visual_dict['stages']
            ]
        else:
            # Engine visual is an object
            visual_dict = {
                'visual_id': visual.visual_id,
                'type': visual.type,
                'total_duration_ms': visual.total_duration_ms,
                'interaction_points': visual.interaction_points,
                'metadata': visual.metadata
            }
            stages_data = [
                {
                    'stage_id': stage.stage_id,
                    'duration_ms': stage.duration_ms,
                    'narration': stage.narration,
                    'animations': stage.animations,
                    'interactions': stage.interactions,
                    'emphasis': stage.emphasis
                }
                for stage in visual.stages
            ]

        response = TeachingVisualResponse(
            success=True,
            visual_id=visual_dict.get('visual_id'),
            type=visual_dict.get('type'),
            stages=stages_data,
            total_duration_ms=visual_dict.get('total_duration_ms'),
            interaction_points=visual_dict.get('interaction_points'),
            metadata=visual_dict.get('metadata')
        )

        # Log usage for analytics
        await ai_service.db.visual_analytics.insert_one({
            'user_id': user.user_id,
            'visual_id': visual_dict.get('visual_id'),
            'question': request.question,
            'subject': request.subject or visual_dict.get('metadata', {}).get('subject'),
            'visual_type': visual_dict.get('type'),
            'pattern': visual_dict.get('metadata', {}).get('pattern') or visual_dict.get('metadata', {}).get('visual_pattern'),
            'complexity': visual_dict.get('metadata', {}).get('complexity'),
            'total_duration_ms': visual_dict.get('total_duration_ms'),
            'num_stages': len(stages_data),
            'num_interactions': len(visual_dict.get('interaction_points', [])),
            'is_template': isinstance(visual, dict),
            'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        })

        return response

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
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
    """
    Submit feedback from student interactions

    Used to:
    1. Track student responses
    2. Measure understanding
    3. Improve future visuals
    """
    try:
        # Store interaction feedback
        await ai_service.db.visual_interactions.insert_one({
            'user_id': user.user_id,
            'visual_id': request.visual_id,
            'stage_index': request.stage_index,
            'interaction_type': request.interaction_type,
            'user_response': request.user_response,
            'timestamp': request.timestamp,
            'server_timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        })

        # Analyze response for correctness if applicable
        is_correct = None
        if request.interaction_type == 'quiz' and 'correct' in request.user_response:
            is_correct = request.user_response['correct']

        return {
            'success': True,
            'feedback_stored': True,
            'is_correct': is_correct
        }

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Interaction feedback error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/patterns")
async def get_available_patterns():
    """
    Get list of available visual patterns

    Returns all supported visual patterns for different concept types
    """
    from services.visual_teaching_engine import VisualPattern, ConceptType

    patterns = {
        'visual_patterns': [
            {
                'name': pattern.value,
                'description': get_pattern_description(pattern)
            }
            for pattern in VisualPattern
        ],
        'concept_types': [
            {
                'name': concept.value,
                'description': get_concept_description(concept)
            }
            for concept in ConceptType
        ]
    }

    return patterns

@router.get("/analytics/{user_id}")
async def get_visual_analytics(
    user_id: str,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get visual learning analytics for a user

    Returns:
    - Visuals viewed
    - Interaction performance
    - Learning patterns
    """
    try:
        # Ensure user can only access their own analytics
        if user.user_id != user_id and not getattr(user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Aggregate analytics
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$subject',
                'total_visuals': {'$sum': 1},
                'total_duration_ms': {'$sum': '$total_duration_ms'},
                'avg_duration_ms': {'$avg': '$total_duration_ms'},
                'patterns_used': {'$addToSet': '$pattern'},
                'complexity_distribution': {
                    '$push': '$complexity'
                }
            }},
            {'$sort': {'total_visuals': -1}}
        ]

        subject_stats = await ai_service.db.visual_analytics.aggregate(pipeline).to_list(length=None)

        # Get interaction performance
        interaction_pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$interaction_type',
                'total_interactions': {'$sum': 1},
                'correct_responses': {
                    '$sum': {'$cond': [{'$eq': ['$user_response.correct', True]}, 1, 0]}
                }
            }}
        ]

        interaction_stats = await ai_service.db.visual_interactions.aggregate(interaction_pipeline).to_list(length=None)

        # Calculate overall metrics
        total_visuals = sum(stat['total_visuals'] for stat in subject_stats)
        total_duration = sum(stat['total_duration_ms'] for stat in subject_stats)

        return {
            'user_id': user_id,
            'overall_stats': {
                'total_visuals_viewed': total_visuals,
                'total_learning_time_seconds': total_duration / 1000,
                'subjects_covered': len(subject_stats)
            },
            'subject_breakdown': subject_stats,
            'interaction_performance': interaction_stats,
            'learning_patterns': {
                'most_used_subject': subject_stats[0]['_id'] if subject_stats else None,
                'avg_visual_duration_seconds': (total_duration / total_visuals / 1000) if total_visuals > 0 else 0,
                'interaction_rate': len(interaction_stats) / total_visuals if total_visuals > 0 else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
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
    """
    Quick endpoint for generating visuals without authentication
    Used for testing and demos
    """
    try:
        result = generate_teaching_animation(question, subject)

        return {
            'success': True,
            'visual': result
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_pattern_description(pattern):
    """Get description for visual pattern"""
    descriptions = {
        'flow_diagram': 'Step-by-step process visualization',
        'split_screen': 'Side-by-side comparison',
        'timeline': 'Chronological sequence',
        'orbit_system': 'Circular relationships and cycles',
        'balance_scale': 'Equilibrium and comparison',
        'transformation_morph': 'Change from one state to another',
        'network_graph': 'Interconnected relationships',
        'layered_stack': 'Hierarchical structure'
    }
    return descriptions.get(pattern.value, 'Visual pattern')

def get_concept_description(concept):
    """Get description for concept type"""
    descriptions = {
        'comparison': 'Comparing two or more items',
        'transformation': 'Change from one state to another',
        'process': 'Step-by-step procedure',
        'cause_effect': 'Cause and effect relationship',
        'hierarchy': 'Hierarchical organization',
        'cycle': 'Cyclical process',
        'relationship': 'Relationships between elements'
    }
    return descriptions.get(concept.value, 'Concept type')