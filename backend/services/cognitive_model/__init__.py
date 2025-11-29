"""
Student Cognitive Model - Adaptive Learning System
===================================================

Tracks and models each student's:
- Knowledge state (what they know)
- Mastery levels (how well they know it)
- Learning patterns (how they learn best)
- Common mistakes (where they struggle)

This enables truly personalized, adaptive education.
"""

from .knowledge_tracker import KnowledgeTracker
from .mastery_model import MasteryModel
from .learning_patterns import LearningPatternAnalyzer
from .adaptive_engine import AdaptiveEngine, get_adaptive_engine

__all__ = [
    'KnowledgeTracker',
    'MasteryModel',
    'LearningPatternAnalyzer',
    'AdaptiveEngine',
    'get_adaptive_engine'
]

