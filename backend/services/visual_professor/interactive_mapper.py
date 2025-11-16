"""
Interactive Mapper - Maps Interactive Controls to Concept Parameters
Creates sliders, toggles, selectors for each concept
Defines how interactive controls affect visual entities
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# INTERACTIVE CONTROL MAPPER
# ============================================================================

class InteractiveMapper:
    """
    Maps interactive controls to concept parameters
    Defines sliders, toggles, selectors for each concept and subject
    """
    
    def __init__(self):
        self.concept_controls_map = self._build_concept_controls_map()
    
    def _build_concept_controls_map(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive map of controls for all concepts"""
        return {
            # Physics concepts
            'velocity': {
                'sliders': [
                    {
                        'id': 'speed',
                        'label': 'Speed (km/h)',
                        'label_hinglish': 'Raftar (km/h)',
                        'min': 0,
                        'max': 120,
                        'default': 60,
                        'step': 5,
                        'unit': 'km/h',
                        'affects': ['metro_train', 'speedometer'],
                        'update_function': 'update_speed'
                    },
                    {
                        'id': 'direction',
                        'label': 'Direction (degrees)',
                        'label_hinglish': 'Disha (degrees)',
                        'min': 0,
                        'max': 360,
                        'default': 0,
                        'step': 15,
                        'unit': '°',
                        'affects': ['direction_arrow', 'metro_train'],
                        'update_function': 'update_direction'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_vectors',
                        'label': 'Show Velocity Vectors',
                        'label_hinglish': 'Vectors Dikhao',
                        'default': False,
                        'affects': ['velocity_vectors']
                    }
                ],
                'buttons': [
                    {
                        'id': 'reset',
                        'label': 'Reset',
                        'label_hinglish': 'Phir Se',
                        'action': 'reset_animation'
                    }
                ]
            },
            
            'projectile': {
                'sliders': [
                    {
                        'id': 'launch_angle',
                        'label': 'Launch Angle (degrees)',
                        'label_hinglish': 'Phenke Ka Angle',
                        'min': 15,
                        'max': 75,
                        'default': 45,
                        'step': 5,
                        'unit': '°',
                        'affects': ['cricket_ball', 'trajectory_arc'],
                        'update_function': 'update_projectile_path'
                    },
                    {
                        'id': 'launch_speed',
                        'label': 'Launch Speed (m/s)',
                        'label_hinglish': 'Raftar (m/s)',
                        'min': 10,
                        'max': 50,
                        'default': 30,
                        'step': 2,
                        'unit': 'm/s',
                        'affects': ['cricket_ball', 'trajectory_arc'],
                        'update_function': 'update_projectile_path'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_components',
                        'label': 'Show Velocity Components',
                        'label_hinglish': 'Components Dikhao',
                        'default': False,
                        'affects': ['velocity_vectors']
                    }
                ]
            },
            
            'newton_first': {
                'toggles': [
                    {
                        'id': 'friction',
                        'label': 'Friction On/Off',
                        'label_hinglish': 'Friction On/Off',
                        'default': True,
                        'affects': ['friction_arrows', 'car_motion']
                    }
                ],
                'buttons': [
                    {
                        'id': 'apply_brakes',
                        'label': 'Apply Brakes',
                        'label_hinglish': 'Brake Lagao',
                        'action': 'trigger_braking'
                    }
                ]
            },
            
            # Chemistry concepts
            'valency': {
                'selectors': [
                    {
                        'id': 'element',
                        'label': 'Select Element',
                        'label_hinglish': 'Element Chuniye',
                        'options': [
                            {'value': 'H', 'label': 'Hydrogen (H)', 'valency': 1},
                            {'value': 'C', 'label': 'Carbon (C)', 'valency': 4},
                            {'value': 'N', 'label': 'Nitrogen (N)', 'valency': 3},
                            {'value': 'O', 'label': 'Oxygen (O)', 'valency': 2},
                            {'value': 'Na', 'label': 'Sodium (Na)', 'valency': 1},
                            {'value': 'Cl', 'label': 'Chlorine (Cl)', 'valency': 1}
                        ],
                        'default': 'C',
                        'affects': ['atom_nucleus', 'electron_shells', 'electrons'],
                        'update_function': 'update_element'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_electrons',
                        'label': 'Show Electrons',
                        'label_hinglish': 'Electrons Dikhao',
                        'default': True,
                        'affects': ['electrons']
                    },
                    {
                        'id': 'show_valency',
                        'label': 'Show Valency Number',
                        'label_hinglish': 'Valency Number Dikhao',
                        'default': True,
                        'affects': ['valency_label']
                    }
                ]
            },
            
            'acids_strength': {
                'sliders': [
                    {
                        'id': 'ph',
                        'label': 'pH Level',
                        'label_hinglish': 'pH Level',
                        'min': 0,
                        'max': 7,
                        'default': 3,
                        'step': 0.5,
                        'unit': 'pH',
                        'affects': ['ph_scale', 'indicator_paper', 'color_gradient'],
                        'update_function': 'update_ph_level'
                    }
                ],
                'selectors': [
                    {
                        'id': 'acid_type',
                        'label': 'Acid Type',
                        'label_hinglish': 'Acid Ka Type',
                        'options': [
                            {'value': 'HCl', 'label': 'Hydrochloric Acid (HCl)', 'ph': 1},
                            {'value': 'H2SO4', 'label': 'Sulfuric Acid (H₂SO₄)', 'ph': 0.5},
                            {'value': 'Acetic', 'label': 'Acetic Acid (Vinegar)', 'ph': 3},
                            {'value': 'Citric', 'label': 'Citric Acid (Lemon)', 'ph': 2}
                        ],
                        'default': 'Acetic',
                        'affects': ['test_tubes', 'ph_scale'],
                        'update_function': 'update_acid_type'
                    }
                ]
            },
            
            'bonding': {
                'selectors': [
                    {
                        'id': 'bond_type',
                        'label': 'Bond Type',
                        'label_hinglish': 'Bond Ka Type',
                        'options': [
                            {'value': 'single', 'label': 'Single Bond (—)', 'electrons': 2},
                            {'value': 'double', 'label': 'Double Bond (=)', 'electrons': 4},
                            {'value': 'triple', 'label': 'Triple Bond (≡)', 'electrons': 6}
                        ],
                        'default': 'single',
                        'affects': ['bond_line', 'shared_electrons'],
                        'update_function': 'update_bond_type'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_electron_cloud',
                        'label': 'Show Electron Cloud',
                        'label_hinglish': 'Electron Cloud Dikhao',
                        'default': True,
                        'affects': ['electron_cloud']
                    }
                ]
            },
            
            # Biology concepts
            'photosynthesis': {
                'selectors': [
                    {
                        'id': 'light_intensity',
                        'label': 'Sunlight Intensity',
                        'label_hinglish': 'Dhoop Ki Taqat',
                        'options': [
                            {'value': 'low', 'label': 'Low (Cloudy)', 'rate': 0.3},
                            {'value': 'medium', 'label': 'Medium (Normal)', 'rate': 1.0},
                            {'value': 'high', 'label': 'High (Bright Sun)', 'rate': 1.5}
                        ],
                        'default': 'medium',
                        'affects': ['sunlight_rays', 'chloroplast', 'reaction_rate'],
                        'update_function': 'update_light_intensity'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_co2',
                        'label': 'Show CO₂ Flow',
                        'label_hinglish': 'CO₂ Flow Dikhao',
                        'default': True,
                        'affects': ['co2_molecules']
                    },
                    {
                        'id': 'show_water',
                        'label': 'Show H₂O Flow',
                        'label_hinglish': 'Pani Flow Dikhao',
                        'default': True,
                        'affects': ['water_molecules']
                    }
                ]
            },
            
            'respiration': {
                'sliders': [
                    {
                        'id': 'oxygen_level',
                        'label': 'Oxygen Level (%)',
                        'label_hinglish': 'Oxygen Level (%)',
                        'min': 0,
                        'max': 100,
                        'default': 21,
                        'step': 5,
                        'unit': '%',
                        'affects': ['oxygen_molecules', 'atp_energy', 'respiration_rate'],
                        'update_function': 'update_oxygen_level'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_atp',
                        'label': 'Show ATP Production',
                        'label_hinglish': 'ATP Production Dikhao',
                        'default': True,
                        'affects': ['atp_energy']
                    }
                ]
            },
            
            # Math concepts
            'quadratic': {
                'sliders': [
                    {
                        'id': 'a_value',
                        'label': 'Coefficient a',
                        'label_hinglish': 'a Ki Value',
                        'min': -5,
                        'max': 5,
                        'default': 1,
                        'step': 0.5,
                        'unit': '',
                        'affects': ['parabola_curve'],
                        'update_function': 'update_parabola'
                    },
                    {
                        'id': 'b_value',
                        'label': 'Coefficient b',
                        'label_hinglish': 'b Ki Value',
                        'min': -10,
                        'max': 10,
                        'default': 0,
                        'step': 1,
                        'unit': '',
                        'affects': ['parabola_curve'],
                        'update_function': 'update_parabola'
                    },
                    {
                        'id': 'c_value',
                        'label': 'Coefficient c',
                        'label_hinglish': 'c Ki Value',
                        'min': -10,
                        'max': 10,
                        'default': 0,
                        'step': 1,
                        'unit': '',
                        'affects': ['parabola_curve'],
                        'update_function': 'update_parabola'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_vertex',
                        'label': 'Show Vertex',
                        'label_hinglish': 'Vertex Dikhao',
                        'default': True,
                        'affects': ['vertex_point']
                    },
                    {
                        'id': 'show_roots',
                        'label': 'Show Roots',
                        'label_hinglish': 'Roots Dikhao',
                        'default': True,
                        'affects': ['roots']
                    }
                ]
            },
            
            'linear': {
                'sliders': [
                    {
                        'id': 'slope',
                        'label': 'Slope (m)',
                        'label_hinglish': 'Slope (m)',
                        'min': -5,
                        'max': 5,
                        'default': 1,
                        'step': 0.5,
                        'unit': '',
                        'affects': ['line', 'slope_triangle'],
                        'update_function': 'update_line'
                    },
                    {
                        'id': 'y_intercept',
                        'label': 'Y-Intercept (b)',
                        'label_hinglish': 'Y-Intercept (b)',
                        'min': -10,
                        'max': 10,
                        'default': 0,
                        'step': 1,
                        'unit': '',
                        'affects': ['line', 'y_intercept_point'],
                        'update_function': 'update_line'
                    }
                ],
                'toggles': [
                    {
                        'id': 'show_slope_triangle',
                        'label': 'Show Slope Triangle',
                        'label_hinglish': 'Slope Triangle Dikhao',
                        'default': True,
                        'affects': ['slope_triangle']
                    }
                ]
            }
        }
    
    def map_interactions(
        self,
        concept: str,
        concept_type: str,
        difficulty: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Map interactive controls for a concept
        
        Args:
            concept: Concept name
            concept_type: Type of concept (comparison, process, etc.)
            difficulty: Difficulty level
            
        Returns:
            Dictionary with sliders, toggles, selectors, buttons
        """
        concept_lower = concept.lower()
        
        # Get concept-specific controls
        controls = self.concept_controls_map.get(concept_lower)
        
        if controls:
            logger.info(f"✅ Mapped {len(controls.get('sliders', []))} sliders and {len(controls.get('toggles', []))} toggles for {concept}")
            return controls
        
        # Fallback: Generate generic controls based on concept type
        return self._generate_generic_controls(concept, concept_type, difficulty)
    
    def _generate_generic_controls(
        self,
        concept: str,
        concept_type: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate generic controls when concept-specific not available"""
        controls = {'sliders': [], 'toggles': [], 'buttons': []}
        
        # Add generic toggle for complexity
        controls['toggles'].append({
            'id': 'show_details',
            'label': 'Show Detailed View',
            'label_hinglish': 'Details Dikhao',
            'default': False,
            'affects': ['detail_layer']
        })
        
        # For comparison concepts
        if concept_type == 'comparison':
            controls['toggles'].extend([
                {
                    'id': 'side_by_side',
                    'label': 'Side-by-Side View',
                    'label_hinglish': 'Side-by-Side Dikhao',
                    'default': True,
                    'affects': ['layout']
                }
            ])
        
        # For process concepts
        elif concept_type == 'process':
            controls['buttons'].append({
                'id': 'play_steps',
                'label': 'Play Step-by-Step',
                'label_hinglish': 'Step-by-Step Chalo',
                'action': 'play_process_animation'
            })
        
        return controls
    
    def get_control_update_function(
        self,
        concept: str,
        control_id: str
    ) -> Optional[str]:
        """Get the update function name for a control"""
        concept_controls = self.concept_controls_map.get(concept.lower(), {})
        
        # Search in sliders
        for slider in concept_controls.get('sliders', []):
            if slider['id'] == control_id:
                return slider.get('update_function')
        
        # Search in selectors
        for selector in concept_controls.get('selectors', []):
            if selector['id'] == control_id:
                return selector.get('update_function')
        
        return None
    
    def get_affected_entities(
        self,
        concept: str,
        control_id: str
    ) -> List[str]:
        """Get list of entities affected by a control"""
        concept_controls = self.concept_controls_map.get(concept.lower(), {})
        
        # Search all control types
        for control_type in ['sliders', 'toggles', 'selectors']:
            for control in concept_controls.get(control_type, []):
                if control['id'] == control_id:
                    return control.get('affects', [])
        
        return []
    
    def generate_control_hints(
        self,
        concept: str,
        control_id: str
    ) -> str:
        """Generate helpful hint text for a control"""
        hints_map = {
            'speed': "Increase to see faster motion",
            'direction': "Change to see velocity direction change",
            'launch_angle': "45° gives maximum range!",
            'ph': "Lower pH = stronger acid",
            'element': "Each element has different valency",
            'slope': "Steeper slope = faster change",
            'light_intensity': "More light = faster photosynthesis"
        }
        return hints_map.get(control_id, "Adjust to see the effect")

