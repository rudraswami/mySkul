"""
Vidya Grammar Engine (VGE)
Declarative DSL for defining how subjects are visualized
Rule-based grammar system - No AI generation, only SME-written rules
"""

from .grammar_parser import GrammarParser, GrammarDefinition
from .grammar_validator import GrammarValidator
from .grammar_runtime import GrammarRuntime

__all__ = ['GrammarParser', 'GrammarDefinition', 'GrammarValidator', 'GrammarRuntime']














