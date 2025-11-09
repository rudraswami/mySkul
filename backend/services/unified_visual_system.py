"""
Unified Visual System - Main Facade
Dynamically understands questions and generates appropriate visuals

Routes to:
- Concept Visual System (for "What is...", "Explain...") → Emotional, metaphor-based
- Solution Visual System (for "Solve...", "Calculate...") → Step-by-step solutions

This is the single entry point that ai_service.py should use.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from .question_classifier import QuestionClassifier, QuestionType
from .problem_parser import ProblemParser
from .solution_generator import SolutionGenerator
from .solution_visual_renderer import SolutionVisualRenderer
from .dynamic_visual_sketch import create_visual_sketch
from .friend_test import friend_test_validation


class UnifiedVisualSystem:
    """Main facade for all visual generation"""

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = ProblemParser()
        self.solution_generator = SolutionGenerator()
        self.solution_renderer = SolutionVisualRenderer()

    def generate_visual(
        self,
        question: str,
        student_profile: Optional[Dict[str, Any]] = None,
        marks: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Generate appropriate visual for any question

        Args:
            question: The student's question
            student_profile: Optional student profile for personalization
            marks: Optional marks (extracted if not provided)

        Returns:
            Dict with:
            - svg: The SVG visual
            - visual_type: "concept" or "solution"
            - metadata: Additional info (steps, metaphors, etc.)
            - friend_test: Validation results
        """
        # Step 1: Classify the question
        analysis = self.classifier.classify(question)

        # Extract marks if not provided
        if marks is None:
            marks = analysis.marks

        # Determine region from student profile
        region = self._get_region(student_profile)

        # Step 2: Route to appropriate system
        if analysis.type in [QuestionType.SOLUTION, QuestionType.PROCEDURE]:
            return self._generate_solution_visual(
                question, analysis, marks, region, student_profile
            )

        elif analysis.type == QuestionType.COMPARISON:
            # TODO: Build comparison visual system
            return self._generate_concept_visual(
                question, marks, region, student_profile
            )

        else:  # CONCEPT or APPLICATION
            return self._generate_concept_visual(
                question, marks, region, student_profile
            )

    def _generate_solution_visual(
        self,
        question: str,
        analysis: Any,
        marks: int,
        region: str,
        student_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate step-by-step solution visual"""

        # Step 1: Parse the problem
        parsed_problem = self.parser.parse(
            question,
            subject=analysis.subject.value
        )

        # Step 2: Generate solution steps
        solution = self.solution_generator.generate(
            parsed_problem,
            marks=marks,
            region=region
        )

        # Step 3: Render as SVG
        svg = self.solution_renderer.render(solution)

        # Step 4: Run Friend Test
        metadata = {
            "visual_type": "solution",
            "problem_type": solution.problem_type,
            "num_steps": len(solution.steps),
            "has_emotional_content": True,  # Has Hinglish tips
            "marks": marks,
            "region": region
        }

        friend_result = friend_test_validation(svg, metadata, question)

        return {
            "svg": svg,
            "visual_type": "solution",
            "metadata": {
                "problem_type": solution.problem_type,
                "steps": [
                    {
                        "number": s.step_number,
                        "title": s.title,
                        "has_formula": s.formula is not None,
                        "has_tips": s.hinglish_tip is not None
                    }
                    for s in solution.steps
                ],
                "final_answer": solution.final_answer,
                "marks_breakdown": solution.marks_breakdown,
                "total_marks": marks,
                "subject": analysis.subject.value,
                "difficulty": analysis.difficulty
            },
            "friend_test": {
                "score": friend_result["score"],
                "passed": friend_result["passed"],
                "feedback": friend_result["feedback"]
            },
            "source": "solution_system"
        }

    def _generate_concept_visual(
        self,
        question: str,
        marks: int,
        region: str,
        student_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate concept explanation visual (existing emotional system)"""

        # Use our existing emotional concept system
        result = create_visual_sketch(
            question=question,
            student_profile=student_profile
        )

        # Run Friend Test
        friend_result = friend_test_validation(
            svg=result["svg"],
            metadata=result,
            concept=question
        )

        return {
            "svg": result["svg"],
            "visual_type": "concept",
            "metadata": {
                "metaphors_used": result.get("metaphors_used", []),
                "topper_hack": result.get("topper_hack"),
                "topper_rank": result.get("topper_rank"),
                "pyq_references": result.get("pyq_references", []),
                "region": result.get("region", region),
                "estimated_marks": result.get("estimated_marks", marks)
            },
            "friend_test": {
                "score": friend_result["score"],
                "passed": friend_result["passed"],
                "feedback": friend_result["feedback"]
            },
            "source": "concept_system"
        }

    def _get_region(self, student_profile: Optional[Dict]) -> str:
        """Extract region from student profile"""
        if not student_profile:
            return "North"

        locale = student_profile.get("locale_language", "hi-IN")

        locale_map = {
            "hi": "North", "pa": "North", "ur": "North",
            "ta": "South", "te": "South", "kn": "South", "ml": "South",
            "mr": "West", "gu": "West",
            "bn": "East", "or": "East", "as": "East"
        }

        lang_code = locale[:2].lower() if locale else "hi"
        return locale_map.get(lang_code, "North")

    def get_visual_type(self, question: str) -> str:
        """
        Quick check: what type of visual is needed?

        Returns:
            "solution" or "concept"
        """
        analysis = self.classifier.classify(question)

        if analysis.type in [QuestionType.SOLUTION, QuestionType.PROCEDURE]:
            return "solution"
        else:
            return "concept"


# Convenience function - main entry point
def generate_visual_for_question(
    question: str,
    student_profile: Optional[Dict[str, Any]] = None,
    marks: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main function: Generate appropriate visual for any question

    This is what ai_service.py should call.

    Args:
        question: The student's question
        student_profile: Optional student profile
        marks: Optional marks

    Returns:
        Dict with svg, metadata, and friend_test results

    Example:
        # Concept question
        result = generate_visual_for_question("What is recursion?")
        # Returns: concept visual with metaphors

        # Solution question
        result = generate_visual_for_question("Solve x^2 + 5x + 6 = 0")
        # Returns: step-by-step solution visual
    """
    system = UnifiedVisualSystem()
    return system.generate_visual(question, student_profile, marks)
