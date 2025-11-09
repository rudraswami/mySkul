"""
Real-time Metaphor Selector (Top 3)
Implements a heuristic version of the 1.2 algorithm with safe fallbacks.
No external ML calls; pluggable hooks provided for future models.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _intuitiveness_score(concept: str, action_mapping: List[str], category: str, text: str) -> float:
    # Heuristic: universal categories score higher; action keywords boost
    base = {
        "family": 0.82,
        "food": 0.85,
        "cricket": 0.70,
        "bollywood": 0.68,
        "gaming": 0.72,
    }.get(category, 0.65)
    boost = 0.05 if any(k in (text.lower() + " " + " ".join(action_mapping)) for k in ["transfer", "accumulate", "iterate", "transform"]) else 0.0
    length_pen = 0.0
    words = len(text.split())
    if words > 28:
        length_pen = 0.08
    elif words > 20:
        length_pen = 0.04
    return max(0.0, min(1.0, base + boost - length_pen))


def _exam_score(marks_type: str, text: str) -> float:
    # Favor brevity for short; slight structure bonus otherwise
    w = len(text.split())
    if marks_type == "short":
        return 1.0 if w <= 22 else 0.7
    if marks_type == "medium":
        return 0.85 if w <= 35 else 0.7
    if marks_type == "long":
        return 0.8
    return 0.75


def _cultural_score(student_profile: Optional[Dict[str, Any]], category: str) -> float:
    if not student_profile:
        return 0.6 if category in {"family", "food"} else 0.5
    gender = (student_profile.get("gender") or "").upper()
    region = (student_profile.get("region") or "India").lower()
    interests = [str(i).lower() for i in (student_profile.get("interests") or [])]
    score = 0.55
    if category in {"family", "food"}:
        score = 0.8
    if category == "cricket" and (gender == "M" or "cricket" in interests or "sports" in interests):
        score = 0.8
    if category == "bollywood" and (gender == "F" or any(x in interests for x in ["bollywood", "movies", "music"])):
        score = 0.78
    if category == "gaming" and any(x in interests for x in ["gaming", "technology", "coding", "pubg", "valorant"]):
        score = 0.78
    # Region can nudge up slightly (we assume content is India-friendly)
    if region not in {"india", "in"}:
        score -= 0.05
    return max(0.0, min(1.0, score))


def _freshness_score(usage_count: int) -> float:
    # Linear decay with soft floor
    freshness = 1.0 - min(0.8, usage_count / 1000.0)
    return max(0.2, freshness)


def select_top_metaphors(
    concept: str,
    candidates: List[Dict[str, Any]],
    student_profile: Optional[Dict[str, Any]] = None,
    marks_type: str = "medium",
) -> List[Dict[str, Any]]:
    """Rank candidates and return top 3 with score breakdowns.

    Mirrors desired weights but uses heuristics in place of ML.
    """
    weights = {
        "intuitiveness": 0.35,
        "exam_relevance": 0.30,
        "cultural_fit": 0.25,
        "freshness": 0.10,
    }

    scored: List[Dict[str, Any]] = []
    for m in candidates:
        text = m.get("text", "")
        category = m.get("category", "family")
        action_map = m.get("action_mapping", [])
        usage = int(m.get("usage_count", 0))

        s_int = _intuitiveness_score(concept, action_map, category, text)
        s_exam = _exam_score(marks_type, text)
        s_cult = _cultural_score(student_profile, category)
        s_fresh = _freshness_score(usage)
        total = (
            s_int * weights["intuitiveness"]
            + s_exam * weights["exam_relevance"]
            + s_cult * weights["cultural_fit"]
            + s_fresh * weights["freshness"]
        )
        m_scored = {**m, "scores": {
            "intuitiveness": s_int,
            "exam_relevance": s_exam,
            "cultural_fit": s_cult,
            "freshness": s_fresh,
            "total": total,
        }}
        scored.append(m_scored)

    scored.sort(key=lambda x: x["scores"]["total"], reverse=True)
    return scored[:3]


