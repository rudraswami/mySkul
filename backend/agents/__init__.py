"""
Agents Package for Druv AI Agentic Architecture

Includes:
- Base agents: Mentor, Professor, Visualise
- Supervisor: Orchestrates multi-agent responses
- EnhancedSupervisor: Adds neuro-symbolic verification (RAG + symbolic math)
"""
from agents.base_agent import BaseAgent
from agents.mentor import MentorAgent
from agents.professor import ProfessorAgent
from agents.visualise import VisualiseAgent
from agents.supervisor import SupervisorAgent
from agents.response_adapter import ResponseAdapter
from agents.enhanced_supervisor import EnhancedSupervisor, create_enhanced_supervisor

__all__ = [
    'BaseAgent',
    'MentorAgent',
    'ProfessorAgent',
    'VisualiseAgent',
    'SupervisorAgent',
    'ResponseAdapter',
    # Enhanced (Neuro-Symbolic)
    'EnhancedSupervisor',
    'create_enhanced_supervisor'
]

