"""
Visual Professor Engine
Dynamic, intelligent, interactive visual system for professor-like animated explanations
"""

from .concept_detector import UnifiedConceptDetector, ConceptMetadata
from .template_registry import VisualTemplateRegistry
from .generator import VisualProfessorGenerator

__all__ = [
    "UnifiedConceptDetector",
    "ConceptMetadata",
    "VisualTemplateRegistry",
    "VisualProfessorGenerator",
]

