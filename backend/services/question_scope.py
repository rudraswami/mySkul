from __future__ import annotations

"""
Question scope extraction

Heuristic parser to detect what exactly the student asked so visuals can be
scoped tightly: define/explain/compare/derive/solve + subtopic hints (e.g.
Newton's first/second/third law) and whether an example is requested.
"""

import re
from typing import Dict, Optional


MODES = ["define", "explain", "compare", "derive", "prove", "solve"]


def build_scope(question: str) -> Dict[str, object]:
    q = (question or "").strip().lower()
    scope: Dict[str, object] = {
        "mode": "explain",
        "wants_example": False,
        "subtopic": None,
        "marks": None,
    }

    # Mode detection
    if re.search(r"\bdefine\b|\bwhat is\b|\bstate\b", q) and not re.search(r"\bexplain\b", q):
        scope["mode"] = "define"
    elif re.search(r"\bcompare\b|\bvs\b|\bversus\b", q):
        scope["mode"] = "compare"
    elif re.search(r"\bderive\b|\bshow that\b|\bprove\b", q):
        scope["mode"] = "derive"
    elif re.search(r"\bsolve\b|\bcalculate\b|\bfind\b", q):
        scope["mode"] = "solve"
    else:
        scope["mode"] = "explain"

    # Example request
    scope["wants_example"] = bool(re.search(r"with example|give example|example", q))

    # Marks
    m = re.search(r"(\d+)\s*marks?", q)
    if m:
        try:
            scope["marks"] = int(m.group(1))
        except Exception:
            pass

    # Subtopic: Newton's law specific
    if re.search(r"newton", q) and re.search(r"law", q):
        if re.search(r"first|1st|i\b", q):
            scope["subtopic"] = "first"
        elif re.search(r"second|2nd|ii\b", q):
            scope["subtopic"] = "second"
        elif re.search(r"third|3rd|iii\b", q):
            scope["subtopic"] = "third"

    return scope


def should_generate_visual(question: str, subject_hint: Optional[str] = None) -> bool:
    """
    Decide if a dynamic visual should be generated for this question.
    Heuristics:
    - Concept mapping hit OR
    - Numbers present + action verbs (vary/compare/derive/solve/explain/draw) OR
    - Marks specified and mode is explain/derive/compare
    Always allow when concept is detected.
    """
    try:
        from .concept_map import detect_concept  # Local import to avoid cycles
    except Exception:
        detect_concept = None

    q = (question or "").lower()
    # 1) Concept mapping
    if detect_concept:
        subj, cid = detect_concept(q, subject_hint)
        if cid:
            return True

    # 2) Numbers + verbs
    has_number = bool(re.search(r"\d", q))
    has_action = bool(re.search(r"\b(vary|change|compare|derive|solve|draw|plot|explain)\b", q))
    if has_number and has_action:
        return True

    # 3) Marks + mode (explain/derive/compare)
    sc = build_scope(q)
    if sc.get("marks") and sc.get("mode") in {"explain", "derive", "compare"}:
        return True

    return False
