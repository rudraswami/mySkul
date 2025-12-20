"""
ConversationStateManager - BEHAVIORAL Conversation Intelligence
================================================================

This is NOT passive data storage. This is the DECISION-MAKING context
that drives how agents behave, what actions they take, and how they
maintain conversational continuity.

BEHAVIORAL STATE FIELDS:
- conversation_phase: Controls what kind of response is appropriate
- intent_confidence: Increases on clarification, affects action decisions
- pending_action: What action we're waiting to complete after clarification
- emotional_signal: Drives tone and empathy level
- response_mode: friend/mentor/listener/guide - how agent should behave

CORE PRINCIPLE:
State influences routing, tone, and action.
State can OVERRIDE intent classifier.
If pending_action exists and user clarifies → ACT, don't re-classify.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class ConversationPhase(Enum):
    """Conversation phases that control response behavior"""
    FIRST_TURN = "first_turn"           # Only time capability menus are allowed
    ACTIVE = "active"                   # Normal conversation flow
    CLARIFYING = "clarifying"           # AI asked clarifying question, awaiting answer
    ACTION_PENDING = "action_pending"   # User expressed intent, action in progress
    EMOTIONAL_SUPPORT = "emotional"     # User needs empathy, not academics


class ResponseMode(Enum):
    """How the agent should behave in responses"""
    MENTOR = "mentor"       # Teaching, explaining
    FRIEND = "friend"       # Casual, warm, supportive
    LISTENER = "listener"   # Empathetic, acknowledging
    GUIDE = "guide"         # Directing, planning


class ConversationStateManager:
    """
    BEHAVIORAL Conversation State Manager.
    
    This is NOT just data storage. This drives:
    - Routing decisions (state can override classifier)
    - Response tone and style
    - Whether to ask or act
    - Conversational continuity
    
    CORE RULE: If pending_action exists and user clarifies → 
               Execute action immediately, don't re-route.
    """
    
    def __init__(self, db):
        self.db = db
        self._cache: Dict[str, Dict] = {}  # In-memory cache for speed
    
    async def get_state(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get current conversation state with all behavioral fields.
        """
        cache_key = f"{user_id}_{session_id}"
        
        # Check cache first (memory for speed)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load from database (DB for persistence)
        try:
            state_doc = await self.db.conversation_states.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            if state_doc:
                state = self._doc_to_state(state_doc)
                self._cache[cache_key] = state
                return state
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
        
        # Return default state - FIRST_TURN phase
        default_state = self._create_default_state()
        self._cache[cache_key] = default_state
        return default_state
    
    def _doc_to_state(self, doc: Dict) -> Dict[str, Any]:
        """Convert database document to state dict with all fields."""
        return {
            # ========== BEHAVIORAL STATE (NEW) ==========
            "conversation_phase": doc.get("conversation_phase", ConversationPhase.FIRST_TURN.value),
            "intent_confidence": doc.get("intent_confidence", 0.0),
            "pending_action": doc.get("pending_action"),  # {type, params, clarification_asked}
            "emotional_signal": doc.get("emotional_signal", "neutral"),
            "response_mode": doc.get("response_mode", ResponseMode.MENTOR.value),
            "last_user_intent": doc.get("last_user_intent"),  # Structured intent
            "clarification_count": doc.get("clarification_count", 0),  # Track re-asks
            
            # ========== CONTEXT STATE (EXISTING) ==========
            "current_topic": doc.get("current_topic"),
            "current_concept": doc.get("current_concept"),
            "current_subject": doc.get("current_subject"),
            "difficulty_level": doc.get("difficulty_level", 0.5),
            "confusion_level": doc.get("confusion_level", 0),
            "topics_covered": doc.get("topics_covered", []),
            "question_count": doc.get("question_count", 0),
            "session_start": doc.get("session_start"),
            "last_message_time": doc.get("last_message_time"),
        }
    
    def _create_default_state(self) -> Dict[str, Any]:
        """Create default state for new session."""
        now = datetime.now(timezone.utc).isoformat()
        return {
            # ========== BEHAVIORAL STATE ==========
            "conversation_phase": ConversationPhase.FIRST_TURN.value,
            "intent_confidence": 0.0,
            "pending_action": None,
            "emotional_signal": "neutral",
            "response_mode": ResponseMode.MENTOR.value,
            "last_user_intent": None,
            "clarification_count": 0,
            
            # ========== CONTEXT STATE ==========
            "current_topic": None,
            "current_concept": None,
            "current_subject": None,
            "difficulty_level": 0.5,
            "confusion_level": 0,
            "topics_covered": [],
            "question_count": 0,
            "session_start": now,
            "last_message_time": now,
        }
    
    # ================================================================
    # BEHAVIORAL STATE METHODS
    # ================================================================
    
    async def set_pending_action(
        self,
        user_id: str,
        session_id: str,
        action_type: str,
        params: Dict[str, Any],
        clarification_question: str
    ) -> None:
        """
        Set a pending action when we need clarification.
        
        When user responds, we should COMPLETE this action, not re-classify.
        """
        state = await self.get_state(user_id, session_id)
        
        state["pending_action"] = {
            "type": action_type,
            "params": params,
            "clarification_asked": clarification_question,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        state["conversation_phase"] = ConversationPhase.ACTION_PENDING.value
        state["clarification_count"] = 0  # Reset on new action
        
        await self._save_state(user_id, session_id, state)
        logger.info(f"[State] Set pending_action: {action_type}")
    
    async def complete_pending_action(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get and clear the pending action.
        
        Returns the pending action so caller can execute it.
        """
        state = await self.get_state(user_id, session_id)
        pending = state.get("pending_action")
        
        if pending:
            # Clear the pending action
            state["pending_action"] = None
            state["conversation_phase"] = ConversationPhase.ACTIVE.value
            state["intent_confidence"] = min(1.0, state.get("intent_confidence", 0.5) + 0.3)
            
            await self._save_state(user_id, session_id, state)
            logger.info(f"[State] Completed pending_action: {pending.get('type')}")
            
        return pending
    
    async def escalate_intent_confidence(
        self,
        user_id: str,
        session_id: str,
        boost: float = 0.2
    ) -> float:
        """
        Increase intent confidence when user clarifies.
        
        Clarification = higher confidence = take action.
        """
        state = await self.get_state(user_id, session_id)
        
        new_confidence = min(1.0, state.get("intent_confidence", 0.5) + boost)
        state["intent_confidence"] = new_confidence
        
        await self._save_state(user_id, session_id, state)
        logger.info(f"[State] Intent confidence escalated to {new_confidence:.2f}")
        
        return new_confidence
    
    async def set_emotional_signal(
        self,
        user_id: str,
        session_id: str,
        signal: str,
        response_mode: str = None
    ) -> None:
        """
        Set emotional signal and optionally response mode.
        """
        state = await self.get_state(user_id, session_id)
        
        state["emotional_signal"] = signal
        if response_mode:
            state["response_mode"] = response_mode
        
        # If emotional, switch to emotional support phase
        if signal in ["sad", "anxious", "frustrated", "lonely", "stressed"]:
            state["conversation_phase"] = ConversationPhase.EMOTIONAL_SUPPORT.value
            state["response_mode"] = ResponseMode.LISTENER.value
        
        await self._save_state(user_id, session_id, state)
    
    async def transition_phase(
        self,
        user_id: str,
        session_id: str,
        new_phase: str
    ) -> None:
        """
        Transition conversation phase.
        """
        state = await self.get_state(user_id, session_id)
        old_phase = state.get("conversation_phase")
        state["conversation_phase"] = new_phase
        
        await self._save_state(user_id, session_id, state)
        logger.info(f"[State] Phase transition: {old_phase} -> {new_phase}")
    
    def is_first_turn(self, state: Dict[str, Any]) -> bool:
        """Check if this is the first turn (capability menus allowed)."""
        return state.get("conversation_phase") == ConversationPhase.FIRST_TURN.value
    
    def has_pending_action(self, state: Dict[str, Any]) -> bool:
        """Check if there's a pending action waiting for clarification."""
        return state.get("pending_action") is not None
    
    def should_act_immediately(self, state: Dict[str, Any]) -> bool:
        """
        Determine if we should act immediately vs ask clarification.
        
        ACT if:
        - Intent confidence >= 0.7
        - OR pending_action exists (user clarified)
        - OR conversation_phase is ACTION_PENDING
        """
        if state.get("pending_action"):
            return True
        if state.get("conversation_phase") == ConversationPhase.ACTION_PENDING.value:
            return True
        if state.get("intent_confidence", 0) >= 0.7:
            return True
        return False
    
    # ================================================================
    # EXISTING METHODS (ENHANCED)
    # ================================================================
    
    async def update_state(
        self,
        user_id: str,
        session_id: str,
        question: str,
        response: str,
        subject: str = None,
        intent: str = None,
        intent_confidence: float = None,
        emotional_signal: str = None
    ) -> None:
        """
        Update conversation state after an exchange.
        
        This method handles:
        - Phase transitions (first_turn -> active)
        - Intent tracking and confidence
        - Topic/concept extraction
        - Emotional signal updates
        """
        state = await self.get_state(user_id, session_id)
        
        # ================================================================
        # PHASE TRANSITION: First turn -> Active
        # ================================================================
        if state.get("conversation_phase") == ConversationPhase.FIRST_TURN.value:
            state["conversation_phase"] = ConversationPhase.ACTIVE.value
            logger.info("[State] Transitioned from FIRST_TURN to ACTIVE")
        
        # ================================================================
        # INTENT AND CONFIDENCE TRACKING
        # ================================================================
        if intent:
            state["last_user_intent"] = intent
        
        if intent_confidence is not None:
            state["intent_confidence"] = intent_confidence
        
        # ================================================================
        # EMOTIONAL SIGNAL
        # ================================================================
        if emotional_signal:
            state["emotional_signal"] = emotional_signal
            # Auto-set response mode based on emotion
            if emotional_signal in ["sad", "anxious", "frustrated", "lonely", "stressed"]:
                state["response_mode"] = ResponseMode.LISTENER.value
            elif emotional_signal in ["excited", "curious", "positive"]:
                state["response_mode"] = ResponseMode.FRIEND.value
            else:
                state["response_mode"] = ResponseMode.MENTOR.value
        
        # ================================================================
        # TOPIC AND CONCEPT EXTRACTION
        # ================================================================
        topic = self._extract_topic(question, subject)
        concept = self._extract_concept(question)
        
        state["question_count"] = state.get("question_count", 0) + 1
        state["last_message_time"] = datetime.now(timezone.utc).isoformat()
        
        if topic:
            state["current_topic"] = topic
            if topic not in state.get("topics_covered", []):
                state["topics_covered"] = state.get("topics_covered", []) + [topic]
        
        if concept:
            state["current_concept"] = concept
        
        if subject:
            state["current_subject"] = subject
        
        # ================================================================
        # CONFUSION DETECTION
        # ================================================================
        confusion_indicators = [
            'confused', "don't understand", 'help', 'stuck', 
            'what do you mean', 'explain again', 'still not clear',
            'no i mean', 'not that', 'i meant'
        ]
        q_lower = question.lower()
        
        if any(ind in q_lower for ind in confusion_indicators):
            state["confusion_level"] = min(1.0, state.get("confusion_level", 0) + 0.3)
            
            # CRITICAL: "no i mean" is a CLARIFICATION, not confusion
            # This should INCREASE confidence and trigger action
            if any(x in q_lower for x in ['no i mean', 'not that', 'i meant', 'actually']):
                state["intent_confidence"] = min(1.0, state.get("intent_confidence", 0.5) + 0.3)
                logger.info("[State] Clarification detected - confidence increased")
        else:
            state["confusion_level"] = max(0, state.get("confusion_level", 0) - 0.1)
        
        # ================================================================
        # PERSIST STATE
        # ================================================================
        await self._save_state(user_id, session_id, state)
    
    async def _save_state(
        self,
        user_id: str,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Save state to both cache and database.
        """
        cache_key = f"{user_id}_{session_id}"
        
        # Update cache (memory)
        self._cache[cache_key] = state
        
        # Persist to database
        try:
            await self.db.conversation_states.update_one(
                {"user_id": user_id, "session_id": session_id},
                {"$set": {
                    **state,
                    "user_id": user_id,
                    "session_id": session_id,
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
    
    async def is_truly_first_turn(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """
        Check if this is truly the first turn based on DB message count.
        
        This is the ONLY reliable way to detect first turn.
        Message history can be trimmed, frontend flags are fragile.
        DB is the source of truth.
        """
        try:
            # Check if any messages exist in this session
            message_count = await self.db.session_messages.count_documents({
                "session_id": session_id
            })
            
            is_first = message_count == 0
            logger.info(f"[State] is_truly_first_turn: {is_first} (messages: {message_count})")
            return is_first
            
        except Exception as e:
            logger.warning(f"Failed to check first turn: {e}")
            # Fallback to state-based check
            state = await self.get_state(user_id, session_id)
            return state.get("question_count", 0) == 0
    
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

