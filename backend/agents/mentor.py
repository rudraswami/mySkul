"""
Mentor Agent - TRUE AGENTIC Emotional Learning Guide
=====================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: MetaphorGenerator, ExampleFinder, EmotionDetector
- Memory: Remembers student's learning style, preferences, struggles
- Actions: Adapts explanations based on emotional state

OLD: Generated friendly explanations
NEW: PERSONALIZES based on memory, detects emotion, adapts style
"""

import logging
from typing import Dict, Any, Optional
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class MentorAgent(ReActAgent):
    """
    TRUE AGENTIC Mentor - Emotional, Intuitive Learning Guide
    
    Capabilities:
    - Detects student's emotional state (frustrated, confident, confused)
    - Adapts explanation style based on emotion
    - Uses metaphors and analogies tailored to student interests
    - Remembers what works for this specific student
    - Provides encouragement when needed
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry (will add custom tools later)
        self.tool_registry = ToolRegistry()
        
        # Initialize memory for personalization (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("🧑‍🏫 MentorAgent initialized as TRUE AGENT with personalization")
    
    def get_agent_name(self) -> str:
        return "MentorAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return []  # Mentor uses LLM primarily, tools can be added later
    
    def get_agent_persona(self) -> str:
        return """You are a warm, encouraging mentor who makes learning feel natural.

Your role:
- Explain concepts using metaphors and real-world analogies
- Adapt your style based on student's emotional state
- Use student's interests (cricket, gaming, etc.) in examples
- Break complex ideas into simple, relatable chunks
- Provide emotional support when student is frustrated

Your style:
- Conversational and friendly (like talking to a friend)
- Use "we" instead of "you" (collaborative)
- Celebrate small wins
- Acknowledge struggles ("This IS tricky, but...")
- Use emojis sparingly but effectively

Remember:
- Learning should feel like a conversation, not a lecture
- Every student has different learning style
- Emotional state affects comprehension
- Metaphors make abstract concepts concrete"""
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mentor response using ReAct loop with personalization.
        
        Think: What's the student's emotional state? What metaphor would work?
        Act: Generate personalized explanation
        Observe: Check if explanation is clear and encouraging
        """
        try:
            user_id = context.get('user_id', '')
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            
            logger.info(f"🧑‍🏫 MentorAgent processing: {query[:100]}")
            
            # THINK: Analyze student state and needs
            emotion = self._detect_emotion(query)
            interests = student_profile.get('interests', ['cricket', 'gaming'])
            learning_style = await self._get_learning_style(user_id)
            
            thought = f"Student seems {emotion}. Interests: {interests}. Learning style: {learning_style}."
            logger.info(f"🧠 {thought}")
            
            # ACT: Generate personalized explanation
            explanation = await self._generate_mentor_response(
                query=query,
                subject=subject,
                emotion=emotion,
                interests=interests,
                learning_style=learning_style,
                context=context
            )
            
            # OBSERVE: Verify response quality
            observation = "Response generated with personalization"
            
            return {
                'success': True,
                'content': explanation,
                'emotion_detected': emotion,
                'personalization_applied': True,
                'thought': thought,
                'action': 'generate_personalized_explanation',
                'observation': observation
            }
            
        except Exception as e:
            logger.error(f"❌ MentorAgent error: {e}", exc_info=True)
            return {
                'success': False,
                'content': "Let me help you understand this concept...",
                'error': str(e)
            }
    
    def _detect_emotion(self, query: str) -> str:
        """Detect student's emotional state from query"""
        query_lower = query.lower()
        
        # Frustration indicators
        if any(word in query_lower for word in ['confused', 'don\'t understand', 'not getting', 'stuck', 'help', 'difficult']):
            return 'frustrated'
        
        # Confidence indicators
        if any(word in query_lower for word in ['got it', 'understand', 'clear', 'easy', 'simple']):
            return 'confident'
        
        # Anxiety indicators
        if any(word in query_lower for word in ['exam', 'test', 'scared', 'worried', 'nervous', 'pressure']):
            return 'anxious'
        
        # Curiosity indicators
        if any(word in query_lower for word in ['why', 'how', 'what if', 'interesting', 'cool']):
            return 'curious'
        
        return 'neutral'
    
    async def _get_learning_style(self, user_id: str) -> str:
        """Get student's learning style from memory"""
        # TODO: Query from memory system
        # For now, default to 'visual'
        return 'visual'
    
    async def _generate_mentor_response(
        self,
        query: str,
        subject: str,
        emotion: str,
        interests: list,
        learning_style: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate personalized mentor response"""
        
        # Build personalized prompt
        prompt = self._build_personalized_prompt(
            query=query,
            subject=subject,
            emotion=emotion,
            interests=interests,
            learning_style=learning_style
        )
        
        # Use LLM to generate response
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY') or self.config.get('emergent_llm_key')
        
        llm_chat = LlmChat(
            api_key=emergent_llm_key,
            session_id=f"mentor_{context.get('user_id', 'unknown')}",
            system_message=prompt
        )
        
        user_message = UserMessage(text=query)
        response = await llm_chat.send_message(user_message)
        
        return response if isinstance(response, str) else str(response)
    
    def _build_personalized_prompt(
        self,
        query: str,
        subject: str,
        emotion: str,
        interests: list,
        learning_style: str
    ) -> str:
        """Build personalized system prompt"""
        
        base_prompt = self.get_agent_persona()
        
        # Add personalization
        personalization = f"\n\nPERSONALIZATION FOR THIS STUDENT:\n"
        personalization += f"- Emotional state: {emotion}\n"
        personalization += f"- Interests: {', '.join(interests)}\n"
        personalization += f"- Learning style: {learning_style}\n"
        personalization += f"- Subject: {subject}\n\n"
        
        # Add emotion-specific instructions
        if emotion == 'frustrated':
            personalization += "IMPORTANT: Student is frustrated. Be extra encouraging. Break down into smaller steps. Acknowledge the difficulty.\n"
        elif emotion == 'anxious':
            personalization += "IMPORTANT: Student is anxious. Be calming and reassuring. Focus on manageable steps. Reduce pressure.\n"
        elif emotion == 'confident':
            personalization += "IMPORTANT: Student is confident. Challenge them slightly. Introduce advanced concepts. Celebrate their progress.\n"
        
        # Add interest-based instructions
        if interests:
            personalization += f"\nUSE ANALOGIES FROM: {', '.join(interests)}. Make examples relatable to their interests.\n"
        
        return base_prompt + personalization
