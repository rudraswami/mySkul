"""
Pydantic models for Auto-Note Mentor functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class AutoNoteSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    session_name: str
    source_type: str = "live"  # live, uploaded, image, pdf
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, completed, processing, transcribing
    audio_duration: float = 0.0
    processing_progress: int = 0  # 0-100


class TopicCard(BaseModel):
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    heading: str
    key_points: List[str]
    formulas: List[str] = []
    examples: List[str] = []
    confidence_score: float = 0.0
    professor_verified: bool = False
    syllabus_tags: List[str] = []


class ProcessedNote(BaseModel):
    note_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    transcript: str = ""
    topic_cards: List[TopicCard] = []
    mentor_summary: str = ""
    professor_verification: Dict[str, Any] = {}
    flashcards: List[Dict[str, str]] = []
    quiz_questions: List[Dict[str, Any]] = []
    concepts_learned: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None


class NoteSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    subject: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = "active"  # active, processing, completed
    audio_duration: Optional[int] = None  # seconds
    transcription: Optional[str] = None
    structured_notes: Optional[Dict[str, Any]] = None
    dual_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AudioChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sequence_number: int
    transcription: str
    timestamp: float  # seconds from start
    confidence: Optional[float] = None
    processed: bool = False


class GeneratedFlashcard(BaseModel):
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    question: str
    answer: str
    concept: str
    difficulty_level: int = Field(ge=1, le=5)
    created_from_point: Optional[str] = None  # Reference to note point
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NoteSessionRequest(BaseModel):
    title: str
    subject: str


class AudioChunkRequest(BaseModel):
    session_id: str
    transcription: str
    timestamp: float
    sequence_number: int
    confidence: Optional[float] = None


class EndSessionRequest(BaseModel):
    fallback_transcription: Optional[str] = None
    total_duration: Optional[float] = None


class ExplainPointRequest(BaseModel):
    session_id: str
    point_reference: str  # e.g., "point_3", "concept_1"
    additional_context: Optional[str] = None


class GenerateFlashcardsRequest(BaseModel):
    session_id: str
    specific_concepts: Optional[List[str]] = None  # If empty, generate from all notes


class DocumentUploadRequest(BaseModel):
    session_id: str
    document_type: str = Field(pattern="^(pdf|image)$")  # "pdf" or "image"
    title: Optional[str] = None
    subject: Optional[str] = None


class SpacedRepetitionCard(BaseModel):
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    front: str  # Question/concept
    back: str   # Answer/explanation
    ease_factor: float = 2.5  # SM-2 algorithm
    interval: int = 1  # Days until next review
    repetitions: int = 0
    next_review: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None
    quality: int = 0  # 0-5 user rating


class CreateSpacedRepetitionRequest(BaseModel):
    session_id: str
    auto_generate: bool = True  # Auto-generate from session notes
    custom_cards: Optional[List[Dict[str, str]]] = None


class ReviewCardRequest(BaseModel):
    card_id: str
    quality: int = Field(ge=0, le=5)  # 0=complete blackout, 5=perfect recall


class SemanticSearchRequest(BaseModel):
    user_id: str
    query: str
    limit: int = 5


class ClassSeriesRequest(BaseModel):
    series_name: str
    subject: str
    description: Optional[str] = None
