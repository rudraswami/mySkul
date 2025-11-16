"""
Animation Builder - SVG/React Animation System
Creates animated sequences using Framer Motion-compatible data structures
Provides fallback when Lottie animations are unavailable
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# ANIMATION DATA STRUCTURES
# ============================================================================

@dataclass
class AnimationKeyframe:
    """Single keyframe in an animation"""
    property: str  # e.g., 'x', 'y', 'opacity', 'scale', 'rotate'
    value: Any  # Target value
    duration_ms: int
    easing: str = 'easeInOut'  # easeIn, easeOut, easeInOut, linear, bounce, spring

@dataclass
class EntityAnimation:
    """Complete animation for a single entity"""
    entity_id: str
    animation_type: str  # translate, rotate, scale, fade, morph, path
    keyframes: List[AnimationKeyframe]
    loop: bool = False
    delay_ms: int = 0
    
    def to_framer_motion(self) -> Dict[str, Any]:
        """Convert to Framer Motion animate prop format"""
        animate_props = {}
        transition_props = {}
        
        for kf in self.keyframes:
            if kf.property in ['x', 'y', 'scale', 'rotate', 'opacity']:
                animate_props[kf.property] = kf.value
                transition_props['duration'] = kf.duration_ms / 1000  # Convert to seconds
                transition_props['ease'] = kf.easing
        
        if self.delay_ms > 0:
            transition_props['delay'] = self.delay_ms / 1000
            
        if self.loop:
            transition_props['repeat'] = float('inf')
            transition_props['repeatType'] = 'loop'
        
        return {
            'animate': animate_props,
            'transition': transition_props
        }

@dataclass
class StageAnimation:
    """All animations for a single stage"""
    stage_id: str
    entity_animations: List[EntityAnimation]
    background_animation: Optional[Dict[str, Any]] = None
    camera_animation: Optional[Dict[str, Any]] = None

# ============================================================================
# ANIMATION BUILDERS BY TYPE
# ============================================================================

class AnimationBuilder:
    """Builds SVG/React animations for various animation types"""
    
    def __init__(self):
        self.animation_catalog = self._build_animation_catalog()
    
    def _build_animation_catalog(self) -> Dict[str, Any]:
        """Catalog of predefined animations"""
        return {
            # MOTION ANIMATIONS
            'move_straight': {
                'type': 'translate',
                'properties': ['x'],
                'default_duration_ms': 2000,
                'default_easing': 'easeInOut'
            },
            'turn_corner': {
                'type': 'rotate',
                'properties': ['rotate', 'x', 'y'],
                'default_duration_ms': 1500,
                'default_easing': 'easeInOut'
            },
            'arc_motion': {
                'type': 'path',
                'properties': ['x', 'y'],
                'default_duration_ms': 3000,
                'default_easing': 'easeOut'
            },
            
            # APPEARANCE ANIMATIONS
            'fade_in': {
                'type': 'fade',
                'properties': ['opacity'],
                'default_duration_ms': 800,
                'default_easing': 'easeIn'
            },
            'fade_out': {
                'type': 'fade',
                'properties': ['opacity'],
                'default_duration_ms': 800,
                'default_easing': 'easeOut'
            },
            'pulse': {
                'type': 'scale',
                'properties': ['scale'],
                'default_duration_ms': 1000,
                'default_easing': 'easeInOut',
                'loop': True
            },
            
            # ROTATION ANIMATIONS
            'rotate': {
                'type': 'rotate',
                'properties': ['rotate'],
                'default_duration_ms': 2000,
                'default_easing': 'linear',
                'loop': True
            },
            'rotate_spin': {
                'type': 'rotate',
                'properties': ['rotate'],
                'default_duration_ms': 500,
                'default_easing': 'linear'
            },
            
            # SCALE ANIMATIONS
            'grow': {
                'type': 'scale',
                'properties': ['scale'],
                'default_duration_ms': 600,
                'default_easing': 'spring'
            },
            'shrink': {
                'type': 'scale',
                'properties': ['scale'],
                'default_duration_ms': 600,
                'default_easing': 'easeOut'
            },
            
            # SPECIAL EFFECTS
            'glow': {
                'type': 'effect',
                'properties': ['opacity', 'scale'],
                'default_duration_ms': 1000,
                'default_easing': 'easeInOut',
                'loop': True
            },
            'highlight': {
                'type': 'effect',
                'properties': ['opacity', 'scale'],
                'default_duration_ms': 1500,
                'default_easing': 'easeInOut'
            }
        }
    
    def build_animation(
        self,
        animation_name: str,
        entity_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> EntityAnimation:
        """
        Build a complete animation for an entity
        
        Args:
            animation_name: Name of animation from catalog
            entity_id: ID of entity to animate
            params: Override parameters (start_pos, end_pos, duration, etc.)
        
        Returns:
            EntityAnimation object
        """
        params = params or {}
        catalog_entry = self.animation_catalog.get(animation_name, {})
        
        animation_type = catalog_entry.get('type', 'translate')
        default_duration = catalog_entry.get('default_duration_ms', 1000)
        default_easing = catalog_entry.get('default_easing', 'easeInOut')
        loop = catalog_entry.get('loop', False)
        
        # Build keyframes based on animation type
        if animation_name == 'move_straight':
            keyframes = self._build_move_straight_keyframes(params, default_duration, default_easing)
        elif animation_name == 'arc_motion':
            keyframes = self._build_arc_motion_keyframes(params, default_duration, default_easing)
        elif animation_name == 'fade_in':
            keyframes = self._build_fade_in_keyframes(default_duration, default_easing)
        elif animation_name == 'fade_out':
            keyframes = self._build_fade_out_keyframes(default_duration, default_easing)
        elif animation_name == 'pulse':
            keyframes = self._build_pulse_keyframes(default_duration, default_easing)
        elif animation_name == 'rotate':
            keyframes = self._build_rotate_keyframes(params, default_duration)
        elif animation_name == 'glow':
            keyframes = self._build_glow_keyframes(default_duration, default_easing)
        elif animation_name == 'highlight':
            keyframes = self._build_highlight_keyframes(default_duration, default_easing)
        else:
            # Generic animation
            keyframes = [AnimationKeyframe('opacity', 1, default_duration, default_easing)]
        
        return EntityAnimation(
            entity_id=entity_id,
            animation_type=animation_type,
            keyframes=keyframes,
            loop=loop,
            delay_ms=params.get('delay_ms', 0)
        )
    
    def _build_move_straight_keyframes(
        self,
        params: Dict[str, Any],
        duration: int,
        easing: str
    ) -> List[AnimationKeyframe]:
        """Build keyframes for straight-line motion"""
        start_x = params.get('start_x', 0)
        end_x = params.get('end_x', 300)
        start_y = params.get('start_y', 0)
        end_y = params.get('end_y', 0)
        
        return [
            AnimationKeyframe('x', end_x, duration, easing),
            AnimationKeyframe('y', end_y, duration, easing)
        ]
    
    def _build_arc_motion_keyframes(
        self,
        params: Dict[str, Any],
        duration: int,
        easing: str
    ) -> List[AnimationKeyframe]:
        """Build keyframes for parabolic arc motion"""
        start_x = params.get('start_x', 0)
        end_x = params.get('end_x', 400)
        start_y = params.get('start_y', 0)
        peak_y = params.get('peak_y', -200)  # Negative = upward
        
        # Break into multiple keyframes for arc
        half_duration = duration // 2
        
        return [
            AnimationKeyframe('x', (start_x + end_x) / 2, half_duration, 'linear'),
            AnimationKeyframe('y', peak_y, half_duration, 'easeOut'),
            AnimationKeyframe('x', end_x, half_duration, 'linear'),
            AnimationKeyframe('y', start_y, half_duration, 'easeIn')
        ]
    
    def _build_fade_in_keyframes(self, duration: int, easing: str) -> List[AnimationKeyframe]:
        """Build fade-in keyframes"""
        return [AnimationKeyframe('opacity', 1, duration, easing)]
    
    def _build_fade_out_keyframes(self, duration: int, easing: str) -> List[AnimationKeyframe]:
        """Build fade-out keyframes"""
        return [AnimationKeyframe('opacity', 0, duration, easing)]
    
    def _build_pulse_keyframes(self, duration: int, easing: str) -> List[AnimationKeyframe]:
        """Build pulse keyframes (scale up/down repeatedly)"""
        return [
            AnimationKeyframe('scale', 1.15, duration // 2, easing),
            AnimationKeyframe('scale', 1.0, duration // 2, easing)
        ]
    
    def _build_rotate_keyframes(self, params: Dict[str, Any], duration: int) -> List[AnimationKeyframe]:
        """Build rotation keyframes"""
        start_angle = params.get('start_angle', 0)
        end_angle = params.get('end_angle', 360)
        
        return [AnimationKeyframe('rotate', end_angle, duration, 'linear')]
    
    def _build_glow_keyframes(self, duration: int, easing: str) -> List[AnimationKeyframe]:
        """Build glow effect keyframes"""
        return [
            AnimationKeyframe('opacity', 0.8, duration // 2, easing),
            AnimationKeyframe('scale', 1.1, duration // 2, easing),
            AnimationKeyframe('opacity', 1.0, duration // 2, easing),
            AnimationKeyframe('scale', 1.0, duration // 2, easing)
        ]
    
    def _build_highlight_keyframes(self, duration: int, easing: str) -> List[AnimationKeyframe]:
        """Build highlight effect keyframes"""
        return [
            AnimationKeyframe('scale', 1.2, duration // 3, 'easeOut'),
            AnimationKeyframe('opacity', 0.9, duration // 3, 'easeInOut'),
            AnimationKeyframe('scale', 1.0, duration // 3, 'easeIn'),
            AnimationKeyframe('opacity', 1.0, duration // 3, 'easeIn')
        ]
    
    # ========================================================================
    # CONCEPT-SPECIFIC ANIMATION BUILDERS
    # ========================================================================
    
    def build_velocity_animation(self, stage_index: int) -> List[EntityAnimation]:
        """Build animations for velocity concept"""
        if stage_index == 0:
            # Intro: Train appears
            return [
                self.build_animation('fade_in', 'metro_train'),
                self.build_animation('fade_in', 'landmark_a', {'delay_ms': 200}),
                self.build_animation('fade_in', 'landmark_b', {'delay_ms': 400})
            ]
        elif stage_index == 1:
            # Speed demo: Train moves with speedometer
            return [
                self.build_animation('move_straight', 'metro_train', {
                    'start_x': 100, 'end_x': 600, 'duration_ms': 3000
                }),
                self.build_animation('fade_in', 'speedometer', {'delay_ms': 500}),
                self.build_animation('pulse', 'speedometer', {'delay_ms': 1000})
            ]
        elif stage_index == 2:
            # Direction change: Arrow rotates, train turns
            return [
                self.build_animation('rotate', 'direction_arrow', {
                    'start_angle': 0, 'end_angle': 180, 'duration_ms': 1500
                }),
                self.build_animation('move_straight', 'metro_train', {
                    'start_x': 600, 'end_x': 100, 'duration_ms': 3000, 'delay_ms': 1500
                })
            ]
        elif stage_index == 3:
            # Vector display: Arrow pulses
            return [
                self.build_animation('pulse', 'direction_arrow'),
                self.build_animation('highlight', 'speedometer', {'delay_ms': 500})
            ]
        else:
            # Summary: All elements glow
            return [
                self.build_animation('glow', 'metro_train'),
                self.build_animation('glow', 'direction_arrow', {'delay_ms': 200}),
                self.build_animation('glow', 'speedometer', {'delay_ms': 400})
            ]
    
    def build_projectile_animation(self, stage_index: int) -> List[EntityAnimation]:
        """Build animations for projectile motion concept"""
        if stage_index == 0:
            return [
                self.build_animation('fade_in', 'cricket_ball'),
                self.build_animation('fade_in', 'ground', {'delay_ms': 200})
            ]
        elif stage_index == 1:
            return [
                self.build_animation('fade_in', 'velocity_vectors'),
                self.build_animation('highlight', 'velocity_vectors', {'delay_ms': 1000})
            ]
        elif stage_index == 2:
            return [
                self.build_animation('arc_motion', 'cricket_ball', {
                    'start_x': 100, 'end_x': 700, 'start_y': 500, 'peak_y': 200, 'duration_ms': 4000
                }),
                self.build_animation('fade_in', 'trajectory_arc', {'delay_ms': 200}),
                self.build_animation('pulse', 'gravity_arrow', {'delay_ms': 2000})
            ]
        elif stage_index == 3:
            return [
                self.build_animation('highlight', 'velocity_vectors'),
                self.build_animation('pulse', 'cricket_ball', {'delay_ms': 500})
            ]
        else:
            return [
                self.build_animation('glow', 'cricket_ball'),
                self.build_animation('glow', 'trajectory_arc', {'delay_ms': 300})
            ]
    
    def build_valency_animation(self, stage_index: int) -> List[EntityAnimation]:
        """Build animations for valency concept"""
        if stage_index == 0:
            return [
                self.build_animation('fade_in', 'atom_nucleus'),
                self.build_animation('rotate', 'atom_nucleus', {'delay_ms': 500})
            ]
        elif stage_index == 1:
            return [
                self.build_animation('fade_in', 'electron_shells'),
                self.build_animation('fade_in', 'electrons', {'delay_ms': 300})
            ]
        elif stage_index == 2:
            return [
                self.build_animation('highlight', 'electron_shells'),
                self.build_animation('pulse', 'empty_slots', {'delay_ms': 500})
            ]
        elif stage_index == 3:
            return [
                self.build_animation('fade_in', 'bonding_hand'),
                self.build_animation('pulse', 'bonding_hand', {'delay_ms': 500})
            ]
        else:
            return [
                self.build_animation('glow', 'atom_nucleus'),
                self.build_animation('glow', 'bonding_hand', {'delay_ms': 300})
            ]
    
    def build_photosynthesis_animation(self, stage_index: int) -> List[EntityAnimation]:
        """Build animations for photosynthesis concept"""
        if stage_index == 0:
            return [
                self.build_animation('fade_in', 'chloroplast'),
                self.build_animation('fade_in', 'sunlight_rays', {'delay_ms': 300})
            ]
        elif stage_index == 1:
            return [
                self.build_animation('move_straight', 'co2_molecules', {
                    'start_x': 700, 'end_x': 400, 'duration_ms': 2000
                }),
                self.build_animation('move_straight', 'water_molecules', {
                    'start_x': 100, 'end_x': 400, 'start_y': 500, 'end_y': 300, 'duration_ms': 2500, 'delay_ms': 500
                })
            ]
        elif stage_index == 2:
            return [
                self.build_animation('glow', 'chloroplast'),
                self.build_animation('pulse', 'sunlight_rays', {'delay_ms': 300})
            ]
        elif stage_index == 3:
            return [
                self.build_animation('fade_in', 'glucose'),
                self.build_animation('fade_in', 'oxygen', {'delay_ms': 500}),
                self.build_animation('move_straight', 'oxygen', {
                    'start_y': 300, 'end_y': 100, 'duration_ms': 2000, 'delay_ms': 1000
                })
            ]
        else:
            return [
                self.build_animation('glow', 'glucose'),
                self.build_animation('pulse', 'chloroplast', {'delay_ms': 300})
            ]

# ============================================================================
# STAGE ANIMATION COMPOSER
# ============================================================================

class StageAnimationComposer:
    """Composes complete stage animations from concept-specific builders"""
    
    def __init__(self):
        self.animation_builder = AnimationBuilder()
    
    def compose_stage_animation(
        self,
        concept: str,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> StageAnimation:
        """
        Compose complete animation for a stage
        
        Args:
            concept: Concept name (e.g., 'velocity')
            stage_index: Index of stage
            stage_data: Stage data from concept library
        
        Returns:
            StageAnimation with all entity animations
        """
        stage_id = stage_data.get('stage_id', f'stage_{stage_index}')
        animation_name = stage_data.get('animation', '')
        
        # Try concept-specific animation first
        entity_animations = self._get_concept_specific_animations(concept, stage_index)
        
        # If no concept-specific animations, build generic ones
        if not entity_animations:
            entity_animations = self._build_generic_animations(stage_data)
        
        return StageAnimation(
            stage_id=stage_id,
            entity_animations=entity_animations
        )
    
    def _get_concept_specific_animations(
        self,
        concept: str,
        stage_index: int
    ) -> List[EntityAnimation]:
        """Get concept-specific animations if available"""
        concept_lower = concept.lower()
        
        if concept_lower == 'velocity':
            return self.animation_builder.build_velocity_animation(stage_index)
        elif concept_lower == 'projectile':
            return self.animation_builder.build_projectile_animation(stage_index)
        elif concept_lower == 'valency':
            return self.animation_builder.build_valency_animation(stage_index)
        elif concept_lower == 'photosynthesis':
            return self.animation_builder.build_photosynthesis_animation(stage_index)
        
        return []
    
    def _build_generic_animations(
        self,
        stage_data: Dict[str, Any]
    ) -> List[EntityAnimation]:
        """Build generic animations based on stage data"""
        entities_visible = stage_data.get('entities_visible', [])
        highlight = stage_data.get('highlight')
        
        animations = []
        
        # Fade in all visible entities
        for i, entity_id in enumerate(entities_visible):
            animations.append(
                self.animation_builder.build_animation(
                    'fade_in',
                    entity_id,
                    {'delay_ms': i * 200}
                )
            )
        
        # Highlight specific entity if specified
        if highlight:
            animations.append(
                self.animation_builder.build_animation(
                    'highlight',
                    highlight,
                    {'delay_ms': len(entities_visible) * 200 + 500}
                )
            )
        
        return animations

# ============================================================================
# FRONTEND ANIMATION COMPONENT GENERATORS
# ============================================================================

def generate_framer_motion_component(
    entity_animation: EntityAnimation,
    svg_content: str
) -> str:
    """
    Generate React component code for Framer Motion animation
    
    Returns:
        JSX string for animated component
    """
    motion_props = entity_animation.to_framer_motion()
    
    return f'''
<motion.g
  id="{entity_animation.entity_id}"
  initial={{{{ opacity: 0, x: 0, y: 0, scale: 1, rotate: 0 }}}}
  animate={{{motion_props['animate']}}}
  transition={{{motion_props['transition']}}}
>
  {svg_content}
</motion.g>
'''

def generate_stage_animation_data(
    stage_animation: StageAnimation
) -> Dict[str, Any]:
    """
    Convert StageAnimation to JSON-serializable format for frontend
    
    Returns:
        Dictionary that can be sent to frontend
    """
    return {
        'stage_id': stage_animation.stage_id,
        'entity_animations': [
            {
                'entity_id': ea.entity_id,
                'animation_type': ea.animation_type,
                'framer_motion': ea.to_framer_motion(),
                'keyframes': [asdict(kf) for kf in ea.keyframes]
            }
            for ea in stage_animation.entity_animations
        ]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_animation_duration(stage_animation: StageAnimation) -> int:
    """Calculate total duration of stage animation"""
    max_duration = 0
    for entity_anim in stage_animation.entity_animations:
        total_time = entity_anim.delay_ms
        for keyframe in entity_anim.keyframes:
            total_time += keyframe.duration_ms
        max_duration = max(max_duration, total_time)
    return max_duration

