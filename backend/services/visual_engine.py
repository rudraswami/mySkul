import logging
from typing import Dict, Any, Optional, List
import time

logger = logging.getLogger(__name__)

class VisualEngine:
    """
    Neuro-Symbolic Visual Engine for the AI Tutor.
    Generates culturally relevant visual metaphors and symbolic structures.
    """

    def __init__(self):
        """Initializes the VisualEngine."""
        self.metaphors = {
            "quantum_numbers": {
                "metaphor": "A hotel in Delhi",
                "symbolic_structure": ["Floor (Principal)", "Room Number (Orbital)", "Bed Position (Spin)"],
                "hero_visual": {
                    "url": "https://cdn.mgxai.com/visuals/physics/quantum_numbers/hotel_delhi.svg",
                    "alt_text": "A hotel in Delhi used as a metaphor for quantum numbers.",
                    "style": "sketch",
                }
            },
            "cricket": {
                "metaphor": "A cricket match",
                "symbolic_structure": ["Batsman", "Bowler", "Fielder"],
                "hero_visual": {
                    "url": "https://cdn.mgxai.com/visuals/physics/newton/cricket_story.svg",
                    "alt_text": "A cricket match used as a metaphor for a generic physics concept.",
                    "style": "sketch",
                }
            },
            "newtons_laws": {
                "metaphor": "Newton's Laws of Motion",
                "symbolic_structure": [
                    "First Law: An object at rest stays at rest.",
                    "Second Law: Force equals mass times acceleration.",
                    "Third Law: For every action, there is an equal and opposite reaction."
                ],
                "hero_visual": {
                    "url": "https://cdn.mgxai.com/visuals/physics/newton/laws_of_motion.svg",
                    "alt_text": "Visual representation of Newton's Laws of Motion.",
                    "style": "sketch",
                }
            }
        }

    def resolve_visual_metaphor(self, topic: str, student_persona: Dict[str, Any], *,
                                question: Optional[str] = None,
                                metaphors_used: Optional[List[str]] = None,
                                depth_target: Optional[str] = None) -> Dict[str, Any]:
        """
        Resolves a visual metaphor for a given topic and student persona.
        Optionally augments with an animation descriptor (Tier X) without replacing existing keys.
        """
        start_time = time.time()  # Start timing
        topic_key = topic.lower().replace(" ", "_")
        metaphor = self.metaphors.get(topic_key)

        if not metaphor:
            logger.warning(f"No metaphor found for topic '{topic}'. Using default metaphor.")
            metaphor = {
                "metaphor": "A generic concept",
                "symbolic_structure": ["Concept Element 1", "Concept Element 2"],
                "hero_visual": {
                    "url": "https://cdn.mgxai.com/visuals/placeholder.svg",
                    "alt_text": "A placeholder visual for undefined concepts.",
                    "style": "sketch",
                }
            }

        # Optional: Tier X animation augmentation (non-breaking)
        try:
            from .animation_library import resolve_animation_visual
            anim = resolve_animation_visual(
                question=question or "",
                metaphors_used=metaphors_used or [],
                depth_target=depth_target,
                topic_hint=topic_key,
            )
            if anim:
                metaphor = {**metaphor, "animation": anim, "fallback_visual_tier": "1"}
        except Exception:
            # Never break primary flow
            pass

        logger.info(f"Resolved visual metaphor for topic '{topic}': {metaphor.get('metaphor','?')}")
        self.log_frame_generation_success(topic)  # Log frame generation success
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        logger.info(f"Frame generation for '{topic}' took {elapsed_time:.2f} seconds.")
        return metaphor

    def log_frame_generation_success(self, topic: str):
        logger.info(f"Frame generated successfully for topic: {topic}")
