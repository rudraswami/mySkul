"""
🔧 Agent Tools - The "Hands" of Agents
======================================

This module contains all available tools that agents can use:

INFORMATION TOOLS (for answering questions):
- Calculator: Mathematical calculations
- KnowledgeSearch: Search concepts and formulas
- CodeExecutor: Run Python code safely
- FactChecker: Verify claims
- FormulaLookup: Find relevant formulas

ACTION TOOLS (for taking real actions - TRUE AGENTIC BEHAVIOR):
- ReminderTool: Schedule one-time reminders
- RecurringReminderTool: Schedule daily/weekly recurring reminders
- NotificationTool: Send real notifications to users
- StudySummaryTool: Generate and send study summaries
"""

from .calculator import CalculatorTool
from .knowledge_search import KnowledgeSearchTool
from .code_executor import CodeExecutorTool
from .fact_checker import FactCheckerTool
from .formula_lookup import FormulaLookupTool

# Action tools for true agentic behavior
from .reminder_tool import ReminderTool
from .recurring_reminder_tool import RecurringReminderTool
from .notification_tool import NotificationTool, StudySummaryTool
from .base_tool import BaseTool, ToolResult

__all__ = [
    # Base
    'BaseTool',
    'ToolResult',
    # Information tools
    'CalculatorTool',
    'KnowledgeSearchTool',
    'CodeExecutorTool',
    'FactCheckerTool',
    'FormulaLookupTool',
    # Action tools
    'ReminderTool',
    'RecurringReminderTool',
    'NotificationTool',
    'StudySummaryTool',
]

