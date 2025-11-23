"""
Professor Agent - Formal & Analytical Reasoning
Handles logical derivations, proofs, and step-by-step solutions
"""
import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ProfessorAgent(BaseAgent):
    """
    Professor Agent provides formal logic, derivations, and structured reasoning
    
    Key Features:
    - Step-by-step analytical explanations
    - Mathematical rigor and formal notation
    - Verification and proof structure
    - No metaphors (pure logic)
    """
    
    def get_agent_type(self) -> str:
        return "Professor"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate professor-style analytical explanation
        
        Args:
            query: Student's question
            context: Dict with subject, exam_mode, etc.
        
        Returns:
            Professor response with formal reasoning
        """
        try:
            logger.info(f"🧮 Professor processing: {query[:100]}")
            
            # Extract context
            subject = context.get('subject', 'Mathematics')
            exam_mode = context.get('exam_mode', 'JEE')
            student_profile = context.get('student_profile', {})
            memory_context = context.get('memory_context')
            
            # Build professor prompt with memory
            professor_prompt = self._build_professor_prompt(query, subject, exam_mode, student_profile, memory_context)
            
            # Call LLM for professor response
            professor_response = await self._generate_professor_response(professor_prompt)
            
            return self._format_response(
                content=professor_response,
                metadata={
                    'tone': 'formal',
                    'approach': 'analytical',
                    'structure': 'step_by_step'
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Professor agent error: {e}", exc_info=True)
            return self._format_error(f"Professor processing failed: {str(e)}")
    
    def _build_professor_prompt(
        self,
        query: str,
        subject: str,
        exam_mode: str,
        student_profile: Dict[str, Any] = None,
        memory_context: Dict[str, Any] = None
    ) -> str:
        """Build professor-specific prompt with adaptive depth"""
        
        # Get mastery level for adaptive depth
        mastery_level = student_profile.get('mastery_level', 50) if student_profile else 50
        
        # Determine depth and rigor based on mastery
        if mastery_level < 30:
            depth_level = "BASIC"
            rigor_instruction = "Use simple steps, explain WHY each step is needed. Avoid complex notation."
        elif mastery_level < 70:
            depth_level = "INTERMEDIATE"
            rigor_instruction = "Use standard steps with clear reasoning. Include important formulas."
        else:
            depth_level = "ADVANCED"
            rigor_instruction = "Use complete rigor, proofs, edge cases. Include exam-specific tricks."
        
        # Memory context for continuity
        memory_str = ""
        if memory_context:
            continuity = memory_context.get('continuity', {})
            if continuity.get('is_continuation'):
                memory_str = f"\n\nConversation History: Student previously learned {', '.join(continuity.get('concepts_covered_before', [])[:2])}. Build on this foundation.\n"
        
        return f"""You are a rigorous AI Professor teaching {subject} for {exam_mode} preparation.

Student Level: {depth_level} (Mastery: {mastery_level}/100)

{memory_str}

Question: {query}

Your role as PROFESSOR:
1. Provide FORMAL, step-by-step explanations
2. **SPECIAL RULE FOR IMAGES**: If the question contains "IMAGE CONTAINS:" or mentions uploaded image:
   - Analyze the ACTUAL extracted content from the image
   - If MCQ: Identify correct answer with clear reasoning
   - If numerical problem: Solve with steps
   - If diagram: Explain what's shown
   - Be FACTUAL and PRECISE - no creative interpretation
   - Answer based strictly on image content
3. {rigor_instruction}
4. Use proper mathematical/scientific notation
5. Include definitions, theorems, and principles
6. Show complete derivations with verification
7. Be precise, accurate, and logically structured
8. NO metaphors or casual language - only formal reasoning
9. Adapt depth to student's mastery level ({depth_level})

Structure your response:
- **Definition**: Core concept definition
- **Step-by-Step Solution**:
  - Step 1: [First logical step]
  - Step 2: [Next step with reasoning]
  - ... (continue based on mastery level)
- **Verification**: Check the answer
- **Key Formula**: [If applicable]

Keep it exam-focused and appropriately rigorous for {depth_level} level (200-300 words).

Professor's Explanation:"""
    
    async def _generate_professor_response(self, prompt: str) -> str:
        """Call LLM to generate professor response"""
        try:
            # Use LlmChat with proper chaining (same as AIService)
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import uuid
            
            # Initialize with system message for professor context
            professor_system = "You are a rigorous AI Professor teaching for competitive exams like JEE, NEET. Provide formal, step-by-step explanations with proper mathematical/scientific notation. Use structure: Definition → Step-by-Step Solution → Verification. Keep responses precise and exam-focused (200-300 words)."
            
            llm_client = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{str(uuid.uuid4())[:8]}",
                system_message=professor_system
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.3,  # Lower for precision
                top_p=0.9,
                max_tokens=600
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
            return """**Definition**: [Core concept]

**Step-by-Step Solution**:
- Step 1: Identify the given information
- Step 2: Apply relevant formula or theorem
- Step 3: Perform calculations systematically
- Step 4: Arrive at the solution

**Verification**: Substitute answer back to verify correctness.

Please note: I'm having technical difficulties generating the full solution. Please try again."""

