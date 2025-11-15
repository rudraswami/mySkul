from __future__ import annotations

"""
Intent planning + adaptive structuring for AI Tutor dual responses.

Translates raw student queries into intent-aware directives that the response
pipeline can use to tune layouts, professor activation, visual gating, and
smart suggestion generation.
"""

import re
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from .adaptive_response import build_compare_visual


INTENT_NAMES = (
    "definition_query",
    "deep_dive",
    "compare_query",
    "application_request",
    "clarification_follow_up",
    "concept_explanation",
)


@dataclass(frozen=True)
class IntentPlan:
    intent: str
    layout: str
    needs_professor: bool
    allow_visual: bool
    auto_visual: bool
    ask_before_visual: bool
    suggestion_mode: str
    visual_mode: str
    context_flags: Tuple[str, ...] = ()
    compare_targets: Optional[Tuple[str, str]] = None


class IntentPlanner:
    """Utility helpers for detecting student intent and building layouts."""

    @staticmethod
    def detect(question: str, previous_text: Optional[str] = None) -> IntentPlan:
        q = (question or "").strip().lower()
        previous = (previous_text or "").lower()

        plan: IntentPlan
        if re.search(r"\b(what is|define|definition|meaning of|state)\b", q):
            plan = IntentPlanner._plan("definition_query")
        elif re.search(r"\b(compare|difference between|vs\b|versus|contrast)\b", q):
            targets = IntentPlanner._extract_compare_targets(question)
            plan = IntentPlanner._plan("compare_query", compare_targets=targets)
        elif re.search(r"\b(deep dive|go deep|prove|derive|exception|edge case|why exactly|explain in detail)\b", q):
            plan = IntentPlanner._plan("deep_dive")
        elif re.search(r"\b(real[- ]world|practical|application|use case|daily life|where .*used|apply this|in reality)\b", q):
            plan = IntentPlanner._plan("application_request")
        elif re.search(r"\b(again|another example|clarify|follow[- ]?up|one more|i know this|show other metaphor)\b", q) or "again" in previous:
            plan = IntentPlanner._plan("clarification_follow_up")
        else:
            plan = IntentPlanner._plan("concept_explanation")

        flags = IntentPlanner._infer_context_flags(question)
        if flags:
            plan = replace(plan, context_flags=flags)
        return plan

    @staticmethod
    def _plan(intent: str, compare_targets: Optional[Tuple[str, str]] = None) -> IntentPlan:
        config = {
            "definition_query": dict(
                layout="definition_block",
                needs_professor=False,
                allow_visual=False,
                auto_visual=False,
                ask_before_visual=False,
                suggestion_mode="foundation",
                visual_mode="micro_explainer",
            ),
            "deep_dive": dict(
                layout="reasoning_path",
                needs_professor=True,
                allow_visual=True,
                auto_visual=True,
                ask_before_visual=False,
                suggestion_mode="extension",
                visual_mode="animated_sequence",
            ),
            "compare_query": dict(
                layout="compare_table",
                needs_professor=True,
                allow_visual=False,
                auto_visual=False,
                ask_before_visual=False,
                suggestion_mode="contrast",
                visual_mode="compare_grid",
            ),
            "application_request": dict(
                layout="application_story",
                needs_professor=True,
                allow_visual=True,
                auto_visual=False,
                ask_before_visual=True,
                suggestion_mode="real_world",
                visual_mode="real_world_offer",
            ),
            "clarification_follow_up": dict(
                layout="follow_up",
                needs_professor=False,
                allow_visual=False,
                auto_visual=False,
                ask_before_visual=False,
                suggestion_mode="clarify",
                visual_mode="none",
            ),
            "concept_explanation": dict(
                layout="concept_layers",
                needs_professor=True,
                allow_visual=False,
                auto_visual=False,
                ask_before_visual=False,
                suggestion_mode="extension",
                visual_mode="hero_static",
            ),
        }

        cfg = config[intent]
        return IntentPlan(
            intent=intent,
            layout=cfg["layout"],
            needs_professor=cfg["needs_professor"],
            allow_visual=cfg["allow_visual"],
            auto_visual=cfg["auto_visual"],
            ask_before_visual=cfg["ask_before_visual"],
            suggestion_mode=cfg["suggestion_mode"],
            visual_mode=cfg["visual_mode"],
            context_flags=(),
            compare_targets=compare_targets,
        )

    @staticmethod
    def _infer_context_flags(question: str) -> Tuple[str, ...]:
        q = (question or "").lower()
        flags: List[str] = []

        if any(keyword in q for keyword in ("valency", "valence", "bond", "ionic", "covalent", "electron", "shell", "periodic")):
            flags.extend(["diagram_eligible", "chemistry_core"])
        if any(keyword in q for keyword in ("velocity", "motion", "speed", "accelerat", "projectile", "orbit", "wave", "momentum")):
            flags.append("requires_motion")
        if any(keyword in q for keyword in ("daily life", "real life", "in india", "train", "metro", "cooking", "school", "tuition")):
            flags.append("real_life_required")
        if any(keyword in q for keyword in ("diagram", "draw", "sketch", "label")):
            flags.append("diagram_eligible")
        if any(keyword in q for keyword in ("compare", "difference", "versus", "vs ")):
            flags.append("compare_visual")

        return tuple(dict.fromkeys(flags))

    @staticmethod
    def _extract_compare_targets(question: str) -> Tuple[str, str]:
        q = (question or "").lower()
        m = re.search(r"\bbetween\s+([a-z0-9\s\-]+?)\s+and\s+([a-z0-9\s\-]+)\b", q)
        if m:
            return (m.group(1).strip().title(), m.group(2).strip().title())
        m = re.search(r"\b([a-z0-9\s\-]+?)\s+(?:vs|versus)\s+([a-z0-9\s\-]+)\b", q)
        if m:
            return (m.group(1).strip().title(), m.group(2).strip().title())
        return ("Left", "Right")

    # -------- Adaptive block builders --------

    @staticmethod
    def build_structured_blocks(
        plan: IntentPlan,
        question: str,
        micro_sections: Dict,
        mentor_sections: Dict,
        professor_text: str,
        mentor_text: str,
    ) -> Dict[str, Dict]:
        """Return intent-aligned structured blocks for frontend consumption."""
        builder_map = {
            "definition_block": IntentPlanner._build_definition_block,
            "compare_table": IntentPlanner._build_compare_table,
            "application_story": IntentPlanner._build_application_story,
            "reasoning_path": IntentPlanner._build_reasoning_path,
            "follow_up": IntentPlanner._build_follow_up_card,
            "concept_layers": IntentPlanner._build_concept_layers,
        }

        builder = builder_map.get(plan.layout, lambda *_: {})
        return builder(
            plan=plan,
            question=question,
            micro_sections=micro_sections,
            mentor_sections=mentor_sections,
            professor_text=professor_text,
            mentor_text=mentor_text,
        )

    @staticmethod
    def _build_definition_block(**kwargs) -> Dict[str, Dict]:
        question = kwargs.get("question", "")
        micro_sections = kwargs.get("micro_sections", {})
        mentor_sections = kwargs.get("mentor_sections", {})
        definition = micro_sections.get("concept_overview") or IntentPlanner._first_sentence(kwargs.get("mentor_text", ""))
        steps = IntentPlanner._split_steps(micro_sections.get("step_by_step"))

        return {
            "definition_block": {
                "concept": IntentPlanner.extract_concept_name(question),
                "definition": definition,
                "exam_ready_points": steps[:3],
                "mentor_hint": mentor_sections.get("mentor_tip") or micro_sections.get("mentor_tip") or "",
            }
        }

    @staticmethod
    def _build_compare_table(**kwargs) -> Dict[str, Dict]:
        question = kwargs.get("question", "")
        plan: IntentPlan = kwargs.get("plan")
        visual = build_compare_visual(question)
        left = visual["stages"][0]["blocks"][0]["left"]
        right = visual["stages"][0]["blocks"][0]["right"]

        return {
            "compare_table": {
                "left_title": plan.compare_targets[0] if plan.compare_targets else left["title"],
                "right_title": plan.compare_targets[1] if plan.compare_targets else right["title"],
                "left_points": left.get("points", []),
                "right_points": right.get("points", []),
            }
        }

    @staticmethod
    def _build_application_story(**kwargs) -> Dict[str, Dict]:
        micro_sections = kwargs.get("micro_sections", {})
        mentor_sections = kwargs.get("mentor_sections", {})
        mentor_story = mentor_sections.get("motivation") or mentor_sections.get("encouragement")
        analogy = micro_sections.get("real_life_analogy")

        return {
            "application_story": {
                "scenario": analogy or mentor_story or "",
                "action_steps": IntentPlanner._split_steps(micro_sections.get("step_by_step"))[:3],
                "cta": "Spot this phenomenon today and describe it back." if analogy else "",
            }
        }

    @staticmethod
    def _build_reasoning_path(**kwargs) -> Dict[str, Dict]:
        micro_sections = kwargs.get("micro_sections", {})
        steps = IntentPlanner._split_steps(micro_sections.get("step_by_step"))
        notes = micro_sections.get("concept_overview") or ""

        return {
            "reasoning_path": {
                "steps": steps,
                "professor_notes": notes,
                "edge_case": micro_sections.get("mentor_tip") or "",
            }
        }

    @staticmethod
    def _build_follow_up_card(**kwargs) -> Dict[str, Dict]:
        mentor_sections = kwargs.get("mentor_sections", {})
        micro_sections = kwargs.get("micro_sections", {})
        return {
            "follow_up": {
                "what_changed": mentor_sections.get("recap") or IntentPlanner._first_sentence(kwargs.get("mentor_text", "")),
                "fresh_example": micro_sections.get("real_life_analogy") or "",
            }
        }

    @staticmethod
    def _build_concept_layers(**kwargs) -> Dict[str, Dict]:
        micro_sections = kwargs.get("micro_sections", {})
        return {
            "concept_layers": {
                "overview": micro_sections.get("concept_overview") or "",
                "key_steps": IntentPlanner._split_steps(micro_sections.get("step_by_step"))[:4],
                "real_life": micro_sections.get("real_life_analogy") or "",
            }
        }

    @staticmethod
    def generate_suggestions(plan: IntentPlan, concept: str, topic: str) -> List[str]:
        concept = concept or topic or "this concept"
        suggestions = {
            "foundation": [
                f"Can you spot {concept} in a board exam style question?",
                f"What changes in {concept} when conditions flip?",
            ],
            "extension": [
                f"Want to connect {concept} with the next harder topic?",
                f"Shall we attempt a derivation that includes {concept}?",
            ],
            "contrast": [
                f"How does {concept} behave when you swap the two setups?",
                "Need a quick lab-style scenario to compare both?",
            ],
            "real_world": [
                f"See how {concept} appears in your city or home experiment?",
                f"Would solving a quick numericals-based case for {concept} help?",
            ],
            "clarify": [
                "Want me to narrate this with a fresh metaphor?",
                "Should we check one textbook-style example for clarity?",
            ],
        }

        return suggestions.get(plan.suggestion_mode, suggestions["extension"])

    # -------- small helpers --------

    @staticmethod
    def _split_steps(text: Optional[str]) -> List[str]:
        if not text:
            return []
        cleaned = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE)
        parts = [part.strip(" -•") for part in re.split(r"\n|;", cleaned) if part.strip()]
        return parts

    @staticmethod
    def extract_concept_name(question: str) -> str:
        q = (question or "").strip().rstrip("?")
        q = re.sub(r"\b(what is|define|explain|please|kindly|tell me about)\b", "", q, flags=re.IGNORECASE)
        q = q.strip()
        return q.title() if q else "Concept"

    @staticmethod
    def _first_sentence(text: str) -> str:
        if not text:
            return ""
        match = re.split(r"(?<=[.!?])\s+", text.strip())
        return match[0] if match else text.strip()
