"""
Concept Deconstruction (Step 1)
Lightweight, dependency-free parser to extract core actions, entities, and marks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


ACTION_SYNONYMS = {
    "transfer": {"transfer", "move", "send", "flow", "pass", "route"},
    "accumulate": {"accumulate", "gather", "add", "sum", "collect", "store", "deposit"},
    "transform": {"transform", "convert", "change", "map", "translate"},
    "compare": {"compare", "contrast", "versus", "vs"},
    "search": {"search", "find", "locate", "lookup", "retrieve"},
    "propagate": {"propagate", "spread", "diffuse", "backpropagate"},
    "balance": {"balance", "equilibrate", "equalize"},
    "optimize": {"optimize", "minimize", "maximize", "improve", "tune"},
    "iterate": {"iterate", "repeat", "loop"},
    "classify": {"classify", "label", "categorize", "cluster"},
    "compose": {"compose", "combine", "blend", "merge"},
    "measure": {"measure", "compute", "calculate", "estimate", "evaluate"},
}


@dataclass
class Entity:
    text: str
    role: str = "context"
    qualifiers: List[str] = field(default_factory=list)


@dataclass
class Marks:
    total_marks: Optional[int]
    type: str
    cues: List[str] = field(default_factory=list)


@dataclass
class ConceptDeconstruction:
    core_actions: List[str]
    entities: List[Entity]
    marks: Marks
    confidence: float
    domain: str = "general"  # e.g., chemistry_bonding, physics_electricity, calculus
    topic: Optional[str] = None


def _extract_marks(text: str) -> Marks:
    m = re.search(r"(\d+)\s*(marks?|pts?|points?)", text, re.I)
    total: Optional[int] = None
    cues: List[str] = []
    if m:
        cues.append(m.group(0))
        try:
            total = int(m.group(1))
        except Exception:
            total = None
    if total is None:
        # keyword cues
        if re.search(r"\b(define|list|short answer|mcq)\b", text, re.I):
            return Marks(total_marks=None, type="short", cues=["short-answer-cue"])
        if re.search(r"\b(explain|compute|with example)\b", text, re.I):
            return Marks(total_marks=None, type="medium", cues=["medium-cue"])
        if re.search(r"\b(derive|prove|discuss|in detail|essay)\b", text, re.I):
            return Marks(total_marks=None, type="long", cues=["long-cue"])
        return Marks(total_marks=None, type="medium", cues=[])
    mtype = "short" if total <= 2 else ("medium" if total <= 5 else "long")
    return Marks(total_marks=total, type=mtype, cues=cues)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]*", text)


PHRASE_ACTION_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"rate of change|derivative|d\w*/d\w*", re.I), "measure"),
    (re.compile(r"integrat(e|ion)|area under (the )?curve", re.I), "accumulate"),
    (re.compile(r"current|flow|through (a|the) (wire|pipe)", re.I), "transfer"),
    (re.compile(r"share|distribute|allocate|transfer", re.I), "transfer"),
    (re.compile(r"diffus(e|ion)|spread|osmosis", re.I), "propagate"),
    (re.compile(r"prove|derive|show that", re.I), "transform"),
]


def _core_actions(tokens: List[str], text: Optional[str] = None) -> List[str]:
    found: List[str] = []
    low = [t.lower() for t in tokens]
    # phrase-based detection first
    if text:
        for pat, act in PHRASE_ACTION_PATTERNS:
            if pat.search(text):
                found.append(act)
    for arche, syns in ACTION_SYNONYMS.items():
        if any(t in syns for t in low):
            found.append(arche)
    # defaults based on cue verbs if none found
    if not found:
        if any(t in {"explain", "describe"} for t in low):
            found.append("transform")
        elif any(t in {"find", "compute", "calculate"} for t in low):
            found.append("measure")
    # de-duplicate preserving order
    out: List[str] = []
    for a in found:
        if a not in out:
            out.append(a)
    return out[:3] or ["transform"]


def _entities(tokens: List[str]) -> List[Entity]:
    # naive heuristic: nouns ≈ words not in verb cue list
    VERBS = {
        "explain",
        "describe",
        "define",
        "find",
        "compute",
        "calculate",
        "prove",
        "derive",
    }
    ents: List[Entity] = []
    for t in tokens:
        if t.lower() not in VERBS and len(t) > 2:
            ents.append(Entity(text=t, role="context"))
    # dedup
    seen = set()
    out: List[Entity] = []
    for e in ents:
        key = e.text.lower()
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out[:5]


DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "chemistry_bonding": [
        "bond", "ionic", "covalent", "valence", "electron", "ion", "compound", "salt",
    ],
    "chemistry_solutions": [
        "solution", "osmosis", "diffusion", "solute", "solvent", "molarity", "concentration",
    ],
    "physics_electricity": [
        "current", "voltage", "resistance", "ohm", "circuit", "wire", "charge", "capacitor",
    ],
    "physics_mechanics": [
        "force", "velocity", "acceleration", "projectile", "momentum", "newton",
    ],
    "physics_waves": [
        "wave", "frequency", "wavelength", "amplitude", "doppler", "interference",
    ],
    "calculus": [
        "integral", "derivative", "differentiate", "integration", "limit", "area under",
    ],
    "algebra": [
        "equation", "polynomial", "quadratic", "root", "factor",
    ],
    "trigonometry": [
        "sin", "cos", "tan", "trigonometry", "angle", "hypotenuse", "radian",
    ],
    "probability": [
        "probability", "permutation", "combination", "random", "event", "outcome",
    ],
    "biology_genetics": [
        "gene", "genetics", "allele", "dna", "inheritance", "mendel",
    ],
}


def _detect_domain(text: str) -> Tuple[str, Optional[str]]:
    low = text.lower()
    best_domain = "general"
    best_hits = 0
    for domain, keys in DOMAIN_KEYWORDS.items():
        hits = sum(1 for k in keys if k in low)
        if hits > best_hits:
            best_hits = hits
            best_domain = domain
    topic = None
    return best_domain, topic


def _detect_with_classifier(question: str, student_dna: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[str]]:
    """Try using TopicClassifier (if available) to detect topic/domain.
    Returns (domain, topic) or (None, None) if unavailable.
    """
    try:
        from services.topic_classifier import TopicClassifier  # type: ignore

        preferred = (student_dna or {}).get("preferred_metaphor") or "family"
        region = (student_dna or {}).get("region") or "India"
        sel = TopicClassifier.select_metaphor(question, preferred_category=preferred, region=region)
        topic = sel.get("topic") if isinstance(sel, dict) else None
        domain = None
        # In this codebase, topic labels generally match our domain keys
        if topic and isinstance(topic, str):
            domain = topic
        return domain, topic
    except Exception:
        return None, None


def deconstruct(question: str, student_dna: Optional[Dict[str, Any]] = None) -> ConceptDeconstruction:
    text = question.strip()
    tokens = _tokenize(text)
    marks = _extract_marks(text)
    actions = _core_actions(tokens, text)
    ents = _entities(tokens)
    # Prefer classifier; fallback to keywords
    domain, topic = _detect_with_classifier(text, student_dna)
    if not domain:
        domain, topic = _detect_domain(text)
    # confidence: simple heuristic
    conf = 0.3 + (0.2 if actions else 0) + (0.2 if ents else 0) + (0.2 if marks.type != "medium" else 0)
    return ConceptDeconstruction(
        core_actions=actions,
        entities=ents,
        marks=marks,
        confidence=min(conf, 0.95),
        domain=domain,
        topic=topic,
    )
