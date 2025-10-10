"""
Core data models for Dhruv AI application
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: str
    password_hash: str
    exam_type: str  # JEE, NEET, UPSC
    grade: Optional[str] = None
    target_year: int
    parent_email: Optional[str] = None
    subscription_type: str = "free"  # free, basic, premium, family
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    exam_type: str
    grade: Optional[str] = None
    target_year: int
    parent_email: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class StudyProgress(BaseModel):
    progress_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    chapter: str
    concept: str
    mastery_level: float = 0.0  # 0-100%
    time_spent: int = 0  # minutes
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    questions_attempted: int = 0
    questions_correct: int = 0


class StudyProgressUpdate(BaseModel):
    subject: str
    chapter: str
    concept: str
    mastery_level: float = 0.0  # 0-100%
    time_spent: int = 0  # minutes
    questions_attempted: int = 0
    questions_correct: int = 0


class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    title: str = "New Chat"
    topic: Optional[str] = "General"
    ai_mode: Optional[str] = "dual"
    pinned: bool = False
    bookmarked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SessionCreateRequest(BaseModel):
    title: str
    subject: str
    topic: Optional[str] = "General"
    ai_mode: Optional[str] = "dual"


class SessionRenameRequest(BaseModel):
    title: str


class SessionPinRequest(BaseModel):
    pinned: bool


class SessionBookmarkRequest(BaseModel):
    bookmarked: bool


class SessionMessageRequest(BaseModel):
    user_message: str
    ai_response: dict
    timestamp: str


class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    message: str
    response: str
    reasoning: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    feedback: Optional[str] = None  # helpful, not_helpful
    confidence: Optional[float] = None