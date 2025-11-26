"""
Intelligent Response Engine
Generates ADAPTIVE responses like ChatGPT/Gemini - NOT a fixed template!

Key Principle: The AI decides what blocks to include based on the question type.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class QuestionIntent(Enum):
    """Detected intent types"""
    GREETING = "greeting"
    SIMPLE_FACT = "simple_fact"
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    CALCULATION = "calculation"
    DERIVATION = "derivation"
    PROCESS = "process"
    EXAMPLE = "example"
    PRACTICE = "practice"
    REVISION = "revision"
    CONFUSION = "confusion"
    VERIFICATION = "verification"
    FOLLOW_UP = "follow_up"
    CONVERSATIONAL = "conversational"


class ResponseBlock(Enum):
    """Available response blocks - AI chooses which to include"""
    DIRECT_ANSWER = "direct_answer"
    SHORT_SUMMARY = "short_summary"
    EXPLANATION = "explanation"
    STEP_BY_STEP = "step_by_step"
    EXAMPLE = "example"
    VISUAL = "visual"
    MEMORY_HOOK = "memory_hook"
    FORMULA_BOX = "formula_box"
    COMMON_MISTAKES = "common_mistakes"
    EXAM_TIPS = "exam_tips"
    FOLLOW_UP = "follow_up"
    COMPARISON_TABLE = "comparison_table"
    ANALOGY = "analogy"


# Topics that benefit from visuals
VISUAL_TOPICS = {
    'physics': ['force', 'motion', 'gravity', 'friction', 'wave', 'light', 'electricity', 'circuit', 'momentum', 'energy', 'projectile'],
    'chemistry': ['atom', 'molecule', 'bond', 'reaction', 'electron', 'orbital', 'periodic'],
    'biology': ['cell', 'photosynthesis', 'respiration', 'dna', 'mitosis', 'meiosis', 'heart', 'digestion'],
    'mathematics': ['triangle', 'circle', 'graph', 'geometry', 'pythagoras', 'coordinate', 'function', 'parabola'],
}


def detect_intent(question: str, context: Dict[str, Any] = None) -> QuestionIntent:
    """
    Detect the intent/type of the question to determine response structure.
    """
    q = question.lower().strip()
    
    # Greeting patterns
    if q.strip('!?.') in ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo', 'good morning', 'good evening']:
        return QuestionIntent.GREETING
    
    # Conversational/casual
    if any(p in q for p in ['how are you', 'what\'s up', 'thank', 'thanks', 'okay', 'ok', 'got it', 'understood']):
        return QuestionIntent.CONVERSATIONAL
    
    # Verification
    if any(p in q for p in ['is this correct', 'am i right', 'check this', 'verify']):
        return QuestionIntent.VERIFICATION
    
    # Calculation/solve
    if any(p in q for p in ['solve', 'calculate', 'find the value', 'evaluate', 'compute', '=']):
        return QuestionIntent.CALCULATION
    
    # Derivation
    if any(p in q for p in ['derive', 'derivation', 'prove', 'proof', 'show that']):
        return QuestionIntent.DERIVATION
    
    # Comparison
    if any(p in q for p in ['difference between', 'compare', 'vs', 'versus', 'distinguish']):
        return QuestionIntent.COMPARISON
    
    # Process/steps
    if any(p in q for p in ['process', 'steps', 'procedure', 'how does', 'mechanism']):
        return QuestionIntent.PROCESS
    
    # Example request
    if any(p in q for p in ['give example', 'example of', 'for example', 'real life example', 'practical example']):
        return QuestionIntent.EXAMPLE
    
    # Practice
    if any(p in q for p in ['practice', 'question', 'problem', 'exercise', 'quiz']):
        return QuestionIntent.PRACTICE
    
    # Revision/summary
    if any(p in q for p in ['revision', 'revise', 'summary', 'summarize', 'quick recap']):
        return QuestionIntent.REVISION
    
    # Confusion/help
    if any(p in q for p in ['confused', 'don\'t understand', 'help', 'stuck', 'difficult', 'hard']):
        return QuestionIntent.CONFUSION
    
    # Definition (what is)
    if any(p in q for p in ['what is', 'what are', 'define', 'definition', 'meaning of']):
        return QuestionIntent.DEFINITION
    
    # Explanation (why/how)
    if any(p in q for p in ['explain', 'why', 'how', 'describe', 'elaborate']):
        return QuestionIntent.EXPLANATION
    
    # Simple fact
    if any(p in q for p in ['who', 'when', 'where', 'which', 'name the', 'list']):
        return QuestionIntent.SIMPLE_FACT
    
    # Default to explanation
    return QuestionIntent.EXPLANATION


def should_include_visual(question: str, subject: str = None) -> bool:
    """
    Determine if this topic would benefit from a visual.
    Only return True for topics where diagrams actually help understanding.
    """
    q = question.lower()
    
    # Check subject-specific visual topics
    if subject:
        subject_lower = subject.lower()
        visual_keywords = VISUAL_TOPICS.get(subject_lower, [])
        if any(keyword in q for keyword in visual_keywords):
            return True
    
    # Check all subjects
    for subject_keywords in VISUAL_TOPICS.values():
        if any(keyword in q for keyword in subject_keywords):
            return True
    
    # Topics that generally DON'T need visuals
    no_visual_patterns = [
        'history', 'date', 'year', 'who', 'when', 'define', 'meaning',
        'formula', 'equation', 'law', 'theorem', 'principle',
        'gandhi', 'nehru', 'freedom', 'movement', 'war', 'battle',
        'literature', 'poem', 'story', 'author', 'grammar',
    ]
    
    if any(p in q for p in no_visual_patterns):
        return False
    
    return False


def get_response_blocks(intent: QuestionIntent, question: str, subject: str = None) -> List[ResponseBlock]:
    """
    Decide which response blocks to include based on intent.
    This is the INTELLIGENT part - different questions get different structures!
    """
    blocks = []
    
    # GREETING - Just a friendly response, nothing more
    if intent == QuestionIntent.GREETING:
        return [ResponseBlock.DIRECT_ANSWER]
    
    # CONVERSATIONAL - Keep it casual
    if intent == QuestionIntent.CONVERSATIONAL:
        return [ResponseBlock.DIRECT_ANSWER]
    
    # SIMPLE FACT - Direct answer only
    if intent == QuestionIntent.SIMPLE_FACT:
        return [ResponseBlock.DIRECT_ANSWER]
    
    # VERIFICATION - Direct answer + explanation if wrong
    if intent == QuestionIntent.VERIFICATION:
        return [ResponseBlock.DIRECT_ANSWER, ResponseBlock.EXPLANATION]
    
    # CALCULATION - Step by step solution
    if intent == QuestionIntent.CALCULATION:
        blocks = [ResponseBlock.STEP_BY_STEP]
        if should_include_visual(question, subject):
            blocks.append(ResponseBlock.VISUAL)
        blocks.append(ResponseBlock.FOLLOW_UP)
        return blocks
    
    # DERIVATION - Full derivation steps
    if intent == QuestionIntent.DERIVATION:
        return [ResponseBlock.STEP_BY_STEP, ResponseBlock.FORMULA_BOX, ResponseBlock.EXAM_TIPS]
    
    # COMPARISON - Table format
    if intent == QuestionIntent.COMPARISON:
        return [ResponseBlock.SHORT_SUMMARY, ResponseBlock.COMPARISON_TABLE, ResponseBlock.FOLLOW_UP]
    
    # PROCESS - Steps + optional visual
    if intent == QuestionIntent.PROCESS:
        blocks = [ResponseBlock.EXPLANATION, ResponseBlock.STEP_BY_STEP]
        if should_include_visual(question, subject):
            blocks.append(ResponseBlock.VISUAL)
        return blocks
    
    # EXAMPLE - Give examples
    if intent == QuestionIntent.EXAMPLE:
        return [ResponseBlock.EXAMPLE, ResponseBlock.FOLLOW_UP]
    
    # PRACTICE - Questions
    if intent == QuestionIntent.PRACTICE:
        return [ResponseBlock.DIRECT_ANSWER, ResponseBlock.FOLLOW_UP]
    
    # REVISION - Summary + memory hooks
    if intent == QuestionIntent.REVISION:
        return [ResponseBlock.SHORT_SUMMARY, ResponseBlock.FORMULA_BOX, ResponseBlock.MEMORY_HOOK, ResponseBlock.COMMON_MISTAKES]
    
    # CONFUSION - Empathetic + simple explanation + analogy
    if intent == QuestionIntent.CONFUSION:
        blocks = [ResponseBlock.DIRECT_ANSWER, ResponseBlock.ANALOGY, ResponseBlock.EXPLANATION]
        if should_include_visual(question, subject):
            blocks.append(ResponseBlock.VISUAL)
        blocks.append(ResponseBlock.FOLLOW_UP)
        return blocks
    
    # DEFINITION - Short answer + explanation
    if intent == QuestionIntent.DEFINITION:
        blocks = [ResponseBlock.DIRECT_ANSWER]
        # Only add more for complex topics
        if len(question) > 30 or any(w in question.lower() for w in ['explain', 'detail', 'elaborate']):
            blocks.append(ResponseBlock.EXPLANATION)
            if should_include_visual(question, subject):
                blocks.append(ResponseBlock.VISUAL)
        return blocks
    
    # EXPLANATION - Full explanation
    if intent == QuestionIntent.EXPLANATION:
        blocks = [ResponseBlock.EXPLANATION]
        if should_include_visual(question, subject):
            blocks.append(ResponseBlock.VISUAL)
        blocks.append(ResponseBlock.EXAMPLE)
        blocks.append(ResponseBlock.FOLLOW_UP)
        return blocks
    
    # Default
    return [ResponseBlock.DIRECT_ANSWER, ResponseBlock.EXPLANATION]


def get_response_config(question: str, subject: str = None, context: Dict = None) -> Dict[str, Any]:
    """
    Main function to get the response configuration.
    Returns which blocks to include and rendering hints.
    """
    intent = detect_intent(question, context)
    blocks = get_response_blocks(intent, question, subject)
    include_visual = should_include_visual(question, subject)
    
    # Response length based on intent
    length_map = {
        QuestionIntent.GREETING: "minimal",
        QuestionIntent.CONVERSATIONAL: "minimal",
        QuestionIntent.SIMPLE_FACT: "short",
        QuestionIntent.VERIFICATION: "short",
        QuestionIntent.DEFINITION: "medium",
        QuestionIntent.EXAMPLE: "medium",
        QuestionIntent.EXPLANATION: "detailed",
        QuestionIntent.CALCULATION: "detailed",
        QuestionIntent.DERIVATION: "detailed",
        QuestionIntent.COMPARISON: "detailed",
        QuestionIntent.PROCESS: "detailed",
        QuestionIntent.REVISION: "medium",
        QuestionIntent.CONFUSION: "detailed",
        QuestionIntent.PRACTICE: "medium",
    }
    
    # Tone based on intent
    tone_map = {
        QuestionIntent.GREETING: "friendly",
        QuestionIntent.CONVERSATIONAL: "casual",
        QuestionIntent.CONFUSION: "empathetic",
        QuestionIntent.CALCULATION: "technical",
        QuestionIntent.DERIVATION: "academic",
        QuestionIntent.REVISION: "concise",
    }
    
    return {
        "intent": intent.value,
        "blocks": [b.value for b in blocks],
        "include_visual": include_visual,
        "response_length": length_map.get(intent, "medium"),
        "tone": tone_map.get(intent, "balanced"),
        "render_directives": {
            "show_quick_answer": ResponseBlock.DIRECT_ANSWER in blocks or ResponseBlock.SHORT_SUMMARY in blocks,
            "show_explanation": ResponseBlock.EXPLANATION in blocks,
            "show_visual": include_visual and ResponseBlock.VISUAL in blocks,
            "show_memory_hook": ResponseBlock.MEMORY_HOOK in blocks,
            "show_formula_box": ResponseBlock.FORMULA_BOX in blocks,
            "show_steps": ResponseBlock.STEP_BY_STEP in blocks,
            "show_examples": ResponseBlock.EXAMPLE in blocks,
            "show_comparison": ResponseBlock.COMPARISON_TABLE in blocks,
            "show_follow_up": ResponseBlock.FOLLOW_UP in blocks,
            "show_exam_tips": ResponseBlock.EXAM_TIPS in blocks,
            "show_common_mistakes": ResponseBlock.COMMON_MISTAKES in blocks,
        }
    }


def build_adaptive_prompt(question: str, config: Dict[str, Any], subject: str = None, student_profile: Dict = None) -> str:
    """
    Build an adaptive prompt for the LLM based on the response configuration.
    The LLM only generates content for the blocks that are needed.
    """
    intent = config["intent"]
    blocks = config["blocks"]
    tone = config["tone"]
    length = config["response_length"]
    
    # Build block instructions
    block_instructions = []
    
    if "direct_answer" in blocks or "short_summary" in blocks:
        block_instructions.append("• Start with a DIRECT, concise answer to the question.")
    
    if "explanation" in blocks:
        block_instructions.append("• Provide a clear explanation with relevant details.")
    
    if "step_by_step" in blocks:
        block_instructions.append("• Show step-by-step solution/process with clear numbering.")
    
    if "example" in blocks:
        block_instructions.append("• Include a practical, relatable example.")
    
    if "analogy" in blocks:
        block_instructions.append("• Use a simple analogy to make the concept relatable.")
    
    if "formula_box" in blocks:
        block_instructions.append("• Include relevant formulas clearly formatted.")
    
    if "memory_hook" in blocks:
        block_instructions.append("• Add a memory trick or mnemonic to help remember.")
    
    if "common_mistakes" in blocks:
        block_instructions.append("• Mention 1-2 common mistakes students make.")
    
    if "exam_tips" in blocks:
        block_instructions.append("• Add exam-relevant tips or marking scheme hints.")
    
    if "follow_up" in blocks:
        block_instructions.append("• End with a follow-up question or suggestion for further learning.")
    
    # Length instructions
    length_instructions = {
        "minimal": "Keep the response very brief - 1-2 sentences max.",
        "short": "Keep the response concise - 2-4 sentences.",
        "medium": "Provide a moderate-length response - cover the essentials.",
        "detailed": "Provide a comprehensive response with full details.",
    }
    
    # Tone instructions
    tone_instructions = {
        "friendly": "Use a warm, friendly tone like a helpful friend.",
        "casual": "Keep it casual and conversational.",
        "empathetic": "Be understanding and supportive - the student is confused.",
        "technical": "Use precise technical language appropriate for the subject.",
        "academic": "Maintain an academic, rigorous approach.",
        "concise": "Be direct and to-the-point.",
        "balanced": "Balance friendliness with informative content.",
    }
    
    prompt = f"""You are an intelligent AI tutor. Generate a response to the student's question.

QUESTION: {question}
SUBJECT: {subject or 'General'}

RESPONSE STRUCTURE:
{chr(10).join(block_instructions)}

IMPORTANT GUIDELINES:
- {length_instructions.get(length, length_instructions['medium'])}
- {tone_instructions.get(tone, tone_instructions['balanced'])}
- Do NOT include sections that are not listed above.
- Do NOT use a fixed template - adapt to this specific question.
- Write naturally like ChatGPT/Gemini - not like a formatted document.
- If this is a simple question, give a simple answer. Don't over-explain.

Generate the response now:"""

    return prompt


# Export main functions
__all__ = [
    'detect_intent',
    'should_include_visual', 
    'get_response_blocks',
    'get_response_config',
    'build_adaptive_prompt',
    'QuestionIntent',
    'ResponseBlock',
]


