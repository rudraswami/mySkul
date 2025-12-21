"""
🧠 Semantic Intent Classifier - TRUE AI Understanding
======================================================

THIS IS THE FIX FOR THE FUNDAMENTAL DESIGN FLAW.

❌ OLD WAY (Pattern Matching - Broken):
   - If "great" → hardcoded response
   - If "need support" → hardcoded response  
   - If "bored" → hardcoded response
   - ... infinite patterns, always breaking

✅ NEW WAY (Semantic Understanding):
   - Send ANY input to LLM
   - LLM understands meaning, tone, context
   - Returns structured intent + emotion + context
   - Works for ANY human input, not just patterns we anticipated

PHILOSOPHY:
If we're building an AI tutor, we should USE AI to understand students.
Pattern matching is for routers, not tutors.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class SemanticIntent(Enum):
    """High-level intents that the classifier can detect"""
    # Educational intents
    QUESTION = "question"                    # Asking about a concept
    EXPLANATION_REQUEST = "explanation"      # "Explain X to me"
    PRACTICE_REQUEST = "practice"            # "Give me problems"
    CLARIFICATION = "clarification"          # "I don't understand"
    
    # Emotional/Support intents
    EMOTIONAL_SUPPORT = "emotional_support"  # Bored, frustrated, anxious, etc.
    MOTIVATION_NEED = "motivation"           # "Need support", feeling down
    CONFUSION = "confusion"                  # Lost, stuck, confused
    CELEBRATION = "celebration"              # "Got it!", "Makes sense!"
    
    # Navigation intents
    EXPLORE_NEW = "explore"                  # "Something new", "What's next"
    CONTINUE_PREVIOUS = "continue"           # "Continue", "Where were we"
    GET_HELP = "help"                        # "Help", "What can you do"
    
    # Social intents
    GREETING = "greeting"                    # "Hi", "Hello"
    FAREWELL = "farewell"                    # "Bye", "Thanks, goodbye"
    CHITCHAT = "chitchat"                    # "How are you", jokes, casual
    GRATITUDE = "gratitude"                  # "Thanks", "Great, thanks"
    ACKNOWLEDGMENT = "acknowledgment"        # "Ok", "Got it", "Sure"
    
    # Meta intents
    UNCLEAR = "unclear"                      # Gibberish, typos, unclear
    OFF_TOPIC = "off_topic"                  # Not education-related
    
    # Fallback
    GENERAL = "general"                      # Catch-all for anything else


@dataclass
class SemanticAnalysis:
    """Complete semantic analysis of user input"""
    # Primary classification
    intent: SemanticIntent
    confidence: float  # 0.0 to 1.0
    
    # Emotional analysis
    emotional_tone: str  # positive, negative, neutral, anxious, frustrated, etc.
    emotional_intensity: float  # 0.0 (calm) to 1.0 (intense)
    
    # Context extraction
    topic_mentioned: Optional[str]  # If they mentioned a specific topic
    is_follow_up: bool  # Seems to reference previous conversation
    urgency_level: str  # low, medium, high
    
    # Response guidance
    needs_empathy: bool
    needs_encouragement: bool
    needs_clarification: bool
    suggested_response_style: str  # supportive, educational, casual, formal
    
    # Raw reasoning from LLM
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "emotional_tone": self.emotional_tone,
            "emotional_intensity": self.emotional_intensity,
            "topic_mentioned": self.topic_mentioned,
            "is_follow_up": self.is_follow_up,
            "urgency_level": self.urgency_level,
            "needs_empathy": self.needs_empathy,
            "needs_encouragement": self.needs_encouragement,
            "needs_clarification": self.needs_clarification,
            "suggested_response_style": self.suggested_response_style,
            "reasoning": self.reasoning
        }


class SemanticIntentClassifier:
    """
    LLM-based semantic intent classifier.
    
    This is the INTELLIGENT layer that replaces pattern matching.
    It uses the LLM to actually UNDERSTAND what the student means.
    """
    
    CLASSIFICATION_PROMPT = """You are a semantic analyzer for Druv AI - an intelligent learning companion. Analyze the student's message and classify their intent.

STUDENT MESSAGE: "{message}"

CONVERSATION CONTEXT (if available):
{context}

Analyze this message and return a JSON object with these fields:

1. "intent": One of these exact values:
   - "question" (asking about a concept or topic)
   - "explanation" (wants something explained)
   - "practice" (wants problems/quizzes)
   - "clarification" (doesn't understand something)
   - "emotional_support" (feeling bored, frustrated, anxious, stressed, lonely, sad)
   - "motivation" (needs encouragement, support, feeling down, overwhelmed)
   - "confusion" (lost, stuck, doesn't know what to do)
   - "celebration" (got it, understood, happy about progress)
   - "explore" (wants something new, different topic)
   - "continue" (wants to resume previous topic, asks "where did I stop", "last time", "what were we doing", "continue from before", session recall)
   - "help" (what can you do, how do you work)
   - "greeting" (hi, hello, hey)
   - "farewell" (bye, goodbye, see you)
   - "chitchat" (casual conversation, jokes, how are you, random chat, life talk)
   - "gratitude" (thanks, thank you, appreciate it)
   - "acknowledgment" (ok, sure, got it, yes, no, great, nice)
   - "unclear" (gibberish, typos, can't understand)
   - "off_topic" (non-academic but valid conversation - movies, games, life advice, random questions)
   - "general" (anything else that doesn't fit above)

2. "confidence": 0.0 to 1.0 (how confident you are)

3. "emotional_tone": "positive", "negative", "neutral", "anxious", "frustrated", "excited", "bored", "confused", "lonely", "curious"

4. "emotional_intensity": 0.0 (calm) to 1.0 (intense)

5. "topic_mentioned": The educational topic if mentioned, or null

6. "is_follow_up": true if this seems to reference a previous conversation

7. "urgency_level": "low", "medium", or "high"

8. "needs_empathy": true if the student seems to need emotional support

9. "needs_encouragement": true if they seem to need motivation

10. "needs_clarification": true if their message is unclear and we should ask what they mean

11. "suggested_response_style": "supportive", "educational", "casual", "formal", "encouraging", "friendly"

12. "reasoning": Brief explanation of your classification (1-2 sentences)

CRITICAL UNDERSTANDING:
- Druv AI is a COMPANION, not just a tutor. Students can discuss ANYTHING.
- "off_topic" does NOT mean reject - it means "casual/non-academic conversation"
- Life questions, emotions, random curiosity are ALL valid and should get warm responses
- "I'm feeling lonely", "life sucks", "tell me something interesting" → emotional_support or chitchat
- "need support", "feeling down", "stressed" → motivation or emotional_support
- "great", "nice", "ok", "sure", "hmm yes", "okay" → acknowledgment
- "try something new", "what's next" → explore
- "where did I stop", "last time", "what were we doing", "continue from before", "pick up where we left off" → continue (SESSION RECALL)
- "getting bored", "feeling bored today", "I'm bored" → emotional_support (NOT explore or question!)
- Be GENEROUS in understanding - students express themselves imperfectly
- When in doubt, prefer chitchat or emotional_support over off_topic
- SHORT MESSAGES like "hmm", "yes", "ok" should be acknowledgment, NOT general

Return ONLY valid JSON, no other text."""

    def __init__(self, llm_api_key: str = None):
        self.llm_api_key = llm_api_key or os.environ.get('OPENAI_API_KEY')
        self._client = None
        logger.info("🧠 SemanticIntentClassifier initialized - TRUE AI understanding active")
    
    @property
    def client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.llm_api_key)
            except ImportError:
                logger.error("OpenAI package not installed")
                raise
        return self._client
    
    async def classify(
        self,
        message: str,
        conversation_context: str = "",
        recent_messages: List[Dict[str, str]] = None
    ) -> SemanticAnalysis:
        """
        Classify user intent using LLM semantic understanding.
        
        This is the CORE method that makes our AI actually intelligent.
        """
        # Build context string
        context_parts = []
        if conversation_context:
            context_parts.append(f"Topic being discussed: {conversation_context}")
        if recent_messages:
            recent_str = "\n".join([
                f"{'Student' if m.get('role') == 'user' else 'AI'}: {m.get('content', '')[:100]}"
                for m in recent_messages[-3:]  # Last 3 messages
            ])
            context_parts.append(f"Recent conversation:\n{recent_str}")
        
        context = "\n".join(context_parts) if context_parts else "No prior context available."
        
        # Build prompt
        prompt = self.CLASSIFICATION_PROMPT.format(
            message=message,
            context=context
        )
        
        try:
            # Call LLM for semantic classification
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for classification
                messages=[
                    {"role": "system", "content": "You are a semantic intent classifier. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Clean up JSON (remove markdown if present)
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            # Parse JSON
            result = json.loads(content)
            
            # Convert to SemanticAnalysis
            intent_str = result.get("intent", "general")
            try:
                intent = SemanticIntent(intent_str)
            except ValueError:
                intent = SemanticIntent.GENERAL
            
            analysis = SemanticAnalysis(
                intent=intent,
                confidence=float(result.get("confidence", 0.5)),
                emotional_tone=result.get("emotional_tone", "neutral"),
                emotional_intensity=float(result.get("emotional_intensity", 0.3)),
                topic_mentioned=result.get("topic_mentioned"),
                is_follow_up=bool(result.get("is_follow_up", False)),
                urgency_level=result.get("urgency_level", "medium"),
                needs_empathy=bool(result.get("needs_empathy", False)),
                needs_encouragement=bool(result.get("needs_encouragement", False)),
                needs_clarification=bool(result.get("needs_clarification", False)),
                suggested_response_style=result.get("suggested_response_style", "supportive"),
                reasoning=result.get("reasoning", "")
            )
            
            logger.info(f"🧠 Semantic analysis: intent={intent.value}, tone={analysis.emotional_tone}, "
                       f"confidence={analysis.confidence:.2f}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM classification response: {e}")
            return self._fallback_analysis(message)
        except Exception as e:
            logger.error(f"Semantic classification failed: {e}")
            return self._fallback_analysis(message)
    
    def _fallback_analysis(self, message: str) -> SemanticAnalysis:
        """Fallback when LLM classification fails - still better than pattern matching"""
        # Very basic heuristics as last resort
        message_lower = message.lower().strip()
        
        # Detect obvious patterns only as fallback
        if len(message_lower) <= 2 and not message_lower in ['hi', 'ok', 'no']:
            intent = SemanticIntent.UNCLEAR
        elif any(w in message_lower for w in ['help', 'support', 'stuck', 'confused']):
            intent = SemanticIntent.EMOTIONAL_SUPPORT
        elif any(w in message_lower for w in ['hi', 'hello', 'hey']):
            intent = SemanticIntent.GREETING
        elif any(w in message_lower for w in ['thanks', 'thank']):
            intent = SemanticIntent.GRATITUDE
        elif any(w in message_lower for w in ['ok', 'okay', 'sure', 'great', 'nice', 'good']):
            intent = SemanticIntent.ACKNOWLEDGMENT
        elif '?' in message:
            intent = SemanticIntent.QUESTION
        else:
            intent = SemanticIntent.GENERAL
        
        return SemanticAnalysis(
            intent=intent,
            confidence=0.5,
            emotional_tone="neutral",
            emotional_intensity=0.3,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=True,  # When uncertain, be empathetic
            needs_encouragement=True,
            needs_clarification=len(message_lower) < 5,
            suggested_response_style="supportive",
            reasoning="Fallback classification due to LLM error"
        )


# ============================================
# SINGLETON & FACTORY
# ============================================

_classifier: Optional[SemanticIntentClassifier] = None


def get_semantic_classifier(llm_api_key: str = None) -> SemanticIntentClassifier:
    """Get or create the semantic intent classifier"""
    global _classifier
    if _classifier is None:
        _classifier = SemanticIntentClassifier(llm_api_key)
    return _classifier


# ============================================
# CONVENIENCE FUNCTION
# ============================================

async def classify_intent(
    message: str,
    context: str = "",
    recent_messages: List[Dict[str, str]] = None,
    llm_api_key: str = None
) -> SemanticAnalysis:
    """Convenience function to classify intent"""
    classifier = get_semantic_classifier(llm_api_key)
    return await classifier.classify(message, context, recent_messages)










