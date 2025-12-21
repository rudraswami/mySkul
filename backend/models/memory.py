"""
Memory System Data Models - MEMORY CONTRACT v2
===============================================

Production-ready models for persistent memory system.

MEMORY CONTRACT: ALL agents read/write the SAME canonical keys.
This ensures consistency across agents and sessions.

SCHEMA VERSION: 2
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


# =============================================================================
# SCHEMA VERSION - For migration compatibility
# =============================================================================
MEMORY_SCHEMA_VERSION = 2


# =============================================================================
# ENUMS
# =============================================================================

class FactType(str, Enum):
    """Types of memory facts"""
    CONCEPT_LEARNED = "concept_learned"
    MISCONCEPTION = "misconception"
    PREFERENCE = "preference"
    MASTERY_UPDATE = "mastery_update"
    ERROR_PATTERN = "error_pattern"
    STRENGTH = "strength"
    WEAKNESS = "weakness"


class MemoryEventType(str, Enum):
    """Types of memory events (write-ahead log)"""
    MASTERY_UPDATE = "mastery_update"
    PREFERENCE = "preference"
    GOAL = "goal"
    SESSION_SUMMARY = "session_summary"
    SAFETY_SIGNAL = "safety_signal"
    TOPIC_FOCUS = "topic_focus"
    CONFUSION_DETECTED = "confusion_detected"
    SUCCESS_CONFIRMED = "success_confirmed"


class MasteryLevel(str, Enum):
    """Mastery level buckets"""
    BEGINNER = "beginner"  # 0-30
    INTERMEDIATE = "intermediate"  # 31-70
    ADVANCED = "advanced"  # 71-100


class ExplanationStyle(str, Enum):
    """Preferred explanation styles"""
    VISUAL = "visual"
    STEP_BY_STEP = "step_by_step"
    ANALOGY = "analogy"
    FORMAL = "formal"
    CONCISE = "concise"
    DETAILED = "detailed"


class Pacing(str, Enum):
    """Learning pacing preferences"""
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class MemoryFact(BaseModel):
    """
    Individual memory fact stored for long-term recall
    """
    user_id: str
    fact_id: str
    fact_type: FactType
    
    # Content
    content: str
    embedding: Optional[List[float]] = None  # 1536-dim OpenAI embedding
    
    # Metadata
    topic: str
    subject: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    mastery_level: Optional[int] = Field(default=None, ge=0, le=100)
    
    # Timestamps
    created_at: datetime
    last_reinforced: Optional[datetime] = None
    reinforcement_count: int = 0
    
    # Spaced repetition
    next_review_at: Optional[datetime] = None
    review_interval_days: int = 1
    easiness_factor: float = 2.5  # SM-2 algorithm
    
    # Source
    source_session_id: Optional[str] = None
    source_message_id: Optional[str] = None
    
    # Flags
    is_active: bool = True
    is_verified: bool = False  # Professor verified this fact
    
    class Config:
        use_enum_values = True


class LearningProfile(BaseModel):
    """
    User's overall learning profile
    """
    user_id: str
    updated_at: datetime
    
    # Mastery per topic (quick lookup)
    mastery_levels: Dict[str, int] = {}  # topic -> 0-100
    
    # Preferences
    preferences: Dict[str, Any] = {
        "metaphor_style": "cricket",
        "backup_metaphors": ["cooking", "gaming"],
        "explanation_depth": "medium",
        "preferred_language": "hinglish",
        "visual_learner": True
    }
    
    # Learning patterns
    patterns: Dict[str, Any] = {
        "best_time_of_day": "evening",
        "avg_session_length_mins": 25,
        "preferred_difficulty": "medium",
        "learns_better_with": "examples"  # vs "proofs"
    }
    
    # Stats (for dashboard)
    stats: Dict[str, Any] = {
        "total_questions": 0,
        "current_streak_days": 0,
        "longest_streak_days": 0,
        "total_xp": 0,
        "level": 1,
        "accuracy_overall": 0.0
    }
    
    # Last active
    last_active_topic: Optional[str] = None
    last_active_concept_thread: List[str] = []
    incomplete_concepts: List[str] = []
    
    # Mastery history (for analytics)
    mastery_history: List[Dict[str, Any]] = []


class ConversationContext(BaseModel):
    """
    Short-term conversation context (rolling window)
    """
    session_id: str
    user_id: str
    created_at: datetime
    last_updated: datetime
    
    # Rolling window (last 10-50 messages)
    messages: List[Dict[str, Any]] = []
    
    # Session summary (for memory consolidation)
    session_summary: Optional[str] = None
    concepts_covered: List[str] = []
    mastery_updates: Dict[str, int] = {}  # topic -> delta
    
    # Session stats
    total_messages: int = 0
    avg_response_time: float = 0.0
    topics_discussed: List[str] = []


class MemorySearchResult(BaseModel):
    """Result from semantic memory search"""
    fact_id: str
    content: str
    topic: str
    subject: str
    similarity_score: float
    created_at: datetime
    mastery_level: Optional[int] = None
    fact_type: FactType


# =============================================================================
# MEMORY CONTRACT v2 - CANONICAL SCHEMAS
# =============================================================================

class TopicMastery(BaseModel):
    """Mastery information for a single topic"""
    topic: str
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    interaction_count: int = 0


class StudentProfile(BaseModel):
    """
    LONG-TERM Student Profile (persists across sessions/restarts)
    
    MEMORY CONTRACT: This is THE canonical schema for student data.
    ALL agents MUST use these keys - no ad-hoc additions.
    
    MULTI-TENANT: Isolated by user_id. NEVER leak between users.
    """
    # Identity (REQUIRED)
    user_id: str
    schema_version: int = MEMORY_SCHEMA_VERSION
    
    # Academic Context
    grade: Optional[str] = None
    exam_target: Optional[str] = None  # JEE/NEET/CBSE/etc
    exam_date: Optional[datetime] = None
    
    # Mastery by Topic (bounded to prevent bloat)
    mastery_by_topic: Dict[str, TopicMastery] = Field(default_factory=dict)
    
    # Strengths & Weaknesses (max 10 each)
    weak_topics: List[str] = Field(default_factory=list, max_items=10)
    strong_topics: List[str] = Field(default_factory=list, max_items=10)
    
    # Learning Preferences
    preferred_explanation: ExplanationStyle = ExplanationStyle.STEP_BY_STEP
    language_style: str = "concise"  # concise/detailed
    pacing: Pacing = Pacing.NORMAL
    preferred_analogies: List[str] = Field(default_factory=lambda: ["cricket", "cooking"])
    
    # Motivation & Engagement
    motivation_baseline: float = Field(default=0.5, ge=0.0, le=1.0)
    current_goals: List[str] = Field(default_factory=list, max_items=5)
    
    # Streaks (gamification)
    practice_streak: int = 0
    revision_streak: int = 0
    last_practice_date: Optional[datetime] = None
    
    # Safety (minimal, no PII)
    safety_flags: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('weak_topics', 'strong_topics', pre=True, always=True)
    def limit_topics(cls, v):
        """Enforce bounded growth - max 10 topics"""
        if v and len(v) > 10:
            return v[-10:]  # Keep most recent
        return v or []
    
    @validator('mastery_by_topic', pre=True, always=True)
    def limit_mastery_topics(cls, v):
        """Enforce bounded growth - max 50 topics"""
        if v and len(v) > 50:
            # Keep topics with highest interaction count
            sorted_topics = sorted(
                v.items(),
                key=lambda x: x[1].get('interaction_count', 0) if isinstance(x[1], dict) else 0,
                reverse=True
            )
            return dict(sorted_topics[:50])
        return v or {}


class SessionState(BaseModel):
    """
    SHORT-TERM Session State (persists across restarts within a session)
    
    MEMORY CONTRACT: This is THE canonical schema for session data.
    Persisted to DB, survives process restarts.
    
    MULTI-TENANT: Isolated by user_id + session_id.
    """
    # Identity (REQUIRED)
    user_id: str
    session_id: str
    schema_version: int = MEMORY_SCHEMA_VERSION
    
    # Last N Turns (bounded to 10)
    last_turns: List[Dict[str, Any]] = Field(default_factory=list, max_items=10)
    
    # Session Summary (bounded to 800 chars)
    session_summary: str = Field(default="", max_length=800)
    
    # Active Task Context
    active_task: Optional[str] = None  # e.g., "solving friction numericals"
    open_questions: List[str] = Field(default_factory=list, max_items=5)
    
    # Agent Context
    last_used_agent: Optional[str] = None
    last_retrieval_topics: List[str] = Field(default_factory=list, max_items=5)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('last_turns', pre=True, always=True)
    def limit_turns(cls, v):
        """Enforce bounded growth - max 10 turns"""
        if v and len(v) > 10:
            return v[-10:]  # Keep most recent
        return v or []
    
    @validator('session_summary', pre=True, always=True)
    def limit_summary(cls, v):
        """Enforce bounded size - max 800 chars"""
        if v and len(v) > 800:
            return v[:800]
        return v or ""


class MemoryEvent(BaseModel):
    """
    WRITE-AHEAD LOG for memory updates
    
    Used for:
    - Audit trail
    - Debugging
    - Rebuilding state if needed
    
    RETENTION: Bounded (e.g., last 100 per user)
    """
    # Identity
    user_id: str
    session_id: str
    event_id: Optional[str] = None
    
    # Event Data
    event_type: MemoryEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Source
    source_agent: Optional[str] = None
    request_id: Optional[str] = None
    
    # Schema
    schema_version: int = MEMORY_SCHEMA_VERSION
    
    @validator('payload', pre=True, always=True)
    def limit_payload(cls, v):
        """Enforce bounded payload size"""
        if v:
            # Convert to string and check size
            import json
            payload_str = json.dumps(v)
            if len(payload_str) > 2000:  # Max 2KB
                return {"truncated": True, "reason": "payload_too_large"}
        return v or {}


class MemoryContextPack(BaseModel):
    """
    COMPACT memory context for agent consumption
    
    This is what agents receive - NOT raw memory dumps.
    Selective recall: only relevant memory is included.
    """
    # User context
    user_id: str
    session_id: str
    
    # Relevant profile fields (not full profile)
    student_name: str = ""
    exam_target: Optional[str] = None
    current_mastery: int = 0  # 0-100
    mastery_bucket: str = "beginner"
    
    # Relevant memory snippets (max 5)
    relevant_memories: List[Dict[str, Any]] = Field(default_factory=list, max_items=5)
    
    # Session context
    session_summary: str = ""
    active_task: Optional[str] = None
    last_topic: Optional[str] = None
    
    # Preferences
    preferred_explanation: str = "step_by_step"
    pacing: str = "normal"
    
    # Flags
    is_weak_area: bool = False
    needs_encouragement: bool = False
    
    def to_prompt_context(self) -> str:
        """Generate concise context string for LLM prompts"""
        parts = []
        
        if self.student_name:
            parts.append(f"Student: {self.student_name}")
        
        if self.exam_target:
            parts.append(f"Preparing for: {self.exam_target}")
        
        parts.append(f"Mastery: {self.current_mastery}% ({self.mastery_bucket})")
        
        if self.session_summary:
            parts.append(f"Session: {self.session_summary[:150]}")
        
        if self.active_task:
            parts.append(f"Working on: {self.active_task}")
        
        if self.is_weak_area:
            parts.append("⚠️ This is a weak area - be extra supportive")
        
        if self.relevant_memories:
            mem_hints = [m.get("content", "")[:50] for m in self.relevant_memories[:2]]
            parts.append(f"Related: {'; '.join(mem_hints)}")
        
        return " | ".join(parts)

