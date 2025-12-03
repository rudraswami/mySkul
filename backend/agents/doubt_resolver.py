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
    Detect if this is a TRUE doubt/confusion query that needs special handling.
    
    IMPORTANT: This is now RESTRICTIVE by design.
    - Normal tutor questions ("what is X", "explain Y") → go to ResponseComposer
    - TRUE confusion/frustration ("I don't understand", "still confused") → doubt resolver
    
    Returns:
        True ONLY for genuine confusion/doubt expressions, not general questions
    """
    query_lower = query.lower().strip()
    
    # ==========================================================================
    # TIER 1: EXPLICIT CONFUSION/FRUSTRATION (High confidence - route to doubt)
    # ==========================================================================
    explicit_confusion = [
        # Direct confusion statements
        "don't understand", "dont understand", "do not understand",
        "not understanding", "can't understand", "cannot understand",
        "confused about", "i'm confused", "i am confused", "so confused",
        "still confused", "very confused", "really confused",
        "makes no sense", "doesn't make sense", "does not make sense",
        "not making sense", "can't make sense",
        
        # Stuck/blocked expressions
        "i'm stuck", "i am stuck", "getting stuck", "got stuck",
        "can't figure", "cannot figure", "can't get", "cannot get",
        "struggling with", "struggling to understand",
        
        # Frustration indicators
        "still don't get", "still dont get", "still not getting",
        "not getting it", "don't get it", "dont get it",
        "what am i missing", "what am i doing wrong",
        "where am i going wrong", "help me understand",
        
        # Request for re-explanation
        "explain again", "explain it again", "one more time",
        "say that again", "repeat that", "clarify this",
        "i need clarification", "need more clarification",
        
        # Hindi/Hinglish confusion expressions
        "samajh nahi aa raha", "samajh nahi aaya", "समझ नहीं आ रहा",
        "samajh me nahi", "clear nahi hai", "confuse ho gaya",
    ]
    
    if any(phrase in query_lower for phrase in explicit_confusion):
        logger.info(f"🤔 TRUE DOUBT detected (explicit confusion): '{query[:50]}...'")
        return True
    
    # ==========================================================================
    # TIER 2: CONTEXTUAL DOUBT PATTERNS (needs additional signals)
    # ==========================================================================
    # These patterns ONLY trigger if combined with emotional/struggle indicators
    contextual_patterns = [
        "why does", "why is", "why do", "why are",
        "how does", "how is", "how do", "how can",
    ]
    
    struggle_indicators = [
        "but", "though", "however", "still", "yet",
        "?", "not sure", "doubt", "unclear", "confusing",
        "tricky", "hard to", "difficult to"
    ]
    
    # Only route to doubt if pattern + struggle indicator present
    has_contextual = any(p in query_lower for p in contextual_patterns)
    has_struggle = any(s in query_lower for s in struggle_indicators) and len(query_lower) > 50
    
    if has_contextual and has_struggle:
        logger.info(f"🤔 TRUE DOUBT detected (contextual + struggle): '{query[:50]}...'")
        return True
    
    # ==========================================================================
    # DEFAULT: NOT A DOUBT - Let ResponseComposer handle it
    # ==========================================================================
    # Normal questions like "what is Newton's first law" should NOT come here
    return False


def is_deep_reasoning_query(query: str) -> bool:
    """
    Detect if query needs deep multi-step reasoning (ReAct with tools).
    
    This is for complex problems that benefit from tool usage and verification,
    NOT for simple conceptual questions.
    """
    query_lower = query.lower().strip()
    
    deep_reasoning_triggers = [
        # Multi-step problem solving
        "solve this step by step", "show all steps", "step by step solution",
        "derive and prove", "prove that", "prove this",
        "calculate and explain", "solve and verify",
        
        # Complex comparisons needing research
        "compare and contrast in detail", "detailed comparison",
        "analyze the differences", "comprehensive analysis",
        
        # Verification requests
        "verify my solution", "check my answer", "is this correct",
        "check if this is right", "verify this calculation",
        
        # Research-heavy queries
        "find all the formulas", "list all methods",
        "what are all the ways", "explain with examples from",
    ]
    
    return any(trigger in query_lower for trigger in deep_reasoning_triggers)


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

