"""
visual_concept_detector.py
Phase 6: AI-powered concept detection for visual generation

Detects:
- Concept type (motion, biology process, math topic, etc.)
- Visual template family
- Required objects and animations
- Interaction types
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConceptType(Enum):
    """Types of concepts that can be visualized"""
    MOTION = "motion"
    BIOLOGY_PROCESS = "biology_process"
    MATH_TOPIC = "math_topic"
    CHEMISTRY_REACTION = "chemistry_reaction"
    ECONOMICS_CHART = "economics_chart"
    HISTORY_TIMELINE = "history_timeline"
    GEOMETRY = "geometry"
    ELECTRICITY = "electricity"
    ALGEBRA = "algebra"
    TRIGONOMETRY = "trigonometry"
    OPTICS = "optics"
    WAVES = "waves"
    THERMODYNAMICS = "thermodynamics"
    GENETICS = "genetics"
    ECOLOGY = "ecology"
    STATISTICS = "statistics"
    CALCULUS = "calculus"


class VisualType(Enum):
    """Types of visual representations"""
    LAB_DEMO = "lab_demo"
    REAL_WORLD_SCENARIO = "real_world_scenario"
    STEP_TIMELINE = "step_timeline"
    GRAPH_SIMULATION = "graph_simulation"
    THREE_D_MODEL = "3d_model"
    OBJECT_INTERACTION = "object_interaction"
    EQUATION_SLIDER = "equation_slider"
    LAYERED_REVEAL = "layered_reveal"
    COMPARATIVE = "comparative"
    FLOWCHART = "flowchart"


@dataclass
class ConceptDetectionResult:
    """Result of concept detection"""
    concept_type: ConceptType
    concept_name: str
    subject: str
    visual_types: List[VisualType]
    objects: List[str]
    animations: List[str]
    interactions: List[str]
    formulas: List[str]
    difficulty: str  # easy, medium, hard
    confidence: float
    indian_context: Optional[str] = None


# Keyword patterns for concept detection
CONCEPT_PATTERNS = {
    # Physics - Mechanics
    ConceptType.MOTION: {
        "keywords": [
            r"\b(motion|velocity|speed|acceleration|displacement|distance|kinematics)\b",
            r"\b(moving|moves|travel|travels|journey)\b",
            r"\b(v\s*=|s\s*=|a\s*=)\b",
            r"\b(equations?\s+of\s+motion)\b",
        ],
        "subject": "physics",
        "visual_types": [VisualType.LAB_DEMO, VisualType.REAL_WORLD_SCENARIO, VisualType.GRAPH_SIMULATION],
        "objects": ["car", "ball", "train", "auto_rickshaw", "runner"],
        "animations": ["linear_motion", "accelerate", "decelerate", "trajectory"],
        "interactions": ["slider", "drag", "tap"],
        "formulas": ["v = u + at", "s = ut + ½at²", "v² = u² + 2as"],
    },
    
    # Physics - Force
    "force": {
        "keywords": [
            r"\b(force|newton|push|pull|thrust|friction)\b",
            r"\b(f\s*=\s*m\s*[×x*]\s*a)\b",
            r"\b(newton'?s?\s+law)\b",
        ],
        "subject": "physics",
        "visual_types": [VisualType.LAB_DEMO, VisualType.OBJECT_INTERACTION, VisualType.EQUATION_SLIDER],
        "objects": ["ball", "box", "spring", "pulley", "cricket_ball_detailed"],
        "animations": ["push", "pull", "throw", "vector_grow"],
        "interactions": ["slider", "tap", "drag"],
        "formulas": ["F = ma", "f = μN", "W = mg"],
    },
    
    # Physics - Gravity
    "gravity": {
        "keywords": [
            r"\b(gravity|gravitation|free\s*fall|weight|g\s*=\s*9\.8)\b",
            r"\b(falling|falls|drop|dropped)\b",
            r"\b(universal\s+gravitation)\b",
        ],
        "subject": "physics",
        "visual_types": [VisualType.LAB_DEMO, VisualType.REAL_WORLD_SCENARIO],
        "objects": ["mango", "ball", "feather", "apple", "pendulum"],
        "animations": ["fall", "bounce", "swing"],
        "interactions": ["slider", "tap", "drop"],
        "formulas": ["F = Gm₁m₂/r²", "g = GM/R²", "W = mg"],
    },
    
    # Physics - Optics
    ConceptType.OPTICS: {
        "keywords": [
            r"\b(light|reflection|refraction|lens|mirror|prism)\b",
            r"\b(optical|ray|beam|spectrum)\b",
            r"\b(snell'?s?\s+law|refractive\s+index)\b",
        ],
        "subject": "physics",
        "visual_types": [VisualType.LAB_DEMO, VisualType.OBJECT_INTERACTION],
        "objects": ["lens_convex", "lens_concave", "prism", "mirror", "bulb"],
        "animations": ["ray_trace", "refract", "reflect", "dispersion"],
        "interactions": ["drag", "rotate", "slider"],
        "formulas": ["n₁sinθ₁ = n₂sinθ₂", "1/f = 1/v - 1/u"],
    },
    
    # Physics - Electricity
    ConceptType.ELECTRICITY: {
        "keywords": [
            r"\b(electricity|current|voltage|resistance|circuit|ohm)\b",
            r"\b(v\s*=\s*i\s*r)\b",
            r"\b(ampere|volt|watt)\b",
        ],
        "subject": "physics",
        "visual_types": [VisualType.LAB_DEMO, VisualType.OBJECT_INTERACTION],
        "objects": ["battery", "bulb", "resistor", "wire", "switch"],
        "animations": ["current_flow", "glow", "connect"],
        "interactions": ["drag", "tap", "slider"],
        "formulas": ["V = IR", "P = VI", "R = ρL/A"],
    },
    
    # Chemistry - Atomic Structure
    "atom": {
        "keywords": [
            r"\b(atom|electron|proton|neutron|nucleus|orbital)\b",
            r"\b(atomic\s+(structure|number|mass))\b",
            r"\b(bohr|rutherford)\b",
        ],
        "subject": "chemistry",
        "visual_types": [VisualType.THREE_D_MODEL, VisualType.LAYERED_REVEAL],
        "objects": ["atom_model", "electron", "proton", "neutron"],
        "animations": ["orbit", "spin", "zoom"],
        "interactions": ["rotate", "tap", "layer_toggle"],
        "formulas": ["A = Z + N", "E = -13.6/n² eV"],
    },
    
    # Chemistry - Reactions
    ConceptType.CHEMISTRY_REACTION: {
        "keywords": [
            r"\b(reaction|reactant|product|catalyst|combustion)\b",
            r"\b(chemical\s+equation|balancing)\b",
            r"\b(oxidation|reduction|redox)\b",
        ],
        "subject": "chemistry",
        "visual_types": [VisualType.STEP_TIMELINE, VisualType.LAB_DEMO],
        "objects": ["test_tube", "beaker", "bunsen_burner", "molecule"],
        "animations": ["bubble", "color_change", "flame", "mix"],
        "interactions": ["pour", "heat", "mix", "slider"],
        "formulas": ["A + B → C + D", "Rate = k[A]ⁿ"],
    },
    
    # Biology - Cell
    "cell": {
        "keywords": [
            r"\b(cell|nucleus|mitochondria|chloroplast|organelle)\b",
            r"\b(cell\s+(membrane|wall|division))\b",
            r"\b(cytoplasm|ribosome|golgi)\b",
        ],
        "subject": "biology",
        "visual_types": [VisualType.LAYERED_REVEAL, VisualType.THREE_D_MODEL],
        "objects": ["cell", "nucleus", "mitochondria", "chloroplast", "rbc", "wbc"],
        "animations": ["zoom", "highlight", "label_reveal"],
        "interactions": ["tap", "zoom", "layer_toggle"],
        "formulas": ["Cell Theory"],
    },
    
    # Biology - Photosynthesis
    ConceptType.BIOLOGY_PROCESS: {
        "keywords": [
            r"\b(photosynthesis|chlorophyll|stomata|glucose)\b",
            r"\b(light\s+reaction|dark\s+reaction|calvin\s+cycle)\b",
            r"\b(6co2|c6h12o6)\b",
        ],
        "subject": "biology",
        "visual_types": [VisualType.STEP_TIMELINE, VisualType.FLOWCHART],
        "objects": ["leaf", "oxygen_bubble", "sun", "chloroplast"],
        "animations": ["absorb", "produce", "flow", "bubble_rise"],
        "interactions": ["tap", "slider", "step_through"],
        "formulas": ["6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂"],
    },
    
    # Biology - Genetics
    ConceptType.GENETICS: {
        "keywords": [
            r"\b(dna|rna|gene|chromosome|heredity|genetics)\b",
            r"\b(replication|transcription|translation)\b",
            r"\b(mendel|allele|genotype|phenotype)\b",
        ],
        "subject": "biology",
        "visual_types": [VisualType.THREE_D_MODEL, VisualType.STEP_TIMELINE],
        "objects": ["dna_helix", "chromosome", "gene", "cell"],
        "animations": ["unwind", "replicate", "transcribe"],
        "interactions": ["rotate", "zoom", "step_through"],
        "formulas": ["A-T, G-C base pairing"],
    },
    
    # Math - Algebra
    ConceptType.ALGEBRA: {
        "keywords": [
            r"\b(equation|polynomial|quadratic|linear|variable)\b",
            r"\b(solve|simplify|factor|expand)\b",
            r"\b(ax²|bx|roots|discriminant)\b",
        ],
        "subject": "mathematics",
        "visual_types": [VisualType.EQUATION_SLIDER, VisualType.GRAPH_SIMULATION],
        "objects": ["axes", "parabola", "line"],
        "animations": ["draw_curve", "highlight_root", "transform"],
        "interactions": ["slider", "tap", "drag"],
        "formulas": ["ax² + bx + c = 0", "x = (-b ± √(b²-4ac))/2a"],
    },
    
    # Math - Geometry
    ConceptType.GEOMETRY: {
        "keywords": [
            r"\b(triangle|circle|square|rectangle|polygon)\b",
            r"\b(area|perimeter|angle|side|vertex)\b",
            r"\b(pythagoras|congruent|similar)\b",
        ],
        "subject": "mathematics",
        "visual_types": [VisualType.OBJECT_INTERACTION, VisualType.EQUATION_SLIDER],
        "objects": ["right_triangle", "circle_with_radius", "axes"],
        "animations": ["construct", "measure", "rotate"],
        "interactions": ["drag", "measure", "slider"],
        "formulas": ["a² + b² = c²", "A = πr²", "A = ½bh"],
    },
    
    # Math - Trigonometry
    ConceptType.TRIGONOMETRY: {
        "keywords": [
            r"\b(sin|cos|tan|trigonometry|angle)\b",
            r"\b(sine|cosine|tangent|secant|cosecant)\b",
            r"\b(unit\s+circle|radian|degree)\b",
        ],
        "subject": "mathematics",
        "visual_types": [VisualType.OBJECT_INTERACTION, VisualType.GRAPH_SIMULATION],
        "objects": ["right_triangle", "unit_circle", "axes"],
        "animations": ["rotate", "trace_curve", "highlight"],
        "interactions": ["slider", "drag", "tap"],
        "formulas": ["sin θ = opp/hyp", "cos θ = adj/hyp", "tan θ = opp/adj"],
    },
    
    # Math - Calculus
    ConceptType.CALCULUS: {
        "keywords": [
            r"\b(derivative|integral|differentiation|integration)\b",
            r"\b(limit|dy/dx|∫|d/dx)\b",
            r"\b(slope|area\s+under\s+curve|rate\s+of\s+change)\b",
        ],
        "subject": "mathematics",
        "visual_types": [VisualType.GRAPH_SIMULATION, VisualType.EQUATION_SLIDER],
        "objects": ["axes", "curve", "tangent_line", "shaded_area"],
        "animations": ["draw_tangent", "shade_area", "animate_limit"],
        "interactions": ["slider", "drag", "tap"],
        "formulas": ["dy/dx", "∫f(x)dx", "lim x→a f(x)"],
    },
    
    # Statistics
    ConceptType.STATISTICS: {
        "keywords": [
            r"\b(mean|median|mode|standard\s+deviation)\b",
            r"\b(probability|statistics|distribution)\b",
            r"\b(histogram|bar\s+chart|pie\s+chart)\b",
        ],
        "subject": "mathematics",
        "visual_types": [VisualType.GRAPH_SIMULATION, VisualType.COMPARATIVE],
        "objects": ["bar_chart", "histogram", "pie_chart", "scatter_plot"],
        "animations": ["grow_bar", "reveal", "highlight"],
        "interactions": ["hover", "tap", "filter"],
        "formulas": ["μ = Σx/n", "σ = √(Σ(x-μ)²/n)"],
    },
}

# Indian context mappings
INDIAN_CONTEXTS = {
    "motion": ["auto_rickshaw", "train", "scooter", "bus"],
    "force": ["cricket", "kabaddi", "wrestling"],
    "gravity": ["mango", "coconut", "neem_tree"],
    "energy": ["solar_panel", "windmill", "biogas"],
    "chemistry": ["haldi", "nimbu", "baking_soda"],
    "biology": ["banyan_tree", "lotus", "peacock"],
    "economics": ["kirana_store", "sabzi_mandi", "chai_stall"],
}


class VisualConceptDetector:
    """Detects concept type and visual requirements from questions"""
    
    def __init__(self):
        self.patterns = CONCEPT_PATTERNS
        self.indian_contexts = INDIAN_CONTEXTS
    
    def detect(self, question: str, subject_hint: Optional[str] = None) -> ConceptDetectionResult:
        """
        Detect concept type and visual requirements from a question
        
        Args:
            question: The student's question
            subject_hint: Optional subject hint (physics, chemistry, etc.)
            
        Returns:
            ConceptDetectionResult with all visual generation info
        """
        question_lower = question.lower()
        
        best_match = None
        best_score = 0
        
        # Search through all concept patterns
        for concept_key, pattern_data in self.patterns.items():
            score = self._calculate_match_score(question_lower, pattern_data["keywords"])
            
            # Boost score if subject matches hint
            if subject_hint and pattern_data.get("subject") == subject_hint.lower():
                score *= 1.5
            
            if score > best_score:
                best_score = score
                best_match = (concept_key, pattern_data)
        
        if not best_match or best_score < 0.3:
            # Return default result
            return self._create_default_result(question)
        
        concept_key, pattern_data = best_match
        
        # Determine concept type
        if isinstance(concept_key, ConceptType):
            concept_type = concept_key
            concept_name = concept_key.value
        else:
            concept_type = self._infer_concept_type(concept_key, pattern_data["subject"])
            concept_name = concept_key
        
        # Get Indian context if applicable
        indian_context = self._get_indian_context(concept_name, pattern_data["subject"])
        
        return ConceptDetectionResult(
            concept_type=concept_type,
            concept_name=concept_name,
            subject=pattern_data["subject"],
            visual_types=pattern_data["visual_types"],
            objects=pattern_data["objects"],
            animations=pattern_data["animations"],
            interactions=pattern_data["interactions"],
            formulas=pattern_data["formulas"],
            difficulty=self._estimate_difficulty(question),
            confidence=min(best_score, 1.0),
            indian_context=indian_context,
        )
    
    def _calculate_match_score(self, text: str, keywords: List[str]) -> float:
        """Calculate match score based on keyword patterns"""
        matches = 0
        total = len(keywords)
        
        for pattern in keywords:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        return matches / total if total > 0 else 0
    
    def _infer_concept_type(self, concept_key: str, subject: str) -> ConceptType:
        """Infer concept type from key and subject"""
        type_mapping = {
            "physics": {
                "force": ConceptType.MOTION,
                "gravity": ConceptType.MOTION,
                "motion": ConceptType.MOTION,
                "light": ConceptType.OPTICS,
                "electricity": ConceptType.ELECTRICITY,
            },
            "chemistry": {
                "atom": ConceptType.CHEMISTRY_REACTION,
                "reaction": ConceptType.CHEMISTRY_REACTION,
            },
            "biology": {
                "cell": ConceptType.BIOLOGY_PROCESS,
                "photosynthesis": ConceptType.BIOLOGY_PROCESS,
            },
            "mathematics": {
                "quadratic": ConceptType.ALGEBRA,
                "triangle": ConceptType.GEOMETRY,
                "trigonometry": ConceptType.TRIGONOMETRY,
            },
        }
        
        return type_mapping.get(subject, {}).get(concept_key, ConceptType.MOTION)
    
    def _get_indian_context(self, concept_name: str, subject: str) -> Optional[str]:
        """Get relevant Indian context for the concept"""
        contexts = self.indian_contexts.get(concept_name) or self.indian_contexts.get(subject)
        if contexts:
            return contexts[0]  # Return first relevant context
        return None
    
    def _estimate_difficulty(self, question: str) -> str:
        """Estimate difficulty based on question complexity"""
        question_lower = question.lower()
        
        # Hard indicators
        hard_patterns = [
            r"derive", r"prove", r"complex", r"advanced",
            r"jee\s+advanced", r"olympiad", r"challenging"
        ]
        
        # Medium indicators
        medium_patterns = [
            r"calculate", r"find", r"solve", r"determine",
            r"explain\s+how", r"why\s+does"
        ]
        
        for pattern in hard_patterns:
            if re.search(pattern, question_lower):
                return "hard"
        
        for pattern in medium_patterns:
            if re.search(pattern, question_lower):
                return "medium"
        
        return "easy"
    
    def _create_default_result(self, question: str) -> ConceptDetectionResult:
        """Create default result when no pattern matches"""
        return ConceptDetectionResult(
            concept_type=ConceptType.MOTION,
            concept_name="general",
            subject="physics",
            visual_types=[VisualType.LAB_DEMO],
            objects=["box", "ball"],
            animations=["move"],
            interactions=["tap"],
            formulas=[],
            difficulty="easy",
            confidence=0.1,
            indian_context=None,
        )


# Singleton instance
concept_detector = VisualConceptDetector()


def detect_concept(question: str, subject_hint: Optional[str] = None) -> ConceptDetectionResult:
    """
    Convenience function to detect concept from question
    
    Args:
        question: The student's question
        subject_hint: Optional subject hint
        
    Returns:
        ConceptDetectionResult
    """
    return concept_detector.detect(question, subject_hint)



