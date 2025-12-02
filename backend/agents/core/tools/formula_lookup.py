"""
📐 Formula Lookup Tool - Find Relevant Formulas
================================================

Searches for formulas relevant to a given topic or problem.
Organized by subject and topic for easy access.
"""

import logging
from typing import Dict, Any, List
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# Formula database organized by subject
FORMULAS = {
    "physics": {
        "mechanics": [
            {"name": "Newton's Second Law", "formula": "F = ma", "variables": "F: force, m: mass, a: acceleration"},
            {"name": "Kinematic Equation 1", "formula": "v = u + at", "variables": "v: final velocity, u: initial velocity, a: acceleration, t: time"},
            {"name": "Kinematic Equation 2", "formula": "s = ut + ½at²", "variables": "s: displacement, u: initial velocity, a: acceleration, t: time"},
            {"name": "Kinematic Equation 3", "formula": "v² = u² + 2as", "variables": "v: final velocity, u: initial velocity, a: acceleration, s: displacement"},
            {"name": "Momentum", "formula": "p = mv", "variables": "p: momentum, m: mass, v: velocity"},
            {"name": "Kinetic Energy", "formula": "KE = ½mv²", "variables": "KE: kinetic energy, m: mass, v: velocity"},
            {"name": "Potential Energy", "formula": "PE = mgh", "variables": "PE: potential energy, m: mass, g: gravity, h: height"},
            {"name": "Work", "formula": "W = F⋅d⋅cos(θ)", "variables": "W: work, F: force, d: displacement, θ: angle"},
            {"name": "Power", "formula": "P = W/t = Fv", "variables": "P: power, W: work, t: time, F: force, v: velocity"},
        ],
        "waves": [
            {"name": "Wave Velocity", "formula": "v = fλ", "variables": "v: velocity, f: frequency, λ: wavelength"},
            {"name": "Time Period", "formula": "T = 1/f", "variables": "T: time period, f: frequency"},
            {"name": "Wave Equation", "formula": "y = A⋅sin(kx - ωt)", "variables": "A: amplitude, k: wave number, ω: angular frequency"},
        ],
        "electricity": [
            {"name": "Ohm's Law", "formula": "V = IR", "variables": "V: voltage, I: current, R: resistance"},
            {"name": "Power (electrical)", "formula": "P = VI = I²R = V²/R", "variables": "P: power, V: voltage, I: current, R: resistance"},
            {"name": "Coulomb's Law", "formula": "F = kq₁q₂/r²", "variables": "F: force, k: Coulomb constant, q: charges, r: distance"},
            {"name": "Electric Field", "formula": "E = F/q = kQ/r²", "variables": "E: electric field, F: force, q: test charge, Q: source charge"},
        ],
        "modern_physics": [
            {"name": "Einstein's Mass-Energy", "formula": "E = mc²", "variables": "E: energy, m: mass, c: speed of light"},
            {"name": "Photoelectric Effect", "formula": "KE = hf - φ", "variables": "KE: kinetic energy, h: Planck constant, f: frequency, φ: work function"},
            {"name": "de Broglie Wavelength", "formula": "λ = h/p = h/mv", "variables": "λ: wavelength, h: Planck constant, p: momentum"},
        ]
    },
    "chemistry": {
        "general": [
            {"name": "Ideal Gas Law", "formula": "PV = nRT", "variables": "P: pressure, V: volume, n: moles, R: gas constant, T: temperature"},
            {"name": "Molarity", "formula": "M = n/V", "variables": "M: molarity, n: moles, V: volume in liters"},
            {"name": "Dilution", "formula": "M₁V₁ = M₂V₂", "variables": "M: molarity, V: volume (before and after)"},
        ],
        "thermodynamics": [
            {"name": "Gibbs Free Energy", "formula": "ΔG = ΔH - TΔS", "variables": "ΔG: Gibbs energy, ΔH: enthalpy, T: temperature, ΔS: entropy"},
            {"name": "Enthalpy", "formula": "ΔH = ΔU + PΔV", "variables": "ΔH: enthalpy, ΔU: internal energy, P: pressure, ΔV: volume change"},
        ],
        "electrochemistry": [
            {"name": "Nernst Equation", "formula": "E = E° - (RT/nF)ln(Q)", "variables": "E: cell potential, E°: standard potential, Q: reaction quotient"},
            {"name": "Faraday's Law", "formula": "m = (M⋅I⋅t)/(n⋅F)", "variables": "m: mass deposited, M: molar mass, I: current, t: time, n: electrons, F: Faraday constant"},
        ]
    },
    "mathematics": {
        "algebra": [
            {"name": "Quadratic Formula", "formula": "x = (-b ± √(b²-4ac))/2a", "variables": "For ax² + bx + c = 0"},
            {"name": "Sum of AP", "formula": "Sₙ = n/2(2a + (n-1)d) = n/2(a + l)", "variables": "a: first term, d: common difference, n: terms, l: last term"},
            {"name": "Sum of GP", "formula": "Sₙ = a(rⁿ - 1)/(r - 1)", "variables": "a: first term, r: common ratio, n: terms"},
            {"name": "Binomial Theorem", "formula": "(a+b)ⁿ = Σ ⁿCᵣ aⁿ⁻ʳbʳ", "variables": "n: power, r: 0 to n"},
        ],
        "calculus": [
            {"name": "Power Rule (derivative)", "formula": "d/dx(xⁿ) = nxⁿ⁻¹", "variables": "n: power"},
            {"name": "Chain Rule", "formula": "d/dx[f(g(x))] = f'(g(x))⋅g'(x)", "variables": "composite function"},
            {"name": "Product Rule", "formula": "d/dx(uv) = u(dv/dx) + v(du/dx)", "variables": "u, v: functions"},
            {"name": "Integration Power Rule", "formula": "∫xⁿdx = xⁿ⁺¹/(n+1) + C", "variables": "n ≠ -1"},
        ],
        "trigonometry": [
            {"name": "Pythagorean Identity", "formula": "sin²θ + cos²θ = 1", "variables": "θ: angle"},
            {"name": "Double Angle (sin)", "formula": "sin(2θ) = 2sinθcosθ", "variables": "θ: angle"},
            {"name": "Double Angle (cos)", "formula": "cos(2θ) = cos²θ - sin²θ", "variables": "θ: angle"},
        ]
    }
}


class FormulaLookupTool(BaseTool):
    """
    Look up formulas relevant to a topic.
    """
    
    @property
    def name(self) -> str:
        return "formula_lookup"
    
    @property
    def description(self) -> str:
        return "Finds relevant formulas for a given topic. Use when you need to recall a specific formula or find formulas related to a concept."
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "The topic to find formulas for (e.g., 'mechanics', 'quadratic', 'electricity')",
            "subject": "(Optional) Subject to filter: physics, chemistry, mathematics"
        }
    
    async def execute(
        self, 
        topic: str = "", 
        subject: str = None,
        context: Dict = None, 
        **kwargs
    ) -> ToolResult:
        """
        Look up formulas
        """
        if not topic:
            return ToolResult.error_result("No topic provided")
        
        topic_lower = topic.lower().strip()
        matches = []
        
        # Search through formulas
        subjects_to_search = [subject.lower()] if subject else FORMULAS.keys()
        
        for subj in subjects_to_search:
            if subj not in FORMULAS:
                continue
                
            for category, formulas in FORMULAS[subj].items():
                for formula in formulas:
                    # Match by topic name, formula name, or category
                    if (topic_lower in formula["name"].lower() or 
                        topic_lower in category.lower() or
                        topic_lower in formula.get("variables", "").lower()):
                        matches.append({
                            "subject": subj.title(),
                            "category": category.title(),
                            **formula
                        })
        
        if not matches:
            return ToolResult.success_result(
                f"No formulas found for '{topic}'. Try searching with different keywords like 'mechanics', 'calculus', 'electricity'.",
                metadata={"found": False, "topic": topic}
            )
        
        # Format results
        results = ["**📐 Relevant Formulas:**\n"]
        
        for m in matches[:8]:  # Limit to 8 formulas
            results.append(f"### {m['name']}")
            results.append(f"**Formula**: `{m['formula']}`")
            results.append(f"**Variables**: {m['variables']}")
            results.append(f"_({m['subject']} - {m['category']})_\n")
        
        output = "\n".join(results)
        
        logger.info(f"📐 Formula lookup: '{topic}' - {len(matches)} formulas found")
        
        return ToolResult.success_result(
            output,
            metadata={"found": True, "count": len(matches), "topic": topic}
        )

