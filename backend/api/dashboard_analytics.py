"""
Dashboard Analytics API
Provides dynamic data for premium dashboard components
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from dependencies import get_current_user, get_database
from models.core import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/analytics")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get comprehensive dashboard analytics for the user
    Returns streak data, progress, subjects, etc.
    """
    try:
        # PATCH: Use User model's user_id attribute instead of dict access
        user_id = current_user.user_id
        
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
async def get_streak_data(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get detailed streak calendar data (365 days)
    Returns: date, minutes studied, activity level (0-4), subjects
    """
    try:
        # PATCH: Use User model's user_id attribute
        user_id = current_user.user_id
        
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
async def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get live leaderboard with top 10 users
    Includes pseudo profiles initially, replaces with real data as users accumulate
    """
    try:
        # PATCH: Use User model's user_id attribute
        user_id = current_user.user_id
        
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


# =============================================================================
# 🤖 AI COMPANION ENDPOINT - Backend-Powered Intelligence
# =============================================================================

@router.get("/companion")
async def get_ai_companion_message(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🤖 AI Companion - Intelligent Dashboard Presence
    
    Returns personalized, contextual message for the dashboard companion.
    Uses MagicContext + Error Genome™ + Exam Urgency + Emotional Calibration.
    
    Phase 3 Enhancement:
    - Cross-agent awareness (knows what notifications were sent)
    - Emotional state detection
    - Tone adaptation based on student state
    """
    import asyncio
    import json
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    user_id = current_user.user_id
    
    try:
        # =================================================================
        # 0. Get Cross-Agent Context (Phase 3)
        # =================================================================
        
        emotional_state = "neutral"
        recent_nudge_count = 0
        
        try:
            from services.intelligent_proactive_mentor import IntelligentProactiveMentor
            mentor = IntelligentProactiveMentor(db)
            
            # Get emotional state
            emotional_data = await mentor.get_emotional_state(user_id)
            emotional_state = emotional_data.get("state", "neutral")
            
            # Get recent nudges for cross-agent awareness
            recent_nudges = await mentor.get_recent_nudges(user_id, hours=24)
            recent_nudge_count = len(recent_nudges)
        except Exception as e:
            logger.warning(f"Cross-agent context failed: {e}")
        
        # =================================================================
        # 1. Gather Comprehensive Student Intelligence
        # =================================================================
        
        student_context = {
            "name": "",
            "days_to_exam": None,
            "exam_name": "exam",
            "current_streak": 0,
            "weak_topics": [],
            "mastery_levels": {},
            "common_mistakes": [],
            "recent_topic": "",
            "due_reviews": [],
            "total_questions_today": 0,
            "hours_since_last_session": None,
            "time_of_day": "day",
            "emotional_state": emotional_state,
            "recent_nudge_count": recent_nudge_count
        }
        
        # Determine time of day
        from datetime import timezone
        now = datetime.now(timezone.utc)
        hour = (now.hour + 5) % 24  # Approx IST
        if 5 <= hour < 12:
            student_context["time_of_day"] = "morning"
        elif 12 <= hour < 17:
            student_context["time_of_day"] = "afternoon"
        elif 17 <= hour < 21:
            student_context["time_of_day"] = "evening"
        else:
            student_context["time_of_day"] = "night"
        
        # Get user profile
        user = await db.users.find_one({"user_id": user_id})
        if user:
            student_context["name"] = (user.get("full_name") or user.get("name") or "").split()[0]
            student_context["current_streak"] = user.get("streak", 0)
            
            # Exam info
            if user.get("exam_date"):
                exam_date = user["exam_date"]
                if isinstance(exam_date, str):
                    exam_date = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
                student_context["days_to_exam"] = max(0, (exam_date - now).days)
                student_context["exam_name"] = user.get("exam_type", "exam")
        
        # Get learning profile for Error Genome™
        learning_profile = await db.learning_profiles.find_one({"user_id": user_id})
        if learning_profile:
            student_context["weak_topics"] = learning_profile.get("weak_topics", [])[:3]
            student_context["common_mistakes"] = learning_profile.get("common_mistake_types", [])[:3]
            student_context["mastery_levels"] = learning_profile.get("topic_mastery", {})
        
        # Get recent session
        recent_session = await db.chat_sessions.find_one(
            {"user_id": user_id},
            sort=[("updated_at", -1)]
        )
        if recent_session:
            student_context["recent_topic"] = recent_session.get("topic", recent_session.get("title", ""))
            last_update = recent_session.get("updated_at")
            if last_update:
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                if last_update.tzinfo is None:
                    last_update = last_update.replace(tzinfo=timezone.utc)
                student_context["hours_since_last_session"] = round((now - last_update).total_seconds() / 3600, 1)
        
        # Get due reviews (spaced repetition)
        due_reviews = await db.sr_items.find({
            "user_id": user_id,
            "next_review": {"$lte": now}
        }).limit(3).to_list(length=3)
        student_context["due_reviews"] = [r.get("topic", "") for r in due_reviews]
        
        # Get today's activity
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_messages = await db.chat_messages.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": today_start},
            "role": "user"
        })
        student_context["total_questions_today"] = today_messages
        
        # =================================================================
        # 2. Determine Companion Message Type
        # =================================================================
        
        message_type = "focus"  # Default
        priority_score = 0
        
        # Priority 1: Comeback (2+ days inactive)
        if student_context["hours_since_last_session"] and student_context["hours_since_last_session"] > 48:
            message_type = "comeback"
            priority_score = 100
        
        # Priority 2: Error pattern alert (if mistakes detected)
        elif student_context["common_mistakes"]:
            message_type = "error_pattern"
            priority_score = 80
        
        # Priority 3: Exam urgency (< 30 days)
        elif student_context["days_to_exam"] and student_context["days_to_exam"] <= 30:
            message_type = "exam_countdown"
            priority_score = 70
        
        # Priority 4: Due reviews
        elif student_context["due_reviews"]:
            message_type = "revision_due"
            priority_score = 60
        
        # Priority 5: Weak topic focus
        elif student_context["weak_topics"]:
            message_type = "weak_topic"
            priority_score = 50
        
        # Priority 6: Streak celebration (milestone)
        elif student_context["current_streak"] in [3, 7, 14, 21, 30, 50, 100]:
            message_type = "celebration"
            priority_score = 40
        
        # Default: Focus directive
        else:
            message_type = "focus"
            priority_score = 30
        
        # =================================================================
        # 3. Generate Intelligent Message with LLM
        # =================================================================
        
        try:
            from services.llm_service import call_gemini
            from core.config import settings
            LLM_AVAILABLE = True
            gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        except ImportError:
            LLM_AVAILABLE = False
            gemini_api_key = None
        
        name = student_context["name"] or "there"
        days = student_context["days_to_exam"]
        exam = student_context["exam_name"]
        streak = student_context["current_streak"]
        weak = student_context["weak_topics"]
        mistakes = student_context["common_mistakes"]
        recent = student_context["recent_topic"] or "your studies"
        due = student_context["due_reviews"]
        time_of_day = student_context["time_of_day"]
        
        if LLM_AVAILABLE and gemini_api_key:
            prompt = f"""You are Sathi, a warm AI study companion on a student's dashboard.
Generate a SHORT, supportive message (max 2 sentences) to greet them.

STUDENT CONTEXT:
- Name: {name}
- Time of day: {time_of_day}
- Emotional state: {emotional_state}
- Current streak: {streak} days
{"- Days to " + exam + ": " + str(days) if days else ""}
{"- Weak topics: " + ", ".join(weak) if weak else ""}
{"- Common mistake patterns: " + ", ".join(mistakes) if mistakes else ""}
{"- Last studied: " + recent if recent else ""}
{"- Topics due for review: " + ", ".join(due) if due else ""}
- Questions asked today: {student_context["total_questions_today"]}
{"- Hours since last session: " + str(student_context["hours_since_last_session"]) if student_context["hours_since_last_session"] else ""}
{"- Recent notifications sent: " + str(recent_nudge_count) if recent_nudge_count > 0 else ""}

MESSAGE TYPE: {message_type}

EMOTIONAL CALIBRATION RULES:
- If frustrated: Be extra gentle, acknowledge difficulty, offer small wins
- If struggling: Offer simpler starting points, be encouraging
- If confident: Can be more challenging, celebrate growth
- If neutral: Standard warm supportive tone

RULES:
1. Be warm like a supportive friend/elder sibling
2. Reference SPECIFIC student data (exam days, weak topics, streak)
3. Keep it SHORT - max 2 sentences
4. Suggest ONE clear action
5. Match tone to emotional state (see above)
6. Match tone to time of day (morning = energetic, night = calm)
7. Use 1-2 emojis max
7. Never guilt-trip

OUTPUT FORMAT (JSON):
{{"title": "short greeting (5-7 words)", "message": "personalized message (1-2 sentences)", "action_label": "button text", "action_type": "start_study|review|practice|rest", "color": "purple|green|orange|blue"}}

Generate:"""

            try:
                response = await asyncio.wait_for(
                    call_gemini(
                        prompt=prompt,
                        api_key=gemini_api_key,
                        temperature=0.7,
                        max_tokens=200,
                        model="gemini-2.0-flash",
                        system_message="You are a notification writer. Output only valid JSON."
                    ),
                    timeout=5.0
                )
                
                # Parse JSON response
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    if all(k in result for k in ["title", "message", "action_label"]):
                        return {
                            "title": result["title"],
                            "message": result["message"],
                            "action_label": result.get("action_label", "Start Learning"),
                            "action_type": result.get("action_type", "start_study"),
                            "color": result.get("color", "purple"),
                            "message_type": message_type,
                            "intelligent": True,
                            "student_context": {
                                "name": name,
                                "streak": streak,
                                "days_to_exam": days,
                                "exam_name": exam,
                                "weak_topics": weak[:2],
                                "due_reviews": due[:2]
                            }
                        }
            except asyncio.TimeoutError:
                logger.warning("Companion LLM generation timed out - using fallback templates")
            except Exception as e:
                logger.warning(f"Companion LLM failed: {e} - using fallback templates")
        
        # =================================================================
        # 4. Fallback Template Messages
        # =================================================================
        
        exam_suffix = f" ({days} days to {exam})" if days and days <= 60 else ""
        
        templates = {
            "comeback": {
                "title": f"👋 Welcome back, {name}!",
                "message": f"We missed you! Ready to pick up where you left off with {recent}?{exam_suffix}",
                "action_label": "Continue Learning",
                "action_type": "start_study",
                "color": "purple"
            },
            "error_pattern": {
                "title": f"🎯 Let's fix {mistakes[0] if mistakes else 'those errors'}",
                "message": f"I noticed you sometimes struggle with {mistakes[0] if mistakes else 'certain patterns'}. Quick practice?{exam_suffix}",
                "action_label": "Practice Now",
                "action_type": "practice",
                "color": "orange"
            },
            "exam_countdown": {
                "title": f"📅 {days} days to {exam}!",
                "message": f"Let's make today count, {name}. Focus on high-yield topics!",
                "action_label": "See Study Plan",
                "action_type": "start_study",
                "color": "orange"
            },
            "revision_due": {
                "title": "🧠 Time for a quick review",
                "message": f"Spaced repetition time! {due[0] if due else 'Some concepts'} need a refresh.{exam_suffix}",
                "action_label": "Start Review",
                "action_type": "review",
                "color": "blue"
            },
            "weak_topic": {
                "title": f"💪 Strengthen {weak[0] if weak else 'weak areas'}",
                "message": f"Focused practice on {weak[0] if weak else 'this topic'} will boost your confidence!{exam_suffix}",
                "action_label": "Practice Now",
                "action_type": "practice",
                "color": "purple"
            },
            "celebration": {
                "title": f"🔥 {streak}-day streak!",
                "message": f"You're on fire, {name}! Keep the momentum going.{exam_suffix}",
                "action_label": "Continue Streak",
                "action_type": "start_study",
                "color": "green"
            },
            "focus": {
                "title": f"📚 Ready to learn, {name}?",
                "message": f"What would you like to study today?{exam_suffix}",
                "action_label": "Start Learning",
                "action_type": "start_study",
                "color": "purple"
            }
        }
        
        fallback = templates.get(message_type, templates["focus"])
        
        return {
            **fallback,
            "message_type": message_type,
            "intelligent": False,
            "student_context": {
                "name": name,
                "streak": streak,
                "days_to_exam": days,
                "exam_name": exam,
                "weak_topics": weak[:2],
                "due_reviews": due[:2]
            }
        }
        
    except Exception as e:
        logger.error(f"Companion endpoint error: {e}")
        return {
            "title": "👋 Hey there!",
            "message": "Ready to learn something new today?",
            "action_label": "Start Learning",
            "action_type": "start_study",
            "color": "purple",
            "message_type": "fallback",
            "intelligent": False,
            "student_context": {}
        }