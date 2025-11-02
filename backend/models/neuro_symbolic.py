"""
Pydantic models for Neuro-Symbolic AI Tutor responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class VisualSchemaNode(BaseModel):
    """Node in visual schema diagram"""
    id: str
    label: str
    type: str = "main"  # main, detail, result
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['main', 'detail', 'result']
        if v not in valid_types:
            return 'main'
        return v


class VisualSchemaEdge(BaseModel):
    """Edge connecting nodes in visual schema"""
    from_node: str = Field(..., alias='from')
    to_node: str = Field(..., alias='to')
    label: Optional[str] = None
    
    class Config:
        populate_by_name = True


class VisualSchema(BaseModel):
    """Visual schema for concept diagram"""
    diagram_type: str  # flow, equation_map, mind_map, timeline, comparison, cycle, hierarchy
    title: str
    nodes: List[VisualSchemaNode]
    edges: List[VisualSchemaEdge]
    caption: str
    
    @validator('diagram_type')
    def validate_diagram_type(cls, v):
        valid_types = ['flow', 'equation_map', 'mind_map', 'timeline', 'comparison', 'cycle', 'hierarchy']
        if v not in valid_types:
            return 'flow'
        return v


class ProfessorVerification(BaseModel):
    """Professor verification section"""
    steps: List[str]  # Step-by-step logical verification
    source: str  # NCERT or standard reference
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    note: Optional[str] = None  # Additional notes


class MiniPractice(BaseModel):
    """Mini practice question"""
    question: str
    options: Optional[List[str]] = None  # For MCQ
    hint: str
    question_type: str = "mcq"  # mcq, fill_blank, short_answer
    
    @validator('question_type')
    def validate_question_type(cls, v):
        valid_types = ['mcq', 'fill_blank', 'short_answer']
        if v not in valid_types:
            return 'mcq'
        return v


class NeuroSymbolicResponse(BaseModel):
    """
    Complete neuro-symbolic AI tutor response
    8-section format for Indian students
    """
    # Core sections
    practical_explanation: str  # 3-6 lines, simple explanation
    indian_example: str  # Concrete example from Indian student life
    metaphor: str  # Memory hook from daily India life
    visual_schema: VisualSchema  # JSON diagram structure
    professor_verification: ProfessorVerification  # Logical verification
    mini_practice: MiniPractice  # Practice question
    encouragement: str  # Clean, sincere encouragement
    ask: str  # Follow-up question
    
    # Metadata
    student_emotion: str = "neutral"  # Detected emotion
    response_tone: str = "balanced"  # Tone adjustment made
    subject: str
    exam_mode: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('student_emotion')
    def validate_emotion(cls, v):
        valid_emotions = ['confused', 'stressed', 'bored', 'curious', 'excited', 'low_confidence', 'neutral']
        if v not in valid_emotions:
            return 'neutral'
        return v


class NeuroSymbolicChatMessage(BaseModel):
    """Chat message with neuro-symbolic response"""
    message_id: str
    session_id: str
    user_id: str
    user_message: str
    ai_response: NeuroSymbolicResponse
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
