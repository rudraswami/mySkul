"""
Sentiment analysis utility for detecting user emotions and adapting AI responses
"""
import re
from typing import Dict, Any, Tuple


class SentimentAnalyzer:
    """Analyze user message sentiment and emotional state"""
    
    def __init__(self):
        # Emotion keywords and patterns
        self.confusion_keywords = ['confused', 'don\'t understand', 'unclear', 'lost', 'struggling', 'help', 'difficult', 'hard']
        self.confidence_keywords = ['understand', 'got it', 'clear', 'makes sense', 'easy', 'simple']
        self.frustration_keywords = ['frustrated', 'annoyed', 'tired', 'fed up', 'give up', 'impossible', 'can\'t']
        self.curiosity_keywords = ['why', 'how', 'what if', 'curious', 'interesting', 'want to know', 'explain more']
        
    def analyze(self, message: str) -> Dict[str, Any]:
        """Analyze message and return sentiment profile"""
        message_lower = message.lower()
        
        # Calculate sentiment scores
        confusion_score = self._calculate_score(message_lower, self.confusion_keywords)
        confidence_score = self._calculate_score(message_lower, self.confidence_keywords)
        frustration_score = self._calculate_score(message_lower, self.frustration_keywords)
        curiosity_score = self._calculate_score(message_lower, self.curiosity_keywords)
        
        # Determine primary sentiment
        scores = {
            'confusion': confusion_score,
            'confidence': confidence_score,
            'frustration': frustration_score,
            'curiosity': curiosity_score
        }
        
        primary_sentiment = max(scores, key=scores.get)
        sentiment_intensity = scores[primary_sentiment]
        
        # Determine user intent type
        intent_type = self._determine_intent(message_lower, scores)
        
        # Recommended persona blend
        persona_blend = self._recommend_persona(primary_sentiment, sentiment_intensity, intent_type)
        
        return {
            'primary_sentiment': primary_sentiment,
            'sentiment_intensity': sentiment_intensity,
            'intent_type': intent_type,
            'persona_blend': persona_blend,
            'tone_color': self._get_tone_color(primary_sentiment),
            'confidence_level': confidence_score,
            'needs_encouragement': frustration_score > 0.3 or confusion_score > 0.5
        }
    
    def _calculate_score(self, message: str, keywords: list) -> float:
        """Calculate score for a set of keywords"""
        score = 0.0
        for keyword in keywords:
            if keyword in message:
                score += 1.0
        # Normalize by message length
        return min(score / (len(message.split()) / 10), 1.0)
    
    def _determine_intent(self, message: str, scores: Dict[str, float]) -> str:
        """Determine user's primary intent"""
        # Check for question patterns
        if message.startswith(('how', 'why', 'what', 'when', 'where', 'can you explain')):
            return 'concept_learning'
        
        # Check for problem-solving
        if 'solve' in message or 'calculate' in message or 'find' in message:
            return 'problem_solving'
        
        # Check for confusion/clarification
        if scores['confusion'] > 0.3:
            return 'confusion_clarification'
        
        # Check for emotional support needed
        if scores['frustration'] > 0.3:
            return 'emotional_support'
        
        return 'general_query'
    
    def _recommend_persona(self, sentiment: str, intensity: float, intent: str) -> Dict[str, float]:
        """Recommend persona blend based on sentiment and intent"""
        # Default balanced blend
        blend = {'professor': 0.5, 'mentor': 0.5}
        
        if intent == 'concept_learning':
            blend = {'professor': 0.7, 'mentor': 0.3}
        elif intent == 'confusion_clarification':
            blend = {'professor': 0.4, 'mentor': 0.6}
        elif intent == 'emotional_support':
            blend = {'professor': 0.2, 'mentor': 0.8}
        elif sentiment == 'frustration' and intensity > 0.5:
            blend = {'professor': 0.3, 'mentor': 0.7}
        elif sentiment == 'curiosity':
            blend = {'professor': 0.6, 'mentor': 0.4}
        
        return blend
    
    def _get_tone_color(self, sentiment: str) -> str:
        """Get color gradient for UI adaptation"""
        color_map = {
            'confusion': '#FFA500',  # Orange
            'confidence': '#22C55E',  # Green
            'frustration': '#EF4444',  # Red
            'curiosity': '#8B5CF6'   # Purple
        }
        return color_map.get(sentiment, '#3B82F6')  # Blue default