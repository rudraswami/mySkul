"""
AI and Chat-related models for Dhruv AI application
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    subject: Optional[str] = None  # Auto-detected if not provided
    image_url: Optional[str] = None  # Base64 image or URL for vision analysis
    image_context: Optional[str] = None  # Additional context about the image


class DualAIRequest(BaseModel):
    message: str
    session_id: str
    subject: Optional[str] = None  # Auto-detected if not provided
    image_url: Optional[str] = None  # Base64 image or URL for vision analysis  
    image_context: Optional[str] = None  # Additional context about the image
    exam_mode: Optional[str] = None  # Dynamic exam mode: JEE, NEET, CBSE, etc. - fetched from user profile if not provided


class MathValidationRequest(BaseModel):
    expression: str
    units: Optional[str] = None


class FactVerificationRequest(BaseModel):
    statement: str
    subject: str
    context: Optional[str] = None


class StudyPlanRequest(BaseModel):
    target_exam_date: str  # ISO date string
    daily_study_hours: int = Field(ge=1, le=16)
    weak_subjects: List[str] = []
    strong_subjects: List[str] = []
    preferred_study_times: List[str] = []  # morning, afternoon, evening, night
    stress_level: int = Field(ge=1, le=10, default=5)


class PracticeProblemsRequest(BaseModel):
    original_question: str
    subject: str
    topic: str
    education_standard: str = "JEE"


class WellnessCheckRequest(BaseModel):
    stress_level: int = Field(ge=1, le=10)
    motivation_level: int = Field(ge=1, le=10)
    confidence_level: int = Field(ge=1, le=10)
    study_satisfaction: int = Field(ge=1, le=10)
    session_id: str