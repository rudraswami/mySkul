"""
Micro-check generator to validate metaphor mapping quickly.
Produces a short prompt and expected facets based on core actions.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


ACTION_FACETS = {
    "transfer": ["what flows", "rate/amount per time"],
    "accumulate": ["what adds up", "total/result"],
    "transform": ["input", "output"],
    "measure": ["quantity", "unit/formula"],
    "iterate": ["step", "what changes each step"],
    "balance": ["opposing parts", "condition for balance"],
}


DOMAIN_FACETS: Dict[str, Dict[str, List[str]]] = {
    "chemistry_bonding": {
        "transfer": ["what moves (electrons)", "who gives/accepts"],
        "balance": ["charge after transfer", "stability reason"],
        "compose": ["bond type", "why that type"],
    },
    "chemistry_solutions": {
        "propagate": ["what spreads (solute)", "direction (high→low)"],
        "balance": ["when balance occurs", "what equalizes"],
        "measure": ["concentration", "units"],
    },
    "physics_electricity": {
        "transfer": ["what flows", "per-second amount (I)"] ,
        "measure": ["formula", "units"],
    },
    "physics_mechanics": {
        "measure": ["quantity (v/a/F)", "relation (e.g., F=ma)"],
        "transform": ["what changes", "cause"],
    },
    "physics_waves": {
        "measure": ["frequency/wavelength/amplitude", "relation (v=fλ)"],
        "propagate": ["medium/energy", "direction"],
    },
    "calculus": {
        "accumulate": ["what accumulates", "with respect to (dx)"],
        "measure": ["rate of change", "with respect to (x/t)"],
    },
    "trigonometry": {
        "measure": ["opposite/adjacent/hyp", "angle reference"],
    },
    "probability": {
        "measure": ["event", "sample space"],
    },
    "biology_genetics": {
        "transfer": ["what passes (alleles)", "to whom"],
        "compose": ["genotype", "phenotype"],
    },
}


def _localize_prompt(en_text: str, locale: Optional[str]) -> str:
    if not locale:
        return en_text
    loc = locale.lower()
    if loc.startswith("hi") or loc.startswith("bn-hi"):
        # Simple Hinglish: replace a few terms
        return (
            en_text.replace("what", "kya").replace("and", "aur").replace("Using", "Use karke")
        )
    return en_text


def make_micro_check(
    question: str,
    core_actions: List[str],
    top_metaphors: List[Dict[str, Any]],
    domain: Optional[str] = None,
    locale: Optional[str] = None,
) -> Dict[str, Any]:
    primary = top_metaphors[0]["name"] if top_metaphors else "Family"
    secondary = top_metaphors[1]["name"] if len(top_metaphors) > 1 else None
    act = core_actions[0] if core_actions else "transform"
    facets = None
    if domain and domain in DOMAIN_FACETS and act in DOMAIN_FACETS[domain]:
        facets = DOMAIN_FACETS[domain][act]
    else:
        facets = ACTION_FACETS.get(act, ["key idea", "result"])
    if secondary:
        prompt_en = (
            f"In the {primary} + {secondary} blend, what maps to '{facets[0]}' and "
            f"what controls '{facets[1]}'?"
        )
    else:
        prompt_en = f"Using {primary}, what is '{facets[0]}' and what is '{facets[1]}'?"
    prompt = _localize_prompt(prompt_en, locale)
    return {"prompt": prompt, "expected_facets": facets}
