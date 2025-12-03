"""
🎯 Action Intent Detector
=========================

Detects when a user request requires an ACTION (agent behavior)
vs just INFORMATION (LLM response).

This is CRITICAL for true agentic behavior:
- "What is photosynthesis?" → INFORMATION (just answer)
- "Remind me tomorrow at 4pm" → ACTION (schedule reminder)
- "Send me a summary" → ACTION (send notification)
- "Set a study goal" → ACTION (create goal in database)

Without this detection, the AI just generates text responses
for everything, never taking real actions.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""
    INFORMATION = "information"      # Just needs an answer
    REMINDER = "reminder"            # Wants to be reminded
    NOTIFICATION = "notification"    # Wants a notification sent
    SUMMARY = "summary"              # Wants a study summary
    GOAL = "goal"                    # Wants to set a goal
    SCHEDULE = "schedule"            # Wants to schedule study time
    FEEDBACK = "feedback"            # Giving feedback
    GREETING = "greeting"            # Just saying hi
    ACTION = "action"                # Generic action request


@dataclass
class DetectedIntent:
    """Result of intent detection"""
    intent_type: IntentType
    confidence: float
    requires_action: bool  # TRUE = needs agent tool, FALSE = just LLM response
    extracted_params: Dict[str, Any]  # Extracted parameters for the action
    original_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'intent_type': self.intent_type.value,
            'confidence': self.confidence,
            'requires_action': self.requires_action,
            'extracted_params': self.extracted_params,
            'original_text': self.original_text
        }


class ActionIntentDetector:
    """
    Detects user intent and extracts action parameters.
    
    This enables TRUE agentic behavior by identifying when
    the agent needs to take a real action vs just respond.
    """
    
    # Patterns for ACTION intents (require tool usage)
    ACTION_PATTERNS = {
        IntentType.REMINDER: [
            r'remind\s+(me|us)',
            r'set\s+(?:a\s+)?reminder',
            r'don\'t\s+let\s+me\s+forget',
            r'alert\s+me',
            r'notify\s+me\s+(?:at|when|in)',
            r'ping\s+me',
            r'remember\s+to\s+tell\s+me',
            r'याद\s+दिला',  # Hindi: remind
            r'reminder\s+set\s+kar',  # Hinglish
        ],
        IntentType.NOTIFICATION: [
            r'send\s+(?:me\s+)?(?:a\s+)?notification',
            r'notify\s+me\s+about',
            r'alert\s+me\s+when',
            r'push\s+notification',
        ],
        IntentType.SUMMARY: [
            r'send\s+(?:me\s+)?(?:a\s+)?summary',
            r'(?:give|show)\s+me\s+(?:a\s+)?(?:study\s+)?summary',
            r'what\s+have\s+i\s+(?:learned|studied)',
            r'my\s+(?:study\s+)?progress',
            r'how\s+(?:much|many)\s+have\s+i\s+(?:done|studied)',
            r'email\s+me\s+(?:a\s+)?summary',
        ],
        IntentType.GOAL: [
            r'set\s+(?:a\s+)?(?:study\s+)?goal',
            r'i\s+want\s+to\s+(?:study|learn|complete)',
            r'my\s+goal\s+is',
            r'target\s+(?:is|set)',
            r'plan\s+my\s+study',
        ],
        IntentType.SCHEDULE: [
            r'schedule\s+(?:my\s+)?(?:study|learning)',
            r'book\s+(?:a\s+)?(?:study\s+)?(?:time|session)',
            r'when\s+should\s+i\s+study',
            r'create\s+(?:a\s+)?(?:study\s+)?(?:plan|schedule)',
        ],
        IntentType.FEEDBACK: [
            r'(?:this|that)\s+(?:was|is)\s+(?:helpful|good|bad|wrong)',
            r'👍|👎|❤️',
            r'thanks?|thank\s+you',
            r'(?:not\s+)?helpful',
        ],
    }
    
    # Patterns for INFORMATION intents (just need LLM response)
    INFO_PATTERNS = [
        r'^(?:what|how|why|when|where|who|which|explain|describe|define)',
        r'^(?:can\s+you\s+)?(?:tell|show)\s+me\s+(?:about|what)',
        r'^(?:i\s+)?(?:don\'t\s+)?understand',
        r'(?:solve|calculate|find)',
        r'(?:difference|compare)\s+between',
        r'^(?:is|are|was|were|do|does|did|can|could|will|would)',
    ]
    
    # Greeting patterns
    GREETING_PATTERNS = [
        r'^(?:hi|hello|hey|yo|sup|hii+|hola|namaste)(?:\s|!|\?)*$',
        r'^(?:good\s+)?(?:morning|afternoon|evening|night)(?:\s|!|\?)*$',
        r'^(?:what\'?s?\s+up|howdy|greetings)(?:\s|!|\?)*$',
    ]
    
    # Time extraction patterns
    TIME_PATTERNS = [
        r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)',
        r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?(?:\s+)?(?:o\'?clock)',
        r'(?:in\s+)?(\d+)\s*(?:minute|min|hour|hr|day|week)s?',
        r'tomorrow',
        r'today',
        r'tonight',
        r'next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(?:this\s+)?(?:morning|afternoon|evening|night)',
    ]
    
    def detect(self, text: str) -> DetectedIntent:
        """
        Detect the intent of user input.
        
        Args:
            text: User's message
        
        Returns:
            DetectedIntent with type, confidence, and extracted params
        """
        text_lower = text.lower().strip()
        
        # Check for greetings first (quick response, no action needed)
        if self._is_greeting(text_lower):
            return DetectedIntent(
                intent_type=IntentType.GREETING,
                confidence=0.95,
                requires_action=False,
                extracted_params={},
                original_text=text
            )
        
        # Check for ACTION intents
        for intent_type, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Extract parameters based on intent type
                    params = self._extract_params(text, intent_type)
                    
                    return DetectedIntent(
                        intent_type=intent_type,
                        confidence=0.85,
                        requires_action=True,
                        extracted_params=params,
                        original_text=text
                    )
        
        # Check for explicit INFORMATION patterns
        for pattern in self.INFO_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return DetectedIntent(
                    intent_type=IntentType.INFORMATION,
                    confidence=0.80,
                    requires_action=False,
                    extracted_params={},
                    original_text=text
                )
        
        # Default to INFORMATION (most common case)
        return DetectedIntent(
            intent_type=IntentType.INFORMATION,
            confidence=0.60,
            requires_action=False,
            extracted_params={},
            original_text=text
        )
    
    def _is_greeting(self, text: str) -> bool:
        """Check if text is just a greeting"""
        for pattern in self.GREETING_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_params(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters for action intents"""
        params = {}
        text_lower = text.lower()
        
        if intent_type == IntentType.REMINDER:
            # Extract time first
            time_str = self._extract_time(text)
            if time_str:
                params['remind_at'] = time_str
            
            # SMART MESSAGE EXTRACTION
            # Try to extract message using common patterns:
            # "remind me in 5min for physics study" -> message = "physics study"
            # "remind me tomorrow to call mom" -> message = "call mom"
            # "remind me at 4pm about the meeting" -> message = "the meeting"
            
            message = None
            
            # Pattern 1: "for <message>" - most common for study reminders
            for_match = re.search(r'\bfor\s+(.+?)(?:\?|$)', text, re.IGNORECASE)
            if for_match:
                message = for_match.group(1).strip().rstrip('?')
            
            # Pattern 2: "to <message>" - for action reminders
            if not message:
                to_match = re.search(r'\bto\s+(.+?)(?:\?|$)', text, re.IGNORECASE)
                if to_match and 'remind' not in to_match.group(1).lower():
                    message = to_match.group(1).strip().rstrip('?')
            
            # Pattern 3: "about <message>"
            if not message:
                about_match = re.search(r'\babout\s+(.+?)(?:\?|$)', text, re.IGNORECASE)
                if about_match:
                    message = about_match.group(1).strip().rstrip('?')
            
            # Fallback: Clean extraction by removing known patterns
            if not message:
                message = text
                for pattern in self.ACTION_PATTERNS[IntentType.REMINDER]:
                    message = re.sub(pattern, '', message, flags=re.IGNORECASE)
                for pattern in self.TIME_PATTERNS:
                    message = re.sub(pattern, '', message, flags=re.IGNORECASE)
                # Clean up connectors but preserve the actual content
                message = re.sub(r'^\s*(?:to|about|that|for)\s+', '', message, flags=re.IGNORECASE)
                message = ' '.join(message.split()).strip().rstrip('?')
            
            if message and len(message) > 2:
                params['message'] = message
            else:
                params['message'] = "Study reminder"
        
        elif intent_type == IntentType.SUMMARY:
            # Extract period
            if 'today' in text_lower:
                params['period'] = 'today'
            elif 'week' in text_lower:
                params['period'] = 'week'
            elif 'month' in text_lower:
                params['period'] = 'month'
            else:
                params['period'] = 'week'  # Default
            
            # Extract channel
            if 'email' in text_lower:
                params['channel'] = 'email'
            else:
                params['channel'] = 'notification'
        
        elif intent_type == IntentType.GOAL:
            # Extract goal text
            match = re.search(r'(?:goal\s+(?:is|to)|want\s+to)\s+(.+)', text_lower)
            if match:
                params['goal_text'] = match.group(1).strip()
        
        return params
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time reference from text"""
        text_lower = text.lower()
        
        # NORMALIZE TYPOS FIRST - critical for user-friendly time parsing
        # Handle common typos: "5mis", "5mns", "5mins", "5m" -> "5 minutes"
        text_lower = re.sub(r'(\d+)\s*(mis|mns|mins?|m)\b', r'\1 minutes', text_lower)
        # Handle "5hrs", "5hr", "5h" -> "5 hours"
        text_lower = re.sub(r'(\d+)\s*(hrs?|h)\b', r'\1 hours', text_lower)
        
        # Look for various time patterns
        
        # "tomorrow at 4pm", "tomorrow morning"
        if 'tomorrow' in text_lower:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
            if time_match:
                return f"tomorrow {time_match.group(0)}"
            
            for tod in ['morning', 'afternoon', 'evening', 'night']:
                if tod in text_lower:
                    return f"tomorrow {tod}"
            
            return "tomorrow"
        
        # "in X minutes/hours" or just "X minutes/hours" (with normalized units)
        match = re.search(r'(?:in\s+)?(\d+)\s*(minutes?|hours?|days?|weeks?)', text_lower)
        if match:
            return f"in {match.group(1)} {match.group(2)}"
        
        # "at 4pm", "at 16:00"
        match = re.search(r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
        if match:
            return match.group(0)
        
        # Day names
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if day in text_lower:
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
                if time_match:
                    return f"next {day} {time_match.group(0)}"
                return f"next {day}"
        
        # Today variants
        if 'today' in text_lower:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
            if time_match:
                return f"today {time_match.group(0)}"
        
        # Tonight, this evening, etc.
        for tod in ['tonight', 'this evening', 'this afternoon', 'this morning']:
            if tod in text_lower:
                return tod
        
        return None
    
    def get_tool_for_intent(self, intent: DetectedIntent) -> Optional[str]:
        """Get the tool name to use for an intent"""
        intent_to_tool = {
            IntentType.REMINDER: 'schedule_reminder',
            IntentType.NOTIFICATION: 'send_notification',
            IntentType.SUMMARY: 'send_study_summary',
            IntentType.GOAL: 'set_study_goal',
            IntentType.SCHEDULE: 'create_study_schedule',
        }
        
        return intent_to_tool.get(intent.intent_type)


# Singleton instance
_detector = None

def get_intent_detector() -> ActionIntentDetector:
    """Get singleton intent detector instance"""
    global _detector
    if _detector is None:
        _detector = ActionIntentDetector()
    return _detector





