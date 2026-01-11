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
    
    # DYNAMIC ACTION DETECTION (LLM-determined, NOT keyword-based)
    # This allows the system to understand when user wants something CREATED/DONE
    has_actionable_request: bool = False  # User wants a specific deliverable created
    requested_output_type: Optional[str] = None  # What the user wants: "study_plan", "solution", "schedule", etc.
    
    # ==========================================================================
    # 🆕 SCOPE-AWARE RESPONSE FIELDS (Proportional Response System)
    # ==========================================================================
    # These fields enable the system to answer PROPORTIONALLY to what was asked,
    # avoiding the "maximum output" behavior where small questions get large responses.
    
    # What kind of response does the student expect?
    response_expectation: str = "conversational_advice"
    # Options:
    # - "conversational_advice": Quick suggestion/opinion (mentor advice)
    # - "detailed_explanation": Teach me something in depth
    # - "structured_deliverable": Create an artifact (plan, schedule, solution)
    # - "emotional_acknowledgment": Support/empathy response
    
    # What's the time scope of the question?
    temporal_scope: str = "unspecified"
    # Options:
    # - "immediate": Right now, this moment
    # - "today": Just today
    # - "this_week": Short-term (few days)
    # - "long_term": Exam prep, multi-week planning
    # - "unspecified": No clear time reference
    
    # How should the response be delivered?
    delivery_mode: str = "conversational"
    # Options:
    # - "conversational": Like a friend talking (natural language)
    # - "structured": Organized with sections (but not formal)
    # - "formal": Document-like deliverable with headers
    
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
            "reasoning": self.reasoning,
            "has_actionable_request": self.has_actionable_request,
            "requested_output_type": self.requested_output_type,
            # Scope-aware fields
            "response_expectation": self.response_expectation,
            "temporal_scope": self.temporal_scope,
            "delivery_mode": self.delivery_mode
        }


class SemanticIntentClassifier:
    """
    LLM-based semantic intent classifier.
    
    This is the INTELLIGENT layer that replaces pattern matching.
    It uses the LLM to actually UNDERSTAND what the student means.
    """
    
    CLASSIFICATION_PROMPT = """You are a semantic analyzer for MySckul - an intelligent learning companion. Analyze the student's message and classify their intent.

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
   - "continue" (wants to resume previous topic, session recall)
   - "help" (asking about capabilities: "what can you do", "how do you work")
   - "greeting" (hi, hello, hey)
   - "farewell" (bye, goodbye, see you)
   - "chitchat" (casual conversation, jokes, how are you)
   - "gratitude" (thanks, thank you)
   - "acknowledgment" (ok, sure, got it, yes, no, great, nice)
   - "unclear" (gibberish, typos, can't understand)
   - "off_topic" (non-academic but valid conversation)
   - "general" (anything else)

2. "confidence": 0.0 to 1.0

3. "emotional_tone": "positive", "negative", "neutral", "anxious", "frustrated", "excited", "bored", "confused", "lonely", "curious"

4. "emotional_intensity": 0.0 (calm) to 1.0 (intense)

5. "topic_mentioned": The educational topic if mentioned, or null

6. "is_follow_up": true if this references a previous conversation

7. "urgency_level": "low", "medium", or "high"
   
   URGENCY DETECTION EXAMPLES (CRITICAL):
   - HIGH: "exam tomorrow", "viva in 2 hours", "test in the morning", "interview tonight", "quick revision", "last minute tips", "quick tips", any mention of imminent deadline
   - MEDIUM: "exam next week", "preparing for test", general study questions
   - LOW: "want to learn", "curious about", no time pressure mentioned
   
   KEY RULE: Any mention of "tomorrow", "today", "tonight", "in X hours", "quick", "last minute", or other imminent time = HIGH urgency

8. "needs_empathy": true if the student needs emotional support

9. "needs_encouragement": true if they need motivation

10. "needs_clarification": true if their message is unclear

11. "suggested_response_style": "supportive", "educational", "casual", "formal", "encouraging", "friendly"

12. "reasoning": Brief explanation (1-2 sentences)

=== CRITICAL: SCOPE-AWARE RESPONSE FIELDS ===
These fields determine HOW MUCH to respond - matching response scope to question scope.

13. "response_expectation": What kind of response does the student expect?
    - "conversational_advice": Quick suggestion, mentor opinion, brief guidance
    - "detailed_explanation": Wants to learn something in depth
    - "structured_deliverable": Wants an ARTIFACT created (plan, schedule, solution document)
    - "emotional_acknowledgment": Needs support/empathy response
    
    KEY DISTINCTION:
    - "What should I study today?" → conversational_advice (wants quick suggestion)
    - "Create a study plan for my exam" → structured_deliverable (wants artifact)
    - "What do you think I should focus on?" → conversational_advice (wants opinion)
    - "Make me a 7-day revision schedule" → structured_deliverable (wants document)

14. "temporal_scope": What time frame is the question about?
    - "immediate": Right now, this moment
    - "today": Just today
    - "this_week": Short-term (few days)
    - "long_term": Exam prep, multi-week planning
    - "unspecified": No clear time reference
    
    EXAMPLES:
    - "What should I study today?" → "today"
    - "Plan my exam prep" → "long_term"
    - "What should I do now?" → "immediate"
    - "What should I study?" → "unspecified"

15. "delivery_mode": How should the response be formatted?
    - "conversational": Like a friend talking, natural sentences
    - "structured": Organized but not formal (bullet points okay)
    - "formal": Document-like with headers, sections, tables

=== ACTIONABLE REQUEST DETECTION ===
16. "has_actionable_request": true/false
    - TRUE ONLY if user wants a STRUCTURED DELIVERABLE created
    - "Create a plan", "Make a schedule", "Build a timetable" → TRUE
    - "What should I study?", "Any suggestions?", "What do you think?" → FALSE (advice, not deliverable)
    
17. "requested_output_type": null or one of:
    - "study_plan" (ONLY for explicit: "create plan", "make schedule", "build timetable")
    - "problem_solution" (wants a problem solved step-by-step)
    - "quiz" (wants practice questions generated)
    - "summary" (wants notes/summary created)
    - null (no deliverable requested, just wants advice/explanation)

=== CRITICAL EXAMPLES ===
"What should I study today?"
→ response_expectation: "conversational_advice"
→ temporal_scope: "today"
→ delivery_mode: "conversational"
→ has_actionable_request: FALSE (asking for advice, not a plan)
→ requested_output_type: null

"Create a study plan for my Physics exam next week"
→ response_expectation: "structured_deliverable"
→ temporal_scope: "this_week"
→ delivery_mode: "formal"
→ has_actionable_request: TRUE
→ requested_output_type: "study_plan"

"What do you think I should focus on?"
→ response_expectation: "conversational_advice"
→ temporal_scope: "unspecified"
→ delivery_mode: "conversational"
→ has_actionable_request: FALSE
→ requested_output_type: null

"I have 2 hours, what should I do?"
→ response_expectation: "conversational_advice"
→ temporal_scope: "immediate"
→ delivery_mode: "conversational"
→ has_actionable_request: FALSE
→ requested_output_type: null

"Make me a revision timetable for the next 10 days"
→ response_expectation: "structured_deliverable"
→ temporal_scope: "this_week"
→ delivery_mode: "formal"
→ has_actionable_request: TRUE
→ requested_output_type: "study_plan"

=== URGENT QUERY EXAMPLE (CRITICAL) ===
"Quick revision tips for exam tomorrow"
→ response_expectation: "conversational_advice"
→ temporal_scope: "today"
→ delivery_mode: "structured" (NOT conversational - urgent needs structure!)
→ urgency_level: "high" (CRITICAL - "tomorrow" = imminent deadline)
→ has_actionable_request: FALSE
→ requested_output_type: null

"Last minute tips for my viva in 2 hours"
→ urgency_level: "high" (CRITICAL - imminent)
→ temporal_scope: "immediate"
→ needs_encouragement: true

Return ONLY valid JSON, no other text."""

    def __init__(self, llm_api_key: str = None):
        self.llm_api_key = llm_api_key or os.environ.get('OPENAI_API_KEY')
        self._client = None
        if not self.llm_api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set - semantic classification will use fallback")
        else:
            logger.info("🧠 SemanticIntentClassifier initialized - TRUE AI understanding active")
    
    @property
    def client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            if not self.llm_api_key:
                raise ValueError("OPENAI_API_KEY not configured - cannot use semantic classification")
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
                reasoning=result.get("reasoning", ""),
                # Dynamic actionable request detection
                has_actionable_request=bool(result.get("has_actionable_request", False)),
                requested_output_type=result.get("requested_output_type"),
                # 🆕 SCOPE-AWARE RESPONSE FIELDS
                response_expectation=result.get("response_expectation", "conversational_advice"),
                temporal_scope=result.get("temporal_scope", "unspecified"),
                delivery_mode=result.get("delivery_mode", "conversational")
            )
            
            logger.info(f"🧠 Semantic analysis: intent={intent.value}, tone={analysis.emotional_tone}, "
                       f"confidence={analysis.confidence:.2f}, "
                       f"response_expectation={analysis.response_expectation}, "
                       f"temporal_scope={analysis.temporal_scope}, "
                       f"actionable={analysis.has_actionable_request}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM classification response: {e}")
            return self._fallback_analysis(message)
        except Exception as e:
            logger.error(f"Semantic classification failed: {e}")
            return self._fallback_analysis(message)
    
    def _fallback_analysis(self, message: str) -> SemanticAnalysis:
        """
        Fallback when LLM classification fails.
        
        PHASE B FIX: When ENABLE_SEMANTIC_ONLY_ROUTING is True, returns GENERAL
        intent with low confidence instead of keyword matching. Downstream
        handlers will ask a clarifying question when confidence is low.
        """
        from core.config import settings
        message_lower = message.lower().strip()
        
        # PHASE B: No keyword matching when semantic-only mode is enabled
        if settings.ENABLE_SEMANTIC_ONLY_ROUTING:
            # Return GENERAL with very low confidence
            # This signals downstream to ask for clarification
            intent = SemanticIntent.GENERAL
            confidence = 0.15  # Very low - triggers clarification path
            reasoning = "LLM classification failed - returning GENERAL with low confidence for clarification"
            
            # Only structural detection (not keywords)
            if len(message_lower) <= 2:
                intent = SemanticIntent.UNCLEAR
                reasoning = "Very short message (<=2 chars) - unclear"
            elif '?' in message and len(message) > 5:
                intent = SemanticIntent.QUESTION
                confidence = 0.3
                reasoning = "Question mark detected - likely a question"
            
            return SemanticAnalysis(
                intent=intent,
                confidence=confidence,
                emotional_tone="neutral",
                emotional_intensity=0.3,
                topic_mentioned=None,
                is_follow_up=False,
                urgency_level="medium",
                needs_empathy=True,
                needs_encouragement=True,
                needs_clarification=confidence < 0.3,  # Ask for clarification when uncertain
                suggested_response_style="supportive",
                reasoning=reasoning,
                # Default scope-aware fields for fallback
                response_expectation="conversational_advice",
                temporal_scope="unspecified",
                delivery_mode="conversational"
            )
        
        # LEGACY: Keyword-based fallback (only when flag disabled)
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
            reasoning="Fallback classification (legacy keyword mode)"
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










