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
    REMINDER = "reminder"            # Wants to be reminded (one-time)
    RECURRING_REMINDER = "recurring_reminder"  # Daily/weekly reminders
    NOTIFICATION = "notification"    # Wants a notification sent
    SUMMARY = "summary"              # Wants a study summary
    GOAL = "goal"                    # Wants to set a goal
    SCHEDULE = "schedule"            # Wants to schedule study time
    STUDY_PLAN = "study_plan"        # Wants help planning for exam
    PROGRESS_CHECK = "progress_check"  # Wants to know how they're doing
    BREAK_REQUEST = "break_request"  # Needs a break
    MOTIVATION = "motivation"        # Feeling demotivated
    WEAK_TOPICS = "weak_topics"      # Wants to know weak areas
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
        # RECURRING REMINDERS - Check this BEFORE regular reminders
        IntentType.RECURRING_REMINDER: [
            r'remind\s+(?:me\s+)?(?:every\s*)?(?:daily|everyday|each\s+day)',
            r'remind\s+(?:me\s+)?(?:every\s+)?(?:week|weekly)',
            r'remind\s+(?:me\s+)?(?:every\s+)?(?:morning|evening|night)',
            r'remind\s+(?:me\s+)?(?:on\s+)?(?:weekdays?|weekends?)',
            r'daily\s+remind',
            r'(?:set|create)\s+(?:a\s+)?(?:daily|weekly|recurring)\s+remind',
            r'remind\s+(?:me\s+)?(?:every|each)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'रोज़\s+याद',  # Hindi: daily remind
            r'हर\s+दिन',   # Hindi: every day
        ],
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
        IntentType.STUDY_PLAN: [
            r'help\s+(?:me\s+)?(?:prepare|plan)\s+(?:for\s+)?(?:jee|neet|boards?|exam)',
            r'(?:create|make)\s+(?:a\s+)?(?:study\s+)?plan',
            r'(?:i\s+have|my)\s+(?:jee|neet|exam)\s+in\s+\d+\s+(?:days?|months?|weeks?)',
            r'plan\s+(?:for|my)\s+(?:jee|neet|exam)',
            r'how\s+(?:should|do)\s+i\s+(?:prepare|study)\s+for',
            r'preparation\s+strategy',
        ],
        IntentType.PROGRESS_CHECK: [
            r'how\s+am\s+i\s+doing',
            r'(?:show|check)\s+(?:my\s+)?progress',
            r'am\s+i\s+(?:improving|getting\s+better)',
            r'(?:my|show)\s+(?:weak|strong)\s+(?:areas?|topics?|points?)',
            r'where\s+(?:am\s+i|do\s+i)\s+(?:weak|struggling)',
            r'analytics|statistics|stats',
        ],
        IntentType.WEAK_TOPICS: [
            r'(?:what|which)\s+(?:are\s+)?(?:my\s+)?weak\s+(?:topics?|areas?|points?)',
            r'where\s+(?:am\s+i|do\s+i)\s+(?:need|have)\s+(?:to\s+)?(?:improve|work)',
            r'(?:show|tell)\s+(?:me\s+)?(?:my\s+)?weak',
            r'(?:i\'?m?|am)\s+(?:weak|struggling)\s+(?:in|at|with)',
        ],
        IntentType.BREAK_REQUEST: [
            r'(?:i\s+)?need\s+(?:a\s+)?break',
            r'(?:i\'?m?|feeling)\s+(?:tired|exhausted|burnt?\s*out)',
            r'take\s+(?:a\s+)?(?:break|rest)',
            r'pause\s+(?:for|study)',
            r'थक\s+गया',  # Hindi: tired
        ],
        IntentType.MOTIVATION: [
            r'(?:i\'?m?|feeling)\s+(?:demotivated|unmotivated|low|sad|down)',
            r'(?:i\s+)?(?:can\'?t|cannot)\s+(?:focus|concentrate|study)',
            r'(?:i\s+)?(?:don\'?t|do\s+not)\s+(?:feel|want)\s+(?:like\s+)?study',
            r'motivate\s+me',
            r'(?:i\s+)?(?:give|need)\s+(?:up|motivation)',
            r'हिम्मत\s+नहीं',  # Hindi: no courage
            r'मन\s+नहीं',     # Hindi: don't feel like
        ],
        IntentType.GOAL: [
            r'set\s+(?:a\s+)?(?:study\s+)?goal',
            r'i\s+want\s+to\s+(?:study|learn|complete)',
            r'my\s+goal\s+is',
            r'target\s+(?:is|set)',
        ],
        IntentType.SCHEDULE: [
            r'schedule\s+(?:my\s+)?(?:study|learning)',
            r'book\s+(?:a\s+)?(?:study\s+)?(?:time|session)',
            r'when\s+should\s+i\s+study',
        ],
    }
    
    # NON-ACTION patterns - conversational, just acknowledge nicely, don't try to execute an action
    NON_ACTION_PATTERNS = {
        IntentType.FEEDBACK: [
            r'(?:this|that)\s+(?:was|is)\s+(?:helpful|good|bad|wrong)',
            r'👍|👎|❤️',
            r'(?:not\s+)?helpful',
        ],
    }
    
    # GRATITUDE patterns - special handling for warm response (not action, not information)
    GRATITUDE_PATTERNS = [
        r'^thanks?(?:\s*(?:you|so\s+much|a\s+lot|buddy|bro|man|dude|yaar)?)?[!\.\s]*$',
        r'^thank\s+you(?:\s*(?:so\s+much|very\s+much|a\s+lot)?)?[!\.\s]*$',
        r'^(?:tysm|ty|thx|thnx|thnks?)[!\.\s]*$',
        r'^(?:धन्यवाद|शुक्रिया|thanks\s+yaar)[!\.\s]*$',
        r'^(?:appreciate\s+(?:it|that)|much\s+appreciated)[!\.\s]*$',
        r'^(?:great|awesome|perfect|nice|cool|ok(?:ay)?|got\s+it|understood)[!\.\s]*$',
    ]
    
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
        
        # Check for gratitude/acknowledgment (needs warm response, not action)
        if self._is_gratitude(text_lower):
            return DetectedIntent(
                intent_type=IntentType.FEEDBACK,
                confidence=0.95,
                requires_action=False,  # NOT an action - just conversational
                extracted_params={'sentiment': 'positive', 'type': 'gratitude'},
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
    
    def _is_gratitude(self, text: str) -> bool:
        """Check if text is expressing gratitude or acknowledgment"""
        for pattern in self.GRATITUDE_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_params(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters for action intents"""
        params = {}
        text_lower = text.lower()
        
        if intent_type == IntentType.RECURRING_REMINDER:
            # Extract frequency
            if 'daily' in text_lower or 'everyday' in text_lower or 'each day' in text_lower:
                params['frequency'] = 'daily'
            elif 'weekday' in text_lower:
                params['frequency'] = 'weekdays'
            elif 'weekend' in text_lower:
                params['frequency'] = 'weekends'
            elif 'weekly' in text_lower or 'every week' in text_lower:
                params['frequency'] = 'weekly'
            else:
                params['frequency'] = 'daily'
            
            # Extract specific days
            days = []
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in day_names:
                if day in text_lower:
                    days.append(day)
            if days:
                params['days'] = ','.join(days)
                params['frequency'] = 'weekly'
            
            # Extract time
            time_str = self._extract_time(text)
            if time_str:
                params['time'] = time_str
            elif 'morning' in text_lower:
                params['time'] = 'morning'
            elif 'evening' in text_lower:
                params['time'] = 'evening'
            elif 'night' in text_lower:
                params['time'] = 'night'
            else:
                params['time'] = '6pm'  # Default
            
            # Extract message/subject
            message = self._extract_reminder_message(text)
            params['message'] = message
            
            # Extract subject if mentioned
            subjects = ['physics', 'chemistry', 'maths', 'math', 'biology', 'english']
            for subj in subjects:
                if subj in text_lower:
                    params['subject'] = subj.capitalize()
                    break
            
            return params
        
        elif intent_type == IntentType.STUDY_PLAN:
            # Extract exam type
            if 'jee' in text_lower:
                params['exam'] = 'JEE'
            elif 'neet' in text_lower:
                params['exam'] = 'NEET'
            elif 'board' in text_lower:
                params['exam'] = 'Boards'
            else:
                params['exam'] = 'General'
            
            # Extract timeframe
            match = re.search(r'in\s+(\d+)\s*(days?|months?|weeks?)', text_lower)
            if match:
                params['duration'] = int(match.group(1))
                params['duration_unit'] = match.group(2).rstrip('s')
            
            return params
        
        elif intent_type == IntentType.PROGRESS_CHECK:
            # Extract subject if mentioned
            subjects = ['physics', 'chemistry', 'maths', 'math', 'biology', 'english']
            for subj in subjects:
                if subj in text_lower:
                    params['subject'] = subj.capitalize()
                    break
            return params
        
        elif intent_type == IntentType.WEAK_TOPICS:
            # Extract subject if mentioned
            subjects = ['physics', 'chemistry', 'maths', 'math', 'biology', 'english']
            for subj in subjects:
                if subj in text_lower:
                    params['subject'] = subj.capitalize()
                    break
            return params
        
        elif intent_type == IntentType.BREAK_REQUEST:
            # Extract break duration if mentioned
            match = re.search(r'(\d+)\s*(?:min|minute|hour|hr)', text_lower)
            if match:
                params['duration'] = int(match.group(1))
            else:
                params['duration'] = 10  # Default 10 minutes
            return params
        
        elif intent_type == IntentType.REMINDER:
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
    
    def _extract_reminder_message(self, text: str) -> str:
        """Extract what to remind about from text"""
        text_lower = text.lower()
        message = None
        
        # Pattern 1: "for <message>" - most common for study reminders
        for_match = re.search(r'\bfor\s+(.+?)(?:\bat\b|\?|$)', text, re.IGNORECASE)
        if for_match:
            message = for_match.group(1).strip().rstrip('?')
        
        # Pattern 2: "to <message>" - for action reminders
        if not message:
            to_match = re.search(r'\bto\s+(?:study\s+)?(.+?)(?:\bat\b|\?|$)', text, re.IGNORECASE)
            if to_match and 'remind' not in to_match.group(1).lower():
                message = to_match.group(1).strip().rstrip('?')
        
        # Pattern 3: "about <message>"
        if not message:
            about_match = re.search(r'\babout\s+(.+?)(?:\bat\b|\?|$)', text, re.IGNORECASE)
            if about_match:
                message = about_match.group(1).strip().rstrip('?')
        
        # Check for subject as message
        if not message:
            subjects = ['physics', 'chemistry', 'maths', 'math', 'biology', 'english']
            for subj in subjects:
                if subj in text_lower:
                    message = f"{subj.capitalize()} study"
                    break
        
        return message or "Study reminder"
    
    def get_tool_for_intent(self, intent: DetectedIntent) -> Optional[str]:
        """Get the tool name to use for an intent"""
        intent_to_tool = {
            IntentType.REMINDER: 'schedule_reminder',
            IntentType.RECURRING_REMINDER: 'schedule_recurring_reminder',
            IntentType.NOTIFICATION: 'send_notification',
            IntentType.SUMMARY: 'send_study_summary',
            IntentType.GOAL: 'set_study_goal',
            IntentType.SCHEDULE: 'create_study_schedule',
            IntentType.STUDY_PLAN: 'create_study_plan',
            IntentType.PROGRESS_CHECK: 'check_progress',
            IntentType.WEAK_TOPICS: 'analyze_weak_topics',
            IntentType.BREAK_REQUEST: 'start_break',
            IntentType.MOTIVATION: 'send_motivation',
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





