"""
🧠 DRUV AI - True Agentic Core
================================

This module contains the foundational components for building
truly agentic AI systems that behave like humans.

Architecture:
- ReActAgent: Think → Act → Observe reasoning loop
- ToolRegistry: Manages available tools for agents
- MemorySystem: Short-term and long-term memory
- Planner: Task decomposition and planning
- Verifier: Self-checking and fact verification

Philosophy:
"An agent is not just an LLM wrapper - it's a reasoning system
that can plan, use tools, remember, learn, and self-correct."

Usage Example:
    from agents.core import ReActAgent, ToolRegistry, MemorySystem
    
    class MyAgent(ReActAgent):
        def get_agent_name(self): return "MyAgent"
        def get_agent_persona(self): return "You are a helpful assistant..."
        def get_available_tools(self): return ["calculator", "knowledge_search"]
    
    agent = MyAgent(config)
    response = await agent.run(query, context)
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'ReActAgent':
        from .react_agent import ReActAgent
        return ReActAgent
    elif name == 'AgentState':
        from .react_agent import AgentState
        return AgentState
    elif name == 'ThoughtAction':
        from .react_agent import ThoughtAction
        return ThoughtAction
    elif name == 'ToolRegistry':
        from .tool_registry import ToolRegistry
        return ToolRegistry
    elif name == 'BaseTool':
        from .tool_registry import BaseTool
        return BaseTool
    elif name == 'ToolResult':
        from .tool_registry import ToolResult
        return ToolResult
    elif name == 'create_tool_registry':
        from .tool_registry import create_tool_registry
        return create_tool_registry
    elif name == 'MemorySystem':
        from .memory import MemorySystem
        return MemorySystem
    elif name == 'ShortTermMemory':
        from .memory import ShortTermMemory
        return ShortTermMemory
    elif name == 'LongTermMemory':
        from .memory import LongTermMemory
        return LongTermMemory
    elif name == 'MemoryItem':
        from .memory import MemoryItem
        return MemoryItem
    elif name == 'Planner':
        from .planner import Planner
        return Planner
    elif name == 'TaskPlan':
        from .planner import TaskPlan
        return TaskPlan
    elif name == 'SubTask':
        from .planner import SubTask
        return SubTask
    elif name == 'Verifier':
        from .verifier import Verifier
        return Verifier
    elif name == 'VerificationResult':
        from .verifier import VerificationResult
        return VerificationResult
    elif name == 'VerificationStatus':
        from .verifier import VerificationStatus
        return VerificationStatus
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Core Agent
    'ReActAgent',
    'AgentState', 
    'ThoughtAction',
    
    # Tools
    'ToolRegistry',
    'BaseTool',
    'ToolResult',
    'create_tool_registry',
    
    # Memory
    'MemorySystem',
    'ShortTermMemory',
    'LongTermMemory',
    'MemoryItem',
    
    # Planning
    'Planner',
    'TaskPlan',
    'SubTask',
    
    # Verification
    'Verifier',
    'VerificationResult',
    'VerificationStatus'
]

