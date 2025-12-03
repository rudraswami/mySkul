"""
Agents Package for Druv AI Agentic Architecture (Cognito OS)

AGENT ECOSYSTEM:
================

CORE AGENTS:
- MentorAgent: Emotional, intuitive explanations with metaphors
- ProfessorAgent: Formal, structured academic explanations
- VisualiseAgent: Visual/diagram generation

SPECIALIZED AGENTS:
- DoubtResolverAgent: Quick, empathetic doubt clearing
- MotivationAgent: Emotional support middleware (detects burnout, frustration, anxiety)

🧠 TRUE AGENTIC SYSTEM (NEW):
- AgenticDoubtResolver: Full ReAct loop with tools, memory, planning, verification
- ReActAgent: Think → Act → Observe reasoning loop
- ToolRegistry: Tool management (calculator, search, fact-check, etc.)
- MemorySystem: Short-term + Long-term student memory
- Planner: Task decomposition for complex queries
- Verifier: Self-verification of calculations and facts

ORCHESTRATION:
- SupervisorAgent: Routes queries to appropriate agents
- EnhancedSupervisor: Adds neuro-symbolic verification (RAG + symbolic math)

INTEGRATION:
- ResponseAdapter: Formats multi-agent responses uniformly
"""
from agents.base_agent import BaseAgent
from agents.mentor import MentorAgent
from agents.professor import ProfessorAgent
from agents.visualise import VisualiseAgent
from agents.supervisor import SupervisorAgent
from agents.response_adapter import ResponseAdapter
from agents.enhanced_supervisor import EnhancedSupervisor, create_enhanced_supervisor

# Specialized agents for Cognito OS
from agents.doubt_resolver import DoubtResolverAgent, is_doubt_query, is_deep_reasoning_query  # Compatibility layer
from agents.motivation import MotivationAgent
from agents.exam_coach import ExamCoachAgent
from agents.weak_area_detective import WeakAreaDetectiveAgent
from agents.study_buddy import StudyBuddyAgent
from agents.parent_report import ParentReportAgent
# from agents.proactive_companion import ProactiveCompanionAgent  # ARCHIVED - use AgenticCompanion instead

# New intelligent base class
from agents.intelligent_agent_base import IntelligentAgentBase

# 🧠 True Agentic System Components
from agents.agentic_doubt_resolver import AgenticDoubtResolver, create_agentic_doubt_resolver
from agents.agentic_companion import AgenticCompanion, create_agentic_companion, process_reminder_request
from agents.core import (
    ReActAgent,
    AgentState,
    ThoughtAction,
    ToolRegistry,
    BaseTool,
    ToolResult,
    create_tool_registry,
    MemorySystem,
    ShortTermMemory,
    LongTermMemory,
    Planner,
    TaskPlan,
    SubTask,
    Verifier,
    VerificationResult
)

__all__ = [
    # Base
    'BaseAgent',
    'IntelligentAgentBase',
    
    # Core Agents
    'MentorAgent',
    'ProfessorAgent',
    'VisualiseAgent',
    
    # Specialized Agents (Cognito OS)
    'DoubtResolverAgent',  # Compatibility layer - uses restrictive is_doubt_query
    'is_doubt_query',
    'is_deep_reasoning_query',
    'MotivationAgent',
    'ExamCoachAgent',
    'WeakAreaDetectiveAgent',
    'StudyBuddyAgent',
    'ParentReportAgent',
    # 'ProactiveCompanionAgent',  # ARCHIVED - use AgenticCompanion instead
    
    # 🧠 True Agentic System
    'AgenticDoubtResolver',
    'create_agentic_doubt_resolver',
    'AgenticCompanion',
    'create_agentic_companion',
    'process_reminder_request',
    'ReActAgent',
    'AgentState',
    'ThoughtAction',
    'ToolRegistry',
    'BaseTool',
    'ToolResult',
    'create_tool_registry',
    'MemorySystem',
    'ShortTermMemory',
    'LongTermMemory',
    'Planner',
    'TaskPlan',
    'SubTask',
    'Verifier',
    'VerificationResult',
    
    # Orchestration
    'SupervisorAgent',
    'ResponseAdapter',
    
    # Enhanced (Neuro-Symbolic)
    'EnhancedSupervisor',
    'create_enhanced_supervisor'
]

