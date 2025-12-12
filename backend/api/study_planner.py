"""
📚 Study Planner API
====================

REST API endpoints for AI-powered study planning.
Generates personalized daily study plans based on student data.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from models.core import User
from dependencies import get_current_user, get_database
from agents.study_planner_agent import StudyPlannerAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/study-planner", tags=["Study Planner"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GeneratePlanRequest(BaseModel):
    """Request to generate a new study plan"""
    available_hours: Optional[float] = Field(default=4.0, ge=0.5, le=12.0, description="Hours available for study")
    exam_date: Optional[str] = Field(default=None, description="Target exam date (YYYY-MM-DD)")
    preferred_subjects: Optional[List[str]] = Field(default=None, description="Subjects to focus on")
    energy_pattern: Optional[str] = Field(default="morning", description="When most alert: morning, evening, flexible")


class MarkCompleteRequest(BaseModel):
    """Request to mark a block as complete"""
    block_index: int = Field(..., ge=0, description="Index of the block to mark complete")


class StudyBlockResponse(BaseModel):
    """Individual study block"""
    block_type: str
    duration_minutes: int
    topic: str
    subject: str
    description: str
    tips: List[str]
    resources: List[str]
    xp_reward: int
    priority: int
    completed: Optional[bool] = False


class DailyPlanResponse(BaseModel):
    """Complete daily study plan response"""
    date: str
    total_study_minutes: int
    total_break_minutes: int
    blocks: List[dict]
    daily_goals: List[str]
    motivational_quote: str
    streak_target: bool
    xp_target: int
    exam_countdown: Optional[int] = None
    completion_percentage: Optional[float] = 0.0


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/today", response_model=DailyPlanResponse)
async def get_today_plan(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    📅 Get today's study plan
    
    Returns the existing plan for today, or generates a new one if none exists.
    """
    try:
        planner = StudyPlannerAgent(db)
        
        # Try to get existing plan
        existing_plan = await planner.get_today_plan(user.user_id)
        
        if existing_plan:
            # Calculate completion percentage
            blocks = existing_plan.get("blocks", [])
            completed = sum(1 for b in blocks if b.get("completed", False))
            completion_pct = (completed / len(blocks) * 100) if blocks else 0
            
            return DailyPlanResponse(
                **existing_plan,
                completion_percentage=round(completion_pct, 1)
            )
        
        # Generate new plan if none exists
        plan = await planner.generate_daily_plan(user.user_id)
        
        return DailyPlanResponse(
            **plan.to_dict(),
            completion_percentage=0.0
        )
        
    except Exception as e:
        logger.error(f"Error getting today's plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get study plan: {str(e)}")


@router.post("/generate", response_model=DailyPlanResponse)
async def generate_new_plan(
    request: GeneratePlanRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🎯 Generate a new personalized study plan
    
    Creates an optimized daily study plan based on:
    - Available study time
    - Exam countdown (if provided)
    - Preferred subjects
    - Current mastery levels
    - Spaced repetition schedule
    """
    try:
        planner = StudyPlannerAgent(db)
        
        # Parse exam date if provided
        exam_date = None
        if request.exam_date:
            try:
                exam_date = datetime.strptime(request.exam_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid exam date format. Use YYYY-MM-DD")
        
        # Generate personalized plan
        plan = await planner.generate_daily_plan(
            user_id=user.user_id,
            available_hours=request.available_hours,
            exam_date=exam_date,
            preferred_subjects=request.preferred_subjects,
            energy_pattern=request.energy_pattern or "morning"
        )
        
        logger.info(f"📚 Generated new study plan for {user.user_id}")
        
        return DailyPlanResponse(
            **plan.to_dict(),
            completion_percentage=0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating study plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")


@router.post("/complete-block")
async def complete_study_block(
    request: MarkCompleteRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    ✅ Mark a study block as completed
    
    Awards XP and updates plan progress.
    """
    try:
        planner = StudyPlannerAgent(db)
        
        result = await planner.mark_block_complete(
            user_id=user.user_id,
            block_index=request.block_index
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to mark complete"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing study block: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete block: {str(e)}")


@router.get("/history")
async def get_plan_history(
    days: int = 7,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    📊 Get study plan history
    
    Returns past study plans and completion stats.
    """
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Query past plans
        cursor = db.daily_study_plans.find({
            "user_id": user.user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).sort("created_at", -1)
        
        plans = await cursor.to_list(length=days)
        
        # Calculate stats
        total_study_minutes = 0
        total_completed_blocks = 0
        total_blocks = 0
        
        history = []
        for p in plans:
            plan_data = p.get("plan", {})
            blocks = plan_data.get("blocks", [])
            completed = sum(1 for b in blocks if b.get("completed", False))
            
            total_study_minutes += plan_data.get("total_study_minutes", 0)
            total_completed_blocks += completed
            total_blocks += len(blocks)
            
            history.append({
                "date": plan_data.get("date"),
                "total_study_minutes": plan_data.get("total_study_minutes", 0),
                "blocks_completed": completed,
                "total_blocks": len(blocks),
                "xp_earned": sum(b.get("xp_reward", 0) for b in blocks if b.get("completed", False))
            })
        
        return {
            "history": history,
            "summary": {
                "total_study_hours": round(total_study_minutes / 60, 1),
                "completion_rate": round(total_completed_blocks / total_blocks * 100, 1) if total_blocks else 0,
                "days_tracked": len(plans)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting plan history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/recommendations")
async def get_study_recommendations(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    💡 Get personalized study recommendations
    
    AI-powered suggestions based on performance patterns.
    """
    try:
        # Get user's weak areas
        weak_cursor = db.concept_knowledge.find({
            "user_id": user.user_id,
            "mastery_level": {"$lt": 0.6}
        }).sort("mastery_level", 1).limit(5)
        
        weak_areas = await weak_cursor.to_list(length=5)
        
        # Get due reviews count
        now = datetime.now(timezone.utc)
        due_count = await db.spaced_repetition_items.count_documents({
            "user_id": user.user_id,
            "next_review_at": {"$lte": now}
        })
        
        # Get recent study streak
        streak = 0
        try:
            user_doc = await db.users.find_one({"user_id": user.user_id})
            streak = user_doc.get("current_streak", 0) if user_doc else 0
        except:
            pass
        
        recommendations = []
        
        # Recommendation 1: Spaced repetition
        if due_count > 0:
            recommendations.append({
                "type": "urgent",
                "icon": "🔄",
                "title": f"{due_count} concepts due for review",
                "description": "Complete spaced repetition to prevent forgetting",
                "action": "Start Revision",
                "priority": 1
            })
        
        # Recommendation 2: Weak areas
        if weak_areas:
            weak_topic = weak_areas[0].get("concept_name", "a topic")
            recommendations.append({
                "type": "focus",
                "icon": "🎯",
                "title": f"Focus on {weak_topic}",
                "description": f"Your mastery is below 60%. Dedicate focused time today.",
                "action": "Practice Now",
                "priority": 2
            })
        
        # Recommendation 3: Streak
        if streak >= 3:
            recommendations.append({
                "type": "motivation",
                "icon": "🔥",
                "title": f"{streak} day streak! Keep going!",
                "description": "You're building great habits. Don't break the chain!",
                "action": "Continue",
                "priority": 3
            })
        else:
            recommendations.append({
                "type": "motivation",
                "icon": "✨",
                "title": "Start a study streak today",
                "description": "Study consistently to build momentum and habits",
                "action": "Begin",
                "priority": 3
            })
        
        # Recommendation 4: Time-based
        hour = datetime.now(timezone.utc).hour
        if 5 <= hour < 10:
            recommendations.append({
                "type": "timing",
                "icon": "🌅",
                "title": "Morning is best for new learning",
                "description": "Your brain is fresh - tackle difficult concepts now",
                "action": "Learn New",
                "priority": 4
            })
        elif 14 <= hour < 18:
            recommendations.append({
                "type": "timing",
                "icon": "☀️",
                "title": "Afternoon is great for practice",
                "description": "Apply what you've learned with problem solving",
                "action": "Practice",
                "priority": 4
            })
        
        return {
            "recommendations": sorted(recommendations, key=lambda x: x["priority"]),
            "weak_areas_count": len(weak_areas),
            "due_reviews_count": due_count,
            "current_streak": streak
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")













