"""
ContextPack - Single Source of Truth for ALL Agent/Pipeline Context
====================================================================

This is the CORE of the Cognitive OS architecture.

PHILOSOPHY:
- Agents receive ContextPack, NOT raw transcripts
- LLM is a reasoning engine, NOT the decision-maker
- All pipelines get IDENTICAL context structure
- Memory is in the SYSTEM, not in prompts

WHAT THIS REPLACES:
- Scattered context building in each pipeline
- Raw message_history passed to LLM
- Inconsistent context between pipelines

REUSES EXISTING SERVICES:
- MemoryIntegrationService.get_enhanced_context()
- StudentIntelligenceHub.get_magic_context()
- ConversationStateManager.get_state()
- ContinuityEngine
- MasteryTracker
- SpacedRepetitionEngine

Author: Druv AI Engineering
"""

import logging
import uuid
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ConversationPhase(Enum):
    """Conversation phases that control agent behavior"""
    FIRST_TURN = "first_turn"
    ACTIVE = "active"
    CLARIFYING = "clarifying"
    ACTION_PENDING = "action_pending"
    EMOTIONAL_SUPPORT = "emotional"


class ResponseMode(Enum):
    """How agents should respond"""
    MENTOR = "mentor"
    FRIEND = "friend"
    LISTENER = "listener"
    GUIDE = "guide"
    CHALLENGER = "challenger"


class MasteryBucket(Enum):
    """Student mastery level classification"""
    NOVICE = "novice"           # 0-20
    BEGINNER = "beginner"       # 21-40
    DEVELOPING = "developing"   # 41-60
    PROFICIENT = "proficient"   # 61-80
    EXPERT = "expert"           # 81-100


class EventType(Enum):
    """Types of learning events to track"""
    CONFUSION = "confusion"
    SUBJECT_SWITCH = "subject_switch"
    MASTERY_DELTA = "mastery_delta"
    EMOTIONAL_SIGNAL = "emotional_signal"
    PLAN_CREATED = "plan_created"
    ACTION_COMPLETED = "action_completed"
    SESSION_END = "session_end"
    TOPIC_ASKED = "topic_asked"
    ACKNOWLEDGEMENT = "acknowledgement"


# =============================================================================
# LEARNING EVENT - Structured event for memory
# =============================================================================

@dataclass
class LearningEvent:
    """
    Structured event for the learning memory system.
    
    This replaces chat transcripts for intelligence purposes.
    """
    event_type: EventType
    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


# =============================================================================
# CONTEXT PACK - The Single Source of Truth
# =============================================================================

@dataclass
class ContextPack:
    """
    Single Source of Truth for ALL agent/pipeline context.
    
    EVERY pipeline receives this IDENTICAL structure.
    Agents make decisions based on this, not raw data.
    
    CORE PRINCIPLE:
    - Structured context, not transcripts
    - Agent-ready format
    - All intelligence in one place
    """
    
    # =========== IDENTITY ===========
    user_id: str
    session_id: str
    request_id: str  # Correlation ID for tracing
    
    # =========== CONVERSATION STATE (Behavioral) ===========
    conversation_phase: str = "active"
    pending_action: Optional[Dict[str, Any]] = None
    is_first_turn: bool = False
    response_mode: str = "mentor"
    emotional_signal: str = "neutral"
    
    # =========== MASTERY SNAPSHOT ===========
    current_topic: str = ""
    current_topic_mastery: int = 0
    mastery_bucket: str = "beginner"
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    
    # =========== SESSION CONTEXT ===========
    subject: str = "General"
    exam_name: str = ""
    days_to_exam: Optional[int] = None
    exam_urgency: str = "normal"
    student_name: str = ""
    
    # =========== CONTINUITY (Minimal, NOT full transcript) ===========
    is_continuation: bool = False
    previous_topic: str = ""
    last_n_messages: List[Dict[str, Any]] = field(default_factory=list)  # Last 5 only
    last_n_events: List[Dict[str, Any]] = field(default_factory=list)    # Last 5 events
    
    # =========== LAST TASK TRACKING (Phase C Continuity Fix) ===========
    # Enables proper "okay" / "got it" continuation by knowing what we last did
    last_output_type: str = ""  # study_plan, problem_solution, explanation, emotional_support, etc.
    last_task_type: str = ""    # deliverable, explanation, conversation, emotional
    last_assistant_message: str = ""  # Truncated last response (max 500 chars)
    awaiting_continuation: bool = False  # True if last response was deliverable expecting ack
    
    # =========== SPACED REPETITION ===========
    due_reviews: List[str] = field(default_factory=list)
    
    # =========== PERSISTENT MEMORY (Real Student Data) ===========
    # These fields contain REAL memory from the database, not fake data
    relevant_memories: List[Dict[str, Any]] = field(default_factory=list)  # Semantic search results
    past_struggles: List[str] = field(default_factory=list)  # Topics student struggled with before
    what_helped_before: str = ""  # What explanations worked
    learning_preference: str = ""  # visual, step_by_step, intuitive, etc.
    preferred_analogies: List[str] = field(default_factory=list)  # cricket, cooking, etc.
    
    # =========== PROACTIVE INTELLIGENCE ===========
    magic_prompts: List[str] = field(default_factory=list)
    needs_encouragement: bool = False
    current_streak: int = 0
    recent_achievement: str = ""
    
    # =========== AGENT DECISION AIDS ===========
    recommended_depth: str = "medium"  # surface, medium, deep, expert
    explanation_style: str = "balanced"  # intuitive, balanced, rigorous
    include_basics: bool = False
    include_advanced: bool = False
    
    # =========== METADATA ===========
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    db_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for passing to agents"""
        return {
            # Identity
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            
            # State
            "conversation_phase": self.conversation_phase,
            "pending_action": self.pending_action,
            "is_first_turn": self.is_first_turn,
            "response_mode": self.response_mode,
            "emotional_signal": self.emotional_signal,
            
            # Mastery
            "current_topic": self.current_topic,
            "current_topic_mastery": self.current_topic_mastery,
            "mastery_bucket": self.mastery_bucket,
            "weak_areas": self.weak_areas,
            "strong_areas": self.strong_areas,
            
            # Session
            "subject": self.subject,
            "exam_name": self.exam_name,
            "days_to_exam": self.days_to_exam,
            "exam_urgency": self.exam_urgency,
            "student_name": self.student_name,
            
            # Continuity
            "is_continuation": self.is_continuation,
            "previous_topic": self.previous_topic,
            "last_n_messages": self.last_n_messages,
            "last_n_events": self.last_n_events,
            
            # Last Task Tracking (Continuity v2)
            "last_output_type": self.last_output_type,
            "last_task_type": self.last_task_type,
            "last_assistant_message": self.last_assistant_message,
            "awaiting_continuation": self.awaiting_continuation,
            
            # Spaced Rep
            "due_reviews": self.due_reviews,
            
            # Persistent Memory (Real Data)
            "relevant_memories": self.relevant_memories,
            "past_struggles": self.past_struggles,
            "what_helped_before": self.what_helped_before,
            "learning_preference": self.learning_preference,
            "preferred_analogies": self.preferred_analogies,
            
            # Proactive
            "magic_prompts": self.magic_prompts,
            "needs_encouragement": self.needs_encouragement,
            "current_streak": self.current_streak,
            "recent_achievement": self.recent_achievement,
            
            # Agent Aids
            "recommended_depth": self.recommended_depth,
            "explanation_style": self.explanation_style,
            "include_basics": self.include_basics,
            "include_advanced": self.include_advanced,
            
            # Meta
            "created_at": self.created_at.isoformat(),
            "db_available": self.db_available
        }
    
    def get_conversation_summary(self) -> str:
        """
        Get a MINIMAL conversation summary for LLM context.
        NOT the full transcript - just enough for continuity.
        """
        if not self.last_n_messages:
            return ""
        
        summary_parts = []
        for msg in self.last_n_messages[-5:]:  # Max 5 messages
            role = "Student" if msg.get("role") == "user" else "Druv"
            content = msg.get("content", "")[:150]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    def get_agent_context_prompt(self) -> str:
        """
        Generate a STRUCTURED context prompt for agents.
        This is what the LLM sees - not raw history.
        """
        prompt_parts = []
        
        # Student identity
        if self.student_name:
            prompt_parts.append(f"Student: {self.student_name}")
        
        # Mastery context
        if self.current_topic:
            prompt_parts.append(f"Current topic: {self.current_topic} (mastery: {self.current_topic_mastery}%, level: {self.mastery_bucket})")
        
        # Exam context
        if self.exam_name and self.days_to_exam is not None:
            prompt_parts.append(f"Exam: {self.exam_name} in {self.days_to_exam} days ({self.exam_urgency} urgency)")
        
        # Emotional context
        if self.emotional_signal != "neutral":
            prompt_parts.append(f"Emotional state: {self.emotional_signal}")
        if self.needs_encouragement:
            prompt_parts.append("Note: Student needs encouragement")
        
        # Continuity
        if self.is_continuation and self.previous_topic:
            prompt_parts.append(f"Continuing from: {self.previous_topic}")
        
        # Weak areas
        if self.weak_areas:
            prompt_parts.append(f"Weak areas: {', '.join(self.weak_areas[:3])}")
        
        # Due reviews
        if self.due_reviews:
            prompt_parts.append(f"Due for review: {', '.join(self.due_reviews[:3])}")
        
        # =========== PERSISTENT MEMORY (Real Student Data) ===========
        # Past struggles - enables "Last time you struggled with..."
        if self.past_struggles:
            prompt_parts.append(f"Past struggles: {', '.join(self.past_struggles[:3])}")
        
        # What helped before - enables adaptive explanations
        if self.what_helped_before:
            prompt_parts.append(f"What helped before: {self.what_helped_before}")
        
        # Learning preference - enables "You usually prefer..."
        if self.learning_preference:
            prompt_parts.append(f"Learning style: {self.learning_preference}")
        
        # Preferred analogies
        if self.preferred_analogies:
            prompt_parts.append(f"Prefers analogies from: {', '.join(self.preferred_analogies[:3])}")
        
        # Relevant past memories
        if self.relevant_memories:
            memory_hints = [m.get('content', '')[:100] for m in self.relevant_memories[:3] if isinstance(m, dict)]
            if memory_hints:
                prompt_parts.append(f"Related past discussions:\n- " + "\n- ".join(memory_hints))
        
        # Recent conversation
        conv_summary = self.get_conversation_summary()
        if conv_summary:
            prompt_parts.append(f"\nRecent conversation:\n{conv_summary}")
        
        # Magic prompts
        if self.magic_prompts:
            prompt_parts.append(f"\nPersonalization hints:\n- " + "\n- ".join(self.magic_prompts[:5]))
        
        return "\n".join(prompt_parts) if prompt_parts else "New conversation, no prior context."


# =============================================================================
# CONTEXT PACK BUILDER - Assembles from existing services
# =============================================================================

class ContextPackBuilder:
    """
    Builds ContextPack by orchestrating existing services.
    
    REUSES (does NOT duplicate):
    - ConversationStateManager
    - MemoryIntegrationService
    - StudentIntelligenceHub
    - MasteryTracker
    - ContinuityEngine
    
    This is the SINGLE PLACE where context is assembled.
    """
    
    def __init__(self, db):
        self.db = db
        self._state_manager = None
        self._memory_integration = None
        self._intelligence_hub = None
        self._mastery_tracker = None
        self._continuity_engine = None
    
    # =========== LAZY LOADING (reuse existing services) ===========
    
    @property
    def state_manager(self):
        if not self._state_manager:
            from services.conversation_state import ConversationStateManager
            self._state_manager = ConversationStateManager(self.db)
        return self._state_manager
    
    @property
    def memory_integration(self):
        if not self._memory_integration:
            try:
                from services.memory_integration import MemoryIntegrationService
                import os
                self._memory_integration = MemoryIntegrationService(
                    self.db, 
                    os.environ.get('OPENAI_API_KEY')
                )
            except Exception as e:
                logger.warning(f"MemoryIntegration not available: {e}")
        return self._memory_integration
    
    @property
    def intelligence_hub(self):
        if not self._intelligence_hub:
            try:
                from services.student_intelligence_hub import get_student_intelligence_hub
                self._intelligence_hub = get_student_intelligence_hub(self.db)
            except Exception as e:
                logger.warning(f"StudentIntelligenceHub not available: {e}")
        return self._intelligence_hub
    
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
    
    # =========== MAIN BUILD METHOD ===========
    
    async def build(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str = "General",
        message_history: List[Dict] = None,
        existing_context: Dict[str, Any] = None
    ) -> ContextPack:
        """
        Build a complete ContextPack by orchestrating existing services.
        
        This is THE ONLY PLACE where context is assembled.
        All pipelines call this, all get identical structure.
        
        TIMEOUT STRATEGY:
        - Core data (state, mastery): MUST complete (5s timeout)
        - Enrichment (magic, proactive): Best effort (3s timeout)
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"📦 Building ContextPack | request_id={request_id} | user={user_id[:8]}...")
        
        # Initialize pack with defaults
        pack = ContextPack(
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            subject=subject,
            db_available=self.db is not None
        )
        
        # Track what we've loaded for logging
        loaded_components = []
        
        try:
            # ============================================================
            # SIMPLIFIED MEMORY LOADING - PRODUCTION GRADE
            # ============================================================
            # Single-level parallelism with individual timeouts
            # Each component has 1s timeout - fast fail, fast fallback
            # Total time: max(all) ≤ 1.5s (not cumulative)
            # ============================================================
            
            async def load_conversation_state():
                """Load conversation state - 1s timeout"""
                try:
                    state = await asyncio.wait_for(
                        self.state_manager.get_state(user_id, session_id),
                        timeout=1.0
                    )
                    return {
                        'success': True,
                        'conversation_phase': state.get('conversation_phase', 'active'),
                        'pending_action': state.get('pending_action'),
                        'response_mode': state.get('response_mode', 'mentor'),
                        'emotional_signal': state.get('emotional_signal', 'neutral'),
                        'is_first_turn': state.get('is_first_turn', True)
                    }
                except asyncio.TimeoutError:
                    logger.debug("State load timeout - using defaults")
                    return {'success': False}
                except Exception as e:
                    logger.debug(f"State load failed: {e}")
                    return {'success': False}
            
            
            async def load_message_history():
                """Load message history - 1s timeout (or use provided)"""
                if message_history:
                    return {'success': True, 'provided': True, 'messages': message_history[-5:]}
                
                if not self.memory_integration:
                    return {'success': False}
                
                try:
                    # Direct call to memory service with timeout
                    context = await asyncio.wait_for(
                        self.memory_integration.get_enhanced_context(
                            user_id=user_id,
                            session_id=session_id,
                            question=message,
                            subject=subject
                        ),
                        timeout=1.5  # Strict 1.5s timeout
                    )
                    
                    recent = context.get('recent_context', {})
                    if isinstance(recent, dict):
                        messages = recent.get('messages', [])[-5:]
                    elif isinstance(recent, list):
                        messages = recent[-5:]
                    else:
                        messages = []
                    
                    continuity = context.get('continuity', {})
                    weak_topics = context.get('weak_topics', [])
                    
                    return {
                        'success': True,
                        'messages': messages,
                        'current_topic': context.get('current_topic', ''),
                        'previous_topic': (
                            continuity.get('previous_topic', '') or
                            continuity.get('last_topic', '') or
                            (weak_topics[0] if weak_topics else '')
                        ),
                        'is_continuation': context.get('is_continuation', False),
                        'student_name': context.get('user_name', ''),
                        'relevant_memories': context.get('relevant_memories', [])
                    }
                except asyncio.TimeoutError:
                    logger.debug("Message history timeout - using defaults")
                    return {'success': False}
                except Exception as e:
                    logger.debug(f"Message history load failed: {e}")
                    return {'success': False}
            
            # ============================================================
            # STEP 2b: LAST TASK TRACKING (Continuity v2 - Phase C Fix)
            # ============================================================
            # This enables proper "okay"/"got it" continuation
            try:
                from core.config import settings
                if settings.ENABLE_CONTINUITY_TRACKING and self.db:
                    last_task_info = await self._get_last_task_info(user_id, session_id)
                    if last_task_info:
                        pack.last_output_type = last_task_info.get('output_type', '')
                        pack.last_task_type = last_task_info.get('task_type', '')
                        pack.last_assistant_message = last_task_info.get('message', '')[:500]  # Truncate
                        pack.awaiting_continuation = last_task_info.get('awaiting_continuation', False)
                        loaded_components.append("last_task")
                        logger.debug(f"   ✓ Last task: type={pack.last_output_type}, awaiting_ack={pack.awaiting_continuation}")
            except Exception as e:
                logger.debug(f"Last task tracking failed (non-critical): {e}")
            
            
            async def load_student_profile():
                """Load student profile - 1s timeout"""
                if not self.memory_integration:
                    return {'success': False}
                
                try:
                    # Use timeout for profile fetch
                    profile = await asyncio.wait_for(
                        self.memory_integration.memory_service.get_student_profile(user_id),
                        timeout=1.0
                    )
                    
                    what_helped = ""
                    if profile is not None:
                        if profile.get('preferred_explanation'):
                            what_helped = f"{profile.get('preferred_explanation')} explanations"
                        if profile.get('pacing'):
                            what_helped += f", {profile.get('pacing')} pacing"
                    
                    return {
                        'success': True,
                        'learning_preference': profile.get('preferred_explanation', '') if profile is not None else '',
                        'relevant_memories': [],  # Skip slow semantic search here
                        'preferred_analogies': profile.get('preferred_analogies', []) if profile is not None else [],
                        'what_helped_before': what_helped
                    }
                except asyncio.TimeoutError:
                    logger.debug("Student profile timeout - using defaults")
                    return {'success': False}
                except Exception as e:
                    logger.debug(f"Student profile load failed: {e}")
                    return {'success': False}
            
            
            async def load_mastery_data():
                """Load mastery data - 1s timeout"""
                try:
                    topic = self._extract_topic(message, subject)
                    
                    # Parallel fetch with timeout
                    mastery_task = self.mastery_tracker.get_mastery_level(user_id, topic)
                    weak_task = self.mastery_tracker.get_weak_topics(user_id, threshold=40)
                    
                    try:
                        mastery, weak_topics = await asyncio.wait_for(
                            asyncio.gather(mastery_task, weak_task),
                            timeout=1.0
                        )
                    except asyncio.TimeoutError:
                        return {'success': False}
                    
                    weak_areas = [t.get('topic', '') for t in weak_topics[:5]]
                    
                    # Use defaults if no weak areas
                    if not weak_areas:
                        weak_areas = self._get_default_weak_areas(subject, pack.exam_name)
                    
                    return {
                        'success': True,
                        'topic': topic,
                        'mastery': mastery,
                        'mastery_bucket': self._get_mastery_bucket(mastery),
                        'weak_areas': weak_areas
                    }
                except Exception as e:
                    logger.debug(f"Mastery load failed: {e}")
                    return {'success': False}
            
            
            async def load_magic_context():
                """Load magic context - 1s timeout"""
                if not self.intelligence_hub:
                    return {'success': False}
                
                try:
                    magic = await asyncio.wait_for(
                        self.intelligence_hub.get_magic_context(
                            user_id=user_id,
                            session_id=session_id,
                            current_query=message,
                            detected_topic=pack.current_topic
                        ),
                        timeout=1.0
                    )
                    
                    return {
                        'success': True,
                        'exam_name': magic.exam_name or "",
                        'days_to_exam': magic.days_to_exam,
                        'exam_urgency': magic.exam_urgency.value if magic.exam_urgency else "normal",
                        'current_streak': magic.current_streak or 0,
                        'recent_achievement': magic.recent_achievement or "",
                        'needs_encouragement': magic.needs_encouragement or False,
                        'due_reviews': magic.due_reviews[:5] if magic.due_reviews else [],
                        'magic_prompts': magic.get_magic_prompts()[:5],
                        'student_name': magic.student_name
                    }
                except asyncio.TimeoutError:
                    logger.debug("Magic context timeout - using defaults")
                    return {'success': False}
                except Exception as e:
                    logger.debug(f"Magic context load failed: {e}")
                    return {'success': False}
            
            # ============================================================
            # LAUNCH ALL MEMORY LOADS IN PARALLEL - FAST PATH
            # ============================================================
            # Each function has 1-1.5s internal timeout
            # Outer timeout is 2.5s safety net (not 5s)
            # Total max time: 2.5s (not cumulative since parallel)
            # ============================================================
            try:
                start_time = time.time()
                
                # Create all tasks
                tasks = [
                    load_conversation_state(),
                    load_message_history(),
                    load_student_profile(),
                    load_mastery_data(),
                    load_magic_context()
                ]
                
                # 2.5s timeout - functions have internal 1s timeouts
                # FIX: Handle CancelledError to prevent "_GatheringFuture never retrieved"
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=2.5
                    )
                except asyncio.CancelledError:
                    # Client disconnected during memory load - graceful fallback
                    logger.info("ContextPack build cancelled (client disconnect), using fast defaults")
                    results = [{'success': False}] * 5
                
                # Unpack results
                state_result, history_result, profile_result, mastery_result, magic_result = results
                
                load_time = time.time() - start_time
                logger.info(f"⚡ Parallel memory load completed in {load_time:.2f}s | request_id={request_id}")
                
                # Apply results to pack (with safe fallbacks)
                
                # 1. Conversation State
                if isinstance(state_result, dict) and state_result.get('success'):
                    pack.conversation_phase = state_result['conversation_phase']
                    pack.pending_action = state_result.get('pending_action')
                    pack.response_mode = state_result['response_mode']
                    pack.emotional_signal = state_result['emotional_signal']
                    pack.is_first_turn = state_result['is_first_turn']
                    loaded_components.append("state")
                
                # 2. Message History
                if isinstance(history_result, dict) and history_result.get('success'):
                    if history_result.get('provided'):
                        pack.last_n_messages = history_result['messages']
                        loaded_components.append("messages_provided")
                    else:
                        pack.last_n_messages = history_result.get('messages', [])
                        pack.current_topic = history_result.get('current_topic', '')
                        pack.previous_topic = history_result.get('previous_topic', '')
                        pack.is_continuation = history_result.get('is_continuation', False)
                        pack.student_name = history_result.get('student_name', '')
                        pack.relevant_memories = history_result.get('relevant_memories', [])
                        loaded_components.append("memory")
                
                # 3. Student Profile
                if isinstance(profile_result, dict) and profile_result.get('success'):
                    pack.learning_preference = profile_result.get('learning_preference', '')
                    if not pack.relevant_memories:  # Don't override if already set
                        pack.relevant_memories = profile_result.get('relevant_memories', [])
                    pack.preferred_analogies = profile_result.get('preferred_analogies', [])
                    pack.what_helped_before = profile_result.get('what_helped_before', '')
                    loaded_components.append("student_profile")
                
                # 4. Mastery Data
                if isinstance(mastery_result, dict) and mastery_result.get('success'):
                    if not pack.current_topic:  # Don't override if already set
                        pack.current_topic = mastery_result.get('topic', '')
                    pack.current_topic_mastery = mastery_result.get('mastery', 0)
                    pack.mastery_bucket = mastery_result.get('mastery_bucket', 'beginner')
                    pack.weak_areas = mastery_result.get('weak_areas', [])
                    pack.past_struggles = pack.weak_areas  # Use weak areas as struggles
                    loaded_components.append("mastery")
                
                # 5. Magic Context
                if isinstance(magic_result, dict) and magic_result.get('success'):
                    pack.exam_name = magic_result.get('exam_name', '')
                    pack.days_to_exam = magic_result.get('days_to_exam')
                    pack.exam_urgency = magic_result.get('exam_urgency', 'normal')
                    pack.current_streak = magic_result.get('current_streak', 0)
                    pack.recent_achievement = magic_result.get('recent_achievement', '')
                    pack.needs_encouragement = magic_result.get('needs_encouragement', False)
                    pack.due_reviews = magic_result.get('due_reviews', [])
                    pack.magic_prompts = magic_result.get('magic_prompts', [])
                    if magic_result.get('student_name'):
                        pack.student_name = magic_result['student_name']
                    loaded_components.append("magic")
                
                logger.info(f"✅ Loaded components: {', '.join(loaded_components)} | request_id={request_id}")
                
            except asyncio.TimeoutError:
                logger.warning(f"⚡ Memory load timeout (>2.5s), using fast defaults | request_id={request_id}")
            except Exception as e:
                logger.warning(f"⚠️ Parallel memory load failed: {e} | request_id={request_id}")
            
            # ============================================================
            # STEP 5: RECENT EVENTS (if available)
            # ============================================================
            try:
                events = await self._get_recent_events(user_id, session_id, limit=5)
                pack.last_n_events = events
                if events:
                    loaded_components.append("events")
            except Exception as e:
                logger.debug(f"Events not available: {e}")
            
            # ============================================================
            # STEP 6: DEPTH RECOMMENDATION (from CognitiveOrchestrator logic)
            # ============================================================
            pack.recommended_depth = self._calculate_depth(pack.mastery_bucket, pack.is_first_turn)
            pack.include_basics = pack.mastery_bucket in ['novice', 'beginner']
            pack.include_advanced = pack.mastery_bucket in ['proficient', 'expert']
            
            # ============================================================
            # STEP 7: MERGE ANY EXISTING CONTEXT
            # ============================================================
            if existing_context:
                # Preserve any fields from existing context that we didn't load
                if existing_context.get('student_profile'):
                    profile = existing_context['student_profile']
                    if not pack.student_name:
                        pack.student_name = profile.get('name', '')
                    if not pack.exam_name:
                        pack.exam_name = profile.get('exam_type', '')
                
                if existing_context.get('db'):
                    pack.db_available = True
            
            # Log what we loaded
            logger.info(f"📦 ContextPack built | request_id={request_id} | "
                       f"components=[{', '.join(loaded_components)}] | "
                       f"topic={pack.current_topic} | mastery={pack.current_topic_mastery}% | "
                       f"phase={pack.conversation_phase}")
            
        except Exception as e:
            logger.error(f"❌ ContextPack build failed: {e} | request_id={request_id}")
            # Return pack with whatever we have
        
        return pack
    
    # =========== HELPER METHODS ===========
    
    def _extract_topic(self, message: str, subject: str) -> str:
        """Extract main topic from message"""
        # Simple extraction - can be enhanced
        topic = subject.lower().replace(' ', '_')
        
        # Check for common topic keywords
        keywords = {
            'derivative': 'calculus_derivatives',
            'integral': 'calculus_integrals',
            'momentum': 'physics_momentum',
            'force': 'physics_forces',
            'equation': 'math_equations',
            'chemical': 'chemistry_basics',
            'organic': 'organic_chemistry',
            'thermodynamic': 'thermodynamics',
            'kinematics': 'physics_kinematics',
            'electro': 'electromagnetism'
        }
        
        msg_lower = message.lower()
        for keyword, topic_name in keywords.items():
            if keyword in msg_lower:
                return topic_name
        
        return topic if topic else 'general_concept'
    
    def _get_mastery_bucket(self, mastery: int) -> str:
        """Convert mastery score to bucket"""
        if mastery <= 20:
            return MasteryBucket.NOVICE.value
        elif mastery <= 40:
            return MasteryBucket.BEGINNER.value
        elif mastery <= 60:
            return MasteryBucket.DEVELOPING.value
        elif mastery <= 80:
            return MasteryBucket.PROFICIENT.value
        else:
            return MasteryBucket.EXPERT.value
    
    def _calculate_depth(self, mastery_bucket: str, is_first_turn: bool) -> str:
        """Calculate recommended explanation depth"""
        if is_first_turn:
            return "medium"
        
        depth_map = {
            'novice': 'surface',
            'beginner': 'medium',
            'developing': 'medium',
            'proficient': 'deep',
            'expert': 'expert'
        }
        return depth_map.get(mastery_bucket, 'medium')
    
    def _get_default_weak_areas(self, subject: str, exam_name: str) -> List[str]:
        """
        Get default weak areas based on exam type and subject.
        
        This ensures new users get personalized defaults instead of empty lists.
        These are commonly challenging topics for each exam type.
        
        Args:
            subject: Current subject context
            exam_name: Exam type (JEE, NEET, CBSE, etc.)
        
        Returns:
            List of default weak area topics
        """
        exam_name_lower = (exam_name or "").lower()
        subject_lower = (subject or "").lower()
        
        # JEE-specific weak areas (most students struggle with)
        if "jee" in exam_name_lower:
            return [
                "calculus_integrals",
                "thermodynamics",
                "organic_chemistry_reactions",
                "coordinate_geometry",
                "electromagnetic_induction"
            ]
        
        # NEET-specific weak areas
        elif "neet" in exam_name_lower:
            return [
                "human_physiology",
                "organic_chemistry",
                "genetics",
                "plant_physiology",
                "cell_biology"
            ]
        
        # CBSE Board exam defaults by class
        elif "cbse" in exam_name_lower or "board" in exam_name_lower:
            return [
                "calculus_derivatives",
                "organic_chemistry",
                "electrostatics",
                "probability",
                "ray_optics"
            ]
        
        # Subject-specific defaults
        elif "physics" in subject_lower:
            return [
                "thermodynamics",
                "electromagnetism",
                "wave_optics",
                "rotational_mechanics",
                "modern_physics"
            ]
        elif "chemistry" in subject_lower:
            return [
                "organic_reactions",
                "chemical_equilibrium",
                "electrochemistry",
                "coordination_compounds",
                "thermochemistry"
            ]
        elif "math" in subject_lower:
            return [
                "calculus_integrals",
                "probability",
                "3d_geometry",
                "differential_equations",
                "complex_numbers"
            ]
        elif "biology" in subject_lower:
            return [
                "genetics",
                "cell_biology",
                "human_physiology",
                "ecology",
                "plant_biology"
            ]
        
        # Generic defaults for unknown context
        return [
            "fundamentals",
            "problem_solving",
            "conceptual_understanding"
        ]
    
    async def _get_recent_events(
        self, 
        user_id: str, 
        session_id: str, 
        limit: int = 5
    ) -> List[Dict]:
        """Get recent learning events from database"""
        try:
            cursor = self.db.learning_events.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit)
            
            events = []
            async for doc in cursor:
                events.append({
                    "type": doc.get("event_type"),
                    "data": doc.get("data", {}),
                    "timestamp": doc.get("timestamp")
                })
            
            return events
        except Exception:
            return []
    
    async def _get_last_task_info(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about the last assistant response for continuity.
        
        PHASE C FIX: This enables proper "okay"/"got it" continuation by
        understanding what we last delivered to the student.
        
        Returns:
            {
                'output_type': 'study_plan' | 'explanation' | 'problem_solution' | etc.,
                'task_type': 'deliverable' | 'explanation' | 'conversation' | 'emotional',
                'message': str (truncated to 500 chars),
                'awaiting_continuation': bool
            }
        """
        try:
            # Get the most recent assistant message from chat_messages
            last_message = await self.db.chat_messages.find_one(
                {
                    "session_id": session_id,
                    "user_id": user_id
                },
                sort=[("timestamp", -1)]
            )
            
            if last_message is None:
                return None
            
            # Extract the assistant response
            ai_response = last_message.get('ai_response', {})
            if isinstance(ai_response, str):
                # Plain text response
                message_text = ai_response
                output_type = 'explanation'
                task_type = 'explanation'
            else:
                # Structured response
                message_text = ai_response.get('main_response', '') or ai_response.get('content', '')
                # Get output_type from metadata if available
                metadata = ai_response.get('metadata', {})
                output_type = metadata.get('output_type', '') or ai_response.get('pipeline', '')
                
                # Determine task_type based on output_type
                deliverable_types = {'study_plan', 'problem_solution', 'quiz', 'schedule', 'timetable'}
                if output_type in deliverable_types or 'plan' in output_type.lower():
                    task_type = 'deliverable'
                elif output_type in {'emotional_support', 'motivation'}:
                    task_type = 'emotional'
                elif output_type in {'fast_response', 'chitchat', 'greeting'}:
                    task_type = 'conversation'
                else:
                    task_type = 'explanation'
            
            # Determine if we're awaiting continuation (deliverable just sent)
            awaiting_continuation = task_type == 'deliverable'
            
            return {
                'output_type': output_type,
                'task_type': task_type,
                'message': message_text[:500] if message_text else '',
                'awaiting_continuation': awaiting_continuation
            }
            
        except Exception as e:
            logger.debug(f"Failed to get last task info: {e}")
            return None


# =============================================================================
# EVENT LOGGER - Structured event logging
# =============================================================================

class EventLogger:
    """
    Logs structured learning events to database.
    
    EVENTS (not transcripts) enable:
    - Pattern detection without LLM
    - Confusion tracking
    - Subject switch history
    - Progress analytics
    """
    
    def __init__(self, db):
        self.db = db
    
    async def log_event(self, event: LearningEvent) -> bool:
        """Log a learning event to database"""
        try:
            await self.db.learning_events.insert_one(event.to_dict())
            logger.debug(f"📝 Event logged: {event.event_type.value} | user={event.user_id[:8]}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Event log failed: {e}")
            return False
    
    async def log_confusion(
        self, 
        user_id: str, 
        session_id: str, 
        topic: str, 
        count: int = 1
    ) -> bool:
        """Log confusion on a topic"""
        event = LearningEvent(
            event_type=EventType.CONFUSION,
            user_id=user_id,
            session_id=session_id,
            data={"topic": topic, "ask_count": count}
        )
        return await self.log_event(event)
    
    async def log_subject_switch(
        self,
        user_id: str,
        session_id: str,
        from_subject: str,
        to_subject: str
    ) -> bool:
        """Log subject switch"""
        event = LearningEvent(
            event_type=EventType.SUBJECT_SWITCH,
            user_id=user_id,
            session_id=session_id,
            data={"from": from_subject, "to": to_subject}
        )
        return await self.log_event(event)
    
    async def log_mastery_delta(
        self,
        user_id: str,
        session_id: str,
        topic: str,
        delta: int,
        new_mastery: int
    ) -> bool:
        """Log mastery change"""
        event = LearningEvent(
            event_type=EventType.MASTERY_DELTA,
            user_id=user_id,
            session_id=session_id,
            data={"topic": topic, "delta": delta, "new_mastery": new_mastery}
        )
        return await self.log_event(event)
    
    async def log_emotional_signal(
        self,
        user_id: str,
        session_id: str,
        emotion: str,
        trigger: str = None
    ) -> bool:
        """Log emotional signal"""
        event = LearningEvent(
            event_type=EventType.EMOTIONAL_SIGNAL,
            user_id=user_id,
            session_id=session_id,
            data={"emotion": emotion, "trigger": trigger}
        )
        return await self.log_event(event)
    
    async def log_plan_created(
        self,
        user_id: str,
        session_id: str,
        subject: str,
        duration: str = None,
        goals: List[str] = None
    ) -> bool:
        """Log study plan creation"""
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            user_id=user_id,
            session_id=session_id,
            data={"subject": subject, "duration": duration, "goals": goals or []}
        )
        return await self.log_event(event)
    
    async def log_acknowledgement(
        self,
        user_id: str,
        session_id: str,
        previous_topic: str
    ) -> bool:
        """Log acknowledgement (ok, great, good)"""
        event = LearningEvent(
            event_type=EventType.ACKNOWLEDGEMENT,
            user_id=user_id,
            session_id=session_id,
            data={"previous_topic": previous_topic}
        )
        return await self.log_event(event)


# =============================================================================
# HELPER: Get singleton instances
# =============================================================================

_context_pack_builder_cache: Dict[int, ContextPackBuilder] = {}
_event_logger_cache: Dict[int, EventLogger] = {}


def get_context_pack_builder(db) -> ContextPackBuilder:
    """Get or create ContextPackBuilder instance"""
    db_id = id(db)
    if db_id not in _context_pack_builder_cache:
        _context_pack_builder_cache[db_id] = ContextPackBuilder(db)
    return _context_pack_builder_cache[db_id]


def get_event_logger(db) -> EventLogger:
    """Get or create EventLogger instance"""
    db_id = id(db)
    if db_id not in _event_logger_cache:
        _event_logger_cache[db_id] = EventLogger(db)
    return _event_logger_cache[db_id]
