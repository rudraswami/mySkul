"""
Problem Parser
Extracts structured information from problem statements for solution generation

Handles:
- Math: equations, values, variables
- Physics: quantities, units, givens/find
- Chemistry: reactions, molarity, compounds
"""
from __future__ import annotations

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ProblemType(Enum):
    """Types of math/science problems"""
    # Math
    QUADRATIC_EQUATION = "quadratic_equation"
    LINEAR_EQUATION = "linear_equation"
    SYSTEM_OF_EQUATIONS = "system_of_equations"
    TRIGONOMETRY = "trigonometry"
    CALCULUS = "calculus"
    GEOMETRY = "geometry"
    ARITHMETIC = "arithmetic"

    # Physics
    KINEMATICS = "kinematics"
    DYNAMICS = "dynamics"
    ENERGY = "energy"
    ELECTRICITY = "electricity"
    WAVES = "waves"

    # Chemistry
    STOICHIOMETRY = "stoichiometry"
    MOLARITY = "molarity"
    PH_CALCULATION = "ph_calculation"

    # General
    WORD_PROBLEM = "word_problem"
    UNKNOWN = "unknown"


@dataclass
class ParsedProblem:
    """Structured representation of a problem"""
    problem_type: ProblemType
    raw_question: str

    # Math specific
    equation: Optional[str] = None
    coefficients: Dict[str, float] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)

    # Physics specific
    given: Dict[str, Tuple[float, str]] = field(default_factory=dict)  # name: (value, unit)
    find: List[str] = field(default_factory=list)

    # General
    numbers: List[float] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    context: Optional[str] = None  # Real-world context if any


class ProblemParser:
    """Parse problems to extract structured information"""

    def parse(self, question: str, subject: str = "math") -> ParsedProblem:
        """
        Parse question into structured problem

        Args:
            question: The problem statement
            subject: Subject (math, physics, chemistry)

        Returns:
            ParsedProblem with extracted information
        """
        if subject.lower() in ["math", "mathematics"]:
            return self._parse_math_problem(question)
        elif subject.lower() == "physics":
            return self._parse_physics_problem(question)
        elif subject.lower() == "chemistry":
            return self._parse_chemistry_problem(question)
        else:
            return self._parse_general_problem(question)

    def _parse_math_problem(self, question: str) -> ParsedProblem:
        """Parse math problems"""
        # Detect problem type
        problem_type = self._detect_math_type(question)

        # Extract equation if present
        equation = self._extract_equation(question)

        # Extract coefficients and variables
        coefficients, variables = self._extract_coefficients_and_variables(equation or question)

        # Extract all numbers
        numbers = self._extract_numbers(question)

        # Extract keywords
        keywords = self._extract_keywords(question)

        # Extract context (real-world scenario)
        context = self._extract_context(question)

        return ParsedProblem(
            problem_type=problem_type,
            raw_question=question,
            equation=equation,
            coefficients=coefficients,
            variables=variables,
            numbers=numbers,
            keywords=keywords,
            context=context
        )

    def _detect_math_type(self, question: str) -> ProblemType:
        """Detect type of math problem"""
        q_lower = question.lower()

        # Check for quadratic
        if any(term in q_lower for term in ['x^2', 'x²', 'quadratic', 'x square']):
            return ProblemType.QUADRATIC_EQUATION

        # Check for trigonometry
        if any(term in q_lower for term in ['sin', 'cos', 'tan', 'angle', 'triangle']):
            return ProblemType.TRIGONOMETRY

        # Check for calculus
        if any(term in q_lower for term in ['derivative', 'integral', 'limit', 'differentiate']):
            return ProblemType.CALCULUS

        # Check for geometry
        if any(term in q_lower for term in ['area', 'volume', 'perimeter', 'circle', 'rectangle']):
            return ProblemType.GEOMETRY

        # Check for linear equation
        if '=' in question and 'x' in q_lower and 'x^2' not in q_lower:
            return ProblemType.LINEAR_EQUATION

        # Check for word problem
        if any(term in q_lower for term in ['if', 'when', 'has', 'costs', 'years old']):
            return ProblemType.WORD_PROBLEM

        return ProblemType.ARITHMETIC

    def _extract_equation(self, question: str) -> Optional[str]:
        """Extract the main equation from question"""
        # Look for patterns like: x^2 + 5x + 6 = 0
        equation_patterns = [
            r'([a-z]\^?\d?\s*[+\-]\s*\d+[a-z]?\s*[+\-]\s*\d+\s*=\s*\d+)',  # x^2 + 5x + 6 = 0
            r'([a-z]\s*[+\-]\s*\d+\s*=\s*\d+)',  # x + 5 = 10
            r'(\d+[a-z]\s*[+\-]\s*\d+[a-z]\s*=\s*\d+)',  # 2x + 3y = 10
        ]

        for pattern in equation_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_coefficients_and_variables(self, text: str) -> Tuple[Dict[str, float], List[str]]:
        """Extract coefficients and variables from equation"""
        coefficients = {}
        variables = []

        # Find terms like: 5x, -3y, x^2, 2x^2
        term_pattern = r'([+\-]?\s*\d*\.?\d*)\s*([a-z])(\^?\d)?'
        matches = re.findall(term_pattern, text, re.IGNORECASE)

        for coef_str, var, power in matches:
            # Clean coefficient
            coef_str = coef_str.replace(' ', '')
            if coef_str in ['', '+']:
                coef = 1.0
            elif coef_str == '-':
                coef = -1.0
            else:
                coef = float(coef_str)

            # Build key
            if power:
                key = f"{var}{power}"
            else:
                key = var

            coefficients[key] = coef

            if var not in variables:
                variables.append(var)

        return coefficients, variables

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        # Match integers and decimals
        number_pattern = r'-?\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        return [float(m) for m in matches if m]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        important_words = [
            'solve', 'find', 'calculate', 'determine', 'area', 'volume',
            'speed', 'velocity', 'force', 'energy', 'maximum', 'minimum',
            'real-world', 'application', 'practical', 'example'
        ]

        keywords = []
        text_lower = text.lower()

        for word in important_words:
            if word in text_lower:
                keywords.append(word)

        return keywords

    def _extract_context(self, question: str) -> Optional[str]:
        """Extract real-world context if present"""
        context_patterns = [
            r'(projectile|ball|rocket|arrow)',
            r'(height|distance|time|speed)',
            r'(real[- ]world|practical|application)',
            r'(profit|cost|price|revenue)',
            r'(age|years old|birthday)'
        ]

        for pattern in context_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                # Extract the sentence containing the context
                sentences = re.split(r'[.!?]', question)
                for sentence in sentences:
                    if match.group(1).lower() in sentence.lower():
                        return sentence.strip()

        return None

    def _parse_physics_problem(self, question: str) -> ParsedProblem:
        """Parse physics problems"""
        # Extract given values with units
        given = self._extract_physics_given(question)

        # Extract what to find
        find = self._extract_what_to_find(question)

        # Detect problem type
        problem_type = self._detect_physics_type(question)

        return ParsedProblem(
            problem_type=problem_type,
            raw_question=question,
            given=given,
            find=find,
            keywords=self._extract_keywords(question),
            context=self._extract_context(question)
        )

    def _extract_physics_given(self, question: str) -> Dict[str, Tuple[float, str]]:
        """Extract given values with units"""
        given = {}

        # Patterns: "mass = 5 kg", "velocity = 10 m/s", "v = 20 m/s"
        pattern = r'([a-z]+)\s*=\s*(\d+\.?\d*)\s*([a-z/]+)'
        matches = re.findall(pattern, question, re.IGNORECASE)

        for var_name, value, unit in matches:
            given[var_name.lower()] = (float(value), unit)

        return given

    def _extract_what_to_find(self, question: str) -> List[str]:
        """Extract what needs to be found"""
        find_patterns = [
            r'find (?:the )?([a-z]+)',
            r'calculate (?:the )?([a-z]+)',
            r'determine (?:the )?([a-z]+)',
            r'what is (?:the )?([a-z]+)'
        ]

        find = []
        for pattern in find_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            find.extend(matches)

        return list(set(find))  # Remove duplicates

    def _detect_physics_type(self, question: str) -> ProblemType:
        """Detect type of physics problem"""
        q_lower = question.lower()

        if any(term in q_lower for term in ['velocity', 'acceleration', 'distance', 'time']):
            return ProblemType.KINEMATICS

        if any(term in q_lower for term in ['force', 'mass', 'newton']):
            return ProblemType.DYNAMICS

        if any(term in q_lower for term in ['energy', 'work', 'power', 'joule']):
            return ProblemType.ENERGY

        if any(term in q_lower for term in ['current', 'voltage', 'resistance', 'ohm']):
            return ProblemType.ELECTRICITY

        return ProblemType.UNKNOWN

    def _parse_chemistry_problem(self, question: str) -> ParsedProblem:
        """Parse chemistry problems"""
        # Similar structure to physics
        problem_type = ProblemType.STOICHIOMETRY  # Default

        if 'ph' in question.lower():
            problem_type = ProblemType.PH_CALCULATION
        elif 'molarity' in question.lower() or 'concentration' in question.lower():
            problem_type = ProblemType.MOLARITY

        return ParsedProblem(
            problem_type=problem_type,
            raw_question=question,
            numbers=self._extract_numbers(question),
            keywords=self._extract_keywords(question)
        )

    def _parse_general_problem(self, question: str) -> ParsedProblem:
        """Parse general/unknown problems"""
        return ParsedProblem(
            problem_type=ProblemType.UNKNOWN,
            raw_question=question,
            numbers=self._extract_numbers(question),
            keywords=self._extract_keywords(question),
            context=self._extract_context(question)
        )


# Convenience function
def parse_problem(question: str, subject: str = "math") -> ParsedProblem:
    """Quick function to parse a problem"""
    parser = ProblemParser()
    return parser.parse(question, subject)
