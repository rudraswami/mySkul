"""
Minimal i18n for visual labels and prompts.
Extensible language map with safe defaults and fallbacks.
"""
from __future__ import annotations

from typing import Dict, Optional


LANG_MAP: Dict[str, Dict[str, str]] = {
    # English (default)
    "en": {
        "concept": "Concept",
        "answer": "Answer",
        "marks": "Marks",
        "students_forget": "90% students forget this",
        "topper_hack": "Topper hack: three keywords bold",
    },
    # Hindi/Hinglish (hi-IN)
    "hi": {
        "concept": "Concept",
        "answer": "Answer",
        "marks": "Ank",
        "students_forget": "90% students yeh bhool jaate hain",
        "topper_hack": "Topper ka hack: teen keywords bold",
    },
    # Tamil (romanized)
    "ta": {
        "concept": "Karuthu",  # concept/idea
        "answer": "Badil",
        "marks": "Marks",
        "students_forget": "90% students idhai marandhuduvanga",
        "topper_hack": "Topper oda hack: moonu keywords bold",
    },
    # Telugu (romanized)
    "te": {
        "concept": "Aalochana",
        "answer": "Samadhanam",
        "marks": "Marks",
        "students_forget": "90% students idi marchipotharu",
        "topper_hack": "Topper hack: moodu keywords bold",
    },
    # Kannada (romanized)
    "kn": {
        "concept": "Kalpane",
        "answer": "Uttara",
        "marks": "Marks",
        "students_forget": "90% vidyarthigalu idannu mareyuttare",
        "topper_hack": "Topper hack: mooru keywords bold",
    },
    # Malayalam (romanized)
    "ml": {
        "concept": "Dharnam",
        "answer": "Utharam",
        "marks": "Marks",
        "students_forget": "90% students ith marakkum",
        "topper_hack": "Topper hack: moonu keywords bold",
    },
}


def _norm(locale: Optional[str]) -> str:
    if not locale:
        return "en"
    loc = locale.lower()
    if loc.startswith("hi"):
        return "hi"
    if loc.startswith("ta"):
        return "ta"
    if loc.startswith("te"):
        return "te"
    if loc.startswith("kn"):
        return "kn"
    if loc.startswith("ml"):
        return "ml"
    return "en"


def get_labels(locale: Optional[str], script: Optional[str] = None) -> Dict[str, str]:
    key = _norm(locale)
    base = LANG_MAP.get("en", {})
    over = LANG_MAP.get(key, {})
    out = {**base, **over}
    return out

