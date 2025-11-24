"""
User profile router for profile management and user operations
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta

from models.core import User, ProfileUpdateRequest
from dependencies import get_current_user, get_database


# Router instance
router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get user profile"""
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": getattr(user, 'phone', ''),
        "exam_type": user.exam_type,
        "grade": user.grade,
        "target_year": user.target_year,
        "current_standard": getattr(user, 'current_standard', ''),
        "institution": getattr(user, 'institution', ''),
        "subscription_type": user.subscription_type,
        "xp": getattr(user, 'xp', 0),
        "level": getattr(user, 'level', 1),
        "badges": getattr(user, 'badges', []),
        "created_at": getattr(user, 'created_at', None)
    }


@router.get("/progress")
async def get_user_progress(user: User = Depends(get_current_user), db = Depends(get_database)):
    """
    Get comprehensive user progress (XP, level, badges, stats, streaks)
    Returns all data needed for GamificationProgress component
    """
    try:
        # Get user's data from database
        user_data = await db.users.find_one({"id": user.user_id})
        
        if not user_data:
            # Return safe defaults for new users
            return {
                "xp": 0,
                "level": 1,
                "badges": [],
                "total_xp": 0,
                "current_level": 1,
                "xp_to_next_level": 100,
                "xp_for_next_level": 100,
                "xp_progress": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "total_badges": 0,
                "available_badges": 10,
                "badges_earned": [],
                "stats": {
                    "total_tests": 0,
                    "average_accuracy": 0,
                    "perfect_scores": 0
                }
            }
        
        xp = user_data.get("xp", 0)
        level = user_data.get("level", 1)
        badges = user_data.get("badges", [])
        
        # Calculate XP progress
        xp_for_next_level = (level + 1) * 100 - xp
        xp_progress = xp % 100
        
        # Get streak data
        current_streak = user_data.get("current_streak", 0)
        longest_streak = user_data.get("longest_streak", 0)
        
        # Get test statistics
        test_attempts = await db.test_attempts.count_documents({"student_id": user.user_id})
        
        # Calculate average accuracy
        attempts = await db.test_attempts.find({"student_id": user.user_id}).to_list(length=None)
        if attempts:
            accuracies = [a.get("accuracy", 0) for a in attempts if a.get("accuracy") is not None]
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            perfect_scores = len([a for a in attempts if a.get("accuracy", 0) >= 100])
        else:
            avg_accuracy = 0
            perfect_scores = 0
        
        return {
            # Legacy fields for backward compatibility
            "xp": xp,
            "level": level,
            "badges": badges,
            "xp_to_next_level": max(0, xp_for_next_level),
            "xp_progress": xp_progress,
            
            # New fields for GamificationProgress component
            "total_xp": xp,
            "current_level": level,
            "xp_for_next_level": max(0, xp_for_next_level),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_badges": len(badges),
            "available_badges": 10,  # Total badges available in system
            "badges_earned": badges if isinstance(badges, list) else [],
            "stats": {
                "total_tests": test_attempts,
                "average_accuracy": int(avg_accuracy),
                "perfect_scores": perfect_scores
            }
        }
    except Exception as e:
        print(f"Error fetching user progress: {e}")
        # Return safe defaults on error
        return {
            "xp": 0,
            "level": 1,
            "badges": [],
            "total_xp": 0,
            "current_level": 1,
            "xp_to_next_level": 100,
            "xp_for_next_level": 100,
            "xp_progress": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "total_badges": 0,
            "available_badges": 10,
            "badges_earned": [],
            "stats": {
                "total_tests": 0,
                "average_accuracy": 0,
                "perfect_scores": 0
            }
        }


@router.get("/recommendations")
async def get_smart_recommendations(user: User = Depends(get_current_user), db = Depends(get_database)):
    """
    Get AI-powered smart study recommendations
    """
    try:
        user_id = user.user_id
        
        # Get user's recent activity
        sessions = await db.ai_sessions.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(50).to_list(length=50)
        
        recommendations = []
        
        # Analyze weak topics
        topic_scores = {}
        for session in sessions:
            topic = session.get("topic", "General")
            # Mock score analysis - in production, analyze actual performance
            if topic not in topic_scores:
                topic_scores[topic] = {"count": 0, "avg_score": 0}
            topic_scores[topic]["count"] += 1
        
        # Add weak topic recommendation
        if topic_scores:
            weakest = min(topic_scores.items(), key=lambda x: x[1]["count"])
            recommendations.append({
                "id": "weak_topic",
                "type": "focus",
                "priority": "high",
                "title": f"Focus on {weakest[0]}",
                "description": f"You've only practiced {weakest[1]['count']} times. Let's strengthen this!",
                "action": "Start Learning",
                "route": f"/tutor?topic={weakest[0]}",
                "progress": (weakest[1]['count'] / 10) * 100
            })
        
        # Check streak
        today_sessions = [s for s in sessions if s.get("created_at", datetime.min).date() == datetime.now().date()]
        if not today_sessions:
            recommendations.append({
                "id": "streak",
                "type": "streak",
                "priority": "medium",
                "title": "Keep Your Streak Alive!",
                "description": "Study for at least 30 minutes today to maintain your streak",
                "action": "Study Now",
                "route": "/tutor",
                "progress": 0
            })
        
        # Revision recommendation
        week_old = datetime.now() - timedelta(days=7)
        old_topics = [s.get("topic") for s in sessions if s.get("created_at", datetime.min) < week_old]
        if old_topics:
            recommendations.append({
                "id": "revision",
                "type": "review",
                "priority": "medium",
                "title": f"Time to Revise {old_topics[0]}",
                "description": "You learned this last week. Perfect time for revision!",
                "action": "Review Topic",
                "route": f"/tutor?topic={old_topics[0]}",
                "progress": 50
            })
        
        # V1: Mock tests hidden - removed recommendation
        # Will be added back in V2 when mock tests are available
        
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return {"recommendations": []}


@router.put("/profile")
async def update_user_profile(
    profile_update: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user profile"""
    try:
        # Prepare update data
        update_data = {}
        
        if profile_update.full_name is not None:
            update_data["full_name"] = profile_update.full_name
        if profile_update.email is not None:
            update_data["email"] = profile_update.email
        if profile_update.phone is not None:
            update_data["phone"] = profile_update.phone
        if profile_update.exam_type is not None:
            update_data["exam_type"] = profile_update.exam_type
        if profile_update.target_year is not None:
            update_data["target_year"] = profile_update.target_year
        if profile_update.current_standard is not None:
            update_data["current_standard"] = profile_update.current_standard
        if profile_update.institution is not None:
            update_data["institution"] = profile_update.institution
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update user in database
        result = await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made to profile")
        
        # Get updated user data
        updated_user = await db.users.find_one({"user_id": user.user_id})
        if not updated_user:
            raise HTTPException(status_code=404, detail="Updated user not found")
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "user_id": updated_user["user_id"],
                "full_name": updated_user.get("full_name"),
                "email": updated_user.get("email"),
                "phone": updated_user.get("phone", ""),
                "exam_type": updated_user.get("exam_type"),
                "target_year": updated_user.get("target_year"),
                "current_standard": updated_user.get("current_standard", ""),
                "institution": updated_user.get("institution", ""),
                "subscription_type": updated_user.get("subscription_type")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")