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
    password_hash: Optional[str] = None  # Optional for Gmail-only users
    exam_type: Optional[str] = None  # JEE, NEET, UPSC, Others - set in profile setup
    grade: Optional[str] = None
    target_year: Optional[int] = None  # Optional until profile setup
    parent_email: Optional[str] = None
    subscription_type: str = "free"  # free, basic, premium, family
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Gmail OAuth fields
    google_id: Optional[str] = None  # Unique Google user ID
    photo_url: Optional[str] = None  # Profile photo from Google
    auth_provider: str = "google"  # google or email (legacy)
    
    # Profile setup tracking
    profile_completed: bool = False  # True after completing profile setup
    study_goal: Optional[str] = None
    preferred_mode: Optional[str] = None  # AI Mentor, Mock Tests, Notes
    timezone: Optional[str] = None
    country: Optional[str] = None
    
    # Session management for Gmail OAuth
    session_token: Optional[str] = None
    session_expiry: Optional[datetime] = None


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


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    exam_type: Optional[str] = None
    target_year: Optional[int] = None
    current_standard: Optional[str] = None
    institution: Optional[str] = None


class ProfileCompleteRequest(BaseModel):
    """Model for post-Gmail-login profile setup"""
    exam_type: str  # Required: JEE, NEET, UPSC, Others
    study_goal: Optional[str] = None
    preferred_mode: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    target_year: Optional[int] = None


class GoogleAuthCallback(BaseModel):
    """Model for Google OAuth session data from Emergent"""
    id: str  # Google user ID
    email: str
    name: str
    picture: str
    session_token: str