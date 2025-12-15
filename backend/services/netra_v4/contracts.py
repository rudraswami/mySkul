"""
🔮 NETRA v4.0 - Data Contracts
==============================

Production-grade data contracts for the Visual Intelligence Orchestrator.
All data flowing through the system must conform to these contracts.

Design Principles:
    - Strict typing with Pydantic
    - No optional fields where data is required
    - Clear separation between input, processing, and output contracts
    - Extensible for future enhancements
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ============================================
# ENUMS - Intent & Visual Types
# ============================================

class TeachingIntent(str, Enum):
    """What the student wants to understand - drives visual strategy"""
    EXPLAIN = "explain"           # "What is X?" → Explanatory diagram
    COMPARE = "compare"           # "X vs Y" → Comparison visual
    SHOW_PROCESS = "show_process" # "How does X work?" → Process/flow diagram
    SHOW_STRUCTURE = "show_structure"  # "Parts of X" → Structural diagram
    DERIVE = "derive"             # "Prove X" → Step-by-step derivation
    CALCULATE = "calculate"       # "Find X" → Worked example visual
    VISUALIZE = "visualize"       # "Show me X" → Direct visualization
    CAUSE_EFFECT = "cause_effect" # "Why does X happen?" → Causal chain
    TIMELINE = "timeline"         # "History of X" → Timeline visual
    RELATIONSHIP = "relationship" # "How are X and Y related?" → Relationship map


class VisualStyle(str, Enum):
    """Visual style - modern edtech aesthetics"""
    MODERN_CLEAN = "modern_clean"       # Clean, minimal, professional
    ILLUSTRATED = "illustrated"         # Rich illustrations
    INFOGRAPHIC = "infographic"         # Data-rich infographic style
    WHITEBOARD = "whiteboard"           # Hand-drawn whiteboard feel
    SCIENTIFIC = "scientific"           # Technical/scientific diagram
    CONCEPTUAL = "conceptual"           # Abstract concept visualization


class ComplexityLevel(str, Enum):
    """Visual complexity based on concept depth"""
    SIMPLE = "simple"       # Single concept, 2-3 elements
    MODERATE = "moderate"   # Multi-part concept, 4-6 elements
    COMPLEX = "complex"     # Deep concept, 7+ elements with relationships


# ============================================
# INPUT CONTRACTS
# ============================================

class UserContext(BaseModel):
    """Optional context about the user/session"""
    previous_questions: List[str] = Field(default_factory=list)
    user_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    language: str = "en"
    session_id: Optional[str] = None


class VisualRequest(BaseModel):
    """
    Input contract for visual generation.
    This is what the frontend sends to the API.
    """
    question: str = Field(..., min_length=3, max_length=1000, description="Student's question")
    context: UserContext = Field(default_factory=UserContext)
    
    # Optional overrides (usually auto-detected)
    force_style: Optional[VisualStyle] = None
    force_intent: Optional[TeachingIntent] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Explain how photosynthesis works in plants",
                "context": {
                    "user_level": "intermediate",
                    "language": "en"
                }
            }
        }


# ============================================
# PROCESSING CONTRACTS (Internal)
# ============================================

class ConceptAnalysis(BaseModel):
    """
    Result of analyzing a question for its core concept.
    Subject-agnostic: we extract WHAT the concept is, not WHICH subject.
    """
    core_concept: str = Field(..., description="The main concept being asked about")
    sub_concepts: List[str] = Field(default_factory=list, description="Related sub-concepts")
    key_entities: List[str] = Field(default_factory=list, description="Key objects/entities in the concept")
    relationships: List[str] = Field(default_factory=list, description="Relationships between entities")
    constraints: List[str] = Field(default_factory=list, description="Physical laws, rules, constraints")
    
    # Detected metadata (not hardcoded by subject)
    detected_domain: Optional[str] = Field(None, description="Auto-detected domain (for logging only)")
    complexity: ComplexityLevel = ComplexityLevel.MODERATE


class VisualStrategy(BaseModel):
    """
    The chosen strategy for visualizing a concept.
    Determined by concept + intent, NOT by subject.
    """
    intent: TeachingIntent
    style: VisualStyle
    complexity: ComplexityLevel
    
    # Visual composition hints
    layout_type: str = Field(..., description="e.g., 'central_focus', 'left_to_right', 'circular', 'hierarchical'")
    color_scheme: str = Field(default="educational_blue", description="Color palette name")
    emphasis_elements: List[str] = Field(default_factory=list, description="Elements to visually emphasize")
    
    # Prompt engineering hints
    visual_metaphor: Optional[str] = Field(None, description="Metaphor to use in visualization")
    avoid_elements: List[str] = Field(default_factory=list, description="Elements to avoid (e.g., 'generic shapes')")


class ImagenPrompt(BaseModel):
    """
    Optimized prompt for Imagen image generation.
    Crafted to produce unique, modern, educational visuals.
    """
    main_prompt: str = Field(..., description="The primary image generation prompt")
    negative_prompt: str = Field(default="", description="What to avoid in generation")
    style_modifiers: List[str] = Field(default_factory=list, description="Style keywords")
    
    # Generation parameters
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4"] = "16:9"
    quality: Literal["standard", "high"] = "high"


# ============================================
# OUTPUT CONTRACTS - Teaching Layer
# ============================================

class Hotspot(BaseModel):
    """
    An interactive region on the visual that can be tapped/clicked.
    Coordinates are percentages (0-100) for responsiveness.
    """
    id: str
    x_percent: float = Field(..., ge=0, le=100)
    y_percent: float = Field(..., ge=0, le=100)
    width_percent: float = Field(default=10, ge=1, le=50)
    height_percent: float = Field(default=10, ge=1, le=50)
    label: str
    description: str
    order: int = Field(default=0, description="Order in teaching sequence")


class TeachingStep(BaseModel):
    """
    A single step in the teaching sequence.
    Used for progressive reveal / guided learning.
    """
    step_number: int
    title: str
    narration: str = Field(..., description="What the teacher would say")
    focus_hotspots: List[str] = Field(default_factory=list, description="Hotspot IDs to highlight")
    duration_ms: int = Field(default=3000, description="Suggested duration for this step")


class Annotation(BaseModel):
    """
    A text annotation overlaid on the visual.
    Can be formulas, labels, or explanatory text.
    """
    id: str
    text: str
    x_percent: float = Field(..., ge=0, le=100)
    y_percent: float = Field(..., ge=0, le=100)
    style: Literal["label", "formula", "callout", "note"] = "label"
    font_size: Literal["small", "medium", "large"] = "medium"
    color: str = Field(default="#333333")
    show_at_step: Optional[int] = Field(None, description="Step number when this appears")


class TeachingFlow(BaseModel):
    """
    Complete teaching metadata for a visual.
    This is what makes Netra a teaching tool, not just an image displayer.
    """
    title: str
    summary: str = Field(..., description="One-sentence summary of the concept")
    
    # Interactive elements
    hotspots: List[Hotspot] = Field(default_factory=list)
    
    # Progressive teaching
    steps: List[TeachingStep] = Field(default_factory=list)
    
    # Overlays
    annotations: List[Annotation] = Field(default_factory=list)
    
    # Engagement
    follow_up_questions: List[str] = Field(default_factory=list)
    key_takeaways: List[str] = Field(default_factory=list)


# ============================================
# OUTPUT CONTRACTS - Final Response
# ============================================

class VisualMetadata(BaseModel):
    """Metadata about the generated visual"""
    concept: str
    intent: TeachingIntent
    style: VisualStyle
    complexity: ComplexityLevel
    visual_strategy: str = Field(..., description="Human-readable strategy description")
    generation_model: str = Field(default="imagen-3.0-generate-002")


class GenerationInfo(BaseModel):
    """Debug/analytics information about the generation"""
    time_ms: int
    prompt_used: str = Field(..., description="The prompt sent to Imagen")
    negative_prompt: str = Field(default="")
    model: str
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VisualData(BaseModel):
    """The actual visual content"""
    type: Literal["generated_image"] = "generated_image"
    image_base64: str = Field(..., description="Base64 encoded image")
    image_format: Literal["png", "webp", "jpeg"] = "png"
    width: int
    height: int


class VisualResponse(BaseModel):
    """
    Complete response from the Netra v4 API.
    Contains everything needed to render and teach with the visual.
    """
    success: bool
    
    # The visual itself
    visual: Optional[VisualData] = None
    
    # Metadata
    metadata: Optional[VisualMetadata] = None
    
    # Teaching layer
    teaching: Optional[TeachingFlow] = None
    
    # Debug info (can be disabled in production)
    generation_info: Optional[GenerationInfo] = None
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "visual": {
                    "type": "generated_image",
                    "image_base64": "...",
                    "image_format": "png",
                    "width": 1024,
                    "height": 576
                },
                "metadata": {
                    "concept": "photosynthesis",
                    "intent": "show_process",
                    "style": "illustrated",
                    "complexity": "moderate",
                    "visual_strategy": "Process flow showing light and dark reactions",
                    "generation_model": "imagen-3.0-generate-002"
                },
                "teaching": {
                    "title": "How Photosynthesis Works",
                    "summary": "Photosynthesis converts light energy into chemical energy in plants",
                    "hotspots": [],
                    "steps": [],
                    "annotations": []
                }
            }
        }

