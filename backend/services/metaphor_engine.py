from __future__ import annotations

"""
Dynamic Metaphor Generation Engine

Implements PRD Steps 1–2:
- Step 1: Concept deconstruction (core actions, entities, constraints, marks)
- Step 2: 5‑Muse candidate generation, filtering, and selection (returns top 3)

This module is dependency‑light and deterministic (no network calls).
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple


Muse = Literal["family", "food", "cricket", "bollywood", "gaming"]
MetaphorType = Literal["mechanical", "narrative", "spatial", "social", "data_flow"]


@dataclass
class StudentDNA:
    level: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    locale_language: Optional[str] = None
    gender: Optional[str] = None
    board: Optional[str] = None
    exam: Optional[str] = None
    accessibility: Dict[str, Any] = field(default_factory=dict)
    device: Optional[str] = None
    prior_metaphor_success: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConceptBundle:
    question: str
    core_actions: List[str]
    entities: List[str]
    constraints: List[str]
    marks_distribution: Dict[str, Any]


@dataclass
class MetaphorCandidate:
    id: str
    muse: Muse
    type: MetaphorType
    hook: str
    mapping: List[str]
    boundaries: str
    exam_anchor: str
    references: List[str]
    visual_elements: List[str]
    usage_count: int = 0
    safety_flags: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    total: float = 0.0


ACTION_TAXONOMY = (
    "transfer",
    "accumulate",
    "compare",
    "transform",
    "search",
    "optimize",
    "prove",
    "construct",
    "predict",
)


def deconstruct_question(question: str) -> ConceptBundle:
    """Step 1: Extract core actions, entities, constraints, marks distribution.

    Heuristics only (no heavy NLP). Safe defaults if detection is weak.
    """
    text = question.strip()

    # Actions (shallow verb mapping)
    verb_map = {
        r"explain|define|describe": "construct",
        r"prove|justify": "prove",
        r"compare|contrast": "compare",
        r"find|search|locate": "search",
        r"optimi[sz]e|minimi[sz]e|maximi[sz]e|best": "optimize",
        r"predict|estimate|forecast": "predict",
        r"transform|convert|simplify|reduce": "transform",
        r"transfer|move|flow": "transfer",
        r"accumulate|sum|integrate|area": "accumulate",
    }
    actions: List[str] = []
    for pattern, action in verb_map.items():
        if re.search(pattern, text, re.IGNORECASE):
            actions.append(action)
    if not actions:
        actions = ["construct"]

    # Entities: grab noun-like tokens (very light), fall back to keywords
    # Split on punctuation and filter short/common words
    tokens = re.split(r"[^A-Za-z0-9_]+", text.lower())
    stop = {
        "the",
        "a",
        "an",
        "of",
        "to",
        "and",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "what",
        "how",
        "why",
        "base",
        "case",
        "show",
        "using",
    }
    entities = [t for t in tokens if len(t) > 2 and t not in stop]
    entities = list(dict.fromkeys(entities))[:6]

    # Constraints: collect comparators/quantifiers/keywords
    constraint_patterns = [r"base case", r"O\(n\)", r"proof", r"diagram", r"formula"]
    constraints: List[str] = []
    for pat in constraint_patterns:
        if re.search(pat, text, re.IGNORECASE):
            constraints.append(pat)

    # Marks distribution
    parts: List[int] = []
    # [2+4] or [2 + 4]
    m = re.search(r"\[(\d+(?:\s*[+,]\s*\d+)*)\]", text)
    if m:
        parts = [int(p) for p in re.split(r"[+,]", m.group(1))]
    else:
        inline = re.findall(r"(\d+)\s*(?:marks?|pts?)", text, re.IGNORECASE)
        parts = [int(inline[0])] if inline else []
    total = sum(parts) if parts else 3
    depth_target = (
        "brief" if total <= 2 else "moderate" if total <= 5 else "deep"
    )
    marks_distribution = {"total": total, "parts": parts or [total], "depth_target": depth_target}

    return ConceptBundle(
        question=text,
        core_actions=actions,
        entities=entities,
        constraints=constraints,
        marks_distribution=marks_distribution,
    )


def generate_5_muse_candidates(bundle: ConceptBundle, dna: Optional[StudentDNA]) -> List[MetaphorCandidate]:
    """
    Step 2: Generate 3–5 candidates from the Five‑Muse System.

    Always include Family and Food; conditionally include Cricket/Bollywood/Gaming.
    """
    entities_text = ", ".join(bundle.entities[:3]) or "concept"

    base: List[Tuple[Muse, str]] = [
        ("family", f"Home analogy for {entities_text}"),
        ("food", f"Cooking analogy for {entities_text}"),
    ]

    # Conditional muses
    cond: List[Tuple[Muse, str]] = []
    if dna and (dna.gender == "M" or (dna.interests and any(i.lower() in {"cricket", "sports"} for i in dna.interests))):
        cond.append(("cricket", f"Cricket drill for {entities_text}"))
    if dna and (dna.gender == "F" or (dna.interests and any(i.lower() in {"movies", "bollywood"} for i in dna.interests))):
        cond.append(("bollywood", f"Movie plot for {entities_text}"))
    # Gaming for Gen Z / default urban tilt
    cond.append(("gaming", f"Game mechanics for {entities_text}"))

    muses: List[Tuple[Muse, str]] = base + cond
    seen: set = set()
    candidates: List[MetaphorCandidate] = []
    for muse_name, desc in muses:
        if muse_name in seen:
            continue
        seen.add(muse_name)
        cand = MetaphorCandidate(
            id=f"{muse_name}_1",
            muse=muse_name,  # type: ignore[arg-type]
            type=_default_type_for_muse(muse_name),
            hook=desc,
            mapping=_mapping_for_muse(muse_name, bundle.entities),
            boundaries=_boundaries_for(bundle),
            exam_anchor=_exam_anchor_for(bundle),
            references=[muse_name],
            visual_elements=["arrows", "labels", "flow"],
        )
        candidates.append(cand)

    # Enforce 3–5
    return candidates[:5]


def _default_type_for_muse(muse: Muse) -> MetaphorType:
    return {
        "family": "social",
        "food": "mechanical",
        "cricket": "spatial",
        "bollywood": "narrative",
        "gaming": "data_flow",
    }[muse]


def _mapping_for_muse(muse: Muse, entities: List[str]) -> List[str]:
    ent = entities[:2] or ["idea", "step"]
    if muse == "family":
        return [f"Concept = household task", f"{ent[0]} = role", f"{ent[-1]} = rule"]
    if muse == "food":
        return [f"Concept = recipe", f"{ent[0]} = ingredient", f"{ent[-1]} = cooking step"]
    if muse == "cricket":
        return [f"Concept = drill", f"{ent[0]} = ball", f"{ent[-1]} = field"]
    if muse == "bollywood":
        return [f"Concept = plot arc", f"{ent[0]} = hero goal", f"{ent[-1]} = twist"]
    return [f"Concept = game loop", f"{ent[0]} = input", f"{ent[-1]} = rule"]


def _boundaries_for(bundle: ConceptBundle) -> str:
    if any("base case" in c for c in bundle.constraints) or "recursion" in bundle.question.lower():
        return "Stop at base case; ensure progress toward it."
    return "State limits and edge cases explicitly."


def _exam_anchor_for(bundle: ConceptBundle) -> str:
    total = bundle.marks_distribution.get("total", 3)
    return f"Targets {total} mark(s) with stepwise mapping"


def score_and_select(
    bundle: ConceptBundle, dna: Optional[StudentDNA], candidates: List[MetaphorCandidate], k: int = 3
) -> List[MetaphorCandidate]:
    """Score by intuitiveness, exam_relevance, cultural_fit, freshness; pick distinct muses."""
    weights = {"intuitiveness": 0.35, "exam_relevance": 0.30, "cultural_fit": 0.25, "freshness": 0.10}

    def intuitiveness(c: MetaphorCandidate) -> float:
        # Light proxy: more explicit mappings + presence of entities
        ent_hit = sum(1 for e in bundle.entities if any(e in m.lower() for m in c.mapping))
        return min(1.0, 0.5 + 0.1 * ent_hit)

    def exam_rel(c: MetaphorCandidate) -> float:
        # Proxy: shorter mapping and explicit exam anchor
        base = 0.6 if bundle.marks_distribution.get("total", 3) <= 3 else 0.7
        return min(1.0, base + (0.05 * max(0, 4 - len(c.mapping))))

    def cultural_fit(c: MetaphorCandidate) -> float:
        if not dna:
            return 0.7 if c.muse in ("family", "food") else 0.5
        score = 0.6
        if c.muse in ("family", "food"):
            score += 0.2
        if c.muse == "cricket" and (dna.gender == "M" or any(i.lower() == "cricket" for i in dna.interests)):
            score += 0.15
        if c.muse == "bollywood" and (dna.gender == "F" or any(i.lower() in {"movies", "bollywood"} for i in dna.interests)):
            score += 0.1
        if c.muse == "gaming" and any(i.lower() in {"gaming", "technology", "cs"} for i in dna.interests):
            score += 0.1
        return min(1.0, score)

    def freshness(c: MetaphorCandidate) -> float:
        used = c.usage_count
        return max(0.2, 1.0 - (used / 1000.0))

    for c in candidates:
        c.scores["intuitiveness"] = intuitiveness(c)
        c.scores["exam_relevance"] = exam_rel(c)
        c.scores["cultural_fit"] = cultural_fit(c)
        c.scores["freshness"] = freshness(c)
        c.total = sum(c.scores[k2] * w for k2, w in weights.items())

    ranked = sorted(candidates, key=lambda x: x.total, reverse=True)

    # Ensure distinct muses
    picked: List[MetaphorCandidate] = []
    seen_muses: set = set()
    for cand in ranked:
        if cand.muse in seen_muses:
            continue
        picked.append(cand)
        seen_muses.add(cand.muse)
        if len(picked) >= k:
            break
    return picked


def select_metaphors(question: str, student_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Facade: Full Step 1–2 flow returning bundle, candidates, and picks."""
    dna = StudentDNA(**student_profile) if student_profile else None
    bundle = deconstruct_question(question)
    candidates = generate_5_muse_candidates(bundle, dna)
    picks = score_and_select(bundle, dna, candidates)
    return {
        "bundle": bundle,
        "candidates": candidates,
        "top": picks,
    }

