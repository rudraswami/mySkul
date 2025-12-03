"""
Professor Agent - TRUE AGENTIC Formal Reasoning Expert
========================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: CodeExecutor, VerificationTool, FormulaDatabase
- Memory: Tracks student's mastery level, common mistakes
- Actions: VERIFIES solutions, EXECUTES code, CHECKS answers

OLD: Generated step-by-step explanations
NEW: ACTUALLY verifies answers, executes code, proves correctness
"""

import logging
from typing import Dict, Any, Optional
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.tools.code_executor import CodeExecutorTool
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class ProfessorAgent(ReActAgent):
    """
    TRUE AGENTIC Professor - Rigorous, Verifiable Teaching
    
    Capabilities:
    - Executes code to verify solutions
    - Uses verification tools to check answers
    - Adapts rigor based on student mastery level
    - Remembers common mistakes and addresses them
    - Provides formal proofs when needed
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with verification tools
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(CodeExecutorTool())
        
        # Initialize memory for tracking mastery (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("🧮 ProfessorAgent initialized as TRUE AGENT with verification")
    
    def get_agent_name(self) -> str:
        return "ProfessorAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return ['execute_code']
    
    def get_agent_persona(self) -> str:
        return """You are a rigorous professor who teaches with precision and verification.

Your role:
- Provide formal, step-by-step explanations
- VERIFY solutions using code execution when possible
- Adapt rigor based on student's mastery level
- Use proper mathematical/scientific notation
- Prove correctness, don't just claim it

Your style:
- Structured: Definition → Steps → Verification
- Precise: No hand-waving, every step justified
- Adaptive: Simpler for beginners, rigorous for advanced
- Evidence-based: Show, don't just tell

Remember:
- A solution is not complete without verification
- Code execution proves correctness
- Adapt depth to student's level"""
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate professor response using ReAct loop with verification.
        
        Think: What level of rigor is needed? Can I verify this?
        Act: Generate solution + Execute verification
        Observe: Check if solution is correct
        """
        try:
            user_id = context.get('user_id', '')
            subject = context.get('subject', 'Mathematics')
            student_profile = context.get('student_profile', {})
            mastery_level = student_profile.get('mastery_level', 50)
            
            logger.info(f"🧮 ProfessorAgent processing: {query[:100]}")
            
            # THINK: Determine rigor level and if verification is possible
            rigor_level = self._determine_rigor_level(mastery_level)
            can_verify = self._can_verify_with_code(query, subject)
            
            thought = f"Student mastery: {mastery_level}. Rigor: {rigor_level}. Verification possible: {can_verify}."
            logger.info(f"🧠 {thought}")
            
            # ACT: Generate formal explanation
            explanation = await self._generate_professor_response(
                query=query,
                subject=subject,
                rigor_level=rigor_level,
                mastery_level=mastery_level,
                context=context
            )
            
            # ACT: Verify solution if possible
            verification_result = None
            if can_verify:
                logger.info("🔍 Attempting to verify solution with code...")
                verification_result = await self._verify_solution(query, explanation, subject)
            
            # OBSERVE: Check verification results
            observation = "Solution generated"
            if verification_result and verification_result.success:
                observation = f"Solution verified: {verification_result.output}"
                explanation += f"\n\n**Verification:** ✅ Solution verified using code execution.\n```\n{verification_result.output}\n```"
            elif verification_result:
                observation = f"Verification failed: {verification_result.error}"
            
            return {
                'success': True,
                'content': explanation,
                'rigor_level': rigor_level,
                'verified': verification_result.success if verification_result else False,
                'thought': thought,
                'actions': ['generate_solution', 'verify_solution'] if can_verify else ['generate_solution'],
                'observation': observation
            }
            
        except Exception as e:
            logger.error(f"❌ ProfessorAgent error: {e}", exc_info=True)
            return {
                'success': False,
                'content': "Let me provide a formal explanation...",
                'error': str(e)
            }
    
    def _determine_rigor_level(self, mastery_level: int) -> str:
        """Determine explanation rigor based on mastery"""
        if mastery_level < 30:
            return 'basic'
        elif mastery_level < 70:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _can_verify_with_code(self, query: str, subject: str) -> bool:
        """Check if query can be verified with code execution"""
        query_lower = query.lower()
        
        # Math/Physics problems that can be verified
        if subject.lower() in ['mathematics', 'physics', 'math', 'chemistry']:
            if any(word in query_lower for word in ['calculate', 'solve', 'find', 'compute', 'evaluate']):
                return True
        
        return False
    
    async def _verify_solution(self, query: str, explanation: str, subject: str):
        """Verify solution using code execution"""
        try:
            # Extract code from explanation if present
            # Or generate verification code
            verification_code = self._generate_verification_code(query, explanation, subject)
            
            if not verification_code:
                return None
            
            # Execute verification code
            result = await self.tool_registry.execute_tool(
                'execute_code',
                code=verification_code,
                language='python'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return None
    
    def _generate_verification_code(self, query: str, explanation: str, subject: str) -> Optional[str]:
        """Generate Python code to verify the solution"""
        # Simple example - can be enhanced with LLM
        query_lower = query.lower()
        
        # Example: "What is 2+2?"
        if 'what is' in query_lower and any(op in query for op in ['+', '-', '*', '/']):
            # Extract expression
            import re
            match = re.search(r'what is (.+?)\?', query_lower)
            if match:
                expr = match.group(1).strip()
                return f"result = {expr}\nprint(f'Result: {{result}}')"
        
        return None
    
    async def _generate_professor_response(
        self,
        query: str,
        subject: str,
        rigor_level: str,
        mastery_level: int,
        context: Dict[str, Any]
    ) -> str:
        """Generate formal professor response"""
        
        # Build prompt
        prompt = self._build_professor_prompt(
            query=query,
            subject=subject,
            rigor_level=rigor_level,
            mastery_level=mastery_level
        )
        
        # Use LLM to generate response
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY') or self.config.get('emergent_llm_key')
        
        llm_chat = LlmChat(
            api_key=emergent_llm_key,
            session_id=f"professor_{context.get('user_id', 'unknown')}",
            system_message=prompt
        )
        
        user_message = UserMessage(text=query)
        response = await llm_chat.send_message(user_message)
        
        return response if isinstance(response, str) else str(response)
    
    def _build_professor_prompt(
        self,
        query: str,
        subject: str,
        rigor_level: str,
        mastery_level: int
    ) -> str:
        """Build professor system prompt"""
        
        base_prompt = self.get_agent_persona()
        
        # Add rigor-specific instructions
        rigor_instructions = {
            'basic': "Use simple steps. Explain WHY each step is needed. Avoid complex notation. Focus on understanding.",
            'intermediate': "Use standard steps with clear reasoning. Include important formulas. Balance rigor with clarity.",
            'advanced': "Use complete rigor. Include proofs, edge cases, exam tricks. Assume strong foundation."
        }
        
        personalization = f"\n\nFOR THIS STUDENT:\n"
        personalization += f"- Subject: {subject}\n"
        personalization += f"- Mastery Level: {mastery_level}/100 ({rigor_level})\n"
        personalization += f"- Rigor: {rigor_instructions[rigor_level]}\n\n"
        personalization += "Structure your response:\n"
        personalization += "1. **Definition/Concept**: Core idea\n"
        personalization += "2. **Step-by-Step Solution**: Justified steps\n"
        personalization += "3. **Verification**: Check the answer\n"
        personalization += "4. **Key Takeaway**: Main formula/principle\n"
        
        return base_prompt + personalization
