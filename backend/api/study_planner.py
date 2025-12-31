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
    Always returns at least 3 actionable recommendations.
    """
    try:
        # Get user's profile for timezone and exam info
        user_doc = await db.users.find_one({"user_id": user.user_id})
        user_timezone = user_doc.get("timezone", "Asia/Kolkata") if user_doc else "Asia/Kolkata"
        exam_type = user_doc.get("exam_type") if user_doc else None
        exam_date_str = user_doc.get("exam_date") if user_doc else None
        
        # Calculate local hour for time-based recommendations
        try:
            from zoneinfo import ZoneInfo
            local_now = datetime.now(ZoneInfo(user_timezone))
            local_hour = local_now.hour
        except Exception:
            # Fallback to IST assumption (most users are Indian students)
            local_hour = (datetime.now(timezone.utc).hour + 5) % 24  # UTC+5:30 approximation
        
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
            streak = user_doc.get("current_streak", 0) if user_doc else 0
        except:
            pass
        
        # Calculate exam countdown
        days_to_exam = None
        if exam_date_str:
            try:
                if isinstance(exam_date_str, str):
                    exam_date = datetime.fromisoformat(exam_date_str.replace('Z', '+00:00'))
                else:
                    exam_date = exam_date_str
                days_to_exam = (exam_date - datetime.now(timezone.utc)).days
            except:
                pass
        
        recommendations = []
        
        # ===== PRIORITY 1: Urgent Actions =====
        
        # Recommendation: Spaced repetition (if due)
        if due_count > 0:
            recommendations.append({
                "type": "urgent",
                "icon": "🔄",
                "title": f"{due_count} concepts due for review",
                "description": "Complete spaced repetition to prevent forgetting",
                "action": "Start Revision",
                "priority": 1
            })
        
        # Recommendation: Exam countdown (if close)
        if days_to_exam and days_to_exam <= 30:
            urgency = "⚠️" if days_to_exam <= 7 else "📅"
            recommendations.append({
                "type": "exam_countdown",
                "icon": urgency,
                "title": f"{days_to_exam} days to {exam_type or 'exam'}!",
                "description": "Focus on high-weightage topics and revision" if days_to_exam <= 7 else "Stay consistent with your study plan",
                "action": "Focus Mode",
                "priority": 1 if days_to_exam <= 7 else 2
            })
        
        # ===== PRIORITY 2: Focus Areas =====
        
        # Recommendation: Weak areas
        if weak_areas:
            weak_topic = weak_areas[0].get("concept_name", "a topic")
            mastery_pct = int(weak_areas[0].get("mastery_level", 0.5) * 100)
            recommendations.append({
                "type": "focus",
                "icon": "🎯",
                "title": f"Strengthen: {weak_topic}",
                "description": f"Currently at {mastery_pct}% mastery. Focused practice can boost this!",
                "action": "Practice Now",
                "priority": 2
            })
        
        # ===== PRIORITY 3: Motivation & Habits =====
        
        # Recommendation: Streak motivation
        if streak >= 7:
            recommendations.append({
                "type": "achievement",
                "icon": "🔥",
                "title": f"Amazing {streak}-day streak!",
                "description": "You're building champion habits. Keep the momentum!",
                "action": "Continue",
                "priority": 3
            })
        elif streak >= 3:
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
                "title": "Start your study streak today",
                "description": "Consistency beats intensity. Begin building momentum!",
                "action": "Begin",
                "priority": 3
            })
        
        # ===== PRIORITY 4: Time-Optimized Suggestions =====
        
        # Time-based recommendations (using LOCAL time)
        if 5 <= local_hour < 10:
            recommendations.append({
                "type": "timing",
                "icon": "🌅",
                "title": "Morning is best for new learning",
                "description": "Your brain is fresh - tackle difficult concepts now",
                "action": "Learn New Topic",
                "priority": 4
            })
        elif 10 <= local_hour < 14:
            recommendations.append({
                "type": "timing",
                "icon": "☀️",
                "title": "Great time for problem practice",
                "description": "You're warmed up - solve challenging problems",
                "action": "Solve Problems",
                "priority": 4
            })
        elif 14 <= local_hour < 18:
            recommendations.append({
                "type": "timing",
                "icon": "📝",
                "title": "Afternoon: Review & Practice",
                "description": "Perfect for applying what you've learned",
                "action": "Practice Session",
                "priority": 4
            })
        elif 18 <= local_hour < 21:
            recommendations.append({
                "type": "timing",
                "icon": "🌙",
                "title": "Evening revision window",
                "description": "Great for consolidating today's learning",
                "action": "Quick Revision",
                "priority": 4
            })
        else:
            recommendations.append({
                "type": "timing",
                "icon": "😴",
                "title": "Rest is important too!",
                "description": "Good sleep helps memory consolidation",
                "action": "Rest Well",
                "priority": 5
            })
        
        # ===== PRIORITY 5: Growth Tips =====
        
        # Always add a growth tip (so we always have 3+ recommendations)
        growth_tips = [
            {
                "type": "tip",
                "icon": "💡",
                "title": "Teach to learn better",
                "description": "Explaining concepts helps you understand them deeply",
                "action": "Try TeachBack",
                "priority": 5
            },
            {
                "type": "tip",
                "icon": "📊",
                "title": "Track your progress",
                "description": "Review your mastery levels weekly to stay on track",
                "action": "View Progress",
                "priority": 5
            },
            {
                "type": "tip",
                "icon": "🎯",
                "title": "Quality over quantity",
                "description": "Deep understanding beats surface-level coverage",
                "action": "Deep Focus",
                "priority": 5
            },
        ]
        
        # Add a growth tip if we have less than 4 recommendations
        if len(recommendations) < 4:
            import random
            recommendations.append(random.choice(growth_tips))
        
        # Ensure we always return at least 3 recommendations
        while len(recommendations) < 3:
            import random
            tip = random.choice(growth_tips)
            if tip not in recommendations:
                recommendations.append(tip)
        
        # Sort by priority and return top 4
        sorted_recs = sorted(recommendations, key=lambda x: x["priority"])[:4]
        
        return {
            "recommendations": sorted_recs,
            "weak_areas_count": len(weak_areas),
            "due_reviews_count": due_count,
            "current_streak": streak,
            "days_to_exam": days_to_exam,
            "exam_type": exam_type
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


























































