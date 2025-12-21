"""
🤖 Agentic Router - Route Requests to True Agents
=================================================

This module is the CRITICAL bridge between user requests and
true agentic behavior. It:

1. Detects if a request requires ACTION vs INFORMATION
2. Routes ACTION requests to appropriate tools
3. Ensures agents actually DO things, not just talk about them

WITHOUT THIS:
- User: "Remind me tomorrow at 4pm"
- AI: "Sure! I'll remind you!" (but does nothing)

WITH THIS:
- User: "Remind me tomorrow at 4pm"
- AI: Actually schedules reminder → User gets notification at 4pm
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from core.config import settings
from services.action_intent_detector import (
    ActionIntentDetector, 
    DetectedIntent, 
    IntentType,
    get_intent_detector
)

logger = logging.getLogger(__name__)


class AgenticRouter:
    """
    Routes user requests to appropriate handlers based on intent.
    
    This enables TRUE agentic behavior by:
    1. Detecting action intents (remind, notify, schedule)
    2. Executing real actions via tools
    3. Falling back to LLM for information requests
    """
    
    def __init__(self, db_client=None):
        self.db = db_client
        self.intent_detector = get_intent_detector()
        self._tool_registry = None
        
        logger.info("🤖 AgenticRouter initialized")
    
    @property
    def tool_registry(self):
        """Lazy load tool registry"""
        if self._tool_registry is None:
            from agents.core.tool_registry import create_tool_registry
            logger.info("🔧 Creating tool registry with action tools...")
            self._tool_registry = create_tool_registry(
                include_default=True,
                include_action_tools=True
            )
            logger.info(f"🔧 Tool registry created with tools: {self._tool_registry.get_tool_names()}")
        return self._tool_registry
    
    async def route(
        self,
        message: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Route a user message to appropriate handler.
        
        Args:
            message: User's message
            user_id: User identifier
            context: Additional context (session, subject, etc.)
        
        Returns:
            (handled, result) tuple:
            - handled=True, result=dict: Action was executed, use this result
            - handled=False, result=None: Not an action, use normal LLM flow
        """
        logger.info(f"🤖 AgenticRouter.route() called with message: '{message[:100]}'")
        
        if not settings.ENABLE_ACTION_DETECTION:
            logger.info("🤖 Action detection is disabled in settings")
            return (False, None)
        
        # Detect intent
        intent = self.intent_detector.detect(message)
        
        logger.info(f"🎯 Detected intent: {intent.intent_type.value}")
        logger.info(f"   - Confidence: {intent.confidence:.2f}")
        logger.info(f"   - Requires action: {intent.requires_action}")
        logger.info(f"   - Params: {intent.extracted_params}")
        
        # If it's not an action request, let normal flow handle it
        if not intent.requires_action:
            logger.info(f"🤖 Not an action request, returning to normal flow")
            return (False, None)
        
        # Handle action intent
        try:
            logger.info(f"🤖 Handling action intent: {intent.intent_type.value}")
            result = await self._handle_action(intent, user_id, context or {})
            logger.info(f"🤖 Action result: {result}")
            
            # =====================================================================
            # CHECK IF ACTION WAS ACTUALLY HANDLED
            # =====================================================================
            # If _handle_action returns pass_to_orchestrator=True or success=False,
            # the intent was NOT a true action and should flow to the intelligent
            # orchestrator for proper handling with semantic understanding.
            # =====================================================================
            if result.get('pass_to_orchestrator') or not result.get('success', True):
                logger.info(f"📤 Action not handled, passing to intelligent orchestrator")
                return (False, None)
            
            return (True, result)
        except Exception as e:
            logger.error(f"Action handling error: {e}", exc_info=True)
            # Fall back to normal flow on error
            return (False, None)
    
    async def _handle_action(
        self,
        intent: DetectedIntent,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle TRUE action intents by executing the appropriate tool.
        
        =========================================================================
        🎯 IMPORTANT: This handler is ONLY for true tool-based actions:
        - REMINDER: Schedule an actual reminder in the database
        - RECURRING_REMINDER: Schedule recurring reminders
        - NOTIFICATION: Send actual push notification
        
        Everything else (study plans, motivation, breaks, progress, etc.) should
        NOT reach this handler. They should flow to UnifiedAIOrchestrator which
        uses semantic understanding and dynamic agent routing.
        =========================================================================
        """
        
        # Build context for tool execution
        tool_context = {
            'user_id': user_id,
            **context
        }
        
        # =====================================================================
        # TRUE ACTIONS ONLY - These require actual tool execution
        # =====================================================================
        if intent.intent_type == IntentType.REMINDER:
            return await self._handle_reminder(intent, tool_context)
        
        elif intent.intent_type == IntentType.RECURRING_REMINDER:
            return await self._handle_recurring_reminder(intent, tool_context)
        
        elif intent.intent_type == IntentType.NOTIFICATION:
            return await self._handle_notification(intent, tool_context)
        
        elif intent.intent_type == IntentType.COMPANION_MODE:
            return await self._handle_companion_mode(intent, tool_context)
        
        else:
            # =====================================================================
            # 🚫 NOT A TRUE ACTION - Return failure so it flows to orchestrator
            # =====================================================================
            # If we reach here, the intent was incorrectly classified as an action.
            # Return success=False so the calling code passes it to the intelligent
            # orchestrator which can handle it with proper semantic understanding.
            logger.info(f"📤 Intent '{intent.intent_type.value}' is not a true action, passing to orchestrator")
            return {
                'success': False,
                'pass_to_orchestrator': True,
                'intent': intent.to_dict()
            }
    
    async def _handle_reminder(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle reminder action"""
        params = intent.extracted_params
        
        # Get reminder parameters
        message = params.get('message', 'Study reminder')
        remind_at = params.get('remind_at', 'tomorrow')
        
        logger.info(f"🔔 Handling reminder: message='{message}', remind_at='{remind_at}'")
        logger.info(f"🔔 Context: {context}")
        
        # Execute reminder tool
        logger.info(f"🔔 Executing schedule_reminder tool...")
        result = await self.tool_registry.execute_tool(
            'schedule_reminder',
            context=context,
            message=message,
            remind_at=remind_at,
            reminder_type='custom'
        )
        logger.info(f"🔔 Tool result: success={result.success}, output={result.output}")
        
        if result.success:
            # Handle both ToolResult variants: base_tool uses 'data', registry uses 'metadata'
            result_data = getattr(result, 'data', None) or getattr(result, 'metadata', None)
            return {
                'success': True,
                'action_taken': 'reminder_scheduled',
                'response': result.output,
                'data': result_data
            }
        else:
            return {
                'success': False,
                'action_taken': 'reminder_failed',
                'response': result.output or "I couldn't set the reminder. Please try again with a clearer time.",
                'error': result.error
            }
    
    async def _handle_notification(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle notification action"""
        params = intent.extracted_params
        
        # This is usually for sending notifications to others
        # For now, acknowledge and explain
        return {
            'success': True,
            'action_taken': 'notification_acknowledged',
            'response': "I can send you notifications about your study progress! Would you like me to set up daily reminders or streak alerts?"
        }
    
    # =========================================================================
    # 🚫 DEPRECATED HANDLERS REMOVED
    # =========================================================================
    # The following handlers have been REMOVED as they bypass intelligent routing:
    # - _handle_summary: Now handled by LLM with memory context
    # - _handle_progress_check: Now handled by agents with analytics
    # - _handle_weak_topics: Now handled by agents with analytics
    # - _handle_break_request: Now handled by empathetic LLM response
    # - _handle_motivation: Now handled by empathetic LLM response
    # - _handle_greeting: Now handled by personalized LLM response
    # - _handle_study_plan: Now handled by MentorAgent + StudyPlannerTool
    #
    # All of these intents now flow to UnifiedAIOrchestrator which uses:
    # 1. SemanticIntentClassifier - True LLM-based understanding
    # 2. Dynamic agent routing - Right agent for the task
    # 3. Memory integration - Personalized context
    # 4. Tool invocation when needed - Real tool execution
    #
    # This ensures:
    # - INTELLIGENT responses (not hardcoded templates)
    # - EMPATHETIC handling (emotional understanding)
    # - ADAPTIVE behavior (context-aware)
    # - AGENTIC processing (reasoning + tools)
    # =========================================================================
    
    async def _handle_recurring_reminder(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle recurring reminder action"""
        params = intent.extracted_params
        
        logger.info(f"🔄 Handling recurring reminder: {params}")
        
        # Execute recurring reminder tool
        result = await self.tool_registry.execute_tool(
            'schedule_recurring_reminder',
            context=context,
            message=params.get('message', 'Study reminder'),
            time=params.get('time', '6pm'),
            frequency=params.get('frequency', 'daily'),
            days=params.get('days'),
            subject=params.get('subject')
        )
        
        if result.success:
            result_data = getattr(result, 'data', None) or getattr(result, 'metadata', None)
            return {
                'success': True,
                'action_taken': 'recurring_reminder_scheduled',
                'response': result.output,
                'data': result_data
            }
        else:
            return {
                'success': False,
                'action_taken': 'recurring_reminder_failed',
                'response': result.output or "I couldn't set the recurring reminder. Please try again.",
                'error': result.error
            }
    
    async def _handle_companion_mode(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle companion mode (Sathi) - TRUE AGENTIC companion interaction.
        
        This routes requests like:
        - "hey Sathi" / "hi sathi"
        - "stay with me for 30 mins"
        - "keep me accountable"
        - "check in with me later"
        
        Uses AgenticCompanion which is a TRUE ReAct agent with tools.
        """
        from agents.agentic_companion import create_agentic_companion
        from core.config import settings
        
        user_id = context.get('user_id')
        original_text = intent.original_text
        
        logger.info(f"🌟 Companion mode activated for user {user_id}: {original_text[:50]}...")
        
        try:
            # Create AgenticCompanion (TRUE ReAct agent)
            companion = create_agentic_companion({
                'db_client': self.db,
                'emergent_llm_key': settings.OPENAI_API_KEY
            })
            
            # Process the request through the companion
            result = await companion.process_request(
                message=original_text,
                user_id=user_id,
                context=context
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'action_taken': 'companion_mode',
                    'response': result.get('content', "I'm here with you! What would you like to work on?"),
                    'data': {
                        'companion_name': 'Sathi',
                        'action': result.get('action_taken'),
                        'agent': 'AgenticCompanion'
                    }
                }
            else:
                # Fallback warm response
                return {
                    'success': True,
                    'action_taken': 'companion_greeting',
                    'response': (
                        "Hey! I'm Sathi, your study companion. 🌟\n\n"
                        "I'm here to help you stay focused and motivated. "
                        "Want me to set a reminder, create a study plan, or just keep you company while you study?"
                    ),
                    'data': {'companion_name': 'Sathi', 'fallback': True}
                }
            
        except Exception as e:
            logger.error(f"Companion mode error: {e}")
            return {
                'success': True,  # Still return success with fallback
                'action_taken': 'companion_greeting',
                'response': (
                    "I'm Sathi, here to support you! 🌟\n\n"
                    "Tell me what's on your mind or what you're studying today."
                ),
                'error': str(e),
                'data': {'companion_name': 'Sathi', 'fallback': True}
            }


# ==============================================
# Module-level convenience functions
# ==============================================

_router_instance = None

async def get_agentic_router(db_client=None) -> AgenticRouter:
    """Get singleton agentic router instance"""
    global _router_instance
    
    if _router_instance is None:
        # db_client should always be provided by ai.py endpoint
        # If not, router will work without db (some tools may fail)
        _router_instance = AgenticRouter(db_client)
    
    return _router_instance


async def route_message(
    message: str,
    user_id: str,
    context: Dict[str, Any] = None,
    db_client=None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Convenience function to route a message.
    
    Returns:
        (handled, result) - If handled=True, use result instead of LLM response
    """
    router = await get_agentic_router(db_client)
    
    # Add db_client to context so tools can use it
    enriched_context = context.copy() if context else {}
    if db_client is not None:
        enriched_context['db'] = db_client
    
    return await router.route(message, user_id, enriched_context)





