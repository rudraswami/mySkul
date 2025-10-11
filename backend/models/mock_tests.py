"""
Pydantic models for Mock Tests functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class TestBlueprint(BaseModel):
    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_type: str  # JEE, NEET, UPSC
    test_type: str  # "full_length", "chapter_wise", "adaptive"
    subjects: List[str]  # ["Mathematics", "Physics"]
    chapters: List[str] = []  # Specific chapters if chapter_wise
    difficulty_distribution: Dict[str, int]  # {"easy": 5, "medium": 15, "hard": 5}
    total_questions: int
    total_marks: int
    time_limit: int  # minutes
    generation_mode: str = "standard"  # "standard", "variant", "adaptive"
    adaptive_focus: List[str] = []  # Weak areas for adaptive mode
    random_seed: Optional[str] = None  # For reproducible variant generation
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MockTest(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    blueprint_id: str
    title: str
    description: str
    questions: List[str]  # List of question_ids
    total_marks: int
    time_limit: int  # minutes
    status: str = "draft"  # "draft", "active", "submitted", "expired"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    expires_at: datetime  # Auto-calculated based on generation + 24h
    cache_key: str  # For Redis caching
    mentor_pre_tips: str = ""
    professor_metadata: Dict[str, Any] = {}


class TestAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    student_id: str
    answers: Dict[str, str]  # question_id: selected_answer
    question_times: Dict[str, int] = {}  # question_id: time_spent_seconds
    score: int = 0
    percentage: float = 0.0
    correct_answers: int = 0
    wrong_answers: int = 0
    unanswered: int = 0
    time_taken: int = 0  # total seconds
    started_at: datetime
    submitted_at: datetime
    concept_mastery: Dict[str, float] = {}  # chapter/topic: mastery_score
    difficulty_performance: Dict[str, float] = {}  # difficulty_level: success_rate
    professor_analysis: str = ""
    mentor_feedback: str = ""
    recommendations: List[str] = []
    bookmarked_questions: List[str] = []
    flashcards_generated: bool = False


class StudentProgress(BaseModel):
    progress_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject: str
    total_tests: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    improvement_rate: float = 0.0
    current_streak: int = 0
    weak_areas: List[str] = []
    strong_areas: List[str] = []
    recommended_difficulty: int = 3
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    performance_trend: List[Dict[str, Any]] = []  # [{date, score, subject}]


class TestGenerationRequest(BaseModel):
    exam_type: str
    subjects: List[str]
    test_type: str = "full_length"  # "full_length", "chapter_wise", "adaptive"
    chapters: List[str] = []
    difficulty_level: int = Field(default=3, ge=1, le=5)
    num_questions: int = Field(default=10, ge=3, le=100)
    generation_mode: str = "standard"  # "standard", "variant", "adaptive"
    focus_areas: List[str] = []  # For adaptive mode


class TestRetakeRequest(BaseModel):
    original_test_id: str
    retake_mode: str  # "exact", "variant", "adaptive"


class TestSubmissionRequest(BaseModel):
    test_id: str
    answers: Dict[str, str]
    question_times: Dict[str, int] = {}


class BookmarkQuestionRequest(BaseModel):
    question_id: str
    notes: Optional[str] = None
