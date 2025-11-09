"""
Visual Quality Validator (Topper's Notebook Test - automated checks)

Implements automated validation per PRD Step 5.
"""

from __future__ import annotations

from typing import Dict


INDIAN_COLORS = ("#FF9933", "#138808", "#000080")


def analyze_path_jitter(svg_code: str) -> float:
    """Crude jitter detection: measure diversity of coordinates in path data.

    Returns an average delta as a proxy (px).
    """
    import re

    coords = [float(x) for x in re.findall(r"[-+]?[0-9]*\.?[0-9]+", svg_code)]
    if len(coords) < 8:
        return 0.0
    deltas = [abs(coords[i] - coords[i - 2]) for i in range(2, len(coords), 2)]
    if not deltas:
        return 0.0
    return sum(deltas) / len(deltas)


def validate_visual(svg_code: str) -> bool:
    tests = {
        "file_size": len(svg_code) / 1024 <= 10.0,
        "no_gradients": ("linearGradient" not in svg_code and "radialGradient" not in svg_code),
        "no_basic_shapes": ("<circle" not in svg_code and "<rect" not in svg_code and "<line" not in svg_code),
        "hand_drawn_elements": svg_code.count("<path") >= 5,
        "exam_annotations": ("marks" in svg_code.lower() or "Topper hack" in svg_code or "hack" in svg_code),
        "indian_colors": any(c in svg_code for c in INDIAN_COLORS),
        "progressive_animation": ("begin=" in svg_code or "animate" in svg_code),
        "jitter_detected": analyze_path_jitter(svg_code) >= 2.0,
    }
    return all(tests.values())

