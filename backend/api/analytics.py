"""
Analytics router for dashboard analytics, performance metrics, and wellness tracking
"""
from fastapi import APIRouter, HTTPException, Depends

from models.core import User
from models.ai import WellnessCheckRequest
from services.analytics_service import AnalyticsService
from dependencies import get_current_user, get_database


# Router instance
router = APIRouter(prefix="/analytics", tags=["analytics"])


# Dependency to get analytics service
async def get_analytics_service(db = Depends(get_database)) -> AnalyticsService:
    """Get analytics service instance"""
    return AnalyticsService(db)


@router.get("/dashboard")
async def get_dashboard_analytics(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get comprehensive dashboard analytics"""
    try:
        analytics = await analytics_service.get_dashboard_analytics(user.user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard analytics: {str(e)}")


@router.get("/daily-goals")
async def get_daily_goals(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get daily goals and progress"""
    try:
        goals = await analytics_service.get_daily_goals(user.user_id)
        return goals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily goals: {str(e)}")


@router.get("/subject-progress")
async def get_subject_progress(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get progress across different subjects"""
    try:
        progress = await analytics_service.get_subject_progress(user.user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subject progress: {str(e)}")


@router.post("/wellness-check")
async def perform_wellness_check(
    request: WellnessCheckRequest,
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Perform wellness check and get recommendations"""
    try:
        wellness_data = {
            "stress_level": request.stress_level,
            "motivation_level": request.motivation_level,
            "confidence_level": request.confidence_level,
            "study_satisfaction": request.study_satisfaction,
            "session_id": request.session_id
        }
        
        result = await analytics_service.wellness_check(user.user_id, wellness_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wellness check failed: {str(e)}")


@router.get("/wellness-history")
async def get_wellness_history(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get wellness check history"""
    try:
        history = await db.wellness_checks.find({
            "user_id": user.user_id
        }).sort("timestamp", -1).limit(30).to_list(length=None)
        
        # Clean up the data
        for record in history:
            if '_id' in record:
                del record['_id']
        
        return {
            "wellness_history": history,
            "total_checks": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wellness history: {str(e)}")


@router.get("/performance")
async def get_performance(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get comprehensive performance analytics (alias for performance-stats)"""
    try:
        analytics = await analytics_service.get_dashboard_analytics(user.user_id)
        subject_progress = await analytics_service.get_subject_progress(user.user_id)
        
        return {
            "overall_accuracy": analytics.get("accuracy_rate", 0),
            "study_streak": analytics.get("study_streak", 0),
            "total_study_time": analytics.get("study_time_today", 0),
            "subjects_mastery": subject_progress.get("subjects", {}),
            "performance_trend": "stable",  # TODO: Calculate from historical data
            "rank_position": None,  # Leaderboard rank - implement when leaderboard ready
            "percentile": None,  # User percentile - implement when leaderboard ready
            "weekly_progress": analytics.get("weekly_progress", []),
            "strong_subjects": [],  # TODO: Calculate from accuracy data
            "weak_subjects": [],  # TODO: Calculate from accuracy data
            "recommended_actions": []  # TODO: AI-generated recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")


@router.get("/performance-stats")
async def get_performance_stats(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get detailed performance statistics"""
    try:
        analytics = await analytics_service.get_dashboard_analytics(user.user_id)
        subject_progress = await analytics_service.get_subject_progress(user.user_id)
        
        return {
            "overall_accuracy": analytics.get("accuracy_rate", 0),
            "study_streak": analytics.get("study_streak", 0),
            "total_study_time": analytics.get("study_time_today", 0),
            "subjects_mastery": subject_progress.get("subjects", {}),
            "performance_trend": "stable",  # TODO: Calculate from historical data
            "rank_position": None,  # Leaderboard rank - implement when leaderboard ready
            "percentile": None  # User percentile - implement when leaderboard ready
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")


@router.get("/learning-analytics")
async def get_learning_analytics(
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get detailed learning analytics"""
    try:
        subject_progress = await analytics_service.get_subject_progress(user.user_id)
        daily_goals = await analytics_service.get_daily_goals(user.user_id)
        
        return {
            "learning_patterns": {
                "most_active_subject": next(iter(subject_progress.get("subjects", {})), "Mathematics"),
                "preferred_study_time": "evening",  # Would analyze from session timestamps
                "average_session_duration": 18,  # minutes
                "question_accuracy_trend": "stable"
            },
            "goal_completion": {
                "daily_completion_rate": daily_goals.get("completion_percentage", 0),
                "streak_maintenance": daily_goals.get("streak_current", 0) >= 3,
                "consistency_score": 75  # Mock calculation
            },
            "recommendations": [
                "Focus more time on weak areas in Physics",
                "Maintain current Mathematics practice frequency", 
                "Consider mock tests for better time management"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning analytics: {str(e)}")