"""
🎮 Gamification API Endpoints
==============================
Handles all gamification-related requests:
- Get student stats
- Process interactions
- Award XP
- Manage streaks
- Track progress
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from services.gamification_engine import (
    get_gamification_service,
    GamificationService,
    MicroDopamineEngine,
    StreakEngine,
    XPEngine
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gamification", tags=["Gamification"])


# ============ REQUEST MODELS ============

class InteractionRequest(BaseModel):
    """Request model for processing an interaction"""
    user_id: str
    interaction_type: str = "question"  # question, answer, followup
    is_correct: bool = True
    response_time_ms: int = 0
    concept: str = ""
    subject: str = ""


class XPAwardRequest(BaseModel):
    """Request model for awarding XP"""
    user_id: str
    action: str
    multiplier: float = 1.0


# ============ RESPONSE MODELS ============

class MicroRewardResponse(BaseModel):
    """Micro reward response"""
    message: str
    emoji: str
    xp_earned: int
    celebration_type: str


class StreakResponse(BaseModel):
    """Streak information response"""
    current: int
    longest: int
    motivation: str
    badge_earned: Optional[str] = None


class LevelProgressResponse(BaseModel):
    """Level progress response"""
    level_name: str
    current_xp: int
    level_xp: int
    next_level_xp: Optional[int]
    progress_percent: float
    next_level_name: Optional[str]
    is_max_level: bool


class TodayStatsResponse(BaseModel):
    """Today's stats response"""
    questions: int
    correct: int
    accuracy: float
    time_spent: int


class StudentStatsResponse(BaseModel):
    """Complete student stats response"""
    user_id: str
    level: LevelProgressResponse
    streak: StreakResponse
    today: TodayStatsResponse
    badges: List[str]
    difficulty: str
    recommendations: List[Dict[str, Any]]


class InteractionResponse(BaseModel):
    """Response after processing an interaction"""
    micro_reward: Optional[MicroRewardResponse]
    streak_update: Dict[str, Any]
    xp_earned: int
    level_up: Optional[Dict[str, Any]]
    difficulty_change: Optional[Dict[str, Any]]
    badges_earned: List[str]
    recommendations: List[Dict[str, Any]]
    level_progress: Dict[str, Any]


# ============ ENDPOINTS ============

@router.get("/stats/{user_id}", response_model=StudentStatsResponse)
async def get_student_stats(user_id: str):
    """
    Get complete gamification stats for a student.
    
    Returns:
    - Level and XP progress
    - Current and longest streak
    - Today's activity stats
    - Earned badges
    - Personalized recommendations
    """
    try:
        service = get_gamification_service()
        stats = await service.get_student_stats(user_id)
        
        return StudentStatsResponse(
            user_id=stats["user_id"],
            level=LevelProgressResponse(
                level_name=stats["level"]["level_name"],
                current_xp=stats["level"]["current_xp"],
                level_xp=stats["level"]["level_xp"],
                next_level_xp=stats["level"].get("next_level_xp"),
                progress_percent=stats["level"]["progress_percent"],
                next_level_name=stats["level"].get("next_level_name"),
                is_max_level=stats["level"]["is_max_level"]
            ),
            streak=StreakResponse(
                current=stats["streak"]["current"],
                longest=stats["streak"]["longest"],
                motivation=stats["streak"]["motivation"]
            ),
            today=TodayStatsResponse(
                questions=stats["today"]["questions"],
                correct=stats["today"]["correct"],
                accuracy=stats["today"]["accuracy"],
                time_spent=stats["today"]["time_spent"]
            ),
            badges=stats["badges"],
            difficulty=stats["difficulty"],
            recommendations=stats["recommendations"]
        )
    except Exception as e:
        logger.error(f"Error getting student stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction", response_model=InteractionResponse)
async def process_interaction(request: InteractionRequest):
    """
    Process a student interaction and return gamification rewards.
    
    This is called after every question/answer to:
    - Update streak
    - Award XP
    - Check for level ups
    - Adjust difficulty
    - Generate micro rewards
    """
    try:
        service = get_gamification_service()
        result = await service.process_interaction(
            user_id=request.user_id,
            interaction_type=request.interaction_type,
            is_correct=request.is_correct,
            response_time_ms=request.response_time_ms,
            concept=request.concept,
            subject=request.subject
        )
        
        # Convert micro_reward to response format
        micro_reward = None
        if result.get("micro_reward"):
            mr = result["micro_reward"]
            micro_reward = MicroRewardResponse(
                message=mr.message,
                emoji=mr.emoji,
                xp_earned=mr.xp_earned,
                celebration_type=mr.celebration_type
            )
        
        return InteractionResponse(
            micro_reward=micro_reward,
            streak_update=result["streak_update"],
            xp_earned=result["xp_earned"],
            level_up=result.get("level_up"),
            difficulty_change=result.get("difficulty_change"),
            badges_earned=result["badges_earned"],
            recommendations=result["recommendations"],
            level_progress=result["level_progress"]
        )
    except Exception as e:
        logger.error(f"Error processing interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/award-xp")
async def award_xp(request: XPAwardRequest):
    """
    Manually award XP for specific actions.
    
    Actions:
    - correct_answer: 10 XP
    - fast_correct: 15 XP
    - concept_mastered: 50 XP
    - subject_completed: 200 XP
    - daily_goal_reached: 25 XP
    """
    try:
        result = XPEngine.award_xp(
            action=request.action,
            multiplier=request.multiplier
        )
        return result
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streak/{user_id}")
async def get_streak(user_id: str):
    """Get streak information for a user"""
    try:
        service = get_gamification_service()
        stats = await service.get_student_stats(user_id)
        return stats["streak"]
    except Exception as e:
        logger.error(f"Error getting streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level/{user_id}")
async def get_level(user_id: str):
    """Get level and XP information for a user"""
    try:
        service = get_gamification_service()
        stats = await service.get_student_stats(user_id)
        return stats["level"]
    except Exception as e:
        logger.error(f"Error getting level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/micro-reward/{reward_type}")
async def get_micro_reward(reward_type: str, is_fast: bool = False, streak: int = 0):
    """
    Get a micro reward message for testing/preview.
    
    Types: correct, understanding, encouragement, streak
    """
    try:
        if reward_type == "correct":
            reward = MicroDopamineEngine.get_correct_answer_reward(is_fast, streak)
        elif reward_type == "understanding":
            reward = MicroDopamineEngine.get_understanding_reward()
        elif reward_type == "encouragement":
            reward = MicroDopamineEngine.get_encouragement()
        elif reward_type == "streak":
            reward = MicroDopamineEngine.get_streak_reward(streak)
            if not reward:
                return {"message": "No streak reward for this day count"}
        else:
            raise HTTPException(status_code=400, detail="Invalid reward type")
        
        return {
            "message": reward.message,
            "emoji": reward.emoji,
            "xp_earned": reward.xp_earned,
            "celebration_type": reward.celebration_type
        }
    except Exception as e:
        logger.error(f"Error getting micro reward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """
    Get XP leaderboard (placeholder - needs database integration).
    """
    # TODO: Implement with actual database query
    return {
        "message": "Leaderboard coming soon!",
        "limit": limit
    }


@router.get("/badges/all")
async def get_all_badges():
    """Get list of all available badges"""
    badges = {
        "streak_badges": [
            {"id": "flame_starter", "name": "Flame Starter", "emoji": "🔥", "requirement": "3-day streak"},
            {"id": "blue_streak", "name": "Blue Streak", "emoji": "💙", "requirement": "7-day streak"},
            {"id": "golden_streak", "name": "Golden Streak", "emoji": "🏆", "requirement": "30-day streak"},
            {"id": "legendary_streak", "name": "Legendary Streak", "emoji": "👑", "requirement": "100-day streak"},
        ],
        "learning_badges": [
            {"id": "first_question", "name": "First Step", "emoji": "🌟", "requirement": "Ask first question"},
            {"id": "concept_crusher", "name": "Concept Crusher", "emoji": "💪", "requirement": "Master 10 concepts"},
            {"id": "speed_demon", "name": "Speed Demon", "emoji": "⚡", "requirement": "Fast correct answers"},
            {"id": "deep_diver", "name": "Deep Diver", "emoji": "🤿", "requirement": "Ask follow-up questions"},
        ],
        "special_badges": [
            {"id": "night_owl", "name": "Night Owl", "emoji": "🦉", "requirement": "Study after 10 PM"},
            {"id": "early_bird", "name": "Early Bird", "emoji": "🐦", "requirement": "Study before 6 AM"},
            {"id": "weekend_warrior", "name": "Weekend Warrior", "emoji": "⚔️", "requirement": "Study on weekend"},
            {"id": "comeback_kid", "name": "Comeback Kid", "emoji": "🔄", "requirement": "Return after break"},
        ]
    }
    return badges


@router.get("/levels/all")
async def get_all_levels():
    """Get list of all levels and XP requirements"""
    levels = [
        {"level": 1, "name": "Explorer", "emoji": "🔭", "xp_required": 0, "description": "Just starting your journey"},
        {"level": 2, "name": "Analyst", "emoji": "🔬", "xp_required": 500, "description": "Building strong foundations"},
        {"level": 3, "name": "Tactician", "emoji": "🎯", "xp_required": 1500, "description": "Strategic problem solver"},
        {"level": 4, "name": "Scientist", "emoji": "🧪", "xp_required": 3500, "description": "Deep understanding achieved"},
        {"level": 5, "name": "Master", "emoji": "👑", "xp_required": 7000, "description": "True mastery unlocked"},
    ]
    return {"levels": levels}
