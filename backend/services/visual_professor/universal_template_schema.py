"""
Universal Visual Professor Template Schema
Auto-generates professor-led, multi-step, Lottie-based templates for ANY concept
Works universally across all subjects without manual template entries
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VisualType(str, Enum):
    """Types of visual content"""
    PROFESSOR_LED = "professor_led"  # Multi-step professor teaching with Lottie
    ANIMATION = "animation"  # Lottie animation
    INTERACTIVE = "interactive"  # Interactive with scrubbing


@dataclass
class LottieAsset:
    """Lottie animation asset configuration"""
    url: str
    loop: bool = True
    autoplay: bool = True
    speed: float = 1.0
    stage_index: int = 0  # Which stage this Lottie belongs to


@dataclass
class ProfessorAvatar:
    """Professor avatar configuration"""
    expression: str  # thinking, explaining, pointing, encouraging
    position: str = "bottom_right"  # bottom_right, top_left, center
    animation: str = "wave"  # wave, point, explain, think
    visible_stages: List[int] = None  # Which stages to show avatar


@dataclass
class InteractionPoint:
    """Interactive element in the visual"""
    type: str  # scrub, hover, click, tap
    target: str  # Element ID or area
    description: str
    stage_index: int
    trigger: str = "auto"  # auto, manual


@dataclass
class VisualStage:
    """Single stage in professor-led lesson"""
    stage_id: str
    duration_ms: int
    narration: str
    narration_style: str = "professor"  # professor, mentor, supervisor
    lottie_assets: List[LottieAsset] = None
    blocks: List[Dict[str, Any]] = None  # Visual blocks (nodes, arrows, equations, etc.)
    interactions: List[InteractionPoint] = None
    highlights: List[Dict[str, Any]] = None  # Elements to highlight
    transitions: Dict[str, Any] = None  # Transition effects
    emphasis: Optional[str] = None


@dataclass
class UniversalProfessorTemplate:
    """Universal template that works for ANY concept"""
    # Required fields (no defaults) must come first
    template_id: str  # Auto-generated from concept
    concept: str
    subject: str
    intent: str
    stages: List[VisualStage]
    professor_avatar: ProfessorAvatar
    total_duration_ms: int
    interaction_points: List[int]  # Stage indices with interactions
    metadata: Dict[str, Any]
    # Optional fields (with defaults) must come last
    visual_type: VisualType = VisualType.PROFESSOR_LED
    lottie_base_url: str = "https://cdn.ai-tutor.in/visuals"  # Base URL for Lottie assets
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "visual_type": self.visual_type.value,
            "template_id": self.template_id,
            "concept": self.concept,
            "subject": self.subject,
            "intent": self.intent,
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "duration_ms": stage.duration_ms,
                    "narration": stage.narration,
                    "narration_style": stage.narration_style,
                    "lottie_assets": [
                        {
                            "url": asset.url,
                            "loop": asset.loop,
                            "autoplay": asset.autoplay,
                            "speed": asset.speed,
                            "stage_index": asset.stage_index
                        } for asset in (stage.lottie_assets or [])
                    ],
                    "blocks": stage.blocks or [],
                    "interactions": [
                        {
                            "type": inter.type,
                            "target": inter.target,
                            "description": inter.description,
                            "stage_index": inter.stage_index,
                            "trigger": inter.trigger
                        } for inter in (stage.interactions or [])
                    ],
                    "highlights": stage.highlights or [],
                    "transitions": stage.transitions or {},
                    "emphasis": stage.emphasis
                } for stage in self.stages
            ],
            "professor_avatar": {
                "expression": self.professor_avatar.expression,
                "position": self.professor_avatar.position,
                "animation": self.professor_avatar.animation,
                "visible_stages": self.professor_avatar.visible_stages or list(range(len(self.stages)))
            },
            "total_duration_ms": self.total_duration_ms,
            "interaction_points": self.interaction_points,
            "metadata": self.metadata,
            "lottie_base_url": self.lottie_base_url
        }


class UniversalTemplateGenerator:
    """
    Generates universal professor-led templates for ANY concept
    No manual template entries required
    Integrates with concept library, scene builder, and animation builder
    """
    
    def __init__(self, student_profile: Optional[Dict[str, Any]] = None):
        self.lottie_base_url = "https://cdn.ai-tutor.in/lottie"
        self.professor_avatar_base = "https://cdn.ai-tutor.in/visuals/professor"
        self.student_profile = student_profile  # Store for metaphor selection
        
        # Import systems (done here to avoid circular imports)
        try:
            from .concept_library import get_concept_content, has_concept_content
            from .lottie_asset_manager import LottieAssetManager
            self.concept_library = {'get': get_concept_content, 'has': has_concept_content}
            self.lottie_manager = LottieAssetManager()
        except ImportError as e:
            import logging
            logging.warning(f"Could not import concept library or lottie manager: {e}")
            self.concept_library = None
            self.lottie_manager = None
    
    def generate_template(
        self,
        concept: str,
        subject: str,
        intent: str,
        concept_type: str,
        key_elements: List[str],
        complexity: str = "medium"
    ) -> UniversalProfessorTemplate:
        """
        Generate a universal professor-led template for any concept
        
        Args:
            concept: Concept name (e.g., "Valency")
            subject: Subject (e.g., "chemistry")
            intent: Intent type (e.g., "concept_explanation")
            concept_type: Concept type (e.g., "process", "comparison")
            key_elements: Key elements to visualize
            complexity: Complexity level (simple, medium, complex)
            
        Returns:
            UniversalProfessorTemplate with multi-step stages
        """
        # Generate template ID
        template_id = f"professor_{subject}_{concept.lower().replace(' ', '_')}_{intent}"
        
        # Generate stages based on concept type
        stages = self._generate_stages(concept, subject, intent, concept_type, key_elements, complexity)
        
        # Generate professor avatar
        professor_avatar = self._generate_professor_avatar(intent, complexity)
        
        # Calculate total duration
        total_duration_ms = sum(stage.duration_ms for stage in stages)
        
        # Find interaction points
        interaction_points = [
            i for i, stage in enumerate(stages)
            if stage.interactions and len(stage.interactions) > 0
        ]
        
        # Generate metadata
        metadata = {
            "concept": concept,
            "subject": subject,
            "intent": intent,
            "concept_type": concept_type,
            "complexity": complexity,
            "key_elements": key_elements,
            "generation_method": "universal_professor_template",
            "template_version": "2.0"
        }
        
        return UniversalProfessorTemplate(
            visual_type=VisualType.PROFESSOR_LED,
            template_id=template_id,
            concept=concept,
            subject=subject,
            intent=intent,
            stages=stages,
            professor_avatar=professor_avatar,
            total_duration_ms=total_duration_ms,
            interaction_points=interaction_points,
            metadata=metadata
        )
    
    def _generate_stages(
        self,
        concept: str,
        subject: str,
        intent: str,
        concept_type: str,
        key_elements: List[str],
        complexity: str
    ) -> List[VisualStage]:
        """
        Generate multi-step stages based on concept type
        PRIORITY 1: Use concept library for hero concepts
        PRIORITY 2: Generate concept-type-specific stages
        """
        # PRIORITY 1: Check if concept exists in concept library
        if self.concept_library and self.concept_library['has'](concept.lower()):
            import logging
            logging.info(f"✅ Using concept library content for: {concept}")
            stages = self._generate_stages_from_concept_library(concept, subject)
            if stages:
                return stages
        
        # PRIORITY 2: Generate based on concept type
        stages = []
        
        if concept_type == "comparison":
            stages = self._generate_comparison_stages(concept, key_elements, subject)
        elif concept_type == "process":
            stages = self._generate_process_stages(concept, key_elements, subject, complexity)
        elif concept_type == "transformation":
            stages = self._generate_transformation_stages(concept, key_elements, subject)
        elif concept_type == "cause_effect":
            stages = self._generate_cause_effect_stages(concept, key_elements, subject)
        else:
            # Generic multi-step explanation
            stages = self._generate_generic_stages(concept, key_elements, subject, complexity)
        
        # Ensure minimum 3 stages for professor-led feel
        if len(stages) < 3:
            stages = self._expand_to_minimum_stages(stages, concept, subject)
        
        return stages
    
    def _generate_stages_from_concept_library(
        self,
        concept: str,
        subject: str
    ) -> List[VisualStage]:
        """
        Generate stages from concept library with COMPLETE ANIMATION ENGINE
        Integrates: Metaphor Selector + Scene Generator + Animation Builder + Interactive Mapper
        Returns fully animated, interactive stages
        """
        concept_data = self.concept_library['get'](concept.lower())
        if not concept_data:
            logger.warning(f"⚠️ Concept '{concept}' not in library, generating generic fallback animated stages")
            return self._generate_generic_animated_stages(concept, subject)
        
        stages_data = concept_data.get('stages', [])
        
        # =====================================================================
        # STEP 1: DYNAMIC METAPHOR SELECTION (Not hardcoded!)
        # =====================================================================
        from .metaphor_registry import MetaphorSelector
        metaphor_selector = MetaphorSelector()
        selected_metaphor = metaphor_selector.select_metaphor(
            concept=concept,
            student_profile=getattr(self, 'student_profile', None),
            difficulty='medium',
            complexity='medium'
        )
        logger.info(f"🎨 Selected metaphor: {selected_metaphor.name} for {concept}")
        
        # =====================================================================
        # STEP 2: GENERATE SCENES FOR EACH STAGE
        # =====================================================================
        from .scene_generation_engine import SceneGenerationEngine
        scene_engine = SceneGenerationEngine()
        
        # =====================================================================
        # STEP 3: BUILD ANIMATION SEQUENCES
        # =====================================================================
        from .animation_sequence_builder import AnimationSequenceBuilder
        animation_builder = AnimationSequenceBuilder()
        
        # =====================================================================
        # STEP 4: MAP INTERACTIVE CONTROLS
        # =====================================================================
        from .interactive_mapper import InteractiveMapper
        interactive_mapper = InteractiveMapper()
        
        # Get concept type from data
        concept_type = concept_data.get('concept_type', 'process')
        
        # Get interactive controls for this concept
        interaction_controls = interactive_mapper.map_interactions(
            concept=concept,
            concept_type=concept_type,
            difficulty='medium'
        )
        
        logger.info(f"🎮 Mapped {len(interaction_controls.get('sliders', []))} interactive controls for {concept}")
        
        # =====================================================================
        # BUILD COMPLETE ANIMATED STAGES
        # =====================================================================
        stages = []
        for i, stage_data in enumerate(stages_data):
            # Generate complete scene specification
            scene_spec = scene_engine.generate_scene(
                concept=concept,
                metaphor=selected_metaphor,
                stage_index=i,
                stage_data=stage_data
            )
            
            # Build animation sequence with professor actions
            animation_sequence_dict = animation_builder.build_sequence(
                scene_spec=scene_spec,
                stage_data=stage_data
            )
            
            # Extract actions array from scene_spec (frontend expects array, not dict)
            # scene_spec.actions is already in the format frontend expects
            animation_sequence = scene_spec.get('actions', [])
            
            # Log for debugging
            logger.info(f"🎬 Stage {i}: {len(animation_sequence)} actions from scene_spec")
            if animation_sequence:
                logger.info(f"   Action types: {[a.get('action') for a in animation_sequence[:3]]}")
            
            # Get Lottie URL for this stage (still supported for avatar)
            lottie_url = None
            if self.lottie_manager:
                from .lottie_asset_manager import get_pack_for_subject
                pack_name = get_pack_for_subject(subject)
                lottie_url = self.lottie_manager.get_asset_for_stage(pack_name, stage_data)
            
            # Build lottie assets (for professor avatar only)
            lottie_assets = []
            if lottie_url:
                lottie_assets.append(LottieAsset(
                    url=lottie_url,
                    loop=False,
                    autoplay=True,
                    speed=1.0,
                    stage_index=i
                ))
            
            # Build animated_scene block (replaces static entity blocks)
            blocks = []
            
            # Title card for first stage
            if i == 0:
                blocks.append({
                    "type": "title_card",
                    "title": concept_data.get('key_concept', concept)
                })
            
            # Add ANIMATED SCENE block (not static entities!)
            blocks.append({
                "type": "animated_scene",
                "scene": scene_spec,
                "animation_sequence": animation_sequence  # Use array from scene_spec, not dict
            })
            
            # Add emphasis callout if present
            if stage_data.get('emphasis'):
                blocks.append({
                    "type": "tip_card",
                    "text": stage_data['emphasis'],
                    "tip_type": "important"
                })
            
            # Create VisualStage with complete animation data
            stage = VisualStage(
                stage_id=stage_data.get('stage_id', f'stage_{i}'),
                duration_ms=stage_data.get('duration_ms', 3000),
                narration=stage_data.get('narration', ''),
                narration_style="professor",
                lottie_assets=lottie_assets if lottie_assets else None,
                blocks=blocks if blocks else None,
                interactions=None,  # Interactions moved to scene_spec
                highlights=None,  # Highlights moved to animation_sequence
                transitions=None,
                emphasis=stage_data.get('emphasis')
            )
            stages.append(stage)
        
        logger.info(f"✅ Generated {len(stages)} ANIMATED stages from concept library for {concept}")
        logger.info(f"   - Metaphor: {selected_metaphor.name}")
        logger.info(f"   - Scene: {selected_metaphor.scene}")
        logger.info(f"   - Interactive controls: {len(interaction_controls.get('sliders', []))} sliders, {len(interaction_controls.get('toggles', []))} toggles")
        
        return stages
    
    def _generate_comparison_stages(
        self,
        concept: str,
        key_elements: List[str],
        subject: str
    ) -> List[VisualStage]:
        """Generate comparison stages"""
        element1 = key_elements[0] if key_elements else "Concept A"
        element2 = key_elements[1] if len(key_elements) > 1 else "Concept B"
        
        return [
            VisualStage(
                stage_id="intro",
                duration_ms=2500,
                narration=f"Let's compare {element1} and {element2} side by side.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/comparison_intro.json",
                    stage_index=0
                )],
                blocks=[
                    {"type": "title_card", "title": f"Comparing {element1} vs {element2}"}
                ],
                interactions=[InteractionPoint(
                    type="hover",
                    target="comparison_panel",
                    description="Hover to see detailed differences",
                    stage_index=0
                )]
            ),
            VisualStage(
                stage_id="left_detail",
                duration_ms=3000,
                narration=f"First, let's examine {element1} in detail.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/comparison_left.json",
                    stage_index=1
                )],
                blocks=[
                    {"type": "compare_grid", "left": {"title": element1, "points": []}}
                ],
                highlights=[{"target": "left_panel", "effect": "glow"}],
                interactions=[InteractionPoint(
                    type="click",
                    target="left_panel",
                    description="Click to explore more",
                    stage_index=1
                )]
            ),
            VisualStage(
                stage_id="right_detail",
                duration_ms=3000,
                narration=f"Now, let's look at {element2}.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/comparison_right.json",
                    stage_index=2
                )],
                blocks=[
                    {"type": "compare_grid", "right": {"title": element2, "points": []}}
                ],
                highlights=[{"target": "right_panel", "effect": "glow"}],
                interactions=[InteractionPoint(
                    type="click",
                    target="right_panel",
                    description="Click to explore more",
                    stage_index=2
                )]
            ),
            VisualStage(
                stage_id="differences",
                duration_ms=2500,
                narration="Notice the key differences highlighted here.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/comparison_highlight.json",
                    stage_index=3
                )],
                blocks=[
                    {"type": "tip_card", "text": "Key differences", "tip_type": "important"}
                ],
                emphasis="Remember these contrasting points"
            )
        ]
    
    def _generate_process_stages(
        self,
        concept: str,
        key_elements: List[str],
        subject: str,
        complexity: str
    ) -> List[VisualStage]:
        """Generate process/timeline stages"""
        num_steps = max(3, len(key_elements)) if key_elements else 4
        stages = []
        
        # Intro stage
        stages.append(VisualStage(
            stage_id="intro",
            duration_ms=2000,
            narration=f"Let's understand {concept} step by step.",
            narration_style="professor",
            lottie_assets=[LottieAsset(
                url=f"{self.lottie_base_url}/{subject}/process_intro.json",
                stage_index=0
            )],
            blocks=[
                {"type": "title_card", "title": f"Understanding {concept}"}
            ]
        ))
        
        # Step stages
        for i in range(num_steps):
            step_num = i + 1
            element = key_elements[i] if i < len(key_elements) else f"Step {step_num}"
            
            stages.append(VisualStage(
                stage_id=f"step_{step_num}",
                duration_ms=3000 if complexity == "simple" else 4000,
                narration=f"Step {step_num}: {element}",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/process_step_{step_num}.json",
                    stage_index=step_num
                )],
                blocks=[
                    {"type": "flow_map", "nodes": [{"id": f"step_{step_num}", "label": element}]}
                ],
                interactions=[InteractionPoint(
                    type="scrub",
                    target="timeline",
                    description=f"Drag to see step {step_num}",
                    stage_index=step_num
                )],
                transitions={"type": "slide", "direction": "right"}
            ))
        
        # Summary stage
        stages.append(VisualStage(
            stage_id="summary",
            duration_ms=2000,
            narration=f"And that's how {concept} works. Let's review the complete process.",
            narration_style="professor",
            lottie_assets=[LottieAsset(
                url=f"{self.lottie_base_url}/{subject}/process_summary.json",
                stage_index=num_steps + 1
            )],
            blocks=[
                {"type": "tip_card", "text": "Complete process overview", "tip_type": "summary"}
            ]
        ))
        
        return stages
    
    def _generate_transformation_stages(
        self,
        concept: str,
        key_elements: List[str],
        subject: str
    ) -> List[VisualStage]:
        """Generate transformation stages"""
        from_state = key_elements[0] if key_elements else "Initial State"
        to_state = key_elements[1] if len(key_elements) > 1 else "Final State"
        
        return [
            VisualStage(
                stage_id="initial",
                duration_ms=2500,
                narration=f"We start with {from_state}.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/transformation_initial.json",
                    stage_index=0
                )],
                blocks=[
                    {"type": "concept_nodes", "nodes": [{"id": "initial", "label": from_state}]}
                ]
            ),
            VisualStage(
                stage_id="transforming",
                duration_ms=3000,
                narration="Watch how the transformation occurs.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/transformation_morph.json",
                    stage_index=1,
                    loop=False
                )],
                blocks=[
                    {"type": "relation_arrows", "relations": [{"from": "initial", "to": "final", "label": "transforms"}]}
                ],
                interactions=[InteractionPoint(
                    type="click",
                    target="transformation_arrow",
                    description="Click to see transformation",
                    stage_index=1
                )]
            ),
            VisualStage(
                stage_id="final",
                duration_ms=2500,
                narration=f"And we arrive at {to_state}.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/transformation_final.json",
                    stage_index=2
                )],
                blocks=[
                    {"type": "concept_nodes", "nodes": [{"id": "final", "label": to_state}]}
                ],
                emphasis="Transformation complete"
            )
        ]
    
    def _generate_cause_effect_stages(
        self,
        concept: str,
        key_elements: List[str],
        subject: str
    ) -> List[VisualStage]:
        """Generate cause-effect stages"""
        cause = key_elements[0] if key_elements else "Cause"
        effect = key_elements[1] if len(key_elements) > 1 else "Effect"
        
        return [
            VisualStage(
                stage_id="cause",
                duration_ms=2500,
                narration=f"Here's the cause: {cause}",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/cause_effect_cause.json",
                    stage_index=0
                )],
                blocks=[
                    {"type": "concept_nodes", "nodes": [{"id": "cause", "label": cause}]}
                ]
            ),
            VisualStage(
                stage_id="effect",
                duration_ms=3000,
                narration=f"This leads to the effect: {effect}",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/cause_effect_effect.json",
                    stage_index=1
                )],
                blocks=[
                    {"type": "relation_arrows", "relations": [{"from": "cause", "to": "effect", "label": "causes"}]}
                ],
                interactions=[InteractionPoint(
                    type="hover",
                    target="causal_arrow",
                    description="Hover to see the connection",
                    stage_index=1
                )]
            ),
            VisualStage(
                stage_id="explanation",
                duration_ms=2500,
                narration="This is the complete cause-effect relationship.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/cause_effect_complete.json",
                    stage_index=2
                )],
                blocks=[
                    {"type": "tip_card", "text": "Cause → Effect relationship", "tip_type": "important"}
                ]
            )
        ]
    
    def _generate_generic_stages(
        self,
        concept: str,
        key_elements: List[str],
        subject: str,
        complexity: str
    ) -> List[VisualStage]:
        """Generate generic multi-step explanation stages"""
        stages = []
        
        # Intro
        stages.append(VisualStage(
            stage_id="intro",
            duration_ms=2000,
            narration=f"Let's understand {concept} together.",
            narration_style="professor",
            lottie_assets=[LottieAsset(
                url=f"{self.lottie_base_url}/{subject}/generic_intro.json",
                stage_index=0
            )],
            blocks=[
                {"type": "title_card", "title": concept}
            ]
        ))
        
        # Concept explanation stages
        num_stages = 3 if complexity == "simple" else 4 if complexity == "medium" else 5
        
        for i in range(1, num_stages):
            element = key_elements[i-1] if i-1 < len(key_elements) else f"Aspect {i}"
            
            stages.append(VisualStage(
                stage_id=f"aspect_{i}",
                duration_ms=3000,
                narration=f"Let's look at {element}.",
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/generic_aspect_{i}.json",
                    stage_index=i
                )],
                blocks=[
                    {"type": "definition_card", "term": element, "definition": f"Explanation of {element}"}
                ],
                interactions=[InteractionPoint(
                    type="hover",
                    target=f"aspect_{i}",
                    description=f"Hover for details about {element}",
                    stage_index=i
                )]
            ))
        
        # Summary
        stages.append(VisualStage(
            stage_id="summary",
            duration_ms=2000,
            narration=f"That's {concept} explained step by step. Any questions?",
            narration_style="professor",
            lottie_assets=[LottieAsset(
                url=f"{self.lottie_base_url}/{subject}/generic_summary.json",
                stage_index=num_stages
            )],
            blocks=[
                {"type": "tip_card", "text": f"Key points about {concept}", "tip_type": "summary"}
            ]
        ))
        
        return stages
    
    def _generate_generic_animated_stages(
        self,
        concept: str,
        subject: str
    ) -> List[VisualStage]:
        """
        Generate animated stages for unknown concepts
        Creates 5-stage generic lesson with REAL ANIMATIONS (move, rotate, scale)
        """
        logger.info(f"📝 Creating 5-stage generic animated lesson for '{concept}'")
        
        # Generic stage templates with educational progression
        generic_stages_data = [
            {
                "title": "What is this?", 
                "narration": f"Let's understand {concept}. This is a fundamental concept in {subject}.",
                "entities": ["main_concept"],
                "animations": [{"action": "fade_in", "from": {"opacity": 0}, "to": {"opacity": 1}}]
            },
            {
                "title": "Key Components", 
                "narration": f"The main elements of {concept} are important to grasp.",
                "entities": ["main_concept", "component_1", "component_2"],
                "animations": [
                    {"action": "move", "entity": "main_concept", "from": {"x": 200, "y": 200}, "to": {"x": 400, "y": 200}},
                    {"action": "fade_in", "entity": "component_1", "from": {"opacity": 0}, "to": {"opacity": 1}},
                    {"action": "fade_in", "entity": "component_2", "from": {"opacity": 0}, "to": {"opacity": 1}}
                ]
            },
            {
                "title": "How it Works", 
                "narration": f"Here's how {concept} functions in practice.",
                "entities": ["main_concept", "component_1", "component_2"],
                "animations": [
                    {"action": "rotate", "entity": "main_concept", "from": {"rotation": 0}, "to": {"rotation": 360}},
                    {"action": "scale", "entity": "component_1", "from": {"scale": 1}, "to": {"scale": 1.2}},
                    {"action": "scale", "entity": "component_2", "from": {"scale": 1}, "to": {"scale": 1.2}}
                ]
            },
            {
                "title": "Real Examples", 
                "narration": f"{concept} appears in many everyday situations.",
                "entities": ["main_concept", "example_1", "example_2"],
                "animations": [
                    {"action": "move", "entity": "main_concept", "from": {"x": 400, "y": 200}, "to": {"x": 300, "y": 150}},
                    {"action": "move", "entity": "example_1", "from": {"x": 100, "y": 300}, "to": {"x": 200, "y": 250}},
                    {"action": "move", "entity": "example_2", "from": {"x": 500, "y": 300}, "to": {"x": 400, "y": 250}}
                ]
            },
            {
                "title": "Remember", 
                "narration": f"Key takeaway: {concept} is essential for deeper understanding.",
                "entities": ["main_concept"],
                "animations": [
                    {"action": "pulse", "entity": "main_concept", "duration_ms": 1500, "loop": True}
                ]
            }
        ]
        
        stages = []
        for i, stage_data in enumerate(generic_stages_data):
            blocks = []
            
            if i == 0:
                blocks.append({
                    "type": "title_card",
                    "title": stage_data["title"]
                })
            
            # Build entities for this stage
            entities = []
            entity_positions = {
                "main_concept": {"x": 300, "y": 200},
                "component_1": {"x": 150, "y": 200},
                "component_2": {"x": 450, "y": 200},
                "example_1": {"x": 100, "y": 300},
                "example_2": {"x": 500, "y": 300}
            }
            
            for entity_id in stage_data["entities"]:
                entities.append({
                    "id": entity_id,
                    "type": "generic",
                    "initial_position": entity_positions.get(entity_id, {"x": 300, "y": 200}),
                    "visible": True,
                    "color": "#FF9933" if entity_id == "main_concept" else "#C41E3A",
                    "size": 60 if entity_id == "main_concept" else 40
                })
            
            # Build animation sequence from stage_data animations
            animation_sequence = []
            for anim in stage_data.get("animations", []):
                action_obj = {
                    "action": anim["action"],
                    "entity": anim.get("entity", "main_concept"),
                    "duration_ms": anim.get("duration_ms", 2000),
                    "start_time": anim.get("start_time", 500),
                    "easing": anim.get("easing", "easeInOut")
                }
                
                # Add from/to based on action type
                if anim["action"] == "move":
                    action_obj["from"] = anim.get("from", {"x": 0, "y": 0})
                    action_obj["to"] = anim.get("to", {"x": 400, "y": 200})
                elif anim["action"] == "rotate":
                    action_obj["from"] = anim.get("from", {"rotation": 0})
                    action_obj["to"] = anim.get("to", {"rotation": 360})
                elif anim["action"] == "scale":
                    action_obj["from"] = anim.get("from", {"scale": 1})
                    action_obj["to"] = anim.get("to", {"scale": 1.2})
                elif anim["action"] == "fade_in":
                    action_obj["from"] = anim.get("from", {"opacity": 0})
                    action_obj["to"] = anim.get("to", {"opacity": 1})
                elif anim["action"] == "pulse":
                    action_obj["loop"] = anim.get("loop", True)
                
                animation_sequence.append(action_obj)
            
            # Add animated_scene block with REAL animations
            blocks.append({
                "type": "animated_scene",
                "scene": {
                    "scene_type": "generic",
                    "background": "#87CEEB",  # Sky blue
                    "entities": entities,
                    "actions": animation_sequence  # Include actions in scene too
                },
                "animation_sequence": animation_sequence
            })
            
            # Add key insight for last stage
            if i == len(generic_stages_data) - 1:
                blocks.append({
                    "type": "key_insight",
                    "text": f"{concept} is a core concept you'll use throughout your learning."
                })
            
            stage = VisualStage(
                stage_id=f"generic_{i}",
                duration_ms=3000,
                narration=stage_data["narration"],
                narration_style="professor",
                blocks=blocks,
                lottie_assets=None,
                interactions=None,
                highlights=None,
                transitions=None,
                emphasis=None
            )
            stages.append(stage)
        
        logger.info(f"✅ Generated {len(stages)} generic animated stages with {sum(len(s.get('animations', [])) for s in generic_stages_data)} total animations")
        return stages
    
    def _expand_to_minimum_stages(
        self,
        stages: List[VisualStage],
        concept: str,
        subject: str
    ) -> List[VisualStage]:
        """
        Ensure minimum 3 stages for professor-led feel
        Uses educational content, not placeholders
        """
        if len(stages) >= 3:
            return stages
        
        # Add intermediate stages with educational narration
        expanded = [stages[0]] if stages else []
        
        # Educational narration templates (not placeholders!)
        educational_narrations = [
            f"Now let's examine the key components of {concept} in detail.",
            f"Here's an important aspect of {concept} that helps us understand it better.",
            f"Notice how this part of {concept} connects to what we just learned."
        ]
        
        stages_needed = 3 - len(stages)
        for i in range(1, stages_needed + 1):
            narration = educational_narrations[min(i-1, len(educational_narrations)-1)]
            
            expanded.append(VisualStage(
                stage_id=f"detail_{i}",
                duration_ms=2500,
                narration=narration,
                narration_style="professor",
                lottie_assets=[LottieAsset(
                    url=f"{self.lottie_base_url}/{subject}/generic_detail_{i}.json",
                    stage_index=i
                )],
                blocks=[
                    {"type": "concept_detail", "title": f"Key Aspect {i}", "description": f"Understanding {concept}"}
                ]
            ))
        
        if len(stages) > 1:
            expanded.extend(stages[1:])
        
        return expanded
    
    def _generate_professor_avatar(
        self,
        intent: str,
        complexity: str
    ) -> ProfessorAvatar:
        """Generate professor avatar configuration"""
        expression_map = {
            "definition_query": "explaining",
            "concept_explanation": "explaining",
            "deep_dive": "thinking",
            "application_request": "pointing",
            "compare_query": "explaining"
        }
        
        expression = expression_map.get(intent, "explaining")
        
        return ProfessorAvatar(
            expression=expression,
            position="bottom_right",
            animation="explain" if intent == "concept_explanation" else "point",
            visible_stages=None  # Show in all stages
        )

