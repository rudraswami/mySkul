"""
Student Cognitive Model - Adaptive Learning System
===================================================

COGNITIVE OS v2.0 - True Educational Intelligence

Tracks and models each student's:
- Knowledge state (what they know)
- Mastery levels (how well they know it)
- Learning patterns (how they learn best)
- Common mistakes (where they struggle)

NEW IN v2.0:
- StudentStateEngine: Mastery-driven depth adaptation
- ConsistencyEngine: Cross-session contradiction detection
- AgentNegotiator: Multi-agent collaboration (existing)

NOTE: TeachMeBack is handled by the original implementation in:
- Backend: services/teach_me_back_evaluator.py
- Frontend: components/ui/TeachMeBackModal.jsx
- API: /api/ai/teach-me-back

This enables truly personalized, adaptive education.
"""

from .knowledge_tracker import KnowledgeTracker
from .mastery_model import MasteryModel
from .learning_patterns import LearningPatternAnalyzer
from .adaptive_engine import AdaptiveEngine, get_adaptive_engine
from .agent_negotiation import AgentNegotiator, get_agent_negotiator

# Cognitive OS v2.0 Engines
from .student_state_engine import (
    StudentStateEngine,
    get_student_state_engine,
    StudentState,
    StudentLevel,
    DepthRecommendation
)
from .consistency_engine import (
    ConsistencyEngine,
    get_consistency_engine,
    ConsistencyCheckResult,
    ConsistencyStatus
)

# Cognitive Orchestrator - Integrates cognitive engines (except TeachMeBack which has its own flow)
from .cognitive_orchestrator import (
    CognitiveOrchestrator,
    get_cognitive_orchestrator,
    CognitiveContext,
    CognitiveResponse
)

__all__ = [
    # Existing
    'KnowledgeTracker',
    'MasteryModel',
    'LearningPatternAnalyzer',
    'AdaptiveEngine',
    'get_adaptive_engine',
    'AgentNegotiator',
    'get_agent_negotiator',
    
    # StudentStateEngine
    'StudentStateEngine',
    'get_student_state_engine',
    'StudentState',
    'StudentLevel',
    'DepthRecommendation',
    
    # ConsistencyEngine
    'ConsistencyEngine',
    'get_consistency_engine',
    'ConsistencyCheckResult',
    'ConsistencyStatus',
    
    # CognitiveOrchestrator (Integration Layer)
    'CognitiveOrchestrator',
    'get_cognitive_orchestrator',
    'CognitiveContext',
    'CognitiveResponse',
]

