import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class VisualEngine:
    """
    Neuro-Symbolic Visual Engine for the AI Tutor.
    Generates culturally relevant visual metaphors and symbolic structures.
    """

    def __init__(self):
        """Initializes the VisualEngine."""
        self.topic_keywords = {
            "valency": ["valency", "valence", "bond", "covalent", "ionic", "outer shell", "electron"],
            "velocity": ["velocity", "speed", "motion", "projectile", "distance", "time", "vector"],
            "catalyst": ["catalyst", "reaction rate", "enzyme", "activation energy"],
            "photosynthesis": ["photosynthesis", "chlorophyll", "sunlight", "glucose"],
            "quantum_numbers": ["quantum number", "orbital", "shell", "principal"],
            "newtons_laws": ["newton", "force", "law of motion", "action", "reaction"],
        }

        self.visual_library: Dict[str, Dict[str, Any]] = self._load_templates()

    def resolve_visual_metaphor(
        self,
        topic: str,
        student_persona: Dict[str, Any],
        intent_plan: Optional[Any] = None,
        context_flags: Optional[Tuple[str, ...]] = None,
    ) -> Dict[str, Any]:
        """
        Resolves a visual metaphor for a given topic and student persona.
        """
        start_time = time.time()
        topic_key = self._match_topic(topic)
        entry = self.visual_library.get(topic_key, self.visual_library["generic"])

        metaphor = {
            "metaphor": entry.get("metaphor", "Story time with Dhruv"),
            "symbolic_structure": entry.get("symbolic_structure", ["Concept anchor", "Hook"]),
            "hero_visual": entry.get("hero_visual", {}).copy(),
        }

        render_strategy = entry.get("render_strategy", {}) or {}

        directives = {
            "visual_mode": intent_plan.visual_mode if intent_plan else "hero_static",
            "context_flags": list(context_flags or ()),
            "caption": entry.get("caption"),
            "offer_text": entry.get("offer_text"),
            "cta_text": entry.get("cta_text", "Show Visual"),
            "persona": entry.get("persona", "mentor"),
            "requires_consent": render_strategy.get("requires_consent", entry.get("requires_consent", False)),
            "force_hero": entry.get("force_hero", False),
            "library_topic": topic_key,
            "visual_type": entry.get("visual_type", "scene"),
            "template": entry.get("template"),
            "render_strategy": render_strategy,
            "intent_types": entry.get("intent_types", []),
        }

        if entry.get("lottie_file"):
            directives["lottie_file"] = entry["lottie_file"]
        if entry.get("asset_url"):
            directives["asset_url"] = entry["asset_url"]
        if entry.get("animation"):
            directives["animation"] = entry["animation"]

        metaphor["visual_directives"] = directives

        logger.info(f"Resolved visual metaphor for topic '{topic_key}': {entry.get('metaphor', 'Generic metaphor')}")
        self.log_frame_generation_success(topic_key)
        elapsed_time = time.time() - start_time
        logger.info(f"Frame generation for '{topic_key}' took {elapsed_time:.2f} seconds.")
        return metaphor

    def _match_topic(self, topic: str) -> str:
        text = (topic or "").lower()
        for key, tokens in self.topic_keywords.items():
            if any(token in text for token in tokens):
                return key
        return "generic"

    def log_frame_generation_success(self, topic: str):
        logger.info(f"Frame generated successfully for topic: {topic}")

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        registry_path = Path(__file__).resolve().parents[1] / "visual_library" / "templates.json"
        try:
            with registry_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if "generic" not in data:
                    data["generic"] = self._default_generic()
                return data
        except Exception as exc:
            logger.error(f"Failed to load visual templates: {exc}")
            return {"generic": self._default_generic()}

    def _default_generic(self) -> Dict[str, Any]:
        return {
            "metaphor": "Friendly chalkboard walkthrough",
            "symbolic_structure": ["Concept Anchor", "Key relationship"],
            "hero_visual": {
                "url": "https://cdn.mgxai.com/visuals/placeholder.svg",
                "alt_text": "Placeholder classroom sketch",
                "style": "sketch",
            },
            "caption": "Dhruv sketches the concept on a chalkboard.",
            "offer_text": "Want me to sketch it quickly?",
            "render_strategy": {"trigger": "on_click"},
            "persona": "mentor",
        }
