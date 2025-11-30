"""
Vidya Grammar Engine - Grammar Parser
Parses YAML grammar definitions into validated Pydantic models
"""

import yaml
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from pathlib import Path


class ParameterType(str, Enum):
    """Parameter types for grammar definitions"""
    ASSET = "asset"  # Reference to BAL asset
    VARIABLE = "variable"  # Numeric variable (slider)
    ENUM = "enum"  # Enumeration (dropdown)
    TEXT = "text"  # Text input
    BOOLEAN = "boolean"  # Toggle


class AnimationType(str, Enum):
    """Animation types"""
    CAUSE_EFFECT = "cause_effect"  # Arrow appears after object moves
    PROGRESSIVE_REVEAL = "progressive_reveal"  # Step-by-step disclosure
    FOCUS_GUIDE = "focus_guide"  # Highlight to guide attention
    PHYSICS_SIMULATION = "physics_simulation"  # Real-time physics


class PedagogicalPurpose(str, Enum):
    """Pedagogical purpose of each animation"""
    SHOW_CAUSE_EFFECT = "show_cause_effect"
    DEMONSTRATE_CONCEPT = "demonstrate_concept"
    GUIDE_ATTENTION = "guide_attention"
    TEST_HYPOTHESIS = "test_hypothesis"  # "What if?" exploration
    BUILD_UNDERSTANDING = "build_understanding"  # Progressive disclosure


class ParameterDefinition(BaseModel):
    """Parameter definition in grammar"""
    name: str
    type: ParameterType
    label: str  # Human-readable label (can be Hinglish)
    description: str  # What this parameter controls
    
    # Type-specific fields
    tag: Optional[str] = None  # For ASSET type: asset tag to filter
    min: Optional[float] = None  # For VARIABLE type
    max: Optional[float] = None  # For VARIABLE type
    unit: Optional[str] = None  # For VARIABLE type (e.g., "N", "kg", "m/s")
    enum_values: Optional[List[str]] = None  # For ENUM type
    default_value: Optional[Union[str, float, bool]] = None
    
    # Cultural context
    cultural_hint: Optional[str] = None  # e.g., "Auto-rickshaw weight"
    real_world_example: Optional[str] = None  # e.g., "Typical auto weighs 450kg"
    
    @validator('type')
    def validate_type_specific_fields(cls, v, values):
        """Ensure type-specific fields are present"""
        if v == ParameterType.ASSET and not values.get('tag'):
            raise ValueError("ASSET type requires 'tag' field")
        if v == ParameterType.VARIABLE:
            if values.get('min') is None or values.get('max') is None:
                raise ValueError("VARIABLE type requires 'min' and 'max' fields")
        if v == ParameterType.ENUM and not values.get('enum_values'):
            raise ValueError("ENUM type requires 'enum_values' field")
        return v


class AnimationStep(BaseModel):
    """Single animation step with pedagogical purpose"""
    step_id: str
    purpose: PedagogicalPurpose  # Why this animation exists
    description: str  # What happens in this step
    
    # Animation definition (Python-like pseudocode)
    animation_code: str  # e.g., "object_a.acceleration = force_slider / object_a.mass"
    
    # Timing
    duration_ms: int = 1000  # Duration of this step
    delay_ms: int = 0  # Delay before starting
    
    # Visual guidance
    camera_focus: Optional[str] = None  # Which object to focus on (Professor's POV)
    highlight_elements: List[str] = Field(default_factory=list)  # Elements to highlight
    show_arrow: bool = False  # Show cause-effect arrow
    arrow_from: Optional[str] = None  # Arrow origin
    arrow_to: Optional[str] = None  # Arrow destination
    
    # Interaction
    pause_for_interaction: bool = False  # Pause and wait for student interaction
    interaction_prompt: Optional[str] = None  # e.g., "Agar yeh double ho jaaye?" (What if this doubles?)
    
    # Zero cognitive load: Only show if adds value
    skip_if_no_value: bool = False  # Skip if doesn't add understanding


class AnnotationDefinition(BaseModel):
    """Annotation (label, callout) in visual"""
    label: str  # Text to display (can be Hinglish)
    position: str  # Position reference (e.g., "friction_force", "object_a.center")
    color: str = "red"  # Color for visibility
    ncert_citation: Optional[str] = None  # e.g., "Page 102, Fig 5.3"
    
    # Professor's POV: Show like teacher pointing
    show_pointer: bool = True  # Show pointing arrow
    pointer_style: str = "hand"  # "hand", "arrow", "circle"
    
    # Value-first: Only show if adds understanding
    required_for_understanding: bool = True


class GrammarDefinition(BaseModel):
    """Complete grammar definition"""
    # Identity
    grammar_id: str  # e.g., "physics.force_between_two_objects"
    name: str  # Human-readable name
    description: str  # What this grammar visualizes
    
    # Subject context
    subject: str  # e.g., "physics", "chemistry", "mathematics"
    syllabus_topic: List[str]  # e.g., ["physics.friction", "physics.motion"]
    ncert_reference: Optional[str] = None
    
    # Parameters (what can be adjusted)
    parameters: List[ParameterDefinition]
    
    # Output: Animation and annotations
    animation: Dict[str, Any]  # Animation definition
    animation_steps: List[AnimationStep]  # Step-by-step animation with purpose
    annotations: List[AnnotationDefinition] = Field(default_factory=list)
    
    # Value-first validation
    learning_objectives: List[str]  # What students will learn
    value_proposition: str  # Why this visual adds value (if removed, understanding suffers)
    
    # Cultural context
    recommended_assets: List[str]  # Suggested BAL asset IDs
    cultural_context: str  # Why these assets are culturally relevant
    
    # Professor's POV settings
    camera_style: str = "teacher_demonstration"  # "teacher_demonstration", "student_view", "overhead"
    pacing: str = "deliberate"  # "deliberate" (slow, like teacher), "fast", "adaptive"
    show_hand_gestures: bool = True  # Show pointing/highlighting gestures
    
    # Interactive depth
    interactive_elements: List[str] = Field(default_factory=list)  # What can be manipulated
    what_if_scenarios: List[str] = Field(default_factory=list)  # Pre-defined "what if?" questions
    
    # Version
    version: str = "1.0.0"
    
    @validator('animation_steps')
    def validate_animation_steps(cls, v):
        """Ensure every animation step has pedagogical purpose"""
        for step in v:
            if not step.purpose:
                raise ValueError(f"Animation step {step.step_id} must have pedagogical purpose")
        return v
    
    @validator('value_proposition')
    def validate_value_proposition(cls, v):
        """Value proposition must explain why visual is essential"""
        if len(v) < 50:
            raise ValueError("Value proposition must be detailed (min 50 chars)")
        if "if removed" not in v.lower() and "without" not in v.lower():
            raise ValueError("Value proposition must explain what happens if visual is removed")
        return v


class GrammarParser:
    """Parser for YAML grammar definitions"""
    
    def __init__(self):
        self.grammars: Dict[str, GrammarDefinition] = {}
    
    def load_from_yaml(self, yaml_path: Union[str, Path]) -> GrammarDefinition:
        """
        Load grammar from YAML file
        
        Args:
            yaml_path: Path to YAML file
        
        Returns:
            Parsed GrammarDefinition
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        grammar = GrammarDefinition(**data)
        self.grammars[grammar.grammar_id] = grammar
        
        return grammar
    
    def load_from_dict(self, data: Dict[str, Any]) -> GrammarDefinition:
        """
        Load grammar from dictionary
        
        Args:
            data: Grammar definition as dict
        
        Returns:
            Parsed GrammarDefinition
        """
        grammar = GrammarDefinition(**data)
        self.grammars[grammar.grammar_id] = grammar
        return grammar
    
    def get_grammar(self, grammar_id: str) -> Optional[GrammarDefinition]:
        """Get grammar by ID"""
        return self.grammars.get(grammar_id)
    
    def list_grammars(self, subject: Optional[str] = None) -> List[GrammarDefinition]:
        """List all grammars, optionally filtered by subject"""
        grammars = list(self.grammars.values())
        if subject:
            grammars = [g for g in grammars if g.subject == subject]
        return grammars












