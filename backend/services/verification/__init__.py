"""
Verification Module - The Symbolic Reasoning Layer
===================================================

This module implements TRUE symbolic reasoning and verification,
transforming Druv AI from a prompt-based system to a neuro-symbolic one.

Components:
- MathVerifier: Symbolic math verification using SymPy
- FactChecker: Curriculum-grounded fact verification
- LogicValidator: Step-by-step logical reasoning validation
- VerificationOrchestrator: Coordinates all verification layers

This is Layer 2 (Symbolic Reasoning) + Layer 3 (Supervisor Verification)
of the Druv AI Four-Layer Architecture.
"""

from .math_verifier import MathVerifier
from .fact_checker import FactChecker
from .logic_validator import LogicValidator
from .orchestrator import VerificationOrchestrator, get_verification_orchestrator

__all__ = [
    'MathVerifier',
    'FactChecker', 
    'LogicValidator',
    'VerificationOrchestrator',
    'get_verification_orchestrator'
]

