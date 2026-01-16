"""
🔧 Tool Registry - Managing Agent Tools
========================================

Tools are the "hands" of agents - they allow agents to interact
with the world beyond just generating text.

This module provides:
- BaseTool: Abstract base class for all tools
- ToolRegistry: Manages and provides access to tools
- ToolResult: Standardized result format

Examples of tools:
- Calculator: Perform mathematical calculations
- Search: Search knowledge base or web
- CodeExecutor: Run Python code safely
- ImageGenerator: Create visualizations
- FactChecker: Verify claims against trusted sources
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Status of a tool execution"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"


@dataclass
class ToolResult:
    """Standardized result from tool execution"""
    success: bool
    output: str
    status: ToolStatus = ToolStatus.SUCCESS
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, output: str, metadata: Dict = None) -> 'ToolResult':
        return cls(success=True, output=output, status=ToolStatus.SUCCESS, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, status: ToolStatus = ToolStatus.ERROR) -> 'ToolResult':
        return cls(success=False, output="", status=status, error=error)


class BaseTool(ABC):
    """
    Base class for all agent tools.
    
    Tools must implement:
    - name: Unique identifier for the tool
    - description: What the tool does (shown to LLM)
    - parameters: Expected parameters and their descriptions
    - execute(): The actual tool logic
    """
    
    def __init__(self):
        self._name = self.name
        self._description = self.description
        logger.info(f"🔧 Tool registered: {self.name}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the tool"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass
    
    @property
    def parameters(self) -> Dict[str, str]:
        """
        Parameters the tool accepts.
        Format: {"param_name": "description"}
        Override in subclass if tool has parameters.
        """
        return {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters + context
        
        Returns:
            ToolResult with output or error
        """
        pass
    
    def validate_params(self, **kwargs) -> Optional[str]:
        """
        Validate input parameters.
        Returns error message if invalid, None if valid.
        Override for custom validation.
        """
        required = [p for p, desc in self.parameters.items() if "required" in desc.lower()]
        for param in required:
            if param not in kwargs:
                return f"Missing required parameter: {param}"
        return None


class ToolRegistry:
    """
    Central registry for all available tools.
    
    Usage:
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        registry.register(SearchTool())
        
        tool = registry.get_tool("calculator")
        result = await tool.execute(expression="2+2")
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - one registry for the app"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._tools: Dict[str, BaseTool] = {}
            self._initialized = True
            logger.info("🗂️ ToolRegistry initialized")
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.info(f"  ├── Registered: {tool.name}")
    
    def register_many(self, tools: List[BaseTool]) -> None:
        """Register multiple tools"""
        for tool in tools:
            self.register(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names"""
        return list(self._tools.keys())
    
    def get_tools_description(self, tools: List[str] = None) -> str:
        """Get formatted description of tools for LLM prompts"""
        tool_list = tools or self.get_tool_names()
        descriptions = []
        
        for name in tool_list:
            tool = self.get_tool(name)
            if tool:
                desc = f"**{tool.name}**: {tool.description}"
                if tool.parameters:
                    params = ", ".join([f"{k}" for k in tool.parameters.keys()])
                    desc += f"\n  Parameters: {params}"
                descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    async def execute_tool(
        self, 
        name: str, 
        context: Dict[str, Any] = None,
        **kwargs
    ) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        
        if not tool:
            return ToolResult.error_result(
                f"Unknown tool: {name}",
                ToolStatus.INVALID_INPUT
            )
        
        # Validate parameters
        validation_error = tool.validate_params(**kwargs)
        if validation_error:
            return ToolResult.error_result(validation_error, ToolStatus.INVALID_INPUT)
        
        try:
            result = await tool.execute(context=context, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool {name} execution error: {e}")
            return ToolResult.error_result(str(e))


# ============================================
# Factory function for easy registry creation
# ============================================

def create_tool_registry(include_default: bool = True, include_action_tools: bool = True) -> ToolRegistry:
    """
    Create and configure a tool registry.
    
    Args:
        include_default: Whether to register default tools
        include_action_tools: Whether to register action tools (reminder, notification)
    
    Returns:
        Configured ToolRegistry
    """
    registry = ToolRegistry()
    
    if include_default:
        # Import and register default tools
        try:
            from agents.core.tools import (
                CalculatorTool,
                KnowledgeSearchTool,
                CodeExecutorTool,
                FactCheckerTool,
                FormulaLookupTool,
                WebSearchTool  # 🌐 Educational web search
            )
            
            registry.register_many([
                CalculatorTool(),
                KnowledgeSearchTool(),
                CodeExecutorTool(),
                FactCheckerTool(),
                FormulaLookupTool(),
                WebSearchTool()  # 🌐 DuckDuckGo educational search
            ])
            
        except ImportError as e:
            logger.warning(f"Could not import default tools: {e}")
    
    if include_action_tools:
        # Import and register ACTION tools (for true agentic behavior)
        try:
            from agents.core.tools.reminder_tool import ReminderTool
            from agents.core.tools.recurring_reminder_tool import RecurringReminderTool
            from agents.core.tools.notification_tool import NotificationTool, StudySummaryTool
            
            registry.register_many([
                ReminderTool(),
                RecurringReminderTool(),
                NotificationTool(),
                StudySummaryTool()
            ])
            
            logger.info("✅ Action tools registered (reminder, recurring_reminder, notification, summary)")
            
        except ImportError as e:
            logger.warning(f"Could not import action tools: {e}")
    
    return registry

