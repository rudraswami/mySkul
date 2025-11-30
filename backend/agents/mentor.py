"""
Mentor Agent - Emotional & Conceptual Guidance
Handles intuitive explanations with metaphors and relatable examples
"""
import logging
import os
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MentorAgent(BaseAgent):
    """
    Mentor Agent provides emotional, conceptual, intuitive explanations
    
    Key Features:
    - Uses metaphors and relatable examples
    - Friendly, confidence-building tone
    - Indian context and cultural relevance
    - Adaptive to student's emotional state
    """
    
    def get_agent_type(self) -> str:
        return "Mentor"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mentor-style conceptual explanation
        
        Args:
            query: Student's question
            context: Dict with subject, student_profile, etc.
        
        Returns:
            Mentor response with emotional guidance and metaphors
        """
        try:
            logger.info(f"👨‍🏫 Mentor processing: {query[:100]}")
            
            # Check if this is a greeting
            query_lower = query.lower().strip()
            greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
            is_greeting = query_lower.strip('!?.,:;') in greeting_words
            
            if is_greeting:
                # Generate friendly greeting response
                student_profile = context.get('student_profile', {})
                greeting_response = self._generate_greeting(student_profile)
                return self._format_response(
                    content=greeting_response,
                    metadata={
                        'tone': 'friendly',
                        'approach': 'greeting',
                        'is_greeting': True
                    }
                )
            
            # Extract context
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            memory_context = context.get('memory_context')
            
            # Build dynamic mentor prompt (varied, conversational)
            from services.dynamic_mentor_prompts import get_dynamic_mentor_prompt
            
            mentor_prompt = get_dynamic_mentor_prompt(
                query=query,
                subject=subject,
                student_profile=student_profile,
                memory_context=memory_context,
                user_id=context.get('user_id', 'anonymous')
            )
            
            # Call LLM for mentor response
            mentor_response = await self._generate_mentor_response(mentor_prompt)
            
            return self._format_response(
                content=mentor_response,
                metadata={
                    'tone': 'emotional',
                    'approach': 'conceptual',
                    'metaphor_used': student_profile.get('interests', ['cricket'])[0] if student_profile.get('interests') else 'cricket'
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Mentor agent error: {e}", exc_info=True)
            return self._format_error(f"Mentor processing failed: {str(e)}")
    
    def _build_mentor_prompt(
        self,
        query: str,
        subject: str,
        student_profile: Dict[str, Any],
        memory_context: Dict[str, Any] = None
    ) -> str:
        """Build mentor-specific prompt with memory context"""
        
        # Student details
        name = student_profile.get('name', '')
        region = student_profile.get('region', 'India')
        interests = student_profile.get('interests', ['cricket', 'gaming'])
        board = student_profile.get('board', 'CBSE')
        exam = student_profile.get('exam', 'JEE')
        mastery_level = student_profile.get('mastery_level', 50)
        
        # LANGUAGE PREFERENCE - Only use Hinglish if student prefers it
        language = student_profile.get('language', 'en')  # Default: English
        use_hinglish = language in ['hi', 'hinglish', 'hindi']
        
        # Memory context
        memory_str = ""
        if memory_context:
            # Continuity check
            continuity = memory_context.get('continuity', {})
            if continuity.get('is_continuation'):
                memory_str += f"\n\nIMPORTANT - Conversation Continuity:\n"
                memory_str += f"Last time, you covered: {', '.join(continuity.get('concepts_covered_before', [])[:3])}\n"
                memory_str += f"{continuity.get('suggestion', '')}\n"
            
            # Relevant past memories
            relevant_memories = memory_context.get('relevant_memories', [])
            if relevant_memories:
                memory_str += f"\n\nStudent's Learning History:\n"
                for mem in relevant_memories[:3]:
                    memory_str += f"- {mem['content']}\n"
        
        # Adaptive instructions based on mastery
        depth_instruction = self._get_depth_instruction(mastery_level)
        
        # Personalized greeting
        greeting = f"Hey {name}!" if name else "Hey there!"
        
        # Language instruction - CONDITIONAL
        if use_hinglish:
            language_instruction = """9. HINGLISH SUPPORT: Student prefers Hindi-English mix. Naturally use:
   - "matlab" (means), "yaar" (friend), "bhai" (bro), "arre" (hey)
   - "samjho" (understand), "dekho" (see), "basically" "actually"
   - Example: "Dekho, basically force matlab push ya pull hai, samjhe?"
   - Use 2-3 Hinglish words per response naturally, not forced"""
        else:
            language_instruction = """9. LANGUAGE: Respond in clear, simple ENGLISH only.
   - Use easy-to-understand vocabulary
   - NO Hindi/Hinglish words (student prefers English)
   - Keep sentences short and crisp
   - Use relatable Indian examples but in English"""
        
        return f"""You are a caring AI Mentor helping {name if name else 'an Indian student'} prepare for {exam} ({board} board).

Student Context:
- Name: {name if name else 'Student'}
- Region: {region}
- Language Preference: {'Hindi/Hinglish' if use_hinglish else 'English only'}
- Interests: {', '.join(interests)}
- Subject: {subject}
- Current Mastery: {mastery_level}/100 ({self._get_mastery_label(mastery_level)})

{memory_str}

Question: {query}

Your role as MENTOR:
1. {greeting} Be PERSONAL - use their name and reference their learning history
2. {depth_instruction}
3. **SPECIAL RULE FOR IMAGES**: If the question mentions "[Student uploaded an image" or contains "IMAGE CONTAINS:", this is an image-based question:
   - Focus ONLY on the extracted content from the image
   - NO metaphors or creative stories - be DIRECT and FACTUAL
   - If it's an MCQ, identify the question and explain options
   - If it's a problem, solve it step-by-step
   - Be precise and educational, not creative
4. For TEXT-only questions: Use METAPHORS from student's interests ({interests[0]} preferred)
5. Give INTUITIVE explanations, not formal derivations
6. Be friendly, encouraging, and culturally relevant
7. If continuing a topic, acknowledge what was covered before
8. Adapt your explanation depth to their mastery level
{language_instruction}

Keep response concise (150-200 words) and warm in tone.

Mentor's Explanation:"""
    
    def _get_depth_instruction(self, mastery_level: int) -> str:
        """Get instruction for explanation depth based on mastery"""
        if mastery_level < 30:
            return "Use VERY SIMPLE language, more visuals, basic examples (beginner level)"
        elif mastery_level < 70:
            return "Use balanced approach with examples and moderate theory (intermediate level)"
        else:
            return "Student is advanced - use deeper insights, proofs, exam tricks (advanced level)"
    
    def _get_mastery_label(self, mastery_level: int) -> str:
        """Convert mastery number to label"""
        if mastery_level < 30:
            return "Beginner"
        elif mastery_level < 70:
            return "Intermediate"
        else:
            return "Advanced"
    
    async def _generate_mentor_response(self, prompt: str) -> str:
        """Call LLM to generate mentor response"""
        try:
            # Use LlmChat with proper chaining (same as AIService)
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import uuid
            
            # Initialize with system message for mentor context
            mentor_system = "You are a caring AI Mentor helping Indian students prepare for competitive exams. Use metaphors from cricket, cooking, or daily life. Be encouraging and explain concepts intuitively. Keep responses conversational and concise (150-200 words)."
            
            llm_client = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"mentor_{str(uuid.uuid4())[:8]}",
                system_message=mentor_system
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.8,  # Higher for creativity
                top_p=0.9,
                max_tokens=400
            )
            
            # Send prompt (use send_message, not send_message_async)
            user_msg = UserMessage(text=prompt)  # text, not content
            response = await llm_client.send_message(user_msg)
            
            if not response:
                raise Exception("Empty response from LLM")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            # Fallback response
            return """I understand you're working on this concept. While I'm having trouble generating a detailed explanation right now, remember that every complex topic becomes clearer with practice. Think of learning like building muscle memory - each attempt makes the next one easier. Let's break this down step by step together."""
    
    def _generate_greeting(self, student_profile: Dict[str, Any]) -> str:
        """Generate a friendly greeting response"""
        import random
        
        region = student_profile.get('region', 'India')
        exam = student_profile.get('exam', 'JEE')
        
        greetings = [
            f"Hey there! 👋 Ready to tackle some {exam} concepts today? I'm here to help you understand anything you're working on!",
            f"Hello! 😊 Great to see you! What concept would you like to explore today? Whether it's tough formulas or tricky theories, we'll break it down together!",
            f"Hi! 🌟 I'm your AI Mentor, here to help you ace {exam}. Ask me anything - from quick doubts to deep concepts - and I'll explain it in the simplest way possible!",
            f"Namaste! 🙏 Ready for some learning? I'm here to make complex concepts feel easy. What would you like to understand today?",
            f"Hey! 💪 Let's crush some concepts together! Whether you need quick clarification or a detailed explanation, I've got you covered!"
        ]
        
        return random.choice(greetings)

