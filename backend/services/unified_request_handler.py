"""
🎯 UNIFIED REQUEST HANDLER - Single Entry Point for All AI Requests
===================================================================

This is the ONLY entry point for AI request processing.
It orchestrates: pre-flight checks → agent selection → LLM call → fallback

GUARANTEES:
1. ONE request = ONE LLM call (maximum)
2. NEVER returns HTTP 500
3. Always responds within budget (10s default)
4. Graceful degradation on any failure

This replaces the previous multi-agent competition model.
"""

import logging
import uuid
import time
from typing import Dict, Any, Optional

from core.request_context import (
    RequestContext,
    CircuitBreaker,
    ConfigurationGuard,
    request_scope,
)
from services.coordinated_llm import (
    CoordinatedLLMService,
    DeterministicFallback,
)
from agents.agent_selector import (
    select_and_configure_agent,
    AgentType,
)

logger = logging.getLogger(__name__)


class UnifiedRequestHandler:
    """
    Single entry point for all AI requests.
    
    Execution Flow:
    1. Pre-flight checks (API keys, circuit breaker, budget)
    2. Agent selection (rule-based, no LLM)
    3. Simple response check (greetings don't need LLM)
    4. Single LLM call (coordinated, no retries)
    5. Fallback if needed (deterministic, never fails)
    
    This class NEVER throws exceptions to the caller.
    All failures are caught and converted to fallback responses.
    """
    
    # Default budget for request processing
    DEFAULT_BUDGET = 10.0  # seconds
    
    @classmethod
    async def handle_request(
        cls,
        query: str,
        subject: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle an AI request with full orchestration.
        
        Args:
            query: User's question
            subject: Detected/specified subject
            user_id: User identifier
            session_id: Session identifier
            **kwargs: Additional parameters
        
        Returns:
            Response dict that ALWAYS has valid content.
            Never throws exceptions.
        """
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"[{request_id}] 🚀 Request started: {query[:50]}...")
        
        try:
            async with request_scope(request_id, query, cls.DEFAULT_BUDGET) as ctx:
                ctx.subject = subject
                ctx.user_id = user_id
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 1: PRE-FLIGHT CHECKS
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                # Check 1: API keys present?
                config_valid, missing_keys = ConfigurationGuard.check_config()
                if not config_valid:
                    logger.warning(f"[{request_id}] ⚠️ Missing API keys: {missing_keys}")
                    return cls._create_fallback_response(
                        query, subject, 
                        reason=f"Configuration incomplete",
                        request_id=request_id
                    )
                
                # Check 2: Circuit breaker open?
                if not await CircuitBreaker.can_call():
                    logger.warning(f"[{request_id}] ⚡ Circuit breaker open")
                    return cls._create_fallback_response(
                        query, subject,
                        reason="Service temporarily degraded",
                        request_id=request_id
                    )
                
                # Check 3: Sufficient budget?
                if ctx.remaining_budget < 2.0:
                    logger.warning(f"[{request_id}] ⏱️ Insufficient budget")
                    return cls._create_fallback_response(
                        query, subject,
                        reason="Request timeout",
                        request_id=request_id
                    )
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 2: AGENT SELECTION (Rule-based, no LLM)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                selection = select_and_configure_agent(query, subject)
                agent_type = selection["agent_type"]
                agent_config = selection["config"]
                ctx.selected_agent = agent_config["name"]
                
                logger.info(f"[{request_id}] 🎯 Agent selected: {agent_config['name']}")
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 3: SIMPLE RESPONSE (No LLM needed)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                if selection.get("simple_response"):
                    logger.info(f"[{request_id}] ✨ Simple response (no LLM)")
                    return cls._create_success_response(
                        selection["simple_response"],
                        query, subject, request_id,
                        agent_name=agent_config["name"],
                        llm_used=False
                    )
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 4: SINGLE LLM CALL (Coordinated)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                # Build prompt
                prompt = cls._build_prompt(query, subject, agent_config)
                
                # Make coordinated LLM call
                llm_result = await CoordinatedLLMService.call_llm(
                    prompt=prompt,
                    context=ctx,
                    system_message=agent_config.get("system_prompt"),
                    temperature=agent_config.get("temperature", 0.7),
                    max_tokens=agent_config.get("max_tokens", 500),
                )
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 5: RESPONSE HANDLING
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                if llm_result:
                    # Success!
                    logger.info(f"[{request_id}] ✅ LLM response received")
                    return cls._create_success_response(
                        llm_result,
                        query, subject, request_id,
                        agent_name=agent_config["name"],
                        llm_used=True
                    )
                else:
                    # LLM failed - use fallback
                    logger.warning(f"[{request_id}] ⚠️ LLM failed, using fallback")
                    return cls._create_fallback_response(
                        query, subject,
                        reason=ctx.llm_error or "LLM unavailable",
                        request_id=request_id
                    )
        
        except Exception as e:
            # Catch-all: NEVER let exceptions escape
            logger.error(f"[{request_id}] ❌ Unexpected error: {e}", exc_info=True)
            return cls._create_fallback_response(
                query, subject,
                reason="Internal error",
                request_id=request_id
            )
        
        finally:
            elapsed = time.time() - start_time
            logger.info(f"[{request_id}] 🏁 Request completed in {elapsed:.2f}s")
    
    @classmethod
    def _build_prompt(
        cls,
        query: str,
        subject: Optional[str],
        agent_config: Dict[str, Any]
    ) -> str:
        """Build the prompt for LLM call."""
        
        subject_context = f"Subject: {subject}\n" if subject else ""
        
        prompt = f"""{subject_context}
Student Question: {query}

Please provide a helpful, educational response. Be clear, use examples, and encourage the student."""
        
        return prompt
    
    @classmethod
    def _create_success_response(
        cls,
        content: str,
        query: str,
        subject: Optional[str],
        request_id: str,
        agent_name: str = "MentorAgent",
        llm_used: bool = True
    ) -> Dict[str, Any]:
        """Create a successful response in the expected format."""
        
        return {
            "success": True,
            "request_id": request_id,
            "response": content,
            "agent": agent_name,
            "llm_used": llm_used,
            "fallback": False,
            # Format for frontend compatibility
            "default_view": {
                "greeting": "Here's what I found! 📚",
                "main_content": {
                    "title": query[:50],
                    "content": content
                },
                "metaphor": None,
            },
            "progressive_sections": {
                "key_takeaways": [],
            },
            "detected_subject": subject,
        }
    
    @classmethod
    def _create_fallback_response(
        cls,
        query: str,
        subject: Optional[str],
        reason: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Create a fallback response that never fails."""
        
        fallback_content = DeterministicFallback.get_response(query, subject)
        
        return {
            "success": True,  # From user's perspective, we always succeed
            "request_id": request_id,
            "response": fallback_content,
            "agent": "FallbackAgent",
            "llm_used": False,
            "fallback": True,
            "fallback_reason": reason,
            # Format for frontend compatibility
            "default_view": {
                "greeting": "Let me help you with that! 📚",
                "main_content": {
                    "title": query[:50],
                    "content": fallback_content
                },
                "metaphor": None,
            },
            "progressive_sections": {
                "key_takeaways": [],
            },
            "detected_subject": subject,
        }


# Convenience function for easy import
async def handle_ai_request(
    query: str,
    subject: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main entry point for AI requests.
    
    Usage:
        from services.unified_request_handler import handle_ai_request
        
        response = await handle_ai_request(
            query="explain force",
            subject="physics"
        )
    """
    return await UnifiedRequestHandler.handle_request(
        query=query,
        subject=subject,
        user_id=user_id,
        **kwargs
    )
