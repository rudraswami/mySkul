"""
🛡️ SAFE AI HANDLER - Production-Grade Request Handler
======================================================

This is a DROP-IN replacement for the multi-agent supervisor.
Use this when you need GUARANTEED response times and stability.

Key Guarantees:
1. ONE LLM call per request (maximum)
2. NEVER returns HTTP 500
3. Always responds within 10 seconds
4. Graceful degradation on any failure

Usage in api/ai.py:
    from services.safe_ai_handler import safe_handle_request, USE_SAFE_HANDLER
    
    if USE_SAFE_HANDLER:
        return await safe_handle_request(request.message, request.subject, user.user_id)
    else:
        # ... existing multi-agent code ...
"""

import os
import logging
import asyncio
import uuid
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Feature flag - set to True to enable safe handler
USE_SAFE_HANDLER = os.getenv("USE_SAFE_AI_HANDLER", "true").lower() == "true"


async def safe_handle_request(
    query: str,
    subject: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Safe, production-grade AI request handler.
    
    GUARANTEES:
    - Single LLM call (no parallel agent competition)
    - 10 second total budget
    - Never throws exceptions
    - Always returns valid response
    
    Args:
        query: User's question
        subject: Subject hint
        user_id: User identifier
        session_id: Session identifier
    
    Returns:
        Response dict compatible with existing frontend
    """
    request_id = f"safe_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    logger.info(f"[{request_id}] 🛡️ Safe handler: {query[:50]}...")
    
    try:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # PRE-FLIGHT: Check API key FIRST (fail-fast)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning(f"[{request_id}] ⚠️ Missing OPENAI_API_KEY")
            return _create_fallback_response(
                query, subject, request_id,
                reason="Service configuration incomplete"
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SIMPLE QUERY CHECK (no LLM needed)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        simple_response = _check_simple_query(query)
        if simple_response:
            logger.info(f"[{request_id}] ✨ Simple response (no LLM)")
            return _create_success_response(
                simple_response, query, subject, request_id,
                llm_used=False
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SINGLE LLM CALL (with strict timeout)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Build prompt
        subject_context = f"Subject: {subject}\n" if subject else ""
        prompt = f"""{subject_context}
Student Question: {query}

You are Sathi, a friendly Indian AI tutor. Please provide:
1. A clear, simple explanation (2-3 sentences)
2. A relatable Indian example (cricket, chai, daily life)
3. Key points to remember

Be encouraging and supportive. Use simple language."""

        system_message = """You are Sathi, a friendly educational AI assistant for Indian students.
You explain concepts simply, use relatable examples, and encourage learning.
Keep responses concise but helpful."""

        try:
            # Import LLM service
            from services.llm_service import call_llm
            
            # Make single LLM call with 8 second timeout
            llm_result = await asyncio.wait_for(
                call_llm(
                    prompt=prompt,
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=500,
                    model="gpt-4o-mini",
                    system_message=system_message
                ),
                timeout=8.0  # 8 second timeout
            )
            
            if llm_result:
                elapsed = time.time() - start_time
                logger.info(f"[{request_id}] ✅ LLM success in {elapsed:.2f}s")
                return _create_success_response(
                    llm_result, query, subject, request_id,
                    llm_used=True
                )
            else:
                logger.warning(f"[{request_id}] ⚠️ Empty LLM response")
                return _create_fallback_response(
                    query, subject, request_id,
                    reason="Empty response from AI"
                )
                
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logger.warning(f"[{request_id}] ⏱️ LLM timeout after {elapsed:.2f}s")
            return _create_fallback_response(
                query, subject, request_id,
                reason="Response took too long"
            )
            
        except Exception as llm_err:
            logger.error(f"[{request_id}] ❌ LLM error: {llm_err}")
            return _create_fallback_response(
                query, subject, request_id,
                reason="AI service temporarily unavailable"
            )
    
    except Exception as e:
        # Catch-all - NEVER let exceptions escape
        logger.error(f"[{request_id}] ❌ Unexpected error: {e}", exc_info=True)
        return _create_fallback_response(
            query, subject, request_id,
            reason="Internal error"
        )
    
    finally:
        elapsed = time.time() - start_time
        logger.info(f"[{request_id}] 🏁 Completed in {elapsed:.2f}s")


def _check_simple_query(query: str) -> Optional[str]:
    """Check if query is simple (greeting, thanks, etc.) and return immediate response."""
    import re
    query_lower = query.lower().strip()
    
    # Greetings
    if re.search(r'^(hi|hello|hey|good morning|good evening)\b', query_lower):
        return "Hey! 👋 I'm Sathi, your study buddy. What would you like to learn today?"
    
    # Thanks
    if re.search(r'\b(thanks|thank you|thx)\b', query_lower):
        return "You're welcome! 😊 Feel free to ask if you have more questions!"
    
    # Acknowledgment
    if re.search(r'^(ok|okay|got it|understood|yes|sure)\b', query_lower):
        return "Great! Let me know if you need any clarification."
    
    # Farewell
    if re.search(r'\b(bye|goodbye|see you)\b', query_lower):
        return "Bye! Good luck with your studies! 📖✨"
    
    return None


def _create_success_response(
    content: str,
    query: str,
    subject: Optional[str],
    request_id: str,
    llm_used: bool = True
) -> Dict[str, Any]:
    """Create successful response in frontend-compatible format."""
    return {
        "success": True,
        "request_id": request_id,
        "handler": "safe_handler",
        "llm_used": llm_used,
        "fallback": False,
        "response": {
            "default_view": {
                "greeting": "Here's what I found! 📚",
                "main_content": {
                    "title": query[:50] if len(query) > 50 else query,
                    "content": content
                },
                "metaphor": None,
                "mentor_avatar": None,
                "hero_visual": None,
                "interactive_options": [],
                "professor_badge": {
                    "verified": True,
                    "badge_visual": None,
                    "ncert_ref": None,
                    "students_solved": "1000+"
                }
            },
            "progressive_sections": {
                "key_takeaways": _extract_key_points(content),
                "encouragement": "Keep up the great work! 💪"
            },
            "format_type": "explanation",
            "detected_subject": subject or "General",
            "intent": "explanation"
        }
    }


def _create_fallback_response(
    query: str,
    subject: Optional[str],
    request_id: str,
    reason: str
) -> Dict[str, Any]:
    """Create fallback response that never fails."""
    
    # Get subject-specific fallback
    fallback_content = _get_fallback_content(query, subject)
    
    return {
        "success": True,  # From user perspective, we always succeed
        "request_id": request_id,
        "handler": "safe_handler",
        "llm_used": False,
        "fallback": True,
        "fallback_reason": reason,
        "response": {
            "default_view": {
                "greeting": "Let me help you with that! 📚",
                "main_content": {
                    "title": query[:50] if len(query) > 50 else query,
                    "content": fallback_content
                },
                "metaphor": None,
                "mentor_avatar": None,
                "hero_visual": None,
                "interactive_options": [],
                "professor_badge": None
            },
            "progressive_sections": {
                "key_takeaways": ["Take your time to understand the concept", "Practice with examples"],
                "encouragement": "Don't worry, learning takes time! 💪"
            },
            "format_type": "explanation",
            "detected_subject": subject or "General",
            "intent": "explanation"
        }
    }


def _get_fallback_content(query: str, subject: Optional[str]) -> str:
    """Get deterministic fallback content based on query and subject."""
    query_lower = query.lower()
    subject_lower = (subject or "").lower()
    
    # Physics fallbacks
    if "physics" in subject_lower or any(w in query_lower for w in ["force", "motion", "energy", "gravity"]):
        if "force" in query_lower:
            return """Force is a push or pull that can change an object's motion.

**Key Points:**
• Newton's First Law: Objects at rest stay at rest unless acted upon by a force
• Newton's Second Law: F = ma (Force = mass × acceleration)
• Newton's Third Law: Every action has an equal and opposite reaction

**Example:** When you kick a cricket ball, your foot applies force to the ball, making it move!

Would you like me to explain any specific aspect in more detail?"""
        
        return """This is a physics concept! Physics helps us understand how the world works.

**Key Areas:**
• Mechanics - forces, motion, energy
• Thermodynamics - heat and temperature
• Waves and Optics - light and sound
• Electricity and Magnetism

Try breaking down the problem into what you know and what you need to find.
Would you like me to help with a specific topic?"""
    
    # Chemistry fallbacks
    if "chemistry" in subject_lower or any(w in query_lower for w in ["atom", "molecule", "reaction", "element"]):
        return """This is a chemistry concept! Chemistry studies matter and its transformations.

**Key Areas:**
• Atomic Structure - electrons, protons, neutrons
• Chemical Bonding - ionic, covalent bonds
• Reactions - how substances change
• Periodic Table - organization of elements

**Tip:** Always balance equations and check your units!
Would you like me to explain a specific topic?"""
    
    # Biology fallbacks
    if "biology" in subject_lower or any(w in query_lower for w in ["cell", "dna", "organism", "plant"]):
        return """This is a biology concept! Biology studies living organisms.

**Key Areas:**
• Cell Biology - the basic unit of life
• Genetics - DNA, inheritance
• Human Body Systems - how our body works
• Ecology - organisms and their environment

**Tip:** Try to visualize biological processes as they happen!
Would you like me to explain a specific topic?"""
    
    # Math fallbacks
    if "math" in subject_lower or any(w in query_lower for w in ["equation", "formula", "calculate", "solve"]):
        return """This is a math concept! Let me help you work through it.

**Problem-Solving Steps:**
1. Identify what you know (given values)
2. Identify what you need to find
3. Choose the right formula or method
4. Solve step by step
5. Check your answer

**Tip:** Write down each step - it helps avoid mistakes!
Would you like me to work through an example?"""
    
    # General fallback
    return """Great question! Let me help you understand this concept.

**Learning Tips:**
• Break the topic into smaller parts
• Look for patterns and connections
• Try explaining it in your own words
• Practice with examples

I'm here to help! Would you like me to elaborate on any specific part?"""


def _extract_key_points(content: str) -> list:
    """Extract key points from content for takeaways."""
    import re
    
    # Look for bullet points
    bullets = re.findall(r'[•\-\*]\s*(.+?)(?=\n|$)', content)
    if bullets:
        return bullets[:3]  # Return first 3 bullets
    
    # Look for numbered points
    numbered = re.findall(r'\d+[.)]\s*(.+?)(?=\n|$)', content)
    if numbered:
        return numbered[:3]
    
    # Default
    return ["Review the explanation above", "Practice with examples"]
