"""
Mock Tests service for test generation, submission, and performance tracking
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


logger = logging.getLogger(__name__)


class MockTestsService:
    """Service for managing mock tests, submissions, and performance tracking"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_user_tests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tests for a user"""
        try:
            tests = await self.db.mock_tests.find({
                "$or": [
                    {"student_id": user_id},
                    {"user_id": user_id}
                ]
            }).sort("generated_at", -1).to_list(length=None)
            
            # Clean up MongoDB fields
            for test in tests:
                if '_id' in test:
                    del test['_id']
            
            return tests
            
        except Exception as e:
            logger.error(f"Get user tests error: {str(e)}")
            return []
    
    async def get_test(self, test_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific test"""
        try:
            test = await self.db.mock_tests.find_one({
                "test_id": test_id,
                "$or": [
                    {"student_id": user_id},
                    {"user_id": user_id}
                ]
            })
            
            if test and '_id' in test:
                del test['_id']
            
            return test
            
        except Exception as e:
            logger.error(f"Get test error: {str(e)}")
            return None
    
    async def get_test_attempts(self, test_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all attempts for a test"""
        try:
            attempts = await self.db.test_attempts.find({
                "test_id": test_id,
                "student_id": user_id
            }).sort("submitted_at", -1).to_list(length=None)
            
            # Clean up MongoDB fields
            for attempt in attempts:
                if '_id' in attempt:
                    del attempt['_id']
            
            return attempts
            
        except Exception as e:
            logger.error(f"Get test attempts error: {str(e)}")
            return []
    
    async def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for user"""
        try:
            total_tests = await self.db.mock_tests.count_documents({
                "$or": [
                    {"student_id": user_id},
                    {"user_id": user_id}
                ]
            })
            
            submitted_tests = await self.db.mock_tests.count_documents({
                "$or": [
                    {"student_id": user_id},
                    {"user_id": user_id}
                ],
                "status": "submitted"
            })
            
            # Get average score from attempts
            attempts = await self.db.test_attempts.find({
                "student_id": user_id
            }).to_list(length=None)
            
            avg_score = 0.0
            if attempts:
                total_percentage = sum(a.get('percentage', 0) for a in attempts)
                avg_score = total_percentage / len(attempts)
            
            return {
                "total_tests": total_tests,
                "submitted_tests": submitted_tests,
                "average_score": round(avg_score, 2),
                "total_attempts": len(attempts)
            }
            
        except Exception as e:
            logger.error(f"Get dashboard stats error: {str(e)}")
            return {
                "total_tests": 0,
                "submitted_tests": 0,
                "average_score": 0.0,
                "total_attempts": 0
            }
    
    async def get_performance_trends(self, user_id: str) -> Dict[str, Any]:
        """Get performance trends for user"""
        try:
            attempts = await self.db.test_attempts.find({
                "student_id": user_id
            }).sort("submitted_at", 1).to_list(length=None)
            
            trends = []
            for attempt in attempts:
                trends.append({
                    "date": attempt.get('submitted_at', datetime.now(timezone.utc)).isoformat() if isinstance(attempt.get('submitted_at'), datetime) else attempt.get('submitted_at'),
                    "score": attempt.get('percentage', 0),
                    "test_id": attempt.get('test_id')
                })
            
            return {
                "trends": trends,
                "total_attempts": len(attempts)
            }
            
        except Exception as e:
            logger.error(f"Get performance trends error: {str(e)}")
            return {"trends": [], "total_attempts": 0}
    
    async def get_available_subjects(self, user_id: str, exam_type: str) -> List[str]:
        """Get available subjects for an exam type"""
        # This would typically query a subjects collection or configuration
        # For now, return static lists based on exam type
        subject_map = {
            "JEE": ["Mathematics", "Physics", "Chemistry"],
            "NEET": ["Physics", "Chemistry", "Biology"],
            "UPSC": ["History", "Geography", "Polity", "Economy", "Science & Technology"]
        }
        return subject_map.get(exam_type, ["General Studies"])
