"""
Agents Package for Druv AI Agentic Architecture (Cognito OS)

AGENT ECOSYSTEM:
================

CORE AGENTS:
- MentorAgent: Emotional, intuitive explanations with metaphors
- ProfessorAgent: Formal, structured academic explanations
- VisualiseAgent: Visual/diagram generation

SPECIALIZED AGENTS (NEW):
- DoubtResolverAgent: Quick, empathetic doubt clearing
- MotivationAgent: Emotional support middleware (detects burnout, frustration, anxiety)

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
from agents.doubt_resolver import DoubtResolverAgent
from agents.motivation import MotivationAgent
from agents.exam_coach import ExamCoachAgent
from agents.weak_area_detective import WeakAreaDetectiveAgent
from agents.study_buddy import StudyBuddyAgent
from agents.parent_report import ParentReportAgent

# New intelligent base class
from agents.intelligent_agent_base import IntelligentAgentBase

__all__ = [
    # Base
    'BaseAgent',
    'IntelligentAgentBase',
    
    # Core Agents
    'MentorAgent',
    'ProfessorAgent',
    'VisualiseAgent',
    
    # Specialized Agents (Cognito OS)
    'DoubtResolverAgent',
    'MotivationAgent',
    'ExamCoachAgent',
    'WeakAreaDetectiveAgent',
    'StudyBuddyAgent',
    'ParentReportAgent',
    
    # Orchestration
    'SupervisorAgent',
    'ResponseAdapter',
    
    # Enhanced (Neuro-Symbolic)
    'EnhancedSupervisor',
    'create_enhanced_supervisor'
]

