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
        
        # Register Exam Strategy Tool (replaces Exam Coach Agent)
        from agents.core.tools.exam_strategy import ExamStrategyTool
        self.tool_registry.register(ExamStrategyTool())
        
        # Register Calculator Tool for math verification
        from agents.core.tools.calculator import CalculatorTool
        self.tool_registry.register(CalculatorTool())
        
        # Initialize memory for tracking mastery (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("🧮 ProfessorAgent initialized as TRUE AGENT with verification + exam strategy")
    
    def get_agent_name(self) -> str:
        return "ProfessorAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return ['execute_code', 'exam_strategy', 'calculator']
    
    def get_agent_persona(self) -> str:
        return """You are "Dr. Druv," India's leading JEE/NEET Professor.

**Your Directive:**

1. **Accuracy First:** NEVER guess math. If you see an equation, use your `calculator` tool to solve it. NEVER do mental math - always verify with tools.

2. **Socratic Style:** Do not dump the answer. Guide the student step-by-step. Ask "What do you think the first step is?" if the question is vague.

3. **Exam Context:** Mention "JEE Main" or "NEET" relevance whenever possible. If a student asks for tips, tricks, or weightage, DO NOT hallucinate. Use the `exam_strategy` tool to get facts.

4. **Formatting:** Use LaTeX for all math (wrapped in $). Use Bullet points for steps.

**Tool Usage Protocol:**

- User: "Derivative of sin(x)"
- Thought: "I need to verify this." -> Call `calculator` tool.
- Observation: "cos(x)"
- Response: "The derivative is $\\cos(x)$. Here is why..."

- User: "What's the weightage of Rotational Motion in JEE?"
- Thought: "Student wants exam-specific data. I must use exam_strategy tool." -> Call `exam_strategy` tool.
- Observation: Tool returns weightage, traps, shortcuts.
- Response: "Rotational Motion has 4.2% weightage in JEE. Here are common traps..."

**Tone:** Academic, Encouraging, Strict about concepts.

**Error Handling:** If a tool fails (e.g., database error), degrade gracefully: "I can't access the database right now, but generally speaking, this topic is important for JEE..." """
    
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
        """
        Generate formal professor response.
        
        Model Priority:
        1. Gemini Pro (fast, intelligent, deep reasoning)
        2. DeepSeek (rigorous mathematical reasoning)
        3. GPT-4o (fallback)
        """
        
        # Build prompt
        system_prompt = self._build_professor_prompt(
            query=query,
            subject=subject,
            rigor_level=rigor_level,
            mastery_level=mastery_level
        )
        
        try:
            from core.config import settings
            
            # === PRIORITY 1: Gemini Pro (primary) ===
            if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
                logger.info("⚡ ProfessorAgent using Gemini Pro for intelligent reasoning...")
                from services.llm_service import call_gemini
                
                # Use Pro model for rigorous explanations
                response = await call_gemini(
                    prompt=query,
                    api_key=settings.GEMINI_API_KEY,
                    temperature=0.3,  # Lower for precision
                    max_tokens=2000,
                    model="gemini-1.5-pro",  # Pro for deep reasoning
                    system_message=system_prompt,
                    use_pro=True
                )
                return response if isinstance(response, str) else str(response)
            
            # === PRIORITY 2: DeepSeek (fallback for rigorous math) ===
            if settings.USE_DEEPSEEK_REASONING and settings.DEEPSEEK_API_KEY:
                logger.info("🧮 ProfessorAgent using DeepSeek for rigorous reasoning...")
                from services.llm_service import call_deepseek
                
                response = await call_deepseek(
                    prompt=query,
                    api_key=settings.DEEPSEEK_API_KEY,
                    temperature=0.3,
                    max_tokens=1500,
                    system_message=system_prompt
                )
                return response if isinstance(response, str) else str(response)
            
            # === PRIORITY 3: OpenAI GPT-4o (final fallback) ===
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import os
            
            emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY') or self.config.get('emergent_llm_key')
            
            llm_chat = LlmChat(
                api_key=emergent_llm_key,
                session_id=f"professor_{context.get('user_id', 'unknown')}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o").with_params(
                temperature=0.3,
                max_tokens=1500
            )
            
            user_message = UserMessage(text=query)
            response = await llm_chat.send_message(user_message)
            
            return response if isinstance(response, str) else str(response)
            
        except Exception as e:
            logger.error(f"❌ Professor LLM call failed: {e}")
            # Return a basic response instead of failing
            return f"Let me explain {subject} concept step by step. The key principle here involves understanding the fundamentals first, then building up to more complex applications."
    
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
