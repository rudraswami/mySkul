"""
Question Type Classifier
Dynamically understands the question and classifies it for appropriate visual generation

Types:
- CONCEPT: Explain, define, what is... (uses emotional concept visuals)
- SOLUTION: Solve, calculate, find, how to solve... (uses step-by-step solution visuals)
- COMPARISON: Compare, difference between... (uses comparison visuals)
- APPLICATION: Real-world, practical... (uses application scenario visuals)
"""
from __future__ import annotations

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class QuestionType(Enum):
    """Question types for visual generation"""
    CONCEPT = "concept"          # Explain recursion, What is quadratic equation
    SOLUTION = "solution"        # Solve x^2 + 5x + 6 = 0, Calculate force
    COMPARISON = "comparison"    # Compare bubble sort vs quick sort
    APPLICATION = "application"  # How to use quadratic equations in real life
    PROCEDURE = "procedure"      # How to derive formula, Steps to prove


class Subject(Enum):
    """Subject classification"""
    MATHEMATICS = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    COMPUTER_SCIENCE = "cs"
    BIOLOGY = "biology"
    GENERAL = "general"


@dataclass
class QuestionAnalysis:
    """Result of question analysis"""
    type: QuestionType
    subject: Subject
    topic: str
    difficulty: str  # easy, medium, hard
    has_numbers: bool
    has_equation: bool
    marks: int
    keywords: List[str]
    confidence: float


class QuestionClassifier:
    """Classifies questions to determine the right visual generation approach"""

    # Question type patterns
    CONCEPT_PATTERNS = [
        r'\b(what is|define|explain|describe|meaning of|concept of)\b',
        r'\b(introduction to|overview of|basics of)\b',
        r'\b(tell me about|help me understand)\b'
    ]

    SOLUTION_PATTERNS = [
        r'\b(solve|calculate|find|compute|determine)\b',
        r'\b(what is the value|what is the answer)\b',
        r'\b(show solution|show steps|how to solve)\b',
        r'\bsolve\s+(?:for|the)\b'
    ]

    COMPARISON_PATTERNS = [
        r'\b(compare|difference|versus|vs|contrast)\b',
        r'\b(better|worse|advantages|disadvantages)\b',
        r'\b(which is|which one)\b'
    ]

    APPLICATION_PATTERNS = [
        r'\b(real[- ]world|practical|application|use case|example)\b',
        r'\b(how to use|how to apply|when to use)\b',
        r'\b(in daily life|in practice)\b'
    ]

    PROCEDURE_PATTERNS = [
        r'\b(how to derive|how to prove|steps to|procedure)\b',
        r'\b(derivation|proof|method)\b'
    ]

    # Subject patterns
    SUBJECT_PATTERNS = {
        Subject.MATHEMATICS: [
            r'\b(equation|formula|calculate|algebra|geometry|trigonometry)\b',
            r'\b(quadratic|linear|polynomial|integral|derivative)\b',
            r'\b(sin|cos|tan|log|sqrt|square root)\b',
            r'\b(area|volume|perimeter|probability|statistics)\b'
        ],
        Subject.PHYSICS: [
            r'\b(force|mass|velocity|acceleration|energy|power)\b',
            r'\b(motion|newton|kinematics|dynamics|momentum)\b',
            r'\b(electric|magnetic|current|voltage|resistance)\b',
            r'\b(wave|light|sound|optics|thermodynamics)\b'
        ],
        Subject.CHEMISTRY: [
            r'\b(reaction|molecule|atom|compound|element)\b',
            r'\b(mole|molarity|ph|acid|base|salt)\b',
            r'\b(organic|inorganic|physical chemistry)\b',
            r'\b(bond|ionic|covalent|oxidation|reduction)\b'
        ],
        Subject.COMPUTER_SCIENCE: [
            r'\b(algorithm|code|program|recursion|loop)\b',
            r'\b(data structure|array|tree|graph|stack|queue)\b',
            r'\b(sorting|searching|complexity|big O)\b',
            r'\b(class|object|inheritance|polymorphism)\b'
        ],
        Subject.BIOLOGY: [
            r'\b(cell|tissue|organ|organism|species)\b',
            r'\b(photosynthesis|respiration|digestion)\b',
            r'\b(dna|rna|protein|gene|chromosome)\b',
            r'\b(evolution|ecology|taxonomy)\b'
        ]
    }

    def classify(self, question: str) -> QuestionAnalysis:
        """
        Classify question and return detailed analysis

        Args:
            question: The student's question

        Returns:
            QuestionAnalysis with type, subject, and metadata
        """
        q_lower = question.lower()

        # Detect question type
        question_type = self._detect_type(q_lower)

        # Detect subject
        subject = self._detect_subject(q_lower)

        # Extract topic (main concept)
        topic = self._extract_topic(question, subject)

        # Check for numbers and equations
        has_numbers = bool(re.search(r'\d+', question))
        has_equation = bool(re.search(r'[=+\-*/^]', question))

        # Extract marks
        marks = self._extract_marks(question)

        # Extract keywords
        keywords = self._extract_keywords(q_lower)

        # Estimate difficulty
        difficulty = self._estimate_difficulty(question, has_numbers, has_equation)

        # Calculate confidence
        confidence = self._calculate_confidence(question_type, subject)

        return QuestionAnalysis(
            type=question_type,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            has_numbers=has_numbers,
            has_equation=has_equation,
            marks=marks,
            keywords=keywords,
            confidence=confidence
        )

    def _detect_type(self, q_lower: str) -> QuestionType:
        """Detect question type from patterns"""
        # Check each pattern type
        concept_score = sum(1 for p in self.CONCEPT_PATTERNS if re.search(p, q_lower))
        solution_score = sum(1 for p in self.SOLUTION_PATTERNS if re.search(p, q_lower))
        comparison_score = sum(1 for p in self.COMPARISON_PATTERNS if re.search(p, q_lower))
        application_score = sum(1 for p in self.APPLICATION_PATTERNS if re.search(p, q_lower))
        procedure_score = sum(1 for p in self.PROCEDURE_PATTERNS if re.search(p, q_lower))

        # Find highest score
        scores = {
            QuestionType.CONCEPT: concept_score,
            QuestionType.SOLUTION: solution_score,
            QuestionType.COMPARISON: comparison_score,
            QuestionType.APPLICATION: application_score,
            QuestionType.PROCEDURE: procedure_score
        }

        max_score = max(scores.values())

        # If solution has numbers or equations, prioritize it
        if solution_score > 0 and (re.search(r'\d+', q_lower) or '=' in q_lower):
            return QuestionType.SOLUTION

        # Otherwise return highest score
        if max_score > 0:
            return max(scores, key=scores.get)

        # Default: if has equation/numbers -> solution, else concept
        if re.search(r'[=+\-]', q_lower) or re.search(r'\bx\s*[+\-*/=]', q_lower):
            return QuestionType.SOLUTION

        return QuestionType.CONCEPT

    def _detect_subject(self, q_lower: str) -> Subject:
        """Detect subject from patterns"""
        scores = {}

        for subject, patterns in self.SUBJECT_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, q_lower))
            scores[subject] = score

        max_score = max(scores.values())

        if max_score > 0:
            return max(scores, key=scores.get)

        return Subject.GENERAL

    def _extract_topic(self, question: str, subject: Subject) -> str:
        """Extract main topic from question"""
        # Common topic patterns
        topic_patterns = [
            r'(?:about|of|on|regarding)\s+([a-zA-Z\s]+?)(?:\?|$|\[|in)',
            r'^(?:what is|explain|define)\s+([a-zA-Z\s]+?)(?:\?|$|\[)',
            r'\b(quadratic|linear|recursion|force|velocity|molecule|cell)\b[a-z\s]*'
        ]

        for pattern in topic_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: return first few meaningful words
        words = [w for w in question.split() if len(w) > 3][:3]
        return ' '.join(words) if words else "General"

    def _extract_marks(self, question: str) -> int:
        """Extract marks from question"""
        # [3 marks], (5m), 4 marks
        patterns = [
            r'\[(\d+)\s*marks?\]',
            r'\((\d+)\s*m\)',
            r'(\d+)\s*marks?'
        ]

        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 3  # Default

    def _extract_keywords(self, q_lower: str) -> List[str]:
        """Extract important keywords"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of',
                     'what', 'how', 'why', 'when', 'where', 'do', 'does', 'can', 'could',
                     'should', 'would', 'will', 'i', 'you', 'me', 'my', 'this', 'that'}

        words = re.findall(r'\b[a-z]{3,}\b', q_lower)
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords
        return list(dict.fromkeys(keywords))[:10]

    def _estimate_difficulty(self, question: str, has_numbers: bool, has_equation: bool) -> str:
        """Estimate question difficulty"""
        # Simple heuristic
        complexity_indicators = [
            'complex', 'advanced', 'difficult', 'hard', 'challenging',
            'derive', 'prove', 'justify'
        ]

        easy_indicators = [
            'simple', 'basic', 'easy', 'introductory', 'what is', 'define'
        ]

        q_lower = question.lower()

        if any(ind in q_lower for ind in complexity_indicators):
            return "hard"

        if any(ind in q_lower for ind in easy_indicators):
            return "easy"

        # If has complex equations or multiple steps
        if has_equation and len(question) > 100:
            return "hard"

        if has_numbers or has_equation:
            return "medium"

        return "easy"

    def _calculate_confidence(self, question_type: QuestionType, subject: Subject) -> float:
        """Calculate classification confidence"""
        # High confidence if clear patterns matched
        # This is a simplified version
        if subject != Subject.GENERAL:
            return 0.8
        return 0.6

    def is_solution_needed(self, question: str) -> bool:
        """Quick check if question needs step-by-step solution"""
        analysis = self.classify(question)
        return analysis.type in [QuestionType.SOLUTION, QuestionType.PROCEDURE]

    def get_visual_strategy(self, question: str) -> Dict[str, Any]:
        """
        Get recommended visual generation strategy

        Returns:
            Dict with strategy details:
            - visual_type: "concept" or "solution"
            - renderer: which renderer to use
            - emphasis: what to emphasize in visual
        """
        analysis = self.classify(question)

        if analysis.type in [QuestionType.SOLUTION, QuestionType.PROCEDURE]:
            return {
                "visual_type": "solution",
                "renderer": "solution_visual_renderer",
                "emphasis": "step_by_step",
                "show_work": True,
                "show_formula": True,
                "analysis": analysis
            }

        elif analysis.type == QuestionType.COMPARISON:
            return {
                "visual_type": "comparison",
                "renderer": "comparison_visual_renderer",
                "emphasis": "side_by_side",
                "show_differences": True,
                "analysis": analysis
            }

        else:  # CONCEPT or APPLICATION
            return {
                "visual_type": "concept",
                "renderer": "concept_visual_renderer",
                "emphasis": "understanding",
                "show_metaphors": True,
                "analysis": analysis
            }


# Convenience function
def classify_question(question: str) -> QuestionAnalysis:
    """Quick function to classify a question"""
    classifier = QuestionClassifier()
    return classifier.classify(question)
