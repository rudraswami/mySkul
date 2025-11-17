"""
Memory & Learning Dashboard API
Provides endpoints for student dashboard to display memory, mastery, and learning stats
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from dependencies import get_current_user, get_database
from models.core import User
from services.memory_service import MemoryService
from services.semantic_memory import SemanticMemoryService
from services.mastery_tracker import MasteryTracker
from services.continuity_engine import ContinuityEngine
from services.spaced_repetition import SpacedRepetitionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["Memory & Learning"])


# Response Models
class MasteryResponse(BaseModel):
    topic: str
    mastery_level: int
    bucket: str  # beginner/intermediate/advanced
    last_updated: str


class LearningStatsResponse(BaseModel):
    total_concepts_learned: int
    total_questions_asked: int
    current_streak_days: int
    total_xp: int
    level: int
    accuracy_overall: float
    strong_topics: List[Dict[str, Any]]
    weak_topics: List[Dict[str, Any]]


class MemoryInsightResponse(BaseModel):
    recent_topics: List[str]
    concept_thread: List[str]
    incomplete_concepts: List[str]
    due_for_review: List[Dict[str, Any]]


@router.get("/masteries", response_model=List[MasteryResponse])
async def get_all_masteries(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get all mastery levels for student dashboard
    
    Returns mastery for each topic student has studied
    """
    try:
        mastery_tracker = MasteryTracker(db)
        
        # Get all masteries
        masteries = await mastery_tracker.get_all_masteries(user.user_id)
        
        # Format for frontend
        results = []
        for topic, level in masteries.items():
            bucket = "beginner" if level < 30 else "intermediate" if level < 70 else "advanced"
            results.append({
                "topic": topic.replace("_", " ").title(),
                "mastery_level": level,
                "bucket": bucket,
                "last_updated": "2025-11-17"  # TODO: Get from history
            })
        
        # Sort by mastery (ascending, so weak topics first)
        results.sort(key=lambda x: x["mastery_level"])
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to get masteries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mastery levels")


@router.get("/stats", response_model=LearningStatsResponse)
async def get_learning_stats(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get comprehensive learning statistics for dashboard
    
    Returns:
    - Total concepts learned
    - Questions asked
    - Streak, XP, level
    - Strong/weak topics
    """
    try:
        mastery_tracker = MasteryTracker(db)
        
        # Get user profile
        profile = await db.user_learning_profile.find_one({"user_id": user.user_id})
        
        if not profile:
            # Return defaults for new users
            return {
                "total_concepts_learned": 0,
                "total_questions_asked": 0,
                "current_streak_days": 0,
                "total_xp": 0,
                "level": 1,
                "accuracy_overall": 0.0,
                "strong_topics": [],
                "weak_topics": []
            }
        
        # Get stats
        stats = profile.get("stats", {})
        
        # Get strong and weak topics
        strong = await mastery_tracker.get_strong_topics(user.user_id, threshold=70)
        weak = await mastery_tracker.get_weak_topics(user.user_id, threshold=40)
        
        return {
            "total_concepts_learned": len(profile.get("mastery_levels", {})),
            "total_questions_asked": stats.get("total_questions", 0),
            "current_streak_days": stats.get("current_streak_days", 0),
            "total_xp": stats.get("total_xp", 0),
            "level": stats.get("level", 1),
            "accuracy_overall": stats.get("accuracy_overall", 0.0),
            "strong_topics": strong[:5],  # Top 5 strong
            "weak_topics": weak[:5]  # Top 5 weak
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get learning stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve learning statistics")


@router.get("/insights", response_model=MemoryInsightResponse)
async def get_memory_insights(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get memory insights for dashboard
    
    Returns:
    - Recent topics studied
    - Active concept thread
    - Incomplete concepts
    - Concepts due for review
    """
    try:
        continuity_engine = ContinuityEngine(db)
        sp_engine = SpacedRepetitionEngine()
        
        # Get user profile
        profile = await db.user_learning_profile.find_one({"user_id": user.user_id})
        
        if not profile:
            return {
                "recent_topics": [],
                "concept_thread": [],
                "incomplete_concepts": [],
                "due_for_review": []
            }
        
        # Get due reviews
        due_reviews = await continuity_engine.get_due_reviews(user.user_id, limit=10)
        
        # Get recent topics (last 7 days)
        recent_sessions = await db.chat_sessions.find({
            "user_id": user.user_id
        }).sort("last_updated", -1).limit(10).to_list(None)
        
        recent_topics = list(set([
            session.get("subject", "General")
            for session in recent_sessions
        ]))
        
        return {
            "recent_topics": recent_topics[:5],
            "concept_thread": profile.get("last_active_concept_thread", []),
            "incomplete_concepts": profile.get("incomplete_concepts", []),
            "due_for_review": due_reviews
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get memory insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory insights")


@router.get("/topic/{topic}/mastery")
async def get_topic_mastery_detail(
    topic: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get detailed mastery information for a specific topic
    
    Returns mastery level, history, and recommendations
    """
    try:
        mastery_tracker = MasteryTracker(db)
        
        # Get current mastery
        mastery = await mastery_tracker.get_mastery_level(user.user_id, topic)
        
        # Get user profile for history
        profile = await db.user_learning_profile.find_one({"user_id": user.user_id})
        
        history = []
        if profile:
            history = [
                h for h in profile.get("mastery_history", [])
                if h.get("topic") == topic
            ]
        
        # Generate recommendations
        recommendations = []
        if mastery < 40:
            recommendations.append("Practice basic problems")
            recommendations.append("Review fundamentals")
        elif mastery < 70:
            recommendations.append("Try intermediate problems")
            recommendations.append("Study related concepts")
        else:
            recommendations.append("Attempt advanced problems")
            recommendations.append("Teach this to others")
        
        return {
            "topic": topic,
            "mastery_level": mastery,
            "bucket": "beginner" if mastery < 30 else "intermediate" if mastery < 70 else "advanced",
            "history": history[-10:],  # Last 10 updates
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get topic mastery detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve mastery for {topic}")


@router.delete("/clear")
async def clear_all_memories(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Clear all memories for user (GDPR compliance)
    
    Privacy control - allows students to delete their learning data
    """
    try:
        semantic_memory = SemanticMemoryService(db, None)
        
        # Delete all memories (soft delete)
        count = await semantic_memory.delete_all_user_memories(user.user_id)
        
        logger.info(f"🗑️ Cleared {count} memories for user {user.user_id}")
        
        return {
            "success": True,
            "memories_deleted": count,
            "message": "All learning memories have been cleared"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear memories: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memories")


@router.get("/continuity/check")
async def check_continuity(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Check if there's an incomplete learning path
    
    Returns suggestions for continuing previous topics
    """
    try:
        # Get user profile
        profile = await db.user_learning_profile.find_one({"user_id": user.user_id})
        
        if not profile:
            return {"has_continuation": False}
        
        incomplete = profile.get("incomplete_concepts", [])
        last_topic = profile.get("last_active_topic")
        thread = profile.get("last_active_concept_thread", [])
        
        if incomplete or (last_topic and thread):
            return {
                "has_continuation": True,
                "last_topic": last_topic,
                "concept_thread": thread,
                "incomplete_concepts": incomplete,
                "suggestion": f"Continue learning {last_topic.replace('_', ' ').title()}?" if last_topic else "Pick up where you left off?"
            }
        
        return {"has_continuation": False}
        
    except Exception as e:
        logger.error(f"❌ Continuity check failed: {e}")
        return {"has_continuation": False}

