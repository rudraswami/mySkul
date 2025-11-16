"""
Scene Generation Engine - Generates Complete Animated Scene Specifications
Creates full scene specs with entities, actions, timeline, interactivity
Supports all subjects: Physics, Chemistry, Biology, Mathematics
"""
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# ============================================================================
# SCENE TYPES AND CONFIGURATIONS
# ============================================================================

SCENE_BACKGROUNDS = {
    # Physics scenes
    'urban_metro_station': {
        'layers': ['sky_blue', 'buildings_silhouette', 'platform_floor', 'tracks'],
        'colors': {'sky': '#87CEEB', 'buildings': '#6B7280', 'platform': '#9CA3AF', 'tracks': '#374151'},
        'ambient': 'urban',
        'time_of_day': 'day'
    },
    'cricket_stadium': {
        'layers': ['sky', 'stadium_stands', 'field_grass', 'pitch'],
        'colors': {'sky': '#60A5FA', 'stands': '#4B5563', 'grass': '#22C55E', 'pitch': '#D4A574'},
        'ambient': 'sports',
        'time_of_day': 'day'
    },
    'highway_road': {
        'layers': ['sky', 'hills_background', 'road_asphalt', 'lane_markings'],
        'colors': {'sky': '#93C5FD', 'hills': '#86EFAC', 'road': '#1F2937', 'markings': '#FCD34D'},
        'ambient': 'outdoor',
        'time_of_day': 'day'
    },
    
    # Chemistry scenes
    'electron_shell_space': {
        'layers': ['space_void', 'atom_glow', 'orbital_paths'],
        'colors': {'space': '#1E1B4B', 'glow': '#8B5CF6', 'orbits': '#A78BFA'},
        'ambient': 'molecular',
        'zoom_level': 'atomic'
    },
    'laboratory_bench': {
        'layers': ['wall', 'bench_surface', 'equipment_shelf'],
        'colors': {'wall': '#F3F4F6', 'bench': '#9CA3AF', 'shelf': '#6B7280'},
        'ambient': 'lab',
        'lighting': 'fluorescent'
    },
    
    # Biology scenes
    'leaf_cross_section': {
        'layers': ['sky_background', 'leaf_exterior', 'cell_layers', 'chloroplasts'],
        'colors': {'sky': '#BFDBFE', 'leaf': '#22C55E', 'cells': '#86EFAC', 'chloroplasts': '#15803D'},
        'ambient': 'cellular',
        'zoom_level': 'microscopic'
    },
    
    # Math scenes
    'graph_coordinate_space': {
        'layers': ['grid_paper', 'axes', 'quadrants'],
        'colors': {'grid': '#F3F4F6', 'axes': '#374151', 'quadrants': '#E5E7EB'},
        'ambient': 'analytical',
        'grid_spacing': 20
    }
}

# ============================================================================
# SCENE GENERATION ENGINE
# ============================================================================

class SceneGenerationEngine:
    """
    Generates complete animated scene specifications
    Returns scene with entities, actions, timeline, and interactivity
    """
    
    def __init__(self):
        self.backgrounds = SCENE_BACKGROUNDS
    
    def generate_scene(
        self,
        concept: str,
        metaphor: Any,  # SelectedMetaphor
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate complete scene specification for a stage
        
        Args:
            concept: Concept name
            metaphor: Selected metaphor with scene and entities
            stage_index: Current stage index
            stage_data: Stage data from concept library
            
        Returns:
            Complete scene specification with all animation data
        """
        scene_id = metaphor.scene if hasattr(metaphor, 'scene') else metaphor.get('scene', 'generic')
        
        # Get subject from concept or stage data
        subject = stage_data.get('subject', self._infer_subject(concept))
        
        # Generate scene based on subject
        if subject in ['physics', 'Physics']:
            return self.generate_physics_scene(concept, metaphor, stage_index, stage_data)
        elif subject in ['chemistry', 'Chemistry']:
            return self.generate_chemistry_scene(concept, metaphor, stage_index, stage_data)
        elif subject in ['biology', 'Biology']:
            return self.generate_biology_scene(concept, metaphor, stage_index, stage_data)
        elif subject in ['mathematics', 'Mathematics', 'math', 'Math']:
            return self.generate_math_scene(concept, metaphor, stage_index, stage_data)
        else:
            return self.generate_generic_scene(concept, metaphor, stage_index, stage_data)
    
    def generate_physics_scene(
        self,
        concept: str,
        metaphor: Any,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate physics-specific scenes with motion, forces, vectors"""
        scene_name = metaphor.scene if hasattr(metaphor, 'scene') else metaphor.get('scene', 'generic')
        background = self.backgrounds.get(scene_name, self.backgrounds.get('highway_road', {}))
        
        # Get entities from SELECTED METAPHOR (not concept library!)
        entities_list = metaphor.entities if hasattr(metaphor, 'entities') else metaphor.get('entities', [])
        
        logger.info(f"🎨 Using metaphor entities: {entities_list} from metaphor {scene_name}")
        
        # Build entities with positions and animations
        entities = []
        for i, entity_id in enumerate(entities_list):
            entity_spec = self._build_physics_entity(
                entity_id,
                stage_index,
                i,
                stage_data
            )
            entities.append(entity_spec)
        
        logger.info(f"🎨 Built {len(entities)} entities for scene {scene_name}")
        
        # Build actions (movements, transformations)
        actions = self._build_physics_actions(concept, entities, stage_index, stage_data)
        
        # Build timeline
        timeline = self._build_timeline(actions, stage_data.get('duration_ms', 3000))
        
        # Build interactivity
        interactivity = self._build_physics_interactivity(concept)
        
        scene_result = {
            'scene_type': 'motion',
            'scene_id': scene_name,
            'background': background,
            'entities': entities,
            'actions': actions,
            'timeline': timeline,
            'interactivity': interactivity,
            'narration': {
                'professor_script': stage_data.get('narration', ''),
                'timing': [0, len(actions) * 500, stage_data.get('duration_ms', 3000) - 500]
            }
        }
        
        logger.info(f"🎬 Scene generated: {scene_name}, {len(entities)} entities, {len(actions)} actions")
        logger.info(f"   Entity IDs: {[e['id'] for e in entities]}")
        
        return scene_result
    
    def generate_chemistry_scene(
        self,
        concept: str,
        metaphor: Any,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate chemistry scenes with atoms, bonds, reactions"""
        scene_name = metaphor.scene if hasattr(metaphor, 'scene') else metaphor.get('scene', 'generic')
        background = self.backgrounds.get(scene_name, self.backgrounds.get('laboratory_bench', {}))
        
        entities_list = metaphor.entities if hasattr(metaphor, 'entities') else metaphor.get('entities', [])
        
        entities = []
        for i, entity_id in enumerate(entities_list):
            entity_spec = self._build_chemistry_entity(
                entity_id,
                stage_index,
                i,
                stage_data
            )
            entities.append(entity_spec)
        
        actions = self._build_chemistry_actions(concept, entities, stage_index, stage_data)
        timeline = self._build_timeline(actions, stage_data.get('duration_ms', 3000))
        interactivity = self._build_chemistry_interactivity(concept)
        
        return {
            'scene_type': 'bonding',
            'scene_id': scene_name,
            'background': background,
            'entities': entities,
            'actions': actions,
            'timeline': timeline,
            'interactivity': interactivity,
            'narration': {
                'professor_script': stage_data.get('narration', ''),
                'timing': [0, len(actions) * 500, stage_data.get('duration_ms', 3000) - 500]
            }
        }
    
    def generate_biology_scene(
        self,
        concept: str,
        metaphor: Any,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate biology scenes with cells, processes, systems"""
        scene_name = metaphor.scene if hasattr(metaphor, 'scene') else metaphor.get('scene', 'generic')
        background = self.backgrounds.get(scene_name, self.backgrounds.get('leaf_cross_section', {}))
        
        entities_list = metaphor.entities if hasattr(metaphor, 'entities') else metaphor.get('entities', [])
        
        entities = []
        for i, entity_id in enumerate(entities_list):
            entity_spec = self._build_biology_entity(
                entity_id,
                stage_index,
                i,
                stage_data
            )
            entities.append(entity_spec)
        
        actions = self._build_biology_actions(concept, entities, stage_index, stage_data)
        timeline = self._build_timeline(actions, stage_data.get('duration_ms', 3000))
        interactivity = self._build_biology_interactivity(concept)
        
        return {
            'scene_type': 'process',
            'scene_id': scene_name,
            'background': background,
            'entities': entities,
            'actions': actions,
            'timeline': timeline,
            'interactivity': interactivity,
            'narration': {
                'professor_script': stage_data.get('narration', ''),
                'timing': [0, len(actions) * 500, stage_data.get('duration_ms', 3000) - 500]
            }
        }
    
    def generate_math_scene(
        self,
        concept: str,
        metaphor: Any,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate math scenes with graphs, shapes, transformations"""
        scene_name = metaphor.scene if hasattr(metaphor, 'scene') else metaphor.get('scene', 'generic')
        background = self.backgrounds.get(scene_name, self.backgrounds.get('graph_coordinate_space', {}))
        
        entities_list = metaphor.entities if hasattr(metaphor, 'entities') else metaphor.get('entities', [])
        
        entities = []
        for i, entity_id in enumerate(entities_list):
            entity_spec = self._build_math_entity(
                entity_id,
                stage_index,
                i,
                stage_data
            )
            entities.append(entity_spec)
        
        actions = self._build_math_actions(concept, entities, stage_index, stage_data)
        timeline = self._build_timeline(actions, stage_data.get('duration_ms', 3000))
        interactivity = self._build_math_interactivity(concept)
        
        return {
            'scene_type': 'graph',
            'scene_id': scene_name,
            'background': background,
            'entities': entities,
            'actions': actions,
            'timeline': timeline,
            'interactivity': interactivity,
            'narration': {
                'professor_script': stage_data.get('narration', ''),
                'timing': [0, len(actions) * 500, stage_data.get('duration_ms', 3000) - 500]
            }
        }
    
    def generate_generic_scene(
        self,
        concept: str,
        metaphor: Any,
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate generic scene fallback"""
        return {
            'scene_type': 'generic',
            'scene_id': 'chalkboard',
            'background': {'layers': ['chalkboard'], 'colors': {'chalkboard': '#1F2937'}},
            'entities': [],
            'actions': [],
            'timeline': {'total_duration_ms': stage_data.get('duration_ms', 3000)},
            'interactivity': {'controls': []},
            'narration': {
                'professor_script': stage_data.get('narration', ''),
                'timing': [0]
            }
        }
    
    # ========================================================================
    # ENTITY BUILDERS BY SUBJECT
    # ========================================================================
    
    def _build_physics_entity(
        self,
        entity_id: str,
        stage_index: int,
        entity_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build physics entity specification"""
        # Position based on entity type and index (spread them out!)
        position = self._calculate_entity_position(entity_id, stage_index, entity_index)
        
        # FORCE ALL ENTITIES VISIBLE (for debugging - shows all 5 entities)
        # In production, respect entities_visible from stage_data
        entities_visible = stage_data.get('entities_visible', [])
        is_visible = True  # ALWAYS visible for now
        
        # Check if entity is highlighted
        highlight = stage_data.get('highlight')
        is_highlighted = entity_id == highlight
        
        # Calculate position to spread entities across screen
        # Instead of using default position, spread them horizontally
        spread_position = {
            'x': 150 + (entity_index * 130),  # Spread across width
            'y': 200  # Same height
        }
        
        return {
            'id': entity_id,
            'type': self._get_entity_type(entity_id),
            'svg_component': self._map_entity_to_component(entity_id),
            'initial_position': spread_position,  # Use spread position
            'size': self._get_entity_size(entity_id),
            'visible': is_visible,  # ALL visible
            'highlighted': is_highlighted,
            'interactive': entity_id in ['speedometer', 'direction_arrow'],
            'animations': self._get_entity_animations(entity_id, stage_index),
            'props': self._get_entity_props(entity_id)
        }
    
    def _build_chemistry_entity(
        self,
        entity_id: str,
        stage_index: int,
        entity_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build chemistry entity specification"""
        highlight = stage_data.get('highlight')
        
        # Spread entities across screen
        spread_position = {
            'x': 150 + (entity_index * 130),
            'y': 220
        }
        
        return {
            'id': entity_id,
            'type': self._get_entity_type(entity_id),
            'svg_component': self._map_entity_to_component(entity_id),
            'initial_position': spread_position,
            'size': self._get_entity_size(entity_id),
            'visible': True,  # ALL visible
            'highlighted': entity_id == highlight,
            'interactive': entity_id in ['electron_shells', 'bonding_hand'],
            'animations': self._get_entity_animations(entity_id, stage_index),
            'props': self._get_entity_props(entity_id)
        }
    
    def _build_biology_entity(
        self,
        entity_id: str,
        stage_index: int,
        entity_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build biology entity specification"""
        highlight = stage_data.get('highlight')
        
        spread_position = {
            'x': 150 + (entity_index * 130),
            'y': 220
        }
        
        return {
            'id': entity_id,
            'type': self._get_entity_type(entity_id),
            'svg_component': self._map_entity_to_component(entity_id),
            'initial_position': spread_position,
            'size': self._get_entity_size(entity_id),
            'visible': True,  # ALL visible
            'highlighted': entity_id == highlight,
            'interactive': entity_id in ['chloroplast', 'mitochondria'],
            'animations': self._get_entity_animations(entity_id, stage_index),
            'props': self._get_entity_props(entity_id)
        }
    
    def _build_math_entity(
        self,
        entity_id: str,
        stage_index: int,
        entity_index: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build math entity specification"""
        highlight = stage_data.get('highlight')
        
        spread_position = {
            'x': 150 + (entity_index * 130),
            'y': 220
        }
        
        return {
            'id': entity_id,
            'type': self._get_entity_type(entity_id),
            'svg_component': self._map_entity_to_component(entity_id),
            'initial_position': spread_position,
            'size': self._get_entity_size(entity_id),
            'visible': True,  # ALL visible
            'highlighted': entity_id == highlight,
            'interactive': entity_id in ['parabola_curve', 'line', 'vertex_point'],
            'animations': self._get_entity_animations(entity_id, stage_index),
            'props': self._get_entity_props(entity_id)
        }
    
    # ========================================================================
    # ACTION BUILDERS BY SUBJECT
    # ========================================================================
    
    def _build_physics_actions(
        self,
        concept: str,
        entities: List[Dict[str, Any]],
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build physics animation actions - MUST GENERATE FOR ALL STAGES!"""
        actions = []
        animation_name = stage_data.get('animation', '')
        concept_lower = concept.lower()
        
        # CRITICAL: Generate actions for ALL visible entities, not just specific concepts
        entities_visible = stage_data.get('entities_visible', [])
        highlight = stage_data.get('highlight')
        
        # STEP 1: Fade in all visible entities
        for i, entity_id in enumerate(entities_visible):
            actions.append({
                'action': 'fade_in',
                'entity': entity_id,
                'duration_ms': 800,
                'start_time': i * 150
            })
        
        # STEP 2: Concept-specific animations (works for ANY metaphor!)
        if 'velocity' in concept_lower:
            # Find the main moving object (metro_train, cricket_ball, car, etc.)
            moving_entity = None
            for entity in entities:
                if any(keyword in entity['id'] for keyword in ['train', 'ball', 'car', 'auto', 'cycle']):
                    moving_entity = entity['id']
                    break
            
            # Find direction indicator
            direction_entity = None
            for entity in entities:
                if 'arrow' in entity['id'] or 'direction' in entity['id']:
                    direction_entity = entity['id']
                    break
            
            # Find speed indicator
            speed_entity = None
            for entity in entities:
                if 'speed' in entity['id'] or 'meter' in entity['id'] or 'gun' in entity['id']:
                    speed_entity = entity['id']
                    break
            
            # Velocity animations (generic - works for any metaphor!)
            if stage_index == 0 and moving_entity:  # Intro - object appears
                actions.append({
                    'action': 'move',
                    'entity': moving_entity,
                    'from': {'x': -50, 'y': 250},
                    'to': {'x': 150, 'y': 250},
                    'duration_ms': 1500,
                    'easing': 'easeOut',
                    'start_time': 800
                })
            elif stage_index == 1 and moving_entity:  # Speed demo - object moves fast
                actions.append({
                    'action': 'move',
                    'entity': moving_entity,
                    'from': {'x': 150, 'y': 250},
                    'to': {'x': 650, 'y': 250},
                    'duration_ms': 2500,
                    'easing': 'linear',
                    'start_time': 1000
                })
                if speed_entity:
                    actions.append({
                        'action': 'pulse',
                        'entity': speed_entity,
                        'duration_ms': 800,
                        'start_time': 2000,
                        'loop': True
                    })
            elif stage_index == 2 and moving_entity:  # Direction change
                if direction_entity:
                    actions.append({
                        'action': 'rotate',
                        'entity': direction_entity,
                        'from': {'rotation': 0},
                        'to': {'rotation': 180},
                        'duration_ms': 1200,
                        'easing': 'easeInOut',
                        'start_time': 800
                    })
                # Object moves in opposite direction
                actions.append({
                    'action': 'move',
                    'entity': moving_entity,
                    'from': {'x': 650, 'y': 250},
                    'to': {'x': 150, 'y': 250},
                    'duration_ms': 2500,
                    'easing': 'linear',
                    'start_time': 2200
                })
            elif stage_index == 3 and direction_entity:  # Vector display
                actions.append({
                    'action': 'pulse',
                    'entity': direction_entity,
                    'duration_ms': 1000,
                    'start_time': 800,
                    'loop': True
                })
        
        elif 'projectile' in concept_lower:
            if stage_index == 2:  # Ball flight
                if 'cricket_ball' in entities_visible:
                    actions.append({
                        'action': 'path',
                        'entity': 'cricket_ball',
                        'path_type': 'parabolic',
                        'from': {'x': 100, 'y': 500},
                        'control': {'x': 400, 'y': 200},
                        'to': {'x': 700, 'y': 500},
                        'duration_ms': 4000,
                        'easing': 'linear',
                        'start_time': 500
                    })
                if 'trajectory_arc' in entities_visible:
                    actions.append({
                        'action': 'draw_path',
                        'entity': 'trajectory_arc',
                        'duration_ms': 4000,
                        'start_time': 500
                    })
        
        elif 'newton' in concept_lower:
            if stage_index == 2:  # Car moving
                if 'car' in entities_visible:
                    actions.append({
                        'action': 'move',
                        'entity': 'car',
                        'from': {'x': 100, 'y': 450},
                        'to': {'x': 600, 'y': 450},
                        'duration_ms': 3500,
                        'easing': 'linear',
                        'start_time': 500
                    })
            elif stage_index == 3:  # Braking
                if 'car' in entities_visible:
                    actions.append({
                        'action': 'move',
                        'entity': 'car',
                        'from': {'x': 600, 'y': 450},
                        'to': {'x': 650, 'y': 450},
                        'duration_ms': 1500,
                        'easing': 'easeOut',
                        'start_time': 500
                    })
                if 'friction_arrows' in entities_visible:
                    actions.append({
                        'action': 'glow',
                        'entity': 'friction_arrows',
                        'intensity': 'high',
                        'duration_ms': 2000,
                        'start_time': 1000
                    })
        
        # STEP 3: Highlight entity if specified
        if highlight and highlight in entities_visible:
            actions.append({
                'action': 'glow',
                'entity': highlight,
                'intensity': 'medium',
                'duration_ms': 1500,
                'start_time': len(entities_visible) * 150 + 1000
            })
        
        # STEP 4: Generic animation if no actions created yet
        if len(actions) == 0 and len(entities_visible) > 0:
            # At minimum, fade in the first entity
            logger.warning(f"⚠️ No specific actions for {concept} stage {stage_index}, using generic fade-in")
            for i, entity_id in enumerate(entities_visible[:3]):  # Limit to first 3
                actions.append({
                    'action': 'fade_in',
                    'entity': entity_id,
                    'duration_ms': 1000,
                    'start_time': i * 300
                })
        
        logger.info(f"✅ Generated {len(actions)} actions for {concept} stage {stage_index}")
        logger.info(f"   Actions: {[a['action'] + '_' + a['entity'] for a in actions]}")
        return actions
    
    def _build_chemistry_actions(
        self,
        concept: str,
        entities: List[Dict[str, Any]],
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build chemistry animation actions - ALWAYS GENERATE!"""
        actions = []
        concept_lower = concept.lower()
        entities_visible = stage_data.get('entities_visible', [])
        highlight = stage_data.get('highlight')
        
        # Fade in all visible entities
        for i, entity_id in enumerate(entities_visible):
            actions.append({
                'action': 'fade_in',
                'entity': entity_id,
                'duration_ms': 800,
                'start_time': i * 150
            })
        
        if 'valency' in concept_lower:
            if stage_index == 1 and 'electrons' in entities_visible:  # Electron shells
                actions.append({
                    'action': 'orbit',
                    'entity': 'electrons',
                    'duration_ms': 2000,
                    'start_time': 1000,
                    'loop': True
                })
            elif stage_index == 2 and 'empty_slots' in entities_visible:  # Octet rule
                actions.append({
                    'action': 'pulse',
                    'entity': 'empty_slots',
                    'duration_ms': 1000,
                    'start_time': 1500,
                    'loop': True
                })
        
        elif 'bonding' in concept_lower or 'bond' in concept_lower:
            if stage_index == 1:  # Electron sharing
                if 'atom_1' in entities_visible:
                    actions.append({
                        'action': 'move',
                        'entity': 'atom_1',
                        'from': {'x': 250, 'y': 300},
                        'to': {'x': 350, 'y': 300},
                        'duration_ms': 2000,
                        'start_time': 800
                    })
                if 'atom_2' in entities_visible:
                    actions.append({
                        'action': 'move',
                        'entity': 'atom_2',
                        'from': {'x': 550, 'y': 300},
                        'to': {'x': 450, 'y': 300},
                        'duration_ms': 2000,
                        'start_time': 800
                    })
        
        elif 'acid' in concept_lower:
            if 'acid_molecules' in entities_visible:
                actions.append({
                    'action': 'glow',
                    'entity': 'acid_molecules',
                    'intensity': 'medium',
                    'duration_ms': 1500,
                    'start_time': 1000
                })
        
        # Highlight if specified
        if highlight and highlight in entities_visible:
            actions.append({
                'action': 'glow',
                'entity': highlight,
                'intensity': 'high',
                'duration_ms': 1500,
                'start_time': len(entities_visible) * 150 + 800
            })
        
        logger.info(f"✅ Generated {len(actions)} chemistry actions for {concept} stage {stage_index}")
        return actions
    
    def _build_biology_actions(
        self,
        concept: str,
        entities: List[Dict[str, Any]],
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build biology animation actions - ALWAYS GENERATE!"""
        actions = []
        concept_lower = concept.lower()
        entities_visible = stage_data.get('entities_visible', [])
        highlight = stage_data.get('highlight')
        
        # Fade in all visible entities
        for i, entity_id in enumerate(entities_visible):
            actions.append({
                'action': 'fade_in',
                'entity': entity_id,
                'duration_ms': 800,
                'start_time': i * 150
            })
        
        if 'photosynthesis' in concept_lower:
            if stage_index == 1 and 'co2_molecules' in entities_visible:  # Inputs arrive
                actions.append({
                    'action': 'move',
                    'entity': 'co2_molecules',
                    'from': {'x': 700, 'y': 200},
                    'to': {'x': 400, 'y': 300},
                    'duration_ms': 2000,
                    'start_time': 800
                })
            if stage_index == 2 and 'chloroplast' in entities_visible:  # Reaction
                actions.append({
                    'action': 'glow',
                    'entity': 'chloroplast',
                    'intensity': 'high',
                    'duration_ms': 2000,
                    'start_time': 1000
                })
        
        elif 'respiration' in concept_lower:
            if stage_index == 1 and 'glucose_molecule' in entities_visible:
                actions.append({
                    'action': 'move',
                    'entity': 'glucose_molecule',
                    'from': {'x': 100, 'y': 200},
                    'to': {'x': 400, 'y': 300},
                    'duration_ms': 1500,
                    'start_time': 800
                })
        
        # Highlight
        if highlight and highlight in entities_visible:
            actions.append({
                'action': 'glow',
                'entity': highlight,
                'intensity': 'high',
                'duration_ms': 1500,
                'start_time': len(entities_visible) * 150 + 800
            })
        
        logger.info(f"✅ Generated {len(actions)} biology actions for {concept} stage {stage_index}")
        return actions
    
    def _build_math_actions(
        self,
        concept: str,
        entities: List[Dict[str, Any]],
        stage_index: int,
        stage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build math animation actions - ALWAYS GENERATE!"""
        actions = []
        concept_lower = concept.lower()
        entities_visible = stage_data.get('entities_visible', [])
        highlight = stage_data.get('highlight')
        
        # Fade in all visible entities
        for i, entity_id in enumerate(entities_visible):
            actions.append({
                'action': 'fade_in',
                'entity': entity_id,
                'duration_ms': 800,
                'start_time': i * 150
            })
        
        if 'quadratic' in concept_lower:
            if stage_index == 0 and 'parabola_curve' in entities_visible:  # Draw parabola
                actions.append({
                    'action': 'draw_curve',
                    'entity': 'parabola_curve',
                    'path_data': 'M 100 500 Q 400 100 700 500',
                    'duration_ms': 2500,
                    'start_time': 800
                })
            elif stage_index == 2 and 'vertex_point' in entities_visible:  # Vertex highlight
                actions.append({
                    'action': 'pulse',
                    'entity': 'vertex_point',
                    'duration_ms': 1000,
                    'start_time': 1000,
                    'loop': True
                })
        
        elif 'linear' in concept_lower:
            if stage_index == 0 and 'line' in entities_visible:  # Draw line
                actions.append({
                    'action': 'draw_line',
                    'entity': 'line',
                    'from': {'x': 100, 'y': 450},
                    'to': {'x': 700, 'y': 150},
                    'duration_ms': 2000,
                    'start_time': 800
                })
            elif stage_index == 1 and 'slope_triangle' in entities_visible:  # Show slope
                actions.append({
                    'action': 'fade_in',
                    'entity': 'slope_triangle',
                    'duration_ms': 1000,
                    'start_time': 1000
                })
        
        # Highlight
        if highlight and highlight in entities_visible:
            actions.append({
                'action': 'glow',
                'entity': highlight,
                'intensity': 'high',
                'duration_ms': 1500,
                'start_time': len(entities_visible) * 150 + 800
            })
        
        logger.info(f"✅ Generated {len(actions)} math actions for {concept} stage {stage_index}")
        return actions
    
    # ========================================================================
    # INTERACTIVITY BUILDERS BY SUBJECT
    # ========================================================================
    
    def _build_physics_interactivity(self, concept: str) -> Dict[str, Any]:
        """Build physics-specific interactive controls"""
        if concept.lower() == 'velocity':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'speed',
                        'label': 'Speed (km/h)',
                        'min': 0,
                        'max': 120,
                        'default': 60,
                        'step': 5,
                        'unit': 'km/h',
                        'affects': ['metro_train_velocity']
                    },
                    {
                        'type': 'slider',
                        'id': 'direction',
                        'label': 'Direction (degrees)',
                        'min': 0,
                        'max': 360,
                        'default': 0,
                        'step': 15,
                        'unit': '°',
                        'affects': ['direction_arrow_rotation']
                    },
                    {
                        'type': 'toggle',
                        'id': 'show_vectors',
                        'label': 'Show Velocity Vectors',
                        'default': False,
                        'affects': ['velocity_vectors_visibility']
                    }
                ]
            }
        elif concept.lower() == 'projectile':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'launch_angle',
                        'label': 'Launch Angle (degrees)',
                        'min': 15,
                        'max': 75,
                        'default': 45,
                        'step': 5,
                        'unit': '°',
                        'affects': ['trajectory_arc']
                    },
                    {
                        'type': 'slider',
                        'id': 'launch_speed',
                        'label': 'Launch Speed (m/s)',
                        'min': 10,
                        'max': 50,
                        'default': 30,
                        'step': 2,
                        'unit': 'm/s',
                        'affects': ['trajectory_arc']
                    }
                ]
            }
        else:
            return {'controls': []}
    
    def _build_chemistry_interactivity(self, concept: str) -> Dict[str, Any]:
        """Build chemistry-specific interactive controls"""
        if concept.lower() == 'valency':
            return {
                'controls': [
                    {
                        'type': 'selector',
                        'id': 'element',
                        'label': 'Select Element',
                        'options': ['H', 'C', 'N', 'O', 'Na', 'Cl'],
                        'default': 'C',
                        'affects': ['atom_nucleus', 'electron_shells']
                    },
                    {
                        'type': 'toggle',
                        'id': 'show_electrons',
                        'label': 'Show Electrons',
                        'default': True,
                        'affects': ['electrons_visibility']
                    }
                ]
            }
        elif concept.lower() == 'acids_strength':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'ph',
                        'label': 'pH Level',
                        'min': 0,
                        'max': 7,
                        'default': 3,
                        'step': 0.5,
                        'unit': 'pH',
                        'affects': ['ph_scale_indicator', 'indicator_paper_color']
                    }
                ]
            }
        else:
            return {'controls': []}
    
    def _build_biology_interactivity(self, concept: str) -> Dict[str, Any]:
        """Build biology-specific interactive controls"""
        if concept.lower() == 'photosynthesis':
            return {
                'controls': [
                    {
                        'type': 'toggle',
                        'id': 'light_intensity',
                        'label': 'Sunlight',
                        'options': ['Low', 'Medium', 'High'],
                        'default': 'Medium',
                        'affects': ['sunlight_rays_intensity']
                    }
                ]
            }
        elif concept.lower() == 'respiration':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'oxygen_level',
                        'label': 'Oxygen Level (%)',
                        'min': 0,
                        'max': 100,
                        'default': 21,
                        'step': 5,
                        'unit': '%',
                        'affects': ['respiration_rate']
                    }
                ]
            }
        else:
            return {'controls': []}
    
    def _build_math_interactivity(self, concept: str) -> Dict[str, Any]:
        """Build math-specific interactive controls"""
        if concept.lower() == 'quadratic':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'a_value',
                        'label': 'a (coefficient)',
                        'min': -5,
                        'max': 5,
                        'default': 1,
                        'step': 0.5,
                        'unit': '',
                        'affects': ['parabola_curve_shape']
                    },
                    {
                        'type': 'slider',
                        'id': 'b_value',
                        'label': 'b (coefficient)',
                        'min': -10,
                        'max': 10,
                        'default': 0,
                        'step': 1,
                        'unit': '',
                        'affects': ['parabola_curve_position']
                    }
                ]
            }
        elif concept.lower() == 'linear':
            return {
                'controls': [
                    {
                        'type': 'slider',
                        'id': 'slope',
                        'label': 'Slope (m)',
                        'min': -5,
                        'max': 5,
                        'default': 1,
                        'step': 0.5,
                        'unit': '',
                        'affects': ['line_angle']
                    },
                    {
                        'type': 'slider',
                        'id': 'y_intercept',
                        'label': 'Y-intercept (b)',
                        'min': -10,
                        'max': 10,
                        'default': 0,
                        'step': 1,
                        'unit': '',
                        'affects': ['line_position']
                    }
                ]
            }
        else:
            return {'controls': []}
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def _build_timeline(
        self,
        actions: List[Dict[str, Any]],
        total_duration_ms: int
    ) -> Dict[str, Any]:
        """Build timeline from actions"""
        # Sort actions by start_time
        sorted_actions = sorted(actions, key=lambda a: a.get('start_time', 0))
        
        # Build sync points (moments when professor should speak/point)
        sync_points = []
        for action in sorted_actions:
            if action.get('start_time', 0) > 0:
                sync_points.append({
                    'time': action['start_time'],
                    'action': action['action'],
                    'entity': action.get('entity')
                })
        
        return {
            'total_duration_ms': total_duration_ms,
            'actions': sorted_actions,
            'sync_points': sync_points,
            'transitions': [
                {'time': 0, 'type': 'fade_in'},
                {'time': total_duration_ms - 500, 'type': 'prepare_next'}
            ]
        }
    
    def _calculate_entity_position(
        self,
        entity_id: str,
        stage_index: int,
        entity_index: int
    ) -> Dict[str, int]:
        """Calculate entity position based on type and stage"""
        # Default positions by entity type
        default_positions = {
            'metro_train': {'x': 100, 'y': 400},
            'car': {'x': 100, 'y': 450},
            'cricket_ball': {'x': 100, 'y': 500},
            'direction_arrow': {'x': 400, 'y': 200},
            'speedometer': {'x': 650, 'y': 100},
            'atom_nucleus': {'x': 400, 'y': 300},
            'chloroplast': {'x': 400, 'y': 300},
            'mitochondria': {'x': 400, 'y': 300},
            'parabola_curve': {'x': 400, 'y': 300},
            'line': {'x': 100, 'y': 400}
        }
        
        return default_positions.get(entity_id, {'x': 400, 'y': 300})
    
    def _get_entity_type(self, entity_id: str) -> str:
        """Get entity type from ID"""
        type_map = {
            'metro_train': 'vehicle',
            'car': 'vehicle',
            'cricket_ball': 'projectile',
            'direction_arrow': 'indicator',
            'speedometer': 'gauge',
            'atom_nucleus': 'particle',
            'electron': 'particle',
            'chloroplast': 'organelle',
            'mitochondria': 'organelle',
            'parabola_curve': 'curve',
            'line': 'line'
        }
        return type_map.get(entity_id, 'generic')
    
    def _map_entity_to_component(self, entity_id: str) -> str:
        """Map entity ID to React component name"""
        component_map = {
            'metro_train': 'MetroTrainSVG',
            'car': 'CarSVG',
            'cricket_ball': 'CricketBallSVG',
            'direction_arrow': 'DirectionArrowSVG',
            'speedometer': 'SpeedometerSVG',
            'atom_nucleus': 'AtomNucleusSVG',
            'electron': 'ElectronSVG',
            'electron_shells': 'ElectronShellsSVG',
            'chloroplast': 'ChloroplastSVG',
            'mitochondria': 'MitochondriaSVG',
            'parabola_curve': 'ParabolaSVG',
            'line': 'LineSVG'
        }
        return component_map.get(entity_id, 'GenericEntitySVG')
    
    def _get_entity_size(self, entity_id: str) -> Dict[str, int]:
        """Get default size for entity"""
        size_map = {
            'metro_train': {'width': 120, 'height': 60},
            'car': {'width': 100, 'height': 50},
            'cricket_ball': {'width': 30, 'height': 30},
            'direction_arrow': {'width': 80, 'height': 80},
            'speedometer': {'width': 100, 'height': 100},
            'atom_nucleus': {'width': 60, 'height': 60},
            'chloroplast': {'width': 120, 'height': 80},
            'mitochondria': {'width': 200, 'height': 150}
        }
        return size_map.get(entity_id, {'width': 60, 'height': 60})
    
    def _get_entity_animations(self, entity_id: str, stage_index: int) -> List[str]:
        """Get available animations for entity"""
        return ['fade_in', 'fade_out', 'move', 'rotate', 'scale', 'pulse', 'glow']
    
    def _get_entity_props(self, entity_id: str) -> Dict[str, Any]:
        """Get entity-specific props (color, texture, etc.)"""
        if 'metro' in entity_id or 'train' in entity_id:
            return {'color': '#7c3aed', 'type': 'metro'}
        elif 'car' in entity_id:
            return {'color': '#3b82f6', 'type': 'sedan'}
        elif 'ball' in entity_id:
            return {'color': '#dc2626', 'sport': 'cricket'}
        elif 'atom' in entity_id:
            return {'element': 'C', 'color': '#10b981'}
        elif 'chloroplast' in entity_id:
            return {'color': '#22c55e', 'active': True}
        else:
            return {}
    
    def _infer_subject(self, concept: str) -> str:
        """Infer subject from concept name"""
        concept_lower = concept.lower()
        
        physics_keywords = ['velocity', 'speed', 'motion', 'force', 'energy', 'projectile', 'newton']
        chemistry_keywords = ['valency', 'bond', 'atom', 'molecule', 'acid', 'reaction']
        biology_keywords = ['photosynthesis', 'respiration', 'cell', 'mitochondria', 'chloroplast']
        math_keywords = ['quadratic', 'linear', 'equation', 'graph', 'parabola']
        
        if any(kw in concept_lower for kw in physics_keywords):
            return 'physics'
        elif any(kw in concept_lower for kw in chemistry_keywords):
            return 'chemistry'
        elif any(kw in concept_lower for kw in biology_keywords):
            return 'biology'
        elif any(kw in concept_lower for kw in math_keywords):
            return 'mathematics'
        else:
            return 'general'

