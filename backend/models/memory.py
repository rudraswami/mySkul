"""
Memory System Data Models
Production-ready models for long-term student memory
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class FactType(str, Enum):
    """Types of memory facts"""
    CONCEPT_LEARNED = "concept_learned"
    MISCONCEPTION = "misconception"
    PREFERENCE = "preference"
    MASTERY_UPDATE = "mastery_update"
    ERROR_PATTERN = "error_pattern"
    STRENGTH = "strength"
    WEAKNESS = "weakness"


class MasteryLevel(str, Enum):
    """Mastery level buckets"""
    BEGINNER = "beginner"  # 0-30
    INTERMEDIATE = "intermediate"  # 31-70
    ADVANCED = "advanced"  # 71-100


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

