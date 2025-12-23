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
    DEFAULT_GLOBAL_TIMEOUT = 45.0  # Increased from 25s for deeper reasoning
    
    # Adaptive iteration limits based on complexity
    ITERATION_LIMITS = {
        'trivial': 3,
        'simple': 5,
        'moderate': 8,
        'complex': 12,
        'deep': 15,  # For proofs, derivations, multi-step problems
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
        
        logger.info(f"🤖 {self.get_agent_name()} initialized (ReAct mode, timeout={self.global_timeout}s)")
    
    def _get_adaptive_iterations(self, query: str, context: Dict[str, Any]) -> int:
        """
        Dynamically determine max iterations based on query complexity.
        
        Deep reasoning queries get more iterations.
        Simple queries get fewer to save time.
        """
        import re
        query_lower = query.lower()
        word_count = len(query.split())
        
        # DEEP complexity indicators
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
        
        # Default to moderate
        logger.info("📊 Query complexity: DEFAULT/MODERATE")
        return self.ITERATION_LIMITS['moderate']
    
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

## REASONING SO FAR
{state.get_reasoning_summary()}
"""
    
    def _get_tools_description(self, context: dict = None) -> str:
        """Get descriptions of all available tools"""
        if not self.tool_registry:
            return "No tools available."
        
        # COGNITIVE OS FIX: Pass context to get_available_tools
        try:
            available = self.get_available_tools(context)
        except TypeError:
            # Backward compatibility: some agents don't accept context param
            available = self.get_available_tools()
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
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point - runs the ReAct loop until completion.
        
        TIMEOUT PROTECTION:
        - Wrapped in global timeout (default 25s)
        - On timeout, returns graceful fallback response
        - Never leaves student waiting indefinitely
        
        Args:
            query: The student's question
            context: Context dict with subject, user_id, etc.
        
        Returns:
            Agent response with reasoning chain and final answer
        """
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
        
        try:
            logger.info(f"[ReAct] Starting loop for {self.get_agent_name()}: max_iter={adaptive_max}")
            
            # Run the ReAct loop
            while state.iterations < state.max_iterations:
                state.iterations += 1
                step_start = datetime.now()
                
                # THINK: Generate next thought/action
                state.status = AgentStatus.THINKING
                logger.info(f"[ReAct] Step {state.iterations}/{adaptive_max}: THINKING...")
                
                thought_action = await self._think(state)
                
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
                
                # ACT: Execute the chosen tool
                state.status = AgentStatus.ACTING
                logger.info(f"[ReAct] Step {state.iterations}: ACTING with {thought_action.action}")
                
                observation = await self._act(thought_action, state)
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
        Generate a helpful fallback response when ReAct loop times out.
        
        Never leave the student with no response!
        """
        subject = context.get('subject', 'your question')
        short_query = query[:80] + "..." if len(query) > 80 else query
        
        # CRITICAL: Natural continuation, NO capability menus, NO numbered options
        fallback_content = f"""That's a thoughtful question about {subject}! 🤔

I want to give you a really good answer to "{short_query}"

Let me think about the clearest way to explain this. What's the specific part that's confusing you most? That way I can focus on exactly what you need."""
        
        logger.info(f"⏰ Generated timeout fallback for: {query[:50]}...")
        
        return {
            "success": True,  # Still successful - we provided a response
            "agent": self.get_agent_name(),
            "content": fallback_content,
            "confidence": 0.4,
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
        """
        subject = context.get('subject', 'your question')
        
        fallback_content = f"""I encountered a small hiccup while processing your question about {subject}! 😅

Don't worry - let me try a different approach:

**What you asked:** {query[:80]}{'...' if len(query) > 80 else ''}

Could you try:
1. **Rephrasing your question** slightly differently?
2. **Asking about one concept at a time** if it's multi-part?

I'm here to help you understand! 📚"""
        
        logger.warning(f"❌ Generated error fallback for: {query[:50]}... (error: {error[:50]})")
        
        return {
            "success": False,
            "agent": self.get_agent_name(),
            "content": fallback_content,
            "error": error,
            "confidence": 0.3,
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
        
        FAULT-TOLERANT: Retries on transient failures, distinguishes failure types.
        """
        MAX_RETRIES = 2
        last_error = None
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                system_prompt = self.get_system_prompt(state)
                user_message = f"What should you do next to answer: {state.query}"
                
                # If we have previous observations, include them
                if state.reasoning_chain and state.reasoning_chain[-1].observation:
                    last = state.reasoning_chain[-1]
                    user_message = f"""Based on the observation from {last.action}:
{last.observation}

What should you do next?"""
                
                # Call LLM with retry awareness
                response = await self._call_llm(system_prompt, user_message)
                
                if not response:
                    # MODEL_FAILURE: LLM returned nothing
                    last_error = "MODEL_FAILURE: LLM returned empty response"
                    if attempt < MAX_RETRIES:
                        logger.warning(f"[ReAct] LLM empty response, retry {attempt + 1}/{MAX_RETRIES}")
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        # After retries, generate a FINISH action to complete gracefully
                        logger.warning("[ReAct] LLM failed after retries, generating direct answer")
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
                last_error = f"REASONING_FAILURE: {str(e)}"
                logger.error(f"[ReAct] Think error (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
        
        # All retries exhausted - generate graceful FINISH
        logger.error(f"[ReAct] Think failed after all retries: {last_error}")
        ta = state.add_thought("Let me provide you with a helpful response.")
        ta.action = "FINISH"
        ta.action_input = {"answer": await self._generate_direct_answer(state)}
        return ta
    
    async def _generate_direct_answer(self, state: AgentState) -> str:
        """
        Generate a direct answer when ReAct reasoning fails.
        This is NOT a fallback to skip reasoning - it's error recovery
        that still uses LLM intelligence.
        """
        try:
            from services.llm_service import call_llm
            
            # Build context from any observations we've gathered
            observations = [ta.observation for ta in state.reasoning_chain if ta.observation]
            context_str = "\n".join(observations[-3:]) if observations else "No prior context."
            
            prompt = f"""You are a knowledgeable mentor. Answer this question directly:

Question: {state.query}

Context from analysis: {context_str}

Provide a clear, helpful, well-structured answer."""
            
            response = await call_llm(
                prompt=prompt,
                api_key=self.llm_key,
                temperature=0.7,
                max_tokens=1000,
                model="gpt-4o-mini",
                system_message=self.get_agent_persona()
            )
            return response if response else "I understand your question. Could you provide more details so I can give you a thorough explanation?"
        except Exception as e:
            logger.error(f"[ReAct] Direct answer generation failed: {e}")
            return f"I'm analyzing your question about {state.context.get('subject', 'this topic')}. Could you tell me more about what specific aspect you'd like me to explain?"
    
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
    
    async def _call_llm(self, system_prompt: str, user_message: str) -> Optional[str]:
        """Call the LLM with the given prompts using services.llm_service"""
        try:
            if not self.llm_key:
                logger.warning("No LLM key available")
                return None
            
            from services.llm_service import call_llm
            
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
                max_tokens=800,
                model="gpt-4o-mini",
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
        """Generate a fallback answer when max iterations reached"""
        # Summarize what we learned
        observations = [
            ta.observation for ta in state.reasoning_chain 
            if ta.observation and ta.observation != "Task complete"
        ]
        
        if observations:
            return f"""Based on my analysis:

{chr(10).join(observations[:3])}

I hope this helps! Let me know if you'd like me to explore further."""
        
        return "I apologize, but I need more information to fully answer your question. Could you please clarify or rephrase?"
    
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """
        Format the final response.
        
        CRITICAL: This is the FINAL gate before content reaches the UI.
        Must ensure NO JSON or internal traces leak through.
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

