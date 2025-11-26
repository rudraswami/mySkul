"""
Memory Integration Service - Complete Memory System Orchestration
Integrates all memory components for seamless AI Tutor experience

This service orchestrates:
- Short-term context (MemoryService)
- Long-term memory (SemanticMemoryService)  
- Mastery tracking (MasteryTracker)
- Topic continuity (ContinuityEngine)
- Spaced repetition (SpacedRepetitionEngine)
- Memory extraction (MemoryExtractor)
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MemoryIntegrationService:
    """
    Unified memory service that orchestrates all memory components
    
    Usage:
        memory = MemoryIntegrationService(db)
        
        # Before AI response
        context = await memory.get_enhanced_context(user_id, session_id, question)
        
        # After AI response
        await memory.process_interaction(user_id, session_id, question, response)
    """
    
    def __init__(self, db, openai_api_key: str = None):
        self.db = db
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize components lazily
        self._memory_service = None
        self._semantic_memory = None
        self._mastery_tracker = None
        self._continuity_engine = None
        self._spaced_repetition = None
        self._memory_extractor = None
    
    @property
    def memory_service(self):
        if not self._memory_service:
            from services.memory_service import MemoryService
            self._memory_service = MemoryService(self.db)
        return self._memory_service
    
    @property
    def semantic_memory(self):
        if not self._semantic_memory:
            from services.semantic_memory import SemanticMemoryService
            self._semantic_memory = SemanticMemoryService(self.db, self.openai_api_key)
        return self._semantic_memory
    
    @property
    def mastery_tracker(self):
        if not self._mastery_tracker:
            from services.mastery_tracker import MasteryTracker
            self._mastery_tracker = MasteryTracker(self.db)
        return self._mastery_tracker
    
    @property
    def continuity_engine(self):
        if not self._continuity_engine:
            from services.continuity_engine import ContinuityEngine
            self._continuity_engine = ContinuityEngine(self.db)
        return self._continuity_engine
    
    @property
    def spaced_repetition(self):
        if not self._spaced_repetition:
            from services.spaced_repetition import SpacedRepetitionEngine
            self._spaced_repetition = SpacedRepetitionEngine(self.db)
        return self._spaced_repetition
    
    @property
    def memory_extractor(self):
        if not self._memory_extractor:
            from services.memory_extraction import MemoryExtractor
            self._memory_extractor = MemoryExtractor(self.db)
        return self._memory_extractor
    
    async def get_enhanced_context(
        self,
        user_id: str,
        session_id: str,
        question: str,
        subject: str = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for AI response generation
        
        This method retrieves:
        1. Recent conversation context (last 5-10 messages)
        2. Relevant long-term memories
        3. Current mastery level for detected topic
        4. Topic continuation info
        5. User preferences
        
        Args:
            user_id: Student user ID
            session_id: Current chat session
            question: Current question
            subject: Subject (optional, will be detected)
        
        Returns:
            Dict with all context needed for personalized response
        """
        try:
            context = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # 1. Get recent conversation context
            recent_messages = await self.memory_service.get_conversation_context(
                session_id=session_id,
                user_id=user_id,
                window_size=5
            )
            context["recent_context"] = recent_messages
            context["has_prior_context"] = len(recent_messages) > 0
            
            # 2. Get relevant long-term memories
            relevant_memories = await self.semantic_memory.search_relevant_memories(
                user_id=user_id,
                query=question,
                top_k=3,
                min_similarity=0.4
            )
            context["relevant_memories"] = relevant_memories
            
            # 3. Check for topic continuation
            continuity = await self.continuity_engine.detect_topic_continuation(
                user_id=user_id,
                current_query=question
            )
            context["continuity"] = continuity
            context["is_continuation"] = continuity.get("is_continuation", False)
            
            # 4. Extract current topic and get mastery
            current_topic = self._extract_main_topic(question)
            context["current_topic"] = current_topic
            
            mastery_level = await self.mastery_tracker.get_mastery_level(
                user_id=user_id,
                topic=current_topic
            )
            context["mastery_level"] = mastery_level
            context["mastery_bucket"] = self._get_mastery_bucket(mastery_level)
            
            # 5. Get user preferences
            user_profile = await self._get_user_profile(user_id)
            context["preferences"] = user_profile.get("preferences", {})
            context["user_name"] = user_profile.get("name", "")
            
            # 6. Get weak topics for potential recommendations
            weak_topics = await self.mastery_tracker.get_weak_topics(user_id, threshold=40)
            context["weak_topics"] = [t["topic"] for t in weak_topics[:3]]
            
            # 7. Build context summary for AI prompt
            context["context_summary"] = self._build_context_summary(context)
            
            logger.info(f"🧠 Enhanced context retrieved: {len(recent_messages)} recent, "
                       f"{len(relevant_memories)} memories, mastery={mastery_level}")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to get enhanced context: {e}")
            # Return minimal context on error
            return {
                "user_id": user_id,
                "session_id": session_id,
                "recent_context": [],
                "relevant_memories": [],
                "mastery_level": 0,
                "error": str(e)
            }
    
    async def process_interaction(
        self,
        user_id: str,
        session_id: str,
        question: str,
        response: Dict[str, Any],
        feedback: str = None,
        message_id: str = None
    ) -> Dict[str, Any]:
        """
        Process completed interaction and update memory system
        
        This method:
        1. Extracts learning facts from interaction
        2. Stores memories with embeddings
        3. Updates mastery levels
        4. Updates concept thread
        5. Schedules spaced repetition reviews
        
        Args:
            user_id: Student user ID
            session_id: Current chat session
            question: Student's question
            response: AI response data
            feedback: Optional feedback ("helpful", "not_helpful")
            message_id: Optional message ID
        
        Returns:
            Dict with update summary
        """
        try:
            results = {
                "facts_extracted": 0,
                "memories_stored": 0,
                "mastery_updates": [],
                "reviews_scheduled": 0
            }
            
            # 1. Extract learning facts
            facts = await self.memory_extractor.extract_learning_facts(
                user_id=user_id,
                question=question,
                response=response,
                session_id=session_id,
                message_id=message_id
            )
            results["facts_extracted"] = len(facts)
            
            # 2. Process each fact
            for fact in facts:
                fact_type = fact.get("fact_type")
                
                if fact_type == "concept_learned":
                    # Store with embedding for semantic search
                    fact_id = await self.semantic_memory.store_memory_with_embedding(
                        user_id=user_id,
                        content=fact.get("content", ""),
                        metadata=fact
                    )
                    
                    if fact_id:
                        results["memories_stored"] += 1
                        
                        # Schedule first review
                        review_schedule = self.spaced_repetition.calculate_next_review(
                            current_interval_days=0,
                            quality=3,  # Default: understood
                            current_easiness=2.5
                        )
                        
                        # Update review schedule
                        await self.db.user_memory_facts.update_one(
                            {"fact_id": fact_id},
                            {"$set": {
                                "next_review_at": review_schedule["next_review_at"],
                                "review_interval_days": review_schedule["interval_days"],
                                "easiness_factor": review_schedule["easiness_factor"]
                            }}
                        )
                        results["reviews_scheduled"] += 1
                
                elif fact_type == "mastery_update":
                    # Update mastery level
                    topic = fact.get("topic", "general")
                    delta = fact.get("mastery_delta", 5)
                    reason = fact.get("reason", "question_answered")
                    
                    await self.mastery_tracker.update_mastery(
                        user_id=user_id,
                        topic=topic,
                        delta=delta,
                        reason=reason
                    )
                    results["mastery_updates"].append({
                        "topic": topic,
                        "delta": delta
                    })
                
                elif fact_type == "preference":
                    # Update user preferences
                    await self._update_user_preference(
                        user_id=user_id,
                        preference_type=fact.get("topic"),
                        value=fact.get("metadata", {})
                    )
            
            # 3. Update concept thread
            concepts = self._extract_concepts_from_text(question + " " + str(response))
            current_topic = self._extract_main_topic(question)
            
            if concepts:
                await self.continuity_engine.update_concept_thread(
                    user_id=user_id,
                    topic=current_topic,
                    concepts=concepts
                )
            
            # 4. Update stats
            await self._increment_question_count(user_id)
            
            # 5. Handle explicit feedback
            if feedback:
                await self._process_feedback(
                    user_id=user_id,
                    question=question,
                    response=response,
                    feedback=feedback
                )
            
            logger.info(f"💾 Interaction processed: {results['facts_extracted']} facts, "
                       f"{results['memories_stored']} stored, "
                       f"{len(results['mastery_updates'])} mastery updates")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to process interaction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    async def get_personalization_context(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get personalization context for response generation
        
        Returns user preferences, learning style, and patterns
        """
        try:
            profile = await self._get_user_profile(user_id)
            
            return {
                "name": profile.get("name", ""),
                "preferred_metaphor": profile.get("preferences", {}).get("metaphor_style", "cricket"),
                "explanation_depth": profile.get("preferences", {}).get("explanation_depth", "medium"),
                "visual_learner": profile.get("preferences", {}).get("visual_learner", True),
                "language_preference": profile.get("preferences", {}).get("preferred_language", "hinglish"),
                "learns_better_with": profile.get("patterns", {}).get("learns_better_with", "examples"),
                "level": profile.get("stats", {}).get("level", 1),
                "streak": profile.get("stats", {}).get("current_streak_days", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get personalization context: {e}")
            return {}
    
    async def get_due_reviews(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get concepts due for spaced repetition review"""
        return await self.continuity_engine.get_due_reviews(user_id, limit)
    
    # ==================== Private Helpers ====================
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get or create user learning profile"""
        try:
            # Try to get from learning profile
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if profile:
                # Get user name from users collection
                user = await self.db.users.find_one({"user_id": user_id})
                if user:
                    full_name = user.get("full_name", "")
                    profile["name"] = full_name.split()[0] if full_name else ""
                return profile
            
            # Create default profile
            default_profile = {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "mastery_levels": {},
                "preferences": {
                    "metaphor_style": "cricket",
                    "backup_metaphors": ["cooking", "gaming"],
                    "explanation_depth": "medium",
                    "preferred_language": "hinglish",
                    "visual_learner": True
                },
                "patterns": {
                    "best_time_of_day": "evening",
                    "avg_session_length_mins": 25,
                    "preferred_difficulty": "medium",
                    "learns_better_with": "examples"
                },
                "stats": {
                    "total_questions": 0,
                    "current_streak_days": 0,
                    "longest_streak_days": 0,
                    "total_xp": 0,
                    "level": 1,
                    "accuracy_overall": 0.0
                },
                "last_active_topic": None,
                "last_active_concept_thread": [],
                "incomplete_concepts": [],
                "mastery_history": []
            }
            
            await self.db.user_learning_profile.insert_one(default_profile)
            
            # Get user name
            user = await self.db.users.find_one({"user_id": user_id})
            if user:
                full_name = user.get("full_name", "")
                default_profile["name"] = full_name.split()[0] if full_name else ""
            
            return default_profile
            
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {e}")
            return {}
    
    async def _update_user_preference(
        self,
        user_id: str,
        preference_type: str,
        value: Any
    ):
        """Update a user preference"""
        try:
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"preferences.{preference_type}": value,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to update preference: {e}")
    
    async def _increment_question_count(self, user_id: str):
        """Increment total questions asked"""
        try:
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"stats.total_questions": 1},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to increment question count: {e}")
    
    async def _process_feedback(
        self,
        user_id: str,
        question: str,
        response: Dict[str, Any],
        feedback: str
    ):
        """Process explicit user feedback"""
        try:
            # Map feedback to quality score
            quality = self.spaced_repetition.infer_quality_from_feedback(feedback)
            
            # Extract topic
            topic = self._extract_main_topic(question)
            
            # Update mastery based on feedback
            delta = 10 if feedback == "helpful" else -5 if feedback == "not_helpful" else 0
            
            if delta != 0:
                await self.mastery_tracker.update_mastery(
                    user_id=user_id,
                    topic=topic,
                    delta=delta,
                    reason=f"feedback_{feedback}"
                )
            
            logger.info(f"📝 Processed feedback: {feedback} for {topic}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process feedback: {e}")
    
    def _extract_main_topic(self, text: str) -> str:
        """Extract main topic from text"""
        text_lower = text.lower()
        
        # Physics
        if "newton" in text_lower and "law" in text_lower:
            return "newton_laws_motion"
        if "force" in text_lower:
            return "force_mechanics"
        if "velocity" in text_lower or "acceleration" in text_lower:
            return "kinematics"
        
        # Calculus
        if "derivative" in text_lower or "differentiation" in text_lower:
            return "calculus_derivatives"
        if "integral" in text_lower or "integration" in text_lower:
            return "calculus_integrals"
        if "limit" in text_lower:
            return "limits_calculus"
        
        # Algebra
        if "quadratic" in text_lower:
            return "quadratic_equations"
        if "polynomial" in text_lower:
            return "polynomials"
        
        # Chemistry
        if "acid" in text_lower or "base" in text_lower:
            return "acids_bases"
        if "organic" in text_lower:
            return "organic_chemistry"
        
        return "general_concept"
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """Extract all concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        concept_keywords = {
            "derivatives": ["derivative", "differentiation", "d/dx"],
            "integrals": ["integral", "integration", "∫"],
            "limits": ["limit", "lim"],
            "newton_laws": ["newton", "f=ma"],
            "force": ["force", "newton"],
            "kinematics": ["velocity", "acceleration", "motion"],
            "quadratic": ["quadratic", "x²"],
            "acids_bases": ["acid", "base", "ph"],
        }
        
        for concept, keywords in concept_keywords.items():
            if any(kw in text_lower for kw in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _get_mastery_bucket(self, mastery: int) -> str:
        """Get mastery bucket from level"""
        if mastery < 30:
            return "beginner"
        elif mastery < 70:
            return "intermediate"
        else:
            return "advanced"
    
    def _build_context_summary(self, context: Dict[str, Any]) -> str:
        """Build human-readable context summary for AI prompt"""
        parts = []
        
        # User name
        if context.get("user_name"):
            parts.append(f"Student: {context['user_name']}")
        
        # Mastery level
        mastery = context.get("mastery_level", 0)
        bucket = context.get("mastery_bucket", "beginner")
        parts.append(f"Mastery: {mastery}/100 ({bucket})")
        
        # Continuation
        if context.get("is_continuation"):
            last_topic = context.get("continuity", {}).get("last_topic", "")
            if last_topic:
                parts.append(f"Continuing from: {last_topic.replace('_', ' ')}")
        
        # Relevant memories
        memories = context.get("relevant_memories", [])
        if memories:
            topics = [m.get("topic", "") for m in memories[:2]]
            parts.append(f"Related topics: {', '.join(topics)}")
        
        # Weak topics
        weak = context.get("weak_topics", [])
        if weak:
            parts.append(f"Needs practice: {', '.join(weak[:2])}")
        
        return " | ".join(parts)


# Convenience function for easy import
async def get_memory_integration(db, openai_api_key: str = None) -> MemoryIntegrationService:
    """Factory function to create MemoryIntegrationService"""
    return MemoryIntegrationService(db, openai_api_key)

