"""
👤 Profile Service - Replaces Weak Area Detective Agent
=======================================================

Background service that analyzes user interactions and updates weak areas.
This is NOT a tool for LLMs - it's a helper function that runs automatically.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Profile Service - Detects and updates student weak areas.
    
    This replaces the Weak Area Detective Agent.
    It's a background service, not an agent tool.
    """
    
    def __init__(self, db_client=None):
        """
        Initialize Profile Service.
        
        Args:
            db_client: MongoDB database client
        """
        self.db = db_client
        logger.info("👤 ProfileService initialized")
    
    async def detect_and_update_weakness(
        self,
        user_id: str,
        interaction_history: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze user's interaction history and update weak areas.
        
        This function:
        1. Analyzes recent conversations
        2. Detects confusion signals ("I don't understand", quiz failures)
        3. Extracts topics mentioned
        4. Updates user_profile.weak_areas
        
        Args:
            user_id: User identifier
            interaction_history: List of recent conversation messages
        
        Returns:
            Dict with detected weak areas and update status
        """
        try:
            if self.db is None:
                logger.warning("⚠️ No database client - skipping weak area detection")
                return {"success": False, "reason": "no_database"}
            
            # Analyze interaction history for confusion signals
            confusion_signals = [
                "i don't understand",
                "i don't get it",
                "confused",
                "not clear",
                "can't solve",
                "stuck",
                "difficult",
                "hard",
                "wrong",
                "incorrect",
                "failed",
                "mistake"
            ]
            
            detected_topics = []
            confusion_count = 0
            
            for message in interaction_history[-10:]:  # Last 10 messages
                message_lower = message.lower()
                
                # Check for confusion signals
                if any(signal in message_lower for signal in confusion_signals):
                    confusion_count += 1
                    
                    # Try to extract topic from context
                    # Simple keyword-based extraction (can be enhanced with NLP)
                    topic_keywords = self._extract_topic_keywords(message)
                    if topic_keywords:
                        detected_topics.extend(topic_keywords)
            
            # If significant confusion detected, update weak areas
            if confusion_count >= 2 or detected_topics:
                await self._update_weak_areas(user_id, detected_topics)
                
                logger.info(f"👤 Updated weak areas for user {user_id}: {detected_topics}")
                
                return {
                    "success": True,
                    "confusion_signals": confusion_count,
                    "detected_topics": list(set(detected_topics)),
                    "updated": True
                }
            
            return {
                "success": True,
                "confusion_signals": confusion_count,
                "detected_topics": [],
                "updated": False
            }
            
        except Exception as e:
            logger.error(f"❌ ProfileService error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _extract_topic_keywords(self, message: str) -> List[str]:
        """
        Extract topic keywords from a message.
        
        This is a simple implementation. In production, use NLP/NER.
        """
        # Common topic keywords
        topic_patterns = {
            "rotational motion": ["rotational", "moment of inertia", "angular"],
            "thermodynamics": ["thermodynamics", "heat", "entropy", "enthalpy"],
            "organic chemistry": ["organic", "reaction", "mechanism", "compound"],
            "calculus": ["calculus", "derivative", "integral", "differentiation"],
            "mechanics": ["mechanics", "force", "motion", "newton"],
            "electricity": ["electricity", "circuit", "current", "voltage"],
            "optics": ["optics", "light", "reflection", "refraction"],
            "genetics": ["genetics", "dna", "gene", "inheritance"],
            "human physiology": ["physiology", "organ", "system", "blood"]
        }
        
        message_lower = message.lower()
        detected = []
        
        for topic, keywords in topic_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                detected.append(topic)
        
        return detected
    
    async def _update_weak_areas(self, user_id: str, topics: List[str]):
        """
        Update user profile with detected weak areas.
        
        Args:
            user_id: User identifier
            topics: List of topics to add to weak areas
        """
        try:
            if self.db is None:
                return
            
            # Get current user profile
            user_doc = await self.db.users.find_one({"user_id": user_id})
            
            if not user_doc:
                logger.warning(f"User {user_id} not found")
                return
            
            # Get existing weak areas
            current_weak_areas = user_doc.get("weak_areas", [])
            
            # Add new topics (avoid duplicates)
            updated_weak_areas = list(set(current_weak_areas + topics))
            
            # Update user profile
            await self.db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "weak_areas": updated_weak_areas,
                        "weak_areas_updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"✅ Updated weak areas for {user_id}: {len(updated_weak_areas)} total")
            
        except Exception as e:
            logger.error(f"❌ Failed to update weak areas: {e}", exc_info=True)


# Singleton instance
_profile_service_instance = None


def get_profile_service(db_client=None) -> ProfileService:
    """Get or create ProfileService instance"""
    global _profile_service_instance
    if _profile_service_instance is None:
        _profile_service_instance = ProfileService(db_client)
    return _profile_service_instance

