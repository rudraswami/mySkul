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


def detect_intent(
    question: str, 
    previous_text: Optional[str] = None,
    semantic_analysis: Optional[Dict] = None
) -> str:
    """
    Detect intent for adaptive visual response.
    
    PHASE 1 FIX: This now defers to semantic analysis when available.
    Keyword regex only runs as legacy fallback.
    
    Args:
        question: The student's question
        previous_text: Previous text context
        semantic_analysis: Dict from SemanticIntentClassifier (optional)
    
    Returns:
        Intent string for visual adaptation
    """
    # ================================================================
    # PHASE 1: SEMANTIC ANALYSIS IS AUTHORITATIVE
    # ================================================================
    if semantic_analysis and semantic_analysis.get('confidence', 0) >= 0.5:
        intent = semantic_analysis.get('intent', '')
        response_expectation = semantic_analysis.get('response_expectation', '')
        
        # Map semantic intents to visual intents
        semantic_to_visual = {
            'explanation': 'conceptual_explanation',
            'question': 'conceptual_explanation',
            'practice': 'application_based',
            'clarification': 'clarification_or_followup',
            'confusion': 'clarification_or_followup',
        }
        
        if intent in semantic_to_visual:
            return semantic_to_visual[intent]
        
        # Check for compare intent via response expectation or topic
        topic = semantic_analysis.get('topic_mentioned', '') or ''
        if 'vs' in topic.lower() or 'compare' in (semantic_analysis.get('reasoning', '') or '').lower():
            return 'compare_contrast'
        
        # Default
        return 'conceptual_explanation'
    
    # ================================================================
    # LEGACY FALLBACK: Regex patterns (only when semantic unavailable)
    # ================================================================
    q = (question or "").strip().lower()

    # STRUCTURAL detection: Look for compare structure (X vs Y)
    if ' vs ' in q or ' versus ' in q or re.search(r"difference between .+ and", q):
        return "compare_contrast"

    # Default: conceptual explanation
    # Let the visual system use default templates
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

