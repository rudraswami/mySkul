"""
🔧 Base Tool - Foundation for All Agent Tools
=============================================

This defines the interface that all tools must implement.
Tools are the "hands" of agents - they enable agents to
take real actions in the world.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class ToolResult:
    """Result of a tool execution"""
    success: bool
    output: str  # Human-readable output for the agent
    data: Optional[Dict[str, Any]] = None  # Structured data
    error: Optional[str] = None  # Error message if failed
    execution_time_ms: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'output': self.output,
            'data': self.data,
            'error': self.error,
            'execution_time_ms': self.execution_time_ms,
            'timestamp': self.timestamp.isoformat()
        }


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.
    
    Every tool must define:
    - name: Unique identifier for the tool
    - description: What the tool does (used by agent to decide when to use it)
    - parameters: What inputs the tool needs
    - execute(): The actual implementation
    """
    
    name: str = "base_tool"
    description: str = "Base tool - override this"
    parameters: Dict[str, str] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters + context
        
        Returns:
            ToolResult with success status and output
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM function calling"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': {
                'type': 'object',
                'properties': {
                    param: {'type': 'string', 'description': desc}
                    for param, desc in self.parameters.items()
                },
                'required': list(self.parameters.keys())
            }
        }
    
    def __repr__(self) -> str:
        return f"<Tool:{self.name}>"





