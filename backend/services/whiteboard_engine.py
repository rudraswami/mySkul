"""
🎨 Next-Gen Whiteboard Sketch Engine
====================================

Revolutionary visual explanation engine that feels like
a friend drawing on your notebook at 2 AM before exam.

Key Principles:
- Progressive reveal (5 beats)
- Indian context metaphors
- No boring MCQs
- Hand-drawn imperfect style
- Pure understanding flow

Now powered by comprehensive Visual Concepts Database:
- 50+ Physics concepts
- 40+ Chemistry concepts
- 45+ Biology concepts
- 35+ Mathematics concepts
= 170+ total visual templates
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

# Import comprehensive visual concepts database
try:
    from services.visual_concepts import (
        ALL_VISUAL_CONCEPTS,
        get_visual_config,
        get_all_concepts,
        get_concepts_by_subject,
        get_concept_count,
    )
    CONCEPTS_LOADED = True
except ImportError:
    CONCEPTS_LOADED = False
    ALL_VISUAL_CONCEPTS = {}

logger = logging.getLogger(__name__)


class BeatType(Enum):
    """Types of animation beats in the visual story."""
    DRAW_OBJECT = "draw_object"      # Draw the main concept
    DRAW_ACTION = "draw_action"      # Show the process/action
    DRAW_RESULT = "draw_result"      # Show the outcome
    HIGHLIGHT_FORMULA = "highlight_formula"  # Emphasize key formula
    MEMORY_HOOK = "memory_hook"      # Memorable takeaway


@dataclass
class VisualBeat:
    """A single beat in the visual story."""
    beat_type: BeatType
    label: str
    emoji: str
    insight: str  # Encouraging text
    duration_ms: int = 2000
    elements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WhiteboardScene:
    """Complete whiteboard scene configuration."""
    concept: str
    subject: str
    title: str
    title_hindi: str
    beats: List[VisualBeat]
    color_theme: Dict[str, str] = field(default_factory=dict)
    indian_metaphor: str = ""
    memory_hook: str = ""


class WhiteboardEngine:
    """
    Generates whiteboard-style visual explanations.
    
    Philosophy:
    - NO MCQs (pure understanding)
    - Indian context (relatable examples)
    - Progressive reveal (5 beats)
    - Encouraging tone (exam stress relief)
    
    Powered by 170+ visual templates across:
    - Physics, Chemistry, Biology, Mathematics
    """
    
    # Default template for unknown concepts
    DEFAULT_CONFIG = {
        "template": "generic",
        "subject": "general",
        "title": "Concept Explanation",
        "title_hindi": "",
        "keywords": [],
        "config": {
            "formula": "Key Concept",
            "memory_hook": "You got this! 💪"
        },
        "indian_context": "Let me explain this simply..."
    }
    
    # Color themes by subject
    SUBJECT_THEMES = {
        "physics": {
            "primary": "#FF9933",    # Saffron
            "secondary": "#138808",  # Green
            "accent": "#3B82F6",     # Blue
            "highlight": "#FBBF24",  # Amber
        },
        "chemistry": {
            "primary": "#8B5CF6",    # Purple
            "secondary": "#10B981",  # Emerald
            "accent": "#EF4444",     # Red
            "highlight": "#F59E0B",  # Amber
        },
        "biology": {
            "primary": "#10B981",    # Green
            "secondary": "#06B6D4",  # Cyan
            "accent": "#F97316",     # Orange
            "highlight": "#84CC16",  # Lime
        },
        "mathematics": {
            "primary": "#3B82F6",    # Blue
            "secondary": "#8B5CF6",  # Purple
            "accent": "#F43F5E",     # Rose
            "highlight": "#14B8A6",  # Teal
        }
    }
    
    def __init__(self):
        if CONCEPTS_LOADED:
            counts = get_concept_count()
            logger.info(f"🎨 Whiteboard Engine initialized with {len(ALL_VISUAL_CONCEPTS)} concepts")
            logger.info(f"   Physics: {counts.get('physics', 0)} | Chemistry: {counts.get('chemistry', 0)}")
            logger.info(f"   Biology: {counts.get('biology', 0)} | Math: {counts.get('mathematics', 0)}")
        else:
            logger.warning("⚠️ Visual concepts database not loaded, using fallback")
    
    def get_concept_config(self, concept: str) -> Dict[str, Any]:
        """Get visual configuration for a concept from database."""
        if CONCEPTS_LOADED:
            config = get_visual_config(concept)
            if config:
                return config
        return self.DEFAULT_CONFIG.copy()
    
    def _build_beats_from_config(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build animation beats based on visual template configuration."""
        template = config.get("template", "generic")
        visual_config = config.get("config", {})
        indian_context = config.get("indian_context", "")
        title = config.get("title", "Concept")
        
        formula = visual_config.get("formula", "Key Concept")
        memory_hook = visual_config.get("memory_hook", "You got this! 💪")
        
        # Template-specific beat generation
        if template == "race_comparison":
            return self._build_race_beats(config)
        elif template == "process_flow":
            return self._build_process_beats(config)
        elif template == "cause_effect":
            return self._build_cause_effect_beats(config)
        elif template == "cycle":
            return self._build_cycle_beats(config)
        elif template == "scale_spectrum":
            return self._build_scale_beats(config)
        elif template == "structure_anatomy":
            return self._build_structure_beats(config)
        elif template == "graph_relationship":
            return self._build_graph_beats(config)
        elif template == "sequence_timeline":
            return self._build_sequence_beats(config)
        else:
            # Generic beats
            return [
                {
                    "beat_type": "draw_object",
                    "label": title,
                    "emoji": "💡",
                    "insight": f"Let's understand {title.lower()}...",
                    "duration_ms": 2000
                },
                {
                    "beat_type": "draw_action",
                    "label": "How it works",
                    "emoji": "➡️",
                    "insight": indian_context,
                    "duration_ms": 2000
                },
                {
                    "beat_type": "draw_result",
                    "label": "Result",
                    "emoji": "✨",
                    "insight": "See the connection!",
                    "duration_ms": 2500
                },
                {
                    "beat_type": "highlight_formula",
                    "label": "Key Formula",
                    "emoji": "📐",
                    "formula": formula,
                    "insight": f"Remember: {formula}",
                    "duration_ms": 2000
                },
                {
                    "beat_type": "memory_hook",
                    "label": "Memory Hook",
                    "emoji": "🎯",
                    "message": memory_hook,
                    "insight": "You'll never forget this! 💪",
                    "duration_ms": 1500
                }
            ]
    
    def _build_race_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for race/comparison template."""
        visual_config = config.get("config", {})
        obj_a = visual_config.get("object_a", {})
        obj_b = visual_config.get("object_b", {})
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        return [
            {
                "beat_type": "draw_object",
                "label": f"{obj_a.get('label', 'Object A')} vs {obj_b.get('label', 'Object B')}",
                "emoji": "🏁",
                "insight": "Let's compare...",
                "duration_ms": 1500
            },
            {
                "beat_type": "draw_action",
                "label": obj_a.get("label", "Object A"),
                "emoji": "🔵",
                "insight": f"{obj_a.get('label', 'First')} starts...",
                "color": obj_a.get("color", "#3B82F6"),
                "duration_ms": 2500
            },
            {
                "beat_type": "draw_action",
                "label": obj_b.get("label", "Object B"),
                "emoji": "🔴",
                "insight": f"{obj_b.get('label', 'Second')} follows...",
                "color": obj_b.get("color", "#EF4444"),
                "duration_ms": 2500
            },
            {
                "beat_type": "highlight_formula",
                "label": "Key Insight",
                "emoji": "📐",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ]
    
    def _build_process_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for process flow template."""
        visual_config = config.get("config", {})
        inputs = visual_config.get("inputs", [])
        process_box = visual_config.get("process_box", {})
        outputs = visual_config.get("outputs", [])
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        return [
            {
                "beat_type": "draw_object",
                "label": "Inputs",
                "emoji": "📥",
                "insight": f"We need: {', '.join([i.get('label', '') for i in inputs])}",
                "elements": inputs,
                "duration_ms": 2000
            },
            {
                "beat_type": "draw_action",
                "label": process_box.get("label", "Process"),
                "emoji": process_box.get("icon", "⚙️"),
                "insight": f"Through {process_box.get('label', 'the process')}...",
                "duration_ms": 2500
            },
            {
                "beat_type": "draw_result",
                "label": "Outputs",
                "emoji": "📤",
                "insight": f"We get: {', '.join([o.get('label', '') for o in outputs])}",
                "elements": outputs,
                "duration_ms": 2000
            },
            {
                "beat_type": "highlight_formula",
                "label": "Formula",
                "emoji": "📐",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ]
    
    def _build_cause_effect_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for cause-effect template."""
        visual_config = config.get("config", {})
        cause = visual_config.get("cause", {})
        effect = visual_config.get("effect", {})
        action_label = visual_config.get("action_label", "leads to")
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        return [
            {
                "beat_type": "draw_object",
                "label": cause.get("label", "Cause"),
                "emoji": cause.get("icon", "💥"),
                "insight": f"When {cause.get('label', 'this happens')}...",
                "duration_ms": 2000
            },
            {
                "beat_type": "draw_action",
                "label": action_label,
                "emoji": "➡️",
                "insight": f"It {action_label.lower()}...",
                "duration_ms": 2000
            },
            {
                "beat_type": "draw_result",
                "label": effect.get("label", "Effect"),
                "emoji": effect.get("icon", "✨"),
                "insight": f"{effect.get('label', 'This happens')}!",
                "duration_ms": 2500
            },
            {
                "beat_type": "highlight_formula",
                "label": "Key Formula",
                "emoji": "📐",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ]
    
    def _build_cycle_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for cycle template."""
        visual_config = config.get("config", {})
        stages = visual_config.get("stages", [])
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        beats = []
        for i, stage in enumerate(stages[:4]):  # Limit to 4 stages for beats
            beats.append({
                "beat_type": "draw_action",
                "label": stage.get("label", f"Stage {i+1}"),
                "emoji": stage.get("icon", "🔄"),
                "insight": f"Step {i+1}: {stage.get('label', '')}",
                "color": stage.get("color", "#3B82F6"),
                "duration_ms": 2000
            })
        
        beats.append({
            "beat_type": "memory_hook",
            "label": "Cycle Continues!",
            "emoji": "🔄",
            "message": memory_hook,
            "formula": formula,
            "insight": f"{memory_hook} | {formula}",
            "duration_ms": 2000
        })
        
        return beats
    
    def _build_scale_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for scale/spectrum template."""
        visual_config = config.get("config", {})
        items = visual_config.get("items", [])
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        beats = [
            {
                "beat_type": "draw_object",
                "label": "The Scale",
                "emoji": "📊",
                "insight": "Let's see the spectrum...",
                "duration_ms": 1500
            }
        ]
        
        # Add key items
        for item in items[:3]:
            beats.append({
                "beat_type": "draw_action",
                "label": item.get("label", ""),
                "emoji": item.get("icon", "🔹"),
                "insight": f"{item.get('label', '')} at value {item.get('value', '')}",
                "color": item.get("color", "#3B82F6"),
                "duration_ms": 1500
            })
        
        beats.extend([
            {
                "beat_type": "highlight_formula",
                "label": "Pattern",
                "emoji": "📐",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ])
        
        return beats
    
    def _build_structure_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for structure/anatomy template."""
        visual_config = config.get("config", {})
        parts = visual_config.get("parts", [])
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        title = config.get("title", "Structure")
        
        beats = [
            {
                "beat_type": "draw_object",
                "label": title,
                "emoji": "🔍",
                "insight": f"Let's explore {title.lower()}...",
                "duration_ms": 1500
            }
        ]
        
        # Add parts (max 3 for animation)
        for part in parts[:3]:
            beats.append({
                "beat_type": "draw_action",
                "label": part.get("label", ""),
                "emoji": "📍",
                "insight": f"This is the {part.get('label', '')}",
                "duration_ms": 1500
            })
        
        beats.extend([
            {
                "beat_type": "highlight_formula",
                "label": "Key Point",
                "emoji": "💡",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ])
        
        return beats
    
    def _build_graph_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for graph/relationship template."""
        visual_config = config.get("config", {})
        equation = visual_config.get("equation", "")
        shape = visual_config.get("shape", "line")
        x_axis = visual_config.get("x_axis", "x")
        y_axis = visual_config.get("y_axis", "y")
        formula = visual_config.get("formula", equation)
        memory_hook = visual_config.get("memory_hook", "")
        
        return [
            {
                "beat_type": "draw_object",
                "label": "Axes",
                "emoji": "📊",
                "insight": f"X-axis: {x_axis}, Y-axis: {y_axis}",
                "duration_ms": 1500
            },
            {
                "beat_type": "draw_action",
                "label": f"Drawing {shape}",
                "emoji": "✏️",
                "insight": f"The relationship forms a {shape}...",
                "shape": shape,
                "duration_ms": 2500
            },
            {
                "beat_type": "draw_result",
                "label": equation,
                "emoji": "✨",
                "insight": f"This follows: {equation}",
                "duration_ms": 2000
            },
            {
                "beat_type": "highlight_formula",
                "label": "Formula",
                "emoji": "📐",
                "formula": formula,
                "insight": formula,
                "duration_ms": 2000
            },
            {
                "beat_type": "memory_hook",
                "label": "Remember!",
                "emoji": "🎯",
                "message": memory_hook,
                "insight": memory_hook,
                "duration_ms": 1500
            }
        ]
    
    def _build_sequence_beats(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build beats for sequence/timeline template."""
        visual_config = config.get("config", {})
        stages = visual_config.get("stages", [])
        formula = visual_config.get("formula", "")
        memory_hook = visual_config.get("memory_hook", "")
        
        beats = []
        for i, stage in enumerate(stages[:4]):
            beats.append({
                "beat_type": "draw_action",
                "label": stage.get("label", f"Step {i+1}"),
                "emoji": stage.get("icon", f"{i+1}️⃣"),
                "insight": stage.get("description", stage.get("label", "")),
                "duration_ms": 1800
            })
        
        beats.append({
            "beat_type": "memory_hook",
            "label": "Complete!",
            "emoji": "🎯",
            "message": memory_hook,
            "formula": formula,
            "insight": memory_hook,
            "duration_ms": 1500
        })
        
        return beats
    
    def generate_scene(
        self,
        concept: str,
        subject: str,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete whiteboard scene for a concept.
        
        Args:
            concept: The concept to explain (e.g., 'force', 'photosynthesis')
            subject: Subject area (physics, chemistry, biology, math)
            question: Original student question for context
        
        Returns:
            Scene configuration dict for frontend rendering
        """
        concept_lower = concept.lower().strip()
        
        # Get concept configuration from database
        config = self.get_concept_config(concept_lower)
        
        # Get template type
        template = config.get("template", "generic")
        
        # Get title
        title = config.get("title", concept.title())
        title_hindi = config.get("title_hindi", "")
        
        # Get formula and memory hook from config
        visual_config = config.get("config", {})
        formula = visual_config.get("formula", "Key Concept")
        memory_hook = visual_config.get("memory_hook", "You got this! 💪")
        
        # Build the animated beats
        beats = self._build_beats_from_config(config)
        
        # Get color theme
        color_theme = self.SUBJECT_THEMES.get(
            subject.lower(), 
            self.SUBJECT_THEMES["physics"]
        )
        
        # Build complete scene
        scene = {
            "version": "3.0",
            "engine": "whiteboard",
            "concept": concept_lower,
            "concept_id": config.get("concept_id", concept_lower),
            "subject": config.get("subject", subject),
            "chapter": config.get("chapter", ""),
            "class_level": config.get("class_level", []),
            "template": template,
            "title": title,
            "title_hindi": title_hindi,
            "beats": beats,
            "total_duration_ms": sum(b.get("duration_ms", 2000) for b in beats),
            "color_theme": color_theme,
            "visual_config": visual_config,
            "indian_context": config.get("indian_context", ""),
            "style": {
                "hand_drawn": True,
                "progressive_reveal": True,
                "no_mcq": True
            },
            "encouragement": {
                "start": f"Let me show you {title.lower()} the easy way! 😊",
                "end": memory_hook
            }
        }
        
        logger.info(f"🎨 Generated whiteboard scene: {concept} (template: {template})")
        return scene
    
    def extract_concept(self, question: str) -> Optional[str]:
        """
        Extract the main concept from a question.
        
        Uses the visual concepts database for comprehensive keyword matching.
        """
        if not question:
            return None
            
        question_lower = question.lower()
        
        # First, check exact concept matches
        if CONCEPTS_LOADED:
            for concept_id in ALL_VISUAL_CONCEPTS:
                if concept_id in question_lower:
                    return concept_id
            
            # Then check keywords from all concepts
            for concept_id, config in ALL_VISUAL_CONCEPTS.items():
                keywords = config.get("keywords", [])
                if any(kw in question_lower for kw in keywords):
                    return concept_id
        
        # Fallback comprehensive keyword-based detection
        keyword_map = {
            # Physics
            "force": ["force", "newton", "push", "pull", "f=ma", "tension"],
            "velocity": ["velocity", "speed", "motion", "fast", "slow", "moving"],
            "gravity": ["gravity", "fall", "weight", "free fall", "g=9.8"],
            "acceleration": ["accelerate", "decelerate", "speed up", "slow down"],
            "momentum": ["momentum", "collision", "crash", "impact", "impulse"],
            "friction": ["friction", "rough", "smooth", "slide", "slip"],
            "energy": ["energy", "kinetic", "potential", "work", "power"],
            "wave": ["wave", "sound", "frequency", "wavelength", "amplitude"],
            "reflection": ["reflection", "mirror", "reflect"],
            "refraction": ["refraction", "bending", "lens", "prism"],
            "electric_current": ["current", "electricity", "ampere", "circuit"],
            "ohms_law": ["ohm", "v=ir", "voltage", "resistance"],
            
            # Chemistry
            "photosynthesis": ["photosynthesis", "plant food", "chlorophyll", "glucose sunlight"],
            "acids": ["acid", "ph", "sour", "hcl", "h+"],
            "bases": ["base", "alkaline", "naoh", "oh-", "soapy"],
            "atom": ["atom", "electron", "proton", "neutron", "nucleus"],
            "ionic_bond": ["ionic", "nacl", "salt", "electrovalent"],
            "covalent_bond": ["covalent", "sharing", "molecule"],
            "oxidation_reduction": ["oxidation", "reduction", "redox", "rust"],
            "periodic_table": ["periodic", "element", "group", "period"],
            
            # Biology
            "cell": ["cell", "nucleus", "mitochondria", "organelle", "membrane"],
            "respiration": ["respiration", "breathing", "oxygen", "atp", "cellular"],
            "photosynthesis": ["photosynthesis", "chloroplast", "glucose", "plant food"],
            "dna": ["dna", "gene", "chromosome", "heredity", "genetic"],
            "mitosis": ["mitosis", "cell division", "pmat"],
            "meiosis": ["meiosis", "gamete", "haploid"],
            "circulatory_system": ["blood", "heart", "circulation", "artery", "vein"],
            "nervous_system": ["nerve", "neuron", "brain", "reflex"],
            "ecosystem": ["ecosystem", "food chain", "producer", "consumer"],
            
            # Math
            "quadratic_equation": ["quadratic", "parabola", "x squared", "ax2+bx+c"],
            "pythagoras_theorem": ["pythagoras", "right triangle", "hypotenuse", "a2+b2"],
            "linear_equation": ["linear", "y=mx+c", "straight line"],
            "trigonometric_ratios": ["sin", "cos", "tan", "trigonometry"],
            "arithmetic_progression": ["ap", "arithmetic progression", "common difference"],
            "probability_basics": ["probability", "chance", "random"],
        }
        
        for concept, keywords in keyword_map.items():
            if any(kw in question_lower for kw in keywords):
                return concept
        
        return None
    
    def get_available_concepts(self, subject: Optional[str] = None) -> List[str]:
        """Get list of available concepts, optionally filtered by subject."""
        if CONCEPTS_LOADED:
            if subject:
                return get_concepts_by_subject(subject)
            return get_all_concepts()
        return []
    
    def get_stats(self) -> Dict[str, int]:
        """Get concept statistics by subject."""
        if CONCEPTS_LOADED:
            return get_concept_count()
        return {}


# Singleton instance
whiteboard_engine = WhiteboardEngine()


def generate_whiteboard_visual(
    concept: str,
    subject: str,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate a whiteboard visual.
    
    Usage:
        from services.whiteboard_engine import generate_whiteboard_visual
        
        scene = generate_whiteboard_visual("force", "physics")
    """
    return whiteboard_engine.generate_scene(
        concept=concept,
        subject=subject,
        question=question
    )
