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
            if last_updated:
                if isinstance(last_updated, str):
                    from dateutil import parser
                    last_updated = parser.parse(last_updated)
                
                # Ensure both datetimes are timezone-aware
                if last_updated.tzinfo is None:
                    last_updated = last_updated.replace(tzinfo=timezone.utc)
                
                hours_since = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
                if hours_since > self.continuation_threshold_hours:
                    # Too old, not a continuation
                    return {"is_continuation": False}
            
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

