"""
Analytics service for dashboard metrics, performance tracking, and user analytics
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics, dashboard metrics, and performance tracking"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def get_dashboard_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics for a user"""
        try:
            # Get user activity data
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            
            # Basic analytics structure
            analytics = {
                "study_time_today": await self._get_study_time(user_id, today),
                "study_streak": await self._get_study_streak(user_id),
                "accuracy_rate": await self._get_accuracy_rate(user_id),
                "progress_this_week": await self._get_weekly_progress(user_id),
                "active_subjects": await self._get_active_subjects(user_id),
                "achievement_count": await self._get_achievement_count(user_id),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Dashboard analytics error: {str(e)}")
            return {
                "study_time_today": 0,
                "study_streak": 0,
                "accuracy_rate": 0.0,
                "progress_this_week": 0,
                "active_subjects": [],
                "achievement_count": 0,
                "error": str(e)
            }
    
    async def get_daily_goals(self, user_id: str) -> Dict[str, Any]:
        """Get daily goals and progress"""
        try:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            
            goals = {
                "study_time_goal": 120,  # minutes
                "study_time_actual": await self._get_study_time(user_id, today),
                "questions_goal": 20,
                "questions_actual": await self._get_questions_attempted_today(user_id),
                "concepts_goal": 3,
                "concepts_actual": await self._get_concepts_learned_today(user_id),
                "streak_current": await self._get_study_streak(user_id),
                "streak_target": 7,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate completion percentage
            goals["completion_percentage"] = min(100, (
                (goals["study_time_actual"] / max(1, goals["study_time_goal"]) * 33.33) +
                (goals["questions_actual"] / max(1, goals["questions_goal"]) * 33.33) +
                (goals["concepts_actual"] / max(1, goals["concepts_goal"]) * 33.33)
            ))
            
            return goals
            
        except Exception as e:
            logger.error(f"Daily goals error: {str(e)}")
            return {
                "study_time_goal": 120,
                "study_time_actual": 0,
                "questions_goal": 20,
                "questions_actual": 0,
                "concepts_goal": 3,
                "concepts_actual": 0,
                "completion_percentage": 0,
                "error": str(e)
            }
    
    async def get_subject_progress(self, user_id: str) -> Dict[str, Any]:
        """Get progress across different subjects"""
        try:
            # Get progress data from various collections
            subjects = ["Mathematics", "Physics", "Chemistry", "Biology"]
            progress_data = {}
            
            for subject in subjects:
                # Get chat sessions for this subject
                chat_count = await self.db.chat_sessions.count_documents({
                    "user_id": user_id,
                    "subject": subject
                })
                
                # Get mock test results for this subject
                mock_results = await self.db.mock_test_results.find({
                    "user_id": user_id,
                    "subject": subject
                }).to_list(length=None)
                
                avg_score = 0
                if mock_results:
                    total_score = sum(result.get("percentage", 0) for result in mock_results)
                    avg_score = total_score / len(mock_results)
                
                progress_data[subject] = {
                    "sessions_count": chat_count,
                    "mock_tests_taken": len(mock_results),
                    "average_score": round(avg_score, 1),
                    "mastery_level": min(100, avg_score + (chat_count * 5)),  # Simple calculation
                    "last_activity": datetime.now(timezone.utc).isoformat()
                }
            
            return {
                "subjects": progress_data,
                "overall_progress": sum(data["mastery_level"] for data in progress_data.values()) / len(subjects),
                "total_sessions": sum(data["sessions_count"] for data in progress_data.values()),
                "total_tests": sum(data["mock_tests_taken"] for data in progress_data.values()),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Subject progress error: {str(e)}")
            return {"subjects": {}, "overall_progress": 0, "error": str(e)}
    
    async def wellness_check(self, user_id: str, wellness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform wellness check and provide recommendations"""
        try:
            # Save wellness data
            wellness_record = {
                "user_id": user_id,
                "stress_level": wellness_data.get("stress_level", 5),
                "motivation_level": wellness_data.get("motivation_level", 5),
                "confidence_level": wellness_data.get("confidence_level", 5),
                "study_satisfaction": wellness_data.get("study_satisfaction", 5),
                "session_id": wellness_data.get("session_id"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.wellness_checks.insert_one(wellness_record)
            
            # Generate recommendations based on stress level
            stress_level = wellness_data.get("stress_level", 5)
            if stress_level >= 7:
                recommendation = "Take a 15-20 minute break. Try some deep breathing exercises or light stretching."
                motivational_content = "Remember, breaks aren't signs of weakness - they're strategic recovery periods that boost performance! 🌟"
            elif stress_level >= 4:
                recommendation = "You're doing well! Consider a 5-10 minute break between topics."
                motivational_content = "Your dedication is impressive! Keep this steady pace and you'll achieve amazing results! ✨"
            else:
                recommendation = "Great energy level! This is perfect for tackling challenging concepts."
                motivational_content = "You're in the perfect state for deep learning! Channel this positive energy into your studies! 🚀"
            
            return {
                "wellness_score": (
                    wellness_data.get("motivation_level", 5) + 
                    wellness_data.get("confidence_level", 5) + 
                    (10 - wellness_data.get("stress_level", 5))
                ) / 3,
                "recommendation": recommendation,
                "motivational_content": motivational_content,
                "break_recommended": stress_level >= 6,
                "next_check_in": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wellness check error: {str(e)}")
            return {
                "wellness_score": 5.0,
                "recommendation": "Take care of yourself while studying!",
                "error": str(e)
            }
    
    # Helper methods
    async def _get_study_time(self, user_id: str, date: datetime) -> int:
        """Get study time for a specific date in minutes"""
        try:
            # This would aggregate from various activity logs
            # For now, return a calculated estimate
            sessions = await self.db.chat_sessions.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": date.isoformat()}
            })
            return sessions * 15  # Assume 15 minutes per session
        except:
            return 0
    
    async def _get_study_streak(self, user_id: str) -> int:
        """Get current study streak in days"""
        try:
            # Simple streak calculation based on daily activity
            today = datetime.now(timezone.utc).date()
            streak = 0
            current_date = today
            
            for days_back in range(30):  # Check last 30 days
                check_date = current_date - timedelta(days=days_back)
                check_datetime = datetime.combine(check_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                activity = await self.db.chat_sessions.count_documents({
                    "user_id": user_id,
                    "created_at": {"$gte": check_datetime.isoformat(), "$lt": (check_datetime + timedelta(days=1)).isoformat()}
                })
                
                if activity > 0:
                    streak += 1
                else:
                    break
            
            return streak
        except:
            return 0
    
    async def _get_accuracy_rate(self, user_id: str) -> float:
        """Get overall accuracy rate"""
        try:
            results = await self.db.mock_test_results.find({"user_id": user_id}).to_list(length=None)
            if results:
                total_score = sum(result.get("percentage", 0) for result in results)
                return round(total_score / len(results), 1)
            return 0.0
        except:
            return 0.0
    
    async def _get_weekly_progress(self, user_id: str) -> int:
        """Get weekly progress as percentage"""
        try:
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_activity = await self.db.chat_sessions.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": week_ago.isoformat()}
            })
            return min(100, recent_activity * 10)  # Cap at 100%
        except:
            return 0
    
    async def _get_active_subjects(self, user_id: str) -> List[str]:
        """Get list of actively studied subjects"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            results = await self.db.chat_sessions.aggregate(pipeline).to_list(length=None)
            return [result["_id"] for result in results]
        except:
            return []
    
    async def _get_achievement_count(self, user_id: str) -> int:
        """Get total achievement count"""
        try:
            return await self.db.user_achievements.count_documents({"user_id": user_id})
        except:
            return 0
    
    async def _get_questions_attempted_today(self, user_id: str) -> int:
        """Get questions attempted today"""
        try:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            results = await self.db.mock_test_attempts.find({
                "user_id": user_id,
                "timestamp": {"$gte": today.isoformat()}
            }).to_list(length=None)
            return len(results)
        except:
            return 0
    
    async def _get_concepts_learned_today(self, user_id: str) -> int:
        """Get concepts learned today"""
        try:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            sessions = await self.db.chat_sessions.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": today.isoformat()}
            })
            return min(sessions, 10)  # Each session = 1 concept, cap at 10
        except:
            return 0