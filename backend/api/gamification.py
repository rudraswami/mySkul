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


@router.get("/daily-quests")
async def get_daily_quests(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get daily quests for the current user.
    Generates new quests if they don't exist for today.
    """
    try:
        user_doc = await db.users.find_one({"user_id": user.user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Check if quests exist for today
        current_quests = user_doc.get("daily_quests", {})
        if current_quests.get("date") == today_str:
            return {"quests": current_quests.get("quests", []), "date": today_str}

        # Generate new quests
        import random
        quest_pool = [
            {"id": "ai_session", "title": "Complete 1 AI Session", "xp": 50, "type": "easy", "icon": "Zap"},
            {"id": "quiz_score", "title": "Score 80%+ on a Quiz", "xp": 100, "type": "medium", "icon": "Trophy"},
            {"id": "study_time", "title": "Study for 30 Minutes", "xp": 75, "type": "easy", "icon": "Clock"},
            {"id": "ask_questions", "title": "Ask 5 Questions", "xp": 50, "type": "easy", "icon": "CheckCircle"},
            {"id": "streak_maintain", "title": "Maintain 3-Day Streak", "xp": 150, "type": "hard", "icon": "Zap"},
            {"id": "mock_test", "title": "Attempt a Mock Test", "xp": 120, "type": "medium", "icon": "FileText"},
            {"id": "review_notes", "title": "Review Auto-Notes", "xp": 60, "type": "easy", "icon": "BookOpen"},
        ]
        
        # Select 3 random quests
        selected_quests = random.sample(quest_pool, 3)
        formatted_quests = []
        for q in selected_quests:
            formatted_quests.append({
                **q,
                "completed": False,
                "progress": 0,
                "target": 1  # simplified for now
            })

        # Save to DB
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"daily_quests": {"date": today_str, "quests": formatted_quests}}}
        )

        return {"quests": formatted_quests, "date": today_str}

    except Exception as e:
        print(f"Error getting daily quests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-quests/{quest_id}/complete")
async def complete_daily_quest(
    quest_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Mark a daily quest as complete and award XP.
    """
    try:
        user_doc = await db.users.find_one({"user_id": user.user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        current_quests = user_doc.get("daily_quests", {})
        quests_list = current_quests.get("quests", [])
        
        quest_index = next((i for i, q in enumerate(quests_list) if q["id"] == quest_id), -1)
        
        if quest_index == -1:
            raise HTTPException(status_code=404, detail="Quest not found")
            
        if quests_list[quest_index]["completed"]:
            return {"message": "Quest already completed", "xp_awarded": 0}

        # Mark as complete
        quests_list[quest_index]["completed"] = True
        xp_reward = quests_list[quest_index]["xp"]

        # Update DB: Mark quest complete AND add XP
        await db.users.update_one(
            {"user_id": user.user_id},
            {
                "$set": {"daily_quests.quests": quests_list},
                "$inc": {"xp": xp_reward}
            }
        )

        return {
            "message": "Quest completed",
            "xp_awarded": xp_reward,
            "quest_id": quest_id,
            "new_total_xp": user_doc.get("xp", 0) + xp_reward
        }

    except Exception as e:
        print(f"Error completing quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))
