"""
Continuity Engine - Topic Thread Detection
Maintains concept threads across sessions for "continue where we left off" experience
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContinuityEngine:
    """
    Detects and maintains topic continuity across sessions
    
    Features:
    - Detect if user is continuing a previous topic
    - Track concept threads (e.g., [derivatives, integrals, ftc])
    - Generate contextual suggestions ("Last time we covered X...")
    - Identify incomplete learning paths
    """
    
    def __init__(self, db):
        self.db = db
        self.continuation_threshold_hours = 72  # Consider continuation if within 3 days
    
    def _normalize_datetime(self, dt_value) -> Optional[datetime]:
        """
        FIX #10: Robust datetime normalization with proper timezone handling
        
        Handles:
        - datetime objects (aware and naive)
        - ISO format strings
        - MongoDB datetime
        
        Returns timezone-aware datetime or None if parsing fails
        """
        try:
            # Handle None
            if dt_value is None:
                return None
            
            # Handle string
            if isinstance(dt_value, str):
                from dateutil import parser
                dt_value = parser.parse(dt_value)
            
            # Handle datetime
            if isinstance(dt_value, datetime):
                # If naive, assume UTC (most common in our system)
                if dt_value.tzinfo is None:
                    # Log warning for visibility
                    logger.debug(f"Converting naive datetime to UTC (assumed)")
                    return dt_value.replace(tzinfo=timezone.utc)
                
                # If already timezone-aware, convert to UTC for comparison
                return dt_value.astimezone(timezone.utc)
            
            logger.warning(f"Unknown datetime type: {type(dt_value)}")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to normalize datetime: {e}")
            return None
    
    async def detect_topic_continuation(
        self,
        user_id: str,
        current_query: str
    ) -> Dict[str, Any]:
        """
        Detect if user is continuing a previous topic
        
        Args:
            user_id: Student user ID
            current_query: Current question
        
        Returns:
            Dict with continuation info and suggestions
        """
        try:
            # Get user's learning profile
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if not profile:
                return {"is_continuation": False}
            
            # Get last active info
            last_topic = profile.get("last_active_topic")
            concept_thread = profile.get("last_active_concept_thread", [])
            last_updated = profile.get("updated_at")
            
            # Check if within continuation window
            # FIX #10: Robust timezone handling
            if last_updated:
                last_updated = self._normalize_datetime(last_updated)
                
                if last_updated:
                    hours_since = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
                    if hours_since > self.continuation_threshold_hours:
                        # Too old, not a continuation
                        return {"is_continuation": False}
                else:
                    # FIX #10: If we can't parse the datetime, log and continue without time check
                    logger.warning(f"⚠️ Could not parse last_updated timestamp, skipping time check")
                    hours_since = None
            
            # Extract concepts from current query
            current_concepts = self._extract_concepts(current_query)
            
            # Check if any current concepts are in the previous thread
            is_continuation = any(
                concept in concept_thread
                for concept in current_concepts
            )
            
            if is_continuation:
                # Get last session details
                last_session_summary = await self._get_last_session_summary(
                    user_id,
                    last_topic
                )
                
                # Generate continuation suggestion
                suggestion = self._generate_continuation_message(
                    concept_thread,
                    current_concepts,
                    last_session_summary
                )
                
                return {
                    "is_continuation": True,
                    "last_topic": last_topic,
                    "concept_thread": concept_thread,
                    "concepts_covered_before": last_session_summary.get("concepts_covered", []),
                    "last_depth_level": last_session_summary.get("depth_level", "medium"),
                    "suggestion": suggestion,
                    "hours_since_last": hours_since if last_updated else None
                }
            
            return {"is_continuation": False}
            
        except Exception as e:
            logger.error(f"❌ Topic continuation detection failed: {e}")
            return {"is_continuation": False}
    
    async def update_concept_thread(
        self,
        user_id: str,
        topic: str,
        concepts: List[str]
    ):
        """
        Update active concept thread
        
        Args:
            user_id: Student user ID
            topic: Main topic
            concepts: List of concepts covered
        """
        try:
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "last_active_topic": topic,
                        "last_active_concept_thread": concepts[-5:],  # Keep last 5
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            logger.info(f"🔗 Updated concept thread: {' → '.join(concepts[-3:])}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update concept thread: {e}")
    
    async def mark_concept_complete(
        self,
        user_id: str,
        concept: str
    ):
        """Mark a concept as complete (remove from incomplete list)"""
        try:
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$pull": {
                        "incomplete_concepts": concept
                    },
                    "$addToSet": {
                        "completed_concepts": concept
                    }
                }
            )
            
            logger.info(f"✅ Marked {concept} as complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to mark concept complete: {e}")
    
    async def add_incomplete_concept(
        self,
        user_id: str,
        concept: str,
        reason: str = "not_finished"
    ):
        """Add concept to incomplete list (needs more work)"""
        try:
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$addToSet": {
                        "incomplete_concepts": concept
                    }
                },
                upsert=True
            )
            
            logger.info(f"📝 Added {concept} to incomplete list ({reason})")
            
        except Exception as e:
            logger.error(f"❌ Failed to add incomplete concept: {e}")
    
    async def _get_last_session_summary(
        self,
        user_id: str,
        topic: str
    ) -> Dict[str, Any]:
        """Get summary of last session on this topic"""
        try:
            # Find most recent session with this topic
            recent_messages = await self.db.chat_messages.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(20).to_list(None)
            
            # Filter messages related to topic
            topic_messages = [
                msg for msg in recent_messages
                if topic in str(msg.get("user_message", "")).lower() or
                   topic in str(msg.get("ai_response", "")).lower()
            ]
            
            if not topic_messages:
                return {}
            
            # Extract what was covered
            concepts_covered = []
            for msg in topic_messages:
                concepts_covered.extend(
                    self._extract_concepts(
                        msg.get("user_message", "")
                    )
                )
            
            return {
                "concepts_covered": list(set(concepts_covered)),
                "depth_level": "medium",  # Can be inferred from mastery
                "last_timestamp": topic_messages[0].get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get last session summary: {e}")
            return {}
    
    def _generate_continuation_message(
        self,
        concept_thread: List[str],
        current_concepts: List[str],
        last_session: Dict[str, Any]
    ) -> str:
        """Generate friendly continuation message"""
        
        if not concept_thread:
            return ""
        
        # Get what was covered before
        covered = last_session.get("concepts_covered", [])
        if not covered:
            covered = concept_thread[-2:] if len(concept_thread) > 1 else concept_thread
        
        # Humanize concept names
        covered_humanized = [self._humanize_concept(c) for c in covered[:2]]
        
        return f"Last time we covered {' and '.join(covered_humanized)}. Ready to continue?"
    
    def _humanize_concept(self, concept: str) -> str:
        """Convert concept_name_format to human-readable"""
        return concept.replace("_", " ").title()
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract concepts from text (simplified)"""
        concepts = []
        text_lower = text.lower()
        
        if "derivative" in text_lower:
            concepts.append("derivatives")
        if "integral" in text_lower:
            concepts.append("integrals")
        if "newton" in text_lower:
            concepts.append("newton_laws")
        if "force" in text_lower:
            concepts.append("force")
        
        return concepts
    
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
                next_review = memory.get("next_review_at")
                due_hours = 0
                if next_review:
                    # Ensure next_review is timezone-aware before subtraction
                    if hasattr(next_review, 'tzinfo') and next_review.tzinfo is None:
                        next_review = next_review.replace(tzinfo=timezone.utc)
                    due_hours = (now - next_review).total_seconds() / 3600
                
                reviews.append({
                    "fact_id": memory.get("fact_id"),
                    "topic": memory.get("topic"),
                    "content": memory.get("content"),
                    "due_since_hours": due_hours,
                    "review_count": memory.get("reinforcement_count", 0),
                    "current_interval": memory.get("review_interval_days", 1)
                })
            
            logger.info(f"📅 {len(reviews)} concepts due for review")
            return reviews
            
        except Exception as e:
            logger.error(f"❌ Failed to get due reviews: {e}")
            return []

