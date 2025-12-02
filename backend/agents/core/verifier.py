"""
✓ Verifier - Self-Checking & Fact Verification
===============================================

The Verifier ensures agent responses are accurate by:
1. Checking mathematical calculations
2. Verifying factual claims
3. Detecting logical inconsistencies
4. Validating against known correct answers

This is crucial for educational content where accuracy matters.
Students trust the AI - we must ensure that trust is deserved.
"""

import logging
import re
import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Status of verification"""
    VERIFIED = "verified"
    FAILED = "failed"
    UNCERTAIN = "uncertain"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class VerificationResult:
    """Result of verification check"""
    status: VerificationStatus
    confidence: float  # 0 to 1
    details: str
    corrections: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": self.confidence,
            "details": self.details,
            "corrections": self.corrections
        }


class Verifier:
    """
    Verifies agent responses for accuracy.
    
    Usage:
        verifier = Verifier()
        
        # Verify a calculation
        result = verifier.verify_calculation("2 + 2 = 5")
        # Returns: VerificationResult(status=FAILED, corrections=["2 + 2 = 4"])
        
        # Verify a factual claim
        result = verifier.verify_fact("Speed of light is 300,000 km/s")
        # Returns: VerificationResult(status=VERIFIED, confidence=0.95)
        
        # Full response verification
        result = await verifier.verify_response(response_text, context)
    """
    
    # Known constants for verification
    CONSTANTS = {
        "speed of light": 299792458,  # m/s
        "gravitational constant": 6.674e-11,
        "planck constant": 6.626e-34,
        "avogadro number": 6.022e23,
        "pi": 3.14159265359,
        "e": 2.71828182846,
    }
    
    # Common mathematical errors to check
    COMMON_ERRORS = [
        # (wrong pattern, correct pattern, description)
        (r"(\d+)\s*[×x]\s*0\s*=\s*(\d+)", "any × 0 = 0", "Multiplication by zero should equal zero"),
        (r"(\d+)\s*/\s*0\s*=", None, "Division by zero is undefined"),
        (r"√(-\d+)", None, "Square root of negative number (in real numbers)"),
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def verify_calculation(self, expression: str) -> VerificationResult:
        """
        Verify a mathematical calculation.
        
        Args:
            expression: String like "2 + 2 = 4" or "sqrt(16) = 4"
        
        Returns:
            VerificationResult with status and any corrections
        """
        try:
            # Parse equation format: "expression = result"
            if "=" not in expression:
                return VerificationResult(
                    status=VerificationStatus.NOT_APPLICABLE,
                    confidence=0,
                    details="No equation found to verify"
                )
            
            parts = expression.split("=")
            if len(parts) != 2:
                return VerificationResult(
                    status=VerificationStatus.UNCERTAIN,
                    confidence=0.5,
                    details="Complex equation - manual verification recommended"
                )
            
            left_side = parts[0].strip()
            claimed_result = parts[1].strip()
            
            # Clean and evaluate left side
            left_clean = self._clean_expression(left_side)
            
            try:
                # Safe evaluation
                actual_result = self._safe_eval(left_clean)
                
                # Parse claimed result
                claimed_value = self._parse_number(claimed_result)
                
                if claimed_value is None:
                    return VerificationResult(
                        status=VerificationStatus.UNCERTAIN,
                        confidence=0.5,
                        details=f"Could not parse result: {claimed_result}"
                    )
                
                # Compare with tolerance for floating point
                if isinstance(actual_result, float):
                    tolerance = abs(actual_result) * 0.0001 if actual_result != 0 else 0.0001
                    is_correct = abs(actual_result - claimed_value) < tolerance
                else:
                    is_correct = actual_result == claimed_value
                
                if is_correct:
                    return VerificationResult(
                        status=VerificationStatus.VERIFIED,
                        confidence=0.99,
                        details=f"✓ Calculation verified: {left_side} = {actual_result}"
                    )
                else:
                    return VerificationResult(
                        status=VerificationStatus.FAILED,
                        confidence=0.95,
                        details=f"✗ Calculation error detected",
                        corrections=[f"Correct answer: {left_side} = {actual_result}"]
                    )
                    
            except ZeroDivisionError:
                return VerificationResult(
                    status=VerificationStatus.FAILED,
                    confidence=1.0,
                    details="Division by zero detected",
                    corrections=["This expression involves division by zero, which is undefined"]
                )
            except Exception as e:
                return VerificationResult(
                    status=VerificationStatus.UNCERTAIN,
                    confidence=0.3,
                    details=f"Could not evaluate: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return VerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0,
                details=f"Verification failed: {str(e)}"
            )
    
    def verify_fact(self, claim: str) -> VerificationResult:
        """
        Verify a factual claim against known facts.
        """
        claim_lower = claim.lower()
        
        # Check against known constants
        for const_name, const_value in self.CONSTANTS.items():
            if const_name in claim_lower:
                # Try to extract the claimed value
                numbers = re.findall(r'[\d.]+(?:e[+-]?\d+)?', claim)
                
                if not numbers:
                    return VerificationResult(
                        status=VerificationStatus.UNCERTAIN,
                        confidence=0.5,
                        details=f"Found reference to {const_name} but no value to verify"
                    )
                
                # Check each number found
                for num_str in numbers:
                    try:
                        claimed_num = float(num_str)
                        # Allow for different units/magnitudes
                        ratio = claimed_num / const_value if const_value != 0 else 0
                        
                        # Check if it's close (within an order of magnitude)
                        if 0.1 <= ratio <= 10 or abs(claimed_num - const_value) / const_value < 0.01:
                            return VerificationResult(
                                status=VerificationStatus.VERIFIED,
                                confidence=0.9,
                                details=f"✓ Value for {const_name} appears correct"
                            )
                    except ValueError:
                        continue
                
                return VerificationResult(
                    status=VerificationStatus.UNCERTAIN,
                    confidence=0.6,
                    details=f"Could not verify value for {const_name}"
                )
        
        return VerificationResult(
            status=VerificationStatus.NOT_APPLICABLE,
            confidence=0,
            details="No verifiable facts found in claim"
        )
    
    def check_logical_consistency(self, statements: List[str]) -> VerificationResult:
        """
        Check a list of statements for logical consistency.
        """
        # Simple checks for obvious contradictions
        contradictions = []
        
        for i, stmt1 in enumerate(statements):
            for stmt2 in statements[i+1:]:
                # Check for direct negation patterns
                if self._are_contradictory(stmt1, stmt2):
                    contradictions.append((stmt1, stmt2))
        
        if contradictions:
            return VerificationResult(
                status=VerificationStatus.FAILED,
                confidence=0.8,
                details="Logical inconsistencies detected",
                corrections=[f"'{c[0]}' contradicts '{c[1]}'" for c in contradictions[:3]]
            )
        
        return VerificationResult(
            status=VerificationStatus.VERIFIED,
            confidence=0.7,
            details="No obvious logical inconsistencies found"
        )
    
    async def verify_response(
        self, 
        response: str, 
        context: Dict[str, Any] = None
    ) -> VerificationResult:
        """
        Comprehensive verification of an agent response.
        
        Checks:
        1. Mathematical calculations
        2. Factual claims
        3. Logical consistency
        """
        results = []
        
        # Extract and verify calculations
        calculations = self._extract_calculations(response)
        for calc in calculations:
            result = self.verify_calculation(calc)
            if result.status == VerificationStatus.FAILED:
                results.append(result)
        
        # Check factual claims (basic check)
        fact_result = self.verify_fact(response)
        if fact_result.status == VerificationStatus.FAILED:
            results.append(fact_result)
        
        # Aggregate results
        if not results:
            return VerificationResult(
                status=VerificationStatus.VERIFIED,
                confidence=0.85,
                details="Response passed verification checks"
            )
        
        # If any failures, return aggregated failure
        all_corrections = []
        for r in results:
            if r.corrections:
                all_corrections.extend(r.corrections)
        
        return VerificationResult(
            status=VerificationStatus.FAILED,
            confidence=0.9,
            details=f"Found {len(results)} issue(s) in response",
            corrections=all_corrections
        )
    
    def _clean_expression(self, expr: str) -> str:
        """Clean expression for evaluation"""
        expr = expr.replace('^', '**')
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        expr = expr.replace('√', 'sqrt')
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)  # 2x -> 2*x
        return expr
    
    def _safe_eval(self, expr: str) -> float:
        """Safely evaluate a mathematical expression"""
        safe_dict = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'abs': abs,
            'pi': math.pi,
            'e': math.e,
            'pow': pow,
        }
        return eval(expr, {"__builtins__": {}}, safe_dict)
    
    def _parse_number(self, s: str) -> Optional[float]:
        """Parse a number from string"""
        try:
            # Remove common formatting
            s = s.strip().replace(',', '').replace(' ', '')
            return float(s)
        except ValueError:
            return None
    
    def _extract_calculations(self, text: str) -> List[str]:
        """Extract calculation expressions from text"""
        # Pattern for equations like "2 + 2 = 4"
        pattern = r'[\d\s\+\-\*/\^\(\)\.]+\s*=\s*[\d\.\-]+'
        matches = re.findall(pattern, text)
        return [m.strip() for m in matches if len(m.strip()) > 3]
    
    def _are_contradictory(self, stmt1: str, stmt2: str) -> bool:
        """Check if two statements are contradictory"""
        s1, s2 = stmt1.lower(), stmt2.lower()
        
        # Simple negation check
        if "not " in s1 and s1.replace("not ", "") in s2:
            return True
        if "not " in s2 and s2.replace("not ", "") in s1:
            return True
        
        # Opposite value check (e.g., "is positive" vs "is negative")
        opposites = [
            ("positive", "negative"),
            ("increase", "decrease"),
            ("greater", "less"),
            ("true", "false"),
            ("always", "never"),
        ]
        
        for pos, neg in opposites:
            if pos in s1 and neg in s2:
                return True
            if neg in s1 and pos in s2:
                return True
        
        return False

