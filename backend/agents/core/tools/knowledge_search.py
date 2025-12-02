"""
📚 Knowledge Search Tool - Concept & Definition Lookup
======================================================

Searches the knowledge base for concepts, definitions, and explanations.
Useful for looking up scientific facts, historical information, and formulas.
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# Built-in knowledge base for common educational concepts
KNOWLEDGE_BASE = {
    # Physics
    "newton's laws": {
        "subject": "Physics",
        "definition": """Newton's Three Laws of Motion:
1. **First Law (Inertia)**: An object at rest stays at rest, and an object in motion stays in motion, unless acted upon by an external force.
2. **Second Law (F=ma)**: Force equals mass times acceleration. The acceleration of an object is directly proportional to the net force and inversely proportional to its mass.
3. **Third Law (Action-Reaction)**: For every action, there is an equal and opposite reaction.""",
        "formulas": ["F = ma", "p = mv"],
        "exam_tips": "JEE often tests these in combination with friction and circular motion problems."
    },
    
    "photosynthesis": {
        "subject": "Biology",
        "definition": """Photosynthesis is the process by which green plants convert light energy into chemical energy (glucose).

**Equation**: 6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂

**Key Points**:
- Occurs in chloroplasts
- Light reaction: In thylakoid membrane (produces ATP, NADPH)
- Dark reaction (Calvin cycle): In stroma (produces glucose)""",
        "formulas": ["6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂"],
        "exam_tips": "NEET focuses on light and dark reactions, photosystems I and II."
    },
    
    "quadratic formula": {
        "subject": "Mathematics",
        "definition": """For a quadratic equation ax² + bx + c = 0:

**Formula**: x = (-b ± √(b² - 4ac)) / 2a

**Discriminant (D)**: D = b² - 4ac
- D > 0: Two distinct real roots
- D = 0: One repeated real root
- D < 0: Two complex conjugate roots""",
        "formulas": ["x = (-b ± √(b² - 4ac)) / 2a", "D = b² - 4ac"],
        "exam_tips": "Check discriminant first to determine nature of roots."
    },
    
    "thermodynamics": {
        "subject": "Physics/Chemistry",
        "definition": """Laws of Thermodynamics:

**Zeroth Law**: If A is in thermal equilibrium with B, and B with C, then A is with C.

**First Law**: Energy conservation: ΔU = Q - W
- ΔU: Change in internal energy
- Q: Heat added to system
- W: Work done by system

**Second Law**: Entropy of an isolated system always increases.

**Third Law**: As temperature approaches absolute zero, entropy approaches a constant minimum.""",
        "formulas": ["ΔU = Q - W", "ΔS ≥ 0", "W = PΔV"],
        "exam_tips": "Sign conventions are crucial - memorize whether work is done BY or ON the system."
    },
    
    "derivatives": {
        "subject": "Mathematics",
        "definition": """A derivative measures the rate of change of a function.

**Definition**: f'(x) = lim(h→0) [f(x+h) - f(x)] / h

**Common Derivatives**:
- d/dx(xⁿ) = nxⁿ⁻¹
- d/dx(eˣ) = eˣ
- d/dx(ln x) = 1/x
- d/dx(sin x) = cos x
- d/dx(cos x) = -sin x""",
        "formulas": ["f'(x) = lim(h→0) [f(x+h) - f(x)] / h"],
        "exam_tips": "Master chain rule and product rule - they appear in almost every calculus problem."
    },
    
    "organic chemistry nomenclature": {
        "subject": "Chemistry",
        "definition": """IUPAC Naming Rules:

1. **Find longest carbon chain** (parent chain)
2. **Number the chain** (lowest locants for substituents)
3. **Name substituents** with position numbers
4. **Alphabetical order** for multiple substituents

**Prefixes**: meth(1), eth(2), prop(3), but(4), pent(5), hex(6)
**Suffixes**: -ane (alkane), -ene (alkene), -yne (alkyne), -ol (alcohol), -al (aldehyde)""",
        "formulas": [],
        "exam_tips": "Practice naming complex molecules - NEET and JEE both test this heavily."
    },
    
    "cell division": {
        "subject": "Biology",
        "definition": """Two types of cell division:

**Mitosis** (Somatic cells):
- Produces 2 identical daughter cells
- Phases: Prophase → Metaphase → Anaphase → Telophase
- Same chromosome number (2n → 2n)

**Meiosis** (Reproductive cells):
- Produces 4 haploid gametes
- Two divisions: Meiosis I and II
- Reduces chromosome number (2n → n)
- Crossing over occurs (genetic variation)""",
        "formulas": [],
        "exam_tips": "Remember: Mitosis = identical copies, Meiosis = variation through crossing over."
    },
    
    "integration": {
        "subject": "Mathematics",
        "definition": """Integration is the reverse of differentiation.

**Indefinite Integral**: ∫f(x)dx = F(x) + C

**Common Integrals**:
- ∫xⁿ dx = xⁿ⁺¹/(n+1) + C
- ∫eˣ dx = eˣ + C
- ∫1/x dx = ln|x| + C
- ∫sin x dx = -cos x + C
- ∫cos x dx = sin x + C

**Definite Integral**: ∫[a,b] f(x)dx = F(b) - F(a)""",
        "formulas": ["∫xⁿ dx = xⁿ⁺¹/(n+1) + C"],
        "exam_tips": "For JEE: Master integration by parts and partial fractions."
    }
}


class KnowledgeSearchTool(BaseTool):
    """
    Search the knowledge base for concepts and definitions.
    """
    
    @property
    def name(self) -> str:
        return "knowledge_search"
    
    @property
    def description(self) -> str:
        return "Searches the knowledge base for concepts, definitions, formulas, and exam tips. Use when you need to look up or verify factual information."
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "query": "The concept or topic to search for",
            "subject": "(Optional) Subject to filter results (Physics, Chemistry, Biology, Mathematics)"
        }
    
    async def execute(
        self, 
        query: str = "", 
        subject: str = None,
        context: Dict = None, 
        **kwargs
    ) -> ToolResult:
        """
        Search knowledge base
        """
        if not query:
            return ToolResult.error_result("No search query provided")
        
        query_lower = query.lower().strip()
        
        # Search for matching concepts
        matches = []
        for key, value in KNOWLEDGE_BASE.items():
            # Check if query matches key
            if query_lower in key or key in query_lower:
                # Filter by subject if specified
                if subject and subject.lower() not in value.get("subject", "").lower():
                    continue
                matches.append((key, value))
            # Also check if query is in definition
            elif query_lower in value.get("definition", "").lower():
                if subject and subject.lower() not in value.get("subject", "").lower():
                    continue
                matches.append((key, value))
        
        if not matches:
            return ToolResult.success_result(
                f"No exact match found for '{query}'. Try searching with different keywords.",
                metadata={"found": False, "query": query}
            )
        
        # Format results
        results = []
        for key, data in matches[:3]:  # Top 3 matches
            result = f"### {key.title()}\n"
            result += f"**Subject**: {data.get('subject', 'General')}\n\n"
            result += data.get('definition', 'No definition available.')
            
            if data.get('formulas'):
                result += f"\n\n**Key Formulas**: {', '.join(data['formulas'])}"
            
            if data.get('exam_tips'):
                result += f"\n\n💡 **Exam Tip**: {data['exam_tips']}"
            
            results.append(result)
        
        output = "\n\n---\n\n".join(results)
        
        logger.info(f"📚 Knowledge search: '{query}' found {len(matches)} results")
        
        return ToolResult.success_result(
            output,
            metadata={"found": True, "count": len(matches), "query": query}
        )

