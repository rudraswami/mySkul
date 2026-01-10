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

CONCURRENCY FIX (2026-01-11):
- Added asyncio.Lock to _profile_cache and _recent_write_keys
- Made cache operations atomic and thread-safe
- Replaced shallow copies with copy.deepcopy
"""
import asyncio
import copy
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
        # CONCURRENCY FIX: Lock for dedup cache
        self._dedup_lock = asyncio.Lock()
        
        # OPTIMIZATION: Micro-cache for user_learning_profile (deduplicates 4 queries)
        # TTL is very short (500ms) - only deduplicates within a single request
        self._profile_cache: Dict[str, tuple] = {}  # {user_id: (profile, timestamp)}
        self._profile_cache_ttl_ms = 500  # 500ms - covers one request's parallel operations
        # CONCURRENCY FIX: Lock for profile cache
        self._profile_cache_lock = asyncio.Lock()
        
        # OBSERVABILITY FIX (2026-01-11): Cache metrics
        self._cache_stats = {
            "profile_hits": 0,
            "profile_misses": 0,
            "dedup_hits": 0,
            "dedup_total": 0
        }
        self._cache_stats_lock = asyncio.Lock()
    
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
        subject: str = None,
        request_id: str = None
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
            request_id: Request correlation ID for tracing (OBSERVABILITY FIX)
        
        Returns:
            Dict with all context needed for personalized response
        
        OPTIMIZED: Parallel execution of independent async calls to reduce latency.
        
        OBSERVABILITY FIX (2026-01-11):
        - Added request_id parameter for correlation
        - Tracks per-component latency
        - Logs context_quality metrics
        """
        import time
        import uuid
        
        # Generate request_id if not provided
        if request_id is None:
            request_id = str(uuid.uuid4())[:8]
        
        request_start = time.time()
        
        try:
            context = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "_request_id": request_id  # OBSERVABILITY: Include in context for downstream tracing
            }
            
            # Extract current topic early (sync operation)
            current_topic = self._extract_main_topic(question)
            context["current_topic"] = current_topic
            
            # ================================================================
            # PROGRESSIVE CONTEXT ACCUMULATION (Resilient Architecture)
            # ================================================================
            # Instead of all-or-nothing, we:
            # 1. Give each operation its own individual timeout (fail fast)
            # 2. Collect results as they complete
            # 3. On global timeout, PRESERVE whatever completed
            # 4. Track explicit context quality level
            # ================================================================
            
            # Component definitions with priorities and individual timeouts
            # Priority 0 = CRITICAL (must have for coherent response)
            # Priority 1 = HIGH (needed for personalization)
            # Priority 2 = MEDIUM (enhancement)
            # Priority 3 = LOW (nice to have)
            
            # TIMEOUT ALIGNMENT FIX (2026-01-11):
            # All component timeouts < global deadline (1.5s)
            # Ensures components complete or fail BEFORE global timeout
            # Previous issue: semantic_memory had 1.5s = global deadline (race condition)
            COMPONENT_CONFIG = {
                "conversation": {"timeout": 0.8, "priority": 0, "default": []},   # Reduced from 1.0s
                "profile": {"timeout": 0.6, "priority": 1, "default": {}},        # Reduced from 0.8s
                "mastery": {"timeout": 0.5, "priority": 1, "default": 0},         # Reduced from 0.6s
                "semantic_memory": {"timeout": 1.0, "priority": 2, "default": []},# Reduced from 1.5s
                "weak_topics": {"timeout": 0.5, "priority": 2, "default": []},    # Reduced from 0.6s
                "continuity": {"timeout": 0.6, "priority": 3, "default": {}},     # Reduced from 0.8s
            }
            
            # Track component outcomes
            component_results = {}
            component_status = {}  # "success", "timeout", "error", "cancelled"
            
            # OBSERVABILITY: Track per-component latency
            component_latencies = {}
            
            async def timed_operation(name: str, coro, timeout: float, default):
                """
                Execute operation with individual timeout, return (name, result, status)
                
                OBSERVABILITY FIX (2026-01-11): Tracks latency per component
                """
                start = time.time()
                try:
                    result = await asyncio.wait_for(coro, timeout=timeout)
                    latency_ms = (time.time() - start) * 1000
                    component_latencies[name] = {"latency_ms": latency_ms, "status": "success"}
                    return (name, result, "success")
                except asyncio.TimeoutError:
                    latency_ms = (time.time() - start) * 1000
                    component_latencies[name] = {"latency_ms": latency_ms, "status": "timeout"}
                    logger.debug(f"⏱️ {name} timed out (>{timeout}s) [rid={request_id}]")
                    return (name, default, "timeout")
                except asyncio.CancelledError:
                    latency_ms = (time.time() - start) * 1000
                    component_latencies[name] = {"latency_ms": latency_ms, "status": "cancelled"}
                    return (name, default, "cancelled")
                except Exception as e:
                    latency_ms = (time.time() - start) * 1000
                    component_latencies[name] = {"latency_ms": latency_ms, "status": "error", "error": str(e)[:50]}
                    logger.warning(f"❌ {name} failed: {str(e)[:80]} [rid={request_id}]")
                    return (name, default, "error")
            
            # Create all tasks with individual timeouts
            tasks = [
                asyncio.create_task(
                    timed_operation(
                        "conversation",
                        self.memory_service.get_conversation_context(
                            session_id=session_id,
                            user_id=user_id,
                            window_size=10
                        ),
                        COMPONENT_CONFIG["conversation"]["timeout"],
                        COMPONENT_CONFIG["conversation"]["default"]
                    ),
                    name="conversation"
                ),
                asyncio.create_task(
                    timed_operation(
                        "profile",
                        self._get_user_profile(user_id),
                        COMPONENT_CONFIG["profile"]["timeout"],
                        COMPONENT_CONFIG["profile"]["default"]
                    ),
                    name="profile"
                ),
                asyncio.create_task(
                    timed_operation(
                        "mastery",
                        self.mastery_tracker.get_mastery_level(
                            user_id=user_id,
                            topic=current_topic
                        ),
                        COMPONENT_CONFIG["mastery"]["timeout"],
                        COMPONENT_CONFIG["mastery"]["default"]
                    ),
                    name="mastery"
                ),
                asyncio.create_task(
                    timed_operation(
                        "semantic_memory",
                        self.semantic_memory.search_relevant_memories(
                            user_id=user_id,
                            query=question,
                            top_k=3,
                            min_similarity=0.4
                        ),
                        COMPONENT_CONFIG["semantic_memory"]["timeout"],
                        COMPONENT_CONFIG["semantic_memory"]["default"]
                    ),
                    name="semantic_memory"
                ),
                asyncio.create_task(
                    timed_operation(
                        "weak_topics",
                        self.mastery_tracker.get_weak_topics(user_id, threshold=40),
                        COMPONENT_CONFIG["weak_topics"]["timeout"],
                        COMPONENT_CONFIG["weak_topics"]["default"]
                    ),
                    name="weak_topics"
                ),
                asyncio.create_task(
                    timed_operation(
                        "continuity",
                        self.continuity_engine.detect_topic_continuation(
                            user_id=user_id,
                            current_query=question
                        ),
                        COMPONENT_CONFIG["continuity"]["timeout"],
                        COMPONENT_CONFIG["continuity"]["default"]
                    ),
                    name="continuity"
                ),
            ]
            
            # Global deadline: collect whatever completes within 1.5s
            # Individual timeouts are shorter, so most will complete or fail fast
            # REDUCED from 2.5s to 1.5s to prevent memory from blocking agent startup
            GLOBAL_DEADLINE = 1.5
            
            logger.debug(f"🧠 Starting {len(tasks)} memory tasks with {GLOBAL_DEADLINE}s deadline")
            
            try:
                done, pending = await asyncio.wait(
                    tasks,
                    timeout=GLOBAL_DEADLINE,
                    return_when=asyncio.ALL_COMPLETED
                )
                logger.debug(f"🧠 asyncio.wait completed: {len(done)} done, {len(pending)} pending")
            except asyncio.CancelledError:
                # Client disconnected - cancel all pending and use defaults
                for task in tasks:
                    if not task.done():
                        task.cancel()
                logger.info("🔌 Memory load cancelled (client disconnect)")
                done, pending = set(), set(tasks)
            except Exception as e:
                # Catch any other unexpected errors
                logger.error(f"❌ Memory task wait failed: {e}")
                done, pending = set(), set(tasks)
            
            # Process completed tasks
            for task in done:
                try:
                    name, result, status = task.result()
                    component_results[name] = result
                    component_status[name] = status
                    logger.debug(f"  ✓ {name}: {status}")
                except Exception as e:
                    # Should not happen, but safety net
                    task_name = task.get_name()
                    component_results[task_name] = COMPONENT_CONFIG.get(task_name, {}).get("default")
                    component_status[task_name] = "error"
                    logger.error(f"❌ Unexpected task error for {task_name}: {e}")
            
            # Handle pending tasks (didn't complete before global deadline)
            for task in pending:
                task_name = task.get_name()
                task.cancel()  # Stop the pending task
                component_results[task_name] = COMPONENT_CONFIG.get(task_name, {}).get("default")
                component_status[task_name] = "deadline"
                logger.warning(f"⏰ {task_name} exceeded global deadline")
            
            # Final status check
            logger.info(f"🧠 Memory components: {len(component_status)} processed - {dict(component_status)}")
            
            # DATABASE PRESSURE DETECTION (2026-01-11):
            # If ALL components timeout, it's likely DB pool exhaustion
            timeout_count = sum(1 for s in component_status.values() if s in ("timeout", "deadline"))
            if timeout_count >= 4:
                logger.error(
                    f"🔥 CRITICAL: {timeout_count}/6 memory components timed out - "
                    f"Possible MongoDB connection pool exhaustion. "
                    f"Consider checking pool stats and increasing maxPoolSize."
                )
            
            # Extract results with defaults for any missing
            recent_messages = component_results.get("conversation", [])
            user_profile = component_results.get("profile", {})
            mastery_level = component_results.get("mastery", 0)
            relevant_memories = component_results.get("semantic_memory", [])
            weak_topics = component_results.get("weak_topics", [])
            continuity = component_results.get("continuity", {})
            
            # ================================================================
            # CONTEXT QUALITY LEVEL CALCULATION
            # ================================================================
            # Level 5: All components succeeded
            # Level 4: conversation + profile + mastery succeeded
            # Level 3: conversation + profile succeeded
            # Level 2: Only conversation succeeded
            # Level 1: No critical components (fallback mode)
            # ================================================================
            
            successful_components = [k for k, v in component_status.items() if v == "success"]
            failed_components = [k for k, v in component_status.items() if v != "success"]
            
            # ================================================================
            # Calculate quality level based on what SUCCEEDED (not data presence)
            # For new users/sessions, components succeed with empty data - that's OK
            # ================================================================
            conv_succeeded = component_status.get("conversation") == "success"
            profile_succeeded = component_status.get("profile") == "success"
            mastery_succeeded = component_status.get("mastery") == "success"
            semantic_succeeded = component_status.get("semantic_memory") == "success"
            weak_topics_succeeded = component_status.get("weak_topics") == "success"
            continuity_succeeded = component_status.get("continuity") == "success"
            
            # Also track if we have ACTUAL data (for richer context)
            has_prior_messages = len(recent_messages) > 0
            has_profile_data = bool(user_profile)
            
            if all([conv_succeeded, profile_succeeded, mastery_succeeded, semantic_succeeded, weak_topics_succeeded, continuity_succeeded]):
                context_quality = 5  # Full intelligence - all systems working
            elif conv_succeeded and profile_succeeded and mastery_succeeded:
                context_quality = 4  # Strong intelligence
            elif conv_succeeded and profile_succeeded:
                context_quality = 3  # Moderate intelligence
            elif conv_succeeded:
                context_quality = 2  # Minimal but working
            elif len(component_status) > 0:
                context_quality = 2  # Some components working
            else:
                context_quality = 1  # No components responded (critical failure)
            
            # Track context quality in the context object
            context["_context_quality"] = context_quality
            context["_components_loaded"] = successful_components
            context["_components_failed"] = failed_components
            context["_component_status"] = component_status
            
            # Backward compatibility: set _memory_degraded flag
            context["_memory_degraded"] = context_quality < 5
            
            # OBSERVABILITY FIX (2026-01-11): Enhanced logging with request_id and latency
            total_latency_ms = (time.time() - request_start) * 1000
            data_info = f"msgs={len(recent_messages)}, profile={'yes' if has_profile_data else 'no'}"
            
            # Store metrics in context for downstream use
            context["_component_latencies"] = component_latencies
            context["_total_latency_ms"] = total_latency_ms
            
            # Build latency summary for log
            latency_summary = ", ".join([
                f"{k}={v['latency_ms']:.0f}ms" 
                for k, v in component_latencies.items()
            ])
            
            if context_quality == 5:
                logger.info(f"🧠 Context quality: FULL (5/5) - all 6 components loaded ({data_info}) [rid={request_id}] [{total_latency_ms:.0f}ms]")
            elif context_quality >= 3:
                logger.info(f"🧠 Context quality: {context_quality}/5 - {len(successful_components)}/6 components ({data_info}) [rid={request_id}] [{total_latency_ms:.0f}ms]")
            elif context_quality == 2:
                logger.info(f"🧠 Context quality: {context_quality}/5 - limited but working ({data_info}) [rid={request_id}] [{total_latency_ms:.0f}ms]")
            else:
                logger.warning(f"⚠️ Context quality: {context_quality}/5 - CRITICAL: components not responding ({len(failed_components)} failed: {', '.join(failed_components)}) [rid={request_id}] [{total_latency_ms:.0f}ms]")
                logger.warning(f"   Component latencies: {latency_summary}")
            
            # 1. Recent conversation context
            context["recent_context"] = recent_messages
            context["has_prior_context"] = has_prior_messages
            context["_has_profile_data"] = has_profile_data
            
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
            
            logger.info(f"🧠 Enhanced context: {len(recent_messages)} recent, "
                       f"{len(relevant_memories)} memories, mastery={mastery_level} [rid={request_id}]")
            
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
        """
        Get or create user learning profile with micro-caching
        
        CONCURRENCY FIX (2026-01-11):
        - Cache access protected by asyncio.Lock
        - Returns deepcopy to prevent mutation of cached data
        """
        try:
            # OPTIMIZATION: Check micro-cache first (deduplicates queries within same request)
            import time
            now_ms = time.time() * 1000
            
            # CONCURRENCY FIX: Check cache under lock
            async with self._profile_cache_lock:
                cached = self._profile_cache.get(user_id)
                if cached:
                    cached_profile, cached_time = cached
                    if (now_ms - cached_time) < self._profile_cache_ttl_ms:
                        # OBSERVABILITY FIX: Track cache hit
                        async with self._cache_stats_lock:
                            self._cache_stats["profile_hits"] += 1
                        logger.debug(f"⚡ Profile cache hit for {user_id[:8]}")
                        # Return deepcopy to prevent mutation of cached data
                        return copy.deepcopy(cached_profile)
            
            # OBSERVABILITY FIX: Track cache miss
            async with self._cache_stats_lock:
                self._cache_stats["profile_misses"] += 1
            
            # Try to get from learning profile
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if profile is not None:
                # Get user name from users collection
                user = await self.db.users.find_one({"user_id": user_id})
                if user is not None:
                    full_name = user.get("full_name", "")
                    profile["name"] = full_name.split()[0] if full_name else ""
                
                # Cache the result under lock
                async with self._profile_cache_lock:
                    self._profile_cache[user_id] = (copy.deepcopy(profile), now_ms)
                await self._cleanup_profile_cache()
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
            
            # Cache the new profile under lock
            async with self._profile_cache_lock:
                self._profile_cache[user_id] = (copy.deepcopy(default_profile), now_ms)
            await self._cleanup_profile_cache()
            
            return default_profile
            
        except asyncio.CancelledError:
            # Re-raise CancelledError - don't swallow it
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {e}")
            return {}
    
    async def _cleanup_profile_cache(self):
        """
        Clean up expired entries from profile cache (prevents memory leak)
        
        CONCURRENCY FIX (2026-01-11):
        - Made async with lock to prevent dict modification during iteration
        - Collect keys to delete first, then delete under lock
        """
        import time
        now_ms = time.time() * 1000
        
        async with self._profile_cache_lock:
            # Collect expired keys first (don't modify during iteration)
            expired_keys = [
                k for k, (_, cached_time) in list(self._profile_cache.items())
                if (now_ms - cached_time) > self._profile_cache_ttl_ms
            ]
            for k in expired_keys:
                del self._profile_cache[k]
            
            # Safety: limit cache size (should rarely hit this)
            if len(self._profile_cache) > 50:
                # Remove oldest entries - collect keys first
                sorted_entries = sorted(
                    list(self._profile_cache.items()),
                    key=lambda x: x[1][1]  # Sort by timestamp
                )
                keys_to_remove = [k for k, _ in sorted_entries[:25]]
                for k in keys_to_remove:
                    del self._profile_cache[k]
    
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
        # CONCURRENCY FIX (2026-01-11): Protected by lock
        import time
        dedup_key = f"{user_id}:{session_id}:{request_id or user_message[:50]}"
        current_time = time.time()
        
        async with self._dedup_lock:
            # Clean old entries from dedup cache (under lock)
            if len(self._recent_write_keys) > self._max_dedup_cache_size:
                cutoff = current_time - self._dedup_window_seconds
                # Create new dict instead of modifying during iteration
                self._recent_write_keys = {
                    k: v for k, v in list(self._recent_write_keys.items())
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
            
            # Record this write (under lock)
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
    
    # =========================================================================
    # OBSERVABILITY: Health and Metrics (2026-01-11)
    # =========================================================================
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring
        
        OBSERVABILITY FIX (2026-01-11): Exposes cache metrics for dashboards
        
        Returns:
            Dict with profile cache and dedup cache statistics
        """
        async with self._cache_stats_lock:
            profile_total = self._cache_stats["profile_hits"] + self._cache_stats["profile_misses"]
            profile_hit_rate = (
                self._cache_stats["profile_hits"] / profile_total 
                if profile_total > 0 else 0
            )
            
            return {
                "profile_cache": {
                    "hits": self._cache_stats["profile_hits"],
                    "misses": self._cache_stats["profile_misses"],
                    "total": profile_total,
                    "hit_rate_percent": round(profile_hit_rate * 100, 1),
                    "size": len(self._profile_cache)
                },
                "dedup_cache": {
                    "hits": self._cache_stats["dedup_hits"],
                    "total": self._cache_stats["dedup_total"],
                    "size": len(self._recent_write_keys)
                },
                "embedding_cache": self.semantic_memory._cache.stats() if self._semantic_memory else {}
            }
    
    async def get_memory_health(self) -> Dict[str, Any]:
        """
        Get overall memory system health
        
        OBSERVABILITY FIX (2026-01-11): Provides health check for monitoring
        
        Returns:
            Dict with health status and component availability
        """
        health = {
            "status": "healthy",
            "components": {
                "memory_service": self._memory_service is not None,
                "semantic_memory": self._semantic_memory is not None,
                "mastery_tracker": self._mastery_tracker is not None,
                "continuity_engine": self._continuity_engine is not None,
            },
            "embedding_status": "unknown"
        }
        
        # Check embedding health
        if self._semantic_memory:
            health["embedding_status"] = self.semantic_memory.get_embedding_health()
        
        # Determine overall status
        components_up = sum(health["components"].values())
        if components_up < 2:
            health["status"] = "degraded"
        elif components_up < 4:
            health["status"] = "partial"
        
        return health


# Convenience function for easy import
async def get_memory_integration(db, openai_api_key: str = None) -> MemoryIntegrationService:
    """Factory function to create MemoryIntegrationService"""
    return MemoryIntegrationService(db, openai_api_key)

