"""
💪 MOTIVATION AGENT - Intelligent Emotional Support

This agent detects emotional states and provides appropriate support:
- Boredom → Engaging challenges, gamification
- Frustration → Empathy + breakthrough strategies
- Burnout → Rest advocacy + perspective
- Anxiety → Calming techniques + confidence building
- Success → Celebration + momentum building

Philosophy: Real support, not cringe motivation
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MotivationAgent:
    """
    Lightweight motivation enhancer that adds emotional support to responses
    """
    
    # Emotional state patterns
    EMOTIONAL_PATTERNS = {
        'bored': {
            'keywords': ['bored', 'boring', 'tired', 'sleepy', 'not interested', 'unmotivated'],
            'response_style': 'engaging',
            'energy': 'high'
        },
        'frustrated': {
            'keywords': ['frustrated', 'angry', 'hate', 'stupid', 'can\'t do this', 'give up', 'failing'],
            'response_style': 'empathetic',
            'energy': 'calm'
        },
        'anxious': {
            'keywords': ['worried', 'scared', 'anxious', 'nervous', 'panic', 'stress', 'pressure'],
            'response_style': 'reassuring',
            'energy': 'calm'
        },
        'burnout': {
            'keywords': ['exhausted', 'burnt out', 'can\'t anymore', 'too much', 'overwhelmed'],
            'response_style': 'compassionate',
            'energy': 'gentle'
        },
        'excited': {
            'keywords': ['excited', 'can\'t wait', 'love this', 'interesting', 'cool'],
            'response_style': 'matching',
            'energy': 'high'
        },
        'confident': {
            'keywords': ['got this', 'easy', 'understand', 'making sense', 'improving'],
            'response_style': 'building',
            'energy': 'positive'
        }
    }
    
    # Engaging activities for boredom
    BOREDOM_BUSTERS = [
        "🎯 Quick Challenge: Solve this in under 2 minutes!",
        "🎮 Game Mode: Let's turn this into a mini-competition",
        "🔥 Speed Round: 5 quick questions, time yourself!",
        "🎲 Random Topic Roulette: Let's explore something unexpected",
        "💡 Did You Know: Here's a mind-blowing fact about this topic",
        "🏆 Streak Builder: Maintain your learning streak!",
    ]
    
    # Empathetic responses for frustration
    FRUSTRATION_HELPERS = [
        "I get it - this one trips up almost everyone at first.",
        "You know what? This topic is genuinely tricky. Let's try a different angle.",
        "Hey, the fact that you're still trying means you're ahead of 90% of people who give up.",
        "Sometimes stepping back for 5 minutes helps. Want to try something else first?",
    ]
    
    # Calming responses for anxiety
    ANXIETY_CALMERS = [
        "Take a breath. You've tackled hard things before.",
        "Remember: exams test knowledge, not worth. You're more than a score.",
        "Let's break this into smaller pieces. One step at a time.",
        "Many toppers felt exactly this way. It's part of the journey.",
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def detect_emotional_state(self, query: str) -> Optional[str]:
        """Detect emotional state from query"""
        query_lower = query.lower()
        
        for state, patterns in self.EMOTIONAL_PATTERNS.items():
            if any(keyword in query_lower for keyword in patterns['keywords']):
                return state
        
        return None
    
    def enhance_response(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance a response with emotional support elements
        
        This doesn't replace the response, it adds supportive elements
        """
        try:
            # Get the query from result or context
            query = result.get('query', context.get('original_query', ''))
            
            # Detect emotional state
            emotional_state = self.detect_emotional_state(query)
            
            if not emotional_state:
                # No emotional state detected, return empty motivation
                return {'motivation': None}
            
            logger.info(f"💪 Emotional state detected: {emotional_state}")
            
            # Build motivation content based on state
            motivation = self._build_motivation(emotional_state, context)
            
            return {'motivation': motivation}
            
        except Exception as e:
            logger.error(f"Motivation enhancement failed: {e}")
            return {'motivation': None}
    
    def _build_motivation(
        self,
        emotional_state: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build motivation content for the detected state"""
        
        student = context.get('student_profile', {})
        name = student.get('user_name', '')
        
        import random
        
        if emotional_state == 'bored':
            return {
                'type': 'engagement',
                'message': random.choice(self.BOREDOM_BUSTERS),
                'suggestion': "Let's make this more interesting!",
                'action': {
                    'type': 'challenge',
                    'label': 'Try a Quick Challenge',
                    'icon': '🎯'
                }
            }
        
        elif emotional_state == 'frustrated':
            return {
                'type': 'empathy',
                'message': random.choice(self.FRUSTRATION_HELPERS),
                'suggestion': "Different approach might help",
                'action': {
                    'type': 'alternative',
                    'label': 'Try Another Approach',
                    'icon': '🔄'
                }
            }
        
        elif emotional_state == 'anxious':
            return {
                'type': 'reassurance',
                'message': random.choice(self.ANXIETY_CALMERS),
                'suggestion': "One step at a time",
                'action': {
                    'type': 'simplify',
                    'label': 'Break It Down',
                    'icon': '📋'
                }
            }
        
        elif emotional_state == 'burnout':
            return {
                'type': 'compassion',
                'message': "It's okay to rest. Your brain actually learns during breaks!",
                'suggestion': "Even 10 minutes of rest can help",
                'action': {
                    'type': 'break',
                    'label': 'Take a Short Break',
                    'icon': '☕'
                }
            }
        
        elif emotional_state == 'excited':
            return {
                'type': 'amplify',
                'message': "Love the energy! Let's channel it into something productive 🚀",
                'suggestion': "Ready for a challenge?",
                'action': {
                    'type': 'challenge',
                    'label': 'Try Something Harder',
                    'icon': '💪'
                }
            }
        
        elif emotional_state == 'confident':
            return {
                'type': 'build',
                'message': "You're doing great! Keep this momentum going!",
                'suggestion': "Ready to level up?",
                'action': {
                    'type': 'advance',
                    'label': 'Next Level',
                    'icon': '⬆️'
                }
            }
        
        return None
    
    def get_opening_for_state(self, emotional_state: str, name: str = '') -> str:
        """Get an appropriate opening based on emotional state"""
        
        greeting = f"Hey {name}! " if name and len(name) > 1 else ""
        
        openings = {
            'bored': f"{greeting}I hear you - let's spice things up! 🌶️",
            'frustrated': f"{greeting}I totally get it. Let's try something different.",
            'anxious': f"{greeting}Take a breath. We'll figure this out together.",
            'burnout': f"{greeting}Your wellbeing matters. Let's take it easy.",
            'excited': f"{greeting}Love the energy! Let's do this! 🚀",
            'confident': f"{greeting}You're on fire! Keep it going! 🔥",
        }
        
        return openings.get(emotional_state, greeting)


# ============================================
# INTEGRATION HELPERS
# ============================================

def should_trigger_motivation(query: str) -> bool:
    """Check if query indicates need for emotional support"""
    agent = MotivationAgent({})
    return agent.detect_emotional_state(query) is not None


def get_motivation_enhancement(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get motivation enhancement for a query"""
    agent = MotivationAgent({})
    fake_result = {'query': query}
    return agent.enhance_response(fake_result, context or {})
