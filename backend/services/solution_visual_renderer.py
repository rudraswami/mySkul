"""
Solution Visual Renderer
Creates hand-drawn SVG visuals for step-by-step solutions

Layout:
┌─────────────────────────────────────┐
│ Problem: Solve x² + 5x + 6 = 0 [3m] │
├─────────────────────────────────────┤
│ Step 1: Identify a,b,c              │
│   a=1, b=5, c=6                     │
│   💡 Sign ka dhyan rakho            │
├─────────────────────────────────────┤
│ Step 2: Calculate Δ                 │
│   Δ = b² - 4ac = 25 - 24 = 1       │
│   🏆 Topper: Pehle discriminant     │
├─────────────────────────────────────┤
│ Step 3: Apply formula               │
│   x = (-b ± √Δ) / 2a                │
└─────────────────────────────────────┘
"""
from __future__ import annotations

import random
from typing import List, Tuple

from .solution_generator import CompleteSolution, SolutionStep


PALETTE = {
    "saffron": "#FF9933",
    "green": "#138808",
    "navy": "#000080",
    "yellow": "#FFD54F",
    "white": "#FFFFFF",
    "black": "#2C3E50",
    "lightblue": "#E3F2FD"
}


class SolutionVisualRenderer:
    """Renders solution steps as hand-drawn SVG"""

    def __init__(self):
        self.width = 700
        self.height = None  # Dynamic based on steps
        self.margin = 30
        self.step_height = 120  # Height per step
        self.header_height = 80

    def render(self, solution: CompleteSolution) -> str:
        """
        Render complete solution as SVG

        Args:
            solution: CompleteSolution from SolutionGenerator

        Returns:
            SVG string
        """
        random.seed(42)  # Deterministic jitter

        # Calculate total height
        num_steps = len(solution.steps)
        self.height = self.header_height + (num_steps * self.step_height) + 100

        svg_parts = []

        # SVG header
        svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">''')

        # Add styles
        svg_parts.append(self._get_styles())

        # Background
        svg_parts.append(f'<rect width="{self.width}" height="{self.height}" fill="{PALETTE["white"]}"/>')

        # Header: Problem statement
        svg_parts.append(self._render_header(solution))

        # Render each step
        y_offset = self.header_height
        for step in solution.steps:
            svg_parts.append(self._render_step(step, y_offset))
            y_offset += self.step_height

        # Final answer box
        svg_parts.append(self._render_final_answer(solution, y_offset))

        # Close SVG
        svg_parts.append('</svg>')

        return ''.join(svg_parts)

    def _get_styles(self) -> str:
        """CSS styles for SVG"""
        return '''
        <style>
            .problem-text { font-family: system-ui, Arial; font-size: 18px; font-weight: bold; fill: #000080; }
            .marks-badge { font-family: system-ui, Arial; font-size: 14px; fill: #FF9933; }
            .step-title { font-family: system-ui, Arial; font-size: 16px; font-weight: bold; fill: #2C3E50; }
            .step-text { font-family: system-ui, Arial; font-size: 14px; fill: #2C3E50; }
            .formula { font-family: 'Courier New', monospace; font-size: 15px; fill: #000080; font-weight: bold; }
            .tip-text { font-family: system-ui, Arial; font-size: 12px; fill: #138808; }
            .mistake-text { font-family: system-ui, Arial; font-size: 11px; fill: #D32F2F; }
            .topper-text { font-family: system-ui, Arial; font-size: 12px; fill: #FF6F00; }
            .final-answer { font-family: system-ui, Arial; font-size: 20px; font-weight: bold; fill: #138808; }
        </style>
        '''

    def _render_header(self, solution: CompleteSolution) -> str:
        """Render problem statement header"""
        parts = []

        # Border box around problem
        box = self._draw_hand_drawn_rect(
            self.margin, 20,
            self.width - 2*self.margin, self.header_height - 30,
            PALETTE["navy"], fill=PALETTE["lightblue"]
        )
        parts.append(box)

        # Problem text
        problem_text = solution.problem[:80] + "..." if len(solution.problem) > 80 else solution.problem
        parts.append(f'<text x="{self.margin + 15}" y="50" class="problem-text">{self._escape(problem_text)}</text>')

        # Marks badge
        parts.append(f'<text x="{self.width - 100}" y="50" class="marks-badge">💯 {solution.total_marks} marks</text>')

        # Problem type
        parts.append(f'<text x="{self.margin + 15}" y="70" class="step-text" font-style="italic">{solution.problem_type}</text>')

        return ''.join(parts)

    def _render_step(self, step: SolutionStep, y_offset: float) -> str:
        """Render a single solution step"""
        parts = []

        # Step box
        step_box = self._draw_hand_drawn_rect(
            self.margin, y_offset + 10,
            self.width - 2*self.margin, self.step_height - 20,
            PALETTE["black"], fill=PALETTE["white"]
        )
        parts.append(step_box)

        current_y = y_offset + 35

        # Step title
        parts.append(f'<text x="{self.margin + 15}" y="{current_y}" class="step-title">Step {step.step_number}: {self._escape(step.title)}</text>')
        current_y += 25

        # Explanation
        if step.explanation:
            parts.append(f'<text x="{self.margin + 20}" y="{current_y}" class="step-text">{self._escape(step.explanation)}</text>')
            current_y += 20

        # Formula (if present) - highlighted
        if step.formula:
            formula_box = self._draw_hand_drawn_rect(
                self.margin + 15, current_y - 15,
                self.width - 2*self.margin - 30, 25,
                PALETTE["navy"], fill="#FFF3E0"
            )
            parts.append(formula_box)
            parts.append(f'<text x="{self.margin + 25}" y="{current_y}" class="formula">{self._escape(step.formula)}</text>')
            current_y += 25

        # Calculation
        if step.calculation:
            # Split multiline calculations
            calc_lines = step.calculation.split('\n')
            for line in calc_lines:
                parts.append(f'<text x="{self.margin + 25}" y="{current_y}" class="step-text" font-family="monospace">{self._escape(line)}</text>')
                current_y += 18

        # Result (bold)
        if step.result:
            parts.append(f'<text x="{self.margin + 25}" y="{current_y}" class="step-text" font-weight="bold">→ {self._escape(step.result)}</text>')

        # Annotations (tips, mistakes, hacks) - right side
        annotation_x = self.width - 250
        annotation_y = y_offset + 35

        if step.hinglish_tip:
            parts.append(f'<text x="{annotation_x}" y="{annotation_y}" class="tip-text">{self._escape(step.hinglish_tip)}</text>')
            annotation_y += 15

        if step.common_mistake:
            parts.append(f'<text x="{annotation_x}" y="{annotation_y}" class="mistake-text">{self._escape(step.common_mistake)}</text>')
            annotation_y += 15

        if step.topper_hack:
            parts.append(f'<text x="{annotation_x}" y="{annotation_y}" class="topper-text">{self._escape(step.topper_hack)}</text>')

        return ''.join(parts)

    def _render_final_answer(self, solution: CompleteSolution, y_offset: float) -> str:
        """Render final answer in a highlighted box"""
        parts = []

        # Answer box (green)
        answer_box = self._draw_hand_drawn_rect(
            self.margin, y_offset + 10,
            self.width - 2*self.margin, 60,
            PALETTE["green"], fill="#E8F5E9", stroke_width=3
        )
        parts.append(answer_box)

        # Answer text
        parts.append(f'<text x="{self.width/2}" y="{y_offset + 35}" class="final-answer" text-anchor="middle">Final Answer:</text>')
        parts.append(f'<text x="{self.width/2}" y="{y_offset + 55}" class="final-answer" text-anchor="middle">{self._escape(solution.final_answer)}</text>')

        return ''.join(parts)

    def _draw_hand_drawn_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        stroke: str,
        fill: str = "none",
        stroke_width: float = 2.0
    ) -> str:
        """Draw hand-drawn rectangle using paths"""
        # Add jitter for hand-drawn effect
        jitter = 2.0

        # Four corners with jitter
        p1 = (x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter))
        p2 = (x + width + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter))
        p3 = (x + width + random.uniform(-jitter, jitter), y + height + random.uniform(-jitter, jitter))
        p4 = (x + random.uniform(-jitter, jitter), y + height + random.uniform(-jitter, jitter))

        # Create path
        path = f'M {p1[0]:.1f},{p1[1]:.1f} '
        path += f'L {p2[0]:.1f},{p2[1]:.1f} '
        path += f'L {p3[0]:.1f},{p3[1]:.1f} '
        path += f'L {p4[0]:.1f},{p4[1]:.1f} Z'

        return f'<path d="{path}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'

    def _escape(self, text: str) -> str:
        """Escape XML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))


# Convenience function
def render_solution_visual(solution: CompleteSolution) -> str:
    """Quick function to render solution visual"""
    renderer = SolutionVisualRenderer()
    return renderer.render(solution)
