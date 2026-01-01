"""
🧠 Agentic Doubt Resolver - True Human-like Agent
==================================================

This is a TRUE agentic system that:
1. THINKS step-by-step (ReAct loop)
2. USES TOOLS to gather information
3. REMEMBERS context and student patterns
4. PLANS complex explanations
5. VERIFIES its own answers

This is NOT just an LLM wrapper - it's a reasoning system
that behaves like a human tutor.

Example flow:
1. Student asks: "I don't understand why momentum is conserved"
2. Agent THINKS: "This is a conceptual physics doubt about conservation laws"
3. Agent ACTS: Uses knowledge_search to look up momentum conservation
4. Agent OBSERVES: Found Newton's laws and isolated systems
5. Agent THINKS: "I should use an analogy they can relate to"
6. Agent ACTS: Checks student memory for preferred examples (cricket!)
7. Agent OBSERVES: Student responds well to cricket analogies
8. Agent THINKS: "Let me construct an explanation with cricket example"
9. Agent VERIFIES: Checks the physics is accurate
10. Agent RESPONDS: Clear explanation with cricket analogy
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.react_agent import ReActAgent, AgentState, ThoughtAction
from agents.core.tool_registry import ToolRegistry, create_tool_registry
from agents.core.memory import MemorySystem
from agents.core.planner import Planner, TaskPlan
from agents.core.verifier import Verifier

logger = logging.getLogger(__name__)


class AgenticDoubtResolver(ReActAgent):
    """
    A truly agentic doubt resolver that thinks, acts, and observes
    like a human tutor would.
    
    Features:
    - ReAct reasoning loop
    - Tool usage (calculator, knowledge search, etc.)
    - Memory (remembers student patterns)
    - Planning (breaks complex doubts into steps)
    - Self-verification (checks its own answers)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize components
        self.tool_registry = create_tool_registry(include_default=True)
        self.planner = Planner()
        self.verifier = Verifier()
        self._memory_cache: Dict[str, MemorySystem] = {}
        
        logger.info("🧠 AgenticDoubtResolver initialized with full agentic capabilities")
    
    def get_agent_name(self) -> str:
        return "AgenticDoubtResolver"
    
    def get_agent_persona(self) -> str:
        return """You are an empathetic, highly intelligent tutor who specializes in resolving student doubts.

YOUR CHARACTER:
- You genuinely care about student understanding, not just answering questions
- You've helped thousands of students - you've seen every type of confusion
- You're patient, encouraging, but also rigorous about accuracy
- You use tools to verify information rather than guessing
- You remember student patterns and adapt your explanations

YOUR APPROACH:
1. UNDERSTAND: First, truly understand what's confusing the student
2. RESEARCH: Use tools to get accurate information
3. RELATE: Find analogies that connect to student's life
4. EXPLAIN: Build understanding step by step
5. VERIFY: Double-check your explanation is accurate
6. CHECK: Ask if the student understood

THINKING STYLE:
- Always reason step-by-step
- Use tools when you need facts or calculations
- Don't guess - verify
- Consider the student's perspective
- Admit when you're uncertain

NEVER:
- Give wrong information (always verify)
- Make students feel stupid
- Rush through explanations
- Use jargon without explaining it"""
    
    def get_available_tools(self) -> List[str]:
        return [
            "calculator",
            "knowledge_search",
            "formula_lookup",
            "fact_checker",
            "code_executor"
        ]
    
    @staticmethod
    def is_doubt_query(
        query: str, 
        semantic_analysis: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Detect if this is a doubt/confusion query needing empathetic agentic handling.
        
        PHASE 1 FIX: This method now defers to semantic analysis when available.
        Keyword patterns only run as fallback when:
        1. No semantic analysis available
        2. Semantic confidence is low (< 0.5)
        
        The semantic classifier already detects confusion, clarification,
        and emotional states - we should use that intelligence.
        """
        # ================================================================
        # PHASE 1: SEMANTIC ANALYSIS IS AUTHORITATIVE
        # ================================================================
        if semantic_analysis:
            confidence = semantic_analysis.get('confidence', 0)
            if confidence >= 0.5:
                intent = semantic_analysis.get('intent', '')
                emotional_tone = semantic_analysis.get('emotional_tone', '')
                
                # Semantic signals that indicate doubt
                doubt_intents = ['clarification', 'confusion', 'emotional_support']
                doubt_tones = ['confused', 'frustrated', 'anxious']
                
                if intent in doubt_intents:
                    logger.info(f"🧠 SEMANTIC DOUBT detected (intent={intent})")
                    return True
                
                if emotional_tone in doubt_tones and semantic_analysis.get('emotional_intensity', 0) > 0.4:
                    logger.info(f"🧠 SEMANTIC DOUBT detected (tone={emotional_tone}, intense)")
                    return True
                
                # Semantic says not a doubt - trust it
                return False
        
        # ================================================================
        # LEGACY FALLBACK: Keyword patterns (only when semantic unavailable)
        # ================================================================
        logger.debug("📋 Using legacy keyword doubt detection (semantic unavailable)")
        
        query_lower = query.lower().strip()
        
        # STRUCTURAL detection only (not keyword lists)
        # 1. Very short follow-up questions often indicate confusion
        word_count = len(query_lower.split())
        has_question = '?' in query_lower
        
        if word_count <= 3 and has_question:
            # "Why?", "How?", "What?" - might be confusion
            # Let routing decide, not us
            return False
        
        # 2. Messages with multiple question marks = frustration/confusion
        question_mark_count = query_lower.count('?')
        if question_mark_count >= 2:
            logger.info(f"🤔 STRUCTURAL: Multiple questions detected")
            return True
        
        # 3. Explicit confusion signals (minimal keyword set - structural)
        # These are so explicit they're essentially structural
        explicit_confusion = [
            "don't understand", "can't understand", "i'm confused",
            "makes no sense", "help me understand", "explain again"
        ]
        
        if any(phrase in query_lower for phrase in explicit_confusion):
            logger.info(f"🤔 EXPLICIT DOUBT detected (structural): '{query[:50]}...'")
            return True
        
        # Default: Not detected - let semantic handle in main flow
        return False
    
    @staticmethod
    def is_deep_reasoning_query(
        query: str,
        semantic_analysis: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Detect if query needs deep multi-step reasoning with tools.
        
        PHASE 1 FIX: Uses structural indicators, not keywords.
        Deep reasoning is detected by:
        1. Mathematical notation (equations, formulas)
        2. Multi-step structure (numbered items, "and then")
        3. Semantic analysis signals (response_expectation, complexity)
        
        NOT by keyword matching on "solve", "prove", etc.
        """
        # ================================================================
        # PHASE 1: SEMANTIC ANALYSIS IS AUTHORITATIVE
        # ================================================================
        if semantic_analysis and semantic_analysis.get('confidence', 0) >= 0.5:
            response_expectation = semantic_analysis.get('response_expectation', '')
            
            # Semantic signals that indicate deep reasoning
            if response_expectation == 'structured_deliverable':
                output_type = semantic_analysis.get('requested_output_type', '')
                if output_type == 'problem_solution':
                    logger.info(f"🧠 SEMANTIC: Deep reasoning (structured problem solution)")
                    return True
            
            # Not detected by semantic - trust it
            return False
        
        # ================================================================
        # LEGACY FALLBACK: STRUCTURAL detection (no keywords)
        # ================================================================
        import re
        
        # 1. Mathematical content (structural - detects symbols)
        math_patterns = [
            r'\d+\s*[+\-*/^=]\s*\d+',  # Equations
            r'd[xy]/d[xy]',  # Derivatives
            r'∫|∑|∏',  # Math symbols
            r'\\frac|\\sqrt|\\int',  # LaTeX
            r'=\s*\?',  # Find X format
        ]
        
        has_math = any(re.search(p, query) for p in math_patterns)
        
        # 2. Multi-step structure (numbered items, steps)
        has_numbered = bool(re.search(r'(?:1\.|step 1|first,?)', query.lower()))
        has_multiple_parts = bool(re.search(r'(?:and then|after that|next,?|finally)', query.lower()))
        
        # 3. Verification request (structural - question about correctness)
        query_lower = query.lower()
        is_verification = '?' in query and any(w in query_lower for w in ['correct', 'right', 'wrong', 'check'])
        
        if has_math and (has_numbered or has_multiple_parts or len(query.split()) > 25):
            logger.info(f"🧠 STRUCTURAL: Deep reasoning (math + complexity)")
            return True
        
        if is_verification and has_math:
            logger.info(f"🧠 STRUCTURAL: Deep reasoning (verification of math)")
            return True
        
        return False
    
    def get_system_prompt(self, state: AgentState) -> str:
        """Enhanced system prompt with memory and planning context"""
        base_prompt = super().get_system_prompt(state)
        
        # Add memory context if available
        memory_context = ""
        student_id = state.context.get('user_id')
        if student_id and student_id in self._memory_cache:
            memory = self._memory_cache[student_id]
            memory_context = f"""
## STUDENT MEMORY
{memory.get_context_for_prompt()}
"""
        
        # Add planning context if complex query
        planning_context = ""
        if hasattr(state, 'plan') and state.plan:
            planning_context = f"""
## EXECUTION PLAN
{self.planner.get_plan_description(state.plan)}
"""
        
        return base_prompt + memory_context + planning_context
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Alias for run() to match standard agent interface.
        Supervisor expects process(), ReActAgent provides run().
        """
        return await self.run(query, context)
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced run with memory, planning, and verification.
        """
        logger.info(f"🧠 AgenticDoubtResolver processing: {query[:50]}...")
        
        # Initialize or get memory for this student (with REAL database persistence)
        student_id = context.get('user_id', 'anonymous')
        db = context.get('db')  # Get database from context for persistent memory
        
        if student_id not in self._memory_cache:
            self._memory_cache[student_id] = MemorySystem(student_id, db=db)
            await self._memory_cache[student_id].initialize(db=db)
        elif db and not self._memory_cache[student_id]._db:
            # If db is now available but wasn't before, update the memory system
            self._memory_cache[student_id].set_db(db)
        
        memory = self._memory_cache[student_id]
        
        # Remember this interaction
        memory.remember(f"Student asked: {query}", "question")
        
        # Create execution plan for complex queries
        plan = self.planner.create_plan(query, context)
        
        # Initialize state with plan
        state = AgentState(
            query=query,
            context=context,
            max_iterations=self.max_iterations
        )
        state.plan = plan  # Attach plan to state
        
        try:
            # Run the ReAct loop
            while state.iterations < state.max_iterations:
                state.iterations += 1
                
                # THINK
                thought_action = await self._think(state)
                
                if not thought_action:
                    break
                
                # Check for FINISH
                if thought_action.action == "FINISH":
                    state.final_answer = thought_action.action_input.get("answer", "")
                    state.confidence = thought_action.action_input.get("confidence", 0.8)
                    break
                
                # ACT
                observation = await self._act(thought_action, state)
                thought_action.observation = observation
                
                # Update plan progress
                if plan and not plan.is_complete():
                    next_task = plan.get_next_task()
                    if next_task:
                        plan.mark_complete(next_task.id, observation)
                
                logger.info(f"  Step {state.iterations}: {thought_action.action} → {observation[:80]}...")
            
            # VERIFY the response
            if state.final_answer:
                verification = await self.verifier.verify_response(
                    state.final_answer,
                    context
                )
                
                if verification.corrections:
                    logger.warning(f"⚠️ Verification found issues: {verification.corrections}")
                    # Could trigger re-reasoning here
                
                state.verification = verification
            
            # Generate fallback if needed
            if not state.final_answer:
                state.final_answer = await self._generate_empathetic_fallback(state)
                state.confidence = 0.6
            
            # Update memory with outcome
            memory.remember(f"Explained: {state.final_answer[:100]}...", "response")
            
            # Save memory
            await memory.save()
            
            return self._format_response(state)
            
        except Exception as e:
            logger.error(f"❌ AgenticDoubtResolver error: {e}", exc_info=True)
            return self._format_error_response(state)
    
    async def _generate_empathetic_fallback(self, state: AgentState) -> str:
        """Generate an empathetic fallback response"""
        # Summarize what we learned from reasoning
        insights = []
        for ta in state.reasoning_chain:
            if ta.observation and len(ta.observation) > 10:
                insights.append(ta.observation)
        
        if insights:
            return f"""Let me help you understand this.

Based on what I found:
{chr(10).join(['- ' + i[:150] for i in insights[:3]])}

Would you like me to:
1. **Explain with a simple analogy** - Connect it to something familiar
2. **Show step-by-step** - Break it down into smaller pieces  
3. **Give an example** - See how it works in practice

What would help you most?"""
        
        return """I want to make sure I fully understand your doubt before explaining. 🤔

Could you tell me a bit more about:
- What specific part is confusing?
- Have you seen this concept before?
- Would you prefer a simple analogy or step-by-step explanation?

I'm here to help you truly understand, not just give you an answer! 💪"""
    
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """Format response with full reasoning chain and verification"""
        base_response = super()._format_response(state)
        
        # Add verification info
        if hasattr(state, 'verification'):
            base_response['verification'] = state.verification.to_dict()
        
        # Add plan info
        if hasattr(state, 'plan') and state.plan:
            base_response['execution_plan'] = state.plan.to_dict()
        
        return base_response


# ============================================
# Factory function for easy instantiation
# ============================================

def create_agentic_doubt_resolver(config: Dict[str, Any] = None) -> AgenticDoubtResolver:
    """
    Create a fully configured AgenticDoubtResolver.
    
    Usage:
        agent = create_agentic_doubt_resolver()
        response = await agent.run(
            query="I don't understand conservation of momentum",
            context={"subject": "Physics", "user_id": "student123"}
        )
    """
    return AgenticDoubtResolver(config)


# ============================================
# Compatibility layer for existing code
# ============================================

async def resolve_doubt_agentically(
    query: str,
    context: Dict[str, Any],
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Resolve a doubt using the agentic system.
    
    Drop-in replacement for existing doubt resolution.
    """
    agent = create_agentic_doubt_resolver(config)
    return await agent.run(query, context)

