"""
Teach Me Back Evaluator
=======================

Evaluates student explanations using the Feynman technique.
Focus: What did they understand? What should they strengthen?

NOT a grading system. It's a learning helper.
"""
import logging
import json
import re
from typing import Dict, Any, List
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


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
                    "encouragement": "Give it another try! Explain it like you're teaching a friend."
                }
            
            # Check for gibberish (all non-alphabetic or random keysmash)
            alpha_ratio = sum(c.isalpha() for c in student_text) / len(student_text)
            if alpha_ratio < 0.5:
                return {
                    "understood": [],
                    "gaps": ["This doesn't look like a real explanation"],
                    "tip": "Write your explanation in complete sentences",
                    "encouragement": "Take a moment and try explaining the concept in your own words."
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
                    
                    return {
                        "understood": understood[:3],  # Max 3 points
                        "gaps": gaps[:3],  # Max 3 gaps
                        "tip": result.get("tip", "Keep practicing explanations!"),
                        "encouragement": result.get("encouragement", "Good effort!")
                    }
                except json.JSONDecodeError as je:
                    logger.warning(f"Failed to parse LLM response as JSON: {response[:200]}")
                    # Try to extract JSON from response
                    json_match = re.search(r'\{[^{}]*"understood"[^{}]*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(0))
                            return {
                                "understood": result.get("understood", ["You attempted the explanation"]),
                                "gaps": result.get("gaps", []),
                                "tip": result.get("tip", "Keep practicing!"),
                                "encouragement": result.get("encouragement", "Good effort!")
                            }
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
                "encouragement": "You're on the right track! Add more detail to show your understanding."
            }
        
        # No overlap with concept - likely wrong or off-topic
        elif overlap == 0:
            return {
                "understood": ["You wrote an explanation"],
                "gaps": ["Your explanation doesn't seem to address the concept directly"],
                "tip": f"Make sure to explain what '{concept}' means in your answer",
                "encouragement": "Try again! Think about what the concept really means."
            }
        
        # Good length but lacks reasoning
        elif not uses_reasoning and word_count > 20:
            return {
                "understood": ["You provided detail about the concept"],
                "gaps": ["Try explaining WHY or HOW it works, not just WHAT it is"],
                "tip": "Add words like 'because', 'therefore', or 'for example' to show deeper understanding",
                "encouragement": "You're getting there! Show the reasoning behind the concept."
            }
        
        # Looks decent
        else:
            return {
                "understood": ["You explained the concept with detail", "You used reasoning words to connect ideas"],
                "gaps": [],
                "tip": "Now try teaching this concept to someone who has never heard of it",
                "encouragement": "Well done! Your explanation shows understanding. Keep practicing!"
            }


# Singleton instance
_evaluator_instance = None

def get_teach_me_back_evaluator(config: Dict[str, Any] = None) -> TeachMeBackEvaluator:
    """Get or create evaluator instance."""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = TeachMeBackEvaluator(config)
    return _evaluator_instance


