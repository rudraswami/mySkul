"""
ConversationStateManager - Unified Context Tracking
====================================================
Maintains conversation state across messages.
Replaces: fragmented context handling, truncated history.

Tracks:
- Current topic and concept
- Difficulty level
- Confusion signals
- Topics covered in session
- Question patterns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ConversationStateManager:
    """
    Manages conversation state for intelligent context-aware responses.
    """
    
    def __init__(self, db):
        self.db = db
        self._cache: Dict[str, Dict] = {}  # In-memory cache for fast access
    
    async def get_state(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get current conversation state.
        """
        cache_key = f"{user_id}_{session_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load from database
        try:
            state_doc = await self.db.conversation_states.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            if state_doc:
                state = {
                    "current_topic": state_doc.get("current_topic"),
                    "current_concept": state_doc.get("current_concept"),
                    "current_subject": state_doc.get("current_subject"),
                    "difficulty_level": state_doc.get("difficulty_level", 0.5),
                    "confusion_level": state_doc.get("confusion_level", 0),
                    "topics_covered": state_doc.get("topics_covered", []),
                    "question_count": state_doc.get("question_count", 0),
                    "last_intent": state_doc.get("last_intent"),
                    "session_start": state_doc.get("session_start")
                }
                self._cache[cache_key] = state
                return state
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
        
        # Return default state
        default_state = {
            "current_topic": None,
            "current_concept": None,
            "current_subject": None,
            "difficulty_level": 0.5,
            "confusion_level": 0,
            "topics_covered": [],
            "question_count": 0,
            "last_intent": None,
            "session_start": datetime.now(timezone.utc).isoformat()
        }
        self._cache[cache_key] = default_state
        return default_state
    
    async def update_state(
        self,
        user_id: str,
        session_id: str,
        question: str,
        response: str,
        subject: str = None,
        intent: str = None
    ) -> None:
        """
        Update conversation state after an exchange.
        """
        cache_key = f"{user_id}_{session_id}"
        state = await self.get_state(user_id, session_id)
        
        # Extract topic from question
        topic = self._extract_topic(question, subject)
        concept = self._extract_concept(question)
        
        # Update state
        state["question_count"] += 1
        state["last_intent"] = intent
        
        if topic:
            state["current_topic"] = topic
            if topic not in state["topics_covered"]:
                state["topics_covered"].append(topic)
        
        if concept:
            state["current_concept"] = concept
        
        if subject:
            state["current_subject"] = subject
        
        # Detect confusion signals
        confusion_indicators = ['confused', 'don\'t understand', 'help', 'stuck', 'what do you mean', 'explain again', 'still not clear']
        if any(ind in question.lower() for ind in confusion_indicators):
            state["confusion_level"] = min(1.0, state["confusion_level"] + 0.3)
        else:
            state["confusion_level"] = max(0, state["confusion_level"] - 0.1)
        
        # Update cache
        self._cache[cache_key] = state
        
        # Persist to database (async, non-blocking)
        try:
            await self.db.conversation_states.update_one(
                {"user_id": user_id, "session_id": session_id},
                {"$set": {
                    **state,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to persist state: {e}")
    
    async def get_context_summary(
        self,
        user_id: str,
        session_id: str,
        message_history: List[Dict]
    ) -> str:
        """
        Generate a concise context summary for the LLM.
        Replaces: raw message dumps, truncated history.
        """
        state = await self.get_state(user_id, session_id)
        
        # Build summary parts
        parts = []
        
        # Current topic context
        if state.get("current_topic"):
            parts.append(f"Current topic: {state['current_topic']}")
        
        if state.get("current_subject"):
            parts.append(f"Subject: {state['current_subject']}")
        
        # Topics covered
        if state.get("topics_covered") and len(state["topics_covered"]) > 1:
            recent_topics = state["topics_covered"][-5:]  # Last 5 topics
            parts.append(f"Topics discussed: {', '.join(recent_topics)}")
        
        # Question count
        if state.get("question_count", 0) > 1:
            parts.append(f"Questions asked: {state['question_count']}")
        
        # Confusion indicator
        if state.get("confusion_level", 0) > 0.3:
            parts.append("Student seems confused - use simpler explanations")
        
        # Summarize recent messages with Q&A pairs
        if message_history and len(message_history) > 0:
            recent = message_history[-10:]
            conversation_lines = []
            
            for msg in recent:
                user_q = msg.get("user_message", msg.get("message", ""))
                ai_response = msg.get("ai_response", {})
                
                if user_q:
                    # Get short version of question
                    short_q = user_q[:80] + "..." if len(user_q) > 80 else user_q
                    
                    # Try to extract topic from AI response
                    topic_discussed = ""
                    if isinstance(ai_response, dict):
                        # Try to get main content
                        default_view = ai_response.get("default_view", {})
                        main_content = default_view.get("main_content", {})
                        if isinstance(main_content, dict):
                            content = main_content.get("content", "")
                        else:
                            content = str(main_content)[:100] if main_content else ""
                        
                        # Extract first sentence as topic hint
                        if content:
                            first_sentence = content.split('.')[0][:60]
                            topic_discussed = f" → Discussed: {first_sentence}..."
                    
                    conversation_lines.append(f"Q: {short_q}{topic_discussed}")
            
            if conversation_lines:
                parts.append("Recent conversation:\n" + "\n".join(conversation_lines[-5:]))
        
        return "\n".join(parts) if parts else ""
    
    def _extract_topic(self, question: str, subject: str = None) -> Optional[str]:
        """Extract the main topic from a question."""
        q = question.lower()
        
        # Physics topics
        physics_topics = {
            'force': ['force', 'newton', 'push', 'pull'],
            'motion': ['motion', 'velocity', 'speed', 'acceleration', 'displacement'],
            'gravity': ['gravity', 'gravitational', 'free fall', 'weight'],
            'energy': ['energy', 'kinetic', 'potential', 'work', 'power'],
            'momentum': ['momentum', 'impulse', 'collision'],
            'waves': ['wave', 'frequency', 'wavelength', 'amplitude'],
            'light': ['light', 'reflection', 'refraction', 'lens', 'mirror', 'optics'],
            'electricity': ['electric', 'current', 'voltage', 'resistance', 'circuit', 'ohm'],
            'magnetism': ['magnet', 'magnetic', 'field', 'flux']
        }
        
        # Chemistry topics
        chemistry_topics = {
            'atomic structure': ['atom', 'electron', 'proton', 'neutron', 'orbital', 'shell'],
            'chemical bonding': ['bond', 'covalent', 'ionic', 'metallic', 'hydrogen bond'],
            'reactions': ['reaction', 'oxidation', 'reduction', 'redox'],
            'acids and bases': ['acid', 'base', 'ph', 'neutralization'],
            'organic chemistry': ['organic', 'carbon', 'hydrocarbon', 'alkane', 'alkene']
        }
        
        # Biology topics
        biology_topics = {
            'cell biology': ['cell', 'nucleus', 'mitochondria', 'organelle'],
            'genetics': ['dna', 'gene', 'chromosome', 'heredity', 'mutation'],
            'photosynthesis': ['photosynthesis', 'chlorophyll', 'chloroplast'],
            'respiration': ['respiration', 'atp', 'glycolysis'],
            'evolution': ['evolution', 'natural selection', 'darwin', 'species']
        }
        
        # Math topics
        math_topics = {
            'algebra': ['equation', 'variable', 'polynomial', 'quadratic'],
            'calculus': ['derivative', 'integral', 'differentiation', 'integration', 'limit'],
            'geometry': ['triangle', 'circle', 'angle', 'area', 'perimeter', 'pythagoras'],
            'trigonometry': ['sin', 'cos', 'tan', 'trigonometry', 'angle'],
            'probability': ['probability', 'statistics', 'mean', 'median', 'variance']
        }
        
        # Check based on subject
        topic_maps = {
            'physics': physics_topics,
            'chemistry': chemistry_topics,
            'biology': biology_topics,
            'mathematics': math_topics
        }
        
        if subject:
            topic_map = topic_maps.get(subject.lower(), {})
            for topic, keywords in topic_map.items():
                if any(kw in q for kw in keywords):
                    return topic
        
        # Check all topics if no subject
        for topic_map in topic_maps.values():
            for topic, keywords in topic_map.items():
                if any(kw in q for kw in keywords):
                    return topic
        
        return None
    
    def _extract_concept(self, question: str) -> Optional[str]:
        """Extract specific concept from question."""
        q = question.lower()
        
        # Common concepts
        concepts = [
            'force', 'motion', 'gravity', 'friction', 'momentum', 'energy',
            'wave', 'light', 'sound', 'electricity', 'magnetism',
            'atom', 'molecule', 'bond', 'reaction', 'acid', 'base',
            'cell', 'dna', 'gene', 'photosynthesis', 'respiration',
            'equation', 'function', 'derivative', 'integral', 'probability'
        ]
        
        for concept in concepts:
            if concept in q:
                return concept
        
        return None
    
    async def clear_state(self, user_id: str, session_id: str) -> None:
        """Clear conversation state (for new session)."""
        cache_key = f"{user_id}_{session_id}"
        
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        try:
            await self.db.conversation_states.delete_one({
                "user_id": user_id,
                "session_id": session_id
            })
        except Exception as e:
            logger.warning(f"Failed to clear state: {e}")
    
    async def get_learning_progress(self, user_id: str) -> Dict[str, Any]:
        """Get overall learning progress for user."""
        try:
            # Aggregate topics from all sessions
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$topics_covered"},
                {"$group": {
                    "_id": "$topics_covered",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            cursor = self.db.conversation_states.aggregate(pipeline)
            topics = await cursor.to_list(length=10)
            
            return {
                "top_topics": [{"topic": t["_id"], "count": t["count"]} for t in topics],
                "total_sessions": await self.db.conversation_states.count_documents({"user_id": user_id})
            }
        except Exception as e:
            logger.warning(f"Failed to get learning progress: {e}")
            return {"top_topics": [], "total_sessions": 0}

