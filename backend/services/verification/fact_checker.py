"""
Fact Checker - Curriculum-Grounded Verification
================================================

Verifies AI responses against authoritative curriculum sources:
- NCERT textbook content
- JEE/NEET syllabus facts
- Scientific constants and formulas
- Historical facts and dates

This prevents hallucinations by grounding responses in verified knowledge.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class FactStatus(Enum):
    """Status of fact verification"""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"


@dataclass
class FactCheckResult:
    """Result of fact checking"""
    status: FactStatus
    confidence: float
    verified_facts: List[Dict[str, Any]]
    unverified_claims: List[str]
    corrections: List[Dict[str, Any]]
    sources: List[str]


@dataclass
class CurriculumFact:
    """A verified curriculum fact"""
    fact: str
    subject: str
    topic: str
    source: str  # e.g., "NCERT Class 12 Physics Ch. 1"
    keywords: List[str]
    formula: Optional[str] = None
    value: Optional[str] = None


class FactChecker:
    """
    Curriculum-Grounded Fact Verification Engine
    
    Verifies claims against a knowledge base of verified facts
    from NCERT, JEE/NEET syllabi, and scientific sources.
    """
    
    def __init__(self):
        """Initialize the Fact Checker with curriculum knowledge"""
        self.knowledge_base = self._build_curriculum_knowledge_base()
        self.constants = self._build_scientific_constants()
        self.formulas = self._build_formula_database()
        logger.info(f"📚 FactChecker initialized with {len(self.knowledge_base)} curriculum facts")
    
    def check_response(
        self,
        response_text: str,
        question: str,
        subject: str
    ) -> FactCheckResult:
        """
        Check an AI response for factual accuracy.
        
        Args:
            response_text: The AI response to verify
            question: Original question for context
            subject: Subject area
            
        Returns:
            FactCheckResult with verification details
        """
        try:
            logger.info(f"🔍 Fact-checking response for subject: {subject}")
            
            # Extract claims from response
            claims = self._extract_claims(response_text)
            
            verified_facts = []
            unverified_claims = []
            corrections = []
            sources = set()
            
            for claim in claims:
                result = self._verify_claim(claim, subject)
                
                if result["status"] == "verified":
                    verified_facts.append({
                        "claim": claim,
                        "source": result.get("source", "Curriculum verified")
                    })
                    if result.get("source"):
                        sources.add(result["source"])
                        
                elif result["status"] == "incorrect":
                    corrections.append({
                        "incorrect_claim": claim,
                        "correct_fact": result.get("correct_fact"),
                        "source": result.get("source")
                    })
                else:
                    unverified_claims.append(claim)
            
            # Calculate overall status
            total_claims = len(claims)
            if total_claims == 0:
                status = FactStatus.VERIFIED
                confidence = 1.0
            elif len(corrections) > 0:
                status = FactStatus.PARTIALLY_CORRECT if len(verified_facts) > 0 else FactStatus.INCORRECT
                confidence = len(verified_facts) / total_claims
            elif len(unverified_claims) > total_claims / 2:
                status = FactStatus.UNVERIFIED
                confidence = len(verified_facts) / total_claims
            else:
                status = FactStatus.VERIFIED
                confidence = len(verified_facts) / total_claims
            
            return FactCheckResult(
                status=status,
                confidence=confidence,
                verified_facts=verified_facts,
                unverified_claims=unverified_claims,
                corrections=corrections,
                sources=list(sources)
            )
            
        except Exception as e:
            logger.error(f"❌ Fact checking error: {e}", exc_info=True)
            return FactCheckResult(
                status=FactStatus.UNVERIFIED,
                confidence=0.5,
                verified_facts=[],
                unverified_claims=[],
                corrections=[],
                sources=[]
            )
    
    def verify_constant(
        self,
        constant_name: str,
        claimed_value: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify a scientific constant value.
        
        Args:
            constant_name: Name of the constant (e.g., "speed of light")
            claimed_value: Claimed value
            
        Returns:
            Tuple of (is_correct, correct_value, source)
        """
        # Normalize constant name
        name_lower = constant_name.lower().strip()
        
        for const_key, const_data in self.constants.items():
            if const_key in name_lower or name_lower in const_key:
                correct_value = const_data["value"]
                # Simple numeric comparison (can be made more sophisticated)
                if self._values_match(claimed_value, correct_value):
                    return True, correct_value, const_data["source"]
                else:
                    return False, correct_value, const_data["source"]
        
        return True, None, None  # Unknown constant, don't flag
    
    def verify_formula(
        self,
        formula_name: str,
        claimed_formula: str,
        subject: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify a formula is correct.
        
        Args:
            formula_name: Name/description of the formula
            claimed_formula: The formula as stated
            subject: Subject area
            
        Returns:
            Tuple of (is_correct, correct_formula, source)
        """
        subject_formulas = self.formulas.get(subject.lower(), {})
        
        for key, formula_data in subject_formulas.items():
            if key in formula_name.lower() or formula_name.lower() in key:
                correct_formula = formula_data["formula"]
                # Normalize and compare formulas
                if self._formulas_match(claimed_formula, correct_formula):
                    return True, correct_formula, formula_data["source"]
                else:
                    return False, correct_formula, formula_data["source"]
        
        return True, None, None
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Look for factual patterns
            factual_patterns = [
                r'is\s+defined\s+as',
                r'equals?\s+to',
                r'is\s+equal\s+to',
                r'the\s+value\s+of',
                r'formula\s+is',
                r'constant\s+is',
                r'measures?\s+\d',
                r'\d+\s*(m/s|kg|J|N|V|A|Hz|m|cm|km)',
            ]
            
            for pattern in factual_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break
        
        return claims
    
    def _verify_claim(self, claim: str, subject: str) -> Dict[str, Any]:
        """Verify a single claim against knowledge base"""
        claim_lower = claim.lower()
        
        # Check against knowledge base
        for fact in self.knowledge_base:
            if fact.subject.lower() != subject.lower():
                continue
            
            # Check keyword overlap
            overlap = sum(1 for kw in fact.keywords if kw.lower() in claim_lower)
            if overlap >= 2:  # At least 2 keywords match
                # Check if claim aligns with fact
                if fact.value:
                    if fact.value.lower() in claim_lower:
                        return {
                            "status": "verified",
                            "source": fact.source
                        }
                    else:
                        # Value mentioned but different
                        return {
                            "status": "incorrect",
                            "correct_fact": fact.fact,
                            "source": fact.source
                        }
                else:
                    return {
                        "status": "verified",
                        "source": fact.source
                    }
        
        return {"status": "unverified"}
    
    def _values_match(self, claimed: str, correct: str) -> bool:
        """Check if two values match (with tolerance for scientific notation)"""
        try:
            # Extract numeric values
            claimed_num = float(re.sub(r'[^\d.eE+-]', '', claimed))
            correct_num = float(re.sub(r'[^\d.eE+-]', '', correct))
            
            # Allow 1% tolerance
            if correct_num != 0:
                return abs(claimed_num - correct_num) / abs(correct_num) < 0.01
            else:
                return abs(claimed_num) < 1e-10
        except:
            # String comparison fallback
            return claimed.strip().lower() == correct.strip().lower()
    
    def _formulas_match(self, claimed: str, correct: str) -> bool:
        """Check if two formula representations match"""
        # Normalize formulas
        def normalize(f):
            f = f.lower().strip()
            f = re.sub(r'\s+', '', f)
            f = f.replace('^', '**')
            f = f.replace('×', '*')
            f = f.replace('·', '*')
            return f
        
        return normalize(claimed) == normalize(correct)
    
    def _build_curriculum_knowledge_base(self) -> List[CurriculumFact]:
        """Build the curriculum knowledge base with verified facts"""
        facts = []
        
        # Physics facts
        physics_facts = [
            CurriculumFact(
                fact="Newton's Second Law states F = ma",
                subject="Physics",
                topic="Mechanics",
                source="NCERT Class 11 Physics Ch. 5",
                keywords=["newton", "second", "law", "force", "mass", "acceleration"],
                formula="F = ma"
            ),
            CurriculumFact(
                fact="Speed of light in vacuum is 3 × 10^8 m/s",
                subject="Physics",
                topic="Optics",
                source="NCERT Class 12 Physics Ch. 10",
                keywords=["speed", "light", "vacuum", "electromagnetic"],
                value="3e8"
            ),
            CurriculumFact(
                fact="Gravitational acceleration on Earth is approximately 9.8 m/s²",
                subject="Physics",
                topic="Gravitation",
                source="NCERT Class 11 Physics Ch. 8",
                keywords=["gravitational", "acceleration", "earth", "g"],
                value="9.8"
            ),
            CurriculumFact(
                fact="Planck's constant h = 6.626 × 10^-34 J·s",
                subject="Physics",
                topic="Modern Physics",
                source="NCERT Class 12 Physics Ch. 11",
                keywords=["planck", "constant", "quantum"],
                value="6.626e-34"
            ),
            CurriculumFact(
                fact="Coulomb's constant k = 9 × 10^9 N·m²/C²",
                subject="Physics",
                topic="Electrostatics",
                source="NCERT Class 12 Physics Ch. 1",
                keywords=["coulomb", "constant", "electrostatic"],
                value="9e9"
            ),
        ]
        facts.extend(physics_facts)
        
        # Chemistry facts
        chemistry_facts = [
            CurriculumFact(
                fact="Avogadro's number is 6.022 × 10^23",
                subject="Chemistry",
                topic="Mole Concept",
                source="NCERT Class 11 Chemistry Ch. 1",
                keywords=["avogadro", "number", "mole"],
                value="6.022e23"
            ),
            CurriculumFact(
                fact="Water has molecular formula H2O with molecular mass 18 g/mol",
                subject="Chemistry",
                topic="Chemical Bonding",
                source="NCERT Class 11 Chemistry Ch. 4",
                keywords=["water", "molecular", "formula", "mass"],
                value="18"
            ),
            CurriculumFact(
                fact="pH of neutral solution is 7 at 25°C",
                subject="Chemistry",
                topic="Ionic Equilibrium",
                source="NCERT Class 11 Chemistry Ch. 7",
                keywords=["pH", "neutral", "solution"],
                value="7"
            ),
            CurriculumFact(
                fact="Universal gas constant R = 8.314 J/(mol·K)",
                subject="Chemistry",
                topic="States of Matter",
                source="NCERT Class 11 Chemistry Ch. 5",
                keywords=["gas", "constant", "universal", "ideal"],
                value="8.314"
            ),
        ]
        facts.extend(chemistry_facts)
        
        # Mathematics facts
        math_facts = [
            CurriculumFact(
                fact="Pi (π) is approximately 3.14159",
                subject="Mathematics",
                topic="Trigonometry",
                source="NCERT Class 11 Mathematics",
                keywords=["pi", "circle", "ratio", "circumference"],
                value="3.14159"
            ),
            CurriculumFact(
                fact="e (Euler's number) is approximately 2.71828",
                subject="Mathematics",
                topic="Calculus",
                source="NCERT Class 12 Mathematics Ch. 5",
                keywords=["euler", "natural", "logarithm", "exponential"],
                value="2.71828"
            ),
            CurriculumFact(
                fact="Quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
                subject="Mathematics",
                topic="Quadratic Equations",
                source="NCERT Class 10 Mathematics Ch. 4",
                keywords=["quadratic", "formula", "roots", "equation"],
                formula="x = (-b ± √(b²-4ac)) / 2a"
            ),
            CurriculumFact(
                fact="nPr (Permutation) = n! / (n-r)!",
                subject="Mathematics",
                topic="Permutations and Combinations",
                source="NCERT Class 11 Mathematics Ch. 7",
                keywords=["permutation", "npr", "arrangement", "order"],
                formula="n! / (n-r)!"
            ),
            CurriculumFact(
                fact="nCr (Combination) = n! / (r!(n-r)!)",
                subject="Mathematics",
                topic="Permutations and Combinations",
                source="NCERT Class 11 Mathematics Ch. 7",
                keywords=["combination", "ncr", "selection", "choose"],
                formula="n! / (r!(n-r)!)"
            ),
        ]
        facts.extend(math_facts)
        
        # Biology facts
        biology_facts = [
            CurriculumFact(
                fact="DNA stands for Deoxyribonucleic Acid",
                subject="Biology",
                topic="Molecular Biology",
                source="NCERT Class 12 Biology Ch. 6",
                keywords=["dna", "deoxyribonucleic", "nucleic", "acid", "genetic"]
            ),
            CurriculumFact(
                fact="Mitochondria is the powerhouse of the cell",
                subject="Biology",
                topic="Cell Biology",
                source="NCERT Class 11 Biology Ch. 8",
                keywords=["mitochondria", "powerhouse", "atp", "energy", "cell"]
            ),
            CurriculumFact(
                fact="Photosynthesis equation: 6CO2 + 6H2O → C6H12O6 + 6O2",
                subject="Biology",
                topic="Photosynthesis",
                source="NCERT Class 11 Biology Ch. 13",
                keywords=["photosynthesis", "carbon", "dioxide", "glucose", "oxygen"],
                formula="6CO2 + 6H2O → C6H12O6 + 6O2"
            ),
            CurriculumFact(
                fact="Human heart has 4 chambers: 2 atria and 2 ventricles",
                subject="Biology",
                topic="Circulation",
                source="NCERT Class 11 Biology Ch. 18",
                keywords=["heart", "chambers", "atria", "ventricles", "four"],
                value="4"
            ),
        ]
        facts.extend(biology_facts)
        
        return facts
    
    def _build_scientific_constants(self) -> Dict[str, Dict[str, str]]:
        """Build database of scientific constants"""
        return {
            "speed of light": {
                "value": "3e8 m/s",
                "source": "NCERT Physics"
            },
            "gravitational constant": {
                "value": "6.67e-11 N⋅m²/kg²",
                "source": "NCERT Physics"
            },
            "planck constant": {
                "value": "6.626e-34 J⋅s",
                "source": "NCERT Physics"
            },
            "avogadro number": {
                "value": "6.022e23",
                "source": "NCERT Chemistry"
            },
            "gas constant": {
                "value": "8.314 J/(mol⋅K)",
                "source": "NCERT Chemistry"
            },
            "electron mass": {
                "value": "9.109e-31 kg",
                "source": "NCERT Physics"
            },
            "proton mass": {
                "value": "1.673e-27 kg",
                "source": "NCERT Physics"
            },
            "elementary charge": {
                "value": "1.602e-19 C",
                "source": "NCERT Physics"
            },
            "boltzmann constant": {
                "value": "1.381e-23 J/K",
                "source": "NCERT Physics"
            },
        }
    
    def _build_formula_database(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Build database of verified formulas by subject"""
        return {
            "physics": {
                "force": {"formula": "F = ma", "source": "NCERT Class 11"},
                "kinetic energy": {"formula": "KE = 0.5*m*v^2", "source": "NCERT Class 11"},
                "potential energy": {"formula": "PE = mgh", "source": "NCERT Class 11"},
                "momentum": {"formula": "p = mv", "source": "NCERT Class 11"},
                "ohm's law": {"formula": "V = IR", "source": "NCERT Class 12"},
                "power": {"formula": "P = VI", "source": "NCERT Class 12"},
                "wave velocity": {"formula": "v = fλ", "source": "NCERT Class 11"},
            },
            "chemistry": {
                "ideal gas": {"formula": "PV = nRT", "source": "NCERT Class 11"},
                "molarity": {"formula": "M = n/V", "source": "NCERT Class 11"},
                "rate law": {"formula": "r = k[A]^n", "source": "NCERT Class 12"},
            },
            "mathematics": {
                "quadratic": {"formula": "x = (-b ± √(b²-4ac)) / 2a", "source": "NCERT Class 10"},
                "distance": {"formula": "d = √((x2-x1)² + (y2-y1)²)", "source": "NCERT Class 10"},
                "derivative power rule": {"formula": "d/dx(x^n) = n*x^(n-1)", "source": "NCERT Class 11"},
                "integration power rule": {"formula": "∫x^n dx = x^(n+1)/(n+1) + C", "source": "NCERT Class 12"},
            },
        }

