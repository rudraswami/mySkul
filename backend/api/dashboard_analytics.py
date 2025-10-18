"""
Dashboard Analytics API
Provides dynamic data for premium dashboard components
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from dependencies import get_current_user, get_database

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/analytics")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)):
    """
    Get comprehensive dashboard analytics for the user
    Returns streak data, progress, subjects, etc.
    """
    try:
        db = await get_database()
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Get user's study sessions
        sessions = await db.ai_sessions.find(
            {"user_id": user_id}
        ).sort("created_at", -1).to_list(length=None)
        
        # Calculate streak data
        streak_data = calculate_streak(sessions)
        
        # Get subject progress
        subjects = await get_subject_progress(db, user_id)
        
        # Calculate study time today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_sessions = [s for s in sessions if s.get("created_at", datetime.min) >= today_start]
        study_time_today = sum([s.get("duration", 0) for s in today_sessions])
        
        # Calculate weekly progress
        week_start = datetime.now() - timedelta(days=7)
        weekly_sessions = [s for s in sessions if s.get("created_at", datetime.min) >= week_start]
        weekly_goal = 10  # 10 sessions per week
        weekly_progress = min(100, (len(weekly_sessions) / weekly_goal) * 100)
        
        return {
            "study_time_today": format_duration(study_time_today),
            "total_sessions": len(sessions),
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "weekly_progress": int(weekly_progress),
            "subjects": subjects,
            "heatmap_data": streak_data["heatmap_data"]
        }
    except Exception as e:
        print(f"Dashboard analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streak")
async def get_streak_data(current_user: dict = Depends(get_current_user)):
    """
    Get detailed streak calendar data (365 days)
    Returns: date, minutes studied, activity level (0-4), subjects
    """
    try:
        db = await get_database()
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Get all sessions for past 365 days
        year_ago = datetime.now() - timedelta(days=365)
        sessions = await db.ai_sessions.find({
            "user_id": user_id,
            "created_at": {"$gte": year_ago}
        }).to_list(length=None)
        
        # Group by date
        daily_data = {}
        for session in sessions:
            date = session.get("created_at", datetime.now()).date().isoformat()
            if date not in daily_data:
                daily_data[date] = {
                    "minutes": 0,
                    "sessions": 0,
                    "subjects": set()
                }
            daily_data[date]["minutes"] += session.get("duration", 0)
            daily_data[date]["sessions"] += 1
            if "subject" in session:
                daily_data[date]["subjects"].add(session["subject"])
        
        # Generate 365 days data
        heatmap_data = []
        today = datetime.now().date()
        for i in range(364, -1, -1):
            date = (today - timedelta(days=i)).isoformat()
            day_data = daily_data.get(date, {"minutes": 0, "sessions": 0, "subjects": set()})
            
            # Calculate activity level (0-4)
            minutes = day_data["minutes"]
            level = 0
            if minutes > 0:
                if minutes < 30:
                    level = 1
                elif minutes < 60:
                    level = 2
                elif minutes < 90:
                    level = 3
                else:
                    level = 4
            
            heatmap_data.append({
                "date": date,
                "minutes": minutes,
                "sessions": day_data["sessions"],
                "level": level,
                "subjects": list(day_data["subjects"])
            })
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        for day in reversed(heatmap_data):
            if day["minutes"] > 0:
                temp_streak += 1
                if current_streak == 0:
                    current_streak = temp_streak
            else:
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                temp_streak = 0
        
        longest_streak = max(longest_streak, temp_streak, current_streak)
        
        return {
            "heatmap_data": heatmap_data,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_days_studied": len([d for d in heatmap_data if d["minutes"] > 0])
        }
    except Exception as e:
        print(f"Streak data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user)):
    """
    Get live leaderboard with top 10 users
    Includes pseudo profiles initially, replaces with real data as users accumulate
    """
    try:
        db = await get_database()
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Get real user scores
        users = await db.users.find().to_list(length=None)
        leaderboard = []
        
        for user in users:
            # Calculate score based on sessions, streak, XP
            sessions_count = await db.ai_sessions.count_documents({"user_id": user.get("id", user.get("_id"))})
            score = sessions_count * 10 + user.get("xp", 0)
            
            leaderboard.append({
                "user_id": str(user.get("id", user.get("_id"))),
                "name": user.get("full_name", "Anonymous"),
                "score": score,
                "level": user.get("level", 1),
                "xp": user.get("xp", 0),
                "sessions": sessions_count,
                "is_current_user": str(user.get("id", user.get("_id"))) == str(user_id)
            })
        
        # If less than 10 users, add pseudo profiles
        if len(leaderboard) < 10:
            pseudo_names = [
                "Rahul", "Kavya", "Vikram", "Priya", "Arjun",
                "Sneha", "Rohan", "Anjali", "Karthik", "Meera",
                "Aditya", "Divya", "Akash", "Riya", "Siddharth",
                "Pooja", "Nikhil", "Tanvi", "Varun", "Shreya"
            ]
            
            for i in range(len(leaderboard), 10):
                leaderboard.append({
                    "user_id": f"pseudo_{i}",
                    "name": pseudo_names[i],
                    "score": random.randint(50, 500),
                    "level": random.randint(1, 5),
                    "xp": random.randint(50, 500),
                    "sessions": random.randint(5, 50),
                    "is_current_user": False,
                    "is_pseudo": True
                })
        
        # Sort by score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard[:10]):
            entry["rank"] = i + 1
        
        return {
            "leaderboard": leaderboard[:10],
            "user_rank": next((e["rank"] for e in leaderboard if e["is_current_user"]), None)
        }
    except Exception as e:
        print(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_streak(sessions: List[Dict]) -> Dict[str, Any]:
    """Calculate streak data from sessions"""
    if not sessions:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "heatmap_data": []
        }
    
    # Group sessions by date
    dates = set()
    for session in sessions:
        date = session.get("created_at", datetime.now()).date()
        dates.add(date)
    
    sorted_dates = sorted(dates, reverse=True)
    
    # Calculate current streak
    current_streak = 0
    today = datetime.now().date()
    current_date = today
    
    for date in sorted_dates:
        if date == current_date or (current_date - date).days <= 1:
            current_streak += 1
            current_date = date
        else:
            break
    
    # Calculate longest streak
    longest_streak = 1
    temp_streak = 1
    
    for i in range(len(sorted_dates) - 1):
        diff = (sorted_dates[i] - sorted_dates[i + 1]).days
        if diff == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return {
        "current_streak": current_streak,
        "longest_streak": max(longest_streak, current_streak),
        "heatmap_data": []
    }


async def get_subject_progress(db, user_id: str) -> List[Dict]:
    """Get progress for each subject"""
    sessions = await db.ai_sessions.find({"user_id": user_id}).to_list(length=None)
    
    subjects = {}
    for session in sessions:
        subject = session.get("subject", "General")
        if subject not in subjects:
            subjects[subject] = {"count": 0, "recent_topic": ""}
        subjects[subject]["count"] += 1
        subjects[subject]["recent_topic"] = session.get("topic", "Various topics")
    
    # Calculate progress (assuming 100 sessions is 100%)
    result = []
    for subject, data in subjects.items():
        progress = min(100, (data["count"] / 100) * 100)
        result.append({
            "name": subject,
            "progress": int(progress),
            "recent_topic": data["recent_topic"]
        })
    
    # If no subjects, return defaults
    if not result:
        result = [
            {"name": "Mathematics", "progress": 0, "recent_topic": "Get started"},
            {"name": "Physics", "progress": 0, "recent_topic": "Get started"},
            {"name": "Chemistry", "progress": 0, "recent_topic": "Get started"}
        ]
    
    return result[:3]  # Return top 3


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"0h {seconds}m"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"
