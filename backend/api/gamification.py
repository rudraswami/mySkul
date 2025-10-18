"""
Gamification API - Leaderboard, achievements, rankings
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
from models.core import User
from dependencies import get_current_user, get_database

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    period: str = Query(default="all_time", regex="^(all_time|weekly|monthly)$"),
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get leaderboard with top users by XP
    Supports filtering by time period: all_time, weekly, monthly
    """
    try:
        # Calculate time filter based on period
        time_filter = {}
        if period == "weekly":
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
            time_filter = {"last_activity": {"$gte": start_date.isoformat()}}
        elif period == "monthly":
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
            time_filter = {"last_activity": {"$gte": start_date.isoformat()}}
        
        # Fetch top users by XP
        users = await db.users.find(
            time_filter,
            {"user_id": 1, "full_name": 1, "email": 1, "xp": 1, "level": 1, "badges": 1, "avatar_url": 1}
        ).sort("xp", -1).limit(limit).to_list(length=limit)
        
        # Find current user's rank
        current_user_xp = 0
        current_user_rank = None
        
        for idx, u in enumerate(users, start=1):
            if u.get("user_id") == user.user_id:
                current_user_rank = idx
                current_user_xp = u.get("xp", 0)
                break
        
        # If current user not in top N, calculate their rank
        if current_user_rank is None:
            user_doc = await db.users.find_one({"user_id": user.user_id})
            if user_doc:
                current_user_xp = user_doc.get("xp", 0)
                # Count users with more XP
                higher_count = await db.users.count_documents({"xp": {"$gt": current_user_xp}})
                current_user_rank = higher_count + 1
        
        # Format leaderboard
        leaderboard = []
        for idx, u in enumerate(users, start=1):
            leaderboard.append({
                "rank": idx,
                "user_id": u.get("user_id"),
                "name": u.get("full_name", "Anonymous"),
                "xp": u.get("xp", 0),
                "level": u.get("level", 1),
                "badges": len(u.get("badges", [])),
                "avatar": u.get("avatar_url", ""),
                "is_current_user": u.get("user_id") == user.user_id
            })
        
        return {
            "leaderboard": leaderboard,
            "current_user": {
                "rank": current_user_rank,
                "xp": current_user_xp,
                "total_users": await db.users.count_documents({})
            },
            "period": period,
            "total_shown": len(leaderboard)
        }
        
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")


@router.get("/progress")
async def get_gamification_progress(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    REDIRECT: This endpoint redirects to /api/user/progress
    Kept for backward compatibility
    
    Get user gamification progress (XP, level, badges, achievements)
    """
    try:
        user_doc = await db.users.find_one({"user_id": user.user_id})
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        xp = user_doc.get("xp", 0)
        level = max(1, xp // 100)  # Level up every 100 XP
        
        # Get user's achievements
        achievements = user_doc.get("achievements", [])
        badges = user_doc.get("badges", [])
        
        # Calculate next level progress
        xp_for_current_level = (level - 1) * 100
        xp_for_next_level = level * 100
        xp_progress = ((xp - xp_for_current_level) / 100) * 100  # Percentage to next level
        
        return {
            "xp": xp,
            "level": level,
            "xp_progress": min(100, max(0, xp_progress)),
            "xp_to_next_level": max(0, xp_for_next_level - xp),
            "badges": badges,
            "achievements": achievements,
            "total_badges": len(badges),
            "total_achievements": len(achievements)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching gamification progress: {e}")
        # Return default data instead of error for graceful fallback
        return {
            "xp": 0,
            "level": 1,
            "xp_progress": 0,
            "xp_to_next_level": 100,
            "badges": [],
            "achievements": [],
            "total_badges": 0,
            "total_achievements": 0
        }


@router.get("/achievements")
async def get_available_achievements(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all available achievements and user's unlock status"""
    try:
        user_doc = await db.users.find_one({"user_id": user.user_id})
        unlocked = user_doc.get("achievements", []) if user_doc else []
        
        # Define available achievements
        achievements = [
            {
                "id": "first_test",
                "name": "First Steps",
                "description": "Complete your first mock test",
                "xp_reward": 50,
                "icon": "🎯",
                "unlocked": "first_test" in unlocked
            },
            {
                "id": "perfect_score",
                "name": "Perfect Score",
                "description": "Get 100% on any test",
                "xp_reward": 200,
                "icon": "💯",
                "unlocked": "perfect_score" in unlocked
            },
            {
                "id": "week_streak",
                "name": "Week Warrior",
                "description": "7-day login streak",
                "xp_reward": 100,
                "icon": "🔥",
                "unlocked": "week_streak" in unlocked
            },
            {
                "id": "ai_master",
                "name": "AI Master",
                "description": "Use AI Tutor 50 times",
                "xp_reward": 150,
                "icon": "🧠",
                "unlocked": "ai_master" in unlocked
            },
            {
                "id": "notes_guru",
                "name": "Notes Guru",
                "description": "Upload 20 auto-notes",
                "xp_reward": 150,
                "icon": "📝",
                "unlocked": "notes_guru" in unlocked
            }
        ]
        
        return {
            "achievements": achievements,
            "total": len(achievements),
            "unlocked_count": len([a for a in achievements if a["unlocked"]])
        }
        
    except Exception as e:
        print(f"Error fetching achievements: {e}")
        # Return empty achievements instead of error
        return {
            "achievements": [],
            "total": 0,
            "unlocked_count": 0
        }
