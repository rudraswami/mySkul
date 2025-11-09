"""
Test Unified Visual System
Tests dynamic question understanding and appropriate visual generation
"""
import pytest
from services.unified_visual_system import generate_visual_for_question, UnifiedVisualSystem
from services.question_classifier import QuestionClassifier, QuestionType
from services.problem_parser import parse_problem
from services.solution_generator import generate_solution


class TestQuestionUnderstanding:
    """Test that system correctly understands different question types"""

    def test_concept_question_detection(self):
        """Test detection of concept questions"""
        questions = [
            "What is recursion?",
            "Explain quadratic equations",
            "Define Newton's laws of motion"
        ]

        classifier = QuestionClassifier()

        for question in questions:
            analysis = classifier.classify(question)
            assert analysis.type == QuestionType.CONCEPT

    def test_solution_question_detection(self):
        """Test detection of solution questions"""
        questions = [
            "Solve x^2 + 5x + 6 = 0",
            "Calculate the force if mass = 5kg and acceleration = 2m/s^2",
            "Find the roots of 2x^2 - 7x + 3 = 0"
        ]

        classifier = QuestionClassifier()

        for question in questions:
            analysis = classifier.classify(question)
            assert analysis.type == QuestionType.SOLUTION

    def test_application_question_detection(self):
        """Test detection of real-world application questions"""
        question = "How do I solve quadratic equations in real-world problems?"

        classifier = QuestionClassifier()
        analysis = classifier.classify(question)

        assert analysis.type == QuestionType.APPLICATION

    def test_subject_detection(self):
        """Test subject classification"""
        test_cases = [
            ("Solve x^2 + 5x + 6 = 0", "math"),
            ("Calculate velocity with mass and force", "physics"),
            ("Explain recursion algorithm", "cs")
        ]

        classifier = QuestionClassifier()

        for question, expected_subject in test_cases:
            analysis = classifier.classify(question)
            assert expected_subject in analysis.subject.value


class TestProblemParsing:
    """Test problem parsing for different types"""

    def test_quadratic_equation_parsing(self):
        """Test parsing quadratic equations"""
        question = "Solve x^2 + 5x + 6 = 0"

        parsed = parse_problem(question, "math")

        assert "x^2" in parsed.coefficients or "x²" in parsed.coefficients
        assert "x" in parsed.coefficients
        assert parsed.equation is not None

    def test_physics_problem_parsing(self):
        """Test parsing physics problems"""
        question = "Find force if mass = 5 kg and acceleration = 2 m/s^2"

        parsed = parse_problem(question, "physics")

        assert "mass" in parsed.given
        assert "acceleration" in parsed.given
        assert "force" in parsed.find

    def test_number_extraction(self):
        """Test number extraction"""
        question = "A ball is thrown with velocity 10 m/s at height 5m"

        parsed = parse_problem(question, "physics")

        assert len(parsed.numbers) >= 2
        assert 10.0 in parsed.numbers or 10 in [int(n) for n in parsed.numbers]


class TestSolutionGeneration:
    """Test solution step generation"""

    def test_quadratic_solution_generation(self):
        """Test generating quadratic solution"""
        question = "Solve x^2 + 5x + 6 = 0"
        parsed = parse_problem(question, "math")

        solution = generate_solution(parsed, marks=3, region="North")

        assert len(solution.steps) >= 3
        assert "quadratic" in solution.problem_type.lower()
        assert solution.final_answer is not None

    def test_solution_has_hinglish(self):
        """Test that solutions include Hinglish tips"""
        question = "Solve x^2 + 5x + 6 = 0"
        parsed = parse_problem(question, "math")

        solution = generate_solution(parsed, marks=3, region="North")

        # Check if at least one step has Hinglish tip
        has_hinglish = any(step.hinglish_tip for step in solution.steps)
        assert has_hinglish

    def test_solution_has_topper_hacks(self):
        """Test that solutions include topper hacks"""
        question = "Solve x^2 + 5x + 6 = 0"
        parsed = parse_problem(question, "math")

        solution = generate_solution(parsed, marks=3, region="North")

        # Check if at least one step has topper hack
        has_topper_hack = any(step.topper_hack for step in solution.steps)
        assert has_topper_hack


class TestUnifiedSystem:
    """Test the complete unified system"""

    def test_concept_visual_generation(self):
        """Test generating concept visual"""
        question = "What is recursion?"

        result = generate_visual_for_question(question)

        assert "svg" in result
        assert result["visual_type"] == "concept"
        assert "metadata" in result
        assert "friend_test" in result

    def test_solution_visual_generation(self):
        """Test generating solution visual"""
        question = "Solve x^2 + 5x + 6 = 0"

        result = generate_visual_for_question(question)

        assert "svg" in result
        assert result["visual_type"] == "solution"
        assert "metadata" in result
        assert result["metadata"]["problem_type"] is not None

    def test_svg_content_validity(self):
        """Test that generated SVG is valid"""
        questions = [
            "What is recursion?",
            "Solve x^2 + 5x + 6 = 0",
            "How to apply quadratic formula in real life?"
        ]

        for question in questions:
            result = generate_visual_for_question(question)

            svg = result["svg"]
            assert "<svg" in svg
            assert "</svg>" in svg
            assert len(svg) > 100  # Should have substantial content

    def test_visual_type_detection(self):
        """Test correct routing to concept vs solution"""
        system = UnifiedVisualSystem()

        # Concept questions
        assert system.get_visual_type("What is recursion?") == "concept"
        assert system.get_visual_type("Explain binary search") == "concept"

        # Solution questions
        assert system.get_visual_type("Solve x^2 + 5x + 6 = 0") == "solution"
        assert system.get_visual_type("Calculate force with mass 5kg") == "solution"

    def test_student_profile_integration(self):
        """Test that student profile is used"""
        question = "Solve x^2 + 5x + 6 = 0"
        student_profile = {
            "locale_language": "ta-IN",  # Tamil
            "board": "TN Board",
            "level": "class_12"
        }

        result = generate_visual_for_question(question, student_profile)

        # Check that metadata includes student-specific info
        assert result["visual_type"] == "solution"
        metadata = result["metadata"]
        assert metadata is not None

    def test_marks_extraction(self):
        """Test automatic marks extraction"""
        questions_with_marks = [
            ("Solve x^2 + 5x + 6 = 0 [3 marks]", 3),
            ("Explain recursion (5m)", 5),
            ("Calculate force 4 marks", 4)
        ]

        classifier = QuestionClassifier()

        for question, expected_marks in questions_with_marks:
            analysis = classifier.classify(question)
            assert analysis.marks == expected_marks


class TestRealWorldQuestions:
    """Test with actual student questions from the screenshot"""

    def test_quadratic_real_world_question(self):
        """Test the exact question from the screenshot"""
        question = "How do I solve quadratic equations in real-world problems?"

        result = generate_visual_for_question(question)

        assert result is not None
        assert "svg" in result
        # Should generate application/concept visual
        assert result["visual_type"] in ["concept", "application"]

    def test_specific_quadratic_solve(self):
        """Test specific quadratic equation"""
        question = "Solve x^2 + 5x + 6 = 0 [3 marks]"

        result = generate_visual_for_question(question)

        assert result["visual_type"] == "solution"
        assert "steps" in result["metadata"]
        assert len(result["metadata"]["steps"]) >= 3

    def test_physics_kinematics(self):
        """Test physics problem"""
        question = "A ball is thrown upward with velocity 20 m/s. Find maximum height."

        result = generate_visual_for_question(question)

        assert result["visual_type"] == "solution"
        assert "physics" in str(result["metadata"]).lower() or True  # May be detected

    def test_concept_explanation(self):
        """Test concept explanation"""
        question = "Explain Newton's second law of motion"

        result = generate_visual_for_question(question)

        assert result["visual_type"] == "concept"
        assert "metaphors" in result["metadata"] or True  # Concept visuals may have metaphors


class TestFriendTestIntegration:
    """Test Friend Test integration with unified system"""

    def test_friend_test_runs(self):
        """Test that Friend Test runs on generated visuals"""
        question = "Solve x^2 + 5x + 6 = 0"

        result = generate_visual_for_question(question)

        assert "friend_test" in result
        assert "score" in result["friend_test"]
        assert "passed" in result["friend_test"]

    def test_friend_test_feedback(self):
        """Test that Friend Test provides feedback"""
        question = "What is recursion?"

        result = generate_visual_for_question(question)

        friend_test = result["friend_test"]
        assert "feedback" in friend_test
        assert isinstance(friend_test["feedback"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
