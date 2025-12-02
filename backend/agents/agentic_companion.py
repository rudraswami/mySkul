"""
🌟 Agentic Companion - TRUE Human-like Proactive Agent
======================================================

This is the UPGRADED version of ProactiveCompanionAgent that uses
the TRUE AGENTIC system with actual tools.

When user says "remind me tomorrow at 4pm":
- OLD: ProactiveCompanionAgent detected it but couldn't execute
- NEW: AgenticCompanion detects AND executes via ReminderTool

This agent is a 24/7 learning partner that:
- Actually schedules reminders (not just talks about it)
- Actually sends notifications
- Actually tracks and protects streaks
- Remembers everything about the student
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import create_tool_registry
from services.action_intent_detector import get_intent_detector, IntentType

logger = logging.getLogger(__name__)


class AgenticCompanion(ReActAgent):
    """
    A TRUE agentic companion that can take real actions.
    
    This agent uses the ReAct loop and has access to action tools:
    - schedule_reminder: Actually schedule reminders
    - send_notification: Actually send notifications
    - send_study_summary: Actually generate and send summaries
    """
    
    COMPANION_NAME = "Sathi"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry WITH action tools
        self.tool_registry = create_tool_registry(
            include_default=True,
            include_action_tools=True
        )
        
        # Intent detector for understanding user requests
        self.intent_detector = get_intent_detector()
        
        logger.info("🌟 AgenticCompanion initialized with TRUE action capabilities")
    
    def get_agent_name(self) -> str:
        return "AgenticCompanion"
    
    def get_agent_persona(self) -> str:
        return f"""You are {self.COMPANION_NAME}, a caring AI learning companion.

YOUR CHARACTER:
- You're like a supportive older sibling who genuinely cares about the student
- You remember everything they've told you
- You take REAL ACTIONS - you don't just talk about doing things
- When asked to set a reminder, you ACTUALLY set it using tools
- When asked to send a summary, you ACTUALLY send it

YOUR CAPABILITIES (USE THESE TOOLS):
- schedule_reminder: Set actual reminders that will notify the student
- send_notification: Send immediate alerts to the student
- send_study_summary: Generate and send study progress reports

YOUR APPROACH:
1. Understand what the student ACTUALLY wants
2. If they want an ACTION (reminder, notification), USE THE TOOLS
3. Confirm the action was taken
4. Be warm and supportive in your responses

IMPORTANT:
- When student says "remind me tomorrow at 4pm", USE schedule_reminder tool!
- When student says "send me a summary", USE send_study_summary tool!
- Don't just say "I'll remind you" - ACTUALLY DO IT!

NEVER:
- Pretend to do something without using tools
- Say you'll remind them without calling schedule_reminder
- Be fake or overly cheerful - be genuine
"""
    
    def get_available_tools(self) -> List[str]:
        return [
            "schedule_reminder",
            "send_notification", 
            "send_study_summary",
            "calculator",
            "knowledge_search"
        ]
    
    async def process_request(
        self,
        message: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user request - detect if it needs action and execute.
        
        This is the main entry point for the companion.
        """
        context = context or {}
        context['user_id'] = user_id
        
        # Detect intent
        intent = self.intent_detector.detect(message)
        
        logger.info(f"🌟 AgenticCompanion processing: {message[:50]}...")
        logger.info(f"   Intent: {intent.intent_type.value}, Requires Action: {intent.requires_action}")
        
        if intent.requires_action:
            # Use ReAct loop to handle the action
            return await self.run(message, context)
        else:
            # Simple response for non-action requests
            return await self._generate_simple_response(message, context)
    
    async def _generate_simple_response(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a simple response for non-action requests"""
        # For simple greetings or chats, respond directly
        message_lower = message.lower().strip()
        
        if message_lower in ['hi', 'hello', 'hey', 'namaste']:
            return {
                'success': True,
                'content': f"Hey! I'm here to help. Want me to set a reminder, send you a study summary, or just chat about your learning? 😊",
                'action_taken': None
            }
        
        # Use LLM for other responses
        try:
            from services.llm_service import LlmChat, UserMessage
            
            if not self.llm_key:
                return {
                    'success': False,
                    'content': "I'm having trouble responding right now. Please try again!",
                    'error': 'No LLM key'
                }
            
            chat = LlmChat(
                api_key=self.llm_key,
                session_id=f"companion_{datetime.now().timestamp()}",
                system_message=self.get_agent_persona()
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.7,
                max_tokens=300
            )
            
            response = await chat.send_message(UserMessage(text=message))
            
            return {
                'success': True,
                'content': response,
                'action_taken': None
            }
            
        except Exception as e:
            logger.error(f"Companion response error: {e}")
            return {
                'success': False,
                'content': "Let me know if you want to set a reminder or get a study summary!",
                'error': str(e)
            }


# ==============================================
# Factory function
# ==============================================

def create_agentic_companion(config: Dict[str, Any] = None) -> AgenticCompanion:
    """Create an AgenticCompanion instance"""
    return AgenticCompanion(config)


# ==============================================
# Integration with existing ProactiveCompanionAgent
# ==============================================

async def process_reminder_request(
    message: str,
    user_id: str,
    context: Dict[str, Any] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process a reminder request using the TRUE agentic system.
    
    This function bridges the old ProactiveCompanionAgent to the new
    agentic infrastructure.
    """
    companion = create_agentic_companion(config)
    return await companion.process_request(message, user_id, context)

