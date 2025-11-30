"""
🤔 DOUBT RESOLVER AGENT - Empathetic & Intelligent Doubt Clarification

This agent handles student doubts with:
- Zero-judgment empathy
- Step-by-step explanation
- Multiple approaches if needed
- Visual suggestions when helpful

Philosophy: "There are no stupid questions, only learning opportunities"
"""

import logging
from typing import Dict, Any, Optional, List
from agents.intelligent_agent_base import IntelligentAgentBase

logger = logging.getLogger(__name__)


class DoubtResolverAgent(IntelligentAgentBase):
    """
    Intelligent doubt resolver that uses LLM for empathetic explanations
    """
    
    @staticmethod
    def is_doubt_query(query: str) -> bool:
        """Detect if this is a doubt/confusion query"""
        query_lower = query.lower()
        
        doubt_phrases = [
            # Direct doubt expressions
            'don\'t understand', 'dont understand', 'not understanding',
            'confused', 'confusion', 'doubt', 'unclear', 'not clear',
            'samajh nahi', 'nahi samjha', 'समझ नहीं',
            
            # Questions indicating confusion
            'why does', 'why is', 'how does', 'how is',
            'what is', 'what are', 'what does',
            'can you explain', 'please explain', 'explain again',
            'help me understand', 'i\'m stuck', 'i am stuck',
            
            # Frustration indicators
            'makes no sense', 'doesn\'t make sense',
            'still confused', 'still don\'t get',
            
            # Clarification requests
            'clarify', 'what do you mean', 'elaborate'
        ]
        
        return any(phrase in query_lower for phrase in doubt_phrases)
    
    def get_agent_type(self) -> str:
        return 'doubt_resolver'
    
    def get_agent_persona(self) -> str:
        """Empathetic teacher persona"""
        return """You are a patient, empathetic teacher who specializes in resolving student doubts.

YOUR CHARACTER:
- You believe NO question is stupid
- You've seen many students have the same doubt before
- You're patient and will explain as many times as needed
- You celebrate when students ask for clarification - it shows they're thinking!

YOUR APPROACH:
- Start by validating their confusion: "Great question!" or "Lots of students find this tricky"
- Break complex ideas into simple chunks
- Use analogies from everyday life
- Check understanding: "Does this click?" or "Want me to try a different approach?"
- If they're frustrated, acknowledge it genuinely

NEVER:
- Make students feel dumb
- Rush through explanations
- Use jargon without explaining it first
- Say "it's simple" or "obviously"
"""
    
    def get_specialized_instructions(self, query: str, context: Dict[str, Any]) -> str:
        """Instructions based on the type of doubt"""
        
        query_lower = query.lower()
        subject = context.get('subject', 'General')
        
        # Detect frustration level
        frustration_words = ['still', 'again', 'not getting', 'frustrated', 'confused']
        is_frustrated = any(w in query_lower for w in frustration_words)
        
        frustration_handling = ""
        if is_frustrated:
            frustration_handling = """
STUDENT SEEMS FRUSTRATED:
- Acknowledge it: "I totally get the frustration - this concept trips up many people"
- Try a DIFFERENT approach than before
- Use a completely new analogy
- Maybe suggest a visual: "Sometimes seeing it helps - want me to show you with a diagram?"
"""
        
        # Detect if asking "why"
        if 'why' in query_lower:
            explanation_type = """
THIS IS A "WHY" QUESTION:
- Don't just state the fact, explain the REASONING
- Connect cause and effect clearly
- If it's a definition/rule, explain WHERE it comes from
- Use "because" and "so that" to show relationships
"""
        
        elif 'how' in query_lower:
            explanation_type = """
THIS IS A "HOW" QUESTION:
- Give step-by-step breakdown
- Number the steps clearly
- Explain what happens at each step
- Connect to the bigger picture
"""
        
        elif 'what' in query_lower:
            explanation_type = """
THIS IS A "WHAT" QUESTION:
- Define clearly first
- Then give examples
- Contrast with what it's NOT (if helpful)
- Connect to things they already know
"""
        
        else:
            explanation_type = """
GENERAL DOUBT:
- Identify what specifically is confusing
- Break into smaller pieces
- Build understanding step by step
- Check in periodically
"""
        
        return f"""
SUBJECT: {subject}

{explanation_type}

{frustration_handling}

STRUCTURE YOUR RESPONSE:
1. Validate the doubt (1 line)
2. Core explanation (3-5 lines, simple language)
3. Example or analogy (relatable to Indian students)
4. Quick check: "Does this make sense?" or offer alternative approach

IF VISUAL WOULD HELP:
- Mention: "This is easier to understand with a visual - want me to show you?"
"""
    
    def _get_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback if LLM fails"""
        subject = context.get('subject', 'this topic')
        
        return f"""That's a great question! 🤔 Many students have the same doubt.

Let me break this down simply...

For {subject}, the key thing to understand is the **core concept first**. Once that clicks, everything else follows.

Would you like me to:
1. **Explain step by step** - I'll break it into small pieces
2. **Use an analogy** - Connect it to something familiar
3. **Show with visual** - Sometimes a diagram helps

What works best for you? 📚"""
    
    def _post_process_response(
        self,
        response: str,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Add visual suggestion if concept is complex"""
        
        # List of concepts that benefit from visuals
        visual_concepts = [
            'force', 'motion', 'velocity', 'acceleration', 'energy',
            'circuit', 'current', 'resistance', 'wave',
            'photosynthesis', 'cell', 'dna', 'mitosis', 'digestion',
            'reaction', 'bond', 'electron', 'orbital',
            'graph', 'function', 'equation', 'geometry'
        ]
        
        query_lower = query.lower()
        needs_visual = any(concept in query_lower for concept in visual_concepts)
        
        # Don't add if already mentions visual
        if needs_visual and 'visual' not in response.lower() and 'diagram' not in response.lower():
            response += "\n\n💡 *Tip: A visual diagram might help cement this concept. Just ask!*"
        
        return response


# ============================================
# COMPATIBILITY: Static method for detection
# ============================================

def is_doubt_query(query: str) -> bool:
    """Module-level function for import compatibility"""
    return DoubtResolverAgent.is_doubt_query(query)
