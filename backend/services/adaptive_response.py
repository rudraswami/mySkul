from __future__ import annotations

"""
Adaptive, intent-driven response helpers.

Detects student intent and, when appropriate, builds minimal teaching visuals
that match the communication goal (e.g., compare/contrast) while leaving the
existing fallback instructional block untouched.
"""

import re
from typing import Dict, Optional, Tuple

INTENTS = (
    "definition",
    "conceptual_explanation",
    "compare_contrast",
    "deep_dive",
    "application_based",
    "clarification_or_followup",
)


def detect_intent(question: str, previous_text: Optional[str] = None) -> str:
    q = (question or "").strip().lower()

    if re.search(r"\b(what is|define|meaning of|state)\b", q):
        return "definition"

    if re.search(r"\b(compare|difference between|vs\b|versus|contrast)\b", q):
        return "compare_contrast"

    if re.search(r"\b(derive|prove|exception|edge case|in depth|deep dive|why exactly)\b", q):
        return "deep_dive"

    if re.search(r"\b(real[- ]world|practical|application|use case|daily life|where.*used|apply)\b", q):
        return "application_based"

    if re.search(r"\b(again|another way|tell me differently|clarify|follow ?up|more detail|i know)\b", q):
        return "clarification_or_followup"

    # Default: conceptual explanation
    if re.search(r"\b(explain|how does|how do|why)\b", q):
        return "conceptual_explanation"

    return "conceptual_explanation"


def _extract_compare_targets(question: str) -> Tuple[str, str]:
    q = (question or "").lower()
    # Try to catch "A vs B" or "difference between A and B"
    m = re.search(r"\bbetween\s+([a-z0-9\s\-]+?)\s+and\s+([a-z0-9\s\-]+)\b", q)
    if m:
        return (m.group(1).strip().title(), m.group(2).strip().title())
    m = re.search(r"\b([a-z0-9\s\-]+?)\s+(?:vs|versus)\s+([a-z0-9\s\-]+)\b", q)
    if m:
        return (m.group(1).strip().title(), m.group(2).strip().title())
    return ("Left", "Right")


def build_compare_visual(question: str) -> Dict:
    """Build a minimal compare/contrast teaching visual (single-stage)."""
    left_title, right_title = _extract_compare_targets(question)

    # Heuristic topic-specific differences (compact, helpful defaults)
    topic = (question or "").lower()
    left_points: list[str] = []
    right_points: list[str] = []

    if "ionic" in topic and "covalent" in topic:
        left_title, right_title = "Ionic", "Covalent"
        left_points = [
            "Electron transfer",
            "Strong electrostatic forces",
            "High melting points",
            "Often soluble in water",
        ]
        right_points = [
            "Electron sharing",
            "Directional bonds",
            "Lower melting points (many)",
            "Variable solubility",
        ]
    elif "series" in topic and "parallel" in topic:
        left_title, right_title = "Series", "Parallel"
        left_points = [
            "R_eq = R1 + R2 + …",
            "Same current through each",
            "Voltage divides",
        ]
        right_points = [
            "1/R_eq = 1/R1 + 1/R2 + …",
            "Same voltage across branches",
            "Current divides",
        ]
    elif "acid" in topic and "base" in topic:
        left_title, right_title = "Acids", "Bases"
        left_points = [
            "pH < 7",
            "Proton donors",
            "Sour taste (safety!)",
        ]
        right_points = [
            "pH > 7",
            "Proton acceptors",
            "Bitter/slippery (safety!)",
        ]

    return {
        "visual_id": "cmp_grid_1",
        "type": "teaching_visual",
        "total_duration_ms": 3000,
        "metadata": {"topic": f"Compare: {left_title} vs {right_title}", "subject": "general", "concept_type": "compare"},
        "stages": [
            {
                "narration": "Side-by-side differences for quick clarity.",
                "duration_ms": 3000,
                "blocks": [
                    {"type": "compare_grid", "left": {"title": left_title, "points": left_points}, "right": {"title": right_title, "points": right_points}}
                ]
            }
        ]
    }


def build_application_hint_card(question: str) -> Dict:
    """Small application card to replace generic CTA for application-based intent."""
    return {
        "type": "tip_card",
        "tip_type": "application",
        "text": "Real-world nudge: Observe this in your surroundings today and note one example."
    }

