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
    def is_doubt_query(query: str) -> bool:
        """
        Detect if this is a doubt/confusion query needing empathetic agentic handling.
        
        PHILOSOPHY: Capture student confusion more generously.
        Students often express confusion in subtle ways. A real teacher would
        pick up on these signals. We should too.
        
        The AgenticDoubtResolver provides:
        - Empathetic, patient explanations
        - Step-by-step reasoning with tools
        - Memory of what confused the student before
        - Verification to ensure accuracy
        """
        query_lower = query.lower().strip()
        
        # ==========================================================================
        # TIER 1: EXPLICIT CONFUSION (High confidence - definitely a doubt)
        # ==========================================================================
        explicit_confusion = [
            # Direct confusion statements
            "don't understand", "dont understand", "do not understand",
            "not understanding", "can't understand", "cannot understand",
            "confused about", "i'm confused", "i am confused", "so confused",
            "still confused", "very confused", "really confused",
            "makes no sense", "doesn't make sense", "does not make sense",
            
            # Stuck/blocked expressions
            "i'm stuck", "i am stuck", "getting stuck", "got stuck",
            "can't figure", "cannot figure", "struggling with",
            
            # Frustration indicators
            "still don't get", "still dont get", "not getting it",
            "don't get it", "dont get it", "what am i missing",
            "where am i going wrong", "help me understand",
            
            # Request for re-explanation
            "explain again", "explain it again", "one more time",
            "clarify this", "need clarification",
            
            # Hindi/Hinglish confusion expressions
            "samajh nahi aa raha", "samajh nahi aaya", "समझ नहीं आ रहा",
            "samajh me nahi", "clear nahi hai", "confuse ho gaya",
        ]
        
        if any(phrase in query_lower for phrase in explicit_confusion):
            logger.info(f"🤔 TRUE DOUBT detected (explicit confusion): '{query[:50]}...'")
            return True
        
        # ==========================================================================
        # TIER 2: SUBTLE CONFUSION (Nuanced signals that real teachers catch)
        # ==========================================================================
        subtle_confusion = [
            # Questioning understanding
            "but why", "but how", "but what",  # "But" often signals lingering doubt
            "wait, so", "wait so", "so basically",  # Re-processing signals
            "i thought", "i think i",  # Uncertainty hedging
            
            # Requesting different angles
            "can you explain", "could you explain",  # Polite re-request
            "what does it mean", "what do you mean",
            "in simple terms", "in simple words", "simply explain",
            "eli5", "explain like i'm 5", "dumb it down",
            
            # Partial understanding signals
            "i get that but", "i understand but", "okay but",
            "that part is clear but", "this part confuses",
            "lost after", "lost at", "lost me at",
            
            # Seeking confirmation (often means doubt)
            "am i right", "is that right", "is this right",
            "did i get", "have i got",
            
            # Asking "why" in specific ways (conceptual doubt)
            "why exactly", "why specifically", "why does this happen",
            "how come", "how is that possible",
            
            # Common student doubt phrases
            "not sure", "not clear", "a bit confused",
            "little confused", "kind of confused",
            "having trouble", "having difficulty", "trouble understanding",
            
            # Help requests
            "please help", "can you help", "need help with",
            "help with this", "help me with",
        ]
        
        if any(phrase in query_lower for phrase in subtle_confusion):
            logger.info(f"🤔 SUBTLE DOUBT detected: '{query[:50]}...'")
            return True
        
        # ==========================================================================
        # TIER 3: FOLLOW-UP PATTERNS (Often indicate previous doubt)
        # ==========================================================================
        # Short follow-ups after explanations often mean the student didn't fully get it
        short_followups = ["why?", "how?", "why is that?", "how so?", "really?", "huh?"]
        if query_lower.strip('?!. ') in [f.strip('?!. ') for f in short_followups]:
            logger.info(f"🤔 SHORT FOLLOW-UP detected (likely confusion): '{query}'")
            return True
        
        # ==========================================================================
        # DEFAULT: Not a doubt - route to standard explanation flow
        # ==========================================================================
        return False
    
    @staticmethod
    def is_deep_reasoning_query(query: str) -> bool:
        """
        Detect if query needs deep multi-step reasoning with tools.
        
        This is for complex problems that benefit from:
        - Tool usage (calculator, knowledge search)
        - Step-by-step verification
        - ReAct loop reasoning
        
        NOT for simple conceptual questions.
        """
        query_lower = query.lower().strip()
        
        deep_reasoning_triggers = [
            # Multi-step problem solving
            "solve this step by step", "show all steps", "step by step solution",
            "derive and prove", "prove that", "prove this",
            "calculate and explain", "solve and verify",
            
            # Verification requests
            "verify my solution", "check my answer", "is this correct",
            "check if this is right", "verify this calculation",
            
            # Complex analysis
            "analyze in detail", "comprehensive analysis",
            "find all the formulas", "list all methods",
        ]
        
        if any(trigger in query_lower for trigger in deep_reasoning_triggers):
            logger.info(f"🧠 DEEP REASONING query detected: '{query[:50]}...'")
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
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced run with memory, planning, and verification.
        """
        logger.info(f"🧠 AgenticDoubtResolver processing: {query[:50]}...")
        
        # Initialize or get memory for this student
        student_id = context.get('user_id', 'anonymous')
        if student_id not in self._memory_cache:
            self._memory_cache[student_id] = MemorySystem(student_id)
            await self._memory_cache[student_id].initialize()
        
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
            return f"""That's a great question! Let me help you understand this. 🤔

Based on what I found:
{chr(10).join(['- ' + i[:150] for i in insights[:3]])}

Would you like me to:
1. **Explain with a simple analogy** - Connect it to something familiar
2. **Show step-by-step** - Break it down into smaller pieces  
3. **Give an example** - See how it works in practice

What would help you most? 💪"""
        
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

