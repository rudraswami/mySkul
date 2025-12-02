"""
🧮 Calculator Tool - Mathematical Computations
===============================================

Safely evaluates mathematical expressions.
Supports: basic arithmetic, powers, roots, trigonometry, logarithms.
"""

import math
import logging
from typing import Dict, Any, Optional
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class CalculatorTool(BaseTool):
    """
    Calculator tool for mathematical computations.
    
    Safely evaluates expressions using Python's math library.
    """
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Performs mathematical calculations. Use for any arithmetic, algebra, trigonometry, or calculus computations. Input should be a valid mathematical expression."
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "expression": "Mathematical expression to evaluate (e.g., '2+2', 'sqrt(16)', 'sin(pi/2)')"
        }
    
    async def execute(self, expression: str = "", context: Dict = None, **kwargs) -> ToolResult:
        """
        Execute mathematical calculation
        
        Args:
            expression: Math expression to evaluate
        
        Returns:
            ToolResult with calculated value
        """
        if not expression:
            return ToolResult.error_result("No expression provided")
        
        try:
            # Clean the expression
            expr = self._sanitize_expression(expression)
            
            # Create safe evaluation environment
            safe_dict = {
                # Basic math
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                
                # Math module functions
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'sinh': math.sinh,
                'cosh': math.cosh,
                'tanh': math.tanh,
                'log': math.log,
                'log10': math.log10,
                'log2': math.log2,
                'exp': math.exp,
                'factorial': math.factorial,
                'gcd': math.gcd,
                'ceil': math.ceil,
                'floor': math.floor,
                
                # Constants
                'pi': math.pi,
                'e': math.e,
                'inf': math.inf,
                
                # Power notation
                '**': pow,
            }
            
            # Evaluate safely
            result = eval(expr, {"__builtins__": {}}, safe_dict)
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            logger.info(f"🧮 Calculator: {expression} = {result}")
            
            return ToolResult.success_result(
                f"The result of {expression} is **{result}**",
                metadata={"expression": expression, "result": result}
            )
            
        except ZeroDivisionError:
            return ToolResult.error_result("Division by zero error")
        except ValueError as e:
            return ToolResult.error_result(f"Math error: {str(e)}")
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return ToolResult.error_result(f"Calculation failed: {str(e)}")
    
    def _sanitize_expression(self, expr: str) -> str:
        """Clean and prepare expression for evaluation"""
        # Replace common notations
        expr = expr.replace('^', '**')  # Power notation
        expr = expr.replace('×', '*')   # Multiplication
        expr = expr.replace('÷', '/')   # Division
        expr = expr.replace('√', 'sqrt')  # Square root
        
        # Remove any potentially dangerous characters
        allowed = set('0123456789+-*/.()[], piefactorialsqrtsincostalogexpabsroundminmaxsumgcdceilfloorhatan2')
        expr_clean = ''.join(c for c in expr if c.isalnum() or c in '+-*/.()[], ')
        
        return expr_clean

