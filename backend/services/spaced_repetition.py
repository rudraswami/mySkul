"""
Spaced Repetition Engine - SM-2 Algorithm
Scientifically optimized review scheduling based on forgetting curve
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SpacedRepetitionEngine:
    """
    Implements SM-2 algorithm for optimal review timing
    
    Features:
    - SM-2 algorithm (SuperMemo 2)
    - Forgetting curve optimization
    - Adaptive interval adjustment
    - Review scheduling
    - Quality-based easiness factor
    
    SM-2 Algorithm Overview:
    - Quality 0-2 (fail): Restart interval
    - Quality 3+ (pass): Increase interval exponentially
    - Easiness factor adjusts based on recall quality
    """
    
    def __init__(self, db=None):
        self.db = db
        self.min_easiness = 1.3
        self.max_easiness = 2.5
    
    def calculate_next_review(
        self,
        current_interval_days: int,
        quality: int,  # 0-5 (0=total forget, 5=perfect recall)
        current_easiness: float = 2.5
    ) -> Dict[str, Any]:
        """
        Calculate next review time using SM-2 algorithm
        
        Args:
            current_interval_days: Current review interval
            quality: Recall quality (0-5)
                - 0: Complete blackout
                - 1: Incorrect, but familiar
                - 2: Incorrect, but on the verge
                - 3: Correct with difficulty
                - 4: Correct with hesitation
                - 5: Perfect recall
            current_easiness: Current easiness factor
        
        Returns:
            Dict with next_review_at, interval_days, easiness_factor
        """
        try:
            # Validate inputs
            quality = max(0, min(5, quality))
            current_easiness = max(self.min_easiness, min(self.max_easiness, current_easiness))
            
            # Calculate new easiness factor
            new_easiness = current_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_easiness = max(self.min_easiness, new_easiness)
            
            # Calculate new interval
            if quality < 3:
                # Failed recall - restart
                new_interval = 1
                new_easiness = max(self.min_easiness, new_easiness - 0.2)  # Penalize
            else:
                # Successful recall - increase interval
                if current_interval_days == 0:
                    new_interval = 1
                elif current_interval_days == 1:
                    new_interval = 6
                else:
                    new_interval = int(current_interval_days * new_easiness)
            
            # Calculate next review date
            next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)
            
            result = {
                "next_review_at": next_review,
                "interval_days": new_interval,
                "easiness_factor": new_easiness,
                "quality_score": quality,
                "review_scheduled": True
            }
            
            logger.info(
                f"📅 Next review in {new_interval} days "
                f"(quality={quality}, easiness={new_easiness:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ SM-2 calculation failed: {e}")
            # Fallback: review in 1 day
            return {
                "next_review_at": datetime.now(timezone.utc) + timedelta(days=1),
                "interval_days": 1,
                "easiness_factor": 2.5,
                "quality_score": quality,
                "review_scheduled": False
            }
    
    def infer_quality_from_feedback(
        self,
        feedback: str,
        time_taken_seconds: float = None
    ) -> int:
        """
        Infer SM-2 quality score from user feedback
        
        Args:
            feedback: User feedback ("helpful", "not_helpful", etc.)
            time_taken_seconds: Time taken to answer (optional)
        
        Returns:
            Quality score (0-5)
        """
        # Map feedback to quality
        feedback_map = {
            "helpful": 4,  # Correct with hesitation
            "very_helpful": 5,  # Perfect recall
            "not_helpful": 2,  # Incorrect, on verge
            "confused": 1,  # Incorrect, but familiar
            "wrong": 0  # Complete blackout
        }
        
        base_quality = feedback_map.get(feedback, 3)  # Default: 3 (correct with difficulty)
        
        # Adjust based on time taken (if available)
        if time_taken_seconds:
            if time_taken_seconds < 10:
                # Very fast = better recall
                base_quality = min(5, base_quality + 1)
            elif time_taken_seconds > 60:
                # Slow = harder recall
                base_quality = max(0, base_quality - 1)
        
        return base_quality
    
    async def get_due_reviews(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get concepts due for review (spaced repetition)
        
        Args:
            user_id: Student user ID
            limit: Max number of reviews to return
        
        Returns:
            List of concepts due for review
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Find memories with next_review_at <= now
            due_memories = await self.db.user_memory_facts.find({
                "user_id": user_id,
                "is_active": True,
                "next_review_at": {"$lte": now}
            }).sort("next_review_at", 1).limit(limit).to_list(None)
            
            reviews = []
            for memory in due_memories:
                # Handle timezone-naive datetimes from database
                next_review = memory.get("next_review_at")
                due_since_hours = 0
                if next_review:
                    # Convert naive datetime to UTC-aware if needed
                    if next_review.tzinfo is None:
                        next_review = next_review.replace(tzinfo=timezone.utc)
                    due_since_hours = (now - next_review).total_seconds() / 3600
                
                reviews.append({
                    "fact_id": memory.get("fact_id", ""),
                    "topic": memory.get("topic", ""),
                    "subject": memory.get("subject", "General"),
                    "concept": memory.get("topic", memory.get("content", "")[:50]),
                    "content": memory.get("content", ""),
                    "due_since_hours": max(0, due_since_hours),
                    "review_count": memory.get("reinforcement_count", 0),
                    "current_interval": memory.get("review_interval_days", 1)
                })
            
            logger.info(f"📅 {len(reviews)} concepts due for review")
            return reviews
            
        except Exception as e:
            logger.error(f"❌ Failed to get due reviews: {e}")
            return []
    
    async def update_concept_thread(
        self,
        user_id: str,
        topic: str,
        concepts: List[str]
    ):
        """
        Update the active concept thread
        
        Args:
            user_id: Student user ID
            topic: Main topic
            concepts: List of concepts covered in this session
        """
        try:
            # Get current thread
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            current_thread = profile.get("last_active_concept_thread", []) if profile else []
            
            # Append new concepts (keep last 10)
            updated_thread = (current_thread + concepts)[-10:]
            
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "last_active_topic": topic,
                        "last_active_concept_thread": updated_thread,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            logger.info(f"🔗 Concept thread updated: {' → '.join(updated_thread[-3:])}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update concept thread: {e}")
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        # Calculus
        if "derivative" in text_lower or "differentiation" in text_lower:
            concepts.append("derivatives")
        if "integral" in text_lower or "integration" in text_lower:
            concepts.append("integrals")
        if "fundamental theorem" in text_lower:
            concepts.append("fundamental_theorem_calculus")
        if "limit" in text_lower:
            concepts.append("limits")
        
        # Physics
        if "newton" in text_lower and "law" in text_lower:
            concepts.append("newton_laws")
        if "force" in text_lower:
            concepts.append("force")
        if "motion" in text_lower or "kinematics" in text_lower:
            concepts.append("kinematics")
        
        return concepts

