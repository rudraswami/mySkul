"""
Agents Package for AI Sathi - Cognito OS v3.0
=============================================

🧠 TRUE AGENTIC SYSTEM:
All agents use ReAct loop (Think → Act → Observe) with tools, memory, and verification.

CORE AGENTS:
- MentorAgent: Emotional, intuitive explanations (TRUE AGENTIC with ReAct)
- ProfessorAgent: Formal, structured academic explanations (TRUE AGENTIC)
- VisualiseAgent: Visual/diagram generation (disabled for v1)

SPECIALIZED AGENTS (ALL TRUE AGENTIC):
- AgenticDoubtResolver: Empathetic doubt clearing with tools + memory
- ExamCoachAgent: Strategic exam preparation with data analysis
- WeakAreaDetectiveAgent: Knowledge gap detection from real data
- StudyBuddyAgent: Peer learning companion
- ParentReportAgent: Guardian communication with insights
- AgenticCompanion: 24/7 learning partner with action capabilities
- MotivationAgent: Emotional support middleware

ORCHESTRATION:
- SupervisorAgent: Routes queries to appropriate agents
- EnhancedSupervisor: Adds neuro-symbolic verification + agent negotiation

ARCHIVED (DO NOT USE):
- doubt_resolver.py → Use AgenticDoubtResolver
- error_dom.py → Never integrated
- proactive_companion.py → Use AgenticCompanion
"""
from agents.base_agent import BaseAgent
from agents.mentor import MentorAgent
from agents.professor import ProfessorAgent
from agents.visualise import VisualiseAgent
from agents.supervisor import SupervisorAgent
from agents.response_adapter import ResponseAdapter
from agents.enhanced_supervisor import EnhancedSupervisor, create_enhanced_supervisor

# Specialized agents for Cognito OS
# NOTE: doubt_resolver.py ARCHIVED - AgenticDoubtResolver is the canonical implementation
from agents.agentic_doubt_resolver import AgenticDoubtResolver as DoubtResolverAgent  # Alias for compatibility
from agents.motivation import MotivationAgent

# Compatibility functions - delegate to AgenticDoubtResolver
def is_doubt_query(query: str) -> bool:
    """Compatibility wrapper - delegates to AgenticDoubtResolver.is_doubt_query"""
    return AgenticDoubtResolver.is_doubt_query(query)

def is_deep_reasoning_query(query: str) -> bool:
    """Compatibility wrapper - checks if query requires deep reasoning"""
    query_lower = query.lower()
    deep_patterns = ['derive', 'prove', 'proof', 'why does', 'step by step', 'analyze', 'evaluate']
    return any(p in query_lower for p in deep_patterns)
from agents.exam_coach import ExamCoachAgent
from agents.weak_area_detective import WeakAreaDetectiveAgent
from agents.study_buddy import StudyBuddyAgent
from agents.parent_report import ParentReportAgent
# from agents.proactive_companion import ProactiveCompanionAgent  # ARCHIVED - use AgenticCompanion instead

# New intelligent base class
from agents.intelligent_agent_base import IntelligentAgentBase

# 🧠 True Agentic System Components
from agents.agentic_doubt_resolver import AgenticDoubtResolver, create_agentic_doubt_resolver
# Note: DoubtResolverAgent is an alias for AgenticDoubtResolver (imported above)
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
    # Base Classes
    'BaseAgent',
    'IntelligentAgentBase',
    'ReActAgent',
    
    # Core Agents (TRUE AGENTIC)
    'MentorAgent',
    'ProfessorAgent',
    'VisualiseAgent',
    
    # Specialized Agents (TRUE AGENTIC)
    'AgenticDoubtResolver',
    'DoubtResolverAgent',  # Alias for AgenticDoubtResolver (compatibility)
    'is_doubt_query',
    'is_deep_reasoning_query',
    'MotivationAgent',
    'ExamCoachAgent',
    'WeakAreaDetectiveAgent',
    'StudyBuddyAgent',
    'ParentReportAgent',
    'AgenticCompanion',
    
    # Factory Functions
    'create_agentic_doubt_resolver',
    'create_agentic_companion',
    'process_reminder_request',
    'create_tool_registry',
    'create_enhanced_supervisor',
    
    # Agentic Infrastructure
    'AgentState',
    'ThoughtAction',
    'ToolRegistry',
    'BaseTool',
    'ToolResult',
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
    'EnhancedSupervisor',
    'ResponseAdapter',
]

