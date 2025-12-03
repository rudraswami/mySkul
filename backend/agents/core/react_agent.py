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
    DEFAULT_GLOBAL_TIMEOUT = 25.0
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.llm_key = self.config.get('emergent_llm_key') or os.environ.get('EMERGENT_LLM_KEY')
        self.tool_registry = None  # Set by subclass or injected
        self.memory = None  # Set by subclass or injected
        self.max_iterations = self.config.get('max_iterations', 10)
        self.verbose = self.config.get('verbose', True)
        
        # Global timeout for entire ReAct loop (configurable)
        self.global_timeout = self.config.get('global_timeout', self.DEFAULT_GLOBAL_TIMEOUT)
        
        logger.info(f"🤖 {self.get_agent_name()} initialized (ReAct mode, timeout={self.global_timeout}s)")
    
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
        tools_desc = self._get_tools_description()
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
    
    def _get_tools_description(self) -> str:
        """Get descriptions of all available tools"""
        if not self.tool_registry:
            return "No tools available."
        
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
        Internal ReAct loop - separated for timeout wrapping.
        """
        # Initialize state
        state = AgentState(
            query=query,
            context=context,
            max_iterations=self.max_iterations
        )
        
        try:
            # Run the ReAct loop
            while state.iterations < state.max_iterations:
                state.iterations += 1
                
                # THINK: Generate next thought/action
                state.status = AgentStatus.THINKING
                thought_action = await self._think(state)
                
                if not thought_action:
                    state.error = "Failed to generate thought"
                    break
                
                # Check if we should finish
                if thought_action.action == "FINISH":
                    state.status = AgentStatus.COMPLETE
                    state.final_answer = thought_action.action_input.get("answer", thought_action.thought)
                    state.confidence = thought_action.action_input.get("confidence", 0.8)
                    break
                
                # ACT: Execute the chosen tool
                state.status = AgentStatus.ACTING
                observation = await self._act(thought_action, state)
                thought_action.observation = observation
                
                # OBSERVE: Process the result (handled implicitly in next iteration)
                state.status = AgentStatus.OBSERVING
                
                if self.verbose:
                    logger.info(f"  Step {state.iterations}: {thought_action.action} → {observation[:100]}...")
            
            # Check if we hit max iterations
            if state.iterations >= state.max_iterations and state.status != AgentStatus.COMPLETE:
                logger.warning(f"⚠️ {self.get_agent_name()} hit max iterations")
                state.status = AgentStatus.COMPLETE
                state.final_answer = await self._generate_fallback_answer(state)
                state.confidence = 0.5
            
            state.end_time = datetime.now()
            
            return self._format_response(state)
            
        except Exception as e:
            logger.error(f"❌ {self.get_agent_name()} loop error: {e}", exc_info=True)
            state.status = AgentStatus.ERROR
            state.error = str(e)
            state.end_time = datetime.now()
            return self._format_error_response(state)
    
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
        
        fallback_content = f"""I'm working on a thorough answer to your question about {subject}, but it's taking longer than expected! 🤔

Let me give you a quick response while I process:

**Your question:** {query[:100]}{'...' if len(query) > 100 else ''}

For now, here's what I can tell you:
- This is a great question that deserves a detailed answer
- Try breaking it down into smaller parts if it's complex
- Feel free to ask a simpler version, and I'll build from there!

Would you like me to:
1. **Try again** with a simpler explanation?
2. **Focus on one specific part** of your question?
3. **Give you a quick summary** instead?

Just let me know! 📚"""
        
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
        """Generate the next thought and action using LLM"""
        try:
            system_prompt = self.get_system_prompt(state)
            user_message = f"What should you do next to answer: {state.query}"
            
            # If we have previous observations, include them
            if state.reasoning_chain and state.reasoning_chain[-1].observation:
                last = state.reasoning_chain[-1]
                user_message = f"""Based on the observation from {last.action}:
{last.observation}

What should you do next?"""
            
            # Call LLM
            response = await self._call_llm(system_prompt, user_message)
            
            if not response:
                return None
            
            # Parse response
            parsed = self._parse_llm_response(response)
            
            # Create thought action
            ta = state.add_thought(parsed.get("thought", "Thinking..."))
            ta.action = parsed.get("action", "FINISH")
            ta.action_input = parsed.get("action_input", {})
            
            return ta
            
        except Exception as e:
            logger.error(f"Think error: {e}")
            return None
    
    async def _act(self, thought_action: ThoughtAction, state: AgentState) -> str:
        """Execute the chosen action/tool"""
        action = thought_action.action
        action_input = thought_action.action_input or {}
        
        if action == "FINISH":
            return "Task complete"
        
        # Execute tool
        if self.tool_registry:
            tool = self.tool_registry.get_tool(action)
            if tool:
                state.tools_used.append(action)
                result = await tool.execute(**action_input, context=state.context)
                return result.output if result.success else f"Error: {result.error}"
        
        return f"Unknown action: {action}"
    
    async def _call_llm(self, system_prompt: str, user_message: str) -> Optional[str]:
        """Call the LLM with the given prompts"""
        try:
            if not self.llm_key:
                logger.warning("No LLM key available")
                return None
            
            from services.llm_service import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=self.llm_key,
                session_id=f"react_{self.get_agent_name()}_{datetime.now().timestamp()}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.3,  # Lower for more consistent reasoning
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            response = await chat.send_message(UserMessage(text=user_message))
            return response
            
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's JSON response"""
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Fallback
            return {
                "thought": response,
                "action": "FINISH",
                "action_input": {"answer": response}
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
        """Format the final response"""
        return {
            "success": True,
            "agent": self.get_agent_name(),
            "content": state.final_answer,
            "confidence": state.confidence,
            "reasoning_chain": [ta.to_dict() for ta in state.reasoning_chain],
            "tools_used": state.tools_used,
            "iterations": state.iterations,
            "metadata": {
                "agent_type": "react",
                "duration_ms": (state.end_time - state.start_time).total_seconds() * 1000 if state.end_time else 0
            }
        }
    
    def _format_error_response(self, state: AgentState) -> Dict[str, Any]:
        """Format an error response"""
        return {
            "success": False,
            "agent": self.get_agent_name(),
            "error": state.error,
            "content": "I encountered an issue processing your request. Please try again.",
            "reasoning_chain": [ta.to_dict() for ta in state.reasoning_chain],
            "metadata": {
                "agent_type": "react",
                "error": True
            }
        }

