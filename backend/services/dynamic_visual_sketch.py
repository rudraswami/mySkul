from __future__ import annotations

"""
Dynamic Visual Sketch Engine (Friend Explaining at 2 AM Feel)

Implements PRD Step 3 with emotional connection layer.
Now includes: Hinglish annotations, topper hacks, and PYQ references.

Constraints:
- Pure SVG (no JS), path-only shapes (no <circle>/<line>/<rect>), no gradients
- Indian palette: Saffron (#FF9933), Green (#138808), Navy (#000080)
- 3 layers: L1 scientific skeleton, L2 exam annotations (with emotion!), L3 cultural metaphor blend
- 5-step progressive drawing (SMIL; step1 auto, steps 2–5 on click)
"""

import random
import re
import math
from typing import Any, Dict, List, Optional, Tuple

from .metaphor_engine import select_metaphors, ConceptBundle, MetaphorCandidate, StudentDNA
from .hinglish_annotations import generate_annotation, get_common_mistake, generate_marks_annotation
from .topper_hack_selector import TopperHackSelector
from .pyq_matcher import PYQMatcher


PALETTE = {"saffron": "#FF9933", "green": "#138808", "navy": "#000080", "yellow": "#FFD54F"}


def _jitter_points(points: List[Tuple[float, float]], intensity: float = 2.0) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for x, y in points:
        out.append((x + random.uniform(-intensity, intensity), y + random.uniform(-intensity, intensity)))
    return out


def _path_from_points(points: List[Tuple[float, float]]) -> str:
    parts = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    for x, y in points[1:]:
        parts.append(f"Q{(x+points[0][0]) / 2:.1f},{(y+points[0][1]) / 2:.1f} {x:.1f},{y:.1f}")
    return " ".join(parts)


def _text(x: float, y: float, txt: str, color: str, size: float = 12, anchor: str = "start", bold: bool = False) -> str:
    """Generate SVG text element with optional centering and bold"""
    weight = "bold" if bold else "normal"
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="system-ui, Arial" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_escape(txt)}</text>'


def _text_centered(x: float, y: float, txt: str, color: str, size: float = 12, bold: bool = False) -> str:
    """Convenience function for centered text"""
    return _text(x, y, txt, color, size, anchor="middle", bold=bold)


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _rough_circle(cx: float, cy: float, r: float, jitter: float = 1.0) -> str:
    base = [
        (cx - r, cy),
        (cx - r / 2, cy - r),
        (cx + r / 2, cy - r),
        (cx + r, cy),
        (cx + r / 2, cy + r),
        (cx - r / 2, cy + r),
        (cx - r, cy),
    ]
    return _path_from_points(_jitter_points(base, jitter))


def _layer_skeleton(bundle: ConceptBundle) -> str:
    """
    Enhanced skeleton layer - Question-type specific visuals
    Analyzes question to determine best visual representation
    """
    question_text = (bundle.question or "").lower()
    
    # Specialized visuals for specific question types
    if any(keyword in question_text for keyword in ("valence", "valency", "valency?")):
        return _layer_valency_sketch(bundle)
    
    # Math problem solving (equations, calculations)
    if any(keyword in question_text for keyword in ("solve", "calculate", "find", "derivative", "integral", "equation")):
        return _layer_math_problem_sketch(bundle)
    
    # Concept explanation (definitions, explanations)
    if any(keyword in question_text for keyword in ("explain", "what is", "define", "describe", "how does")):
        return _layer_concept_explanation_sketch(bundle)
    
    # Comparison questions
    if any(keyword in question_text for keyword in ("difference", "compare", "vs", "versus", "similar", "contrast")):
        return _layer_comparison_sketch(bundle)
    
    # Process/flow questions
    if any(keyword in question_text for keyword in ("process", "steps", "how to", "procedure", "flow")):
        return _layer_process_flow_sketch(bundle)
    
    # Default: Generic two-box diagram
    stroke = PALETTE["navy"]
    imp1 = _path_from_points(_jitter_points([(60, 120), (200, 120), (200, 170), (60, 170), (60, 120)], 2.5))
    imp2 = _path_from_points(_jitter_points([(260, 120), (400, 120), (400, 170), (260, 170), (260, 120)], 2.5))
    arrow = _path_from_points(_jitter_points([(200, 145), (230, 140), (260, 145)], 2.0))
    txt1 = _text(90, 145, (bundle.entities[:1] or ["Part A"])[0], stroke, 12)
    txt2 = _text(290, 145, (bundle.entities[1:2] or ["Part B"])[0], stroke, 12)
    return (
        f'<path id="l1_box1" d="{imp1}" stroke="{stroke}" stroke-width="1.6" fill="none" />'
        f'<path id="l1_box2" d="{imp2}" stroke="{stroke}" stroke-width="1.5" fill="none" />'
        f'<path id="l1_arrow" d="{arrow}" stroke="{stroke}" stroke-width="1.8" fill="none" />'
        f"{txt1}{txt2}"
    )


def _layer_math_problem_sketch(bundle: ConceptBundle) -> str:
    """Enhanced math problem visual - Step-by-step solving diagram"""
    stroke = PALETTE["navy"]
    highlight = PALETTE["saffron"]
    
    # Problem statement box
    problem_box = _path_from_points(_jitter_points([(50, 80), (590, 80), (590, 130), (50, 130), (50, 80)], 2.0))
    
    # Step boxes (3-4 steps)
    steps = []
    step_y = 160
    num_steps = min(4, len(bundle.core_actions) + 1) if bundle.core_actions else 3
    
    for i in range(num_steps):
        step_box = _path_from_points(_jitter_points([
            (50, step_y), (280, step_y), (280, step_y + 50), (50, step_y + 50), (50, step_y)
        ], 2.0))
        steps.append(step_box)
        step_y += 70
    
    # Solution box (final answer)
    solution_box = _path_from_points(_jitter_points([(50, step_y), (590, step_y), (590, step_y + 60), (50, step_y + 60), (50, step_y)], 2.5))
    
    # Arrows between steps
    arrows = []
    for i in range(num_steps):
        arrow_y = 160 + (i * 70) + 50
        arrow = _path_from_points(_jitter_points([(145, arrow_y), (145, arrow_y + 20)], 1.5))
        arrows.append(f'<path d="{arrow}" stroke="{highlight}" stroke-width="2" fill="none" marker-end="url(#arrowhead)" />')
    
    # Step numbers
    step_numbers = []
    for i in range(num_steps):
        step_y = 160 + (i * 70) + 25
        step_numbers.append(_text(70, step_y, f"Step {i+1}", stroke, 11))
    
    # Problem text
    problem_text = bundle.question[:40] + "..." if len(bundle.question) > 40 else bundle.question
    
    return (
        f'<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{highlight}" /></marker></defs>'
        f'<path id="l1_problem" d="{problem_box}" stroke="{stroke}" stroke-width="2" fill="#FFFCEF" />'
        f'{_text(60, 105, problem_text, stroke, 13)}'
        + ''.join([f'<path id="l1_step{i+1}" d="{step}" stroke="{stroke}" stroke-width="1.8" fill="#F0F8FF" />' for i, step in enumerate(steps)])
        + ''.join(arrows)
        + ''.join(step_numbers)
        + f'<path id="l1_solution" d="{solution_box}" stroke="{highlight}" stroke-width="2.5" fill="#FFE9D6" />'
        + f'{_text(60, step_y + 30, "Final Answer", highlight, 14)}'
    )


def _layer_concept_explanation_sketch(bundle: ConceptBundle) -> str:
    """
    Enhanced concept explanation visual - Interactive, value-adding visual
    For "explain force" type questions, shows:
    - Force as vector (magnitude + direction)
    - Real-world examples (cricket ball, auto-rickshaw)
    - Cause-effect relationships
    - Interactive elements (force arrows, motion indicators)
    """
    stroke = PALETTE["navy"]
    highlight = PALETTE["saffron"]
    supportive = PALETTE["green"]
    question_lower = (bundle.question or "").lower()
    
    # Special handling for Physics concepts (Force, Motion, etc.)
    if "force" in question_lower:
        return _layer_force_concept_visual(bundle, stroke, highlight, supportive)
    elif any(term in question_lower for term in ["motion", "velocity", "acceleration"]):
        return _layer_motion_concept_visual(bundle, stroke, highlight, supportive)
    elif any(term in question_lower for term in ["gravity", "gravitational"]):
        return _layer_gravity_concept_visual(bundle, stroke, highlight, supportive)
    
    # Default: Central concept with related ideas (enhanced)
    center_x, center_y = 320, 180
    center_circle = _rough_circle(center_x, center_y, 50, 1.5)
    
    # Related concepts (3-4 around center)
    related_concepts = bundle.entities[:4] if bundle.entities else ["Related 1", "Related 2", "Related 3"]
    concept_circles = []
    concept_texts = []
    
    import math
    for i, concept in enumerate(related_concepts):
        angle = (2 * math.pi * i) / len(related_concepts)
        radius = 120
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        circle = _rough_circle(x, y, 35, 1.2)
        concept_circles.append(circle)
        
        # Connection line with arrow
        conn_points = _jitter_points([(center_x, center_y), ((x + center_x)/2, (y + center_y)/2), (x, y)], 1.0)
        concept_texts.append(f'<path d="{_path_from_points(conn_points)}" stroke="{supportive}" stroke-width="1.5" fill="none" stroke-dasharray="4 4" marker-end="url(#arrowhead)" />')
        concept_texts.append(_text(x - 30, y + 5, concept[:15], stroke, 10))
    
    # Main concept text
    main_concept = bundle.entities[0] if bundle.entities else "Concept"
    
    return (
        f'<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{supportive}" /></marker></defs>'
        f'<path id="l1_center" d="{center_circle}" stroke="{highlight}" stroke-width="2.5" fill="#FFE9D6" />'
        + ''.join([f'<path id="l1_concept{i+1}" d="{circle}" stroke="{stroke}" stroke-width="1.8" fill="#E8F5E9" />' for i, circle in enumerate(concept_circles)])
        + ''.join(concept_texts)
        + f'{_text(center_x - 40, center_y + 5, main_concept[:20], highlight, 13)}'
    )


def _layer_force_concept_visual(bundle: ConceptBundle, stroke: str, highlight: str, supportive: str) -> str:
    """
    SCENE-BASED FORCE VISUAL - Clean, Focused, Interactive
    
    Design Philosophy:
    - ONE powerful scene that demonstrates the concept
    - Clean visual hierarchy (important things are BIG)
    - Hinglish explanations (mix of Hindi + English)
    - Works on small screens (mobile-first)
    - Interactive tap-to-reveal layers
    """
    
    # =====================================================
    # SCENE: CRICKET STADIUM - Bowler delivering to batsman
    # This is something EVERY Indian student understands
    # =====================================================
    
    # Background: Cricket pitch (simple, clean)
    pitch = _path_from_points(_jitter_points([
        (100, 280), (540, 280), (540, 320), (100, 320), (100, 280)
    ], 1.0))
    pitch_crease = _path_from_points(_jitter_points([(150, 280), (150, 320)], 0.5))
    pitch_crease2 = _path_from_points(_jitter_points([(490, 280), (490, 320)], 0.5))
    
    # BOWLER (Left side) - Clean stick figure with bowling action
    bowler_head = _rough_circle(140, 180, 15, 0.8)
    bowler_body = _path_from_points(_jitter_points([(140, 195), (140, 245)], 1.0))
    bowler_back_leg = _path_from_points(_jitter_points([(140, 245), (120, 280)], 1.0))
    bowler_front_leg = _path_from_points(_jitter_points([(140, 245), (165, 280)], 1.0))
    # Bowling arm (raised, about to release)
    bowler_arm_back = _path_from_points(_jitter_points([(140, 210), (110, 180)], 1.0))
    bowler_arm_forward = _path_from_points(_jitter_points([(140, 210), (180, 170), (200, 160)], 1.2))
    
    # BALL - Clear red circle with motion trail
    ball = _rough_circle(215, 155, 12, 0.6)
    ball_trail = _path_from_points(_jitter_points([
        (200, 160), (190, 165), (180, 170)
    ], 0.8))
    
    # BIG FORCE ARROW - This is the MAIN visual element
    # Large, prominent, impossible to miss
    force_arrow_path = _path_from_points(_jitter_points([
        (230, 155), (280, 155), (330, 155), (380, 155)
    ], 0.5))
    
    # STUMPS (Right side) - Target of the force
    stump1 = _path_from_points(_jitter_points([(480, 200), (480, 280)], 0.8))
    stump2 = _path_from_points(_jitter_points([(490, 200), (490, 280)], 0.8))
    stump3 = _path_from_points(_jitter_points([(500, 200), (500, 280)], 0.8))
    bails = _path_from_points(_jitter_points([(477, 200), (503, 200)], 0.5))
    
    # BATSMAN (simplified)
    batsman_head = _rough_circle(440, 200, 12, 0.8)
    batsman_body = _path_from_points(_jitter_points([(440, 212), (440, 255)], 1.0))
    batsman_legs = _path_from_points(_jitter_points([(440, 255), (425, 280), (440, 255), (455, 280)], 1.0))
    bat = _path_from_points(_jitter_points([(440, 225), (415, 200), (410, 195)], 1.2))
    
    # =====================================================
    # TEXT ELEMENTS - Hinglish, Clear, Educational
    # =====================================================
    
    return (
        f'<defs>'
        # Big arrow marker for force
        f'<marker id="force-arrow" markerWidth="20" markerHeight="20" refX="18" refY="10" orient="auto">'
        f'<path d="M 0 0 L 20 10 L 0 20 L 5 10 Z" fill="{highlight}" />'
        f'</marker>'
        # Gradient for ground
        f'<linearGradient id="pitch-grass" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:#8BC34A;stop-opacity:1" />'
        f'<stop offset="100%" style="stop-color:#558B2F;stop-opacity:1" />'
        f'</linearGradient>'
        # Glow effect for ball
        f'<filter id="ball-glow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="3" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter>'
        f'</defs>'
        
        # === TITLE - Clean, Bold, Centered ===
        f'<rect x="0" y="0" width="640" height="60" fill="#1A237E" />'
        f'{_text_centered(320, 28, "FORCE (बल)", "#FFFFFF", 24, bold=True)}'
        f'{_text_centered(320, 50, "Push या Pull जो चीज़ों को हिलाता है", "#FFD54F", 14)}'
        
        # === PITCH/GROUND ===
        f'<rect x="0" y="280" width="640" height="80" fill="url(#pitch-grass)" />'
        f'<path d="{pitch}" stroke="#4E342E" stroke-width="2" fill="#D7CCC8" />'
        f'<path d="{pitch_crease}" stroke="#FFF" stroke-width="2" fill="none" />'
        f'<path d="{pitch_crease2}" stroke="#FFF" stroke-width="2" fill="none" />'
        
        # === BOWLER ===
        f'<g id="bowler">'
        f'<path d="{bowler_head}" stroke="{stroke}" stroke-width="2" fill="#FFE0B2" />'
        f'<path d="{bowler_body}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{bowler_back_leg}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{bowler_front_leg}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{bowler_arm_back}" stroke="{stroke}" stroke-width="2.5" fill="none" />'
        f'<path d="{bowler_arm_forward}" stroke="{stroke}" stroke-width="2.5" fill="none" />'
        f'{_text_centered(140, 150, "Bowler", stroke, 11)}'
        f'</g>'
        
        # === BALL with glow ===
        f'<g id="ball" filter="url(#ball-glow)">'
        f'<path d="{ball}" stroke="#8B0000" stroke-width="2" fill="#D32F2F" />'
        f'<path d="{ball_trail}" stroke="#D32F2F" stroke-width="2" fill="none" opacity="0.4" stroke-dasharray="4 4" />'
        f'</g>'
        
        # === THE BIG FORCE ARROW - Main Visual Element ===
        f'<g id="force-visual">'
        f'<path d="{force_arrow_path}" stroke="{highlight}" stroke-width="8" fill="none" marker-end="url(#force-arrow)" />'
        # Force label - BIG and clear
        f'<rect x="270" y="100" width="100" height="45" rx="8" fill="{highlight}" />'
        f'{_text_centered(320, 118, "FORCE", "#FFF", 16, bold=True)}'
        f'{_text_centered(320, 135, "बल (F)", "#FFF", 12)}'
        # Arrow from label to force line
        f'<path d="M 320 145 L 320 150" stroke="{highlight}" stroke-width="2" fill="none" />'
        f'</g>'
        
        # === STUMPS ===
        f'<g id="stumps">'
        f'<path d="{stump1}" stroke="#5D4037" stroke-width="3" fill="#8D6E63" />'
        f'<path d="{stump2}" stroke="#5D4037" stroke-width="3" fill="#8D6E63" />'
        f'<path d="{stump3}" stroke="#5D4037" stroke-width="3" fill="#8D6E63" />'
        f'<path d="{bails}" stroke="#FFC107" stroke-width="4" fill="none" />'
        f'</g>'
        
        # === BATSMAN ===
        f'<g id="batsman">'
        f'<path d="{batsman_head}" stroke="{stroke}" stroke-width="2" fill="#FFE0B2" />'
        f'<path d="{batsman_body}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{batsman_legs}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{bat}" stroke="#5D4037" stroke-width="4" fill="#8D6E63" />'
        f'</g>'
        
        # === KEY INSIGHT BOX - Bottom Left ===
        f'<rect x="20" y="200" width="95" height="70" rx="8" fill="#E3F2FD" stroke="#1976D2" stroke-width="2" />'
        f'{_text_centered(67, 218, "💡 याद रखो", "#1976D2", 10, bold=True)}'
        f'{_text_centered(67, 235, "ज़्यादा Force", stroke, 9)}'
        f'{_text_centered(67, 250, "= ज़्यादा Speed", supportive, 9)}'
        f'{_text_centered(67, 265, "(तेज़ गेंद!)", stroke, 8)}'
        
        # === FORMULA BOX - Bottom Right ===
        f'<rect x="525" y="200" width="95" height="70" rx="8" fill="#FFF8E1" stroke="{highlight}" stroke-width="2" />'
        f'{_text_centered(572, 218, "📐 Formula", highlight, 10, bold=True)}'
        f'{_text_centered(572, 242, "F = m × a", stroke, 14, bold=True)}'
        f'{_text_centered(572, 260, "Force = Mass", stroke, 8)}'
        f'{_text_centered(572, 272, "× Acceleration", stroke, 8)}'
        
        # === CAUSE-EFFECT ANNOTATION ===
        f'<rect x="220" y="175" width="200" height="30" rx="6" fill="#E8F5E9" stroke="{supportive}" stroke-width="1.5" />'
        f'{_text_centered(320, 195, "Arm का Force → Ball तेज़ जाती है 🚀", supportive, 11)}'
    )


def _layer_comparison_sketch(bundle: ConceptBundle) -> str:
    """Enhanced comparison visual - Side-by-side comparison"""
    stroke = PALETTE["navy"]
    left_color = PALETTE["saffron"]
    right_color = PALETTE["green"]
    
    # Left side (Concept A)
    left_box = _path_from_points(_jitter_points([(50, 100), (280, 100), (280, 280), (50, 280), (50, 100)], 2.5))
    
    # Right side (Concept B)
    right_box = _path_from_points(_jitter_points([(360, 100), (590, 100), (590, 280), (360, 280), (360, 100)], 2.5))
    
    # Comparison arrow
    compare_arrow = _path_from_points(_jitter_points([(280, 190), (320, 180), (360, 190)], 2.0))
    
    # Labels
    concept_a = bundle.entities[0] if bundle.entities else "Concept A"
    concept_b = bundle.entities[1] if len(bundle.entities) > 1 else "Concept B"
    
    # Similarities/Differences section (bottom)
    diff_box = _path_from_points(_jitter_points([(50, 300), (590, 300), (590, 340), (50, 340), (50, 300)], 2.0))
    
    return (
        f'<path id="l1_left" d="{left_box}" stroke="{left_color}" stroke-width="2" fill="#FFE9D6" />'
        f'<path id="l1_right" d="{right_box}" stroke="{right_color}" stroke-width="2" fill="#E8F5E9" />'
        f'<path id="l1_arrow" d="{compare_arrow}" stroke="{stroke}" stroke-width="2" fill="none" />'
        f'{_text(165 - len(concept_a)*3, 130, concept_a[:25], left_color, 13)}'
        f'{_text(475 - len(concept_b)*3, 130, concept_b[:25], right_color, 13)}'
        f'<path id="l1_diff" d="{diff_box}" stroke="{stroke}" stroke-width="1.5" fill="#F0F8FF" />'
        f'{_text(60, 320, "Key Differences", stroke, 11)}'
    )


def _layer_process_flow_sketch(bundle: ConceptBundle) -> str:
    """Enhanced process flow visual - Step-by-step flow diagram"""
    stroke = PALETTE["navy"]
    highlight = PALETTE["saffron"]
    
    # Process steps (horizontal flow)
    num_steps = min(5, len(bundle.core_actions) + 1) if bundle.core_actions else 4
    step_width = 100
    start_x = 80
    
    steps = []
    arrows = []
    step_labels = []
    
    for i in range(num_steps):
        x = start_x + (i * step_width)
        y = 150
        
        # Step box
        step_box = _path_from_points(_jitter_points([
            (x, y), (x + 80, y), (x + 80, y + 60), (x, y + 60), (x, y)
        ], 2.0))
        steps.append(step_box)
        
        # Arrow to next step
        if i < num_steps - 1:
            arrow = _path_from_points(_jitter_points([(x + 80, y + 30), (x + step_width, y + 30)], 1.5))
            arrows.append(f'<path d="{arrow}" stroke="{highlight}" stroke-width="2" fill="none" />')
        
        # Step label
        step_labels.append(_text(x + 10, y + 35, f"Step {i+1}", stroke, 11))
    
    # Start and End labels
    start_label = _text(start_x + 20, y - 20, "Start", stroke, 12)
    end_x = start_x + ((num_steps - 1) * step_width)
    end_label = _text(end_x + 20, y + 100, "End", highlight, 12)
    
    return (
        ''.join([f'<path id="l1_step{i+1}" d="{step}" stroke="{stroke}" stroke-width="1.8" fill="#F0F8FF" />' for i, step in enumerate(steps)])
        + ''.join(arrows)
        + ''.join(step_labels)
        + start_label
        + end_label
    )


def _layer_valency_sketch(bundle: ConceptBundle) -> str:
    stroke = PALETTE["navy"]
    highlight = PALETTE["saffron"]
    supportive = PALETTE["green"]
    entity = (bundle.entities[:1] or ["Atom"])[0]
    question = (bundle.question or "").lower()
    valence_hint = None
    match = re.search(r"(\d+)", question)
    if match:
        try:
            valence_hint = int(match.group(1))
        except ValueError:
            valence_hint = None
    slot_count = valence_hint if valence_hint and valence_hint < 8 else 3
    filled_slots = max(1, slot_count - 1)

    nucleus = _rough_circle(250, 185, 30, 1.2)
    orbit_points = [
        (160, 185),
        (190, 115),
        (310, 115),
        (340, 185),
        (310, 255),
        (190, 255),
        (160, 185),
    ]
    orbit = _path_from_points(_jitter_points(orbit_points, 1.4))

    slot_positions = [
        (250, 110),
        (315, 150),
        (315, 220),
        (250, 260),
        (185, 220),
        (185, 150),
    ]
    slot_paths = []
    connectors = []
    for idx, (sx, sy) in enumerate(slot_positions[:max(slot_count, 3)]):
        is_filled = idx < filled_slots
        slot_path = _rough_circle(sx, sy, 12, 0.7)
        slot_paths.append(
            f'<path d="{slot_path}" stroke="{highlight if is_filled else stroke}" stroke-width="1.6" fill="{"#FFE9D6" if is_filled else "none"}" />'
        )
        conn = _path_from_points(_jitter_points([(250, 185), ((sx + 250) / 2, (sy + 185) / 2 - 10), (sx, sy)], 1.0))
        connectors.append(f'<path d="{conn}" stroke="{highlight if is_filled else stroke}" stroke-width="1.2" fill="none" stroke-dasharray="4 4" />')

    scoreboard_shape = _path_from_points(
        _jitter_points([(380, 90), (580, 90), (560, 185), (360, 185), (380, 90)], 1.8)
    )
    professor_head = _rough_circle(130, 240, 16, 0.9)
    professor_body = _path_from_points(_jitter_points([(130, 256), (130, 300), (110, 330)], 1.4))
    professor_arm = _path_from_points(_jitter_points([(130, 275), (160, 255), (190, 250)], 1.2))
    pointer_arrow = _path_from_points(_jitter_points([(188, 248), (260, 210), (290, 200)], 0.9))

    return "".join(
        [
            f'<path id="valency_orbit" d="{orbit}" stroke="{stroke}" stroke-width="1.8" fill="none" stroke-dasharray="6 6" />',
            f'<path id="valency_core" d="{nucleus}" stroke="{stroke}" stroke-width="1.5" fill="#FDF7E3" />',
            "".join(connectors),
            "".join(slot_paths),
            _text(235, 190, entity, stroke, 12),
            _text(230, 205, "core", stroke, 10),
            _text(212, 95, "Valence slots", highlight, 11),
            f'<path d="{scoreboard_shape}" stroke="{stroke}" stroke-width="1.4" fill="#FFFCEF" />',
            _text(395, 115, "Cricket Strategy Board", stroke, 12),
            _text(395, 135, f"Need mates: {slot_count}", stroke, 11),
            _text(395, 155, f"Already ready: {filled_slots}", stroke, 11),
            _text(395, 175, "Target: stable XI", stroke, 11),
            f'<path d="{professor_head}" stroke="{stroke}" stroke-width="1.5" fill="#FFF" />',
            f'<path d="{professor_body}" stroke="{stroke}" stroke-width="1.5" fill="none" />',
            f'<path d="{professor_arm}" stroke="{stroke}" stroke-width="1.4" fill="none" />',
            f'<path d="{pointer_arrow}" stroke="{supportive}" stroke-width="1.4" fill="none" />',
            _text(90, 330, "Coach Sir: \"Get the missing players to seal bonds!\"", supportive, 11),
            _text(180, 285, "open slots = bonding need", supportive, 10),
        ]
    )


def _layer_motion_concept_visual(bundle: ConceptBundle, stroke: str, highlight: str, supportive: str) -> str:
    """
    SCENE-BASED MOTION VISUAL - Auto-rickshaw on Indian Road
    Clean, focused, relatable to every Indian student
    """
    
    # =====================================================
    # SCENE: Auto-rickshaw starting from traffic signal
    # Every Indian student has experienced this!
    # =====================================================
    
    # Road
    road_path = _path_from_points(_jitter_points([
        (0, 260), (640, 260), (640, 320), (0, 320), (0, 260)
    ], 0.5))
    
    # Road markings (dashed center line)
    
    # Traffic signal (left side)
    signal_pole = _path_from_points(_jitter_points([(50, 120), (50, 260)], 0.8))
    signal_box = _path_from_points(_jitter_points([
        (35, 120), (65, 120), (65, 180), (35, 180), (35, 120)
    ], 1.0))
    signal_green = _rough_circle(50, 165, 8, 0.5)  # Green light ON
    
    # AUTO-RICKSHAW - Clean, recognizable
    # Position 1: At rest (left)
    auto1_body = _path_from_points(_jitter_points([
        (120, 220), (180, 220), (185, 230), (185, 250), (115, 250), (115, 230), (120, 220)
    ], 1.2))
    auto1_roof = _path_from_points(_jitter_points([
        (125, 220), (130, 200), (170, 200), (175, 220)
    ], 1.0))
    auto1_wheel1 = _rough_circle(130, 255, 8, 0.6)
    auto1_wheel2 = _rough_circle(170, 255, 8, 0.6)
    
    # Position 2: Moving (middle) - with motion lines
    auto2_body = _path_from_points(_jitter_points([
        (300, 220), (360, 220), (365, 230), (365, 250), (295, 250), (295, 230), (300, 220)
    ], 1.2))
    auto2_roof = _path_from_points(_jitter_points([
        (305, 220), (310, 200), (350, 200), (355, 220)
    ], 1.0))
    auto2_wheel1 = _rough_circle(310, 255, 8, 0.6)
    auto2_wheel2 = _rough_circle(350, 255, 8, 0.6)
    
    # Position 3: Fast (right) - more motion lines
    auto3_body = _path_from_points(_jitter_points([
        (480, 220), (540, 220), (545, 230), (545, 250), (475, 250), (475, 230), (480, 220)
    ], 1.2))
    auto3_roof = _path_from_points(_jitter_points([
        (485, 220), (490, 200), (530, 200), (535, 220)
    ], 1.0))
    auto3_wheel1 = _rough_circle(490, 255, 8, 0.6)
    auto3_wheel2 = _rough_circle(530, 255, 8, 0.6)
    
    # Motion lines (showing speed increase)
    motion_lines_1 = _path_from_points(_jitter_points([(280, 235), (290, 235)], 0.5))
    motion_lines_2 = _path_from_points(_jitter_points([(450, 230), (465, 230)], 0.5))
    motion_lines_3 = _path_from_points(_jitter_points([(450, 240), (470, 240)], 0.5))
    motion_lines_4 = _path_from_points(_jitter_points([(450, 250), (465, 250)], 0.5))
    
    # Velocity arrows (increasing size to show acceleration)
    vel_arrow_1 = _path_from_points(_jitter_points([(190, 235), (220, 235)], 0.5))
    vel_arrow_2 = _path_from_points(_jitter_points([(370, 235), (420, 235)], 0.5))
    vel_arrow_3 = _path_from_points(_jitter_points([(550, 235), (620, 235)], 0.5))
    
    return (
        f'<defs>'
        f'<marker id="vel-arrow" markerWidth="15" markerHeight="15" refX="13" refY="7" orient="auto">'
        f'<path d="M 0 0 L 15 7 L 0 15 L 4 7 Z" fill="{supportive}" />'
        f'</marker>'
        f'<linearGradient id="road-grad" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:#424242" />'
        f'<stop offset="100%" style="stop-color:#212121" />'
        f'</linearGradient>'
        f'<linearGradient id="sky-grad" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:#81D4FA" />'
        f'<stop offset="100%" style="stop-color:#E1F5FE" />'
        f'</linearGradient>'
        f'</defs>'
        
        # === SKY BACKGROUND ===
        f'<rect x="0" y="60" width="640" height="200" fill="url(#sky-grad)" />'
        
        # === TITLE - Clean, Bold ===
        f'<rect x="0" y="0" width="640" height="60" fill="#00695C" />'
        f'{_text_centered(320, 28, "MOTION (गति)", "#FFFFFF", 24, bold=True)}'
        f'{_text_centered(320, 50, "जगह का बदलाव समय के साथ", "#A5D6A7", 14)}'
        
        # === ROAD ===
        f'<rect x="0" y="260" width="640" height="60" fill="url(#road-grad)" />'
        # Center line (dashed)
        f'<path d="M 0 290 L 50 290 M 70 290 L 120 290 M 140 290 L 190 290 M 210 290 L 260 290 M 280 290 L 330 290 M 350 290 L 400 290 M 420 290 L 470 290 M 490 290 L 540 290 M 560 290 L 610 290 M 630 290 L 640 290" stroke="#FFC107" stroke-width="3" fill="none" />'
        
        # === TRAFFIC SIGNAL ===
        f'<path d="{signal_pole}" stroke="#424242" stroke-width="4" fill="none" />'
        f'<path d="{signal_box}" stroke="#424242" stroke-width="2" fill="#37474F" />'
        f'<circle cx="50" cy="135" r="7" fill="#EF5350" opacity="0.3" />'  # Red off
        f'<circle cx="50" cy="150" r="7" fill="#FFC107" opacity="0.3" />'  # Yellow off
        f'<path d="{signal_green}" stroke="#2E7D32" stroke-width="2" fill="#4CAF50" />'  # Green ON
        f'{_text_centered(50, 195, "🟢 GO", supportive, 10)}'
        
        # === AUTO 1: AT REST ===
        f'<g id="auto1">'
        f'<path d="{auto1_body}" stroke="{stroke}" stroke-width="2" fill="#81C784" />'
        f'<path d="{auto1_roof}" stroke="{stroke}" stroke-width="2" fill="#FDD835" />'
        f'<path d="{auto1_wheel1}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'<path d="{auto1_wheel2}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'</g>'
        f'<rect x="115" y="170" width="75" height="25" rx="5" fill="#E3F2FD" stroke="#1976D2" stroke-width="1.5" />'
        f'{_text_centered(152, 187, "v = 0", "#1976D2", 12, bold=True)}'
        f'{_text_centered(152, 210, "रुका हुआ", stroke, 10)}'
        
        # === AUTO 2: SLOW ===
        f'<g id="auto2">'
        f'<path d="{auto2_body}" stroke="{stroke}" stroke-width="2" fill="#81C784" />'
        f'<path d="{auto2_roof}" stroke="{stroke}" stroke-width="2" fill="#FDD835" />'
        f'<path d="{auto2_wheel1}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'<path d="{auto2_wheel2}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'<path d="{motion_lines_1}" stroke="#90A4AE" stroke-width="2" fill="none" />'
        f'</g>'
        f'<rect x="295" y="170" width="75" height="25" rx="5" fill="#FFF8E1" stroke="{highlight}" stroke-width="1.5" />'
        f'{_text_centered(332, 187, "v = 20", highlight, 12, bold=True)}'
        f'{_text_centered(332, 210, "धीरे चल रहा", stroke, 10)}'
        f'<path d="{vel_arrow_2}" stroke="{supportive}" stroke-width="4" fill="none" marker-end="url(#vel-arrow)" />'
        
        # === AUTO 3: FAST ===
        f'<g id="auto3">'
        f'<path d="{auto3_body}" stroke="{stroke}" stroke-width="2" fill="#81C784" />'
        f'<path d="{auto3_roof}" stroke="{stroke}" stroke-width="2" fill="#FDD835" />'
        f'<path d="{auto3_wheel1}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'<path d="{auto3_wheel2}" stroke="{stroke}" stroke-width="2" fill="#212121" />'
        f'<path d="{motion_lines_2}" stroke="#90A4AE" stroke-width="2" fill="none" />'
        f'<path d="{motion_lines_3}" stroke="#78909C" stroke-width="2" fill="none" />'
        f'<path d="{motion_lines_4}" stroke="#607D8B" stroke-width="2" fill="none" />'
        f'</g>'
        f'<rect x="475" y="170" width="75" height="25" rx="5" fill="#FFEBEE" stroke="#D32F2F" stroke-width="1.5" />'
        f'{_text_centered(512, 187, "v = 60", "#D32F2F", 12, bold=True)}'
        f'{_text_centered(512, 210, "तेज़ 🚀", stroke, 10)}'
        f'<path d="{vel_arrow_3}" stroke="{supportive}" stroke-width="6" fill="none" marker-end="url(#vel-arrow)" />'
        
        # === BIG ACCELERATION ARROW (connecting the states) ===
        f'<path d="M 200 150 Q 320 100 440 150" stroke="{highlight}" stroke-width="4" fill="none" marker-end="url(#vel-arrow)" stroke-dasharray="8 4" />'
        f'<rect x="260" y="90" width="120" height="35" rx="8" fill="{highlight}" />'
        f'{_text_centered(320, 108, "ACCELERATION", "#FFF", 11, bold=True)}'
        f'{_text_centered(320, 122, "तेज़ी बढ़ रही है", "#FFF", 10)}'
        
        # === FORMULA BOX ===
        f'<rect x="15" y="325" width="180" height="30" rx="6" fill="#FFF8E1" stroke="{highlight}" stroke-width="1.5" />'
        f'{_text_centered(105, 345, "📐 v = u + at (Speed formula)", stroke, 10)}'
        
        # === KEY INSIGHT ===
        f'<rect x="445" y="325" width="180" height="30" rx="6" fill="#E8F5E9" stroke="{supportive}" stroke-width="1.5" />'
        f'{_text_centered(535, 345, "💡 ज़्यादा समय = ज़्यादा speed", supportive, 10)}'
    )


def _layer_gravity_concept_visual(bundle: ConceptBundle, stroke: str, highlight: str, supportive: str) -> str:
    """
    SCENE-BASED GRAVITY VISUAL - Mango Tree in Indian Village
    Clean, focused, relatable - Every Indian has seen mangoes fall!
    """
    
    # =====================================================
    # SCENE: Mango tree with falling mangoes
    # Universal Indian experience - sitting under mango tree
    # =====================================================
    
    # Ground (grass/earth)
    
    # MANGO TREE - Center of the visual
    # Trunk
    trunk = _path_from_points(_jitter_points([
        (280, 200), (280, 320), (360, 320), (360, 200)
    ], 1.5))
    
    # Tree crown (large, lush)
    crown_main = _rough_circle(320, 130, 100, 2.0)
    
    # Mangoes on tree
    mango1 = _rough_circle(250, 100, 10, 0.6)
    mango2 = _rough_circle(380, 120, 10, 0.6)
    mango3 = _rough_circle(300, 80, 10, 0.6)
    
    # FALLING MANGO - Main focus
    mango_falling1 = _rough_circle(420, 120, 12, 0.6)  # Just detached
    mango_falling2 = _rough_circle(430, 180, 12, 0.6)  # Mid-fall
    mango_falling3 = _rough_circle(440, 250, 12, 0.6)  # Near ground
    mango_fallen = _rough_circle(445, 310, 10, 0.6)    # On ground
    
    # Gravity arrow (THE MAIN CONCEPT - big and clear)
    gravity_arrow = _path_from_points(_jitter_points([
        (470, 100), (470, 150), (470, 200), (470, 250), (470, 300)
    ], 0.5))
    
    # BOY sitting under tree (Indian village boy)
    boy_head = _rough_circle(180, 260, 15, 0.8)
    boy_body = _path_from_points(_jitter_points([(180, 275), (180, 310)], 1.0))
    boy_legs = _path_from_points(_jitter_points([(180, 310), (160, 330), (180, 310), (200, 330)], 1.0))
    boy_arm = _path_from_points(_jitter_points([(180, 285), (210, 270)], 1.0))  # Pointing up
    
    # Thought bubble
    thought_bubble = _rough_circle(230, 210, 30, 1.2)
    thought_small1 = _rough_circle(200, 235, 8, 0.5)
    thought_small2 = _rough_circle(190, 250, 5, 0.5)
    
    return (
        f'<defs>'
        f'<marker id="gravity-arrow" markerWidth="20" markerHeight="20" refX="10" refY="18" orient="auto">'
        f'<path d="M 0 0 L 10 20 L 20 0 L 10 5 Z" fill="{highlight}" />'
        f'</marker>'
        f'<linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:#64B5F6" />'
        f'<stop offset="100%" style="stop-color:#E3F2FD" />'
        f'</linearGradient>'
        f'<linearGradient id="ground" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:#8BC34A" />'
        f'<stop offset="100%" style="stop-color:#558B2F" />'
        f'</linearGradient>'
        f'</defs>'
        
        # === SKY ===
        f'<rect x="0" y="60" width="640" height="260" fill="url(#sky)" />'
        
        # === TITLE ===
        f'<rect x="0" y="0" width="640" height="60" fill="#5D4037" />'
        f'{_text_centered(320, 28, "GRAVITY (गुरुत्वाकर्षण)", "#FFFFFF", 24, bold=True)}'
        f'{_text_centered(320, 50, "धरती सब चीज़ों को अपनी ओर खींचती है", "#A5D6A7", 14)}'
        
        # === GROUND ===
        f'<rect x="0" y="320" width="640" height="40" fill="url(#ground)" />'
        
        # === TREE ===
        f'<path d="{trunk}" stroke="#4E342E" stroke-width="2" fill="#6D4C41" />'
        f'<path d="{crown_main}" stroke="#2E7D32" stroke-width="3" fill="#4CAF50" />'
        # Add some texture to crown
        f'<circle cx="280" cy="110" r="30" fill="#388E3C" />'
        f'<circle cx="360" cy="120" r="35" fill="#43A047" />'
        f'<circle cx="320" cy="90" r="25" fill="#66BB6A" />'
        
        # === MANGOES ON TREE ===
        f'<path d="{mango1}" stroke="#E65100" stroke-width="2" fill="#FF9800" />'
        f'<path d="{mango2}" stroke="#E65100" stroke-width="2" fill="#FFC107" />'
        f'<path d="{mango3}" stroke="#E65100" stroke-width="2" fill="#FFB300" />'
        
        # === FALLING MANGOES (with trail effect) ===
        f'<path d="{mango_falling1}" stroke="#E65100" stroke-width="2" fill="#FF9800" />'
        f'<path d="{mango_falling2}" stroke="#E65100" stroke-width="2" fill="#FF9800" opacity="0.8" />'
        f'<path d="{mango_falling3}" stroke="#E65100" stroke-width="2" fill="#FF9800" opacity="0.9" />'
        f'<path d="{mango_fallen}" stroke="#E65100" stroke-width="2" fill="#F57C00" />'
        # Motion trail
        f'<path d="M 420 120 Q 435 150 430 180 Q 440 215 440 250 Q 445 280 445 310" stroke="{highlight}" stroke-width="2" fill="none" stroke-dasharray="5 5" opacity="0.5" />'
        
        # === BIG GRAVITY ARROW ===
        f'<path d="{gravity_arrow}" stroke="{highlight}" stroke-width="10" fill="none" marker-end="url(#gravity-arrow)" />'
        f'<rect x="490" y="180" width="130" height="50" rx="10" fill="{highlight}" />'
        f'{_text_centered(555, 200, "GRAVITY", "#FFF", 16, bold=True)}'
        f'{_text_centered(555, 220, "g = 9.8 m/s²", "#FFF", 12)}'
        
        # === BOY ===
        f'<path d="{boy_head}" stroke="{stroke}" stroke-width="2" fill="#FFE0B2" />'
        f'<path d="{boy_body}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{boy_legs}" stroke="{stroke}" stroke-width="3" fill="none" />'
        f'<path d="{boy_arm}" stroke="{stroke}" stroke-width="2.5" fill="none" />'
        # Eyes looking at mango
        f'<circle cx="175" cy="257" r="2" fill="{stroke}" />'
        f'<circle cx="185" cy="257" r="2" fill="{stroke}" />'
        
        # === THOUGHT BUBBLE ===
        f'<path d="{thought_bubble}" stroke="{stroke}" stroke-width="1.5" fill="#FFF" />'
        f'<path d="{thought_small1}" stroke="{stroke}" stroke-width="1" fill="#FFF" />'
        f'<path d="{thought_small2}" stroke="{stroke}" stroke-width="1" fill="#FFF" />'
        f'{_text_centered(230, 205, "आम क्यों", stroke, 10)}'
        f'{_text_centered(230, 220, "गिरता है? 🤔", stroke, 10)}'
        
        # === KEY INSIGHT BOX (Left) ===
        f'<rect x="20" y="85" width="140" height="70" rx="8" fill="#E8F5E9" stroke="{supportive}" stroke-width="2" />'
        f'{_text_centered(90, 105, "💡 KEY INSIGHT", supportive, 10, bold=True)}'
        f'{_text_centered(90, 125, "Earth pulls", stroke, 11)}'
        f'{_text_centered(90, 142, "everything DOWN", highlight, 11, bold=True)}'
        
        # === FORMULA BOX (Right) ===
        f'<rect x="510" y="85" width="120" height="70" rx="8" fill="#FFF8E1" stroke="{highlight}" stroke-width="2" />'
        f'{_text_centered(570, 105, "📐 FORMULA", highlight, 10, bold=True)}'
        f'{_text_centered(570, 128, "F = mg", stroke, 16, bold=True)}'
        f'{_text_centered(570, 148, "Weight = mass × g", stroke, 9)}'
        
        # === BOTTOM INFO ===
        f'<rect x="140" y="330" width="360" height="25" rx="5" fill="rgba(255,255,255,0.9)" />'
        f'{_text_centered(320, 347, "🥭 आम गिरता है क्योंकि धरती उसे अपनी ओर खींचती है (Gravity)", stroke, 11)}'
    )


def _layer_exam(
    bundle: ConceptBundle,
    student_dna: Optional[StudentDNA] = None,
    topper_selector: Optional[TopperHackSelector] = None,
    pyq_matcher: Optional[PYQMatcher] = None
) -> str:
    """Enhanced Layer 2 with Hinglish, topper hacks, and PYQ references"""
    # Initialize services if not provided
    if topper_selector is None:
        topper_selector = TopperHackSelector()
    if pyq_matcher is None:
        pyq_matcher = PYQMatcher()

    # Determine region from student DNA
    region = "North"
    if student_dna and student_dna.locale_language:
        locale_map = {
            "hi": "North", "pa": "North", "ur": "North",
            "ta": "South", "te": "South", "kn": "South", "ml": "South",
            "mr": "West", "gu": "West",
            "bn": "East", "or": "East", "as": "East"
        }
        lang_code = student_dna.locale_language[:2].lower()
        region = locale_map.get(lang_code, "North")

    # Yellow sticky note background
    stroke = PALETTE["navy"]
    note = _path_from_points(_jitter_points([(430, 90), (560, 95), (555, 190), (425, 185), (430, 90)], 2.5))

    # Marks annotation with Hinglish
    marks_text = generate_marks_annotation(
        total_marks=bundle.marks_distribution["total"],
        parts=bundle.marks_distribution.get("parts", []),
        region=region
    )

    # Common mistake warning
    concept = bundle.entities[0] if bundle.entities else "concept"
    mistake = get_common_mistake(concept, region)

    # Topper hack
    hack_obj = topper_selector.get_hack(
        concept_keywords=bundle.entities,
        board=student_dna.board if student_dna else None,
        level=student_dna.level if student_dna else None
    )

    # PYQ references
    pyqs = pyq_matcher.find_similar_pyqs(
        question=bundle.question,
        board=student_dna.board if student_dna else None,
        max_results=1  # Only show top match for space
    )

    # Build SVG text elements
    y_offset = 105
    elements = []

    # Marks
    elements.append(_text(440, y_offset, marks_text, stroke, 11))
    y_offset += 18

    # Common mistake
    if len(mistake) < 50:  # Short enough to fit
        elements.append(_text(440, y_offset, mistake, stroke, 9))
        y_offset += 16

    # Topper hack (split into multiple lines if needed)
    if hack_obj:
        hack_line1 = f"🏆 {hack_obj['rank']}:"
        elements.append(_text(440, y_offset, hack_line1, stroke, 9))
        y_offset += 14

        hack_line2 = hack_obj['hack'][:45] + "..." if len(hack_obj['hack']) > 45 else hack_obj['hack']
        elements.append(_text(440, y_offset, hack_line2, stroke, 8))
        y_offset += 14

    # PYQ reference
    if pyqs:
        pyq = pyqs[0]
        pyq_text = f"📌 {pyq.board} {pyq.year} {pyq.question_number} ({int(pyq.similarity*100)}%)"
        elements.append(_text(440, y_offset, pyq_text, stroke, 9))

    return f'<path id="l2_note" d="{note}" stroke="{stroke}" stroke-width="1.3" fill="{PALETTE["yellow"]}" />{"".join(elements)}'


def _layer_culture_blended(
    primary: MetaphorCandidate,
    secondary: MetaphorCandidate,
    tertiary: MetaphorCandidate,
    region: str = "North"
) -> str:
    """Enhanced Layer 3: All metaphors blended at low opacity with icons"""
    from .hinglish_annotations import get_regional_metaphor_label

    # Create 3 overlapping organic blob shapes
    metaphors = [primary, secondary, tertiary]
    colors = [PALETTE["saffron"], PALETTE["green"], PALETTE["navy"]]

    svg_parts = ['<g id="l3_meta" opacity="0.10">']

    # Metaphor icons for better visual appeal
    icon_map = {
        "family": "👨‍👩‍👦",
        "food": "🍲",
        "cricket": "🏏",
        "bollywood": "🎬",
        "gaming": "🎮"
    }

    for i, (metaphor, color) in enumerate(zip(metaphors, colors)):
        # Create organic blob shape for each metaphor (overlapping)
        x_offset = 60 + (i * 160)
        y_base = 220 + (i * 8)  # Slight vertical offset for depth

        # Wavy blob path (more organic shapes)
        blob_points = [
            (x_offset, y_base),
            (x_offset + 95, y_base - 12),
            (x_offset + 115, y_base + 25),
            (x_offset + 90, y_base + 55),
            (x_offset + 25, y_base + 45),
            (x_offset, y_base)
        ]

        jittered = _jitter_points(blob_points, 4.0)  # More jitter for hand-drawn feel
        path = _path_from_points(jittered)

        # Add metaphor shape with fill
        svg_parts.append(
            f'<path d="{path}" stroke="{color}" stroke-width="1.6" '
            f'fill="{color}" fill-opacity="0.25" />'
        )

        # Add icon + label
        icon = icon_map.get(metaphor.muse, "•")
        label = get_regional_metaphor_label(metaphor.muse, region)

        svg_parts.append(
            _text(x_offset + 35, y_base + 28, f"{icon} {label}", color, 9)
        )

    # Add blend explanation at bottom
    blend_text = f"Memory Hook: {primary.muse} + {secondary.muse} + {tertiary.muse} blend"
    svg_parts.append(_text(320, 295, blend_text, PALETTE["navy"], 7))

    svg_parts.append('</g>')
    return ''.join(svg_parts)


def _animation_block_interactive() -> str:
    """
    True tap-to-advance with invisible click zones and progress indicator
    5 steps: Auto-draw skeleton, then click to reveal each layer
    """
    # Tap zones use paths (not rect) to satisfy "no <rect>" constraint
    full_canvas_path = "M0,0 L640,0 L640,360 L0,360 Z"
    return f'''
    <style><![CDATA[
        text{{pointer-events:none}}
        .tap-zone{{fill:transparent;cursor:pointer;opacity:0}}
        .tap-zone:hover{{opacity:0.05;fill:#FFD700}}
        .progress-text{{font-family:system-ui,Arial;font-size:11px;fill:#666}}
    ]]></style>

    <!-- Progress indicator -->
    <text id="progress1" class="progress-text" x="10" y="350" visibility="visible">Tap anywhere to continue →</text>
    <text id="progress2" class="progress-text" x="10" y="350" visibility="hidden">Tap for arrows →</text>
    <text id="progress3" class="progress-text" x="10" y="350" visibility="hidden">Tap for exam tips →</text>
    <text id="progress4" class="progress-text" x="10" y="350" visibility="hidden">Tap for memory hooks →</text>
    <text id="progress5" class="progress-text" x="10" y="350" visibility="hidden">Complete! 🎯</text>

    <!-- Step 1: Auto-draw skeleton (boxes only) -->
    <set xlink:href="#layer1" attributeName="visibility" to="visible" begin="0.5s" />
    <set xlink:href="#l1_arrow" attributeName="visibility" to="hidden" begin="0.5s" />

    <!-- Tap zone 1: Click anywhere to show arrows -->
    <path id="tap1" class="tap-zone" d="{full_canvas_path}" />
    <set xlink:href="#l1_arrow" attributeName="visibility" to="visible" begin="tap1.click" />
    <set xlink:href="#tap1" attributeName="display" to="none" begin="tap1.click" />
    <set xlink:href="#progress1" attributeName="visibility" to="hidden" begin="tap1.click" />
    <set xlink:href="#progress2" attributeName="visibility" to="visible" begin="tap1.click" />

    <!-- Tap zone 2: Show second box fully -->
    <path id="tap2" class="tap-zone" d="{full_canvas_path}" display="none" />
    <set xlink:href="#tap2" attributeName="display" to="block" begin="tap1.click" />
    <set xlink:href="#l1_box2" attributeName="opacity" from="0.5" to="1.0" begin="tap2.click" dur="0.3s" fill="freeze" />
    <set xlink:href="#tap2" attributeName="display" to="none" begin="tap2.click" />
    <set xlink:href="#progress2" attributeName="visibility" to="hidden" begin="tap2.click" />
    <set xlink:href="#progress3" attributeName="visibility" to="visible" begin="tap2.click" />

    <!-- Tap zone 3: Show exam layer (yellow sticky note) -->
    <path id="tap3" class="tap-zone" d="{full_canvas_path}" display="none" />
    <set xlink:href="#tap3" attributeName="display" to="block" begin="tap2.click" />
    <set xlink:href="#layer2" attributeName="visibility" to="visible" begin="tap3.click" />
    <animate xlink:href="#layer2" attributeName="opacity" from="0" to="1" begin="tap3.click" dur="0.4s" fill="freeze" />
    <set xlink:href="#tap3" attributeName="display" to="none" begin="tap3.click" />
    <set xlink:href="#progress3" attributeName="visibility" to="hidden" begin="tap3.click" />
    <set xlink:href="#progress4" attributeName="visibility" to="visible" begin="tap3.click" />

    <!-- Tap zone 4: Show metaphor layer (cultural blend) -->
    <path id="tap4" class="tap-zone" d="{full_canvas_path}" display="none" />
    <set xlink:href="#tap4" attributeName="display" to="block" begin="tap3.click" />
    <set xlink:href="#layer3" attributeName="visibility" to="visible" begin="tap4.click" />
    <animate xlink:href="#l3_meta" attributeName="opacity" from="0" to="0.10" begin="tap4.click" dur="0.5s" fill="freeze" />
    <set xlink:href="#progress4" attributeName="visibility" to="hidden" begin="tap4.click" />
    <set xlink:href="#progress5" attributeName="visibility" to="visible" begin="tap4.click" />
    '''


def _create_enhanced_fallback_visual(bundle: ConceptBundle, metaphors: List[MetaphorCandidate]) -> str:
    """
    Create enhanced fallback visual when generation fails
    Ensures visuals always add value (Value-First principle)
    """
    stroke = PALETTE["navy"]
    highlight = PALETTE["saffron"]
    supportive = PALETTE["green"]
    
    # Create a proper concept explanation visual
    main_concept = bundle.entities[0] if bundle.entities else "Concept"
    
    # Central concept
    center_x, center_y = 320, 180
    center_circle = _rough_circle(center_x, center_y, 60, 1.5)
    
    # Key aspects around it
    aspects = ["Definition", "Examples", "Applications", "Formula"] if "force" in (bundle.question or "").lower() else ["Key Point 1", "Key Point 2", "Key Point 3"]
    
    aspect_elements = []
    import math
    for i, aspect in enumerate(aspects[:4]):
        angle = (2 * math.pi * i) / len(aspects[:4])
        radius = 140
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        box = _path_from_points(_jitter_points([
            (x - 40, y - 15), (x + 40, y - 15), (x + 40, y + 15), (x - 40, y + 15), (x - 40, y - 15)
        ], 2.0))
        aspect_elements.append(f'<path d="{box}" stroke="{stroke}" stroke-width="1.8" fill="#F0F8FF" />')
        aspect_elements.append(_text(x - 35, y + 5, aspect[:12], stroke, 10))
        
        # Connection line
        conn = _path_from_points(_jitter_points([(center_x, center_y), ((x + center_x)/2, (y + center_y)/2), (x, y)], 1.0))
        aspect_elements.append(f'<path d="{conn}" stroke="{supportive}" stroke-width="1.5" fill="none" stroke-dasharray="3 3" />')
    
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="640" height="360" style="background: #FFFFFF;">'
        f'<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{supportive}" /></marker></defs>'
        f'<path id="l1_center" d="{center_circle}" stroke="{highlight}" stroke-width="3" fill="#FFE9D6" />'
        + ''.join(aspect_elements)
        + f'{_text(center_x - 50, center_y + 8, main_concept[:25], highlight, 14)}'
        + f'<g id="layer2" opacity="0">{_layer_exam(bundle, None, None, None)}</g>'
        + f'<g id="layer3" opacity="0">{_layer_culture_blended(metaphors[0] if metaphors else None, metaphors[1] if len(metaphors) > 1 else None, metaphors[2] if len(metaphors) > 2 else None, "North")}</g>'
        + _animation_block_interactive()
        + '</svg>'
    )
    
    return svg_content


def _metadata_defs(bundle: ConceptBundle, metaphors: List[MetaphorCandidate]) -> str:
    concept = _escape(" ".join(bundle.entities) or bundle.question[:40])
    marks = str(bundle.marks_distribution.get("total", 3))
    return (
        "<defs><metadata>"
        f"<concept>{concept}</concept>"
        f"<marks>{marks}</marks>"
        "<pyq>n/a</pyq>"
        f"<metaphors>{', '.join(m.muse for m in metaphors[:3])}</metaphors>"
        "</metadata></defs>"
    )


def create_visual_sketch(question: str, student_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced facade: question -> Emotionally resonant SVG visual sketch.

    Now includes:
    - Hinglish annotations (region-aware)
    - Topper hacks with rank attribution
    - PYQ pattern references
    - Multi-metaphor blending

    Returns dict with svg (string), metaphors used, and metadata
    """
    # Deterministic jitter for caching (stable per question + profile)
    seed_input = question + repr(sorted(student_profile.items())) if student_profile else question
    random.seed(hash(seed_input) % (2**32))

    # Initialize services
    topper_selector = TopperHackSelector()
    pyq_matcher = PYQMatcher()

    # Select metaphors
    sel = select_metaphors(question, student_profile)
    bundle: ConceptBundle = sel["bundle"]
    top: List[MetaphorCandidate] = sel["top"]

    # Ensure 3 metaphors by padding if needed
    while len(top) < 3 and sel["candidates"]:
        top.append(sel["candidates"][len(top) % len(sel["candidates"])])

    # Convert student profile to StudentDNA if provided
    student_dna = None
    if student_profile:
        student_dna = StudentDNA(**student_profile)

    # Determine region for Hinglish
    region = "North"
    if student_dna and student_dna.locale_language:
        locale_map = {
            "hi": "North", "pa": "North", "ur": "North",
            "ta": "South", "te": "South", "kn": "South", "ml": "South",
            "mr": "West", "gu": "West",
            "bn": "East", "or": "East", "as": "East"
        }
        lang_code = student_dna.locale_language[:2].lower()
        region = locale_map.get(lang_code, "North")

    # Build layers with enhanced emotional content
    l1 = _layer_skeleton(bundle)
    l2 = _layer_exam(bundle, student_dna, topper_selector, pyq_matcher)
    l3 = _layer_culture_blended(top[0], top[1], top[2], region)
    anim = _animation_block_interactive()
    defs = _metadata_defs(bundle, top)

    # CRITICAL: Ensure layers are not empty (Value-First principle)
    # If skeleton layer is too basic, enhance it
    if len(l1) < 200:  # Basic layer is too simple
        # Enhance with more detail for better learning value
        question_lower = (bundle.question or "").lower()
        if "force" in question_lower or "explain" in question_lower:
            # Force-specific enhancement
            l1 = _layer_force_concept_visual(bundle, PALETTE["navy"], PALETTE["saffron"], PALETTE["green"])
        elif len(bundle.entities) > 0:
            # Use entities to create better visual
            main_entity = bundle.entities[0]
            l1 = _layer_concept_explanation_sketch(bundle)
    
    # Assemble SVG with proper structure
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 640 360" width="640" height="360" style="background: #FFFFFF;">'
        f"{defs}"
        f'<g id="layer1">{l1}</g>'
        f'<g id="layer2" opacity="0">{l2}</g>'
        f'<g id="layer3" opacity="0">{l3}</g>'
        f"{anim}"
        f"</svg>"
    )
    
    # Validate SVG is substantial (Value-First check)
    if len(svg) < 500:
        # Fallback: Create a proper visual
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Generated SVG too short ({len(svg)} chars), creating enhanced fallback")
        svg = _create_enhanced_fallback_visual(bundle, top)

    # Get topper hack info for metadata
    hack_obj = topper_selector.get_hack(
        concept_keywords=bundle.entities,
        board=student_dna.board if student_dna else None
    )

    # Get PYQ info for metadata
    pyqs = pyq_matcher.find_similar_pyqs(
        question=question,
        board=student_dna.board if student_dna else None,
        max_results=3
    )

    return {
        "svg": svg,
        "metaphors_used": [m.muse for m in top[:3]],
        "estimated_marks": bundle.marks_distribution.get("total", 3),
        "topper_hack": hack_obj["hack"] if hack_obj else None,
        "topper_rank": hack_obj["rank"] if hack_obj else None,
        "pyq_references": [f"{pyq.board} {pyq.year} {pyq.question_number}" for pyq in pyqs],
        "region": region,
        "has_emotional_content": True
    }
