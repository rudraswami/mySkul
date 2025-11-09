"""
Solution Step Generator
Generates step-by-step solutions with Hinglish annotations

For the example: "Solve x^2 + 5x + 6 = 0"
Generates:
Step 1: Identify a, b, c
Step 2: Apply quadratic formula
Step 3: Calculate discriminant
Step 4: Find roots
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .problem_parser import ParsedProblem, ProblemType
from .hinglish_annotations import generate_annotation


@dataclass
class SolutionStep:
    """Single step in solution"""
    step_number: int
    title: str              # "Step 1: Identify coefficients"
    explanation: str        # What to do
    formula: Optional[str] = None  # Formula if applicable
    calculation: Optional[str] = None  # Actual calculation
    result: Optional[str] = None  # Result of this step
    hinglish_tip: Optional[str] = None  # "Yaha dhyan se dekho"
    common_mistake: Optional[str] = None  # "90% yaha galti karte hain"
    topper_hack: Optional[str] = None  # "Topper trick: ..."


@dataclass
class CompleteSolution:
    """Complete step-by-step solution"""
    problem: str
    problem_type: str
    steps: List[SolutionStep]
    final_answer: str
    marks_breakdown: Dict[str, int]  # Which step is worth how many marks
    total_marks: int
    region: str = "North"


class SolutionGenerator:
    """Generates step-by-step solutions for different problem types"""

    def generate(
        self,
        parsed_problem: ParsedProblem,
        marks: int = 3,
        region: str = "North"
    ) -> CompleteSolution:
        """
        Generate complete solution

        Args:
            parsed_problem: Parsed problem from ProblemParser
            marks: Total marks for question
            region: Region for Hinglish annotations

        Returns:
            CompleteSolution with all steps
        """
        # Route to appropriate generator
        if parsed_problem.problem_type == ProblemType.QUADRATIC_EQUATION:
            return self._generate_quadratic_solution(parsed_problem, marks, region)

        elif parsed_problem.problem_type == ProblemType.LINEAR_EQUATION:
            return self._generate_linear_solution(parsed_problem, marks, region)

        elif parsed_problem.problem_type == ProblemType.KINEMATICS:
            return self._generate_kinematics_solution(parsed_problem, marks, region)

        else:
            return self._generate_generic_solution(parsed_problem, marks, region)

    def _generate_quadratic_solution(
        self,
        problem: ParsedProblem,
        marks: int,
        region: str
    ) -> CompleteSolution:
        """Generate solution for quadratic equations"""

        # Extract coefficients
        a = problem.coefficients.get('x^2', problem.coefficients.get('x²', 1.0))
        b = problem.coefficients.get('x', 0.0)
        c = problem.numbers[-1] if problem.numbers else 0.0

        steps = []

        # Step 1: Identify coefficients
        steps.append(SolutionStep(
            step_number=1,
            title="Identify a, b, c",
            explanation=f"For equation {problem.equation or 'ax² + bx + c = 0'}",
            calculation=f"a = {a}, b = {b}, c = {c}",
            result=f"Coefficients identified",
            hinglish_tip="⚠️ Yaha sign ka dhyan rakho - galat sign means galat answer!" if region == "North" else "⚠️ Mind the signs carefully!",
            common_mistake="❌ 90% students bhool jaate hain negative signs" if region == "North" else "❌ Most students forget negative signs",
            topper_hack="🏆 Topper tip: Pehle sabko = 0 ke form mein likho"
        ))

        # Step 2: Calculate discriminant
        discriminant = b*b - 4*a*c
        steps.append(SolutionStep(
            step_number=2,
            title="Calculate Discriminant (Δ)",
            explanation="Discriminant tells us about nature of roots",
            formula="Δ = b² - 4ac",
            calculation=f"Δ = ({b})² - 4({a})({c}) = {b*b} - {4*a*c}",
            result=f"Δ = {discriminant}",
            hinglish_tip="💡 Discriminant > 0 means 2 real roots" if discriminant > 0 else "💡 Discriminant = 0 means equal roots",
            common_mistake="❌ 4ac calculation mein sign galti hoti hai",
            topper_hack="🏆 Pehle discriminant check karo - nature pata chal jayega"
        ))

        # Step 3: Apply quadratic formula
        if discriminant >= 0:
            import math
            sqrt_d = math.sqrt(discriminant)
            root1 = (-b + sqrt_d) / (2*a)
            root2 = (-b - sqrt_d) / (2*a)

            steps.append(SolutionStep(
                step_number=3,
                title="Apply Quadratic Formula",
                explanation="Use the standard formula",
                formula="x = (-b ± √Δ) / 2a",
                calculation=f"x = ({-b} ± √{discriminant}) / {2*a}",
                result=f"x = ({-b} ± {sqrt_d:.2f}) / {2*a}",
                hinglish_tip="⚠️ ± means do answers aayenge" if region == "North" else "⚠️ ± means two answers",
                topper_hack="🏆 Formula yaad karo: minus b plus minus root delta by 2a"
            ))

            # Step 4: Final roots
            steps.append(SolutionStep(
                step_number=4,
                title="Calculate Final Roots",
                explanation="Solve for both values",
                calculation=f"x₁ = {(-b + sqrt_d):.2f} / {2*a} = {root1:.2f}\nx₂ = {(-b - sqrt_d):.2f} / {2*a} = {root2:.2f}",
                result=f"x = {root1:.2f} or x = {root2:.2f}",
                hinglish_tip="✓ Dono values verify kar lo" if region == "North" else "✓ Verify both values",
                topper_hack="🏆 Answer ko equation mein daalke check karo - 1 mark pakka"
            ))

            final_answer = f"x = {root1:.2f} or x = {root2:.2f}"

        else:
            steps.append(SolutionStep(
                step_number=3,
                title="No Real Roots",
                explanation="Discriminant is negative",
                result="No real roots exist (complex roots)",
                hinglish_tip="Δ < 0 means imaginary roots" if region == "North" else "Negative discriminant → imaginary",
            ))
            final_answer = "No real roots (Δ < 0)"

        # Marks breakdown
        marks_breakdown = {
            "Step 1": 1,
            "Step 2": 1,
            "Step 3": max(1, marks - 2),
            "Final Answer": 0  # Already counted
        }

        return CompleteSolution(
            problem=problem.raw_question,
            problem_type="Quadratic Equation",
            steps=steps,
            final_answer=final_answer,
            marks_breakdown=marks_breakdown,
            total_marks=marks,
            region=region
        )

    def _generate_linear_solution(
        self,
        problem: ParsedProblem,
        marks: int,
        region: str
    ) -> CompleteSolution:
        """Generate solution for linear equations"""

        steps = []

        # Simplified linear equation solver
        steps.append(SolutionStep(
            step_number=1,
            title="Rearrange Equation",
            explanation="Move all x terms to left, constants to right",
            hinglish_tip="⚠️ Side change karte waqt sign change karo" if region == "North" else "⚠️ Change signs when moving across =",
            common_mistake="❌ Sign change karna bhool jaate hain",
            topper_hack="🏆 Always write each step - partial marks milte hain"
        ))

        steps.append(SolutionStep(
            step_number=2,
            title="Solve for x",
            explanation="Divide both sides by coefficient of x",
            result="x = [value]",
            hinglish_tip="✓ Final answer underline karo - examiner ko dikhna chahiye" if region == "North" else "✓ Underline final answer",
            topper_hack="🏆 Answer check karo by substituting back"
        ))

        return CompleteSolution(
            problem=problem.raw_question,
            problem_type="Linear Equation",
            steps=steps,
            final_answer="x = [calculated value]",
            marks_breakdown={"Step 1": 1, "Step 2": marks - 1},
            total_marks=marks,
            region=region
        )

    def _generate_kinematics_solution(
        self,
        problem: ParsedProblem,
        marks: int,
        region: str
    ) -> CompleteSolution:
        """Generate solution for kinematics problems"""

        steps = []

        # Step 1: List given values
        given_str = "\n".join([f"{k} = {v[0]} {v[1]}" for k, v in problem.given.items()])
        steps.append(SolutionStep(
            step_number=1,
            title="List Given Values",
            explanation="Write down all known quantities",
            calculation=given_str or "u = ?, v = ?, a = ?, t = ?",
            hinglish_tip="⚠️ Units ko sath mein likhna zaroori hai" if region == "North" else "⚠️ Always write units",
            common_mistake="❌ Units miss karne pe marks cut jayenge",
            topper_hack="🏆 Given/Find table banao - clear dikhta hai"
        ))

        # Step 2: Choose formula
        steps.append(SolutionStep(
            step_number=2,
            title="Select Appropriate Formula",
            explanation="Choose formula based on given/find values",
            formula="v = u + at (or) s = ut + ½at² (or) v² = u² + 2as",
            hinglish_tip="💡 Jo nahi pata woh formula mein nahi hona chahiye" if region == "North" else "💡 Choose formula without unknown terms",
            topper_hack="🏆 Teen equations yaad karo - koi ek lagega"
        ))

        # Step 3: Substitute and solve
        steps.append(SolutionStep(
            step_number=3,
            title="Substitute Values",
            explanation="Put values in formula and calculate",
            result="[Calculated value with unit]",
            hinglish_tip="✓ Calculator use karo but steps likhna mat bhoolna" if region == "North" else "✓ Show calculation steps",
            topper_hack="🏆 Har step likhne se partial marks milte hain"
        ))

        return CompleteSolution(
            problem=problem.raw_question,
            problem_type="Kinematics",
            steps=steps,
            final_answer="[Final answer with unit]",
            marks_breakdown={"Step 1": 1, "Step 2": 1, "Step 3": marks - 2},
            total_marks=marks,
            region=region
        )

    def _generate_generic_solution(
        self,
        problem: ParsedProblem,
        marks: int,
        region: str
    ) -> CompleteSolution:
        """Generate generic solution template"""

        steps = []

        steps.append(SolutionStep(
            step_number=1,
            title="Understand the Problem",
            explanation="Read carefully and identify what is given and what to find",
            hinglish_tip="⚠️ Question ko 2 baar padho" if region == "North" else "⚠️ Read question twice",
            common_mistake="❌ Seedha formula lagana galat hai - pehle samjho",
            topper_hack="🏆 Given/Find separate karke likho"
        ))

        steps.append(SolutionStep(
            step_number=2,
            title="Apply Relevant Formula/Concept",
            explanation="Use appropriate method to solve",
            hinglish_tip="💡 Formula yaad nahi toh logic se try karo" if region == "North" else "💡 Use logic if formula forgotten",
            topper_hack="🏆 Diagram draw karne se samajh aata hai"
        ))

        steps.append(SolutionStep(
            step_number=3,
            title="Calculate and Write Answer",
            explanation="Show all steps clearly",
            result="[Final Answer]",
            hinglish_tip="✓ Units aur sign check karo" if region == "North" else "✓ Check units and signs",
            topper_hack="🏆 Box around final answer - looks professional"
        ))

        return CompleteSolution(
            problem=problem.raw_question,
            problem_type="General Problem",
            steps=steps,
            final_answer="[Solution here]",
            marks_breakdown={"Understanding": 1, "Method": 1, "Answer": marks - 2},
            total_marks=marks,
            region=region
        )


# Convenience function
def generate_solution(
    problem: ParsedProblem,
    marks: int = 3,
    region: str = "North"
) -> CompleteSolution:
    """Quick function to generate solution"""
    generator = SolutionGenerator()
    return generator.generate(problem, marks, region)
