"""
✓ Fact Checker Tool - Verify Claims & Statements
=================================================

Verifies factual claims against trusted knowledge.
Helps agents ensure accuracy in their responses.
"""

import logging
from typing import Dict, Any, List, Tuple
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# Verified facts database (can be expanded or connected to external APIs)
VERIFIED_FACTS = {
    # Physics constants
    "speed of light": ("299,792,458 m/s", "exact value"),
    "gravitational constant": ("6.674 × 10⁻¹¹ N⋅m²/kg²", "approximate"),
    "planck constant": ("6.626 × 10⁻³⁴ J⋅s", "approximate"),
    "electron mass": ("9.109 × 10⁻³¹ kg", "approximate"),
    "proton mass": ("1.673 × 10⁻²⁷ kg", "approximate"),
    "avogadro number": ("6.022 × 10²³ mol⁻¹", "approximate"),
    "boltzmann constant": ("1.381 × 10⁻²³ J/K", "approximate"),
    "acceleration due to gravity": ("9.81 m/s² (on Earth's surface)", "approximate"),
    
    # Mathematical constants
    "pi": ("3.14159265359...", "irrational number"),
    "euler number": ("2.71828182846...", "irrational number"),
    "golden ratio": ("1.61803398875...", "irrational number"),
    
    # Chemistry
    "water boiling point": ("100°C at 1 atm", "standard conditions"),
    "water freezing point": ("0°C at 1 atm", "standard conditions"),
    "atomic number of carbon": ("6", "exact"),
    "atomic number of hydrogen": ("1", "exact"),
    "atomic number of oxygen": ("8", "exact"),
    
    # Biology
    "human chromosomes": ("46 (23 pairs)", "normal diploid"),
    "dna bases": ("Adenine, Thymine, Guanine, Cytosine (A, T, G, C)", "exact"),
    "blood types": ("A, B, AB, O (with Rh factor +/-)", "human ABO system"),
    
    # JEE/NEET specific
    "jee mains total marks": ("300 marks (75 questions × 4 marks)", "2024 pattern"),
    "neet total marks": ("720 marks (180 questions × 4 marks)", "current pattern"),
}


class FactCheckerTool(BaseTool):
    """
    Verify factual claims against trusted sources.
    """
    
    @property
    def name(self) -> str:
        return "fact_checker"
    
    @property
    def description(self) -> str:
        return "Verifies factual claims and constants. Use to double-check numerical values, scientific constants, or factual statements before presenting them."
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "claim": "The claim or fact to verify",
            "value": "(Optional) The specific value to check"
        }
    
    async def execute(
        self, 
        claim: str = "", 
        value: str = None,
        context: Dict = None, 
        **kwargs
    ) -> ToolResult:
        """
        Check a factual claim
        """
        if not claim:
            return ToolResult.error_result("No claim provided to verify")
        
        claim_lower = claim.lower().strip()
        
        # Search for matching facts
        matches = []
        for fact_key, (fact_value, certainty) in VERIFIED_FACTS.items():
            if fact_key in claim_lower or claim_lower in fact_key:
                matches.append((fact_key, fact_value, certainty))
        
        if not matches:
            return ToolResult.success_result(
                f"⚠️ Could not verify '{claim}' against known facts. Please double-check with authoritative sources.",
                metadata={"verified": False, "claim": claim}
            )
        
        # Format verification results
        results = []
        for fact_key, fact_value, certainty in matches:
            result = f"✓ **{fact_key.title()}**: {fact_value}"
            result += f"\n  _Certainty: {certainty}_"
            
            # If user provided a value, compare
            if value:
                # Simple comparison (could be enhanced)
                if value.lower() in fact_value.lower():
                    result += "\n  ✅ Your value appears correct!"
                else:
                    result += f"\n  ⚠️ Your value '{value}' may differ from verified value."
            
            results.append(result)
        
        output = "**Fact Check Results:**\n\n" + "\n\n".join(results)
        
        logger.info(f"✓ Fact check: '{claim}' - {len(matches)} matches found")
        
        return ToolResult.success_result(
            output,
            metadata={"verified": True, "matches": len(matches), "claim": claim}
        )

