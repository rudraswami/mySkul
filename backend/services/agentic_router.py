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
            self._tool_registry = create_tool_registry(
                include_default=True,
                include_action_tools=True
            )
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
        if not settings.ENABLE_ACTION_DETECTION:
            return (False, None)
        
        # Detect intent
        intent = self.intent_detector.detect(message)
        
        logger.info(f"🎯 Detected intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")
        
        # If it's not an action request, let normal flow handle it
        if not intent.requires_action:
            return (False, None)
        
        # Handle action intent
        try:
            result = await self._handle_action(intent, user_id, context or {})
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
        """Handle an action intent by executing the appropriate tool"""
        
        # Build context for tool execution
        tool_context = {
            'user_id': user_id,
            **context
        }
        
        if intent.intent_type == IntentType.REMINDER:
            return await self._handle_reminder(intent, tool_context)
        
        elif intent.intent_type == IntentType.NOTIFICATION:
            return await self._handle_notification(intent, tool_context)
        
        elif intent.intent_type == IntentType.SUMMARY:
            return await self._handle_summary(intent, tool_context)
        
        elif intent.intent_type == IntentType.GREETING:
            return self._handle_greeting(intent)
        
        else:
            # Unknown action type - return info about what was detected
            return {
                'success': False,
                'response': f"I detected that you want to: {intent.intent_type.value}, but I can't do that yet. Let me help you another way!",
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
        
        # Execute reminder tool
        result = await self.tool_registry.execute_tool(
            'schedule_reminder',
            context=context,
            message=message,
            remind_at=remind_at,
            reminder_type='custom'
        )
        
        if result.success:
            return {
                'success': True,
                'action_taken': 'reminder_scheduled',
                'response': result.output,
                'data': result.metadata
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
    
    async def _handle_summary(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle study summary request"""
        params = intent.extracted_params
        period = params.get('period', 'week')
        
        # Execute summary tool
        result = await self.tool_registry.execute_tool(
            'send_study_summary',
            context=context,
            period=period,
            channel='notification'
        )
        
        if result.success:
            return {
                'success': True,
                'action_taken': 'summary_sent',
                'response': result.output,
                'data': result.metadata
            }
        else:
            return {
                'success': False,
                'action_taken': 'summary_failed',
                'response': "I couldn't generate your summary right now. Let me tell you about your progress instead!",
                'error': result.error
            }
    
    def _handle_greeting(self, intent: DetectedIntent) -> Dict[str, Any]:
        """Handle greeting - quick response"""
        greetings = [
            "Hey! Ready to learn something awesome? 📚",
            "Hi there! What can I help you with today? 🎯",
            "Hello! Let's make today productive! 💪",
            "Hey! Ask me anything - I'm here to help! 🤝",
        ]
        
        import random
        return {
            'success': True,
            'action_taken': 'greeting',
            'response': random.choice(greetings),
            'is_greeting': True
        }


# ==============================================
# Module-level convenience functions
# ==============================================

_router_instance = None

async def get_agentic_router(db_client=None) -> AgenticRouter:
    """Get singleton agentic router instance"""
    global _router_instance
    
    if _router_instance is None:
        if db_client is None:
            from db.mongo import get_database
            db_client = await get_database()
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
    return await router.route(message, user_id, context)





