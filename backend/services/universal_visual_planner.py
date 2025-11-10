from __future__ import annotations

"""
Universal Visual Planner

Question-agnostic visual planning that guarantees a clear, multi-stage
teaching visual using a small set of reusable blocks defined in
`visual_contract.py`.
"""

import hashlib
import re
from typing import Dict, List, Optional

from .visual_contract import (
    TeachingVisual,
    Stage,
    TitleCard,
    ConceptNodes,
    RelationArrows,
    EquationBlock,
    CompareGrid,
    WorkedExample,
    TipCard,
)
from .question_scope import build_scope


def _slug(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def _extract_equation(question: str) -> Optional[str]:
    # Very lightweight heuristic for equations
    # Picks up patterns like F = m a, V = I R, a^2 + b^2 = c^2, etc.
    eq = re.search(r"([A-Za-z0-9^_]+\s*[=≈]\s*[^,;]+)", question)
    if eq:
        return eq.group(1).strip()
    return None


def _guess_topic(question: str) -> str:
    q = question.lower()
    if "newton" in q and "law" in q:
        return "Newton's Laws of Motion"
    if "photosynthesis" in q:
        return "Photosynthesis"
    if "ohm" in q or re.search(r"v\s*=\s*i\s*r", q):
        return "Ohm's Law"
    if "quadratic" in q:
        return "Quadratic Equations"
    words = re.findall(r"[a-zA-Z]{4,}", q)
    return " ".join(words[:3]).title() or "Concept Overview"


def plan_universal_visual(question: str, subject: Optional[str] = None, brief: Optional[dict] = None) -> TeachingVisual:
    topic = _guess_topic(question)
    scope = brief or build_scope(question)
    eq = _extract_equation(question)
    visual_id = _slug(question + (subject or ""))

    # Stage 1: Overview / Definition
    s1: Stage = {
        "narration": f"We’ll quickly map the key ideas behind {topic}.",
        "emphasis": "See the big picture first, details later.",
        "duration_ms": 2000,
        "blocks": [
            cast_block(TitleCard(type="title_card", title=topic, subtitle="Overview")),
            cast_block({
                "type": "definition_card",
                "term": topic,
                "definition": f"What it means: {topic.split(' ')[0]} in one line (exam-ready)."
            }),
            cast_block(
                ConceptNodes(
                    type="concept_nodes",
                    layout="row",
                    nodes=[
                        {"id": "c1", "label": "Idea 1"},
                        {"id": "c2", "label": "Idea 2"},
                        {"id": "c3", "label": "Idea 3"},
                    ],
                )
            ),
        ],
    }

    # Stage 2: Relations / Equation
    relations_block = cast_block(
        RelationArrows(
            type="relation_arrows",
            relations=[
                {"from_": "c1", "to": "c2", "label": "influences"},
                {"from_": "c2", "to": "c3", "label": "leads to"},
            ],
        )
    )

    blocks_s2: List[Dict] = [relations_block]
    if eq:
        blocks_s2.append(cast_block(EquationBlock(type="equation", tex=eq)))

    s2: Stage = {
        "narration": "Here’s how the pieces connect and the key formula if any.",
        "emphasis": "Links > isolated facts.",
        "duration_ms": 2200,
        "blocks": blocks_s2,
    }

    # Stage 3: Worked example
    s3: Stage = {
        "narration": "Let’s walk through a quick example to make it stick.",
        "emphasis": "Concrete example = faster recall in exams.",
        "duration_ms": 2400,
        "blocks": [
            cast_block(
                WorkedExample(
                    type="worked_example",
                    icon="cricket",
                    steps=[
                        {"label": "Setup", "detail": "Define given and target."},
                        {"label": "Apply", "detail": "Use relation / formula."},
                        {"label": "Solve", "detail": "Compute or conclude."},
                    ],
                )
            )
        ],
    }

    # Stage 4: Compare / Recap
    s4: Stage = {
        "narration": "Common confusion and the topper’s quick recap.",
        "emphasis": "Avoid these mistakes; summarize in 2 lines.",
        "duration_ms": 2000,
        "blocks": [
            cast_block(
                CompareGrid(
                    type="compare_grid",
                    left={"title": "A", "points": ["Definition", "Example"]},
                    right={"title": "B", "points": ["Definition", "Example"]},
                )
            ),
            cast_block(TipCard(type="tip_card", tip_type="exam", text="State → Relate → Example → Equation.")),
            cast_block({
                "type": "mcq_quiz",
                "question": "Quick check: which block gives marks fastest?",
                "options": ["Definitions only", "Relations + Example", "Equation only", "Story"],
                "correct": 1,
                "explanation": "Relations + example demonstrates understanding (marks!)."
            }),
        ],
    }

    # Mode-based pruning for tight visuals
    if scope.get("mode") == "define":
        stages: List[Stage] = [s1, s2] if eq else [s1]
    elif scope.get("mode") == "compare":
        stages = [s1, s4]
    else:
        stages = [s1, s2, s3, s4]
    total_duration = sum(s["duration_ms"] for s in stages)

    return {
        "visual_id": visual_id,
        "type": "teaching_visual",
        "total_duration_ms": int(total_duration),
        "metadata": {
            "topic": topic,
            "subject": subject or "general",
            "concept_type": "overview",
        },
        "stages": stages,
    }


def cast_block(b: Dict) -> Dict:
    # Small helper to keep mypy happy if used in typed contexts.
    return b
