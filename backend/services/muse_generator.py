"""
5-Muse Metaphor Candidate Generator
Generates culturally tuned candidate metaphors from five universal muse categories:
Family/Household, Food/Cooking, Cricket/Sports, Bollywood/Movies, Gaming/Technology.

This module is lightweight, dependency-free, and safe to call synchronously.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


MUSE_UNIVERSALITY = {
    "family": 0.90,
    "food": 0.95,
    "cricket": 0.60,
    "bollywood": 0.70,  # avg across genders
    "gaming": 0.60,     # varies by urban/Gen Z
}


def _gender(student: Optional[Dict[str, Any]]) -> Optional[str]:
    g = (student or {}).get("gender")
    if not g:
        return None
    g = str(g).strip().upper()
    return g if g in {"M", "F"} else None


def _region(student: Optional[Dict[str, Any]]) -> str:
    return (student or {}).get("region") or "India"


def _interests(student: Optional[Dict[str, Any]]) -> List[str]:
    vals = (student or {}).get("interests") or []
    return [str(v).lower() for v in vals]


def generate_5_muse_candidates(
    concept: str,
    student_profile: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Generate candidate metaphors across the 5 muse categories.

    Returns a list of candidates with minimal, safe features for ranking.
    """
    g = _gender(student_profile)
    region = _region(student_profile)
    interests = _interests(student_profile)

    # Base candidates per muse (short, neutral phrasing). Hinglish retained lightly where apt.
    family = [
        {
            "name": "Family Sharing",
            "category": "family",
            "text": f"{concept}: ghar mein cheezein baantna—jo zyada hai, woh share hota hai (transfer/accumulate).",
            "references": ["home", "sharing", region],
            "visual_elements": ["members", "arrows", "items"],
            "action_mapping": ["transfer", "accumulate"],
        },
        {
            "name": "Rooms and Roles",
            "category": "family",
            "text": f"{concept}: ghar ke kamre aur zimmedariyan—har role ek jagah aur kaam (structure/mapping).",
            "references": ["rooms", region],
            "visual_elements": ["rooms", "labels", "paths"],
            "action_mapping": ["classify", "compose"],
        },
    ]

    food = [
        {
            "name": "Biryani Process",
            "category": "food",
            "text": f"{concept}: biryani banana—steps follow karte hue result banta hai (transform).",
            "references": ["biryani", region],
            "visual_elements": ["layers", "steam", "arrow"],
            "action_mapping": ["transform", "compose"],
        },
        {
            "name": "Chai Sugar",
            "category": "food",
            "text": f"{concept}: chai mein shakkar ghulna—meetha dheere-dheere har jagah failta (diffuse/balance).",
            "references": ["chai", region],
            "visual_elements": ["cup", "stir", "swirl"],
            "action_mapping": ["propagate", "balance"],
        },
    ]

    cricket = [
        {
            "name": "Batting Order",
            "category": "cricket",
            "text": f"{concept}: batting order matter karta—kaun pehle aata hai result badalta (permutation/priority).",
            "references": ["cricket", region],
            "visual_elements": ["lineup", "score", "arrow"],
            "action_mapping": ["compose", "order"],
        },
        {
            "name": "Field Positions",
            "category": "cricket",
            "text": f"{concept}: fielding positions—vector jaisa direction + magnitude kaam aata (vectors/map).",
            "references": ["cricket", region],
            "visual_elements": ["field", "arrows"],
            "action_mapping": ["measure", "classify"],
        },
    ]

    bollywood = [
        {
            "name": "Plot Arc",
            "category": "bollywood",
            "text": f"{concept}: movie ka arc—shuruat se climax tak badlav (rate/accumulate).",
            "references": ["movies", region],
            "visual_elements": ["curve", "beats"],
            "action_mapping": ["iterate", "measure", "transform"],
        },
        {
            "name": "On‑Screen Chemistry",
            "category": "bollywood",
            "text": f"{concept}: do leads ki chemistry—bandh mazboot ya halka (bond strength analogy).",
            "references": ["movies", region],
            "visual_elements": ["pair", "link", "tension"],
            "action_mapping": ["compose", "balance"],
        },
    ]

    gaming = [
        {
            "name": "Game Loop",
            "category": "gaming",
            "text": f"{concept}: game loop—har chakkar mein state update hoti (iterate/optimize).",
            "references": ["gaming", region],
            "visual_elements": ["loop", "state", "tick"],
            "action_mapping": ["iterate", "optimize"],
        },
        {
            "name": "Power‑Up Speed",
            "category": "gaming",
            "text": f"{concept}: power‑up se speed badalti—rate of change samjho (derivative).",
            "references": ["gaming", region],
            "visual_elements": ["bar", "arrow", "spark"],
            "action_mapping": ["measure", "transform"],
        },
    ]

    # Gender/interest gating (soft): adjust candidate ordering
    candidates: List[Dict[str, Any]] = []

    # Always include universal: family + food
    candidates.extend(family[:1])
    candidates.extend(food[:1])

    # Consider remaining from each muse
    pool: List[Dict[str, Any]] = []
    pool.extend(family[1:])
    pool.extend(food[1:])
    # Sports: prefer if male or interest contains cricket/sports
    if g == "M" or any(x in interests for x in ["cricket", "sports", "football"]):
        pool.extend(cricket)
    # Bollywood: prefer if F or explicit interest
    if g == "F" or any(x in interests for x in ["bollywood", "movies", "music"]):
        pool.extend(bollywood)
    # Gaming: prefer if Gen Z/urban inferred via interests
    if any(x in interests for x in ["gaming", "technology", "coding", "pubg", "free fire", "valorant"]):
        pool.extend(gaming)

    # Fallback: if pool lacks variety, add one from each
    if not any(p["category"] == "cricket" for p in pool):
        pool.append(cricket[0])
    if not any(p["category"] == "bollywood" for p in pool):
        pool.append(bollywood[0])
    if not any(p["category"] == "gaming" for p in pool):
        pool.append(gaming[0])

    # Final list: start with two universal + pick up to 3 diverse others
    seen_categories = {c["category"] for c in candidates}
    for p in pool:
        if len(candidates) >= 5:
            break
        if p["category"] not in seen_categories:
            candidates.append(p)
            seen_categories.add(p["category"])

    # Add feature defaults
    for c in candidates:
        c.setdefault("usage_count", 0)
        c.setdefault("scores", {})

    return candidates


