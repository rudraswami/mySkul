"""
Intent Classification Service
Detects user query intent to route appropriately

Phase 0 - Priority P0
"""

class IntentClassifier:
    """
    Classifies user query intent to prevent concept explanations for greetings
    """
    
    # Low-signal queries (greetings, casual chat)
    GREETING_PATTERNS = [
        'hi', 'hello', 'hey', 'hii', 'hiii', 'sup', 'wassup',
        'good morning', 'good afternoon', 'good evening',
        'namaste', 'namaskar', 'vanakkam', 'salaam',
        'yo', 'hola', 'helo', 'heya', 'hy'
    ]
    
    CASUAL_PATTERNS = [
        'how are you', 'what\'s up', 'whats up', 
        'how r u', 'kaise ho', 'how do you do',
        'nice to meet you', 'glad to meet you'
    ]
    
    EMOJI_ONLY_PATTERNS = ['👋', '🙏', '😊', '🙂', '😄', '✋', '🤚']
    
    # Learning intent indicators
    LEARNING_INTENT_KEYWORDS = [
        'explain', 'what is', 'how does', 'why', 'solve', 'problem',
        'understand', 'learn', 'teach', 'tell me', 'show me',
        'define', 'meaning', 'concept', 'theory', 'formula',
        'example', 'practice', 'question', 'doubt', 'help with',
        'confused', 'integrate', 'differentiate', 'calculate',
        'prove', 'derive', 'find', 'determine'
    ]
    
    @staticmethod
    def classify_intent(message: str) -> str:
        """
        Classify user message intent
        
        Returns:
        - 'greeting': Casual greeting or small talk
        - 'learning': Clear learning intent
        - 'ambiguous': Unclear intent (treat as learning)
        """
        if not message or len(message.strip()) == 0:
            return 'greeting'
        
        message_lower = message.lower().strip()
        
        # Check for emoji-only
        if all(char in IntentClassifier.EMOJI_ONLY_PATTERNS for char in message.strip()):
            return 'greeting'
        
        # Check for exact greeting matches
        if message_lower in IntentClassifier.GREETING_PATTERNS:
            return 'greeting'
        
        # Check for casual patterns
        for pattern in IntentClassifier.CASUAL_PATTERNS:
            if pattern in message_lower:
                return 'greeting'
        
        # Check for very short messages (likely greetings)
        if len(message_lower) <= 3 and not any(keyword in message_lower for keyword in IntentClassifier.LEARNING_INTENT_KEYWORDS):
            return 'greeting'
        
        # Check for learning intent
        if any(keyword in message_lower for keyword in IntentClassifier.LEARNING_INTENT_KEYWORDS):
            return 'learning'
        
        # If message has punctuation and > 10 words, likely learning
        if len(message.split()) > 10:
            return 'learning'
        
        # Default: treat as learning (false positive better than false negative)
        return 'learning'
    
    @staticmethod
    def should_trigger_concept_explanation(message: str) -> bool:
        """
        Determine if message should trigger concept explanation
        
        Returns: True if concept explanation needed, False for greeting
        """
        intent = IntentClassifier.classify_intent(message)
        return intent == 'learning'


def generate_greeting_response(user_name: str = "there", streak_days: int = 0, 
                               metaphor_category: str = "cricket", region: str = "Bangalore") -> dict:
    """
    Generate warm mentor greeting response
    Triggered for casual greetings, not concept queries
    
    Phase 2: Mentor Personality
    """
    
    # Import real visual assets
    from prompts.metaphor_visual_library import REAL_VISUAL_ASSETS
    
    # Regional greetings
    regional_greetings = {
        'Delhi': 'Namaste',
        'Mumbai': 'Namaste',
        'Chennai': 'Vanakkam',
        'Kolkata': 'Nomoshkar',
        'Bangalore': 'Namaskara'
    }
    
    greeting = regional_greetings.get(region, 'Namaste')
    
    # Emoji based on metaphor
    metaphor_emoji = {
        'cricket': '🏏',
        'cooking': '🍳',
        'bollywood': '🎬',
        'gaming': '🎮'
    }.get(metaphor_category, '🏏')
    
    # Get real hero visual based on metaphor
    hero_visual_url = REAL_VISUAL_ASSETS.get(metaphor_category, REAL_VISUAL_ASSETS['cricket'])[0]
    
    # Streak message
    streak_msg = ""
    if streak_days > 0:
        streak_msg = f" 🔥 {streak_days} day streak! Keep it up!"
    
    response = {
        "type": "greeting",
        "default_view": {
            "mentor_avatar": {
                "visual_url": "https://assets.dhruvai.com/visuals/mentor/avatar-happy.png",
                "expression": "happy",
                "greeting_animation": "wave"
            },
            "greeting": f"{greeting} {user_name}!{streak_msg}",
            "hero_visual": {
                "visual_url": hero_visual_url,  # REAL image, not abstract SVG
                "alt_text": f"Welcome! {metaphor_emoji}",
                "placeholder_color": "#EFF6FF",
                "tier": 2,  # Real image
                "load_priority": "high"
            },
            "metaphor": {
                "category": metaphor_category,
                "text": f"I'm here to help you ace your exams with {metaphor_category} examples and practical learning!",
                "emoji": metaphor_emoji
            },
            "main_content": {
                "type": "greeting",
                "content": f"Great to see you! I'm your AI mentor - think of me as a helpful IIT senior.\n\nWhat can I help you with today?\n\n• Need concept explanation?\n• Want to solve problems?\n• Practice questions?\n• Clarify doubts?",
                "key_insight": "Ask me anything about your subjects!"
            },
            "quick_actions": [
                {"text": "📚 Explain a concept", "action": "concept"},
                {"text": "🎯 Practice problems", "action": "practice"},
                {"text": "🤔 Clarify doubts", "action": "doubt"},
                {"text": "📊 Mock test", "action": "mock_test"}
            ],
            "professor_badge": {
                "verified": True,
                "badge_visual": "https://assets.dhruvai.com/visuals/badges/professor-verified.png",
                "ncert_ref": "NCERT Aligned",
                "confidence": "high",
                "students_solved": "50,000+"
            }
        },
        "progressive_sections": {
            "encouragement": {
                "message": f"Let's make learning fun with {metaphor_category} examples! Ready when you are."
            },
            "whats_next": [
                {"suggestion": "Start with a topic you're curious about"},
                {"suggestion": "Ask me to explain any concept"},
                {"suggestion": "Try a practice problem"}
            ]
        }
    }
    
    return response
