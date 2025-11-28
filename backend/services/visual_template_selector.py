"""
visual_template_selector.py
Phase 6: Template selection and TOON generation for visuals

Selects appropriate visual templates and generates TOON blocks
for the frontend visual engine.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .visual_concept_detector import (
    ConceptDetectionResult, 
    ConceptType, 
    VisualType,
    detect_concept
)


@dataclass
class TOONBlock:
    """TOON (Teaching Object Oriented Notation) block for visual generation"""
    topic: str
    topic_hi: str  # Hindi translation
    scene: str
    actors: List[Dict]
    props: List[Dict]
    animations: List[Dict]
    labels: List[Dict]
    steps: List[Dict]
    formulas: List[str]
    analogy: str
    analogy_hi: str
    interactions: List[Dict]
    layers: List[Dict]
    exam_mode: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# Template families for different concept types
TEMPLATE_FAMILIES = {
    ConceptType.MOTION: {
        "scene": "cricket_pitch",
        "default_props": ["cricket_ball_detailed", "bat", "stumps"],
        "professor_gestures": ["point", "explain", "celebrate"],
        "animation_style": "trajectory",
        "indian_theme": "cricket",
    },
    
    ConceptType.OPTICS: {
        "scene": "lab",
        "default_props": ["lens_convex", "prism", "bulb"],
        "professor_gestures": ["point", "explain"],
        "animation_style": "ray_trace",
        "indian_theme": "classroom",
    },
    
    ConceptType.ELECTRICITY: {
        "scene": "lab",
        "default_props": ["battery", "bulb", "resistor"],
        "professor_gestures": ["point", "explain", "think"],
        "animation_style": "flow",
        "indian_theme": "home",
    },
    
    ConceptType.CHEMISTRY_REACTION: {
        "scene": "lab",
        "default_props": ["test_tube", "beaker", "bunsen_burner"],
        "professor_gestures": ["explain", "surprise", "celebrate"],
        "animation_style": "reaction",
        "indian_theme": "kitchen",
    },
    
    ConceptType.BIOLOGY_PROCESS: {
        "scene": "nature",
        "default_props": ["leaf", "oxygen_bubble", "cell"],
        "professor_gestures": ["explain", "point"],
        "animation_style": "process_flow",
        "indian_theme": "garden",
    },
    
    ConceptType.GENETICS: {
        "scene": "lab",
        "default_props": ["dna_helix", "chromosome", "cell"],
        "professor_gestures": ["explain", "think"],
        "animation_style": "3d_rotate",
        "indian_theme": "classroom",
    },
    
    ConceptType.ALGEBRA: {
        "scene": "classroom",
        "default_props": ["axes", "parabola"],
        "professor_gestures": ["point", "explain", "encourage"],
        "animation_style": "graph_draw",
        "indian_theme": "classroom",
    },
    
    ConceptType.GEOMETRY: {
        "scene": "classroom",
        "default_props": ["right_triangle", "circle_with_radius", "axes"],
        "professor_gestures": ["point", "explain"],
        "animation_style": "construct",
        "indian_theme": "classroom",
    },
    
    ConceptType.TRIGONOMETRY: {
        "scene": "classroom",
        "default_props": ["right_triangle", "unit_circle"],
        "professor_gestures": ["point", "explain"],
        "animation_style": "rotate",
        "indian_theme": "classroom",
    },
    
    ConceptType.CALCULUS: {
        "scene": "classroom",
        "default_props": ["axes", "curve", "tangent_line"],
        "professor_gestures": ["explain", "think", "celebrate"],
        "animation_style": "graph_draw",
        "indian_theme": "classroom",
    },
    
    ConceptType.STATISTICS: {
        "scene": "classroom",
        "default_props": ["bar_chart", "histogram"],
        "professor_gestures": ["point", "explain"],
        "animation_style": "chart_grow",
        "indian_theme": "market",
    },
}

# Scene backgrounds
SCENE_BACKGROUNDS = {
    "cricket_pitch": {
        "type": "outdoor",
        "gradient": ["#4FC3F7", "#E1F5FE"],
        "ground": "#66BB6A",
        "elements": ["sun", "clouds", "pitch_markings"],
    },
    "lab": {
        "type": "indoor",
        "gradient": ["#ECEFF1", "#CFD8DC"],
        "elements": ["table", "shelf", "equipment"],
    },
    "classroom": {
        "type": "indoor",
        "gradient": ["#FFF8E1", "#FFECB3"],
        "elements": ["blackboard", "desk", "chart"],
    },
    "nature": {
        "type": "outdoor",
        "gradient": ["#81D4FA", "#B3E5FC"],
        "ground": "#A5D6A7",
        "elements": ["trees", "sun", "grass"],
    },
    "home": {
        "type": "indoor",
        "gradient": ["#FFF3E0", "#FFE0B2"],
        "elements": ["window", "furniture"],
    },
}

# Hindi translations for common concepts
HINDI_TRANSLATIONS = {
    "force": "बल",
    "motion": "गति",
    "gravity": "गुरुत्वाकर्षण",
    "velocity": "वेग",
    "acceleration": "त्वरण",
    "momentum": "संवेग",
    "energy": "ऊर्जा",
    "light": "प्रकाश",
    "reflection": "परावर्तन",
    "refraction": "अपवर्तन",
    "electricity": "विद्युत",
    "current": "धारा",
    "atom": "परमाणु",
    "cell": "कोशिका",
    "photosynthesis": "प्रकाश संश्लेषण",
    "equation": "समीकरण",
    "triangle": "त्रिभुज",
    "circle": "वृत्त",
}

# Analogies for concepts
CONCEPT_ANALOGIES = {
    "force": {
        "en": "Like a bowler pushing the ball - more force means faster ball!",
        "hi": "जैसे गेंदबाज़ गेंद को धकेलता है - ज़्यादा बल = तेज़ गेंद!",
    },
    "gravity": {
        "en": "Like a mango falling from tree - Earth pulls everything down!",
        "hi": "जैसे आम पेड़ से गिरता है - धरती सबको खींचती है!",
    },
    "motion": {
        "en": "Like an auto rickshaw moving on road - distance over time!",
        "hi": "जैसे ऑटो सड़क पर चलता है - दूरी बटा समय!",
    },
    "photosynthesis": {
        "en": "Like a plant's kitchen - sunlight is the stove, CO₂ is ingredient!",
        "hi": "जैसे पौधे की रसोई - सूरज चूल्हा है, CO₂ मसाला है!",
    },
    "atom": {
        "en": "Like a tiny solar system - nucleus is sun, electrons are planets!",
        "hi": "जैसे छोटा सौर मंडल - नाभिक सूर्य है, इलेक्ट्रॉन ग्रह हैं!",
    },
    "quadratic": {
        "en": "Like a ball thrown up - goes up, comes down in a curve!",
        "hi": "जैसे गेंद ऊपर फेंको - ऊपर जाती है, नीचे आती है!",
    },
}


class VisualTemplateSelector:
    """Selects and generates visual templates based on detected concepts"""
    
    def __init__(self):
        self.template_families = TEMPLATE_FAMILIES
        self.scene_backgrounds = SCENE_BACKGROUNDS
        self.translations = HINDI_TRANSLATIONS
        self.analogies = CONCEPT_ANALOGIES
    
    def generate_toon(
        self, 
        question: str, 
        subject_hint: Optional[str] = None,
        student_profile: Optional[Dict] = None
    ) -> TOONBlock:
        """
        Generate a complete TOON block for visual rendering
        
        Args:
            question: Student's question
            subject_hint: Optional subject hint
            student_profile: Optional student profile for personalization
            
        Returns:
            TOONBlock ready for frontend rendering
        """
        # Detect concept
        detection = detect_concept(question, subject_hint)
        
        # Get template family
        template = self.template_families.get(
            detection.concept_type, 
            self.template_families[ConceptType.MOTION]
        )
        
        # Build TOON block
        toon = TOONBlock(
            topic=self._format_topic(detection.concept_name),
            topic_hi=self.translations.get(detection.concept_name, detection.concept_name),
            scene=template["scene"],
            actors=self._generate_actors(template),
            props=self._generate_props(detection, template, student_profile),
            animations=self._generate_animations(detection, template),
            labels=self._generate_labels(detection),
            steps=self._generate_steps(detection),
            formulas=detection.formulas,
            analogy=self._get_analogy(detection.concept_name, "en"),
            analogy_hi=self._get_analogy(detection.concept_name, "hi"),
            interactions=self._generate_interactions(detection),
            layers=self._generate_layers(detection),
            exam_mode=self._generate_exam_mode(detection),
        )
        
        return toon
    
    def _format_topic(self, concept_name: str) -> str:
        """Format concept name as readable topic"""
        return concept_name.replace("_", " ").title()
    
    def _generate_actors(self, template: Dict) -> List[Dict]:
        """Generate actor configurations (professor, etc.)"""
        return [
            {
                "id": "professor",
                "type": "professor",
                "position": {"x": 0.1, "y": 0.5},
                "gestures": template["professor_gestures"],
                "initial_gesture": "explain",
            }
        ]
    
    def _generate_props(
        self, 
        detection: ConceptDetectionResult, 
        template: Dict,
        student_profile: Optional[Dict]
    ) -> List[Dict]:
        """Generate prop configurations"""
        props = []
        
        # Add detected objects
        for i, obj in enumerate(detection.objects[:4]):  # Limit to 4 props
            props.append({
                "id": f"prop_{i}",
                "type": obj,
                "position": {"x": 0.3 + i * 0.15, "y": 0.5},
                "size": "medium",
                "interactive": True,
            })
        
        # Add Indian context prop if available
        if detection.indian_context:
            props.append({
                "id": "indian_context",
                "type": detection.indian_context,
                "position": {"x": 0.8, "y": 0.6},
                "size": "small",
                "interactive": False,
            })
        
        return props
    
    def _generate_animations(
        self, 
        detection: ConceptDetectionResult, 
        template: Dict
    ) -> List[Dict]:
        """Generate animation configurations"""
        animations = []
        
        for i, anim_type in enumerate(detection.animations[:3]):
            animations.append({
                "id": f"anim_{i}",
                "target": f"prop_{min(i, len(detection.objects) - 1)}",
                "type": anim_type,
                "trigger": "auto" if i == 0 else "step",
                "duration": 1000 + i * 500,
                "easing": "easeOut",
            })
        
        return animations
    
    def _generate_labels(self, detection: ConceptDetectionResult) -> List[Dict]:
        """Generate label configurations"""
        labels = []
        
        # Add formula labels
        for i, formula in enumerate(detection.formulas[:2]):
            labels.append({
                "id": f"formula_{i}",
                "type": "formula",
                "text": formula,
                "position": {"x": 0.7, "y": 0.1 + i * 0.1},
                "style": "highlight",
            })
        
        # Add concept label
        labels.append({
            "id": "concept_label",
            "type": "title",
            "text": self._format_topic(detection.concept_name),
            "text_hi": self.translations.get(detection.concept_name, ""),
            "position": {"x": 0.5, "y": 0.05},
            "style": "title",
        })
        
        return labels
    
    def _generate_steps(self, detection: ConceptDetectionResult) -> List[Dict]:
        """Generate step-by-step progression"""
        steps = [
            {
                "id": "step_1",
                "title": "Observe",
                "title_hi": "देखो",
                "description": "Watch the concept in action",
                "animations": ["anim_0"],
                "duration": 2000,
            },
            {
                "id": "step_2",
                "title": "Understand",
                "title_hi": "समझो",
                "description": "See the formula applied",
                "animations": ["anim_1"] if len(detection.animations) > 1 else [],
                "duration": 2000,
                "show_formula": True,
            },
            {
                "id": "step_3",
                "title": "Interact",
                "title_hi": "प्रयोग करो",
                "description": "Try changing values",
                "enable_sliders": True,
                "duration": 0,  # User-controlled
            },
        ]
        
        return steps
    
    def _generate_interactions(self, detection: ConceptDetectionResult) -> List[Dict]:
        """Generate interaction configurations"""
        interactions = []
        
        for interaction_type in detection.interactions:
            if interaction_type == "slider":
                interactions.append({
                    "type": "slider",
                    "variables": self._get_slider_variables(detection),
                })
            elif interaction_type == "tap":
                interactions.append({
                    "type": "tap",
                    "targets": [f"prop_{i}" for i in range(len(detection.objects))],
                    "action": "highlight",
                })
            elif interaction_type == "drag":
                interactions.append({
                    "type": "drag",
                    "targets": ["prop_0"],
                    "constraints": {"axis": "x"},
                })
        
        return interactions
    
    def _get_slider_variables(self, detection: ConceptDetectionResult) -> List[Dict]:
        """Get slider variable configurations based on concept"""
        variable_configs = {
            "force": [
                {"name": "force", "label": "Force (N)", "min": 5, "max": 50, "default": 15},
                {"name": "mass", "label": "Mass (kg)", "min": 0.1, "max": 5, "default": 1},
            ],
            "motion": [
                {"name": "velocity", "label": "Velocity (m/s)", "min": 0, "max": 100, "default": 20},
                {"name": "time", "label": "Time (s)", "min": 0, "max": 10, "default": 2},
            ],
            "gravity": [
                {"name": "mass", "label": "Mass (kg)", "min": 0.1, "max": 10, "default": 1},
                {"name": "height", "label": "Height (m)", "min": 1, "max": 50, "default": 10},
            ],
            "electricity": [
                {"name": "voltage", "label": "Voltage (V)", "min": 1, "max": 12, "default": 6},
                {"name": "resistance", "label": "Resistance (Ω)", "min": 1, "max": 100, "default": 10},
            ],
        }
        
        return variable_configs.get(detection.concept_name, [
            {"name": "value", "label": "Value", "min": 0, "max": 100, "default": 50}
        ])
    
    def _generate_layers(self, detection: ConceptDetectionResult) -> List[Dict]:
        """Generate layer configurations for progressive reveal"""
        return [
            {
                "id": "basic",
                "name": "Basic",
                "description": "Concept understanding",
                "elements": ["props", "basic_labels"],
                "unlocked": True,
            },
            {
                "id": "formula",
                "name": "Formula",
                "description": "Mathematical representation",
                "elements": ["formulas", "calculations"],
                "unlocked": False,
                "unlock_condition": "view_basic",
            },
            {
                "id": "mechanics",
                "name": "Deep Dive",
                "description": "Vectors and graphs",
                "elements": ["vectors", "graphs"],
                "unlocked": False,
                "unlock_condition": "interact_formula",
            },
            {
                "id": "exam",
                "name": "Exam Mode",
                "description": "Test yourself",
                "elements": ["questions", "hints"],
                "unlocked": False,
                "unlock_condition": "complete_mechanics",
            },
        ]
    
    def _generate_exam_mode(self, detection: ConceptDetectionResult) -> Dict:
        """Generate exam mode questions"""
        # Basic question template
        return {
            "enabled": True,
            "questions": [
                {
                    "question": f"What is the formula for {detection.concept_name}?",
                    "options": detection.formulas[:4] if len(detection.formulas) >= 4 else 
                              detection.formulas + ["None of the above"] * (4 - len(detection.formulas)),
                    "correct": 0,
                    "explanation": f"The correct formula is {detection.formulas[0] if detection.formulas else 'N/A'}",
                }
            ],
            "xp_reward": 10,
        }
    
    def _get_analogy(self, concept_name: str, lang: str) -> str:
        """Get analogy for concept in specified language"""
        analogies = self.analogies.get(concept_name, {})
        return analogies.get(lang, f"Understanding {concept_name} through real-world examples")


# Singleton instance
template_selector = VisualTemplateSelector()


def generate_visual_toon(
    question: str, 
    subject_hint: Optional[str] = None,
    student_profile: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to generate TOON block
    
    Args:
        question: Student's question
        subject_hint: Optional subject hint
        student_profile: Optional student profile
        
    Returns:
        TOON block as dictionary
    """
    toon = template_selector.generate_toon(question, subject_hint, student_profile)
    return toon.to_dict()



