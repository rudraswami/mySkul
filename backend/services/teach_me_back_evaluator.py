"""
Teach Me Back v2 — The Most Advanced Learning Verification System
==================================================================

Uses the Feynman technique to verify student understanding:
- Auto-detects when to prompt for explanation (no keywords)
- Evaluates student explanations with rubric-based scoring
- Provides adaptive follow-up questions based on gaps
- Updates mastery ONLY when understanding is demonstrated

COMPONENTS:
1. TeachbackTriggerDetector - Detects learning moments (structure-based)
2. TeachMeBackEvaluator - Rubric-based evaluation
3. TeachbackFollowUpPlanner - Adaptive question selection

Philosophy: Every student is like our own child. Warm, supportive, but honest.
"""
import logging
import json
import re
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


class UnderstandingLevel(Enum):
    """Student understanding classification for adaptive depth."""
    NOT_ATTEMPTED = "not_attempted"      # Student didn't try to explain
    INCORRECT = "incorrect"              # Fundamental misunderstanding  
    PARTIAL = "partial"                  # Some understanding, gaps exist
    GOOD = "good"                        # Solid understanding
    EXCELLENT = "excellent"              # Deep understanding, can teach others


class TeachbackMode(Enum):
    """Type of teachback prompt to use."""
    NONE = "none"                        # Don't trigger
    QUICK_CHECK = "quick_check"          # "Explain in 1-2 lines"
    STEP_CHECK = "step_check"            # "What's the next step?"
    DEEP_TEACH = "deep_teach"            # "Teach it to a friend"


@dataclass
class TeachbackTrigger:
    """Result from trigger detection."""
    should_trigger: bool
    mode: TeachbackMode
    reason: str
    prompt: str
    topic: str
    confidence: float


# =============================================================================
# TEACHBACK TRIGGER DETECTOR — Detects learning moments (NO KEYWORDS)
# =============================================================================

class TeachbackTriggerDetector:
    """
    Detects when to prompt student for explanation.
    
    Uses STRUCTURE-BASED signals, NOT keywords:
    1. Route must be Education Lane (multi_agent, hybrid, react_agentic, visual_sync)
    2. Prior turn was an explanation (AI provided educational content)
    3. Student acknowledged or asked follow-up (short message after explanation)
    4. Confidence/retrieval quality was high (topic was well-covered)
    
    Trigger modes:
    - QUICK_CHECK: After short explanations or definitions
    - STEP_CHECK: After problem-solving explanations
    - DEEP_TEACH: After complex multi-step explanations
    """
    
    # Education lane route types
    EDUCATION_ROUTES = {'multi_agent', 'hybrid', 'react_agentic', 'visual_sync'}
    
    # Cooldown: Don't trigger teachback too often
    MIN_TURNS_BETWEEN_TEACHBACK = 3
    
    def __init__(self):
        # FIXED: Cooldown is now SESSION-ISOLATED: (user_id, session_id) -> turn_count
        self._last_teachback_turn = {}
    
    def detect(
        self,
        route_type: str,
        user_message: str,
        ai_response: str,
        conversation_state: Dict[str, Any],
        retrieval_confidence: float = 0.0,
        user_id: str = None,
        session_id: str = None
    ) -> TeachbackTrigger:
        """
        Detect if this is a good moment for teachback.
        
        Returns TeachbackTrigger with should_trigger, mode, reason, prompt.
        """
        # 1. Must be Education Lane
        if route_type.lower() not in self.EDUCATION_ROUTES:
            return TeachbackTrigger(
                should_trigger=False,
                mode=TeachbackMode.NONE,
                reason="not_education_lane",
                prompt="",
                topic="",
                confidence=0.0
            )
        
        # 2. Check cooldown (SESSION-ISOLATED)
        turn_count = conversation_state.get('turn_count', 0)
        if user_id and session_id:
            # Key is (user_id, session_id) for session isolation
            cooldown_key = (user_id, session_id)
            last_turn = self._last_teachback_turn.get(cooldown_key, -999)
            if turn_count - last_turn < self.MIN_TURNS_BETWEEN_TEACHBACK:
                return TeachbackTrigger(
                    should_trigger=False,
                    mode=TeachbackMode.NONE,
                    reason="cooldown",
                    prompt="",
                    topic="",
                    confidence=0.0
                )
        
        # 3. Detect learning moment signals
        signals = self._detect_learning_signals(
            user_message=user_message,
            ai_response=ai_response,
            conversation_state=conversation_state,
            retrieval_confidence=retrieval_confidence
        )
        
        # 4. Decide if we should trigger
        if signals['trigger_score'] < 0.5:
            return TeachbackTrigger(
                should_trigger=False,
                mode=TeachbackMode.NONE,
                reason="low_signal_score",
                prompt="",
                topic="",
                confidence=signals['trigger_score']
            )
        
        # 5. Determine mode and build prompt
        mode = self._select_mode(signals, ai_response)
        topic = conversation_state.get('last_topic', '') or signals.get('detected_topic', 'this concept')
        prompt = self._build_teachback_prompt(mode, topic, signals)
        
        # Update cooldown tracker (SESSION-ISOLATED)
        if user_id and session_id:
            cooldown_key = (user_id, session_id)
            self._last_teachback_turn[cooldown_key] = turn_count
        
        logger.info(f"🎓 Teachback triggered: mode={mode.value}, topic={topic}, score={signals['trigger_score']:.2f}")
        
        return TeachbackTrigger(
            should_trigger=True,
            mode=mode,
            reason=signals['primary_reason'],
            prompt=prompt,
            topic=topic,
            confidence=signals['trigger_score']
        )
    
    def _detect_learning_signals(
        self,
        user_message: str,
        ai_response: str,
        conversation_state: Dict[str, Any],
        retrieval_confidence: float
    ) -> Dict[str, Any]:
        """
        Detect structure-based learning signals (NOT keyword matching).
        """
        signals = {
            'trigger_score': 0.0,
            'primary_reason': '',
            'detected_topic': '',
            'is_acknowledgment': False,
            'is_short_follow_up': False,
            'prior_was_explanation': False,
            'high_confidence_retrieval': False,
            'response_has_steps': False,
            'response_has_formula': False
        }
        
        msg_lower = user_message.lower().strip()
        msg_len = len(msg_lower)
        word_count = len(msg_lower.split())
        
        # Signal 1: Short acknowledgment after explanation (structure-based)
        # Short message (<20 chars or <5 words) following a longer AI response
        ai_response_len = len(ai_response) if ai_response else 0
        if msg_len < 30 and word_count <= 5 and ai_response_len > 200:
            signals['is_acknowledgment'] = True
            signals['trigger_score'] += 0.3
            signals['primary_reason'] = 'acknowledgment_after_explanation'
        
        # Signal 2: Short question/follow-up after explanation
        if msg_len < 60 and '?' in user_message and ai_response_len > 200:
            signals['is_short_follow_up'] = True
            signals['trigger_score'] += 0.2
            if not signals['primary_reason']:
                signals['primary_reason'] = 'follow_up_question'
        
        # Signal 3: Prior turn was educational explanation
        prior_intent = conversation_state.get('last_intent', '')
        prior_pipeline = conversation_state.get('last_pipeline', '')
        if prior_pipeline in ['multi_agent', 'hybrid', 'react_agentic']:
            signals['prior_was_explanation'] = True
            signals['trigger_score'] += 0.3
            if not signals['primary_reason']:
                signals['primary_reason'] = 'educational_context'
        
        # Signal 4: High retrieval confidence (well-grounded response)
        if retrieval_confidence >= 0.7:
            signals['high_confidence_retrieval'] = True
            signals['trigger_score'] += 0.2
        
        # Signal 5: Response contains steps (numbered/bulleted)
        if ai_response:
            step_patterns = [r'\d+\.', r'\*\*Step', r'First,', r'Second,', r'Then,']
            if any(re.search(p, ai_response) for p in step_patterns):
                signals['response_has_steps'] = True
                signals['trigger_score'] += 0.1
        
        # Signal 6: Response contains formula (educational math)
        if ai_response and any(c in ai_response for c in ['=', '²', '∫', 'Σ', '√']):
            signals['response_has_formula'] = True
            signals['trigger_score'] += 0.1
        
        # Extract topic from conversation state
        signals['detected_topic'] = conversation_state.get('last_topic', '') or \
                                    conversation_state.get('current_subject', '')
        
        # Cap score at 1.0
        signals['trigger_score'] = min(1.0, signals['trigger_score'])
        
        return signals
    
    def _select_mode(self, signals: Dict[str, Any], ai_response: str) -> TeachbackMode:
        """Select appropriate teachback mode based on signals."""
        response_len = len(ai_response) if ai_response else 0
        
        # Deep teach for long, complex responses
        if response_len > 800 or signals.get('response_has_steps'):
            return TeachbackMode.DEEP_TEACH
        
        # Step check for formula-heavy or procedural content
        if signals.get('response_has_formula'):
            return TeachbackMode.STEP_CHECK
        
        # Default to quick check
        return TeachbackMode.QUICK_CHECK
    
    def _build_teachback_prompt(
        self,
        mode: TeachbackMode,
        topic: str,
        signals: Dict[str, Any]
    ) -> str:
        """
        Build a warm, student-first teachback prompt.
        
        DETERMINISTIC selection based on:
        1. TeachbackMode (quick/step/deep)
        2. Signal confidence (high retrieval = more direct prompt)
        3. Message context (acknowledgment vs follow-up)
        
        NO randomization - predictable UX.
        """
        topic_display = topic.replace('_', ' ').title() if topic else "this"
        
        # Determine prompt style based on signals
        high_confidence = signals.get('high_confidence_retrieval', False)
        was_acknowledgment = signals.get('is_acknowledgment', False)
        
        if mode == TeachbackMode.QUICK_CHECK:
            # Short, friendly - for after acknowledgments
            if was_acknowledgment:
                return f"Quick check! 🧠 Can you explain {topic_display} in 1-2 sentences?"
            else:
                return f"Your turn! What's the main idea of {topic_display}? No pressure!"
                
        elif mode == TeachbackMode.STEP_CHECK:
            # Procedural - for formula/step content
            if high_confidence:
                return f"Let's see if it clicked! 🎯 What's the first step to solve this?"
            else:
                return f"Quick test! If I gave you a similar problem, how would you start?"
                
        else:  # DEEP_TEACH
            # Challenge - for complex multi-step
            if high_confidence:
                return f"Challenge time! 🌟 Can you teach {topic_display} back to me like I'm hearing it for the first time?"
            else:
                return f"You're the teacher now! 📚 Explain {topic_display} in your own words."


# =============================================================================
# TEACHBACK FOLLOW-UP PLANNER — Adaptive next question selection
# =============================================================================

class TeachbackFollowUpPlanner:
    """
    Chooses adaptive follow-up based on rubric evaluation.
    
    Strategy:
    - Misconception detected → Targeted correction question
    - Missing concept → Bridging question
    - Good understanding → Transfer question (apply in new context)
    """
    
    def plan_follow_up(
        self,
        evaluation: Dict[str, Any],
        topic: str,
        original_explanation: str
    ) -> Dict[str, Any]:
        """
        Plan the next follow-up based on evaluation results.
        
        Returns:
            {
                'type': 'correction' | 'bridging' | 'transfer' | 'celebration',
                'question': str,
                'focus_area': str,
                'encouragement': str
            }
        """
        score = evaluation.get('score', 50)
        gaps = evaluation.get('gaps', [])
        understood = evaluation.get('understood', [])
        understanding_level = evaluation.get('understanding_level', 'partial')
        
        topic_display = topic.replace('_', ' ').title() if topic else "this concept"
        
        # EXCELLENT: Transfer question (apply to new situation)
        if understanding_level == UnderstandingLevel.EXCELLENT.value or score >= 85:
            return {
                'type': 'transfer',
                'question': f"Amazing explanation! 🌟 Now here's a challenge: Can you think of a real-life example where {topic_display} applies?",
                'focus_area': 'application',
                'encouragement': "You've really got this! Let's see you apply it."
            }
        
        # GOOD: Light extension question
        if understanding_level == UnderstandingLevel.GOOD.value or score >= 70:
            return {
                'type': 'extension',
                'question': f"Great job! 💪 Quick bonus: What would happen if one of the conditions changed in {topic_display}?",
                'focus_area': 'deeper_understanding',
                'encouragement': "You're on the right track. Let's go a bit deeper!"
            }
        
        # PARTIAL with gaps: Bridging question
        if gaps and understanding_level == UnderstandingLevel.PARTIAL.value:
            gap_focus = gaps[0] if isinstance(gaps[0], str) else str(gaps[0])
            return {
                'type': 'bridging',
                'question': f"Good start! 😊 Let's fill in one piece: {gap_focus}. Can you tell me more about that part?",
                'focus_area': gap_focus,
                'encouragement': "You're getting there! Let's clarify this one part."
            }
        
        # INCORRECT: Targeted correction
        if understanding_level == UnderstandingLevel.INCORRECT.value or score < 50:
            # Extract the main misconception
            misconception = gaps[0] if gaps else "the core concept"
            return {
                'type': 'correction',
                'question': f"Let's try a different angle! 🎯 What do you think is the MAIN PURPOSE of {topic_display}? Just one sentence!",
                'focus_area': misconception if isinstance(misconception, str) else 'fundamentals',
                'encouragement': "No worries! Learning takes practice. Let's break it down together."
            }
        
        # NOT_ATTEMPTED: Gentle nudge
        return {
            'type': 'nudge',
            'question': f"Give it a try! 💙 Even a rough attempt helps. What's ONE thing you remember about {topic_display}?",
            'focus_area': 'any_recall',
            'encouragement': "You've got this! Start with whatever comes to mind."
        }


class TeachMeBackEvaluator:
    """
    Evaluates student explanations constructively.
    
    Philosophy:
    - Encourage, don't grade
    - Identify understanding, not just errors
    - Give ONE actionable tip
    - Keep feedback specific and kind
    - VALIDATE correctness - catch misconceptions early
    """
    
    EVALUATION_PROMPT = """You are an intelligent tutor evaluating a student's explanation. Be supportive but HONEST about correctness.

CONCEPT: {concept}

CORRECT EXPLANATION (from AI tutor):
{original_explanation}

STUDENT'S EXPLANATION:
{student_explanation}

Your task: Evaluate their understanding ACCURATELY AND CONSTRUCTIVELY.

IMPORTANT:
1. If their explanation is WRONG, IRRELEVANT, or NONSENSICAL - you MUST point this out gently but clearly
2. If they wrote gibberish, random words, or completely wrong concepts - identify this
3. If they understood correctly, praise specifically what they got right
4. Be encouraging but NEVER fake understanding - that harms learning

Respond in this EXACT JSON format:
{{
    "understood": ["specific point they got right" or "You attempted to explain the concept" if wrong],
    "gaps": ["specific misconception or missing concept" or "The explanation doesn't match the concept" if wrong],
    "tip": "One specific, actionable next step",
    "encouragement": "Warm message (honest based on their actual understanding)"
}}

Examples:
- If student wrote nonsense: gaps = ["The response doesn't relate to the concept"], tip = "Try explaining what the concept means in one sentence"
- If student was close: gaps = ["Missing the part about X"], understood = ["Got Y correct"]
- If student nailed it: gaps = [], understood = [multiple specific points]

Keep each point under 20 words. Be kind but ACCURATE.
"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = config.get("emergent_llm_key") if config else None
    
    async def evaluate(
        self,
        concept: str,
        original_explanation: str,
        student_explanation: str
    ) -> Dict[str, Any]:
        """
        Evaluate a student's explanation INTELLIGENTLY.
        
        Returns:
            {
                "understood": ["what they got right"],
                "gaps": ["what to strengthen or what's wrong"],
                "tip": "one actionable tip",
                "encouragement": "warm but honest message"
            }
        """
        try:
            # Quick validation checks
            student_text = student_explanation.strip()
            
            # Check for empty or too short
            if len(student_text) < 10:
                return {
                    "understood": ["You started writing something"],
                    "gaps": ["Your explanation needs more detail to evaluate"],
                    "tip": "Try writing at least 2-3 sentences explaining the concept",
                    "encouragement": "Give it another try! Explain it like you're teaching a friend.",
                    "score": 20,
                    "understanding_level": UnderstandingLevel.NOT_ATTEMPTED.value
                }
            
            # Check for gibberish (all non-alphabetic or random keysmash)
            alpha_ratio = sum(c.isalpha() for c in student_text) / len(student_text)
            if alpha_ratio < 0.5:
                return {
                    "understood": [],
                    "gaps": ["This doesn't look like a real explanation"],
                    "tip": "Write your explanation in complete sentences",
                    "encouragement": "Take a moment and try explaining the concept in your own words.",
                    "score": 10,
                    "understanding_level": UnderstandingLevel.NOT_ATTEMPTED.value
                }
            
            # Build prompt
            prompt = self.EVALUATION_PROMPT.format(
                concept=concept,
                original_explanation=original_explanation[:1500],  # Limit length
                student_explanation=student_explanation[:1000]
            )
            
            # Use LLM to evaluate with timeout protection
            if self.api_key:
                import asyncio
                try:
                    response = await asyncio.wait_for(
                        call_llm(
                            prompt=prompt,
                            api_key=self.api_key,
                            temperature=0.3,  # Lower temp for consistent evaluation
                            max_tokens=600,
                            system_message="You are a supportive educational evaluator who provides honest, constructive feedback. Always respond in valid JSON format."
                        ),
                        timeout=30.0  # 30 second timeout
                    )
                except asyncio.TimeoutError:
                    logger.warning("LLM evaluation timed out after 30s, using fallback")
                    return self._generate_intelligent_fallback(student_explanation, concept)
                
                # Parse JSON response
                try:
                    # Clean response if needed
                    response_text = response.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.startswith('```'):
                        response_text = response_text[3:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    
                    result = json.loads(response_text.strip())
                    
                    # Validate structure and ensure lists
                    understood = result.get("understood", [])
                    gaps = result.get("gaps", [])
                    
                    # Ensure they're lists
                    if isinstance(understood, str):
                        understood = [understood]
                    if isinstance(gaps, str):
                        gaps = [gaps]
                    
                    feedback = {
                        "understood": understood[:3],  # Max 3 points
                        "gaps": gaps[:3],  # Max 3 gaps
                        "tip": result.get("tip", "Keep practicing explanations!"),
                        "encouragement": result.get("encouragement", "Good effort!")
                    }
                    # Add score and level for mastery tracking
                    feedback["score"] = self._calculate_score(feedback)
                    feedback["understanding_level"] = self._classify_understanding(feedback["score"]).value
                    return feedback
                except json.JSONDecodeError as je:
                    logger.warning(f"Failed to parse LLM response as JSON: {response[:200]}")
                    # Try to extract JSON from response
                    json_match = re.search(r'\{[^{}]*"understood"[^{}]*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(0))
                            feedback = {
                                "understood": result.get("understood", ["You attempted the explanation"]),
                                "gaps": result.get("gaps", []),
                                "tip": result.get("tip", "Keep practicing!"),
                                "encouragement": result.get("encouragement", "Good effort!")
                            }
                            feedback["score"] = self._calculate_score(feedback)
                            feedback["understanding_level"] = self._classify_understanding(feedback["score"]).value
                            return feedback
                        except:
                            pass
                    return self._generate_intelligent_fallback(student_explanation, concept)
            else:
                logger.warning("No API key available for LLM evaluation, using fallback")
                return self._generate_intelligent_fallback(student_explanation, concept)
                
        except Exception as e:
            logger.error(f"TeachMeBack evaluation failed: {e}")
            return self._generate_intelligent_fallback(student_explanation, concept)
    
    def _generate_intelligent_fallback(self, explanation: str, concept: str) -> Dict[str, Any]:
        """
        Generate intelligent fallback feedback when LLM is unavailable.
        Uses heuristics to give reasonable feedback.
        """
        word_count = len(explanation.split())
        words_in_concept = set(concept.lower().split())
        words_in_explanation = set(explanation.lower().split())
        
        # Check overlap between concept and explanation
        overlap = len(words_in_concept.intersection(words_in_explanation))
        
        # Check if they used key educational terms
        educational_terms = ['because', 'therefore', 'means', 'example', 'such as', 'like', 'when', 'how', 'why']
        uses_reasoning = any(term in explanation.lower() for term in educational_terms)
        
        # Too short
        if word_count < 15:
            return {
                "understood": ["You started explaining the concept"],
                "gaps": ["Your explanation needs more depth and detail"],
                "tip": "Try explaining: what it is, why it matters, and give an example",
                "encouragement": "You're on the right track! Add more detail to show your understanding.",
                "score": 35,
                "understanding_level": UnderstandingLevel.INCORRECT.value
            }
        
        # No overlap with concept - likely wrong or off-topic
        elif overlap == 0:
            return {
                "understood": ["You wrote an explanation"],
                "gaps": ["Your explanation doesn't seem to address the concept directly"],
                "tip": f"Make sure to explain what '{concept}' means in your answer",
                "encouragement": "Try again! Think about what the concept really means.",
                "score": 30,
                "understanding_level": UnderstandingLevel.INCORRECT.value
            }
        
        # Good length but lacks reasoning
        elif not uses_reasoning and word_count > 20:
            return {
                "understood": ["You provided detail about the concept"],
                "gaps": ["Try explaining WHY or HOW it works, not just WHAT it is"],
                "tip": "Add words like 'because', 'therefore', or 'for example' to show deeper understanding",
                "encouragement": "You're getting there! Show the reasoning behind the concept.",
                "score": 55,
                "understanding_level": UnderstandingLevel.PARTIAL.value
            }
        
        # Looks decent
        else:
            return {
                "understood": ["You explained the concept with detail", "You used reasoning words to connect ideas"],
                "gaps": [],
                "tip": "Now try teaching this concept to someone who has never heard of it",
                "encouragement": "Well done! Your explanation shows understanding. Keep practicing!",
                "score": 80,
                "understanding_level": UnderstandingLevel.GOOD.value
            }
    
    def _calculate_score(self, feedback: Dict[str, Any]) -> int:
        """
        Calculate understanding score (0-100) based on feedback.
        
        Used for mastery tracking and adaptive depth.
        """
        understood = feedback.get("understood", [])
        gaps = feedback.get("gaps", [])
        
        # Base score from understood points
        understood_score = len(understood) * 30  # Max 90 for 3 points
        
        # Penalty for gaps
        gaps_penalty = len(gaps) * 20  # Max 60 penalty for 3 gaps
        
        # Calculate final score
        score = 40 + understood_score - gaps_penalty  # Base 40 + max 90 - max 60
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _classify_understanding(self, score: int) -> UnderstandingLevel:
        """Classify understanding based on score."""
        if score >= 85:
            return UnderstandingLevel.EXCELLENT
        elif score >= 70:
            return UnderstandingLevel.GOOD
        elif score >= 50:
            return UnderstandingLevel.PARTIAL
        elif score >= 20:
            return UnderstandingLevel.INCORRECT
        else:
            return UnderstandingLevel.NOT_ATTEMPTED
    
    def get_mastery_delta(self, understanding_level: str) -> int:
        """
        Get mastery change based on understanding level.
        
        Used by API to update student mastery after teach-back.
        
        POLICY: No negative deltas from teachback.
        - INCORRECT/NOT_ATTEMPTED → 0 (no change, store misconception tags instead)
        - We don't punish students for trying to explain
        """
        deltas = {
            UnderstandingLevel.EXCELLENT.value: 15,
            UnderstandingLevel.GOOD.value: 10,
            UnderstandingLevel.PARTIAL.value: 3,
            UnderstandingLevel.INCORRECT.value: 0,      # No negative - store misconception instead
            UnderstandingLevel.NOT_ATTEMPTED.value: 0   # No penalty for not trying
        }
        return deltas.get(understanding_level, 0)


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

_evaluator_instance = None
_trigger_detector_instance = None
_follow_up_planner_instance = None


def get_teach_me_back_evaluator(config: Dict[str, Any] = None) -> TeachMeBackEvaluator:
    """Get or create evaluator instance."""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = TeachMeBackEvaluator(config)
    return _evaluator_instance


def get_teachback_trigger_detector() -> TeachbackTriggerDetector:
    """Get or create trigger detector instance."""
    global _trigger_detector_instance
    if _trigger_detector_instance is None:
        _trigger_detector_instance = TeachbackTriggerDetector()
    return _trigger_detector_instance


def get_teachback_follow_up_planner() -> TeachbackFollowUpPlanner:
    """Get or create follow-up planner instance."""
    global _follow_up_planner_instance
    if _follow_up_planner_instance is None:
        _follow_up_planner_instance = TeachbackFollowUpPlanner()
    return _follow_up_planner_instance


# =============================================================================
# TEACHBACK INTEGRATION HELPER — For Orchestrator use
# =============================================================================

async def check_and_build_teachback_payload(
    route_type: str,
    user_message: str,
    ai_response: str,
    conversation_state: Dict[str, Any],
    retrieval_confidence: float = 0.0,
    user_id: str = None,
    session_id: str = None
) -> Optional[Dict[str, Any]]:
    """
    Check if teachback should be triggered and return STRUCTURED payload.
    
    Called by UnifiedAIOrchestrator after educational responses.
    
    IMPORTANT: Returns structured object for UI to render as CTA, NOT a string to append.
    The frontend should render this as a clickable button that opens a modal.
    
    Returns:
        Dict with triggered, mode, topic, cta_text, prompt, guardrail_status
        or None if no teachback.
    """
    detector = get_teachback_trigger_detector()
    
    trigger = detector.detect(
        route_type=route_type,
        user_message=user_message,
        ai_response=ai_response,
        conversation_state=conversation_state,
        retrieval_confidence=retrieval_confidence,
        user_id=user_id,
        session_id=session_id
    )
    
    if trigger.should_trigger:
        logger.info(f"🎓 Teachback triggered: mode={trigger.mode.value}, reason={trigger.reason}")
        return {
            'triggered': True,
            'mode': trigger.mode.value,
            'topic': trigger.topic,
            'cta_text': "Think you got it? Try explaining it back",
            'prompt': trigger.prompt,
            'confidence': trigger.confidence,
            'reason': trigger.reason
        }
    
    return None


# DEPRECATED: Keep for backward compatibility but log warning
async def check_and_build_teachback_prompt(
    route_type: str,
    user_message: str,
    ai_response: str,
    conversation_state: Dict[str, Any],
    retrieval_confidence: float = 0.0,
    user_id: str = None,
    session_id: str = None
) -> Optional[str]:
    """
    DEPRECATED: Use check_and_build_teachback_payload instead.
    
    This function appends text to main_response which breaks the UX contract.
    Kept for backward compatibility - returns None to prevent text appending.
    """
    logger.warning("⚠️ check_and_build_teachback_prompt is deprecated. Use check_and_build_teachback_payload.")
    # Return None to prevent any text appending - the new API should be used
    return None


async def process_teachback_response(
    student_explanation: str,
    topic: str,
    original_explanation: str,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process student's teachback response end-to-end.
    
    Returns:
        {
            'evaluation': {...},  # Rubric scores
            'follow_up': {...},   # Next question
            'mastery_delta': int, # Delta to apply (only if threshold met, NEVER negative)
            'should_update_mastery': bool,
            'misconception_tags': list,  # For memory storage on low scores
            'memory_event': dict  # Compact event for Memory v2
        }
    """
    evaluator = get_teach_me_back_evaluator(config)
    planner = get_teachback_follow_up_planner()
    
    # 1. Evaluate the explanation
    evaluation = await evaluator.evaluate(
        concept=topic,
        original_explanation=original_explanation,
        student_explanation=student_explanation
    )
    
    # 2. Plan adaptive follow-up
    follow_up = planner.plan_follow_up(
        evaluation=evaluation,
        topic=topic,
        original_explanation=original_explanation
    )
    
    # 3. Determine mastery update eligibility
    # POLICY: Only update if score >= 50 AND student provided explanation
    # POLICY: NEVER apply negative delta from teachback
    score = evaluation.get('score', 0)
    understanding_level = evaluation.get('understanding_level', 'not_attempted')
    gaps = evaluation.get('gaps', [])
    
    # Check if student actually provided meaningful explanation (>10 chars)
    has_explanation = len(student_explanation.strip()) > 10
    
    should_update = (
        score >= 50 and 
        has_explanation and 
        understanding_level not in ['not_attempted', 'incorrect']
    )
    
    # Get delta (will be 0 for incorrect/not_attempted due to policy)
    mastery_delta = evaluator.get_mastery_delta(understanding_level) if should_update else 0
    
    # Extract misconception tags for low scores (stored in memory, not mastery)
    misconception_tags = []
    if score < 50 and gaps:
        # Convert gaps to compact tags
        misconception_tags = [
            g[:50] if isinstance(g, str) else str(g)[:50] 
            for g in gaps[:3]
        ]
    
    # Build compact memory event (bounded storage)
    memory_event = {
        'type': 'teachback',
        'topic': topic[:100],
        'score': score,
        'level': understanding_level,
        'mastery_delta': mastery_delta,
        'misconceptions': misconception_tags,
        'follow_up_type': follow_up['type'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"🎓 Teachback processed: score={score}, level={understanding_level}, "
                f"mastery_delta={mastery_delta}, misconceptions={len(misconception_tags)}, "
                f"follow_up_type={follow_up['type']}")
    
    return {
        'evaluation': evaluation,
        'follow_up': follow_up,
        'mastery_delta': mastery_delta,
        'should_update_mastery': should_update,
        'misconception_tags': misconception_tags,
        'memory_event': memory_event
    }

