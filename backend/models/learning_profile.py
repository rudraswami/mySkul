"""
Learning Profile models for cross-session memory
Tracks student learning history, mastery, and preferences
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class TopicMastery(BaseModel):
    """Tracks mastery level for a specific topic"""
    topic: str
    subject: str
    mastery_level: float = Field(ge=0.0, le=1.0)  # 0.0 = not learned, 1.0 = mastered
    times_reviewed: int = 0
    last_reviewed: Optional[datetime] = None
    correct_answers: int = 0
    total_attempts: int = 0
    metaphors_used: List[str] = []
    notes: Optional[str] = None


class LearningSession(BaseModel):
    """Summary of a learning session"""
    session_id: str
    date: datetime
    duration_minutes: int = 0
    topics_covered: List[str] = []
    messages_count: int = 0
    subjects: List[str] = []
    engagement_level: str = "medium"  # high, medium, low
    summary: Optional[str] = None


class WeakArea(BaseModel):
    """Tracks areas where student struggles"""
    topic: str
    subject: str
    struggle_count: int = 1
    last_struggled: datetime
    common_mistakes: List[str] = []
    needs_revision: bool = True


class LearningPreferences(BaseModel):
    """Student's learning preferences discovered over time"""
    preferred_metaphors: Dict[str, int] = {}  # metaphor -> usage_count
    preferred_visual_types: Dict[str, int] = {}  # visual_type -> usage_count
    learning_pace: str = "moderate"  # slow, moderate, fast
    depth_preference: str = "standard"  # quick, standard, deep
    best_study_time: Optional[str] = None  # morning, afternoon, evening, night
    subjects_of_interest: List[str] = []


class LearningProfile(BaseModel):
    """
    Comprehensive learning profile for cross-session memory
    Stored in users collection as embedded document
    """
    user_id: str

    # Learning history
    topics_mastered: List[TopicMastery] = []
    weak_areas: List[WeakArea] = []
    recent_sessions: List[LearningSession] = []

    # Preferences and patterns
    preferences: LearningPreferences = Field(default_factory=LearningPreferences)

    # Stats
    total_sessions: int = 0
    total_questions_asked: int = 0
    total_topics_explored: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_active_date: Optional[datetime] = None

    # Current learning path
    current_topic_focus: Optional[str] = None
    recommended_next_topics: List[str] = []

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningInsight(BaseModel):
    """Generated insights about student's learning"""
    insight_type: str  # progress, strength, weakness, recommendation
    message: str
    topics: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    actionable: bool = True
    generated_at: datetime = Field(default_factory=datetime.utcnow)
