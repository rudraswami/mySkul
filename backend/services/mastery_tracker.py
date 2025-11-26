"""
Mastery Tracking Engine
Tracks student mastery levels (0-100) per topic with history
"""
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MasteryTracker:
    """
    Track and update student mastery levels per topic
    
    Features:
    - 0-100 mastery scale
    - Historical tracking
    - Multi-factor updates (quiz, feedback, time, errors)
    - Mastery level bucketing (beginner/intermediate/advanced)
    - Dashboard-ready analytics
    """
    
    def __init__(self, db):
        self.db = db
    
    async def get_mastery_level(
        self,
        user_id: str,
        topic: str
    ) -> int:
        """
        Get current mastery level for a topic
        
        Args:
            user_id: Student user ID
            topic: Topic identifier (e.g., "calculus_derivatives")
        
        Returns:
            Mastery level (0-100)
        """
        try:
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if not profile:
                logger.info(f"📝 No profile found for {user_id}, returning 0")
                return 0
            
            mastery = profile.get("mastery_levels", {}).get(topic, 0)
            logger.info(f"📊 Mastery level for {topic}: {mastery}/100")
            
            return mastery
            
        except Exception as e:
            logger.error(f"❌ Failed to get mastery level: {e}")
            return 0
    
    async def update_mastery(
        self,
        user_id: str,
        topic: str,
        delta: int,
        reason: str = "question_answered"
    ):
        """
        Update mastery level for a topic
        
        Args:
            user_id: Student user ID
            topic: Topic identifier
            delta: Change in mastery (+/- value)
            reason: Reason for update (quiz_result, feedback, etc.)
        """
        try:
            # Get current mastery
            current = await self.get_mastery_level(user_id, topic)
            
            # Calculate new mastery (clamped to 0-100)
            new_mastery = max(0, min(100, current + delta))
            
            # Determine mastery bucket
            bucket = self._get_mastery_bucket(new_mastery)
            
            # Update in database
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"mastery_levels.{topic}": new_mastery,
                        f"mastery_buckets.{topic}": bucket,
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$push": {
                        "mastery_history": {
                            "topic": topic,
                            "old_level": current,
                            "new_level": new_mastery,
                            "delta": delta,
                            "reason": reason,
                            "timestamp": datetime.now(timezone.utc),
                            "bucket": bucket
                        }
                    }
                },
                upsert=True
            )
            
            logger.info(f"📈 Mastery updated: {topic} {current} → {new_mastery} ({bucket}) [{reason}]")
            
        except Exception as e:
            logger.error(f"❌ Failed to update mastery: {e}")
    
    async def get_all_masteries(
        self,
        user_id: str
    ) -> Dict[str, int]:
        """
        Get all mastery levels for dashboard
        
        Returns:
            Dict of topic -> mastery_level
        """
        try:
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if not profile:
                return {}
            
            return profile.get("mastery_levels", {})
            
        except Exception as e:
            logger.error(f"❌ Failed to get all masteries: {e}")
            return {}
    
    async def get_weak_topics(
        self,
        user_id: str,
        threshold: int = 40
    ) -> List[Dict[str, Any]]:
        """
        Get topics where student is weak (mastery < threshold)
        
        Args:
            user_id: Student user ID
            threshold: Mastery threshold (default: 40)
        
        Returns:
            List of weak topics with mastery levels
        """
        try:
            masteries = await self.get_all_masteries(user_id)
            
            weak_topics = [
                {
                    "topic": topic,
                    "mastery": level,
                    "bucket": self._get_mastery_bucket(level),
                    "needs_practice": True
                }
                for topic, level in masteries.items()
                if level < threshold
            ]
            
            # Sort by mastery (weakest first)
            weak_topics.sort(key=lambda x: x["mastery"])
            
            logger.info(f"📉 Found {len(weak_topics)} weak topics for user")
            return weak_topics
            
        except Exception as e:
            logger.error(f"❌ Failed to get weak topics: {e}")
            return []
    
    async def get_strong_topics(
        self,
        user_id: str,
        threshold: int = 70
    ) -> List[Dict[str, Any]]:
        """
        Get topics where student is strong (mastery >= threshold)
        
        Returns:
            List of strong topics
        """
        try:
            masteries = await self.get_all_masteries(user_id)
            
            strong_topics = [
                {
                    "topic": topic,
                    "mastery": level,
                    "bucket": self._get_mastery_bucket(level),
                    "achievement_earned": level >= 90
                }
                for topic, level in masteries.items()
                if level >= threshold
            ]
            
            # Sort by mastery (strongest first)
            strong_topics.sort(key=lambda x: x["mastery"], reverse=True)
            
            logger.info(f"📈 Found {len(strong_topics)} strong topics for user")
            return strong_topics
            
        except Exception as e:
            logger.error(f"❌ Failed to get strong topics: {e}")
            return []
    
    def _get_mastery_bucket(self, mastery: int) -> str:
        """Categorize mastery into buckets"""
        if mastery < 30:
            return "beginner"
        elif mastery < 70:
            return "intermediate"
        else:
            return "advanced"
    
    def _extract_concepts(
        self,
        question: str,
        response: Dict[str, Any]
    ) -> List[str]:
        """Extract concepts from question and response"""
        concepts = []
        text = (question + " " + str(response.get('response', {}).get('default_view', {}).get('main_content', {}).get('content', ''))).lower()
        
        # Physics
        concept_patterns = {
            "newton_laws_motion": [r"newton.*law", r"न्यूटन.*नियम"],
            "force_mechanics": [r"\bforce\b", r"बल"],
            "kinematics": [r"velocity", r"acceleration", r"motion"],
            "work_energy": [r"work.*energy", r"कार्य.*ऊर्जा"],
            
            # Calculus
            "calculus_derivatives": [r"derivative", r"differentiation", r"अवकलन"],
            "calculus_integrals": [r"integral", r"integration", r"समाकलन"],
            "fundamental_theorem_calculus": [r"fundamental theorem.*calculus", r"ftc"],
            "limits": [r"limit\b", r"सीमा"],
            
            # Algebra
            "quadratic_equations": [r"quadratic", r"वर्ग समीकरण"],
            "polynomials": [r"polynomial", r"बहुपद"],
            
            # Chemistry
            "acids_bases": [r"acid.*base", r"अम्ल"],
            "organic_chemistry": [r"organic.*chemistry", r"कार्बनिक"],
            "chemical_reactions": [r"chemical.*reaction", r"रासायनिक"]
        }
        
        for concept, patterns in concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    concepts.append(concept)
                    break  # Don't add same concept multiple times
        
        # Default fallback
        if not concepts:
            concepts.append("general_concept")
        
        return list(set(concepts))  # Unique concepts
    
    def _detect_metaphor_preference(self, response: Dict[str, Any]) -> Optional[str]:
        """Detect metaphor style from response"""
        response_text = str(response.get('response', {}).get('default_view', {}).get('metaphor', {}).get('text', '')).lower()
        
        metaphors = {
            "cricket": ["cricket", "bowler", "bat", "ball", "pitch", "wicket"],
            "cooking": ["cooking", "recipe", "ingredient", "kitchen", "chef"],
            "gaming": ["game", "player", "level", "score", "challenge"],
            "bollywood": ["movie", "film", "scene", "actor", "director"],
            "metro": ["metro", "station", "train", "platform", "commute"]
        }
        
        for metaphor_type, keywords in metaphors.items():
            if any(keyword in response_text for keyword in keywords):
                return metaphor_type
        
        return None
    
    def _is_advanced_question(self, question: str) -> bool:
        """Check if question indicates advanced level"""
        advanced_indicators = [
            "prove", "derive", "proof", "derivation",
            "why does", "how come", "exception",
            "edge case", "when does not work",
            "compare", "contrast", "relationship",
            "implications", "applications"
        ]
        
        q_lower = question.lower()
        return any(indicator in q_lower for indicator in advanced_indicators)

