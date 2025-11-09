"""Business logic services package"""
from .auth_service import AuthService
from .subscription_service import SubscriptionService
from .ai_service import AIService
from .analytics_service import AnalyticsService
from .auto_notes_service import AutoNotesService
from .mock_tests_service import MockTestsService

# PRD: export metaphor + visual generators
from .metaphor_engine import (
    StudentDNA,
    ConceptBundle,
    MetaphorCandidate,
    deconstruct_question,
    generate_5_muse_candidates,
    score_and_select,
    select_metaphors,
)
from .dynamic_visual_sketch import create_visual_sketch
