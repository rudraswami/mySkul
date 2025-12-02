"""
🛠️ Shared Utilities for Agentic System
========================================

Common utilities used across all agents to avoid code duplication.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ============== Intent Detection ==============

class QueryIntent(Enum):
    """Types of queries/intents"""
    GREETING = "greeting"
    CONCEPT = "concept"
    DOUBT = "doubt"
    DERIVATION = "derivation"
    APPLICATION = "application"
    COMPARISON = "comparison"
    CALCULATION = "calculation"
    DEFINITION = "definition"
    EXAMPLE = "example"
    MOTIVATION = "motivation"
    EXAM_STRATEGY = "exam_strategy"
    WEAK_AREA = "weak_area"
    REVISION = "revision"
    PARENT_COMMUNICATION = "parent_communication"
    UNKNOWN = "unknown"


class IntentDetector:
    """Unified intent detection for all agents"""

    @staticmethod
    def detect_intent(query: str) -> QueryIntent:
        """Detect the primary intent of a query"""
        query_lower = query.lower().strip()

        # Greeting
        if IntentDetector._is_greeting(query_lower):
            return QueryIntent.GREETING

        # Doubt/Confusion
        if IntentDetector._is_doubt(query_lower):
            return QueryIntent.DOUBT

        # Calculation
        if IntentDetector._is_calculation(query_lower):
            return QueryIntent.CALCULATION

        # Derivation
        if IntentDetector._is_derivation(query_lower):
            return QueryIntent.DERIVATION

        # Comparison
        if IntentDetector._is_comparison(query_lower):
            return QueryIntent.COMPARISON

        # Application
        if IntentDetector._is_application(query_lower):
            return QueryIntent.APPLICATION

        # Definition
        if IntentDetector._is_definition(query_lower):
            return QueryIntent.DEFINITION

        # Example request
        if IntentDetector._is_example_request(query_lower):
            return QueryIntent.EXAMPLE

        # Exam strategy
        if IntentDetector._is_exam_strategy(query_lower):
            return QueryIntent.EXAM_STRATEGY

        # Weak area analysis
        if IntentDetector._is_weak_area(query_lower):
            return QueryIntent.WEAK_AREA

        # Default to concept explanation
        return QueryIntent.CONCEPT

    @staticmethod
    def _is_greeting(text: str) -> bool:
        greetings = ['hi', 'hello', 'hey', 'namaste', 'hola', 'good morning', 'good evening']
        words = text.strip('!?.,:;').split()
        return len(words) <= 3 and any(g in text for g in greetings)

    @staticmethod
    def _is_doubt(text: str) -> bool:
        doubt_patterns = [
            r"don'?t understand", r"confused", r"doubt", r"not clear",
            r"help me understand", r"stuck on", r"struggling with",
            r"समझ नहीं", r"nahi samjha", r"kaise", r"kyun"
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in doubt_patterns)

    @staticmethod
    def _is_calculation(text: str) -> bool:
        calc_patterns = [
            r"calculate", r"compute", r"find the value",
            r"what is \d+", r"solve for", r"evaluate"
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in calc_patterns)

    @staticmethod
    def _is_derivation(text: str) -> bool:
        derive_words = ['derive', 'proof', 'prove', 'derivation', 'show that', 'demonstrate']
        return any(word in text for word in derive_words)

    @staticmethod
    def _is_comparison(text: str) -> bool:
        compare_words = ['difference between', 'compare', 'versus', 'vs', 'differ from', 'similarity']
        return any(word in text for word in compare_words)

    @staticmethod
    def _is_application(text: str) -> bool:
        app_patterns = ['real world', 'application', 'used in', 'practical', 'example in life', 'where do we use']
        return any(pattern in text for pattern in app_patterns)

    @staticmethod
    def _is_definition(text: str) -> bool:
        def_patterns = [r"what is", r"what are", r"define", r"meaning of", r"kya hai"]
        return any(re.search(p, text, re.IGNORECASE) for p in def_patterns)

    @staticmethod
    def _is_example_request(text: str) -> bool:
        example_words = ['example', 'instance', 'show me', 'demonstrate', 'illustration']
        return any(word in text for word in example_words)

    @staticmethod
    def _is_exam_strategy(text: str) -> bool:
        exam_patterns = [
            'exam', 'test', 'preparation', 'strategy', 'tips',
            'jee', 'neet', 'boards', 'score', 'marks'
        ]
        return any(pattern in text for pattern in exam_patterns)

    @staticmethod
    def _is_weak_area(text: str) -> bool:
        weak_patterns = [
            'weak area', 'weakness', 'improve', 'struggling',
            'bad at', 'mistakes', 'where am i going wrong'
        ]
        return any(pattern in text for pattern in weak_patterns)


# ============== Subject Detection ==============

class SubjectDetector:
    """Detect academic subject from query"""

    SUBJECT_KEYWORDS = {
        'physics': [
            'force', 'motion', 'energy', 'momentum', 'velocity', 'acceleration',
            'gravity', 'electric', 'magnetic', 'wave', 'optics', 'thermodynamics',
            'newton', 'einstein', 'quantum', 'atom', 'nuclear'
        ],
        'chemistry': [
            'element', 'compound', 'reaction', 'acid', 'base', 'mole',
            'periodic table', 'bond', 'organic', 'inorganic', 'equilibrium',
            'oxidation', 'reduction', 'pH', 'solution', 'concentration'
        ],
        'mathematics': [
            'equation', 'algebra', 'calculus', 'derivative', 'integral',
            'matrix', 'vector', 'probability', 'statistics', 'theorem',
            'function', 'graph', 'trigonometry', 'geometry', 'polynomial'
        ],
        'biology': [
            'cell', 'dna', 'gene', 'evolution', 'organism', 'ecosystem',
            'photosynthesis', 'respiration', 'protein', 'enzyme', 'hormone',
            'nervous', 'digestive', 'circulatory', 'reproduction'
        ]
    }

    @classmethod
    def detect_subject(cls, query: str) -> Optional[str]:
        """Detect subject from query text"""
        query_lower = query.lower()

        scores = {}
        for subject, keywords in cls.SUBJECT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[subject] = score

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return None


# ============== Language Detection ==============

class LanguageDetector:
    """Detect language preference from text"""

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language: 'en' (English), 'hi' (Hindi), or 'hinglish'
        """
        # Hindi character ranges
        hindi_chars = re.findall(r'[\u0900-\u097F]+', text)
        english_words = re.findall(r'[a-zA-Z]+', text)

        hindi_ratio = len(''.join(hindi_chars)) / max(len(text), 1)
        english_ratio = len(''.join(english_words)) / max(len(text), 1)

        if hindi_ratio > 0.6:
            return 'hi'
        elif english_ratio > 0.8:
            return 'en'
        else:
            return 'hinglish'


# ============== Response Formatting ==============

class ResponseFormatter:
    """Format responses consistently across agents"""

    @staticmethod
    def format_success_response(
        agent_name: str,
        content: str,
        confidence: float = 0.8,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format a successful response"""
        return {
            'success': True,
            'agent': agent_name,
            'content': content,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

    @staticmethod
    def format_error_response(
        agent_name: str,
        error: str,
        fallback_content: str = "I encountered an issue. Please try rephrasing your question."
    ) -> Dict[str, Any]:
        """Format an error response"""
        return {
            'success': False,
            'agent': agent_name,
            'content': fallback_content,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def merge_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple agent responses"""
        if not responses:
            return ResponseFormatter.format_error_response(
                "system",
                "No responses available"
            )

        # Find primary response (highest confidence)
        primary = max(responses, key=lambda r: r.get('confidence', 0))

        # Merge content if multiple successful responses
        successful = [r for r in responses if r.get('success')]
        if len(successful) > 1:
            merged_content = "\n\n".join([r['content'] for r in successful])
            primary['content'] = merged_content

        # Aggregate metadata
        primary['metadata']['response_count'] = len(responses)
        primary['metadata']['agents_used'] = [r['agent'] for r in responses]

        return primary


# ============== Time Management ==============

class TimeManager:
    """Manage time-related operations"""

    @staticmethod
    def parse_natural_time(text: str) -> Optional[datetime]:
        """
        Parse natural language time expressions
        Examples: "in 2 hours", "tomorrow", "next week"
        """
        now = datetime.now()
        text_lower = text.lower()

        # Simple patterns
        if "now" in text_lower:
            return now
        elif "tomorrow" in text_lower:
            return now + timedelta(days=1)
        elif "today" in text_lower:
            return now

        # Extract numbers and units
        matches = re.findall(r'(\d+)\s*(minute|hour|day|week)', text_lower)
        if matches:
            number, unit = matches[0]
            number = int(number)

            if unit.startswith('minute'):
                return now + timedelta(minutes=number)
            elif unit.startswith('hour'):
                return now + timedelta(hours=number)
            elif unit.startswith('day'):
                return now + timedelta(days=number)
            elif unit.startswith('week'):
                return now + timedelta(weeks=number)

        return None

    @staticmethod
    def is_late_night() -> bool:
        """Check if current time is late night (11 PM - 4 AM)"""
        hour = datetime.now().hour
        return hour >= 23 or hour <= 4

    @staticmethod
    def get_study_session_recommendation() -> str:
        """Get study session recommendation based on time"""
        hour = datetime.now().hour

        if 5 <= hour < 8:
            return "Early morning - Great for memorization and fresh concepts!"
        elif 8 <= hour < 12:
            return "Morning - Perfect for complex problem-solving!"
        elif 12 <= hour < 15:
            return "Afternoon - Good for revision and practice!"
        elif 15 <= hour < 18:
            return "Late afternoon - Ideal for group study or discussions!"
        elif 18 <= hour < 21:
            return "Evening - Great for homework and assignments!"
        elif 21 <= hour < 23:
            return "Night - Good for light revision!"
        else:
            return "Late night - Consider resting for better retention!"


# ============== Validation Utilities ==============

class Validator:
    """Input validation utilities"""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number (Indian format)"""
        pattern = r'^[+91]?[6-9]\d{9}$'
        cleaned = re.sub(r'[^\d+]', '', phone)
        return bool(re.match(pattern, cleaned))

    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        return text.strip()


# ============== Metaphor Generator ==============

class MetaphorGenerator:
    """Generate culturally relevant metaphors"""

    METAPHOR_TEMPLATES = {
        'physics': {
            'force': "Force is like a push or pull in cricket - the harder you hit, the farther the ball goes",
            'momentum': "Momentum is like a running train - heavy and fast means hard to stop",
            'energy': "Energy is like money - you can save it, spend it, or convert it to different forms"
        },
        'chemistry': {
            'reaction': "Chemical reactions are like cooking - mix ingredients, add heat, get something new",
            'catalyst': "A catalyst is like a matchmaker - helps others react without getting involved",
            'equilibrium': "Equilibrium is like a see-saw - balanced when both sides are equal"
        },
        'mathematics': {
            'derivative': "Derivative is like checking your speedometer - tells you how fast you're changing",
            'integral': "Integration is like collecting rain in a bucket - adding up tiny drops",
            'function': "A function is like a machine - put something in, get something out"
        }
    }

    @classmethod
    def generate_metaphor(cls, concept: str, subject: str = None) -> Optional[str]:
        """Generate a metaphor for a concept"""
        concept_lower = concept.lower()

        if subject and subject in cls.METAPHOR_TEMPLATES:
            subject_metaphors = cls.METAPHOR_TEMPLATES[subject]
            for key, metaphor in subject_metaphors.items():
                if key in concept_lower:
                    return metaphor

        # Search all subjects
        for subj_metaphors in cls.METAPHOR_TEMPLATES.values():
            for key, metaphor in subj_metaphors.items():
                if key in concept_lower:
                    return metaphor

        return None


# ============== Student Context ==============

@dataclass
class StudentContext:
    """Standardized student context"""
    user_id: str
    name: str = "Student"
    exam: str = "General"
    grade: Optional[int] = None
    language: str = "en"
    subjects: List[str] = None
    weak_areas: List[str] = None
    strong_areas: List[str] = None
    learning_style: str = "visual"  # visual, auditory, kinesthetic
    streak_days: int = 0
    last_active: Optional[datetime] = None
    emotional_state: Optional[str] = None

    def __post_init__(self):
        if self.subjects is None:
            self.subjects = []
        if self.weak_areas is None:
            self.weak_areas = []
        if self.strong_areas is None:
            self.strong_areas = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'exam': self.exam,
            'grade': self.grade,
            'language': self.language,
            'subjects': self.subjects,
            'weak_areas': self.weak_areas,
            'strong_areas': self.strong_areas,
            'learning_style': self.learning_style,
            'streak_days': self.streak_days,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'emotional_state': self.emotional_state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudentContext':
        """Create from dictionary"""
        if 'last_active' in data and data['last_active']:
            data['last_active'] = datetime.fromisoformat(data['last_active'])
        return cls(**data)

    def needs_motivation(self) -> bool:
        """Check if student needs motivation"""
        if self.streak_days == 0:
            return True
        if self.emotional_state in ['frustrated', 'anxious', 'stressed']:
            return True
        if self.last_active:
            days_inactive = (datetime.now() - self.last_active).days
            return days_inactive > 3
        return False


# ============== Performance Metrics ==============

class PerformanceTracker:
    """Track agent and student performance"""

    @staticmethod
    def calculate_confidence_score(
        tools_used: List[str],
        iterations: int,
        verification_passed: bool
    ) -> float:
        """Calculate confidence score for a response"""
        base_confidence = 0.5

        # Boost for tool usage
        if tools_used:
            base_confidence += min(0.2, len(tools_used) * 0.05)

        # Adjust for iteration count
        if iterations <= 3:
            base_confidence += 0.1  # Quick resolution
        elif iterations > 7:
            base_confidence -= 0.1  # Struggled to find answer

        # Verification boost
        if verification_passed:
            base_confidence += 0.2

        return min(1.0, max(0.1, base_confidence))

    @staticmethod
    def track_agent_performance(
        agent_name: str,
        execution_time: float,
        success: bool,
        confidence: float
    ) -> Dict[str, Any]:
        """Track agent performance metrics"""
        return {
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'execution_time_ms': execution_time,
            'success': success,
            'confidence': confidence,
            'performance_score': (confidence * 0.5 + (1.0 if success else 0) * 0.5)
        }


# ============== Error Recovery ==============

class ErrorRecovery:
    """Error recovery strategies"""

    @staticmethod
    def get_fallback_response(error_type: str, context: Dict[str, Any]) -> str:
        """Get appropriate fallback response for error type"""
        fallbacks = {
            'timeout': "This is taking longer than expected. Let me try a simpler approach.",
            'tool_error': "I had trouble accessing my tools. Let me explain based on what I know.",
            'llm_error': "I'm having trouble formulating a response. Could you rephrase your question?",
            'validation_error': "I need to verify my answer. Give me a moment to double-check.",
            'unknown': "I encountered an unexpected issue. Let me try again with a different approach."
        }
        return fallbacks.get(error_type, fallbacks['unknown'])

    @staticmethod
    def should_retry(error: Exception, attempt: int) -> bool:
        """Determine if operation should be retried"""
        max_retries = 3

        # Don't retry certain errors
        non_retriable = [
            "InvalidAPIKey",
            "QuotaExceeded",
            "InvalidInput"
        ]

        error_name = type(error).__name__
        if error_name in non_retriable:
            return False

        return attempt < max_retries