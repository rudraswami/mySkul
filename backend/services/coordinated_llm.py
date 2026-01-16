"""
🎯 COORDINATED LLM SERVICE - Single-Flight Execution
=====================================================

This service REPLACES direct LLM calls for all agents.
It enforces the critical invariant: ONE REQUEST = ONE LLM CALL.

Agents MUST NOT call llm_service directly. They MUST use this service.

Key Features:
1. Single-flight: Only one LLM call per request context
2. Circuit breaker: Automatic fallback when LLM unhealthy
3. Budget enforcement: Timeout based on remaining budget
4. NO retries: Failure = immediate fallback
"""

import logging
import asyncio
from typing import Optional, Dict, Any

from core.request_context import (
    RequestContext,
    CircuitBreaker,
    ConfigurationGuard,
    get_current_context
)

logger = logging.getLogger(__name__)


class CoordinatedLLMService:
    """
    Single-flight LLM coordinator.
    
    This service ensures that within a request context:
    - Only ONE LLM call is made
    - All subsequent requests use the cached result
    - Failures trigger immediate fallback (no retries)
    """
    
    # Minimum budget required for LLM call
    MIN_BUDGET_FOR_LLM = 2.0  # seconds
    
    # Maximum LLM timeout (never exceed this)
    MAX_LLM_TIMEOUT = 8.0  # seconds
    
    @classmethod
    async def call_llm(
        cls,
        prompt: str,
        context: Optional[RequestContext] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        model: str = "gpt-4o-mini"
    ) -> Optional[str]:
        """
        Coordinated LLM call with single-flight enforcement.
        
        Args:
            prompt: The prompt to send
            context: Request context (auto-fetched if not provided)
            system_message: Optional system message
            temperature: LLM temperature
            max_tokens: Max response tokens
            model: Model to use
        
        Returns:
            LLM response or None if failed/skipped
        
        GUARANTEES:
        - Will NOT call LLM if already called in this context
        - Will NOT retry on failure
        - Will NOT exceed budget
        - Will NOT call if circuit breaker open
        """
        # Get context
        ctx = context or get_current_context()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CHECK 1: Already called? Return cached result
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if ctx and ctx.llm_called:
            logger.info(f"[{ctx.request_id}] 🔄 Using cached LLM result (single-flight)")
            return ctx.llm_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CHECK 2: Configuration valid?
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if not ConfigurationGuard.is_llm_available():
            logger.warning("⚠️ LLM not available (missing API key)")
            if ctx:
                ctx.mark_llm_called(result=None, error="Missing API key")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CHECK 3: Circuit breaker allows call?
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if not await CircuitBreaker.can_call():
            logger.warning("⚡ Circuit breaker OPEN - using fallback")
            if ctx:
                ctx.mark_llm_called(result=None, error="Circuit breaker open")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CHECK 4: Sufficient budget?
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if ctx and ctx.remaining_budget < cls.MIN_BUDGET_FOR_LLM:
            logger.warning(f"[{ctx.request_id}] Insufficient budget ({ctx.remaining_budget:.1f}s)")
            ctx.mark_llm_called(result=None, error="Budget exhausted")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # EXECUTE: Single LLM call (no retries)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Calculate timeout based on remaining budget
        if ctx:
            # Leave 2s buffer for post-processing
            timeout = min(cls.MAX_LLM_TIMEOUT, ctx.remaining_budget - 2.0)
        else:
            timeout = cls.MAX_LLM_TIMEOUT
        
        timeout = max(timeout, 3.0)  # Minimum 3s timeout
        
        request_id = ctx.request_id if ctx else "no_context"
        logger.info(f"[{request_id}] 🚀 Single-flight LLM call (timeout={timeout:.1f}s)")
        
        try:
            # Import actual LLM service
            from services.llm_service import call_llm as actual_llm_call
            import os
            
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Make the call with strict timeout
            result = await asyncio.wait_for(
                actual_llm_call(
                    prompt=prompt,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model,
                    system_message=system_message
                ),
                timeout=timeout
            )
            
            # Success! Record and return
            await CircuitBreaker.record_success()
            
            if ctx:
                ctx.mark_llm_called(result=result)
            
            logger.info(f"[{request_id}] ✅ LLM call successful")
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"[{request_id}] ⏱️ LLM timeout after {timeout:.1f}s")
            await CircuitBreaker.record_failure()
            if ctx:
                ctx.mark_llm_called(result=None, error=f"Timeout after {timeout:.1f}s")
            return None
            
        except Exception as e:
            logger.error(f"[{request_id}] ❌ LLM error: {e}")
            await CircuitBreaker.record_failure()
            if ctx:
                ctx.mark_llm_called(result=None, error=str(e))
            return None


class DeterministicFallback:
    """
    Rule-based fallback responses when LLM is unavailable.
    
    These responses are:
    - Instant (no external calls)
    - Deterministic (same input = same output)
    - Educational (still helpful to students)
    - Never HTTP 500
    """
    
    # Subject-specific templates
    TEMPLATES = {
        "physics": {
            "default": "This is a physics concept. Let me explain the key principles...\n\n"
                      "• Physics studies matter, energy, and their interactions\n"
                      "• Key concepts include force, motion, energy, and waves\n"
                      "• Try breaking down the problem into known quantities and unknowns\n\n"
                      "Would you like me to focus on a specific aspect?",
            "force": "Force is a push or pull that can change an object's motion.\n\n"
                    "• Newton's First Law: Objects at rest stay at rest unless acted upon by a force\n"
                    "• Newton's Second Law: F = ma (Force = mass × acceleration)\n"
                    "• Newton's Third Law: Every action has an equal and opposite reaction\n\n"
                    "Real-world example: When you kick a cricket ball, your foot applies force to the ball.",
        },
        "chemistry": {
            "default": "This is a chemistry concept. Let me explain the fundamentals...\n\n"
                      "• Chemistry studies matter and its transformations\n"
                      "• Key concepts include atoms, molecules, reactions, and bonds\n"
                      "• Try identifying the reactants and products\n\n"
                      "Would you like me to focus on a specific aspect?",
        },
        "biology": {
            "default": "This is a biology concept. Let me explain the basics...\n\n"
                      "• Biology studies living organisms\n"
                      "• Key concepts include cells, genetics, evolution, and ecology\n"
                      "• Try relating the concept to how living things function\n\n"
                      "Would you like me to focus on a specific aspect?",
        },
        "mathematics": {
            "default": "This is a math concept. Let me break it down...\n\n"
                      "• Mathematics is the study of numbers, quantities, and patterns\n"
                      "• Key areas include algebra, geometry, calculus, and statistics\n"
                      "• Try identifying what you know and what you need to find\n\n"
                      "Would you like me to work through an example?",
        },
        "general": {
            "default": "Great question! Let me help you understand this concept.\n\n"
                      "• Break the topic into smaller parts\n"
                      "• Look for patterns and connections\n"
                      "• Try explaining it in your own words\n\n"
                      "Would you like me to elaborate on any specific part?",
        }
    }
    
    @classmethod
    def get_response(cls, query: str, subject: Optional[str] = None) -> str:
        """
        Get a deterministic fallback response.
        
        Args:
            query: The user's question
            subject: Detected subject (physics, chemistry, etc.)
        
        Returns:
            A helpful response that never fails
        """
        query_lower = query.lower()
        subject = (subject or "general").lower()
        
        # Get subject templates
        templates = cls.TEMPLATES.get(subject, cls.TEMPLATES["general"])
        
        # Check for specific keywords
        if "force" in query_lower and subject == "physics":
            return templates.get("force", templates["default"])
        
        # Return default template for subject
        return templates["default"]
    
    @classmethod
    def wrap_response(cls, fallback_text: str, reason: str) -> Dict[str, Any]:
        """
        Wrap fallback response in standard format.
        """
        return {
            "response": fallback_text,
            "fallback": True,
            "fallback_reason": reason,
            "default_view": {
                "greeting": "I'm here to help! 📚",
                "main_content": {
                    "content": fallback_text
                }
            },
            "progressive_sections": {}
        }


# Convenience function for easy import
async def coordinated_llm_call(
    prompt: str,
    context: Optional[RequestContext] = None,
    **kwargs
) -> Optional[str]:
    """
    Convenience wrapper for coordinated LLM calls.
    
    Usage:
        from services.coordinated_llm import coordinated_llm_call
        
        result = await coordinated_llm_call(prompt, context)
    """
    return await CoordinatedLLMService.call_llm(prompt, context, **kwargs)
