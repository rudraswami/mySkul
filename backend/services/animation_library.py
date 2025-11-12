from __future__ import annotations

"""
Animation Visual Library (Tier X)

Purpose:
- Provide optional animated metaphor scenes for supported topic+metaphor pairs.
- Never replace existing SVG/template flow; only augment results when applicable.

Triggering rules (must ALL hold):
- Intent indicates deeper or application-style explanation (deep_dive/application).
- A supported (topic, metaphor) animation asset exists.

Return shape (embedded into existing visual results):
{
  "visual_type": "animation",
  "metaphor": "catalyst",
  "topic": "chemistry_kinetics",
  "animation_asset_url": "https://cdn.visuals.dhruvai.ai/animations/catalyst_tadka.mp4",
  "fallback_visual_tier": "1"
}
"""

from typing import Dict, Optional, List

from .adaptive_response import detect_intent
from .topic_classifier import TopicClassifier


# Canonical animation asset registry
# Keys are normalized topic keys and friendly metaphor categories
ANIMATION_ASSETS: Dict[str, Dict[str, str]] = {
    # Physics
    "newtons_laws": {
        "cricket": "https://cdn.visuals.dhruvai.ai/animations/newton_cricket_bat_ball.mp4",
    },
    "physics_mechanics": {
        "cricket": "https://cdn.visuals.dhruvai.ai/animations/newton_cricket_bat_ball.mp4",
    },

    # Chemistry
    "chemistry_kinetics": {
        "cooking": "https://cdn.visuals.dhruvai.ai/animations/catalyst_tadka.mp4",
    },
    "chemistry_reaction": {
        "cooking": "https://cdn.visuals.dhruvai.ai/animations/catalyst_tadka.mp4",
    },

    # Quantum numbers / atomic structure
    "quantum_physics": {
        "accommodation": "https://cdn.visuals.dhruvai.ai/animations/quantum_hotel_floors.mp4",
    },
    "quantum_numbers": {
        "accommodation": "https://cdn.visuals.dhruvai.ai/animations/quantum_hotel_floors.mp4",
    },

    # Probability / permutations
    "probability": {
        "cooking": "https://cdn.visuals.dhruvai.ai/animations/filter_coffee_permutations.mp4",
    },
}


def _normalize_topic(question: str, topic_hint: Optional[str]) -> str:
    if topic_hint:
        return topic_hint
    try:
        return TopicClassifier.classify_topic(question)
    except Exception:
        return "generic"


def _friendly_metaphor_name(metaphors_used: List[str]) -> Optional[str]:
    """Map internal metaphor tags to friendly categories used in assets."""
    if not metaphors_used:
        return None
    m = (metaphors_used[0] or "").lower()
    # Common normalizations
    mapping = {
        "cricket": "cricket",
        "food": "cooking",
        "family": "family",
        "bollywood": "bollywood",
        "gaming": "gaming",
        "hotel": "accommodation",
        "accommodation": "accommodation",
        "cooking": "cooking",
    }
    return mapping.get(m, m)


def should_offer_animation(question: str, depth_target: Optional[str]) -> bool:
    """Gate for Tier X animation. Conservative to avoid over-triggering."""
    intent = detect_intent(question)
    if intent in {"deep_dive", "application_based"}:
        return True
    # If the PRD depth looks deep, allow as well
    if (depth_target or "").lower() == "deep":
        return True
    # Keywords that imply show-in-motion
    q = (question or "").lower()
    if any(k in q for k in ["show how", "animate", "in action", "demonstrate", "visualize", "step by step"]):
        return True
    return False


def resolve_animation_visual(
    question: str,
    metaphors_used: List[str],
    depth_target: Optional[str] = None,
    topic_hint: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    """
    Return an animation descriptor when supported and intent qualifies.
    Never raises; returns None if no suitable asset.
    """
    try:
        if not should_offer_animation(question, depth_target):
            return None
        topic = _normalize_topic(question, topic_hint)
        metaphor = _friendly_metaphor_name(metaphors_used)
        if not metaphor:
            return None

        # Direct match on topic, else try a couple of relaxed aliases
        asset = ANIMATION_ASSETS.get(topic, {}).get(metaphor)
        if not asset:
            # Relaxed topic aliases
            aliases = {
                "newtons_laws": ["physics_mechanics"],
                "chemistry_kinetics": ["chemistry_reaction"],
                "quantum_numbers": ["quantum_physics"],
            }.get(topic, [])
            for alt in aliases:
                asset = ANIMATION_ASSETS.get(alt, {}).get(metaphor)
                if asset:
                    break

        if not asset:
            return None

        return {
            "visual_type": "animation",
            "metaphor": metaphor,
            "topic": topic,
            "animation_asset_url": asset,
            # We do not replace the existing flow; default fallback is template tier (1)
            "fallback_visual_tier": "1",
        }
    except Exception:
        return None

