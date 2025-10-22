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
    """
    Request model for mock test generation with comprehensive validation
    """
    exam_type: str = Field(..., min_length=1, max_length=50, description="Exam type (e.g., JEE, NEET, UPSC)")
    subjects: List[str] = Field(..., min_items=1, description="List of subjects (must have at least 1)")
    test_type: str = Field(default="full_length", description="Test type")
    chapters: List[str] = Field(default_factory=list)
    difficulty_level: Any = Field(default=2, description="Difficulty: 1=easy, 2=medium, 3=hard (int or string)")
    num_questions: int = Field(default=10, ge=3, le=100, description="Number of questions (3-100)")
    generation_mode: str = Field(default="standard", description="Generation mode")
    focus_areas: List[str] = Field(default_factory=list)
    
    @validator('exam_type')
    def validate_exam_type(cls, v):
        """Validate exam type"""
        if not v or not v.strip():
            raise ValueError("exam_type cannot be empty")
        return v.strip()
    
    @validator('subjects')
    def validate_subjects(cls, v):
        """Validate subjects list"""
        if not v:
            raise ValueError("subjects cannot be empty - must provide at least one subject")
        # Remove empty strings
        valid_subjects = [s.strip() for s in v if s and s.strip()]
        if not valid_subjects:
            raise ValueError("subjects must contain at least one valid subject")
        return valid_subjects
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        """Normalize difficulty level from int or string to string"""
        # Accept int (1-3) or string (easy/medium/hard)
        if isinstance(v, int):
            difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
            if v not in difficulty_map:
                raise ValueError(f"Invalid difficulty level: {v}. Must be 1-3")
            return difficulty_map[v]
        elif isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower not in ['easy', 'medium', 'hard']:
                raise ValueError(f"Invalid difficulty level: {v}. Must be 'easy', 'medium', or 'hard'")
            return v_lower
        else:
            raise ValueError(f"Invalid difficulty_level type: {type(v)}. Must be int or str")
    
    @validator('test_type')
    def validate_test_type(cls, v):
        """Validate test type"""
        valid_types = ['full_length', 'chapter_wise', 'subject_wise', 'adaptive']
        if v not in valid_types:
            raise ValueError(f"Invalid test_type: {v}. Must be one of {valid_types}")
        return v
    
    @validator('generation_mode')
    def validate_generation_mode(cls, v):
        """Validate generation mode"""
        valid_modes = ['standard', 'variant', 'adaptive']
        if v not in valid_modes:
            raise ValueError(f"Invalid generation_mode: {v}. Must be one of {valid_modes}")
        return v


class TestGenerationResponse(BaseModel):
    """Response model for test generation"""
    success: bool = True
    test_id: str
    test: Dict[str, Any]
    message: str = "Mock test generated successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "test_id": "123e4567-e89b-12d3-a456-426614174000",
                "test": {
                    "test_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "JEE Full Length Test",
                    "num_questions": 10
                },
                "message": "Mock test generated successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Structured error response"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": {"field": "subjects", "error": "Cannot be empty"},
                "trace_id": "abc-123"
            }
        }


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
