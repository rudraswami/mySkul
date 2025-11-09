"""
Visual Teaching Engine - Core Implementation
Transforms static diagrams into living, animated lessons
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
import re
import json
import uuid
from datetime import datetime
from .cultural_metaphor_library import get_culturally_relevant_metaphor

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class ConceptType(Enum):
    """Types of concepts that require different visual patterns"""
    COMPARISON = "comparison"          # A vs B
    TRANSFORMATION = "transformation"   # A → B
    PROCESS = "process"                # Step 1 → Step 2 → Step 3
    CAUSE_EFFECT = "cause_effect"      # If A then B
    HIERARCHY = "hierarchy"            # Parent → Children
    CYCLE = "cycle"                    # A → B → C → A
    RELATIONSHIP = "relationship"      # A ↔ B connections

class VisualPattern(Enum):
    """Universal visual patterns that work across subjects"""
    FLOW_DIAGRAM = "flow_diagram"
    SPLIT_SCREEN = "split_screen"
    TIMELINE = "timeline"
    ORBIT_SYSTEM = "orbit_system"
    BALANCE_SCALE = "balance_scale"
    TRANSFORMATION_MORPH = "transformation_morph"
    NETWORK_GRAPH = "network_graph"
    LAYERED_STACK = "layered_stack"

@dataclass
class TeachingIntent:
    """Parsed semantic understanding of what to teach"""
    concept_type: ConceptType
    subject_domain: str
    key_elements: List[str]
    complexity_level: str  # simple, medium, complex
    visual_pattern: VisualPattern
    cultural_metaphor: Optional[str] = None
    emphasis_points: List[str] = None
    common_mistakes: List[str] = None

@dataclass
class AnimationStage:
    """Single stage in the teaching animation"""
    stage_id: str
    duration_ms: int
    narration: str
    animations: List[Dict[str, Any]]
    interactions: Optional[List[Dict[str, Any]]] = None
    emphasis: Optional[str] = None

@dataclass
class TeachingVisual:
    """Complete visual teaching experience"""
    visual_id: str
    type: str  # animated_lesson, interactive_scene, etc.
    stages: List[AnimationStage]
    total_duration_ms: int
    interaction_points: List[int]  # Stage indices where interaction happens
    metadata: Dict[str, Any]

# ============================================================================
# SEMANTIC PARSER
# ============================================================================

class SemanticParser:
    """
    Understands the deep meaning and teaching intent of any question
    """

    def __init__(self):
        self.concept_patterns = {
            # Comparison patterns
            r"(?:difference|compare|versus|vs|between)\s+(\w+)\s+(?:and|vs|versus)\s+(\w+)": ConceptType.COMPARISON,
            r"(\w+)\s+vs\s+(\w+)": ConceptType.COMPARISON,

            # Transformation patterns
            r"(?:convert|change|transform)\s+(\w+)\s+(?:to|into)\s+(\w+)": ConceptType.TRANSFORMATION,
            r"(?:active|passive)\s+voice": ConceptType.TRANSFORMATION,

            # Process patterns
            r"(?:how|steps|process)\s+(?:to|of|for)\s+(\w+)": ConceptType.PROCESS,
            r"solve\s+(\w+)": ConceptType.PROCESS,

            # Cause-effect patterns
            r"(?:why|reason|cause|effect|result)": ConceptType.CAUSE_EFFECT,
            r"if\s+(\w+)\s+then\s+(\w+)": ConceptType.CAUSE_EFFECT,

            # Hierarchy patterns
            r"(?:types|categories|classification)\s+of\s+(\w+)": ConceptType.HIERARCHY,

            # Cycle patterns
            r"(?:cycle|circular|recurring)": ConceptType.CYCLE,

            # Relationship patterns
            r"(?:relationship|connection|link)\s+between": ConceptType.RELATIONSHIP,
        }

        self.subject_indicators = {
            'mathematics': ['equation', 'solve', 'calculate', 'formula', 'algebra', 'geometry'],
            'physics': ['force', 'motion', 'energy', 'wave', 'velocity', 'acceleration'],
            'chemistry': ['atom', 'molecule', 'bond', 'reaction', 'element', 'compound'],
            'biology': ['cell', 'organism', 'evolution', 'dna', 'ecosystem', 'photosynthesis'],
            'grammar': ['voice', 'tense', 'noun', 'verb', 'sentence', 'clause'],
            'history': ['event', 'period', 'civilization', 'war', 'revolution', 'empire'],
            'geography': ['map', 'climate', 'terrain', 'country', 'continent', 'ocean']
        }

    def parse(self, question: str, subject: Optional[str] = None) -> TeachingIntent:
        """
        Parse a question to understand its teaching intent
        """
        question_lower = question.lower()

        # Detect concept type
        concept_type = self._detect_concept_type(question_lower)

        # Detect subject if not provided
        if not subject:
            subject = self._detect_subject(question_lower)

        # Extract key elements
        key_elements = self._extract_key_elements(question_lower, concept_type)

        # Determine complexity
        complexity = self._assess_complexity(question_lower, key_elements)

        # Map to visual pattern
        visual_pattern = self._map_to_visual_pattern(concept_type, subject)

        # Get cultural metaphor
        cultural_metaphor = self._get_cultural_metaphor(concept_type, subject)

        # Extract emphasis points
        emphasis_points = self._extract_emphasis_points(question_lower)

        return TeachingIntent(
            concept_type=concept_type,
            subject_domain=subject,
            key_elements=key_elements,
            complexity_level=complexity,
            visual_pattern=visual_pattern,
            cultural_metaphor=cultural_metaphor,
            emphasis_points=emphasis_points,
            common_mistakes=self._get_common_mistakes(concept_type, subject)
        )

    def _detect_concept_type(self, question: str) -> ConceptType:
        """Detect the type of concept being asked about"""
        for pattern, concept_type in self.concept_patterns.items():
            if re.search(pattern, question):
                return concept_type
        return ConceptType.PROCESS  # Default

    def _detect_subject(self, question: str) -> str:
        """Detect subject domain from question content"""
        max_score = 0
        detected_subject = 'general'

        for subject, keywords in self.subject_indicators.items():
            score = sum(1 for keyword in keywords if keyword in question)
            if score > max_score:
                max_score = score
                detected_subject = subject

        return detected_subject

    def _extract_key_elements(self, question: str, concept_type: ConceptType) -> List[str]:
        """Extract the main elements to be visualized"""
        elements = []

        if concept_type == ConceptType.COMPARISON:
            # Extract items being compared
            match = re.search(r"between\s+(\w+)\s+and\s+(\w+)", question)
            if match:
                elements = [match.group(1), match.group(2)]
            else:
                # Try to extract from "X vs Y" pattern
                match = re.search(r"(\w+)\s+vs\s+(\w+)", question)
                if match:
                    elements = [match.group(1), match.group(2)]

        elif concept_type == ConceptType.TRANSFORMATION:
            # Extract before and after states
            if 'active' in question and 'passive' in question:
                elements = ['active_voice', 'passive_voice']
            else:
                match = re.search(r"(\w+)\s+to\s+(\w+)", question)
                if match:
                    elements = [match.group(1), match.group(2)]

        # Default: extract significant nouns
        if not elements:
            # Simple noun extraction
            words = question.split()
            elements = [w for w in words if len(w) > 4 and not w in ['what', 'where', 'when', 'which', 'how']][:3]

        return elements

    def _assess_complexity(self, question: str, elements: List[str]) -> str:
        """Assess the complexity level of the concept"""
        word_count = len(question.split())
        element_count = len(elements)

        if word_count < 10 and element_count <= 2:
            return 'simple'
        elif word_count < 20 and element_count <= 4:
            return 'medium'
        else:
            return 'complex'

    def _map_to_visual_pattern(self, concept_type: ConceptType, subject: str) -> VisualPattern:
        """Map concept type and subject to best visual pattern"""
        pattern_map = {
            ConceptType.COMPARISON: VisualPattern.SPLIT_SCREEN,
            ConceptType.TRANSFORMATION: VisualPattern.TRANSFORMATION_MORPH,
            ConceptType.PROCESS: VisualPattern.FLOW_DIAGRAM,
            ConceptType.CAUSE_EFFECT: VisualPattern.FLOW_DIAGRAM,
            ConceptType.HIERARCHY: VisualPattern.LAYERED_STACK,
            ConceptType.CYCLE: VisualPattern.ORBIT_SYSTEM,
            ConceptType.RELATIONSHIP: VisualPattern.NETWORK_GRAPH
        }

        # Subject-specific overrides
        if subject == 'chemistry' and concept_type == ConceptType.TRANSFORMATION:
            return VisualPattern.FLOW_DIAGRAM  # For chemical reactions
        elif subject == 'physics' and concept_type == ConceptType.RELATIONSHIP:
            return VisualPattern.BALANCE_SCALE  # For force relationships

        return pattern_map.get(concept_type, VisualPattern.FLOW_DIAGRAM)

    def _get_cultural_metaphor(self, concept_type: ConceptType, subject: str) -> str:
        """Get culturally relevant metaphor for Indian students"""
        metaphors = {
            ('grammar', ConceptType.TRANSFORMATION): 'cricket_batting',
            ('physics', ConceptType.CAUSE_EFFECT): 'train_momentum',
            ('chemistry', ConceptType.TRANSFORMATION): 'cooking_process',
            ('mathematics', ConceptType.PROCESS): 'rangoli_pattern',
            ('biology', ConceptType.CYCLE): 'season_cycle',
            ('history', ConceptType.TIMELINE): 'festival_calendar'
        }

        return metaphors.get((subject, concept_type), 'daily_life')

    def _extract_emphasis_points(self, question: str) -> List[str]:
        """Extract points that need emphasis in teaching"""
        emphasis_keywords = ['important', 'key', 'main', 'crucial', 'remember', 'note']
        points = []

        for keyword in emphasis_keywords:
            if keyword in question:
                points.append(f"Focus on {keyword} concepts")

        return points

    def _get_common_mistakes(self, concept_type: ConceptType, subject: str) -> List[str]:
        """Get common mistakes students make for this concept"""
        mistakes_db = {
            ('grammar', ConceptType.TRANSFORMATION): [
                "Forgetting 'by' in passive voice",
                "Wrong tense conversion",
                "Missing auxiliary verbs"
            ],
            ('mathematics', ConceptType.PROCESS): [
                "Sign errors",
                "Order of operations",
                "Forgetting to check answer"
            ],
            ('physics', ConceptType.CAUSE_EFFECT): [
                "Confusing force and momentum",
                "Wrong direction of vectors",
                "Unit conversion errors"
            ]
        }

        return mistakes_db.get((subject, concept_type), ["Check your work carefully"])

# ============================================================================
# SCENE GENERATOR
# ============================================================================

class SceneGenerator:
    """
    Generates animated teaching scenes based on visual patterns
    """

    def __init__(self):
        self.animation_templates = self._load_animation_templates()

    def _load_animation_templates(self) -> Dict:
        """Load animation templates for different patterns"""
        return {
            VisualPattern.SPLIT_SCREEN: self._generate_split_screen,
            VisualPattern.TRANSFORMATION_MORPH: self._generate_transformation,
            VisualPattern.FLOW_DIAGRAM: self._generate_flow_diagram,
            VisualPattern.TIMELINE: self._generate_timeline,
            VisualPattern.ORBIT_SYSTEM: self._generate_orbit,
            VisualPattern.BALANCE_SCALE: self._generate_balance,
            VisualPattern.NETWORK_GRAPH: self._generate_network,
            VisualPattern.LAYERED_STACK: self._generate_layers
        }

    def create_scene(self, intent: TeachingIntent) -> List[AnimationStage]:
        """
        Create a complete animated teaching scene with cultural relevance
        """
        # Get cultural metaphor for the concept
        cultural_metaphor = get_culturally_relevant_metaphor(
            concept=' '.join(intent.key_elements[:2]) if intent.key_elements else "concept",
            subject=intent.subject_domain,
            preferred_category=intent.cultural_metaphor
        )

        # Store cultural context in intent
        intent.cultural_metaphor = cultural_metaphor

        # Get appropriate generator for the visual pattern
        generator = self.animation_templates.get(
            intent.visual_pattern,
            self._generate_flow_diagram  # Default
        )

        # Generate stages with cultural context
        stages = generator(intent)

        # Enhance with cultural metaphor animations
        if cultural_metaphor:
            stages = self._add_cultural_layer(stages, cultural_metaphor)

        # Add emphasis animations
        if intent.emphasis_points:
            stages = self._add_emphasis(stages, intent.emphasis_points)

        return stages

    def _generate_split_screen(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate split-screen comparison animation"""
        stages = []

        # Stage 1: Setup
        stages.append(AnimationStage(
            stage_id="setup",
            duration_ms=2000,
            narration=f"Let's compare {intent.key_elements[0]} and {intent.key_elements[1]}",
            animations=[
                {
                    "type": "split_screen_create",
                    "left_label": intent.key_elements[0],
                    "right_label": intent.key_elements[1],
                    "animation": "slide_in"
                }
            ]
        ))

        # Stage 2: Left side details
        stages.append(AnimationStage(
            stage_id="left_detail",
            duration_ms=3000,
            narration=f"First, let's look at {intent.key_elements[0]}",
            animations=[
                {
                    "type": "highlight",
                    "target": "left_panel",
                    "effect": "glow"
                },
                {
                    "type": "add_points",
                    "panel": "left",
                    "points": self._get_comparison_points(intent.key_elements[0], intent.subject_domain)
                }
            ],
            interactions=[{"type": "tap_to_continue"}]
        ))

        # Stage 3: Right side details
        stages.append(AnimationStage(
            stage_id="right_detail",
            duration_ms=3000,
            narration=f"Now, let's examine {intent.key_elements[1]}",
            animations=[
                {
                    "type": "highlight",
                    "target": "right_panel",
                    "effect": "glow"
                },
                {
                    "type": "add_points",
                    "panel": "right",
                    "points": self._get_comparison_points(intent.key_elements[1], intent.subject_domain)
                }
            ],
            interactions=[{"type": "tap_to_continue"}]
        ))

        # Stage 4: Key differences
        stages.append(AnimationStage(
            stage_id="differences",
            duration_ms=3000,
            narration="The key differences are highlighted",
            animations=[
                {
                    "type": "connect_differences",
                    "style": "curved_arrows",
                    "color": "#f59e0b"
                }
            ],
            emphasis="Notice the contrasting elements"
        ))

        return stages

    def _generate_transformation(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate transformation/morphing animation"""
        stages = []

        # For active/passive voice example
        if 'voice' in str(intent.key_elements):
            stages.extend(self._generate_voice_transformation(intent))
        else:
            # Generic transformation
            stages.append(AnimationStage(
                stage_id="initial_state",
                duration_ms=2000,
                narration=f"We start with {intent.key_elements[0]}",
                animations=[
                    {
                        "type": "create_element",
                        "element": intent.key_elements[0],
                        "position": "center",
                        "animation": "fade_in"
                    }
                ]
            ))

            stages.append(AnimationStage(
                stage_id="transform",
                duration_ms=3000,
                narration=f"Watch as it transforms into {intent.key_elements[1]}",
                animations=[
                    {
                        "type": "morph",
                        "from": intent.key_elements[0],
                        "to": intent.key_elements[1],
                        "duration": 2000,
                        "effect": "smooth_morph"
                    }
                ],
                interactions=[{"type": "slider", "controls": "transformation_progress"}]
            ))

        return stages

    def _generate_voice_transformation(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Special transformation for active/passive voice"""
        return [
            AnimationStage(
                stage_id="active_setup",
                duration_ms=3000,
                narration="In active voice, the subject performs the action",
                animations=[
                    {
                        "type": "create_sentence",
                        "structure": ["Kohli", "hits", "the ball"],
                        "labels": ["Subject", "Verb", "Object"],
                        "style": "blocks"
                    },
                    {
                        "type": "arrow",
                        "from": "Subject",
                        "to": "Object",
                        "label": "action",
                        "color": "#10b981"
                    }
                ]
            ),
            AnimationStage(
                stage_id="transformation",
                duration_ms=4000,
                narration="Now watch the magical transformation to passive voice",
                animations=[
                    {
                        "type": "rotate_scene",
                        "degrees": 180,
                        "duration": 1000
                    },
                    {
                        "type": "rearrange_blocks",
                        "new_order": ["The ball", "was hit", "by Kohli"],
                        "new_labels": ["Subject", "Verb", "Agent"],
                        "animation": "slide_and_swap"
                    }
                ],
                emphasis="Notice how the object becomes the subject"
            ),
            AnimationStage(
                stage_id="passive_result",
                duration_ms=3000,
                narration="In passive voice, the subject receives the action",
                animations=[
                    {
                        "type": "arrow",
                        "from": "Agent",
                        "to": "Subject",
                        "label": "action",
                        "color": "#f59e0b",
                        "reverse": True
                    }
                ],
                interactions=[
                    {
                        "type": "quiz",
                        "question": "Which voice emphasizes the doer?",
                        "options": ["Active", "Passive"],
                        "correct": 0
                    }
                ]
            )
        ]

    def _generate_flow_diagram(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate flow diagram animation"""
        # Implementation for flow diagrams
        return []

    def _generate_timeline(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate timeline animation"""
        # Implementation for timelines
        return []

    def _generate_orbit(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate orbit system animation"""
        # Implementation for orbit systems
        return []

    def _generate_balance(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate balance scale animation"""
        # Implementation for balance scales
        return []

    def _generate_network(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate network graph animation"""
        # Implementation for network graphs
        return []

    def _generate_layers(self, intent: TeachingIntent) -> List[AnimationStage]:
        """Generate layered stack animation"""
        # Implementation for layered stacks
        return []

    def _add_cultural_layer(self, stages: List[AnimationStage], metaphor: Dict[str, Any]) -> List[AnimationStage]:
        """Add cultural metaphor elements to stages"""

        # Extract visual elements and animations from metaphor
        visual_elements = metaphor.get("visual_elements", [])
        animation_sequence = metaphor.get("animation_sequence", [])
        visual_style = metaphor.get("visual_style", {})

        # Apply cultural animations to stages
        for i, stage in enumerate(stages):
            # Add cultural visual elements
            if i < len(animation_sequence):
                cultural_anim = animation_sequence[i]
                stage.animations.append({
                    "type": "cultural_element",
                    "animation": cultural_anim,
                    "style": visual_style,
                    "elements": visual_elements
                })

            # Add cultural narration context if applicable
            if metaphor.get("template"):
                # Enhance narration with cultural context
                stage.narration = f"{stage.narration} - {metaphor['category'].title()} style"

        # Add micro-interactions from cultural metaphor
        interactions = metaphor.get("interactions", [])
        for i, interaction in enumerate(interactions):
            if i < len(stages):
                if stages[i].interactions is None:
                    stages[i].interactions = []
                stages[i].interactions.append(interaction)

        return stages

    def _add_emphasis(self, stages: List[AnimationStage], emphasis_points: List[str]) -> List[AnimationStage]:
        """Add emphasis animations to important points"""
        for stage in stages:
            if any(point in stage.narration for point in emphasis_points):
                stage.animations.append({
                    "type": "emphasis",
                    "effect": "pulse_glow",
                    "color": "#fbbf24"
                })
        return stages

    def _get_comparison_points(self, element: str, subject: str) -> List[str]:
        """Get comparison points for an element"""
        # This would be expanded with subject-specific knowledge
        return [
            f"Key feature 1 of {element}",
            f"Key feature 2 of {element}",
            f"Key feature 3 of {element}"
        ]

# ============================================================================
# MAIN ENGINE
# ============================================================================

class VisualTeachingEngine:
    """
    Main orchestrator for the Visual Teaching Engine
    """

    def __init__(self):
        self.parser = SemanticParser()
        self.scene_generator = SceneGenerator()

    async def generate_teaching_visual(
        self,
        question: str,
        subject: Optional[str] = None,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> TeachingVisual:
        """
        Generate a complete animated teaching visual for any question
        """
        # Parse the question to understand intent
        intent = self.parser.parse(question, subject)

        # Generate animation stages
        stages = self.scene_generator.create_scene(intent)

        # Calculate total duration and interaction points
        total_duration = sum(stage.duration_ms for stage in stages)
        interaction_points = [
            i for i, stage in enumerate(stages)
            if stage.interactions
        ]

        # Create the teaching visual
        visual = TeachingVisual(
            visual_id=f"teach_{hash(question) % 1000000}",
            type="animated_lesson",
            stages=stages,
            total_duration_ms=total_duration,
            interaction_points=interaction_points,
            metadata={
                "intent": intent.__dict__,
                "question": question,
                "subject": subject or intent.subject_domain,
                "complexity": intent.complexity_level,
                "pattern": intent.visual_pattern.value
            }
        )

        return visual

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_teaching_animation(question: str, subject: str = None) -> Dict[str, Any]:
    """
    Main entry point for generating teaching animations
    """
    import asyncio

    engine = VisualTeachingEngine()
    visual = asyncio.run(engine.generate_teaching_visual(question, subject))

    # Convert to dict for JSON serialization
    return {
        'visual_id': visual.visual_id,
        'type': visual.type,
        'stages': [
            {
                'id': stage.stage_id,
                'duration': stage.duration_ms,
                'narration': stage.narration,
                'animations': stage.animations,
                'interactions': stage.interactions,
                'emphasis': stage.emphasis
            }
            for stage in visual.stages
        ],
        'total_duration': visual.total_duration_ms,
        'interaction_points': visual.interaction_points,
        'metadata': visual.metadata
    }