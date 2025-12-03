"""
Analytics Helper Functions
===========================

Implements analytics calculations that were marked as TODO.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def _calculate_performance_trend(user_id: str, db) -> str:
    """
    Calculate user's performance trend from recent sessions.
    
    Returns: "improving" | "stable" | "declining"
    """
    try:
        # Get last 14 days of activity
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        
        sessions = await db.chat_sessions.find({
            "user_id": user_id,
            "created_at": {"$gte": two_weeks_ago.isoformat()}
        }).sort("created_at", 1).to_list(length=100)
        
        if len(sessions) < 3:
            return "stable"  # Not enough data
        
        # Split into two halves
        mid = len(sessions) // 2
        first_half = sessions[:mid]
        second_half = sessions[mid:]
        
        # Calculate average session quality (based on message count as proxy)
        first_avg = sum(len(s.get('messages', [])) for s in first_half) / len(first_half)
        second_avg = sum(len(s.get('messages', [])) for s in second_half) / len(second_half)
        
        # Determine trend
        if second_avg > first_avg * 1.2:
            return "improving"
        elif second_avg < first_avg * 0.8:
            return "declining"
        else:
            return "stable"
            
    except Exception as e:
        logger.error(f"Error calculating performance trend: {e}")
        return "stable"


async def _get_strong_subjects(user_id: str, db) -> List[str]:
    """
    Identify user's strong subjects based on activity and mastery.
    
    Returns: List of subject names
    """
    try:
        # Get subject distribution from sessions
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$subject",
                "count": {"$sum": 1},
                "avg_messages": {"$avg": {"$size": "$messages"}}
            }},
            {"$sort": {"avg_messages": -1}},
            {"$limit": 3}
        ]
        
        result = await db.chat_sessions.aggregate(pipeline).to_list(length=3)
        
        strong_subjects = [r["_id"] for r in result if r.get("avg_messages", 0) > 5]
        return strong_subjects
        
    except Exception as e:
        logger.error(f"Error getting strong subjects: {e}")
        return []


async def _get_weak_subjects(user_id: str, db) -> List[str]:
    """
    Identify user's weak subjects based on activity patterns.
    
    Returns: List of subject names
    """
    try:
        # Get subjects with low engagement
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$subject",
                "count": {"$sum": 1},
                "avg_messages": {"$avg": {"$size": "$messages"}}
            }},
            {"$sort": {"avg_messages": 1}},
            {"$limit": 3}
        ]
        
        result = await db.chat_sessions.aggregate(pipeline).to_list(length=3)
        
        weak_subjects = [r["_id"] for r in result if r.get("avg_messages", 0) < 3]
        return weak_subjects
        
    except Exception as e:
        logger.error(f"Error getting weak subjects: {e}")
        return []


async def _generate_recommendations(user_id: str, db) -> List[str]:
    """
    Generate AI-powered recommendations based on user activity.
    
    Returns: List of recommendation strings
    """
    try:
        recommendations = []
        
        # Check recent activity
        recent_sessions = await db.chat_sessions.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": (datetime.utcnow() - timedelta(days=7)).isoformat()}
        })
        
        if recent_sessions == 0:
            recommendations.append("Start a new learning session today!")
        elif recent_sessions < 3:
            recommendations.append("Try to study more regularly for better retention")
        
        # Check streak
        user_doc = await db.users.find_one({"user_id": user_id})
        if user_doc:
            streak = user_doc.get("current_streak", 0)
            if streak == 0:
                recommendations.append("Build a learning streak - study daily!")
            elif streak >= 7:
                recommendations.append(f"Amazing {streak}-day streak! Keep it going!")
        
        # Check weak subjects
        weak_subjects = await _get_weak_subjects(user_id, db)
        if weak_subjects:
            recommendations.append(f"Focus on {weak_subjects[0]} - practice makes perfect!")
        
        return recommendations[:3]  # Max 3 recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return ["Keep up the great work!"]


