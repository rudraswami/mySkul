"""
🤔 Doubt Resolver Agent - Compatibility Layer
==============================================

This module provides backward compatibility for code importing from
agents.doubt_resolver. The actual implementation is now in:
- AgenticDoubtResolver (for complex doubts with ReAct + tools)
- ResponseComposer (for normal tutor questions - the DEFAULT path)

IMPORTANT DESIGN DECISION:
- is_doubt_query() is now RESTRICTIVE - only catches TRUE confusion/stuck situations
- Normal "what is / explain / why" questions should go to ResponseComposer
- Only genuine "I don't understand / confused / stuck" goes to doubt resolver
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def is_doubt_query(query: str) -> bool:
    """
    UPGRADED: Intelligent doubt detection with multi-signal analysis.
    
    Now uses SMART ROUTING instead of restrictive pattern matching:
    - Analyzes conceptual depth needed
    - Detects implicit confusion (not just explicit phrases)
    - Routes complex educational queries to multi-agent system
    
    Returns:
        True for queries that benefit from multi-agent reasoning
    """
    query_lower = query.lower().strip()
    word_count = len(query.split())
    
    # ==========================================================================
    # TIER 1: EXPLICIT CONFUSION (High confidence - always route)
    # ==========================================================================
    explicit_confusion = [
        "don't understand", "dont understand", "do not understand",
        "confused about", "i'm confused", "i am confused", "so confused",
        "makes no sense", "doesn't make sense", "not making sense",
        "i'm stuck", "i am stuck", "can't figure", "cannot figure",
        "struggling with", "not getting it", "don't get it",
        "help me understand", "explain again", "clarify this",
        "samajh nahi aa raha", "clear nahi hai", "confuse ho gaya",
    ]
    
    if any(phrase in query_lower for phrase in explicit_confusion):
        logger.info(f"🤔 Routing to multi-agent (explicit confusion): '{query[:50]}...'")
        return True
    
    # ==========================================================================
    # TIER 2: DEEP CONCEPTUAL QUERIES (benefit from multi-agent reasoning)
    # ==========================================================================
    deep_concept_indicators = [
        # Derivations and proofs
        "derive", "derivation", "prove", "proof", "show that",
        # Conceptual understanding
        "why does", "why is", "why do", "how does", "how is",
        "what is the reason", "what causes", "what happens when",
        # Comparisons and analysis
        "difference between", "compare", "contrast", "versus", "vs",
        "relation between", "relationship between", "connection between",
        # Explanations
        "explain the mechanism", "explain how", "explain why",
        "intuition behind", "physical significance", "conceptual meaning",
        # Problem solving
        "solve step by step", "step by step", "show steps",
        "calculate", "find the value", "determine",
    ]
    
    if any(ind in query_lower for ind in deep_concept_indicators):
        logger.info(f"🤔 Routing to multi-agent (deep conceptual): '{query[:50]}...'")
        return True
    
    # ==========================================================================
    # TIER 3: COMPLEXITY-BASED ROUTING
    # ==========================================================================
    # Long queries usually need multi-agent reasoning
    if word_count > 15:
        # Check for educational content indicators
        edu_indicators = [
            "physics", "chemistry", "math", "biology", "formula",
            "equation", "theorem", "law", "principle", "concept",
            "jee", "neet", "cbse", "board", "exam",
        ]
        if any(ind in query_lower for ind in edu_indicators):
            logger.info(f"🤔 Routing to multi-agent (complex educational): '{query[:50]}...'")
            return True
    
    # ==========================================================================
    # TIER 4: IMPLICIT DEPTH INDICATORS
    # ==========================================================================
    # Questions that seem simple but need deep understanding
    implicit_depth = [
        "but why", "but how", "what if", "what about",
        "is it true that", "i thought", "i heard",
        "can you explain", "please explain", "tell me more",
        "in detail", "in depth", "thoroughly",
    ]
    
    if any(phrase in query_lower for phrase in implicit_depth):
        logger.info(f"🤔 Routing to multi-agent (implicit depth): '{query[:50]}...'")
        return True
    
    # ==========================================================================
    # DEFAULT: Simple queries go to fast path
    # ==========================================================================
    return False


def is_deep_reasoning_query(query: str) -> bool:
    """
    UPGRADED: Smart detection for queries needing ReAct loop with tools.
    
    Routes to full agentic system for:
    - Multi-step mathematical problems
    - Proofs and derivations
    - Problems requiring verification
    - Complex analysis tasks
    """
    query_lower = query.lower().strip()
    word_count = len(query.split())
    
    # ==========================================================================
    # TIER 1: EXPLICIT DEEP REASONING NEEDS
    # ==========================================================================
    explicit_deep = [
        # Proofs and derivations
        "prove", "proof", "derive", "derivation", "show that",
        "demonstrate that", "establish that",
        # Multi-step solutions
        "step by step", "show steps", "show all steps",
        "solve completely", "full solution",
        # Verification
        "verify", "check my", "is this correct", "am i right",
        "validate", "confirm",
        # Analysis
        "analyze", "analyse", "comprehensive", "detailed explanation",
        "in depth", "thorough explanation",
    ]
    
    if any(trigger in query_lower for trigger in explicit_deep):
        return True
    
    # ==========================================================================
    # TIER 2: MATHEMATICAL/SCIENTIFIC COMPLEXITY
    # ==========================================================================
    # Problems with numbers, equations, or scientific notation
    import re
    
    math_patterns = [
        r'\d+\s*[+\-*/^=]\s*\d+',  # Arithmetic
        r'x\s*[+\-*/^=]',  # Algebra
        r'd[xy]/d[xy]',  # Derivatives
        r'∫|integral|integrate',  # Integrals
        r'sin|cos|tan|log|ln',  # Functions
        r'matrix|vector|determinant',  # Linear algebra
        r'probability|permutation|combination',  # Probability
        r'mole|concentration|molarity',  # Chemistry
        r'force|velocity|acceleration|momentum',  # Physics
    ]
    
    for pattern in math_patterns:
        if re.search(pattern, query_lower):
            # If math + word count > 10, likely needs deep reasoning
            if word_count > 10:
                return True
    
    # ==========================================================================
    # TIER 3: SUBJECT-SPECIFIC COMPLEXITY
    # ==========================================================================
    jee_neet_topics = [
        # Physics JEE/NEET
        "mechanics", "thermodynamics", "electromagnetism", "optics",
        "semiconductor", "modern physics", "wave motion",
        # Chemistry JEE/NEET
        "organic chemistry", "inorganic chemistry", "physical chemistry",
        "electrochemistry", "chemical kinetics", "equilibrium",
        # Math JEE
        "calculus", "coordinate geometry", "trigonometry",
        "differential equation", "complex number", "probability",
        # Biology NEET
        "genetics", "evolution", "ecology", "human physiology",
    ]
    
    if any(topic in query_lower for topic in jee_neet_topics):
        # These topics usually need multi-step reasoning
        return True
    
    # ==========================================================================
    # TIER 4: COMPLEXITY BY LENGTH AND STRUCTURE
    # ==========================================================================
    # Long queries with multiple parts usually need deep reasoning
    if word_count > 25:
        return True
    
    # Questions with multiple parts
    if query_lower.count('?') > 1:
        return True
    
    if any(phrase in query_lower for phrase in ['and also', 'additionally', 'furthermore', 'as well as']):
        return True
    
    return False


# ==========================================================================
# BACKWARD COMPATIBILITY: DoubtResolverAgent class
# ==========================================================================
# This provides the class interface that old code expects

class DoubtResolverAgent:
    """
    Backward-compatible DoubtResolverAgent.
    
    For new code, prefer using ResponseComposer for normal questions
    and AgenticDoubtResolver for complex doubt resolution.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        logger.info("DoubtResolverAgent initialized (compatibility layer)")
    
    @staticmethod
    def is_doubt_query(query: str) -> bool:
        """Static method for backward compatibility"""
        return is_doubt_query(query)
    
    @staticmethod
    def is_deep_reasoning_query(query: str) -> bool:
        """Detect if query needs deep reasoning with tools"""
        return is_deep_reasoning_query(query)
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a doubt query.
        
        For true doubts, this delegates to AgenticDoubtResolver.
        For simpler clarifications, returns a structured response.
        """
        try:
            # For complex doubts, use agentic resolver
            if is_deep_reasoning_query(query):
                from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
                agent = create_agentic_doubt_resolver(self.config)
                return await agent.run(query, context)
            
            # For simpler doubts, use lightweight LLM call
            return await self._lightweight_doubt_response(query, context)
            
        except Exception as e:
            logger.error(f"DoubtResolverAgent error: {e}")
            return {
                'success': False,
                'content': self._get_fallback_response(query, context),
                'error': str(e)
            }
    
    async def _lightweight_doubt_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a lightweight response for simple doubts"""
        # This will be handled by the main ResponseComposer in most cases
        # This is a minimal fallback
        return {
            'success': True,
            'content': self._get_fallback_response(query, context),
            'metadata': {'lightweight': True}
        }
    
    def _get_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback response when LLM fails"""
        subject = context.get('subject', 'this topic')
        return f"""That's a great question! 🤔

Let me help you understand {subject} better.

Could you tell me:
1. **What specific part** is confusing you?
2. **What have you tried** so far?

This will help me give you a more targeted explanation! 📚"""

