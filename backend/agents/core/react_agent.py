"""
🧠 ReAct Agent - Reasoning + Acting Architecture
=================================================

Implementation of the ReAct (Reasoning and Acting) paradigm where agents:
1. THINK - Reason about the current situation
2. ACT - Choose and execute a tool/action
3. OBSERVE - Process the result
4. REPEAT - Until task is complete

This creates truly intelligent agents that behave like humans:
- They plan before acting
- They use tools appropriately
- They reflect on outcomes
- They self-correct mistakes

Paper Reference: "ReAct: Synergizing Reasoning and Acting in Language Models"
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Current status of the agent"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ThoughtAction:
    """Represents a single thought-action pair in the reasoning chain"""
    step: int
    thought: str  # What the agent is thinking
    action: Optional[str] = None  # Tool/action to take
    action_input: Optional[Dict[str, Any]] = None  # Input for the action
    observation: Optional[str] = None  # Result of the action
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AgentState:
    """Complete state of an agent during execution"""
    query: str
    context: Dict[str, Any]
    status: AgentStatus = AgentStatus.IDLE
    reasoning_chain: List[ThoughtAction] = field(default_factory=list)
    final_answer: Optional[str] = None
    confidence: float = 0.0
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    tools_used: List[str] = field(default_factory=list)
    iterations: int = 0
    max_iterations: int = 10
    
    def add_thought(self, thought: str) -> ThoughtAction:
        """Add a new thought to the reasoning chain"""
        ta = ThoughtAction(
            step=len(self.reasoning_chain) + 1,
            thought=thought
        )
        self.reasoning_chain.append(ta)
        return ta
    
    def get_reasoning_summary(self) -> str:
        """Get a summary of the reasoning chain for prompts"""
        if not self.reasoning_chain:
            return "No reasoning yet."
        
        summary = []
        for ta in self.reasoning_chain:
            summary.append(f"Step {ta.step}:")
            summary.append(f"  Thought: {ta.thought}")
            if ta.action:
                summary.append(f"  Action: {ta.action}")
                if ta.action_input:
                    summary.append(f"  Input: {json.dumps(ta.action_input)}")
            if ta.observation:
                summary.append(f"  Observation: {ta.observation[:200]}...")
        
        return "\n".join(summary)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status.value,
            "reasoning_chain": [ta.to_dict() for ta in self.reasoning_chain],
            "final_answer": self.final_answer,
            "confidence": self.confidence,
            "error": self.error,
            "iterations": self.iterations,
            "tools_used": self.tools_used,
            "duration_ms": (
                (self.end_time - self.start_time).total_seconds() * 1000
                if self.end_time else None
            )
        }


class ReActAgent(ABC):
    """
    Base class for ReAct-style agents that can reason, act, and observe.
    
    Subclasses must implement:
    - get_agent_name(): Return agent identifier
    - get_agent_persona(): Return the agent's character/personality
    - get_available_tools(): Return list of tools this agent can use
    - should_finish(): Determine if the agent should stop
    
    The ReAct loop:
    1. THINK: Generate a thought about what to do next
    2. ACT: Choose a tool and execute it
    3. OBSERVE: Process the tool's output
    4. REPEAT or FINISH
    
    TIMEOUT PROTECTION:
    - Global timeout (default 25s) prevents infinite loops
    - On timeout, gracefully falls back to simple response
    - Never leaves student waiting indefinitely
    """
    
    # Default timeout in seconds for the entire ReAct loop
    # FIX v1.0: Aligned with frontend timeout (30s) - backend MUST be under frontend
    # This prevents race condition where frontend times out before backend responds
    DEFAULT_GLOBAL_TIMEOUT = 25.0  # MUST be < frontend's 30s timeout
    
    # Adaptive iteration limits based on complexity
    # FIX v1.0: Reduced limits for faster response times
    ITERATION_LIMITS = {
        'trivial': 2,   # Was 3 - simple follow-ups need instant response
        'simple': 3,    # Was 5 - most queries should complete in 3 iterations
        'moderate': 5,  # Was 8 - explanations need some reasoning
        'complex': 7,   # Was 12 - multi-step problems
        'deep': 10,     # Was 15 - proofs/derivations (rare)
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.llm_key = self.config.get('emergent_llm_key') or os.environ.get('OPENAI_API_KEY')
        self.tool_registry = None  # Set by subclass or injected
        self.memory = None  # Set by subclass or injected
        self.base_max_iterations = self.config.get('max_iterations', 10)
        self.max_iterations = self.base_max_iterations  # Will be adjusted dynamically
        self.verbose = self.config.get('verbose', True)
        
        # Global timeout for entire ReAct loop (configurable)
        self.global_timeout = self.config.get('global_timeout', self.DEFAULT_GLOBAL_TIMEOUT)
        
        # Feature flag for self-assessment (safe default: ON)
        # Respects both config and global settings
        try:
            from core.config import settings
            global_flag = getattr(settings, 'ENABLE_AGENT_SELF_ASSESSMENT', True)
        except ImportError:
            global_flag = True
        self.enable_self_assessment = self.config.get('enable_self_assessment', global_flag)
        
        logger.info(f"🤖 {self.get_agent_name()} initialized (ReAct mode, timeout={self.global_timeout}s)")
    
    def _resolve_model(self, model_from_context: Optional[str] = None) -> str:
        """
        Resolve the LLM model to use, respecting cognitive routing decisions.
        
        Priority:
        1. Model passed from context (upstream routing decision)
        2. settings.DEFAULT_LLM_MODEL (global configuration)
        3. 'gpt-4o-mini' (hardcoded fallback if settings unavailable)
        
        Args:
            model_from_context: Model selected by upstream routing (e.g., orchestrator)
        
        Returns:
            Model identifier string to use for LLM calls
        """
        if model_from_context:
            return model_from_context
        
        try:
            from core.config import settings
            return getattr(settings, 'DEFAULT_LLM_MODEL', 'gpt-4o-mini')
        except ImportError:
            return 'gpt-4o-mini'
    
    def evaluate_confidence(self, query: str, context: Dict[str, Any]) -> float:
        """
        SELF-ASSESSMENT: Agent evaluates its own confidence for handling this query.
        
        This enables TRUE agent autonomy - agents decide their own fitness,
        not external routing logic.
        
        Override in subclasses for specialized confidence assessment.
        
        Args:
            query: The student's question
            context: Request context (subject, exam_mode, etc.)
            
        Returns:
            Confidence score 0.0 to 1.0
        """
        if not self.enable_self_assessment:
            return 0.7  # Default confidence when disabled
        
        # Base confidence from agent type and query match
        base_confidence = 0.5
        
        # Check if agent has relevant tools
        if self.tool_registry:
            available_tools = self.get_available_tools() if hasattr(self, 'get_available_tools') else []
            if available_tools:
                base_confidence += 0.1
        
        # Subject match boost
        subject = context.get('subject', '').lower()
        agent_name = self.get_agent_name().lower()
        
        # Domain expertise mapping (can be overridden by subclasses)
        domain_boost = self._get_domain_confidence_boost(subject, query)
        
        return min(1.0, base_confidence + domain_boost)
    
    def _get_domain_confidence_boost(self, subject: str, query: str) -> float:
        """
        Get confidence boost based on domain expertise.
        Override in subclasses for specialized matching.
        """
        # Default implementation - no boost
        return 0.0
    
    def should_abstain(self, query: str, context: Dict[str, Any]) -> tuple:
        """
        SELF-INITIATED ABSTAIN: Agent decides if it should skip this query.
        
        Checks:
        1. Self-assessed confidence
        2. Cognitive control signals (if available)
        
        Returns:
            Tuple of (should_abstain: bool, reason: str)
        """
        # Check cognitive control signals first
        try:
            from services.cognitive_model.cognitive_control import get_cognitive_signal
            
            signal = get_cognitive_signal(context, self.get_agent_name())
            if signal:
                decision = signal.get('decision')
                if decision == 'should_defer':
                    defer_to = signal.get('defer_to', 'another agent')
                    return (True, f"Cognitive control: deferring to {defer_to}")
                elif decision == 'may_abstain':
                    # May abstain - check confidence to decide
                    pass  # Continue to confidence check
        except ImportError:
            pass  # Cognitive control not available
        except Exception:
            pass  # Any error, proceed with confidence check
        
        confidence = self.evaluate_confidence(query, context)
        
        if confidence < 0.3:
            return (True, f"Low confidence ({confidence:.2f}) - not suited for this query")
        
        return (False, "")
    
    async def _post_insight_to_shared_state(
        self,
        context: Dict[str, Any],
        thought: str,
        confidence: float = 0.7
    ):
        """
        Post an insight to the shared reasoning state if available.
        
        This enables TRUE multi-agent collaboration: agents share their
        intermediate thoughts as they reason, not just final outputs.
        
        ADDITIVE: Only runs if shared state exists, completely non-blocking.
        """
        try:
            from services.cognitive_model.shared_reasoning_state import (
                get_shared_state, InsightType
            )
            
            shared_state = get_shared_state(context)
            if shared_state is None:
                return  # No shared state available, proceed normally
            
            # Determine insight type from thought content
            thought_lower = thought.lower()
            if any(w in thought_lower for w in ['i think', 'hypothesis', 'might be', 'could be']):
                insight_type = InsightType.HYPOTHESIS
            elif any(w in thought_lower for w in ['verified', 'confirmed', 'calculated']):
                insight_type = InsightType.FACT
            elif any(w in thought_lower for w in ['warning', 'careful', 'note that']):
                insight_type = InsightType.WARNING
            elif any(w in thought_lower for w in ['unsure', 'not sure', 'need help']):
                insight_type = InsightType.QUESTION
            else:
                insight_type = InsightType.HYPOTHESIS
            
            # Post the insight (non-blocking)
            await shared_state.post_insight(
                agent_name=self.get_agent_name(),
                insight_type=insight_type,
                content=thought[:500],  # Limit length
                confidence=confidence
            )
            
        except ImportError:
            pass  # Module not available, proceed normally
        except Exception:
            pass  # Any error, proceed normally - this is non-blocking
    
    async def _get_insights_from_shared_state(
        self,
        context: Dict[str, Any],
        min_confidence: float = 0.5
    ) -> str:
        """
        Get relevant insights from other agents for context enrichment.
        
        Returns a formatted string of insights that can be added to prompts.
        """
        try:
            from services.cognitive_model.shared_reasoning_state import get_shared_state
            
            shared_state = get_shared_state(context)
            if shared_state is None:
                return ""
            
            # Get insights from other agents
            insights = await shared_state.get_latest_insights(
                exclude_agent=self.get_agent_name(),
                limit=3
            )
            
            if not insights:
                return ""
            
            # Format insights for prompt
            formatted = "\n[INSIGHTS FROM OTHER AGENTS]\n"
            for insight in insights:
                formatted += f"- {insight.agent_name} ({insight.insight_type.value}): {insight.content[:200]}\n"
            
            return formatted
            
        except ImportError:
            return ""
        except Exception:
            return ""
    
    def _get_adaptive_iterations(self, query: str, context: Dict[str, Any]) -> int:
        """
        Dynamically determine max iterations based on query complexity.
        
        Deep reasoning queries get more iterations.
        Simple queries get fewer to save time.
        
        CRITICAL OPTIMIZATION: Continuation/follow-up questions use TRIVIAL (2-3 iterations)
        to avoid 45s timeouts on simple "explain again" requests.
        """
        import re
        query_lower = query.lower()
        word_count = len(query.split())
        
        # ================================================================
        # TRIVIAL: Simple follow-ups, continuations, clarifications
        # These should be FAST (2-3 iterations max) - no deep reasoning needed
        # ================================================================
        trivial_indicators = [
            # Clarification requests
            "explain in simple", "explain simply", "in simple words",
            "i did not get", "i didn't get", "i dont get", "i don't get",
            "didn't understand", "don't understand", "did not understand",
            "can you explain", "explain again", "say again", "repeat",
            "make it simple", "simpler", "easier", "more clearly",
            # Short confirmations/follow-ups
            "yes", "no", "ok", "okay", "sure", "thanks", "thank you",
            "got it", "understood", "i see", "hmm", "hm",
            # Context references (needs prior context, not new reasoning)
            "what about", "and what", "also", "more about",
        ]
        
        # Check for trivial patterns
        if any(ind in query_lower for ind in trivial_indicators):
            logger.info("📊 Query complexity: TRIVIAL - fast continuation (2 iterations)")
            return self.ITERATION_LIMITS['trivial']
        
        # Very short queries (< 6 words) without complex keywords are trivial
        if word_count < 6 and not any(kw in query_lower for kw in ['prove', 'solve', 'calculate', 'derive']):
            logger.info(f"📊 Query complexity: TRIVIAL - short query ({word_count} words)")
            return self.ITERATION_LIMITS['trivial']
        
        # Check context for continuation signal
        if context.get('is_continuation') or context.get('awaiting_continuation'):
            logger.info("📊 Query complexity: TRIVIAL - continuation context detected")
            return self.ITERATION_LIMITS['trivial']
        
        # ================================================================
        # DEEP complexity indicators
        # ================================================================
        deep_indicators = [
            'prove', 'proof', 'derive', 'derivation', 'show that',
            'step by step completely', 'rigorous', 'comprehensive',
        ]
        if any(ind in query_lower for ind in deep_indicators):
            logger.info("📊 Query complexity: DEEP (15 iterations)")
            return self.ITERATION_LIMITS['deep']
        
        # COMPLEX indicators
        complex_indicators = [
            'solve', 'calculate', 'compare and contrast', 'analyze',
            'detailed', 'explain mechanism', 'why does', 'how does',
        ]
        if any(ind in query_lower for ind in complex_indicators):
            logger.info("📊 Query complexity: COMPLEX (12 iterations)")
            return self.ITERATION_LIMITS['complex']
        
        # Mathematical content
        if re.search(r'\d+\s*[+\-*/^=]\s*\d+|f\(x\)|d[xy]/d[xy]', query_lower):
            logger.info("📊 Query complexity: COMPLEX (mathematical)")
            return self.ITERATION_LIMITS['complex']
        
        # MODERATE indicators
        moderate_indicators = ['explain', 'what is', 'difference between', 'describe']
        if any(ind in query_lower for ind in moderate_indicators):
            if word_count > 10:
                logger.info("📊 Query complexity: MODERATE (8 iterations)")
                return self.ITERATION_LIMITS['moderate']
            logger.info("📊 Query complexity: SIMPLE (5 iterations)")
            return self.ITERATION_LIMITS['simple']
        
        # Long queries need more iterations
        if word_count > 20:
            logger.info("📊 Query complexity: MODERATE (long query)")
            return self.ITERATION_LIMITS['moderate']
        
        # Default to simple (not moderate) for faster responses
        logger.info("📊 Query complexity: DEFAULT/SIMPLE")
        return self.ITERATION_LIMITS['simple']
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the agent's name/identifier"""
        pass
    
    @abstractmethod
    def get_agent_persona(self) -> str:
        """Return the agent's persona/character description"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Return list of tool names this agent can use"""
        pass
    
    def get_system_prompt(self, state: AgentState) -> str:
        """Build the system prompt for the LLM"""
        tools_desc = self._get_tools_description(state.context)
        # COGNITIVE OS FIX: Pass context to persona for context-aware behavior
        try:
            persona = self.get_agent_persona(state.context)
        except TypeError:
            # Backward compatibility: some agents don't accept context param
            persona = self.get_agent_persona()
        
        return f"""{persona}

## YOUR CAPABILITIES
You are an intelligent agent that can THINK, ACT, and OBSERVE.
You have access to the following tools:

{tools_desc}

## HOW TO RESPOND
You MUST respond in this exact JSON format:

{{
    "thought": "Your reasoning about what to do next. Be specific and logical.",
    "action": "tool_name or FINISH",
    "action_input": {{"param1": "value1"}} or null if finishing,
    "confidence": 0.0 to 1.0
}}

## RULES
1. ALWAYS think step by step before acting
2. Use tools when you need information or calculations
3. Don't guess - use tools to verify
4. When you have enough information, use action "FINISH"
5. Be honest about your confidence level
6. If stuck, try a different approach

## CURRENT CONTEXT
Student Query: {state.query}
Subject: {state.context.get('subject', 'General')}
Student Name: {state.context.get('student_profile', {}).get('user_name', 'Student')}

{self._get_constraint_instruction(state.context)}

## REASONING SO FAR
{state.get_reasoning_summary()}
"""
    
    def _get_tools_description(self, context: dict = None) -> str:
        """Get descriptions of all available tools"""
        if not self.tool_registry:
            return "No tools available."
        
        context = context or {}
        
        # COGNITIVE OS FIX: Pass context to get_available_tools
        try:
            agent_tools = self.get_available_tools(context)
        except TypeError:
            # Backward compatibility: some agents don't accept context param
            agent_tools = self.get_available_tools()
        
        # =================================================================
        # FIX v1.0: ROUTING DECISION AS SINGLE SOURCE OF TRUTH FOR TOOLS
        # If routing decision specifies tools_to_enable, use union of:
        # - Agent's native tools (from get_available_tools)
        # - Routing-requested tools (from context)
        # This allows routing to ADD tools like web_search to any agent
        # =================================================================
        routing_tools = context.get('_routing_allowed_tools', [])
        
        if routing_tools:
            # Create union: agent's tools + routing's tools
            available = list(set(agent_tools) | set(routing_tools))
            logger.info(f"🔧 [TOOL UNION] agent_tools={agent_tools} + routing_tools={routing_tools} = {available}")
        else:
            available = agent_tools
        
        descriptions = []
        
        for tool_name in available:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                descriptions.append(f"- **{tool.name}**: {tool.description}")
                if tool.parameters:
                    params = ", ".join([f"{k}: {v}" for k, v in tool.parameters.items()])
                    descriptions.append(f"  Parameters: {params}")
        
        # Always add FINISH action
        descriptions.append("- **FINISH**: Use when you have the final answer ready")
        descriptions.append("  Parameters: {\"answer\": \"Your final response to the student\"}")
        
        return "\n".join(descriptions)
    
    def _get_constraint_instruction(self, context: dict) -> str:
        """
        Get formula/fact constraints from context for pre-generation injection.
        
        This is part of the NEURO-SYMBOLIC enhancement:
        - Formulas verified by RAG/KnowledgeGraph are injected as constraints
        - Symbolic proofs are provided as verified solutions
        - This prevents hallucination of incorrect formulas
        
        Non-breaking: Returns empty string if no constraints available.
        """
        instruction = context.get('_constraint_instruction', '')
        
        # Add symbolic solution if available
        symbolic = context.get('symbolic_solution')
        if symbolic and instruction:
            instruction += f"\n\nVerified symbolic solution: {symbolic}"
        elif symbolic:
            instruction = f"VERIFIED SOLUTION AVAILABLE: {symbolic}"
        
        # Wrap in section header if present
        if instruction:
            return f"## VERIFIED CONSTRAINTS\n{instruction}"
        
        return ""
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        quick_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point - runs the ReAct loop until completion.
        
        FAST-FIRST ARCHITECTURE:
        - quick_mode=True: Single LLM call with rich context (Phase 1, <5s SLA)
        - quick_mode=False: Full ReAct reasoning loop (Phase 2, deep)
        
        TIMEOUT PROTECTION:
        - Wrapped in global timeout (default 25s, 4s in quick_mode)
        - On timeout, returns graceful fallback response
        - Never leaves student waiting indefinitely
        
        Args:
            query: The student's question
            context: Context dict with subject, user_id, etc.
            quick_mode: If True, skip ReAct loop for fast single-call response
        
        Returns:
            Agent response with reasoning chain and final answer
        """
        # PHASE 1: FAST-FIRST (Single LLM call, <5s SLA)
        if quick_mode:
            logger.info(f"⚡ {self.get_agent_name()} QUICK MODE: {query[:50]}...")
            return await self._run_fast(query, context)
        
        # PHASE 2: DEEP REASONING (Full ReAct loop)
        logger.info(f"🧠 {self.get_agent_name()} starting (timeout={self.global_timeout}s): {query[:50]}...")
        
        try:
            # Wrap entire ReAct loop in global timeout
            return await asyncio.wait_for(
                self._run_react_loop(query, context),
                timeout=self.global_timeout
            )
            
        except asyncio.TimeoutError:
            # TIMEOUT: Generate graceful fallback
            logger.warning(f"⏰ {self.get_agent_name()} TIMEOUT after {self.global_timeout}s - falling back")
            return self._generate_timeout_fallback(query, context)
            
        except Exception as e:
            logger.error(f"❌ {self.get_agent_name()} error: {e}", exc_info=True)
            return self._generate_error_fallback(query, context, str(e))
    
    async def _try_math_fast_path(self, query: str) -> Optional[Dict[str, Any]]:
        """
        🧮 MATH FAST-PATH: Solve simple equations instantly without LLM.
        
        This avoids the 5-6s LLM round-trip for trivial calculations like:
        - "Solve: 3x + 5 = 17"
        - "What is 25 * 4?"
        - "Calculate: 15% of 200"
        
        Returns None if query is not a simple math problem (falls through to LLM).
        """
        import re
        
        query_lower = query.lower()
        
        # Detect if this is a math problem
        math_keywords = ['solve', 'calculate', 'what is', 'find', 'compute', 'evaluate']
        is_math_query = any(kw in query_lower for kw in math_keywords)
        has_equation = '=' in query or any(op in query for op in ['+', '-', '*', '/', '^'])
        
        if not (is_math_query or has_equation):
            return None
        
        try:
            # Try to extract and solve equation
            # Pattern: "Solve: (3x + 5) = 2x + 17" or "3x + 5 = 17"
            equation_match = re.search(r'(?:solve[:\s]*)?(.+?)\s*=\s*(.+?)(?:\s*$|[,.])', query, re.IGNORECASE)
            
            if equation_match:
                left = equation_match.group(1).strip('()[] ')
                right = equation_match.group(2).strip('()[] ')
                
                # Check if it's a simple linear equation (contains x or y)
                if 'x' in left.lower() or 'x' in right.lower():
                    try:
                        from sympy import symbols, Eq, solve, sympify
                        from sympy.parsing.sympy_parser import parse_expr
                        
                        x = symbols('x')
                        
                        # Parse both sides
                        left_expr = parse_expr(left.lower().replace('^', '**'), local_dict={'x': x})
                        right_expr = parse_expr(right.lower().replace('^', '**'), local_dict={'x': x})
                        
                        # Solve the equation
                        equation = Eq(left_expr, right_expr)
                        solution = solve(equation, x)
                        
                        if solution:
                            sol_str = ', '.join([f"x = {s}" for s in solution])
                            
                            # Format nice response with steps
                            response = f"""**Solution:**

Given equation: {left} = {right}

**Step 1:** Rearrange the equation
Move all terms with x to one side:
{left} - ({right}) = 0

**Step 2:** Simplify and solve
{sol_str}

**Verification:**
Substituting back: {left.replace('x', f'({solution[0]})')} = {right.replace('x', f'({solution[0]})')} ✓

The answer is **{sol_str}** 🎯"""
                            
                            logger.info(f"⚡ Math fast-path solved: {query[:40]}... → {sol_str}")
                            
                            return {
                                'success': True,
                                'content': response,
                                'agent': self.get_agent_name(),
                                'confidence': 0.95,
                                'metadata': {
                                    'mode': 'math_fast_path',
                                    'solution': str(solution),
                                    'phase': 1,
                                    'llm_calls': 0  # No LLM call needed!
                                }
                            }
                    except Exception as sympy_err:
                        logger.debug(f"🧮 SymPy failed: {sympy_err}")
                        # Fall through to LLM
            
            # Try simple arithmetic
            # Pattern: "What is 25 * 4?" or "Calculate 15% of 200"
            arith_match = re.search(r'(?:what is|calculate|compute)[:\s]*([0-9+\-*/()%\s.]+)', query_lower)
            if arith_match:
                expr = arith_match.group(1).strip()
                # Handle percentage: "15% of 200" -> "15/100*200"
                expr = re.sub(r'(\d+)\s*%\s*of\s*(\d+)', r'(\1/100)*\2', expr)
                
                try:
                    result = eval(expr)  # Safe for simple math expressions
                    if isinstance(result, (int, float)):
                        response = f"""**Calculation:**

{arith_match.group(1).strip()} = **{result}**

That's your answer! 🎯"""
                        
                        return {
                            'success': True,
                            'content': response,
                            'agent': self.get_agent_name(),
                            'confidence': 0.99,
                            'metadata': {
                                'mode': 'arithmetic_fast_path',
                                'result': result,
                                'phase': 1,
                                'llm_calls': 0
                            }
                        }
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"🧮 Math fast-path error: {e}")
        
        return None  # Fall through to LLM
    
    async def _run_fast(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        FAST-FIRST: Single LLM call with rich context.
        
        This is Phase 1 of the Fast-First architecture:
        - ONE LLM call only (hard cap)
        - 4 second timeout (hard SLA)
        - Rich context injection (agent persona + student profile + memory)
        - Always returns valid response (never hangs)
        - 🆕 Web search for current events/real-time queries
        
        Intelligence is preserved through:
        - Agent-specific system prompt (persona)
        - Student profile personalization
        - Memory context injection
        - RAG/curriculum context if available
        - Web search for real-time information
        """
        # ================================================================
        # 🚨 ENTRY POINT LOG - This MUST appear if _run_fast is called
        # ================================================================
        logger.info(f"🚀 [_run_fast ENTRY] {self.get_agent_name()} processing: {query[:60]}...")
        
        # ================================================================
        # 🧮 MATH FAST-PATH: Solve simple equations instantly
        # ================================================================
        # For simple algebraic equations, use SymPy to solve directly
        # This avoids the 5-6s LLM round-trip for trivial calculations
        # ================================================================
        try:
            math_result = await self._try_math_fast_path(query)
            if math_result:
                logger.info(f"⚡ [_run_fast] Math fast-path SUCCESS")
                return math_result
        except Exception as math_err:
            logger.debug(f"🧮 Math fast-path skipped: {math_err}")
            # Continue to normal path
        
        # ================================================================
        # TIMEOUT BUDGET: Must fit within supervisor's 15s budget with retry margin
        # Primary: 8s (sufficient for most LLM calls)
        # Retry: 5s (shorter, we've already waited)
        # Total: 13s worst case, leaves 2s margin in supervisor's 15s
        # ================================================================
        FAST_TIMEOUT = 8.0  # Primary call timeout
        RETRY_TIMEOUT = 5.0  # Retry call timeout (shorter)
        
        try:
            from services.llm_service import call_llm
            
            # Build rich context for single-shot answer
            subject = context.get('subject', 'the topic')
            student_profile = context.get('student_profile', {})
            student_name = student_profile.get('name', '')
            mastery_level = context.get('memory_context', {}).get('mastery_level', 50)
            
            # Memory context for continuity
            memory_ctx = context.get('memory_context', {})
            recent = memory_ctx.get('recent_context', [])[-3:]
            continuity = memory_ctx.get('continuity', {})
            
            # ================================================================
            # 🌐 WEB SEARCH: Use routing engine's semantic decision
            # ================================================================
            # CRITICAL: Use the routing engine's decision (based on semantic analysis)
            # instead of fragile keyword matching. The routing engine analyzes:
            # - temporal_scope (immediate, today, recent)
            # - urgency_level (high, medium, low)
            # - intent classification
            # - topic category (current affairs, static content)
            # This ensures consistent, intent-driven web search triggering.
            # ================================================================
            web_search_context = ""
            
            # Primary: Use routing engine's semantic decision (passed in context)
            needs_web_search = context.get('requires_web_search', False)
            web_search_reason = context.get('web_search_reason', 'routing_decision')
            
            logger.info(f"🌐 [_run_fast] Web search needed: {needs_web_search} | Reason: {web_search_reason} | Query: {query[:40]}...")
            
            if needs_web_search:
                logger.info(f"🌐 [QUICK MODE] Detected real-time query, fetching web search...")
                try:
                    from agents.core.tools.web_search import WebSearchTool
                    web_tool = WebSearchTool()
                    search_result = await asyncio.wait_for(
                        web_tool.execute(query=query, subject=subject, context=context),
                        timeout=3.0  # 3s timeout for web search
                    )
                    if search_result.success and search_result.output:
                        # Safe slicing - ensure output is a string
                        output_str = str(search_result.output) if search_result.output else ""
                        web_search_context = f"\n\n**Web Search Results:**\n{output_str[:800]}"
                        logger.info(f"🌐 [QUICK MODE] Web search successful")
                except asyncio.TimeoutError:
                    logger.warning(f"🌐 [QUICK MODE] Web search timeout - continuing without")
                except Exception as e:
                    logger.warning(f"🌐 [QUICK MODE] Web search error: {e}")
            
            # Build context string
            context_parts = []
            if student_name:
                context_parts.append(f"Student: {student_name}")
            if mastery_level:
                context_parts.append(f"Mastery: {mastery_level}%")
            if continuity.get('is_continuation'):
                context_parts.append(f"Continuing topic: {continuity.get('topic', 'previous')}")
            if recent:
                # Safely extract recent context (could be str or dict or None)
                try:
                    recent_item = recent[-1]
                    if isinstance(recent_item, dict):
                        recent_str = recent_item.get('content') or recent_item.get('message') or str(recent_item)
                    else:
                        recent_str = str(recent_item) if recent_item else ""
                    if recent_str:
                        context_parts.append(f"Recent: {str(recent_str)[:100]}")
                except Exception:
                    pass  # Skip if any error extracting recent context
            
            # RAG/curriculum context if available (safe slicing)
            curriculum = context.get('curriculum_context')
            if curriculum:
                curriculum_str = str(curriculum) if curriculum else ""
                if curriculum_str:
                    context_parts.append(f"Curriculum: {curriculum_str[:200]}")
            
            # Formula constraints if available
            constraints = context.get('_constraint_instruction', '')
            
            context_str = "\n".join(context_parts) if context_parts else "New student"
            
            # Build the prompt with agent persona (include web search if available)
            prompt = f"""Question: {query}
Subject: {subject}

Student Context:
{context_str}

{constraints}
{web_search_context}

Provide a clear, helpful, well-structured educational response.
Be accurate, engaging, and appropriately detailed for the student's level.
Use examples and analogies to make concepts clear.
{"Use the web search results above to provide current/accurate information." if web_search_context else ""}"""

            # Single LLM call with hard timeout
            # PERFORMANCE: Reduced max_tokens for faster response in quick mode
            # 500 tokens ≈ 375 words, sufficient for initial explanation
            # Phase 2 (deep mode) can elaborate further if needed
            import time
            llm_start = time.time()
            
            # Use model from cognitive routing (upstream decision)
            selected_model = self._resolve_model(context.get('selected_model'))
            logger.info(f"⚡ [_run_fast] Using model: {selected_model}")
            
            response = await asyncio.wait_for(
                call_llm(
                    prompt=prompt,
                    api_key=self.llm_key,
                    temperature=0.7,
                    max_tokens=500,  # Reduced from 1000 for faster quick mode
                    model=selected_model,
                    system_message=self.get_agent_persona()
                ),
                timeout=FAST_TIMEOUT
            )
            
            llm_time = time.time() - llm_start
            logger.info(f"⚡ [_run_fast] LLM call completed in {llm_time:.2f}s")
            
            if response and len(response.strip()) > 30:
                logger.info(f"⚡ {self.get_agent_name()} QUICK MODE success {'(with web search)' if web_search_context else ''}")
                return {
                    'success': True,
                    'content': response,
                    'agent': self.get_agent_name(),
                    'confidence': 0.9 if web_search_context else 0.85,
                    'metadata': {
                        'mode': 'quick',
                        'phase': 1,
                        'llm_calls': 1,
                        'web_search_used': bool(web_search_context),
                        'refinement_available': True  # Flag for Phase 2
                    }
                }
            
            # ================================================================
            # 🔄 SINGLE RETRY: LLM returned empty/short - retry once
            # Transient failures (network, rate limit) often succeed on retry
            # ================================================================
            if not response or len(response.strip()) <= 30:
                logger.warning(f"⚠️ [_run_fast] LLM returned empty/short response, retrying once...")
                try:
                    response = await asyncio.wait_for(
                        call_llm(
                            prompt=prompt,
                            api_key=self.llm_key,
                            temperature=0.7,
                            max_tokens=500,
                            model=selected_model,
                            system_message=self.get_agent_persona()
                        ),
                        timeout=FAST_TIMEOUT
                    )
                    if response and len(response.strip()) > 30:
                        logger.info(f"⚡ {self.get_agent_name()} QUICK MODE retry SUCCESS")
                        return {
                            'success': True,
                            'content': response,
                            'agent': self.get_agent_name(),
                            'confidence': 0.8,  # Slightly lower confidence for retry
                            'metadata': {
                                'mode': 'quick_retry',
                                'phase': 1,
                                'llm_calls': 2,
                                'web_search_used': bool(web_search_context),
                                'refinement_available': True
                            }
                        }
                except Exception as retry_err:
                    logger.warning(f"⚠️ [_run_fast] Retry also failed: {retry_err}")
                
        except asyncio.TimeoutError:
            # ================================================================
            # 🔄 SINGLE RETRY: Timeout - retry with shorter timeout
            # LLM providers sometimes have transient slowdowns
            # ================================================================
            logger.warning(f"⏰ {self.get_agent_name()} QUICK MODE timeout (>{FAST_TIMEOUT}s), retrying with shorter timeout...")
            try:
                response = await asyncio.wait_for(
                    call_llm(
                        prompt=prompt,
                        api_key=self.llm_key,
                        temperature=0.7,
                        max_tokens=400,  # Reduced tokens for faster response
                        model=selected_model,
                        system_message=self.get_agent_persona()
                    ),
                    timeout=RETRY_TIMEOUT
                )
                if response and len(response.strip()) > 30:
                    logger.info(f"⚡ {self.get_agent_name()} QUICK MODE timeout retry SUCCESS")
                    return {
                        'success': True,
                        'content': response,
                        'agent': self.get_agent_name(),
                        'confidence': 0.75,  # Lower confidence for timeout retry
                        'metadata': {
                            'mode': 'quick_timeout_retry',
                            'phase': 1,
                            'llm_calls': 2,
                            'web_search_used': bool(web_search_context),
                            'refinement_available': True
                        }
                    }
            except Exception as retry_err:
                logger.warning(f"⚠️ [_run_fast] Timeout retry also failed: {retry_err}")
                
        except Exception as e:
            logger.warning(f"⚠️ {self.get_agent_name()} QUICK MODE error: {e}")
        
        # ================================================================
        # 🛡️ FALLBACK: Use partial intelligence if available
        # If we have web search results, include them in fallback
        # ================================================================
        import uuid as uuid_module
        refinement_request_id = f"refine_{uuid_module.uuid4().hex[:8]}"
        
        logger.warning(f"⏰ {self.get_agent_name()} QUICK MODE fallback triggered - starting background refinement: {refinement_request_id}")
        subject = context.get('subject', 'your question')
        
        # 🛡️ PRESERVE PARTIAL INTELLIGENCE: If we gathered web search results, include them
        # This gives the student SOMETHING useful even when LLM fails
        if web_search_context:
            logger.info(f"🛡️ [_run_fast] Including web search results in fallback response")
            fallback_content = f"""I'm working on your question about {subject}. Here's what I found so far:

{web_search_context}

I'm preparing a more complete explanation for you! 🧠"""
            fallback_confidence = 0.5  # Higher confidence since we have partial data
        else:
            fallback_content = f"""I'm analyzing your question about {subject}...

Just a moment while I prepare a detailed explanation! 🧠

(Loading complete answer...)"""
            fallback_confidence = 0.3  # Low confidence = UI should expect refinement
        
        return {
            'success': True,
            'is_fallback': True,
            'content': fallback_content,
            'agent': self.get_agent_name(),
            'confidence': fallback_confidence,
            'metadata': {
                'mode': 'quick_fallback',
                'phase': 1,
                'llm_calls': 0,
                'web_search_used': bool(web_search_context),
                'partial_intelligence': bool(web_search_context),  # Flag that we have partial data
                'refinement_available': True,
                'refinement_pending': True,
                'refinement_request_id': refinement_request_id,
                'timeout_occurred': True
            }
        }
    
    async def _run_react_loop(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Internal ReAct loop - the core reasoning engine.
        
        FAULT-TOLERANT DESIGN:
        - Retries on transient failures (handled in _think)
        - Isolates tool failures (handled in _act)
        - Tracks failure types for observability
        - Always produces a reasoned response
        
        Uses ADAPTIVE iteration limits based on query complexity:
        - Simple queries: fewer iterations (faster response)
        - Complex queries: more iterations (deeper reasoning)
        """
        # Get adaptive iteration limit based on query complexity
        adaptive_max = self._get_adaptive_iterations(query, context)
        self.max_iterations = adaptive_max
        
        # Initialize state
        state = AgentState(
            query=query,
            context=context,
            max_iterations=adaptive_max
        )
        
        # Track failures for observability
        failure_log = []
        
        # ================================================================
        # PER-ITERATION TIMEOUT: Each step gets max 12s
        # FIX v1.0: Reduced from 25s to allow 2 iterations within global timeout
        # This ensures slow iterations don't consume the entire agent budget
        # If one iteration is slow, we finish early rather than timeout
        # ================================================================
        ITERATION_TIMEOUT = 12.0  # Max 12s per think+act cycle (allows 2 iterations in 25s global)
        slow_iteration_count = 0
        MAX_SLOW_ITERATIONS = 2  # After 2 slow iterations, finish early
        
        try:
            logger.info(f"[ReAct] Starting loop for {self.get_agent_name()}: max_iter={adaptive_max}")
            
            # Run the ReAct loop
            while state.iterations < state.max_iterations:
                state.iterations += 1
                step_start = datetime.now()
                
                # THINK: Generate next thought/action with iteration timeout
                state.status = AgentStatus.THINKING
                logger.info(f"[ReAct] Step {state.iterations}/{adaptive_max}: THINKING...")
                
                try:
                    thought_action = await asyncio.wait_for(
                        self._think(state),
                        timeout=ITERATION_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ [ReAct] Step {state.iterations} THINK timed out (>{ITERATION_TIMEOUT}s)")
                    slow_iteration_count += 1
                    if slow_iteration_count >= MAX_SLOW_ITERATIONS:
                        logger.warning(f"[ReAct] Too many slow iterations, finishing early")
                        state.status = AgentStatus.COMPLETE
                        state.final_answer = await self._generate_direct_answer(state)
                        state.confidence = 0.6
                        break
                    # Create a FINISH action to complete gracefully
                    thought_action = state.add_thought("I'll provide a direct answer due to response time.")
                    thought_action.action = "FINISH"
                    thought_action.action_input = {"answer": await self._generate_direct_answer(state)}
                
                # ================================================================
                # SHARED REASONING: Post insight to shared state if available
                # This enables TRUE multi-agent collaboration during reasoning
                # ADDITIVE: Only runs if shared state exists, non-blocking
                # ================================================================
                if thought_action and thought_action.thought:
                    await self._post_insight_to_shared_state(
                        context=state.context,
                        thought=thought_action.thought,
                        confidence=getattr(thought_action, 'confidence', 0.7)
                    )
                
                # _think now always returns a ThoughtAction (with FINISH on failure)
                if not thought_action:
                    # This should not happen with the new _think, but handle defensively
                    failure_log.append(f"Step {state.iterations}: THINK returned None")
                    logger.error(f"[ReAct] Critical: _think returned None at step {state.iterations}")
                    # Create emergency FINISH
                    thought_action = state.add_thought("I'll provide my best answer.")
                    thought_action.action = "FINISH"
                    thought_action.action_input = {"answer": await self._generate_direct_answer(state)}
                
                # Check if we should finish
                if thought_action.action == "FINISH":
                    answer = thought_action.action_input.get("answer", "")
                    
                    # CRITICAL: If answer is empty or looks like JSON, regenerate
                    if not answer or len(answer.strip()) < 20 or answer.strip().startswith('{'):
                        logger.warning("[ReAct] Empty or invalid answer, regenerating with direct LLM call")
                        answer = await self._generate_direct_answer(state)
                    
                    state.status = AgentStatus.COMPLETE
                    state.final_answer = answer
                    state.confidence = thought_action.action_input.get("confidence", 0.8)
                    logger.info(f"[ReAct] Completed at step {state.iterations} with FINISH action")
                    break
                
                # ACT: Execute the chosen tool with timeout protection
                state.status = AgentStatus.ACTING
                logger.info(f"[ReAct] Step {state.iterations}: ACTING with {thought_action.action}")
                
                try:
                    observation = await asyncio.wait_for(
                        self._act(thought_action, state),
                        timeout=ITERATION_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ [ReAct] Step {state.iterations} ACT timed out (>{ITERATION_TIMEOUT}s)")
                    slow_iteration_count += 1
                    observation = f"Tool '{thought_action.action}' is taking too long. Proceeding with available information."
                thought_action.observation = observation
                
                # Track if this was a failure observation
                if "failed" in observation.lower() or "error" in observation.lower():
                    failure_log.append(f"Step {state.iterations}: {thought_action.action} - {observation[:100]}")
                
                # OBSERVE: Process the result (handled implicitly in next iteration)
                state.status = AgentStatus.OBSERVING
                
                step_time = (datetime.now() - step_start).total_seconds()
                if self.verbose:
                    logger.info(f"[ReAct] Step {state.iterations} complete: {thought_action.action} ({step_time:.2f}s)")
            
            # Check if we hit max iterations
            if state.iterations >= state.max_iterations and state.status != AgentStatus.COMPLETE:
                logger.warning(f"[ReAct] {self.get_agent_name()} hit max iterations ({adaptive_max})")
                state.status = AgentStatus.COMPLETE
                state.final_answer = await self._generate_fallback_answer(state)
                state.confidence = 0.5
            
            state.end_time = datetime.now()
            
            # Add failure log to metadata for observability
            response = self._format_response(state)
            if failure_log:
                response['metadata'] = response.get('metadata', {})
                response['metadata']['failure_log'] = failure_log
                response['metadata']['had_failures'] = True
            
            return response
            
        except Exception as e:
            logger.error(f"[ReAct] {self.get_agent_name()} critical loop error: {e}", exc_info=True)
            state.status = AgentStatus.ERROR
            state.error = str(e)
            state.end_time = datetime.now()
            
            # Even on critical error, try to provide a response
            error_response = self._format_error_response(state)
            error_response['metadata'] = error_response.get('metadata', {})
            error_response['metadata']['failure_type'] = 'CRITICAL_ERROR'
            error_response['metadata']['failure_log'] = failure_log + [f"Critical: {str(e)}"]
            
            return error_response
    
    def _generate_timeout_fallback(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate fallback response when ReAct loop times out.
        
        PRINCIPLE: Be honest about timeouts, don't pretend to think.
        """
        subject = context.get('subject', 'your question')
        short_query = query[:60] + "..." if len(query) > 60 else query
        
        # Honest acknowledgment - don't say "let me think" when no thinking is happening
        fallback_content = f"""I'm taking longer than expected to process your question about {subject}.

Your question: "{short_query}"

This is a complex topic that needs more time. Please try asking again - I want to give you a proper answer."""
        
        logger.warning(f"⏰ [ReAct] Timeout fallback for: {query[:50]}...")
        
        return {
            "success": False,  # Timeout is a failure, be honest
            "agent": self.get_agent_name(),
            "content": fallback_content,
            "confidence": 0.3,
            "reasoning_chain": [],
            "tools_used": [],
            "iterations": 0,
            "metadata": {
                "agent_type": "react",
                "timeout_fallback": True,
                "timeout_seconds": self.global_timeout
            }
        }
    
    def _generate_error_fallback(
        self,
        query: str,
        context: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """
        Generate a graceful error response.
        
        PRINCIPLE: Be honest about errors, don't blame the student.
        - Acknowledge the issue is on our side
        - Don't ask them to rephrase
        - Offer to try again
        """
        subject = context.get('subject', 'your question')
        short_query = query[:60] + "..." if len(query) > 60 else query
        
        # Contextual acknowledgment without blaming student
        fallback_content = f"""I ran into a technical issue while working on your question about {subject}.

Your question was: "{short_query}"

This is on my end, not yours. Please try asking again - I want to help you understand this topic properly."""
        
        logger.error(f"❌ [ReAct] Error fallback for: {query[:50]}... (error: {error[:100]})")
        
        return {
            "success": False,
            "agent": self.get_agent_name(),
            "content": fallback_content,
            "error": error,
            "confidence": 0.2,
            "reasoning_chain": [],
            "tools_used": [],
            "iterations": 0,
            "metadata": {
                "agent_type": "react",
                "error_fallback": True,
                "original_error": error[:200]
            }
        }
    
    async def _think(self, state: AgentState) -> Optional[ThoughtAction]:
        """
        Generate the next thought and action using LLM.
        
        RESILIENT SINGLE-FLIGHT:
        - Primary LLM call attempt
        - Single retry for empty/transient failures
        - On persistent failure, return FINISH with direct answer
        """
        try:
            system_prompt = self.get_system_prompt(state)
            user_message = f"What should you do next to answer: {state.query}"
            
            # If we have previous observations, include them
            if state.reasoning_chain and state.reasoning_chain[-1].observation:
                last = state.reasoning_chain[-1]
                user_message = f"""Based on the observation from {last.action}:
{last.observation}

What should you do next?"""
            
            # Primary LLM call with single retry for transient failures
            # Pass model from context (cognitive routing decision)
            selected_model = state.context.get('selected_model') if state.context else None
            response = await self._call_llm(system_prompt, user_message, model=selected_model)
            
            if not response:
                # ================================================================
                # 🔄 SINGLE RETRY: Empty response - likely transient failure
                # Network issues, rate limits, or cold starts often resolve on retry
                # ================================================================
                logger.warning("[ReAct] LLM empty response, retrying once...")
                response = await self._call_llm(system_prompt, user_message, model=selected_model)
                
                if not response:
                    # Retry also failed - fall back to direct answer
                    logger.warning("[ReAct] LLM retry also empty, generating direct answer")
                    ta = state.add_thought("I'll provide a direct answer based on my knowledge.")
                    ta.action = "FINISH"
                    ta.action_input = {"answer": await self._generate_direct_answer(state)}
                    return ta
            
            # Parse response
            parsed = self._parse_llm_response(response)
            
            # Create thought action
            ta = state.add_thought(parsed.get("thought", "Thinking..."))
            ta.action = parsed.get("action", "FINISH")
            ta.action_input = parsed.get("action_input", {})
            
            return ta
            
        except Exception as e:
            # ================================================================
            # 🔄 SINGLE RETRY: Exception - may be transient network issue
            # ================================================================
            logger.warning(f"[ReAct] Think error, retrying once: {e}")
            try:
                selected_model = state.context.get('selected_model') if state.context else None
                response = await self._call_llm(system_prompt, user_message, model=selected_model)
                if response:
                    parsed = self._parse_llm_response(response)
                    ta = state.add_thought(parsed.get("thought", "Thinking..."))
                    ta.action = parsed.get("action", "FINISH")
                    ta.action_input = parsed.get("action_input", {})
                    logger.info("[ReAct] Think retry succeeded")
                    return ta
            except Exception as retry_err:
                logger.warning(f"[ReAct] Think retry also failed: {retry_err}")
            
            # Both attempts failed - fall back to direct answer
            logger.error(f"[ReAct] Think failed after retry: {e}")
            ta = state.add_thought("Let me provide you with a helpful response.")
            ta.action = "FINISH"
            ta.action_input = {"answer": await self._generate_direct_answer(state)}
            return ta
    
    async def _generate_direct_answer(self, state: AgentState) -> str:
        """
        Generate a direct answer when ReAct reasoning fails.
        
        RESILIENT DIRECT ANSWER:
        - Primary LLM call with single retry for transient failures
        - Falls back to deterministic response only after retry fails
        - Preserves gathered observations in fallback
        """
        # Build context from any observations we've gathered
        observations = [ta.observation for ta in state.reasoning_chain if ta.observation]
        context_str = "\n".join(observations[-3:]) if observations else "No prior context."
        subject = state.context.get('subject', 'the topic')
        
        prompt = f"""You are a knowledgeable mentor. Answer this question directly:

Question: {state.query}
Subject: {subject}

Context from analysis: {context_str}

Provide a clear, helpful, well-structured answer. Be accurate and educational."""
        
        from services.llm_service import call_llm
        
        # Use model from cognitive routing (upstream decision)
        selected_model = self._resolve_model(state.context.get('selected_model'))
        
        # Primary LLM call
        try:
            response = await asyncio.wait_for(
                call_llm(
                    prompt=prompt,
                    api_key=self.llm_key,
                    temperature=0.7,
                    max_tokens=1500,  # Cognitive path: full educational explanation capacity
                    model=selected_model,
                    system_message=self.get_agent_persona()
                ),
                timeout=15.0
            )
            if response and len(response.strip()) > 30:
                logger.info(f"[ReAct] Direct answer generated successfully (model: {selected_model})")
                return response
                
            # ================================================================
            # 🔄 SINGLE RETRY: Empty response - retry once
            # ================================================================
            if not response or len(response.strip()) <= 30:
                logger.warning("[ReAct] Direct answer empty, retrying once...")
                response = await asyncio.wait_for(
                    call_llm(
                        prompt=prompt,
                        api_key=self.llm_key,
                        temperature=0.7,
                        max_tokens=1500,
                        model=selected_model,
                        system_message=self.get_agent_persona()
                    ),
                    timeout=12.0  # Shorter timeout for retry
                )
                if response and len(response.strip()) > 30:
                    logger.info(f"[ReAct] Direct answer retry succeeded (model: {selected_model})")
                    return response
                    
        except Exception as e:
            # ================================================================
            # 🔄 SINGLE RETRY: Exception - may be transient
            # ================================================================
            logger.warning(f"[ReAct] Direct answer LLM failed, retrying: {e}")
            try:
                response = await asyncio.wait_for(
                    call_llm(
                        prompt=prompt,
                        api_key=self.llm_key,
                        temperature=0.7,
                        max_tokens=1200,  # Reduced tokens for faster retry
                        model=selected_model,
                        system_message=self.get_agent_persona()
                    ),
                    timeout=10.0  # Shorter timeout for retry
                )
                if response and len(response.strip()) > 30:
                    logger.info(f"[ReAct] Direct answer exception retry succeeded")
                    return response
            except Exception as retry_err:
                logger.warning(f"[ReAct] Direct answer retry also failed: {retry_err}")
        
        # ================================================================
        # 🛡️ DETERMINISTIC FALLBACK: Preserve any observations we gathered
        # ================================================================
        logger.warning("[ReAct] Using deterministic fallback response")
        short_q = state.query[:60] + "..." if len(state.query) > 60 else state.query
        
        # If we have observations, include them in fallback (partial intelligence)
        if observations:
            obs_text = "\n".join([f"• {obs[:200]}" for obs in observations[:3]])
            return f"""I'm working on your question about {subject}.

**Your question:** "{short_q}"

**Here's what I found so far:**
{obs_text}

I'm preparing a more complete explanation. Please wait a moment! 🧠"""
        
        # No observations - generic fallback
        return f"""I'm working on your question about {subject}.

**Your question:** "{short_q}"

**Key points to consider:**
- Break down the problem into smaller parts
- Review the fundamental concepts first
- Practice with examples

I'm experiencing a brief delay. Please try asking again, and I'll give you a proper explanation! 💪"""
    
    async def _act(self, thought_action: ThoughtAction, state: AgentState) -> str:
        """
        Execute the chosen action/tool with error isolation.
        
        FAULT-TOLERANT: Tool failures don't crash the loop.
        Returns observations that help reasoning continue.
        """
        action = thought_action.action
        action_input = thought_action.action_input or {}
        
        if action == "FINISH":
            return "Task complete"
        
        try:
            # Execute tool
            if self.tool_registry:
                tool = self.tool_registry.get_tool(action)
                if tool:
                    state.tools_used.append(action)
                    try:
                        # Wrap tool execution with timeout
                        result = await asyncio.wait_for(
                            tool.execute(**action_input, context=state.context),
                            timeout=10.0  # 10 second timeout per tool
                        )
                        if result.success:
                            logger.info(f"[ReAct] Tool {action} succeeded")
                            return result.output
                        else:
                            # TOOL_FAILURE: Tool executed but returned error
                            logger.warning(f"[ReAct] TOOL_FAILURE: {action} - {result.error}")
                            return f"Tool '{action}' encountered an issue: {result.error}. I'll proceed with available information."
                    except asyncio.TimeoutError:
                        # TOOL_TIMEOUT: Tool took too long
                        logger.warning(f"[ReAct] TOOL_TIMEOUT: {action} exceeded 10s")
                        return f"Tool '{action}' is taking too long. I'll continue with my reasoning."
                    except Exception as tool_error:
                        # TOOL_ERROR: Unexpected tool failure
                        logger.error(f"[ReAct] TOOL_ERROR: {action} - {tool_error}")
                        return f"Tool '{action}' failed unexpectedly. Continuing without it."
                else:
                    # Unknown tool - suggest alternatives
                    available_tools = self.get_available_tools()
                    logger.warning(f"[ReAct] Unknown tool: {action}. Available: {available_tools}")
                    return f"Tool '{action}' not found. Available tools: {', '.join(available_tools)}. I'll use my knowledge instead."
            else:
                # No tool registry - proceed with reasoning
                logger.info(f"[ReAct] No tool registry, using direct reasoning for: {action}")
                return f"Proceeding with direct reasoning for: {action}"
                
        except Exception as e:
            # Catch-all for any unexpected errors
            logger.error(f"[ReAct] ACT_ERROR: {e}", exc_info=True)
            return f"Action execution encountered an issue. Continuing with available information."
    
    async def _call_llm(self, system_prompt: str, user_message: str, model: Optional[str] = None) -> Optional[str]:
        """Call the LLM with the given prompts using services.llm_service
        
        Args:
            system_prompt: System prompt for the LLM
            user_message: User message/prompt
            model: Model to use (from cognitive routing). Falls back to settings.DEFAULT_LLM_MODEL
        """
        try:
            if not self.llm_key:
                logger.warning("No LLM key available")
                return None
            
            from services.llm_service import call_llm
            
            # Use model from cognitive routing (upstream decision)
            selected_model = self._resolve_model(model)
            
            # Build JSON-formatted prompt for ReAct reasoning
            json_instruction = """
Respond in valid JSON format with these fields:
{
  "thought": "Your reasoning about what to do next",
  "action": "TOOL_NAME or FINISH",
  "action_input": {"param": "value"} or {"answer": "your final answer"}
}"""
            
            full_prompt = f"{user_message}\n\n{json_instruction}"
            
            response = await call_llm(
                prompt=full_prompt,
                api_key=self.llm_key,
                temperature=0.3,  # Lower for more consistent reasoning
                max_tokens=1200,  # Cognitive path: room for JSON structure + reasoning + answer
                model=selected_model,
                system_message=system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's JSON response.
        
        CRITICAL: Never return raw JSON as the answer. If parsing fails,
        extract any meaningful text content or provide a graceful message.
        """
        import re
        
        # Clean the response first - remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith('```'):
            # Remove markdown code fences
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        
        # Try to parse as JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # ================================================================
        # CRITICAL FIX: Extract answer from malformed JSON
        # Never return raw JSON to the UI
        # ================================================================
        
        # Try to extract just the answer field from malformed JSON
        answer_match = re.search(r'"answer"\s*:\s*"([^"]*(?:"[^"]*"[^"]*)*)"', cleaned)
        if answer_match:
            extracted_answer = answer_match.group(1)
            # Clean up escaped characters
            extracted_answer = extracted_answer.replace('\\"', '"').replace('\\n', '\n')
            if len(extracted_answer) > 20:  # Reasonable answer length
                logger.info(f"[ReAct] Extracted answer from malformed JSON ({len(extracted_answer)} chars)")
                return {
                    "thought": "Extracted answer from partial response",
                    "action": "FINISH",
                    "action_input": {"answer": extracted_answer}
                }
        
        # Try to find clean text content (not JSON structure)
        # Remove JSON-like patterns to find actual content
        text_content = re.sub(r'\{[^{}]*"(?:thought|action|action_input)"[^{}]*\}', '', cleaned)
        text_content = re.sub(r'"(?:thought|action|action_input)":\s*', '', text_content)
        text_content = re.sub(r'[{}\[\]]', '', text_content)
        text_content = text_content.strip(' \n",:')
        
        if len(text_content) > 50:  # Found substantial text
            logger.info(f"[ReAct] Extracted text content from response ({len(text_content)} chars)")
            return {
                "thought": "Extracted text from response",
                "action": "FINISH",
                "action_input": {"answer": text_content}
            }
        
        # Final fallback - DO NOT return raw JSON
        # Instead, signal that we need to regenerate
        logger.warning("[ReAct] Could not parse LLM response, returning empty for retry")
        return {
            "thought": "Response parsing failed",
            "action": "FINISH",
            "action_input": {"answer": ""}  # Empty triggers regeneration
        }
    
    async def _generate_fallback_answer(self, state: AgentState) -> str:
        """
        Generate fallback answer when max iterations reached.
        
        PRINCIPLE: Failures reduce richness, NOT intelligence.
        - Use observations if available
        - Otherwise attempt LLM recovery
        - Never return static templates
        """
        # Summarize what we learned
        observations = [
            ta.observation for ta in state.reasoning_chain 
            if ta.observation and ta.observation != "Task complete"
        ]
        
        if observations:
            # We have real insights - synthesize them
            return f"""Based on my analysis:

{chr(10).join(observations[:3])}

I hope this helps! Let me know if you'd like me to explore further."""
        
        # No observations - attempt LLM recovery instead of static template
        logger.info("[ReAct] No observations gathered, attempting LLM recovery...")
        return await self._generate_direct_answer(state)
    
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """
        Format the final response.
        
        CRITICAL: This is the FINAL gate before content reaches the UI.
        Must ensure NO JSON or internal traces leak through.
        MUST NEVER return empty content - always provide a valid response.
        """
        import re
        
        # Fix escaped newlines in final answer (LLM returns \n as literal string)
        content = state.final_answer or ""
        if content:
            # Replace literal \n with actual newlines
            content = content.replace('\\n', '\n')
            # Also handle other common escape sequences
            content = content.replace('\\t', '\t')
            content = content.replace('\\"', '"')
        
        # ================================================================
        # FINAL SANITIZATION: Remove ANY JSON/ReAct traces from content
        # This is the LAST LINE OF DEFENSE before UI
        # ================================================================
        if content:
            # Remove JSON blocks that look like ReAct reasoning
            content = re.sub(
                r'\{\s*"(?:thought|action|action_input|confidence|observation)"[^}]*\}',
                '', content, flags=re.IGNORECASE | re.DOTALL
            )
            
            # Remove partial/incomplete JSON that starts with these patterns
            content = re.sub(r'^\s*\{\s*"(?:thought|action)"[^}]*$', '', content, flags=re.MULTILINE)
            
            # Remove lines that are just JSON keys
            content = re.sub(r'^\s*"(?:thought|action|action_input|confidence)":\s*.*$', '', content, flags=re.MULTILINE)
            
            # Remove stray JSON delimiters at start/end
            content = re.sub(r'^\s*[\{\[\]]+\s*', '', content)
            content = re.sub(r'\s*[\}\]\[]+\s*$', '', content)
            
            # Clean up excessive whitespace from removals
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()
        
        # ================================================================
        # CRITICAL: Log if content is unexpectedly empty
        # At this point, all recovery attempts should have been made
        # If still empty, pass through with warning (don't insert fake content)
        # ================================================================
        if not content or len(content.strip()) < 20:
            logger.error(f"[ReAct] CRITICAL: Empty content after all recovery attempts for: {state.query[:50]}...")
            # Provide minimal contextual response (not a menu)
            subject = state.context.get('subject', 'your question')
            content = f"I encountered an issue processing your question about {subject}. Please try again."
        
        # ================================================================
        # NEVER include reasoning_chain in the response sent to frontend
        # It's logged for observability but never exposed to student
        # ================================================================
        return {
            "success": True,
            "agent": self.get_agent_name(),
            "content": content,
            "confidence": state.confidence,
            # REMOVED: "reasoning_chain" - NEVER expose to student
            # Log it instead for observability
            "tools_used": state.tools_used,
            "iterations": state.iterations,
            "metadata": {
                "agent_type": "react",
                "duration_ms": (state.end_time - state.start_time).total_seconds() * 1000 if state.end_time else 0,
                "reasoning_steps": len(state.reasoning_chain)  # Just the count, not the content
            }
        }
    
    def _format_error_response(self, state: AgentState) -> Dict[str, Any]:
        """Format an error response - NEVER expose internal traces"""
        return {
            "success": False,
            "agent": self.get_agent_name(),
            "error": state.error,
            "content": "I encountered an issue processing your request. Please try again.",
            # REMOVED: "reasoning_chain" - NEVER expose to student
            "metadata": {
                "agent_type": "react",
                "error": True,
                "reasoning_steps": len(state.reasoning_chain)  # Just the count
            }
        }

