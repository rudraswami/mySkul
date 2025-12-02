"""
💻 Code Executor Tool - Safe Python Execution
==============================================

Safely executes Python code for calculations and demonstrations.
Uses restricted execution environment to prevent security issues.
"""

import logging
import ast
import math
import numpy as np
from typing import Dict, Any
from io import StringIO
import sys
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class CodeExecutorTool(BaseTool):
    """
    Safely execute Python code snippets.
    
    Restricted to mathematical and educational operations.
    """
    
    # Allowed modules and functions
    SAFE_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
        'float', 'int', 'len', 'list', 'map', 'max', 'min', 'pow',
        'print', 'range', 'reversed', 'round', 'set', 'sorted', 
        'str', 'sum', 'tuple', 'zip', 'True', 'False', 'None'
    }
    
    # Blocked operations (Note: ast.Exec doesn't exist in Python 3)
    BLOCKED_NODES = {
        ast.Import, ast.ImportFrom,
        ast.Delete, ast.Global, ast.Nonlocal
    }
    
    @property
    def name(self) -> str:
        return "code_executor"
    
    @property
    def description(self) -> str:
        return "Executes Python code safely for calculations, demonstrations, or verifying mathematical solutions. Use for complex calculations that need step-by-step computation."
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "code": "Python code to execute (mathematical/educational operations only)"
        }
    
    async def execute(self, code: str = "", context: Dict = None, **kwargs) -> ToolResult:
        """
        Safely execute Python code
        """
        if not code:
            return ToolResult.error_result("No code provided")
        
        # Validate code safety
        safety_check = self._validate_code(code)
        if safety_check:
            return ToolResult.error_result(f"Unsafe code: {safety_check}")
        
        try:
            # Create restricted environment
            safe_globals = self._create_safe_globals()
            
            # Capture output
            output_buffer = StringIO()
            old_stdout = sys.stdout
            sys.stdout = output_buffer
            
            try:
                # Execute code
                exec(code, safe_globals)
                
                # Get printed output
                printed_output = output_buffer.getvalue()
                
                # Get result variable if exists
                result = safe_globals.get('result', None)
                
                if printed_output:
                    output = f"**Output**:\n```\n{printed_output.strip()}\n```"
                elif result is not None:
                    output = f"**Result**: {result}"
                else:
                    output = "Code executed successfully (no output)"
                
                logger.info(f"💻 Code executed successfully")
                
                return ToolResult.success_result(
                    output,
                    metadata={"code": code[:100], "has_result": result is not None}
                )
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return ToolResult.error_result(f"Execution error: {str(e)}")
    
    def _validate_code(self, code: str) -> str:
        """
        Validate code for safety. Returns error message if unsafe, None if safe.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"Syntax error: {e}"
        
        for node in ast.walk(tree):
            # Check for blocked node types
            if type(node) in self.BLOCKED_NODES:
                return f"Blocked operation: {type(node).__name__}"
            
            # Check for attribute access to dangerous modules
            if isinstance(node, ast.Attribute):
                if node.attr in ['__class__', '__bases__', '__subclasses__', '__mro__']:
                    return f"Blocked attribute: {node.attr}"
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', 'open', '__import__']:
                        return f"Blocked function: {node.func.id}"
        
        return None
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a restricted execution environment"""
        safe_builtins = {k: getattr(__builtins__, k) if hasattr(__builtins__, k) else None 
                        for k in self.SAFE_BUILTINS}
        
        # Filter None values
        safe_builtins = {k: v for k, v in safe_builtins.items() if v is not None}
        
        return {
            '__builtins__': safe_builtins,
            'math': math,
            'np': np,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
            # Common numpy functions
            'array': np.array,
            'zeros': np.zeros,
            'ones': np.ones,
            'linspace': np.linspace,
            'arange': np.arange,
        }

