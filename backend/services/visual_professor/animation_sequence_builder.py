"""
Animation Sequence Builder - Creates Framer Motion Animation Sequences
Builds complete animation sequences with:
- Entity keyframes for Framer Motion
- Professor actions (pointing, writing, demonstrating)
- Highlight effects synchronized with narration
- Timeline coordination
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ANIMATION SEQUENCE BUILDER
# ============================================================================

class AnimationSequenceBuilder:
    """
    Builds Framer Motion-compatible animation sequences
    Converts scene actions into React-ready animation data
    """
    
    def __init__(self):
        self.easing_map = {
            'easeInOut': [0.42, 0, 0.58, 1],
            'easeIn': [0.42, 0, 1, 1],
            'easeOut': [0, 0, 0.58, 1],
            'linear': [0, 0, 1, 1],
            'spring': 'spring',
            'bounce': [0.68, -0.55, 0.265, 1.55]
        }
    
    def build_sequence(
        self,
        scene_spec: Dict[str, Any],
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build complete animation sequence from scene specification
        
        Args:
            scene_spec: Scene specification from SceneGenerationEngine
            stage_data: Stage data from concept library
            
        Returns:
            Animation sequence with entity keyframes and professor actions
        """
        actions = scene_spec.get('actions', [])
        entities = scene_spec.get('entities', [])
        timeline = scene_spec.get('timeline', {})
        
        # Build entity animations
        entity_animations = []
        for action in actions:
            entity_anim = self._build_entity_animation(action, entities)
            if entity_anim:
                entity_animations.append(entity_anim)
        
        # Build professor actions
        professor_actions = self._build_professor_actions(
            scene_spec,
            stage_data,
            timeline.get('sync_points', [])
        )
        
        # Build highlights
        highlights = self._build_highlights(stage_data, timeline)
        
        # Build annotations (text that professor writes)
        annotations = self._build_annotations(stage_data)
        
        sequence_id = f"{scene_spec.get('scene_id', 'scene')}_{stage_data.get('stage_id', 'stage')}"
        
        return {
            'sequence_id': sequence_id,
            'entities': entity_animations,
            'professor_actions': professor_actions,
            'highlights': highlights,
            'annotations': annotations,
            'total_duration_ms': timeline.get('total_duration_ms', 3000)
        }
    
    def _build_entity_animation(
        self,
        action: Dict[str, Any],
        entities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Build animation for single entity from action"""
        entity_id = action.get('entity')
        action_type = action.get('action')
        
        if not entity_id or not action_type:
            return None
        
        # Find entity spec
        entity_spec = next((e for e in entities if e['id'] == entity_id), None)
        if not entity_spec:
            return None
        
        # Build keyframes based on action type
        keyframes = []
        
        if action_type == 'move':
            keyframes = self._build_move_keyframes(action, entity_spec)
        elif action_type == 'rotate':
            keyframes = self._build_rotate_keyframes(action, entity_spec)
        elif action_type == 'fade_in':
            keyframes = self._build_fade_in_keyframes(action)
        elif action_type == 'fade_out':
            keyframes = self._build_fade_out_keyframes(action)
        elif action_type == 'pulse':
            keyframes = self._build_pulse_keyframes(action)
        elif action_type == 'glow':
            keyframes = self._build_glow_keyframes(action)
        elif action_type == 'path':
            keyframes = self._build_path_keyframes(action, entity_spec)
        elif action_type == 'draw_curve':
            keyframes = self._build_draw_curve_keyframes(action)
        elif action_type == 'draw_line':
            keyframes = self._build_draw_line_keyframes(action)
        else:
            # Generic fade in
            keyframes = [{'time': 0, 'props': {'opacity': 1}}]
        
        return {
            'entity_id': entity_id,
            'svg_component': entity_spec.get('svg_component', 'GenericEntitySVG'),
            'keyframes': keyframes,
            'loop': action.get('loop', False),
            'delay_ms': action.get('start_time', 0)
        }
    
    def _build_move_keyframes(
        self,
        action: Dict[str, Any],
        entity_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build keyframes for linear motion"""
        from_pos = action.get('from', entity_spec.get('initial_position', {'x': 0, 'y': 0}))
        to_pos = action.get('to', {'x': 0, 'y': 0})
        duration = action.get('duration_ms', 2000)
        easing = action.get('easing', 'easeInOut')
        
        return [
            {
                'time': 0,
                'props': {
                    'x': from_pos.get('x', 0),
                    'y': from_pos.get('y', 0),
                    'opacity': 1
                }
            },
            {
                'time': duration,
                'props': {
                    'x': to_pos.get('x', 0),
                    'y': to_pos.get('y', 0),
                    'opacity': 1
                },
                'easing': easing
            }
        ]
    
    def _build_path_keyframes(
        self,
        action: Dict[str, Any],
        entity_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build keyframes for parabolic/curved path"""
        from_pos = action.get('from', {'x': 0, 'y': 0})
        control_pos = action.get('control', {'x': 400, 'y': 200})
        to_pos = action.get('to', {'x': 800, 'y': 0})
        duration = action.get('duration_ms', 4000)
        
        # Break path into multiple keyframes for smooth arc
        return [
            {
                'time': 0,
                'props': {'x': from_pos['x'], 'y': from_pos['y'], 'opacity': 1}
            },
            {
                'time': duration // 4,
                'props': {
                    'x': from_pos['x'] + (control_pos['x'] - from_pos['x']) / 2,
                    'y': from_pos['y'] + (control_pos['y'] - from_pos['y']) / 2,
                    'opacity': 1
                },
                'easing': 'easeOut'
            },
            {
                'time': duration // 2,
                'props': {'x': control_pos['x'], 'y': control_pos['y'], 'opacity': 1},
                'easing': 'linear'
            },
            {
                'time': 3 * duration // 4,
                'props': {
                    'x': control_pos['x'] + (to_pos['x'] - control_pos['x']) / 2,
                    'y': control_pos['y'] + (to_pos['y'] - control_pos['y']) / 2,
                    'opacity': 1
                },
                'easing': 'easeIn'
            },
            {
                'time': duration,
                'props': {'x': to_pos['x'], 'y': to_pos['y'], 'opacity': 1},
                'easing': 'easeIn'
            }
        ]
    
    def _build_rotate_keyframes(
        self,
        action: Dict[str, Any],
        entity_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build rotation keyframes"""
        from_rotation = action.get('from', {}).get('rotation', 0)
        to_rotation = action.get('to', {}).get('rotation', 360)
        duration = action.get('duration_ms', 2000)
        easing = action.get('easing', 'easeInOut')
        
        return [
            {'time': 0, 'props': {'rotate': from_rotation}},
            {'time': duration, 'props': {'rotate': to_rotation}, 'easing': easing}
        ]
    
    def _build_fade_in_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build fade-in keyframes"""
        duration = action.get('duration_ms', 1000)
        return [
            {'time': 0, 'props': {'opacity': 0}},
            {'time': duration, 'props': {'opacity': 1}, 'easing': 'easeIn'}
        ]
    
    def _build_fade_out_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build fade-out keyframes"""
        duration = action.get('duration_ms', 1000)
        return [
            {'time': 0, 'props': {'opacity': 1}},
            {'time': duration, 'props': {'opacity': 0}, 'easing': 'easeOut'}
        ]
    
    def _build_pulse_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build pulse keyframes"""
        duration = action.get('duration_ms', 1000)
        return [
            {'time': 0, 'props': {'scale': 1}},
            {'time': duration // 2, 'props': {'scale': 1.15}, 'easing': 'easeInOut'},
            {'time': duration, 'props': {'scale': 1}, 'easing': 'easeInOut'}
        ]
    
    def _build_glow_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build glow effect keyframes"""
        duration = action.get('duration_ms', 1500)
        intensity = action.get('intensity', 'medium')
        
        scale_factor = {'low': 1.05, 'medium': 1.1, 'high': 1.2}.get(intensity, 1.1)
        
        return [
            {'time': 0, 'props': {'scale': 1, 'opacity': 1}},
            {'time': duration // 2, 'props': {'scale': scale_factor, 'opacity': 0.9}, 'easing': 'easeInOut'},
            {'time': duration, 'props': {'scale': 1, 'opacity': 1}, 'easing': 'easeInOut'}
        ]
    
    def _build_draw_curve_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build curve drawing keyframes"""
        duration = action.get('duration_ms', 2500)
        return [
            {'time': 0, 'props': {'strokeDashoffset': 1000}},
            {'time': duration, 'props': {'strokeDashoffset': 0}, 'easing': 'easeInOut'}
        ]
    
    def _build_draw_line_keyframes(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build line drawing keyframes"""
        from_pos = action.get('from', {'x': 0, 'y': 0})
        to_pos = action.get('to', {'x': 100, 'y': 100})
        duration = action.get('duration_ms', 2000)
        
        return [
            {'time': 0, 'props': {'x2': from_pos['x'], 'y2': from_pos['y']}},
            {'time': duration, 'props': {'x2': to_pos['x'], 'y2': to_pos['y']}, 'easing': 'easeInOut'}
        ]
    
    # ========================================================================
    # PROFESSOR ACTIONS BUILDER
    # ========================================================================
    
    def _build_professor_actions(
        self,
        scene_spec: Dict[str, Any],
        stage_data: Dict[str, Any],
        sync_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build professor actions synchronized with scene animations
        Professor points to entities, writes equations, demonstrates
        """
        actions = []
        narration = stage_data.get('narration', '')
        stage_id = stage_data.get('stage_id', '')
        
        # Intro stage: Professor explaining gesture
        if 'intro' in stage_id.lower():
            actions.append({
                'action': 'explaining',
                'time': 0,
                'duration_ms': 2000,
                'gesture': 'open_arms',
                'speech_bubble': "Let me explain this concept..."
            })
        
        # When entity is highlighted, professor points
        highlight = stage_data.get('highlight')
        if highlight:
            actions.append({
                'action': 'point_to',
                'target': highlight,
                'time': 1500,
                'duration_ms': 1500,
                'speech_bubble': None
            })
        
        # If stage has emphasis, professor writes it
        emphasis = stage_data.get('emphasis')
        if emphasis:
            actions.append({
                'action': 'write_text',
                'text': emphasis,
                'time': sync_points[-1]['time'] if sync_points else 2000,
                'duration_ms': 2000,
                'position': {'x': 400, 'y': 100}
            })
        
        # If stage has interaction, professor demonstrates
        if stage_data.get('interaction'):
            actions.append({
                'action': 'demonstrating',
                'target': stage_data['interaction'].get('target'),
                'time': 1000,
                'duration_ms': 1500,
                'gesture': 'pointing_animated'
            })
        
        # Summary stage: Professor concluding gesture
        if 'summary' in stage_id.lower():
            actions.append({
                'action': 'concluding',
                'time': 0,
                'duration_ms': 2000,
                'gesture': 'thumbs_up',
                'speech_bubble': "Remember this!"
            })
        
        return actions
    
    def _build_highlights(
        self,
        stage_data: Dict[str, Any],
        timeline: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build highlight effects for important elements"""
        highlights = []
        
        highlight_entity = stage_data.get('highlight')
        if highlight_entity:
            # Calculate when to highlight (after initial animations)
            sync_points = timeline.get('sync_points', [])
            highlight_time = sync_points[0]['time'] if sync_points else 1000
            
            highlights.append({
                'entity': highlight_entity,
                'time': highlight_time,
                'duration_ms': 2000,
                'effect': 'glow',
                'color': '#FCD34D',
                'intensity': 'high'
            })
        
        return highlights
    
    def _build_annotations(
        self,
        stage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build text annotations that appear during stage"""
        annotations = []
        
        # Key concept annotation
        if stage_data.get('stage_id') == 'intro':
            key_concept = stage_data.get('key_concept')
            if key_concept:
                annotations.append({
                    'type': 'equation',
                    'text': key_concept,
                    'position': {'x': 400, 'y': 80},
                    'time': 1000,
                    'duration_ms': 2000,
                    'style': 'bold',
                    'color': '#7C3AED'
                })
        
        # Emphasis annotation
        emphasis = stage_data.get('emphasis')
        if emphasis:
            annotations.append({
                'type': 'callout',
                'text': emphasis,
                'position': {'x': 400, 'y': 520},
                'time': 2000,
                'duration_ms': 2000,
                'style': 'highlight',
                'color': '#FCD34D'
            })
        
        return annotations
    
    # ========================================================================
    # CONCEPT-SPECIFIC SEQUENCE BUILDERS
    # ========================================================================
    
    def build_velocity_sequence(
        self,
        stage_index: int,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build velocity-specific animation sequence"""
        if stage_index == 0:
            # Intro: Metro appears
            return {
                'entities': [
                    {
                        'entity_id': 'metro_train',
                        'keyframes': [
                            {'time': 0, 'props': {'x': 100, 'y': 400, 'opacity': 0}},
                            {'time': 800, 'props': {'x': 100, 'y': 400, 'opacity': 1}, 'easing': 'easeIn'}
                        ]
                    }
                ],
                'professor_actions': [
                    {'action': 'explaining', 'time': 0, 'duration_ms': 2000}
                ]
            }
        elif stage_index == 1:
            # Metro moves north
            return {
                'entities': [
                    {
                        'entity_id': 'metro_train',
                        'keyframes': [
                            {'time': 0, 'props': {'x': 100, 'y': 400}},
                            {'time': 3000, 'props': {'x': 700, 'y': 400}, 'easing': 'easeInOut'}
                        ]
                    },
                    {
                        'entity_id': 'speedometer',
                        'keyframes': [
                            {'time': 1500, 'props': {'scale': 1}},
                            {'time': 2000, 'props': {'scale': 1.1}, 'easing': 'spring'},
                            {'time': 2500, 'props': {'scale': 1}, 'easing': 'spring'}
                        ]
                    }
                ],
                'professor_actions': [
                    {'action': 'point_to', 'target': 'speedometer', 'time': 1500}
                ],
                'annotations': [
                    {'text': '60 km/h', 'position': {'x': 650, 'y': 80}, 'time': 2000}
                ]
            }
        else:
            return {'entities': [], 'professor_actions': []}
    
    def build_projectile_sequence(
        self,
        stage_index: int,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build projectile-specific animation sequence"""
        if stage_index == 2:
            # Ball flies in arc
            return {
                'entities': [
                    {
                        'entity_id': 'cricket_ball',
                        'keyframes': [
                            {'time': 0, 'props': {'x': 100, 'y': 500}},
                            {'time': 1000, 'props': {'x': 250, 'y': 300}, 'easing': 'easeOut'},
                            {'time': 2000, 'props': {'x': 400, 'y': 200}, 'easing': 'linear'},
                            {'time': 3000, 'props': {'x': 550, 'y': 300}, 'easing': 'easeIn'},
                            {'time': 4000, 'props': {'x': 700, 'y': 500}, 'easing': 'easeIn'}
                        ]
                    }
                ],
                'professor_actions': [
                    {'action': 'point_to', 'target': 'trajectory_arc', 'time': 2000}
                ],
                'highlights': [
                    {'entity': 'trajectory_arc', 'time': 2500, 'effect': 'glow'}
                ]
            }
        else:
            return {'entities': [], 'professor_actions': []}
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def convert_to_framer_motion_format(
        self,
        keyframes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Convert keyframes to Framer Motion animate/transition format
        Used by frontend to apply animations
        """
        if not keyframes:
            return {}
        
        # Get final state
        final_props = keyframes[-1]['props']
        
        # Build transition
        total_duration = keyframes[-1]['time']
        easing = keyframes[-1].get('easing', 'easeInOut')
        
        return {
            'animate': final_props,
            'transition': {
                'duration': total_duration / 1000,  # Convert to seconds
                'ease': easing
            }
        }
    
    def get_professor_action_at_time(
        self,
        professor_actions: List[Dict[str, Any]],
        current_time_ms: int
    ) -> Optional[Dict[str, Any]]:
        """Get active professor action at given time"""
        for action in professor_actions:
            start = action.get('time', 0)
            duration = action.get('duration_ms', 1000)
            end = start + duration
            
            if start <= current_time_ms <= end:
                return action
        
        return None

