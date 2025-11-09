"""
SVG Visual Quality Validation (Topper's Notebook Test - automated subset)
"""
from __future__ import annotations

import re
from typing import Dict


def analyze_path_jitter(svg_code: str) -> float:
    """Rudimentary jitter analysis: parse path numbers, estimate std-dev per segment.
    Returns a crude jitter estimate in px (0..~5).
    """
    coords = [float(x) for x in re.findall(r"[-+]?[0-9]*\.?[0-9]+", svg_code) if len(x) <= 6]
    if not coords:
        return 0.0
    # Very rough: variance across consecutive deltas
    deltas = []
    for i in range(2, len(coords)):
        deltas.append(abs(coords[i] - coords[i - 2]))
    if not deltas:
        return 0.0
    mean = sum(deltas) / len(deltas)
    var = sum((d - mean) ** 2 for d in deltas) / len(deltas)
    jitter = (var ** 0.5) / 10.0
    return min(5.0, jitter)


def validate_visual(svg_code: str) -> bool:
    tests: Dict[str, bool] = {
        "file_size": len(svg_code) / 1024 <= 10.0,
        "no_gradients": ("linearGradient" not in svg_code and "radialGradient" not in svg_code),
        "hand_drawn_elements": svg_code.count("<path") >= 5,
        "exam_annotations": ("Marks:" in svg_code or "\uD83D\uDD34" in svg_code or "Topper" in svg_code),
        "indian_colors": any(c in svg_code for c in ["#FF9933", "#138808", "#000080"]),
        "progressive_animation": ("animate" in svg_code or "begin=" in svg_code),
        "no_forbidden_shapes": all(t not in svg_code for t in ["<circle", "<rect", "<line"]),
        "jitter_detected": analyze_path_jitter(svg_code) >= 0.5,
    }
    return all(tests.values())


