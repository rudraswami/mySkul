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
        
        elif intent.intent_type == IntentType.RECURRING_REMINDER:
            return await self._handle_recurring_reminder(intent, tool_context)
        
        elif intent.intent_type == IntentType.NOTIFICATION:
            return await self._handle_notification(intent, tool_context)
        
        elif intent.intent_type == IntentType.SUMMARY:
            return await self._handle_summary(intent, tool_context)
        
        elif intent.intent_type == IntentType.STUDY_PLAN:
            return await self._handle_study_plan(intent, tool_context)
        
        elif intent.intent_type == IntentType.PROGRESS_CHECK:
            return await self._handle_progress_check(intent, tool_context)
        
        elif intent.intent_type == IntentType.WEAK_TOPICS:
            return await self._handle_weak_topics(intent, tool_context)
        
        elif intent.intent_type == IntentType.BREAK_REQUEST:
            return await self._handle_break_request(intent, tool_context)
        
        elif intent.intent_type == IntentType.MOTIVATION:
            return await self._handle_motivation(intent, tool_context)
        
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
            # Handle both ToolResult variants: base_tool uses 'data', registry uses 'metadata'
            result_data = getattr(result, 'data', None) or getattr(result, 'metadata', None)
            return {
                'success': True,
                'action_taken': 'summary_sent',
                'response': result.output,
                'data': result_data
            }
        else:
            return {
                'success': False,
                'action_taken': 'summary_failed',
                'response': "I couldn't generate your summary right now. Let me tell you about your progress instead!",
                'error': result.error
            }
    
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
    
    async def _handle_study_plan(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle study plan creation request"""
        params = intent.extracted_params
        exam = params.get('exam', 'JEE')
        duration = params.get('duration', 30)
        duration_unit = params.get('duration_unit', 'day')
        
        # For now, return a helpful response
        # TODO: Implement full study plan generator
        response = f"""🎯 **Study Plan for {exam}**

I'll help you prepare! Here's what we'll do:

1. **Assessment** - Let's identify your current level
2. **Weak Areas** - Focus on topics that need work
3. **Daily Schedule** - Consistent study routine
4. **Weekly Tests** - Track your progress
5. **Revision** - Spaced repetition for retention

Would you like me to:
• Start with a quick assessment?
• Show your weak topics first?
• Create a daily reminder schedule?

Just let me know! 💪"""
        
        return {
            'success': True,
            'action_taken': 'study_plan_offered',
            'response': response,
            'data': {'exam': exam, 'duration': duration, 'unit': duration_unit}
        }
    
    async def _handle_progress_check(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle progress check request"""
        try:
            from services.intelligent_proactive_mentor import get_proactive_mentor
            
            db = context.get('db')
            if db:
                mentor = await get_proactive_mentor(db)
                user_id = context.get('user_id')
                
                # Get user stats
                user = await db.users.find_one({'user_id': user_id})
                streak = user.get('streak', 0) if user else 0
                xp = user.get('xp', 0) if user else 0
                
                # Get weak topics
                weak_topics = await mentor.analyze_weak_topics(user_id)
                
                response = f"""📊 **Your Progress Report**

🔥 **Streak:** {streak} days
⭐ **XP:** {xp} points

"""
                if weak_topics:
                    response += "📈 **Areas to improve:**\n"
                    for topic in weak_topics[:3]:
                        response += f"• {topic['topic']} ({topic['average_score']}%)\n"
                else:
                    response += "✨ Great job! No weak areas detected.\n"
                
                response += "\nKeep going! Every question makes you stronger! 💪"
                
                return {
                    'success': True,
                    'action_taken': 'progress_checked',
                    'response': response,
                    'data': {'streak': streak, 'xp': xp, 'weak_topics': weak_topics}
                }
        except Exception as e:
            logger.error(f"Progress check error: {e}")
        
        return {
            'success': True,
            'action_taken': 'progress_checked',
            'response': "Let me check your progress... Keep studying and I'll track your improvement! 📈"
        }
    
    async def _handle_weak_topics(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle weak topics analysis request"""
        try:
            from services.intelligent_proactive_mentor import get_proactive_mentor
            
            db = context.get('db')
            if db:
                mentor = await get_proactive_mentor(db)
                user_id = context.get('user_id')
                
                weak_topics = await mentor.analyze_weak_topics(user_id)
                
                if weak_topics:
                    response = "🎯 **Your Weak Areas (Focus Here!)**\n\n"
                    for i, topic in enumerate(weak_topics, 1):
                        trend_emoji = "📈" if topic.get('trend') == 'improving' else "⚠️"
                        response += f"{i}. **{topic['topic']}** - {topic['average_score']}% avg {trend_emoji}\n"
                    response += "\nWant me to help you practice these? Just say the topic name!"
                else:
                    response = "🌟 **Great news!** I haven't found any significant weak areas. Keep up the excellent work!\n\nWant me to give you some challenging problems to test yourself?"
                
                return {
                    'success': True,
                    'action_taken': 'weak_topics_analyzed',
                    'response': response,
                    'data': {'weak_topics': weak_topics}
                }
        except Exception as e:
            logger.error(f"Weak topics error: {e}")
        
        return {
            'success': True,
            'action_taken': 'weak_topics_analyzed',
            'response': "I need more quiz/test data to analyze your weak areas. Try taking a few practice tests first! 📝"
        }
    
    async def _handle_break_request(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle break request"""
        duration = intent.extracted_params.get('duration', 10)
        
        response = f"""☕ **Break Time!** ({duration} minutes)

Taking breaks is smart studying! Here's what to do:

• 🚶 Stretch or walk around
• 💧 Drink some water
• 👀 Look at something far away (rest your eyes)
• 🧘 Take 5 deep breaths

I'll remind you when your break is over. Relax! 😊"""
        
        # Schedule break end reminder
        try:
            result = await self.tool_registry.execute_tool(
                'schedule_reminder',
                context=context,
                message="Break over! Time to get back to studying 📚",
                remind_at=f"in {duration} minutes",
                reminder_type='break'
            )
        except Exception as e:
            logger.error(f"Break reminder error: {e}")
        
        return {
            'success': True,
            'action_taken': 'break_started',
            'response': response,
            'data': {'duration': duration}
        }
    
    async def _handle_motivation(
        self,
        intent: DetectedIntent,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle motivation request - be empathetic and encouraging"""
        import random
        
        motivational_messages = [
            """💪 **I believe in you!**

Every JEE topper felt exactly like this at some point. The difference? They kept going.

Remember:
• You don't have to be perfect, just persistent
• One topic at a time, one day at a time
• Progress > Perfection

What's ONE small thing you can do right now? Even 5 minutes counts! 🌟""",

            """🌟 **Feeling low is normal**

Top performers have bad days too. What matters is what you do next.

Quick wins to get momentum:
• Solve just 1 easy problem
• Watch a 5-minute concept video
• Review notes you already made

Small steps → Big results. I'm here with you! 💪""",

            """🎯 **You've got this!**

Think about why you started. Your dreams are valid and achievable.

Today's challenge:
• Just open your book for 5 minutes
• That's it. No pressure.

Often, starting is the hardest part. Once you begin, momentum takes over. 

Ready when you are! 🚀""",

            """❤️ **It's okay to struggle**

Struggling means you're pushing your limits - that's exactly how growth happens!

Fun fact: The brain literally grows new connections when you work through hard problems.

What's bothering you the most right now? Let's tackle it together, one step at a time. 🤝"""
        ]
        
        return {
            'success': True,
            'action_taken': 'motivation_sent',
            'response': random.choice(motivational_messages)
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





