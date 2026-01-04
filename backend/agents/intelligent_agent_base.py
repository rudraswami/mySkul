"""
🧠 INTELLIGENT AGENT BASE - LLM-Powered Agent Framework

Philosophy: Agents should GUIDE the LLM, not REPLACE it.

The Problem with Template Agents:
- Template responses feel robotic
- No real intelligence
- Can't adapt to context
- Break conversation flow

The Solution:
- Agents provide SPECIALIZED PROMPTS to the LLM
- Agents add CONTEXT and PERSONA
- LLM generates the actual intelligent response
- Agents post-process to add structure (if needed)

This base class provides:
1. LLM integration for all agents
2. Specialized prompt building
3. Context management
4. Response formatting
"""

import logging
import os
from typing import Dict, Any, Optional, List
from abc import abstractmethod
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class IntelligentAgentBase(BaseAgent):
    """
    Base class for LLM-powered intelligent agents
    
    Instead of returning templates, this agent:
    1. Builds a specialized system prompt
    2. Calls the LLM with that prompt
    3. Returns an intelligent, contextual response
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.llm_key = config.get('emergent_llm_key') if config else os.environ.get('OPENAI_API_KEY')
    
    @abstractmethod
    def get_agent_persona(self) -> str:
        """
        Return the persona/character for this agent.
        Example: "You are a supportive study buddy named Priya..."
        """
        pass
    
    @abstractmethod
    def get_specialized_instructions(self, query: str, context: Dict[str, Any]) -> str:
        """
        Return specialized instructions for handling this type of query.
        This is what makes each agent unique.
        """
        pass
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Build context summary for LLM"""
        student = context.get('student_profile', {})
        session = context.get('session_data', {})
        
        parts = []
        
        # Student info
        name = student.get('user_name') or student.get('name')
        if name and len(name) > 1:
            parts.append(f"Student's name: {name}")
        
        exam = student.get('exam') or 'JEE'
        parts.append(f"Preparing for: {exam}")
        
        subject = context.get('subject', 'General')
        parts.append(f"Current subject: {subject}")
        
        # Session context
        if session.get('current_streak', 0) > 0:
            parts.append(f"Current streak: {session['current_streak']} days")
        
        if session.get('topics_covered'):
            parts.append(f"Recently studied: {', '.join(session['topics_covered'][:3])}")
        
        return '\n'.join(parts) if parts else "Student context: General learner"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process query using LLM with specialized prompt
        """
        try:
            logger.info(f"🧠 {self.get_agent_type()} processing with LLM...")
            
            # Build the intelligent prompt
            system_prompt = self._build_system_prompt(query, context)
            
            # Call LLM
            response_text = await self._call_llm(query, system_prompt, context)
            
            if not response_text:
                # Attempt LLM-based recovery instead of static template
                logger.warning(f"⚠️ LLM call failed, attempting recovery")
                response_text = await self._get_recovery_response(query, context)
            
            # Post-process if needed
            final_response = self._post_process_response(response_text, query, context)
            
            return self._format_response(
                content=final_response,
                metadata={
                    'agent': self.get_agent_type(),
                    'llm_powered': True,
                    'context_used': True
                }
            )
            
        except Exception as e:
            logger.error(f"❌ {self.get_agent_type()} error: {e}", exc_info=True)
            return self._format_error(f"Agent processing failed: {str(e)}")
    
    def _build_system_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build the complete system prompt for LLM"""
        
        # Get agent-specific components
        persona = self.get_agent_persona()
        instructions = self.get_specialized_instructions(query, context)
        context_summary = self.get_context_summary(context)
        
        # Get language preference
        language = context.get('student_profile', {}).get('language', 'en')
        
        if language in ['hi', 'hindi', 'hinglish']:
            language_instruction = """
LANGUAGE: Use Hinglish naturally - mix Hindi and English like Indian students do.
Examples: "Dekho...", "matlab...", "samjho...", "basically...", "bhai/yaar..."
"""
        else:
            language_instruction = """
LANGUAGE: Use simple, clear English. Be friendly but not overly casual.
"""
        
        prompt = f"""{persona}

STUDENT CONTEXT:
{context_summary}

{instructions}

{language_instruction}

CRITICAL RULES:
1. Be CONVERSATIONAL - like chatting with a friend, not lecturing
2. Keep responses CONCISE - 3-5 sentences unless more detail needed
3. Be ENCOURAGING without being fake or cringe
4. If student seems frustrated/bored, acknowledge it genuinely
5. Use student's name naturally (if known)
6. Ask follow-up questions to keep engagement
7. DON'T start with "I'll keep this short" - just be concise naturally

Current query: {query}
"""
        return prompt
    
    async def _call_llm(
        self,
        query: str,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Call LLM with the specialized prompt"""
        try:
            if not self.llm_key:
                logger.warning("No LLM key available")
                return None
            
            from services.llm_service import LlmChat, UserMessage
            
            session_id = context.get('session_id', 'agent_session')
            
            chat = LlmChat(
                api_key=self.llm_key,
                session_id=f"{self.get_agent_type()}_{session_id}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.8,  # More creative
                max_tokens=400,   # Concise but complete
                presence_penalty=0.3,  # Avoid repetition
                frequency_penalty=0.3
            )
            
            user_msg = UserMessage(text=query)
            response = await chat.send_message(user_msg)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None
    
    async def _get_recovery_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        Recovery response using alternate LLM when primary fails.
        
        PRINCIPLE: Failures reduce richness, NOT intelligence.
        - Always attempt real LLM reasoning
        - Never return static templates
        """
        logger.info(f"🔄 {self.get_agent_type()} attempting LLM recovery...")
        
        subject = context.get('subject', 'your question')
        recovery_prompt = f"""You are a helpful tutor. Answer this student's question directly:

Question: {query}
Subject: {subject}

Provide a clear, helpful answer. Be concise but complete."""

        try:
            # Try Gemini Flash for fast recovery
            import google.generativeai as genai
            from core.config import settings
            import asyncio
            
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: model.generate_content(recovery_prompt)
                    ),
                    timeout=10.0
                )
                
                if response and response.text and len(response.text.strip()) > 20:
                    logger.info(f"✅ {self.get_agent_type()} recovery successful")
                    return response.text
                    
        except Exception as e:
            logger.warning(f"⚠️ {self.get_agent_type()} Gemini recovery failed: {e}")
        
        # Final fallback: contextual acknowledgment
        short_q = query[:50] + "..." if len(query) > 50 else query
        return f"""I'm having trouble processing your question about "{short_q}" right now.

Could you try asking again? I want to give you a helpful answer about {subject}."""
    
    def _post_process_response(
        self,
        response: str,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Post-process the LLM response - override in subclass if needed"""
        return response












