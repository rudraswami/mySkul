"""
Enhanced Intent Classification System
Maps user queries to specific response strategies
"""
import re
from typing import Dict, Optional, Tuple


class EnhancedIntentClassifier:
    """
    Advanced intent detection for adaptive response routing
    Classifies into 5 core intent types + greeting
    """

    # Intent-specific keywords and patterns
    DEFINITION_PATTERNS = [
        r'\bwhat is\b', r'\bdefine\b', r'\bmeaning of\b', r'\bstate\b',
        r'\bwhat are\b', r'\bwhat\'s\b', r'\bwhat does.*mean\b'
    ]

    DEEP_DIVE_PATTERNS = [
        r'\bgo deep\b', r'\bdeep dive\b', r'\bin depth\b', r'\bderive\b',
        r'\bprove\b', r'\bexception\b', r'\bedge case\b', r'\bwhy exactly\b',
        r'\bdetailed\b', r'\bcomprehensive\b', r'\bfundamental\b',
        r'\bthorough\b', r'\bexhaustive\b'
    ]

    COMPARE_PATTERNS = [
        r'\bcompare\b', r'\bdifference between\b', r'\bvs\b', r'\bversus\b',
        r'\bcontrast\b', r'\bdifferences\b', r'\bsimilarities\b',
        r'\bcompared to\b', r'\brather than\b'
    ]

    APPLICATION_PATTERNS = [
        r'\breal[- ]world\b', r'\bpractical\b', r'\bapplication\b',
        r'\buse case\b', r'\bdaily life\b', r'\bwhere.*used\b',
        r'\bapply\b', r'\bexample\b', r'\breal life\b',
        r'\bin practice\b', r'\bin reality\b', r'\bhow.*use\b'
    ]

    CLARIFICATION_PATTERNS = [
        r'\bagain\b', r'\banother way\b', r'\bdifferently\b',
        r'\bclarify\b', r'\bfollow ?up\b', r'\bmore detail\b',
        r'\bi know\b', r'\balready learned\b', r'\bone more\b',
        r'\bdifferent metaphor\b', r'\banother example\b'
    ]

    # Greeting patterns (from existing IntentClassifier)
    GREETING_PATTERNS = [
        'hi', 'hello', 'hey', 'hii', 'sup', 'wassup',
        'good morning', 'good afternoon', 'good evening',
        'namaste', 'namaskar', 'vanakkam', 'salaam'
    ]

    @staticmethod
    def classify_intent(message: str, conversation_history: list = None) -> Dict[str, any]:
        """
        Classify user query intent with confidence score

        Returns:
        {
            'intent': str,  # definition_query, deep_dive, compare_query, application_request, clarification_follow_up, greeting
            'confidence': float,  # 0.0 to 1.0
            'requires_visual': bool,  # Whether visual is needed
            'requires_professor': bool,  # Whether professor layer needed
            'metadata': dict  # Additional context
        }
        """
        if not message or len(message.strip()) == 0:
            return {
                'intent': 'greeting',
                'confidence': 1.0,
                'requires_visual': False,
                'requires_professor': False,
                'metadata': {}
            }

        message_lower = message.lower().strip()
        word_count = len(message.split())

        # Check for greeting first
        if EnhancedIntentClassifier._is_greeting(message_lower):
            return {
                'intent': 'greeting',
                'confidence': 0.9,
                'requires_visual': False,
                'requires_professor': False,
                'metadata': {}
            }

        # Priority order: deep_dive > compare > application > definition > clarification

        # 1. Deep Dive Detection (high priority)
        if EnhancedIntentClassifier._matches_patterns(message_lower, EnhancedIntentClassifier.DEEP_DIVE_PATTERNS):
            return {
                'intent': 'deep_dive',
                'confidence': 0.95,
                'requires_visual': True,  # Deep dives benefit from visuals
                'requires_professor': True,  # Activate professor layer
                'metadata': {
                    'depth_level': 'advanced',
                    'show_derivation': True,
                    'show_edge_cases': True
                }
            }

        # 2. Compare/Contrast Detection
        if EnhancedIntentClassifier._matches_patterns(message_lower, EnhancedIntentClassifier.COMPARE_PATTERNS):
            targets = EnhancedIntentClassifier._extract_compare_targets(message)
            return {
                'intent': 'compare_query',
                'confidence': 0.9,
                'requires_visual': True,  # Comparison tables are visual
                'requires_professor': False,
                'metadata': {
                    'compare_targets': targets,
                    'use_table': True
                }
            }

        # 3. Application/Real-world Detection
        if EnhancedIntentClassifier._matches_patterns(message_lower, EnhancedIntentClassifier.APPLICATION_PATTERNS):
            return {
                'intent': 'application_request',
                'confidence': 0.85,
                'requires_visual': True,  # Real-world examples benefit from visuals
                'requires_professor': False,
                'metadata': {
                    'focus': 'real_world',
                    'show_examples': True,
                    'case_study': True
                }
            }

        # 4. Definition Detection
        if EnhancedIntentClassifier._matches_patterns(message_lower, EnhancedIntentClassifier.DEFINITION_PATTERNS):
            return {
                'intent': 'definition_query',
                'confidence': 0.9,
                'requires_visual': False,  # Simple definitions don't need visuals by default
                'requires_professor': False,
                'metadata': {
                    'response_length': 'short',
                    'metaphor_only': True  # Use metaphor but not full visual
                }
            }

        # 5. Clarification/Follow-up Detection
        if EnhancedIntentClassifier._matches_patterns(message_lower, EnhancedIntentClassifier.CLARIFICATION_PATTERNS):
            return {
                'intent': 'clarification_follow_up',
                'confidence': 0.8,
                'requires_visual': False,  # Skip visuals for clarifications
                'requires_professor': False,
                'metadata': {
                    'build_on_previous': True,
                    'skip_intro': True,
                    'use_different_metaphor': True
                }
            }

        # Default: Conceptual Explanation
        return {
            'intent': 'conceptual_explanation',
            'confidence': 0.7,
            'requires_visual': True if word_count > 5 else False,
            'requires_professor': False,
            'metadata': {
                'depth_level': 'standard'
            }
        }

    @staticmethod
    def _is_greeting(message_lower: str) -> bool:
        """Check if message is a greeting"""
        # Exact match
        if message_lower in EnhancedIntentClassifier.GREETING_PATTERNS:
            return True

        # Very short messages (< 4 chars) without keywords
        if len(message_lower) <= 3:
            return True

        return False

    @staticmethod
    def _matches_patterns(text: str, patterns: list) -> bool:
        """Check if text matches any of the regex patterns"""
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    @staticmethod
    def _extract_compare_targets(message: str) -> Tuple[str, str]:
        """Extract the two items being compared"""
        msg_lower = message.lower()

        # Try "A vs B" pattern
        match = re.search(r'([a-zA-Z0-9\s\-]+?)\s+(?:vs|versus)\s+([a-zA-Z0-9\s\-]+)', msg_lower)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())

        # Try "difference between A and B" pattern
        match = re.search(r'difference.*between\s+([a-zA-Z0-9\s\-]+?)\s+and\s+([a-zA-Z0-9\s\-]+)', msg_lower)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())

        # Try "compare A and B" pattern
        match = re.search(r'compare\s+([a-zA-Z0-9\s\-]+?)\s+(?:and|with)\s+([a-zA-Z0-9\s\-]+)', msg_lower)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())

        return ("Option A", "Option B")

    @staticmethod
    def should_show_visual(intent_result: Dict) -> bool:
        """
        Determine if visual should be shown based on intent

        Visual Gating Logic:
        - definition_query: No visual (metaphor text only)
        - deep_dive: Yes (professor notes + visual)
        - compare_query: Yes (comparison table)
        - application_request: Suggest visual (user choice)
        - clarification_follow_up: No (skip to avoid repetition)
        """
        intent = intent_result.get('intent')
        requires_visual = intent_result.get('requires_visual', False)

        # Hard rules
        if intent in ['definition_query', 'clarification_follow_up', 'greeting']:
            return False

        if intent in ['compare_query', 'deep_dive']:
            return True

        if intent == 'application_request':
            # Suggest visual but let user decide
            return 'suggest'  # Special value

        return requires_visual

    @staticmethod
    def get_professor_activation(intent_result: Dict) -> bool:
        """Determine if professor layer should be activated"""
        intent = intent_result.get('intent')
        requires_professor = intent_result.get('requires_professor', False)

        # Professor layer only for deep dives and complex explanations
        if intent == 'deep_dive':
            return True

        return requires_professor


def test_intent_classifier():
    """Test the enhanced intent classifier"""
    test_cases = [
        ("What is valency?", "definition_query"),
        ("Compare ionic and covalent bonding", "compare_query"),
        ("Explain catalyst with a real-life example", "application_request"),
        ("Go deep into Aufbau principle", "deep_dive"),
        ("Give me another metaphor for quantum numbers", "clarification_follow_up"),
        ("Hello", "greeting"),
        ("Explain Newton's law with a real-life demo", "application_request"),
    ]

    print("Testing Enhanced Intent Classifier:\n")
    for message, expected in test_cases:
        result = EnhancedIntentClassifier.classify_intent(message)
        status = "✅" if result['intent'] == expected else "❌"
        print(f"{status} '{message}'")
        print(f"   → Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print(f"   → Visual: {result['requires_visual']} | Professor: {result['requires_professor']}")
        print()


if __name__ == "__main__":
    test_intent_classifier()
