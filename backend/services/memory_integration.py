"""
Memory Integration Service - Complete Memory System Orchestration (MEMORY v2)
=============================================================================

Integrates all memory components for seamless AI Tutor experience.

MEMORY v2 ADDITIONS:
- Persistent session state (survives restarts)
- Selective memory recall (only relevant memories)
- Memory contract compliance (canonical schemas)
- Bounded memory growth
- Multi-tenant isolation

This service orchestrates:
- Short-term context (MemoryService)
- Long-term memory (SemanticMemoryService)  
- Mastery tracking (MasteryTracker)
- Topic continuity (ContinuityEngine)
- Spaced repetition (SpacedRepetitionEngine)
- Memory extraction (MemoryExtractor)
"""
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Debug flag
MEMORY_DEBUG = os.getenv("MEMORY_DEBUG", "false").lower() == "true"


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
        
        # FIX #12: Deduplication cache for memory writes
        # Prevents same interaction from being written multiple times
        self._recent_write_keys: Dict[str, float] = {}  # {key: timestamp}
        self._dedup_window_seconds = 5  # Ignore duplicate writes within 5 seconds
        self._max_dedup_cache_size = 100
    
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
        6. Formatted conversation summary for AI prompt
        
        Args:
            user_id: Student user ID
            session_id: Current chat session
            question: Current question
            subject: Subject (optional, will be detected)
        
        Returns:
            Dict with all context needed for personalized response
        
        OPTIMIZED: Parallel execution of independent async calls to reduce latency.
        """
        try:
            context = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Extract current topic early (sync operation)
            current_topic = self._extract_main_topic(question)
            context["current_topic"] = current_topic
            
            # ================================================================
            # PARALLEL EXECUTION: Run independent async calls concurrently
            # This reduces total time from ~sum(all_calls) to ~max(slowest_call)
            # FIX #4: Track failures for visibility (not silent degradation)
            # ================================================================
            memory_errors = []  # FIX #4: Track all component failures
            
            async def safe_get_conversation():
                try:
                    return await self.memory_service.get_conversation_context(
                        session_id=session_id,
                        user_id=user_id,
                        window_size=10
                    )
                except asyncio.CancelledError:
                    # Re-raise CancelledError to let gather handle it properly
                    raise
                except Exception as e:
                    memory_errors.append(("conversation_context", str(e)))
                    logger.warning(f"Conversation context fetch failed: {e}")
                    return []
            
            async def safe_search_memories():
                try:
                    return await self.semantic_memory.search_relevant_memories(
                        user_id=user_id,
                        query=question,
                        top_k=3,
                        min_similarity=0.4
                    )
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    memory_errors.append(("semantic_memory", str(e)))
                    logger.warning(f"Semantic memory search failed: {e}")
                    return []
            
            async def safe_detect_continuation():
                try:
                    return await self.continuity_engine.detect_topic_continuation(
                        user_id=user_id,
                        current_query=question
                    )
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    memory_errors.append(("continuity", str(e)))
                    logger.warning(f"Continuity detection failed: {e}")
                    return {}
            
            async def safe_get_mastery():
                try:
                    return await self.mastery_tracker.get_mastery_level(
                        user_id=user_id,
                        topic=current_topic
                    )
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    memory_errors.append(("mastery", str(e)))
                    logger.warning(f"Mastery fetch failed: {e}")
                    return 0
            
            async def safe_get_profile():
                try:
                    return await self._get_user_profile(user_id)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    memory_errors.append(("profile", str(e)))
                    logger.warning(f"User profile fetch failed: {e}")
                    return {}
            
            async def safe_get_weak_topics():
                try:
                    return await self.mastery_tracker.get_weak_topics(user_id, threshold=40)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    memory_errors.append(("weak_topics", str(e)))
                    logger.warning(f"Weak topics fetch failed: {e}")
                    return []
            
            # Run all in parallel with timeout protection
            # FIX: Added 3s timeout to prevent slow semantic search from blocking
            # FIX: Use return_exceptions=True to prevent "_GatheringFuture never retrieved" error
            # When gather is cancelled, individual task exceptions must be retrieved
            try:
                raw_results = await asyncio.wait_for(
                    asyncio.gather(
                        safe_get_conversation(),
                        safe_search_memories(),
                        safe_detect_continuation(),
                        safe_get_mastery(),
                        safe_get_profile(),
                        safe_get_weak_topics(),
                        return_exceptions=True  # FIX: Capture exceptions as results to prevent unretrieved futures
                    ),
                    timeout=3.0  # Aggressive 3s timeout for all memory operations
                )
                
                # FIX: Process results - replace any exceptions with default values
                defaults = ([], [], {}, 0, {}, [])
                results = []
                for i, result in enumerate(raw_results):
                    if isinstance(result, Exception):
                        # Log the exception but use default
                        if not isinstance(result, asyncio.CancelledError):
                            memory_errors.append((f"component_{i}", str(result)))
                        results.append(defaults[i])
                    else:
                        results.append(result)
                results = tuple(results)
                
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Memory parallel gather timed out (>3s), using defaults")
                # Return empty results for all components
                results = ([], [], {}, 0, {}, [])
            except asyncio.CancelledError:
                # Streaming client disconnected - graceful degradation, not crash
                logger.info("Memory load cancelled (client disconnect), using defaults")
                results = ([], [], {}, 0, {}, [])
            
            # Unpack results
            recent_messages, relevant_memories, continuity, mastery_level, user_profile, weak_topics = results
            
            # FIX #4: Track component health in context for visibility
            if memory_errors:
                context["_memory_degraded"] = True
                context["_memory_errors"] = memory_errors
                context["_components_failed"] = len(memory_errors)
                logger.warning(f"⚠️ Memory partially degraded: {len(memory_errors)}/6 components failed: {[e[0] for e in memory_errors]}")
            else:
                context["_memory_degraded"] = False
            
            # 1. Recent conversation context
            context["recent_context"] = recent_messages
            context["has_prior_context"] = len(recent_messages) > 0
            
            # Build conversation summary for AI prompt
            if recent_messages:
                context["conversation_summary"] = self._build_conversation_summary(recent_messages)
            else:
                context["conversation_summary"] = ""
            
            # 2. Relevant long-term memories
            context["relevant_memories"] = relevant_memories
            
            # 3. Topic continuation
            context["continuity"] = continuity
            context["is_continuation"] = continuity.get("is_continuation", False)
            
            # FIX: Ensure previous_topic is set for downstream use (context_pack)
            if continuity.get("last_topic"):
                context["continuity"]["previous_topic"] = continuity["last_topic"]
            
            # 4. Mastery level
            context["mastery_level"] = mastery_level
            context["mastery_bucket"] = self._get_mastery_bucket(mastery_level)
            
            # 5. User preferences
            context["preferences"] = user_profile.get("preferences", {})
            context["user_name"] = user_profile.get("name", "")
            
            # 6. Weak topics
            context["weak_topics"] = [t["topic"] for t in weak_topics[:3]]
            
            # 7. Build context summary for AI prompt
            context["context_summary"] = self._build_context_summary(context)
            
            logger.info(f"🧠 Enhanced context (parallel): {len(recent_messages)} recent, "
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
            
            if profile is not None:
                # Get user name from users collection
                user = await self.db.users.find_one({"user_id": user_id})
                if user is not None:
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
            
            # FIX: Wrap insert in try-except to handle cancellation during insert
            try:
                await self.db.user_learning_profile.insert_one(default_profile)
            except asyncio.CancelledError:
                # Don't let profile insert cancellation orphan the future
                # Just log and return the default profile (not persisted)
                logger.info("Profile insert cancelled (client disconnect)")
                return default_profile
            
            # Get user name
            user = await self.db.users.find_one({"user_id": user_id})
            if user is not None:
                full_name = user.get("full_name", "")
                default_profile["name"] = full_name.split()[0] if full_name else ""
            
            return default_profile
            
        except asyncio.CancelledError:
            # Re-raise CancelledError - don't swallow it
            raise
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
    
    def _build_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Build formatted conversation summary from recent messages
        
        Args:
            messages: List of recent messages
        
        Returns:
            Formatted string of conversation history for AI prompt
        """
        if not messages:
            return ""
        
        summary_parts = []
        for msg in messages[-5:]:  # Last 5 messages only
            # Defensive: skip if msg is not a dict (bad data)
            if not isinstance(msg, dict):
                continue
            
            user_msg = msg.get("user_message", "")
            ai_response = msg.get("ai_response", {})
            
            if user_msg:
                # Extract question topic (for internal context, NOT shown to user)
                # Use neutral format that won't look like debug dump if leaked
                question_brief = user_msg[:80].strip()
                summary_parts.append(f"Q: {question_brief}")
                
                # Extract key points from AI response - DEFENSIVE chained .get()
                if isinstance(ai_response, dict):
                    response_text = ""
                    try:
                        resp_obj = ai_response.get("response", {})
                        if isinstance(resp_obj, dict):
                            default_view = resp_obj.get("default_view", {})
                            if isinstance(default_view, dict):
                                main_content = default_view.get("main_content", {})
                                if isinstance(main_content, dict):
                                    response_text = str(main_content.get("content", ""))
                    except (AttributeError, TypeError):
                        response_text = ""
                    
                    if response_text:
                        # Get first 100 chars as summary (clean format)
                        answer_brief = response_text[:100].strip()
                        summary_parts.append(f"A: {answer_brief}...")
        
        if not summary_parts:
            return ""
        
        return "\n".join(summary_parts)
    
    # =========================================================================
    # MEMORY v2 - SELECTIVE RECALL (Intelligent Read)
    # =========================================================================
    
    async def get_memory_context_pack(
        self,
        user_id: str,
        session_id: str,
        query: str,
        route_type: str = "educational",
        agent_name: str = None
    ) -> Dict[str, Any]:
        """
        Build a COMPACT MemoryContextPack for agent consumption.
        
        SELECTIVE RECALL: Only retrieves memory RELEVANT to the current query.
        Does NOT dump all memory - keeps prompts lean.
        
        MEMORY CONTRACT: Returns MemoryContextPack schema fields.
        MULTI-TENANT: Isolated by user_id.
        
        Args:
            user_id: User ID (for isolation)
            session_id: Current session
            query: Current user query (for relevance)
            route_type: Routing type (affects recall strategy)
            agent_name: Target agent (for agent-specific recall)
        
        Returns:
            Dict matching MemoryContextPack schema
            
        FIX #11: Partial failure handling - keeps successful data, doesn't wipe everything
        """
        # FIX #11: Start with default pack (always returned, even on failures)
        pack = {
            "user_id": user_id,
            "session_id": session_id,
            "student_name": "",
            "exam_target": None,
            "current_mastery": 0,
            "mastery_bucket": "beginner",
            "relevant_memories": [],
            "session_summary": "",
            "active_task": None,
            "last_topic": None,
            "preferred_explanation": "step_by_step",
            "pacing": "normal",
            "is_weak_area": False,
            "needs_encouragement": False,
            "_partial_failure": False,  # FIX #11: Track if any component failed
            "_failed_components": []    # FIX #11: List of failed components
        }
        
        # FIX #11: Each component wrapped individually - failures don't cascade
        
        # 1. Get session state (persistent)
        try:
            session_state = await self.memory_service.get_session_state(user_id, session_id)
            pack["session_summary"] = session_state.get("session_summary", "")
            pack["active_task"] = session_state.get("active_task")
            pack["last_topic"] = session_state.get("last_retrieval_topics", [None])[0] if session_state.get("last_retrieval_topics") else None
        except asyncio.CancelledError:
            # Client disconnected - return partial pack
            logger.info("MemoryContextPack: session_state cancelled (client disconnect)")
            return pack
        except Exception as e:
            pack["_partial_failure"] = True
            pack["_failed_components"].append("session_state")
            logger.warning(f"⚠️ MemoryContextPack: session_state failed: {e}")
        
        # 2. Get student profile (persistent)
        profile = {}
        try:
            profile = await self.memory_service.get_student_profile(user_id)
            pack["exam_target"] = profile.get("exam_target")
            pack["preferred_explanation"] = profile.get("preferred_explanation", "step_by_step")
            pack["pacing"] = profile.get("pacing", "normal")
        except asyncio.CancelledError:
            logger.info("MemoryContextPack: student_profile cancelled (client disconnect)")
            return pack
        except Exception as e:
            pack["_partial_failure"] = True
            pack["_failed_components"].append("student_profile")
            logger.warning(f"⚠️ MemoryContextPack: student_profile failed: {e}")
        
        # Get student name
        try:
            user_doc = await self.db.users.find_one({"user_id": user_id})
            if user_doc is not None:
                full_name = user_doc.get("full_name", "")
                pack["student_name"] = full_name.split()[0] if full_name else ""
        except asyncio.CancelledError:
            # Client disconnected - don't crash, use default
            pass
        except Exception as e:
            pack["_partial_failure"] = True
            pack["_failed_components"].append("student_name")
            logger.debug(f"Student name fetch failed: {e}")
        
        # 3. Get mastery for current topic
        try:
            topic = self._extract_main_topic(query)
            if topic:
                topic_key = topic.lower().replace(" ", "_")
                mastery_data = profile.get("mastery_by_topic", {}).get(topic_key, {})
                mastery_score = mastery_data.get("mastery_score", 0.0) if isinstance(mastery_data, dict) else 0.0
                pack["current_mastery"] = int(mastery_score * 100)
                pack["mastery_bucket"] = self._get_mastery_bucket(pack["current_mastery"])
                
                # Check if weak area
                weak_topics = profile.get("weak_topics", [])
                pack["is_weak_area"] = topic_key in [t.lower().replace(" ", "_") for t in weak_topics]
        except asyncio.CancelledError:
            logger.info("MemoryContextPack: mastery cancelled (client disconnect)")
            return pack
        except Exception as e:
            pack["_partial_failure"] = True
            pack["_failed_components"].append("mastery")
            logger.warning(f"⚠️ MemoryContextPack: mastery failed: {e}")
        
        # 4. SELECTIVE RECALL - Only relevant memories (max 5)
        try:
            if route_type in ["educational", "problem_solving", "concept"]:
                relevant_memories = await self.semantic_memory.search_relevant_memories(
                    user_id=user_id,
                    query=query,
                    top_k=5,
                    min_similarity=0.4
                )
                
                # Compact the memories (only essential fields)
                pack["relevant_memories"] = [
                    {
                        "content": m.get("content", "")[:200],
                        "topic": m.get("topic", ""),
                        "similarity": m.get("similarity_score", 0)
                    }
                    for m in relevant_memories[:5]
                    if isinstance(m, dict)
                ]
        except asyncio.CancelledError:
            logger.info("MemoryContextPack: semantic_memory cancelled (client disconnect)")
            return pack
        except Exception as e:
            pack["_partial_failure"] = True
            pack["_failed_components"].append("semantic_memory")
            logger.warning(f"⚠️ MemoryContextPack: semantic_memory failed: {e}")
        
        # 5. Check if needs encouragement
        if pack["is_weak_area"] or pack["current_mastery"] < 30:
            pack["needs_encouragement"] = True
        
        # FIX #11: Log degradation if any components failed
        if pack["_partial_failure"]:
            logger.warning(f"⚠️ MemoryContextPack partially degraded: {pack['_failed_components']}")
        
        if MEMORY_DEBUG:
            logger.info(f"📦 MemoryContextPack built: user={user_id[:8]}, "
                       f"mastery={pack['current_mastery']}%, memories={len(pack['relevant_memories'])}, "
                       f"degraded={pack['_partial_failure']}")
        
        return pack
    
    # =========================================================================
    # MEMORY v2 - INTELLIGENT WRITE (Memory Update Policy)
    # =========================================================================
    
    async def write_memory_after_response(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: str,
        agent_name: str = None,
        topics: List[str] = None,
        mastery_delta: float = None,
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Intelligently update memory after a response.
        
        MEMORY WRITE POLICY:
        - At most 1 session_summary update (only if meaningfully changed)
        - Mastery updates only when user confirms understanding
        - Turn always added to session state
        - Memory event logged for audit
        
        DOES NOT:
        - Store raw long user text (summaries only)
        - Update every interaction (selective)
        - Overwrite full documents (diff updates)
        
        Args:
            user_id: User ID
            session_id: Session ID
            user_message: User's message
            ai_response: AI response text
            agent_name: Agent that handled the response
            topics: Topics discussed
            mastery_delta: Mastery change (if any)
            request_id: Request correlation ID
        
        Returns:
            Dict with update summary
        """
        # FIX #12: Deduplication check
        import time
        dedup_key = f"{user_id}:{session_id}:{request_id or user_message[:50]}"
        current_time = time.time()
        
        # Clean old entries from dedup cache
        if len(self._recent_write_keys) > self._max_dedup_cache_size:
            cutoff = current_time - self._dedup_window_seconds
            self._recent_write_keys = {
                k: v for k, v in self._recent_write_keys.items()
                if v > cutoff
            }
        
        # Check for duplicate
        if dedup_key in self._recent_write_keys:
            last_write = self._recent_write_keys[dedup_key]
            if current_time - last_write < self._dedup_window_seconds:
                logger.debug(f"🔄 Deduplicated memory write: {dedup_key[:30]}...")
                return {
                    "turn_added": False,
                    "summary_updated": False,
                    "mastery_updated": False,
                    "event_logged": False,
                    "errors": [],
                    "retries": 0,
                    "deduplicated": True  # FIX #12: Mark as deduplicated
                }
        
        # Record this write
        self._recent_write_keys[dedup_key] = current_time
        
        results = {
            "turn_added": False,
            "summary_updated": False,
            "mastery_updated": False,
            "event_logged": False,
            "errors": [],
            "retries": 0,  # FIX #7: Track retry attempts
            "deduplicated": False  # FIX #12: Not a duplicate
        }
        
        try:
            # FIX #7: Add retry logic for turn addition (critical operation)
            # 1. Always add turn to session state (bounded) - WITH RETRY
            turn_success = False
            max_retries = 2
            
            for attempt in range(max_retries + 1):
                try:
                    turn_success = await self.memory_service.update_session_turn(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=user_message,
                        ai_response=ai_response,
                        agent_name=agent_name,
                        topics=topics
                    )
                    if turn_success:
                        break
                except Exception as turn_err:
                    results["retries"] += 1
                    if attempt < max_retries:
                        await asyncio.sleep(0.1 * (attempt + 1))  # Backoff
                        logger.warning(f"⚠️ Turn update retry {attempt + 1}/{max_retries}: {turn_err}")
                    else:
                        results["errors"].append(f"turn_update: {str(turn_err)}")
                        logger.error(f"❌ Turn update failed after {max_retries + 1} attempts: {turn_err}")
            
            results["turn_added"] = turn_success
            
            # 2. Update session summary if enough turns accumulated
            session_state = await self.memory_service.get_session_state(user_id, session_id)
            # Defensive: ensure session_state is a dict
            if not isinstance(session_state, dict):
                session_state = {}
            turns = session_state.get("last_turns", [])
            
            if len(turns) >= 3 and len(turns) % 3 == 0:  # Every 3 turns
                new_summary = self._generate_session_summary(turns)
                if new_summary:
                    summary_success = await self.memory_service.update_session_summary(
                        user_id=user_id,
                        session_id=session_id,
                        summary=new_summary
                    )
                    results["summary_updated"] = summary_success
            
            # 3. Update mastery if delta provided (user confirmed understanding)
            if mastery_delta and topics:
                for topic in topics[:3]:  # Max 3 topics
                    await self.memory_service.update_topic_mastery(
                        user_id=user_id,
                        topic=topic,
                        mastery_delta=mastery_delta
                    )
                results["mastery_updated"] = True
            
            # 4. Log memory event (audit trail)
            event_success = await self.memory_service.log_memory_event(
                user_id=user_id,
                session_id=session_id,
                event_type="topic_focus",
                payload={
                    "topics": topics or [],
                    "agent": agent_name,
                    "mastery_delta": mastery_delta
                },
                source_agent=agent_name,
                request_id=request_id
            )
            results["event_logged"] = event_success
            
            if MEMORY_DEBUG:
                logger.info(f"💾 Memory written: turn={results['turn_added']}, "
                           f"summary={results['summary_updated']}, mastery={results['mastery_updated']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to write memory: {e}")
            results["errors"].append(str(e))
            return results
    
    def _generate_session_summary(self, turns: List[Dict[str, Any]]) -> str:
        """Generate a bounded session summary from turns."""
        if not turns:
            return ""
        
        # Extract key topics and questions
        topics = set()
        questions = []
        
        for turn in turns[-5:]:  # Last 5 turns only
            # Defensive: skip if turn is not a dict (bad data)
            if not isinstance(turn, dict):
                continue
            
            user_msg = turn.get("user", "")
            if user_msg:
                questions.append(user_msg[:80])
            
            turn_topics = turn.get("topics", [])
            # Defensive: ensure turn_topics is iterable
            if isinstance(turn_topics, list):
                topics.update(turn_topics)
        
        # Build summary
        parts = []
        if topics:
            parts.append(f"Topics: {', '.join(list(topics)[:5])}")
        if questions:
            parts.append(f"Discussed: {'; '.join(questions[:3])}")
        
        summary = " | ".join(parts)
        return summary[:800]  # Enforce bound


# Convenience function for easy import
async def get_memory_integration(db, openai_api_key: str = None) -> MemoryIntegrationService:
    """Factory function to create MemoryIntegrationService"""
    return MemoryIntegrationService(db, openai_api_key)

