"""
Teach Me Back Evaluator
=======================

Evaluates student explanations using the Feynman technique.
Focus: What did they understand? What should they strengthen?

NOT a grading system. It's a learning helper.

ENHANCED (v2.0):
- Now includes understanding score (0-100)
- Understanding level classification
- Mastery update support for adaptive depth
"""
import logging
import json
import re
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


class UnderstandingLevel(Enum):
    """Student understanding classification for adaptive depth."""
    NOT_ATTEMPTED = "not_attempted"      # Student didn't try to explain
    INCORRECT = "incorrect"              # Fundamental misunderstanding  
    PARTIAL = "partial"                  # Some understanding, gaps exist
    GOOD = "good"                        # Solid understanding
    EXCELLENT = "excellent"              # Deep understanding, can teach others


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
        """
        deltas = {
            UnderstandingLevel.EXCELLENT.value: 15,
            UnderstandingLevel.GOOD.value: 10,
            UnderstandingLevel.PARTIAL.value: 3,
            UnderstandingLevel.INCORRECT.value: -5,
            UnderstandingLevel.NOT_ATTEMPTED.value: 0
        }
        return deltas.get(understanding_level, 0)


# Singleton instance
_evaluator_instance = None

def get_teach_me_back_evaluator(config: Dict[str, Any] = None) -> TeachMeBackEvaluator:
    """Get or create evaluator instance."""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = TeachMeBackEvaluator(config)
    return _evaluator_instance


