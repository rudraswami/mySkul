"""
Visual Professor Response Model
Structured response format for visual professor explanations
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class VisualType(str, Enum):
    """Types of visual content"""
    ANIMATION = "animation"
    SCENE = "scene"
    TIMELINE = "timeline"
    INTERACTIVE = "interactive"
    SVG = "svg"


@dataclass
class VisualStage:
    """Single stage in the visual explanation"""
    stage_id: str
    duration_ms: int
    narration: str
    animations: List[Dict[str, Any]]
    interactions: List[Dict[str, Any]]
    emphasis: Optional[str] = None
    narration_style: str = "professor"  # professor, mentor, supervisor


@dataclass
class VisualProfessorResponse:
    """Complete visual professor response"""
    visual_id: str
    type: str  # animated_lesson, interactive_scene, etc.
    visual_type: VisualType
    template: str
    stages: List[VisualStage]
    total_duration_ms: int
    interaction_points: List[int]
    metadata: Dict[str, Any]
    lottie_file: Optional[str] = None
    asset_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert enum to string
        result["visual_type"] = self.visual_type.value
        # Convert stages
        result["stages"] = [asdict(stage) for stage in self.stages]
        return result

