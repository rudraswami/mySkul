"""
Base Agent Class for Druv AI Agentic Architecture
All specialized agents (Mentor, Professor, Visualise, ErrorDom) inherit from this
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the Druv AI system
    
    All agents must implement:
    - process(): Main processing logic
    - get_agent_type(): Returns agent type identifier
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent
        
        Args:
            config: Agent configuration dict (e.g., API keys, settings)
        """
        self.config = config or {}
        self.emergent_llm_key = self.config.get('emergent_llm_key')
        self.agent_type = self.get_agent_type()
        logger.info(f"✅ {self.agent_type} initialized")
    
    @abstractmethod
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a query and return agent-specific response
        
        Args:
            query: The student's question or request
            context: Context dict with subject, user_id, session_id, etc.
        
        Returns:
            Dict with agent response
        """
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the agent type identifier"""
        pass
    
    def _should_process(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Determine if this agent should process the query
        Override in specialized agents for custom logic
        
        Returns:
            True if agent should process, False otherwise
        """
        return True
    
    def _format_response(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format agent response in standard structure
        
        Args:
            content: Main response content
            metadata: Additional metadata
        
        Returns:
            Formatted response dict
        """
        return {
            'agent': self.agent_type,
            'content': content,
            'metadata': metadata or {},
            'success': True
        }
    
    def _format_error(self, error_message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'agent': self.agent_type,
            'error': error_message,
            'success': False
        }

