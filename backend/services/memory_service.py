"""
Memory Service - Persistent Memory Management (MEMORY v2)
=========================================================

Handles:
- Short-term conversation context (rolling window)
- Session state persistence (survives restarts)
- Student profile management (long-term)
- Memory event logging (write-ahead log)

MEMORY CONTRACT: Uses canonical schemas from models/memory.py
MULTI-TENANT: All operations require user_id for isolation
"""
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# Debug flag
MEMORY_DEBUG = os.getenv("MEMORY_DEBUG", "false").lower() == "true"


class MemoryService:
    """
    Manages short-term conversation context for AI Tutor
    
    Features:
    - Rolling window of last N messages
    - Session-based context management
    - Context trimming for token budget
    - Fast retrieval for real-time responses
    """
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.default_window_size = 10
        self.max_messages_per_session = 50
    
    async def get_conversation_context(
        self,
        session_id: str,
        user_id: str,
        window_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get last N messages for context
        
        Args:
            session_id: Current chat session
            user_id: User ID (for security)
            window_size: Number of messages to retrieve (default: 10)
        
        Returns:
            List of messages in chronological order
        """
        try:
            window = window_size or self.default_window_size
            
            # Get last N messages
            messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).sort("timestamp", -1).limit(window).to_list(None)
            
            # Reverse to chronological order
            messages = list(reversed(messages))
            
            logger.info(f"📜 Retrieved {len(messages)} messages for context")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation context: {e}")
            return []
    
    async def save_message_to_context(
        self,
        session_id: str,
        user_id: str,
        message: Dict[str, Any]
    ):
        """
        Save message and maintain rolling window
        
        Args:
            session_id: Current session
            user_id: User ID
            message: Message data to save
        """
        try:
            # Add timestamps if missing
            if "timestamp" not in message:
                message["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Save message
            await self.db.chat_messages.insert_one(message)
            
            # Maintain rolling window - keep only last N messages
            all_messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).sort("timestamp", -1).to_list(None)
            
            if len(all_messages) > self.max_messages_per_session:
                # Delete oldest messages
                old_ids = [msg["_id"] for msg in all_messages[self.max_messages_per_session:]]
                await self.db.chat_messages.delete_many({
                    "_id": {"$in": old_ids}
                })
                logger.info(f"🗑️ Deleted {len(old_ids)} old messages (rolling window)")
            
        except Exception as e:
            logger.error(f"❌ Failed to save message to context: {e}")
    
    async def get_session_summary(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get summarized context for current session
        
        Returns:
            Dict with session summary, concepts covered, etc.
        """
        try:
            # Get all messages in session
            messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).to_list(None)
            
            # Extract concepts discussed
            concepts = []
            for msg in messages:
                if msg.get("intent") == "concept_explanation":
                    # Extract concept from question
                    question = msg.get("user_message", "")
                    concepts.extend(self._extract_concepts_simple(question))
            
            # Count messages
            user_msgs = [m for m in messages if m.get("user_message")]
            ai_msgs = [m for m in messages if m.get("ai_response")]
            
            return {
                "session_id": session_id,
                "total_messages": len(messages),
                "user_messages": len(user_msgs),
                "ai_messages": len(ai_msgs),
                "concepts_discussed": list(set(concepts)),
                "session_duration_mins": self._calculate_duration(messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session summary: {e}")
            return {}
    
    def _extract_concepts_simple(self, text: str) -> List[str]:
        """Simple concept extraction (can be enhanced with NLP)"""
        concepts = []
        text_lower = text.lower()
        
        # Physics
        if "newton" in text_lower and "law" in text_lower:
            concepts.append("newton_laws")
        if "force" in text_lower or "f=ma" in text_lower:
            concepts.append("force_acceleration")
        
        # Math
        if "derivative" in text_lower or "differentiation" in text_lower:
            concepts.append("derivatives")
        if "integral" in text_lower or "integration" in text_lower:
            concepts.append("integrals")
        if "fundamental theorem" in text_lower:
            concepts.append("fundamental_theorem_calculus")
        
        return concepts
    
    def _calculate_duration(self, messages: List[Dict]) -> int:
        """Calculate session duration in minutes"""
        if not messages or len(messages) < 2:
            return 0
        
        try:
            first = messages[0].get("timestamp")
            last = messages[-1].get("timestamp")
            
            if isinstance(first, str):
                from dateutil import parser
                first = parser.parse(first)
            if isinstance(last, str):
                from dateutil import parser
                last = parser.parse(last)
            
            duration = (last - first).total_seconds() / 60
            return int(duration)
        except:
            return 0
    
    async def consolidate_session_memory(
        self,
        session_id: str,
        user_id: str
    ) -> str:
        """
        Consolidate session into summary for long-term storage
        (Saves tokens by summarizing old conversations)
        
        Returns:
            Session summary text
        """
        try:
            messages = await self.get_conversation_context(session_id, user_id, window_size=50)
            
            if not messages:
                return ""
            
            # Build summary
            summary_parts = []
            for msg in messages:
                user_q = msg.get("user_message", "")
                if user_q:
                    summary_parts.append(f"Q: {user_q[:100]}")
            
            summary = " | ".join(summary_parts)
            return f"Session covered: {summary}"
            
        except Exception as e:
            logger.error(f"❌ Session consolidation failed: {e}")
            return ""
    
    # =========================================================================
    # MEMORY v2 - PERSISTENT SESSION STATE
    # =========================================================================
    
    async def get_session_state(
        self,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get persistent session state (survives restarts).
        
        MEMORY CONTRACT: Returns SessionState schema fields.
        MULTI-TENANT: Isolated by user_id + session_id.
        """
        try:
            # Query by user_id + session_id (multi-tenant isolation)
            state_doc = await self.db.session_states.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            if state_doc:
                if MEMORY_DEBUG:
                    logger.info(f"📦 Session state loaded: user={user_id[:8]}, session={session_id[:8]}")
                return self._doc_to_session_state(state_doc)
            
            # Return default state if not found
            return self._create_default_session_state(user_id, session_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to get session state: {e}")
            return self._create_default_session_state(user_id, session_id)
    
    async def save_session_state(
        self,
        user_id: str,
        session_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Save session state (persistent across restarts).
        
        IDEMPOTENT: Can be called multiple times safely.
        """
        try:
            # Enforce bounded growth
            state = self._enforce_session_bounds(state)
            
            # Add metadata
            state["user_id"] = user_id
            state["session_id"] = session_id
            state["last_updated"] = datetime.now(timezone.utc)
            state["schema_version"] = 2
            
            # Upsert (atomic)
            await self.db.session_states.update_one(
                {"user_id": user_id, "session_id": session_id},
                {"$set": state},
                upsert=True
            )
            
            if MEMORY_DEBUG:
                logger.info(f"💾 Session state saved: user={user_id[:8]}, session={session_id[:8]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save session state: {e}")
            return False
    
    async def update_session_turn(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: str,
        agent_name: str = None,
        topics: List[str] = None
    ) -> bool:
        """
        Add a turn to session state (bounded to last 10).
        
        MEMORY CONTRACT: Uses diff updates, not full overwrites.
        """
        try:
            turn = {
                "user": user_message[:500],  # Bounded
                "ai": ai_response[:1000],    # Bounded
                "agent": agent_name,
                "topics": (topics or [])[:3],  # Max 3 topics per turn
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Push to last_turns with bounded size
            await self.db.session_states.update_one(
                {"user_id": user_id, "session_id": session_id},
                {
                    "$push": {
                        "last_turns": {
                            "$each": [turn],
                            "$slice": -10  # Keep only last 10
                        }
                    },
                    "$set": {
                        "last_updated": datetime.now(timezone.utc),
                        "last_used_agent": agent_name
                    },
                    "$addToSet": {
                        "last_retrieval_topics": {"$each": (topics or [])[:5]}
                    }
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update session turn: {e}")
            return False
    
    async def update_session_summary(
        self,
        user_id: str,
        session_id: str,
        summary: str
    ) -> bool:
        """
        Update session summary (bounded to 800 chars).
        
        Only updates if meaningfully different from current.
        """
        try:
            # Get current summary
            current = await self.db.session_states.find_one(
                {"user_id": user_id, "session_id": session_id},
                {"session_summary": 1}
            )
            
            current_summary = current.get("session_summary", "") if current else ""
            
            # Only update if meaningfully different (>20% change)
            if self._is_meaningfully_different(current_summary, summary):
                bounded_summary = summary[:800]  # Enforce bound
                
                await self.db.session_states.update_one(
                    {"user_id": user_id, "session_id": session_id},
                    {
                        "$set": {
                            "session_summary": bounded_summary,
                            "last_updated": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True
                )
                
                if MEMORY_DEBUG:
                    logger.info(f"📝 Session summary updated: {len(bounded_summary)} chars")
                
                return True
            
            return False  # No update needed
            
        except Exception as e:
            logger.error(f"❌ Failed to update session summary: {e}")
            return False
    
    # =========================================================================
    # MEMORY v2 - PERSISTENT STUDENT PROFILE
    # =========================================================================
    
    async def get_student_profile(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get student profile (long-term, persists across sessions).
        
        MEMORY CONTRACT: Returns StudentProfile schema fields.
        MULTI-TENANT: Isolated by user_id.
        """
        try:
            profile_doc = await self.db.student_profiles.find_one({"user_id": user_id})
            
            if profile_doc:
                if MEMORY_DEBUG:
                    logger.info(f"👤 Student profile loaded: user={user_id[:8]}")
                return self._doc_to_student_profile(profile_doc)
            
            # Create default profile
            return await self._create_default_student_profile(user_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to get student profile: {e}")
            return self._default_profile(user_id)
    
    async def update_student_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update student profile (diff update, not full overwrite).
        
        MEMORY CONTRACT: Only updates specified fields.
        """
        try:
            # Add metadata
            updates["updated_at"] = datetime.now(timezone.utc)
            
            # Apply bounded growth constraints
            if "weak_topics" in updates:
                updates["weak_topics"] = updates["weak_topics"][-10:]
            if "strong_topics" in updates:
                updates["strong_topics"] = updates["strong_topics"][-10:]
            
            await self.db.student_profiles.update_one(
                {"user_id": user_id},
                {"$set": updates},
                upsert=True
            )
            
            if MEMORY_DEBUG:
                logger.info(f"👤 Student profile updated: user={user_id[:8]}, fields={list(updates.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update student profile: {e}")
            return False
    
    async def update_topic_mastery(
        self,
        user_id: str,
        topic: str,
        mastery_delta: float,
        confidence: float = 0.7
    ) -> bool:
        """
        Update mastery for a specific topic.
        
        MEMORY CONTRACT: Bounded mastery (0-1), bounded topics (max 50).
        """
        try:
            topic_key = topic.lower().replace(" ", "_")[:50]  # Normalize + bound
            
            # Get current mastery
            profile = await self.db.student_profiles.find_one(
                {"user_id": user_id},
                {f"mastery_by_topic.{topic_key}": 1}
            )
            
            current = 0.0
            if profile and "mastery_by_topic" in profile:
                topic_data = profile["mastery_by_topic"].get(topic_key, {})
                current = topic_data.get("mastery_score", 0.0)
            
            # Calculate new mastery (bounded 0-1)
            new_mastery = max(0.0, min(1.0, current + mastery_delta))
            
            await self.db.student_profiles.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"mastery_by_topic.{topic_key}": {
                            "topic": topic,
                            "mastery_score": new_mastery,
                            "last_updated": datetime.now(timezone.utc),
                            "confidence": confidence
                        },
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$inc": {
                        f"mastery_by_topic.{topic_key}.interaction_count": 1
                    }
                },
                upsert=True
            )
            
            if MEMORY_DEBUG:
                logger.info(f"📈 Mastery updated: {topic} = {new_mastery:.2f} (delta={mastery_delta:+.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update mastery: {e}")
            return False
    
    # =========================================================================
    # MEMORY v2 - MEMORY EVENTS (WRITE-AHEAD LOG)
    # =========================================================================
    
    async def log_memory_event(
        self,
        user_id: str,
        session_id: str,
        event_type: str,
        payload: Dict[str, Any],
        source_agent: str = None,
        request_id: str = None
    ) -> bool:
        """
        Log a memory event (write-ahead log for audit/debug).
        
        RETENTION: Auto-pruned to last 100 per user.
        """
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc),
                "payload": self._bound_payload(payload),
                "source_agent": source_agent,
                "request_id": request_id,
                "schema_version": 2
            }
            
            await self.db.memory_events.insert_one(event)
            
            # Prune old events (keep last 100 per user)
            await self._prune_memory_events(user_id)
            
            if MEMORY_DEBUG:
                logger.info(f"📝 Memory event logged: {event_type} | user={user_id[:8]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to log memory event: {e}")
            return False
    
    async def get_memory_events(
        self,
        user_id: str,
        event_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get memory events for a user (for debugging/audit)."""
        try:
            query = {"user_id": user_id}
            if event_type:
                query["event_type"] = event_type
            
            cursor = self.db.memory_events.find(query).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory events: {e}")
            return []
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    def _doc_to_session_state(self, doc: Dict) -> Dict[str, Any]:
        """Convert MongoDB doc to SessionState schema."""
        return {
            "user_id": doc.get("user_id"),
            "session_id": doc.get("session_id"),
            "schema_version": doc.get("schema_version", 2),
            "last_turns": doc.get("last_turns", [])[-10:],  # Bounded
            "session_summary": (doc.get("session_summary", "") or "")[:800],  # Bounded
            "active_task": doc.get("active_task"),
            "open_questions": doc.get("open_questions", [])[:5],
            "last_used_agent": doc.get("last_used_agent"),
            "last_retrieval_topics": doc.get("last_retrieval_topics", [])[:5],
            "created_at": doc.get("created_at"),
            "last_updated": doc.get("last_updated")
        }
    
    def _create_default_session_state(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Create default session state."""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "schema_version": 2,
            "last_turns": [],
            "session_summary": "",
            "active_task": None,
            "open_questions": [],
            "last_used_agent": None,
            "last_retrieval_topics": [],
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
    
    def _enforce_session_bounds(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce bounded growth on session state."""
        if "last_turns" in state:
            state["last_turns"] = state["last_turns"][-10:]
        if "session_summary" in state:
            state["session_summary"] = (state["session_summary"] or "")[:800]
        if "open_questions" in state:
            state["open_questions"] = state["open_questions"][:5]
        if "last_retrieval_topics" in state:
            state["last_retrieval_topics"] = state["last_retrieval_topics"][:5]
        return state
    
    def _doc_to_student_profile(self, doc: Dict) -> Dict[str, Any]:
        """Convert MongoDB doc to StudentProfile schema."""
        return {
            "user_id": doc.get("user_id"),
            "schema_version": doc.get("schema_version", 2),
            "grade": doc.get("grade"),
            "exam_target": doc.get("exam_target"),
            "exam_date": doc.get("exam_date"),
            "mastery_by_topic": doc.get("mastery_by_topic", {}),
            "weak_topics": doc.get("weak_topics", [])[-10:],
            "strong_topics": doc.get("strong_topics", [])[-10:],
            "preferred_explanation": doc.get("preferred_explanation", "step_by_step"),
            "language_style": doc.get("language_style", "concise"),
            "pacing": doc.get("pacing", "normal"),
            "preferred_analogies": doc.get("preferred_analogies", ["cricket", "cooking"]),
            "motivation_baseline": doc.get("motivation_baseline", 0.5),
            "current_goals": doc.get("current_goals", [])[:5],
            "practice_streak": doc.get("practice_streak", 0),
            "revision_streak": doc.get("revision_streak", 0),
            "last_practice_date": doc.get("last_practice_date"),
            "safety_flags": doc.get("safety_flags", {}),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        }
    
    async def _create_default_student_profile(self, user_id: str) -> Dict[str, Any]:
        """Create and save default student profile."""
        profile = self._default_profile(user_id)
        
        try:
            await self.db.student_profiles.insert_one(profile)
            logger.info(f"👤 Created default profile for user {user_id[:8]}")
        except Exception as e:
            # May already exist (race condition)
            logger.debug(f"Profile may already exist: {e}")
        
        return profile
    
    def _default_profile(self, user_id: str) -> Dict[str, Any]:
        """Return default profile dict."""
        now = datetime.now(timezone.utc)
        return {
            "user_id": user_id,
            "schema_version": 2,
            "grade": None,
            "exam_target": None,
            "exam_date": None,
            "mastery_by_topic": {},
            "weak_topics": [],
            "strong_topics": [],
            "preferred_explanation": "step_by_step",
            "language_style": "concise",
            "pacing": "normal",
            "preferred_analogies": ["cricket", "cooking"],
            "motivation_baseline": 0.5,
            "current_goals": [],
            "practice_streak": 0,
            "revision_streak": 0,
            "last_practice_date": None,
            "safety_flags": {},
            "created_at": now,
            "updated_at": now
        }
    
    def _is_meaningfully_different(self, old: str, new: str) -> bool:
        """Check if new content is meaningfully different (>20% change)."""
        if not old:
            return bool(new)
        if not new:
            return False
        
        # Simple word-based diff
        old_words = set(old.lower().split())
        new_words = set(new.lower().split())
        
        if not old_words:
            return bool(new_words)
        
        overlap = len(old_words & new_words) / len(old_words)
        return overlap < 0.8  # >20% change
    
    def _bound_payload(self, payload: Any) -> Dict[str, Any]:
        """
        Bound payload size for memory events.
        
        DEFENSIVE: Handles list/tuple/None inputs gracefully.
        NEVER raises.
        """
        import json
        try:
            # DEFENSIVE: Normalize payload to dict if it's a list/tuple/None
            if payload is None:
                return {}
            
            if isinstance(payload, (list, tuple)):
                # Wrap list/tuple as {"items": [...]}
                payload = {"items": list(payload) if isinstance(payload, tuple) else payload}
            
            if not isinstance(payload, dict):
                # Fallback: wrap as {"value": str(payload)}
                payload = {"value": str(payload)}
            
            payload_str = json.dumps(payload, default=str)  # default=str for non-serializable objects
            if len(payload_str) > 2000:
                return {"truncated": True, "reason": "payload_too_large", "keys": list(payload.keys())}
            return payload
        except Exception:
            return {"error": "serialization_failed"}
    
    async def _prune_memory_events(self, user_id: str, max_events: int = 100):
        """Prune old memory events (keep last N per user)."""
        try:
            # Count events
            count = await self.db.memory_events.count_documents({"user_id": user_id})
            
            if count > max_events:
                # Find oldest events to delete
                cursor = self.db.memory_events.find(
                    {"user_id": user_id}
                ).sort("timestamp", 1).limit(count - max_events)
                
                old_ids = [doc["_id"] async for doc in cursor]
                
                if old_ids:
                    await self.db.memory_events.delete_many({"_id": {"$in": old_ids}})
                    if MEMORY_DEBUG:
                        logger.info(f"🗑️ Pruned {len(old_ids)} old memory events for user {user_id[:8]}")
        except Exception as e:
            logger.warning(f"Failed to prune memory events: {e}")

