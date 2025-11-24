"""
Test Cache Service
Pre-generates and caches high-quality tests for instant delivery
Students get tests in <1 second instead of waiting 5+ minutes
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

logger = logging.getLogger(__name__)


class TestCacheService:
    """Manages pre-generated test cache for instant delivery"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_quick_test(
        self,
        exam_type: str,
        subject: str,
        num_questions: int = 10,
        difficulty: str = "medium"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a pre-generated test from cache instantly
        
        Returns test in <100ms instead of 5+ minutes
        """
        try:
            # Find cached test matching criteria
            cached_test = await self.db.test_cache.find_one({
                "exam_type": exam_type,
                "subject": subject,
                "num_questions": num_questions,
                "difficulty": difficulty,
                "is_used": False,  # Not yet served to any user
                "quality_score": {"$gte": 0.8}  # High quality only
            })
            
            if cached_test:
                logger.info(f"✅ Serving cached test: {cached_test['test_id']}")
                
                # Mark as used
                await self.db.test_cache.update_one(
                    {"_id": cached_test["_id"]},
                    {"$set": {"is_used": True, "used_at": datetime.now(timezone.utc)}}
                )
                
                return cached_test
            
            logger.warning(f"⚠️ No cached test found for {exam_type} - {subject} - {num_questions}Q - {difficulty}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache lookup failed: {e}")
            return None
    
    async def cache_test(
        self,
        exam_type: str,
        subject: str,
        questions: List[Dict[str, Any]],
        difficulty: str,
        quality_score: float
    ) -> bool:
        """Cache a generated test for future use"""
        try:
            import uuid
            
            test_doc = {
                "test_id": str(uuid.uuid4()),
                "exam_type": exam_type,
                "subject": subject,
                "num_questions": len(questions),
                "difficulty": difficulty,
                "questions": questions,
                "quality_score": quality_score,
                "is_used": False,
                "created_at": datetime.now(timezone.utc),
                "used_at": None
            }
            
            await self.db.test_cache.insert_one(test_doc)
            logger.info(f"✅ Cached test: {test_doc['test_id']} - {exam_type} - {subject} - {len(questions)}Q")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cache test: {e}")
            return False


# Pre-defined high-quality test templates for instant serving
PRESET_TESTS = {
    "JEE_MATHS_QUICK_10": {
        "exam_type": "JEE",
        "subject": "Mathematics",
        "title": "JEE Maths Quick Test",
        "num_questions": 10,
        "duration_mins": 15,
        "difficulty": "medium",
        "description": "Quick practice for JEE Mathematics fundamentals"
    },
    "JEE_PHYSICS_QUICK_10": {
        "exam_type": "JEE",
        "subject": "Physics",
        "title": "JEE Physics Quick Test",
        "num_questions": 10,
        "duration_mins": 15,
        "difficulty": "medium",
        "description": "Quick practice for JEE Physics concepts"
    },
    "NEET_BIOLOGY_QUICK_15": {
        "exam_type": "NEET",
        "subject": "Biology",
        "title": "NEET Biology Quick Test",
        "num_questions": 15,
        "duration_mins": 20,
        "difficulty": "medium",
        "description": "Quick practice for NEET Biology"
    },
    "CBSE_CHEMISTRY_QUICK_10": {
        "exam_type": "CBSE",
        "subject": "Chemistry",
        "title": "CBSE Chemistry Quick Test",
        "num_questions": 10,
        "duration_mins": 15,
        "difficulty": "easy",
        "description": "Quick practice for CBSE Chemistry"
    }
}


def get_preset_tests() -> List[Dict[str, Any]]:
    """Get all preset test templates"""
    return list(PRESET_TESTS.values())


def get_preset_by_id(preset_id: str) -> Optional[Dict[str, Any]]:
    """Get specific preset test template"""
    return PRESET_TESTS.get(preset_id)



