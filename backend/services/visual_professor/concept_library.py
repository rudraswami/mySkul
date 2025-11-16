"""
Concept Library - Real Educational Content for Visual Professor Engine
Contains complete teaching content for hero concepts across all subjects
Each concept has: scenes, entities, stages, narration, animations, interactions
"""
from typing import Dict, List, Any, Optional

# ============================================================================
# HERO CONCEPTS - COMPLETE EDUCATIONAL CONTENT
# ============================================================================

CONCEPT_LIBRARY: Dict[str, Dict[str, Any]] = {
    # ========================================================================
    # PHYSICS CONCEPTS
    # ========================================================================
    
    'velocity': {
        'subject': 'physics',
        'scene': 'delhi_metro_road',  # Default scene, overridden by metaphor
        'available_metaphors': ['delhi_metro', 'cricket_ball_bowling', 'auto_rickshaw_traffic', 'local_train_mumbai', 'river_flow', 'drone_delivery', 'cyclist_morning', 'bullet_train'],
        'preferred_metaphor': 'delhi_metro',
        'entities': ['metro_train', 'direction_arrow', 'speedometer', 'landmark_a', 'landmark_b'],
        'key_concept': 'Velocity = Speed + Direction',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Velocity is more than just speed - it's speed with direction. Imagine a metro train moving through Delhi.",
                'animation': 'metro_intro',
                'entities_visible': ['metro_train', 'landmark_a', 'landmark_b'],
                'highlight': 'metro_train',
                'emphasis': 'Direction is what makes velocity different from speed'
            },
            {
                'stage_id': 'speed_demo',
                'duration_ms': 3500,
                'narration': "If the metro moves at 60 km/h, that's its speed. But watch carefully - WHERE is it going?",
                'animation': 'metro_moves_north',
                'entities_visible': ['metro_train', 'speedometer', 'direction_arrow'],
                'highlight': 'speedometer',
                'interaction': {'type': 'hover', 'target': 'speedometer', 'description': 'Hover to see speed value'}
            },
            {
                'stage_id': 'direction_matters',
                'duration_ms': 4000,
                'narration': "Now the metro turns and moves SOUTH at the same 60 km/h. Same speed, but different velocity because direction changed!",
                'animation': 'metro_turns_south',
                'entities_visible': ['metro_train', 'speedometer', 'direction_arrow'],
                'highlight': 'direction_arrow',
                'emphasis': 'Velocity changed even though speed stayed the same'
            },
            {
                'stage_id': 'vector_concept',
                'duration_ms': 3000,
                'narration': "Velocity is a vector - it has both magnitude (speed) and direction. Speed is just magnitude.",
                'animation': 'vector_display',
                'entities_visible': ['direction_arrow', 'speedometer'],
                'interaction': {'type': 'slider', 'control': 'direction', 'range': [0, 360], 'description': 'Change direction to see velocity change'}
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Remember: Velocity = Speed + Direction. Two objects can have same speed but different velocities!",
                'animation': 'summary_comparison',
                'entities_visible': ['metro_train', 'direction_arrow', 'speedometer'],
                'emphasis': 'Always specify direction when talking about velocity'
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'speed', 'range': [0, 100], 'unit': 'km/h'},
            {'type': 'slider', 'control': 'direction', 'range': [0, 360], 'unit': 'degrees'}
        ],
        'real_world_examples': ['Metro trains', 'Cars on highway', 'Airplanes', 'Cricket ball']
    },
    
    'projectile': {
        'subject': 'physics',
        'scene': 'cricket_field',
        'available_metaphors': ['cricket_six', 'water_fountain', 'football_goal', 'kite_flying', 'stone_skipping'],
        'preferred_metaphor': 'cricket_six',
        'entities': ['cricket_ball', 'trajectory_arc', 'velocity_vectors', 'gravity_arrow', 'ground'],
        'key_concept': 'Projectile motion combines horizontal and vertical motion',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "When Dhoni hits a six, the ball follows a beautiful curved path. This is projectile motion!",
                'animation': 'ball_launch',
                'entities_visible': ['cricket_ball', 'ground'],
                'highlight': 'cricket_ball'
            },
            {
                'stage_id': 'launch_velocity',
                'duration_ms': 3500,
                'narration': "The ball starts with velocity at an angle. This velocity has two parts: horizontal and vertical.",
                'animation': 'velocity_decomposition',
                'entities_visible': ['cricket_ball', 'velocity_vectors'],
                'highlight': 'velocity_vectors',
                'emphasis': 'Initial velocity breaks into horizontal (Vx) and vertical (Vy) components'
            },
            {
                'stage_id': 'arc_motion',
                'duration_ms': 4000,
                'narration': "Gravity pulls the ball down while it moves forward. This creates the parabolic arc we see.",
                'animation': 'ball_flies_parabola',
                'entities_visible': ['cricket_ball', 'trajectory_arc', 'gravity_arrow'],
                'highlight': 'gravity_arrow',
                'interaction': {'type': 'scrub', 'target': 'timeline', 'description': 'Scrub to see ball motion frame by frame'}
            },
            {
                'stage_id': 'horizontal_constant',
                'duration_ms': 3500,
                'narration': "Notice: horizontal velocity stays constant (no air resistance). Only vertical velocity changes due to gravity.",
                'animation': 'horizontal_motion_analysis',
                'entities_visible': ['cricket_ball', 'velocity_vectors'],
                'emphasis': 'Horizontal motion is uniform, vertical motion is accelerated'
            },
            {
                'stage_id': 'landing',
                'duration_ms': 3000,
                'narration': "The ball lands with the same speed it was launched (but direction is downward now). That's projectile motion!",
                'animation': 'ball_lands',
                'entities_visible': ['cricket_ball', 'trajectory_arc', 'ground'],
                'interaction': {'type': 'slider', 'control': 'launch_angle', 'range': [0, 90], 'description': 'Change launch angle to see different trajectories'}
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'launch_angle', 'range': [15, 75], 'unit': 'degrees'},
            {'type': 'slider', 'control': 'launch_speed', 'range': [10, 50], 'unit': 'm/s'}
        ],
        'real_world_examples': ['Cricket six', 'Basketball shot', 'Water fountain', 'Cannon ball']
    },
    
    'newton_first': {
        'subject': 'physics',
        'scene': 'highway_road',
        'available_metaphors': ['bus_sudden_brake', 'train_leaving_station', 'table_cloth_trick', 'car_highway_cruise', 'hockey_puck'],
        'preferred_metaphor': 'bus_sudden_brake',
        'entities': ['car', 'friction_arrows', 'velocity_arrow', 'obstacle'],
        'key_concept': "An object at rest stays at rest, object in motion stays in motion (unless external force acts)",
        'concept_type': 'cause_effect',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Newton's First Law: Objects resist changes to their motion. This is called inertia.",
                'animation': 'car_stationary',
                'entities_visible': ['car'],
                'highlight': 'car'
            },
            {
                'stage_id': 'rest_stays_rest',
                'duration_ms': 3000,
                'narration': "A parked car won't move on its own. It stays at rest until someone applies force (engine/push).",
                'animation': 'car_at_rest',
                'entities_visible': ['car'],
                'emphasis': 'At rest stays at rest - no force, no motion'
            },
            {
                'stage_id': 'motion_stays_motion',
                'duration_ms': 3500,
                'narration': "Now the car is moving at 60 km/h. Without friction or brakes, it would keep moving forever at the same speed!",
                'animation': 'car_moving_constant',
                'entities_visible': ['car', 'velocity_arrow'],
                'highlight': 'velocity_arrow',
                'emphasis': 'In motion stays in motion - constant velocity without external force'
            },
            {
                'stage_id': 'external_force',
                'duration_ms': 4000,
                'narration': "But wait - driver hits the brakes! This external force (friction) stops the car. Inertia resisted, but force won.",
                'animation': 'car_braking',
                'entities_visible': ['car', 'friction_arrows', 'velocity_arrow'],
                'highlight': 'friction_arrows',
                'interaction': {'type': 'click', 'target': 'brakes', 'description': 'Click to apply brakes'}
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Every object has inertia - resistance to change. External forces are needed to change motion.",
                'animation': 'inertia_demo',
                'entities_visible': ['car', 'friction_arrows'],
                'emphasis': 'Inertia keeps things as they are; force changes motion'
            }
        ],
        'interactions': [
            {'type': 'toggle', 'control': 'friction', 'states': ['on', 'off']},
            {'type': 'button', 'control': 'apply_brakes', 'label': 'Apply Brakes'}
        ],
        'real_world_examples': ['Car braking', 'Hockey puck sliding', 'Satellite in space', 'Seatbelt safety']
    },
    
    # ========================================================================
    # CHEMISTRY CONCEPTS
    # ========================================================================
    
    'valency': {
        'subject': 'chemistry',
        'scene': 'electron_shell_space',
        'available_metaphors': ['cricket_team_formation', 'friendship_bonds', 'plug_socket', 'lego_blocks', 'hand_holding', 'magnet_pairing', 'key_lock'],
        'preferred_metaphor': 'cricket_team_formation',
        'entities': ['atom_nucleus', 'electron_shells', 'electrons', 'empty_slots', 'bonding_hand'],
        'key_concept': 'Valency is the combining capacity of an atom',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Valency tells us how many bonds an atom can form. Think of it like open hands ready to hold other atoms.",
                'animation': 'atom_intro',
                'entities_visible': ['atom_nucleus', 'electron_shells'],
                'highlight': 'atom_nucleus'
            },
            {
                'stage_id': 'electron_shells',
                'duration_ms': 3500,
                'narration': "Atoms have electron shells. The outermost shell determines valency - it shows how many electrons an atom wants to gain or lose.",
                'animation': 'shells_highlight',
                'entities_visible': ['atom_nucleus', 'electron_shells', 'electrons'],
                'highlight': 'electron_shells',
                'emphasis': 'Outermost shell (valence shell) determines chemical behavior'
            },
            {
                'stage_id': 'octet_rule',
                'duration_ms': 4000,
                'narration': "Atoms want 8 electrons in their outer shell (octet rule). If oxygen has 6, it needs 2 more - so valency is 2!",
                'animation': 'octet_demonstration',
                'entities_visible': ['atom_nucleus', 'electron_shells', 'electrons', 'empty_slots'],
                'highlight': 'empty_slots',
                'interaction': {'type': 'hover', 'target': 'empty_slots', 'description': 'Hover to see missing electrons'}
            },
            {
                'stage_id': 'bonding_capacity',
                'duration_ms': 3500,
                'narration': "Carbon has 4 electrons in outer shell. It can gain or lose 4 electrons, so valency = 4. This means carbon can form 4 bonds!",
                'animation': 'carbon_bonding',
                'entities_visible': ['atom_nucleus', 'bonding_hand', 'electrons'],
                'highlight': 'bonding_hand',
                'emphasis': 'Valency = number of bonds an atom can form'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Valency is combining capacity. It determines how atoms bond: H=1, O=2, N=3, C=4. Remember the outermost shell!",
                'animation': 'valency_chart',
                'entities_visible': ['atom_nucleus', 'bonding_hand'],
                'emphasis': 'Valency comes from valence (outer) shell electron count'
            }
        ],
        'interactions': [
            {'type': 'selector', 'control': 'element', 'options': ['H', 'C', 'N', 'O'], 'description': 'Select element to see its valency'}
        ],
        'real_world_examples': ['Water H2O (H=1, O=2)', 'Methane CH4 (C=4, H=1)', 'Ammonia NH3 (N=3, H=1)']
    },
    
    'acids_strength': {
        'subject': 'chemistry',
        'scene': 'laboratory_bench',
        'available_metaphors': ['spice_levels_indian', 'tea_strength', 'battery_power', 'water_pressure', 'soap_cleaning'],
        'preferred_metaphor': 'spice_levels_indian',
        'entities': ['ph_scale', 'test_tubes', 'acid_molecules', 'indicator_paper', 'color_gradient'],
        'key_concept': 'Acid strength depends on how easily it releases H+ ions',
        'concept_type': 'comparison',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Not all acids are equally strong. Lemon juice is acidic but won't burn your hand like battery acid would!",
                'animation': 'acid_comparison',
                'entities_visible': ['test_tubes', 'ph_scale'],
                'highlight': 'test_tubes'
            },
            {
                'stage_id': 'ph_scale',
                'duration_ms': 3500,
                'narration': "pH scale measures acidity. pH 0-7 is acidic, 7 is neutral, 7-14 is basic. Lower pH = stronger acid.",
                'animation': 'ph_scale_display',
                'entities_visible': ['ph_scale', 'color_gradient'],
                'highlight': 'ph_scale',
                'emphasis': 'pH scale: 0 (strongest acid) to 14 (strongest base)'
            },
            {
                'stage_id': 'hydrogen_ions',
                'duration_ms': 4000,
                'narration': "Acids release H+ ions in water. Strong acids release ALL their H+ easily. Weak acids release only some H+.",
                'animation': 'h_ion_release',
                'entities_visible': ['acid_molecules', 'test_tubes'],
                'highlight': 'acid_molecules',
                'interaction': {'type': 'hover', 'target': 'acid_molecules', 'description': 'Hover to see H+ ion release'}
            },
            {
                'stage_id': 'strong_vs_weak',
                'duration_ms': 3500,
                'narration': "HCl (hydrochloric acid) completely breaks apart - strong acid. Acetic acid (vinegar) only partially breaks - weak acid.",
                'animation': 'dissociation_comparison',
                'entities_visible': ['acid_molecules', 'test_tubes', 'indicator_paper'],
                'emphasis': 'Complete dissociation = strong acid, Partial dissociation = weak acid'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Acid strength = ease of releasing H+ ions. Strong acids: HCl, H2SO4. Weak acids: vinegar, citric acid. Check pH to know!",
                'animation': 'ph_test_demo',
                'entities_visible': ['ph_scale', 'indicator_paper', 'color_gradient'],
                'interaction': {'type': 'slider', 'control': 'ph', 'range': [0, 7], 'description': 'Slide to see different acid strengths'}
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'ph', 'range': [0, 7], 'unit': 'pH'},
            {'type': 'selector', 'control': 'acid_type', 'options': ['HCl', 'H2SO4', 'Acetic', 'Citric']}
        ],
        'real_world_examples': ['Battery acid (pH 0)', 'Stomach acid (pH 1-2)', 'Lemon juice (pH 2)', 'Vinegar (pH 3)']
    },
    
    'bonding': {
        'subject': 'chemistry',
        'scene': 'molecule_space',
        'available_metaphors': ['friendship_bracelets', 'rakhi_bandhan', 'train_coaches', 'chain_links', 'hands_holding'],
        'preferred_metaphor': 'rakhi_bandhan',
        'entities': ['atom_1', 'atom_2', 'electron_cloud', 'bond_line', 'shared_electrons'],
        'key_concept': 'Chemical bonds form when atoms share or transfer electrons',
        'concept_type': 'transformation',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Atoms don't stay alone - they bond together to form molecules. Let's see how bonding happens!",
                'animation': 'atoms_separate',
                'entities_visible': ['atom_1', 'atom_2'],
                'highlight': 'atom_1'
            },
            {
                'stage_id': 'electron_sharing',
                'duration_ms': 3500,
                'narration': "Covalent bonding: atoms SHARE electrons. Like two friends sharing a pizza - both get to enjoy it!",
                'animation': 'electron_share',
                'entities_visible': ['atom_1', 'atom_2', 'shared_electrons'],
                'highlight': 'shared_electrons',
                'emphasis': 'Covalent bond = electron sharing'
            },
            {
                'stage_id': 'bond_formation',
                'duration_ms': 4000,
                'narration': "When electrons are shared, a bond forms! This bond holds atoms together. The electron cloud overlaps between atoms.",
                'animation': 'bond_forms',
                'entities_visible': ['atom_1', 'atom_2', 'bond_line', 'electron_cloud'],
                'highlight': 'bond_line',
                'interaction': {'type': 'click', 'target': 'atoms', 'description': 'Click to form/break bond'}
            },
            {
                'stage_id': 'bond_types',
                'duration_ms': 3500,
                'narration': "Single bond (one pair shared), double bond (two pairs), triple bond (three pairs). More shared electrons = stronger bond!",
                'animation': 'bond_types_demo',
                'entities_visible': ['atom_1', 'atom_2', 'bond_line', 'shared_electrons'],
                'emphasis': 'More electron pairs shared = stronger, shorter bond'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Chemical bonds are electron interactions. Sharing creates covalent bonds. This is how molecules form from atoms!",
                'animation': 'molecule_formed',
                'entities_visible': ['atom_1', 'atom_2', 'bond_line'],
                'emphasis': 'Bonding satisfies the octet rule - atoms want 8 outer electrons'
            }
        ],
        'interactions': [
            {'type': 'selector', 'control': 'bond_type', 'options': ['single', 'double', 'triple']},
            {'type': 'toggle', 'control': 'electron_visibility', 'states': ['show', 'hide']}
        ],
        'real_world_examples': ['H2 molecule (H-H single bond)', 'O2 molecule (O=O double bond)', 'N2 molecule (N≡N triple bond)']
    },
    
    # ========================================================================
    # BIOLOGY CONCEPTS
    # ========================================================================
    
    'photosynthesis': {
        'subject': 'biology',
        'scene': 'leaf_cross_section',
        'available_metaphors': ['solar_panel_home', 'kitchen_cooking', 'factory_production', 'atm_machine', 'charging_phone'],
        'preferred_metaphor': 'solar_panel_home',
        'entities': ['chloroplast', 'sunlight_rays', 'co2_molecules', 'water_molecules', 'glucose', 'oxygen'],
        'key_concept': 'Plants convert light energy into chemical energy (glucose)',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Photosynthesis is how plants make their own food using sunlight. It's nature's solar-powered factory!",
                'animation': 'leaf_intro',
                'entities_visible': ['chloroplast', 'sunlight_rays'],
                'highlight': 'chloroplast'
            },
            {
                'stage_id': 'inputs',
                'duration_ms': 3500,
                'narration': "Plants need three things: sunlight (energy), CO2 (from air), and water (from roots). These are the raw materials.",
                'animation': 'inputs_arrive',
                'entities_visible': ['sunlight_rays', 'co2_molecules', 'water_molecules', 'chloroplast'],
                'highlight': 'co2_molecules',
                'emphasis': 'Inputs: Light + CO2 + H2O'
            },
            {
                'stage_id': 'chloroplast_factory',
                'duration_ms': 4000,
                'narration': "Inside chloroplasts, magical chlorophyll captures sunlight. This energy breaks water molecules and combines CO2 to make glucose!",
                'animation': 'reaction_process',
                'entities_visible': ['chloroplast', 'sunlight_rays', 'co2_molecules', 'water_molecules'],
                'highlight': 'chloroplast',
                'interaction': {'type': 'hover', 'target': 'chloroplast', 'description': 'Hover to see reaction details'}
            },
            {
                'stage_id': 'outputs',
                'duration_ms': 3500,
                'narration': "Two products are made: glucose (C6H12O6) - plant's food - and oxygen (O2) - which we breathe! Win-win!",
                'animation': 'outputs_produced',
                'entities_visible': ['glucose', 'oxygen', 'chloroplast'],
                'highlight': 'glucose',
                'emphasis': 'Outputs: Glucose (food) + O2 (oxygen)'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Equation: 6CO2 + 6H2O + Light → C6H12O6 + 6O2. Plants feed themselves and give us oxygen. Thank you, plants!",
                'animation': 'equation_display',
                'entities_visible': ['co2_molecules', 'water_molecules', 'glucose', 'oxygen'],
                'emphasis': 'Photosynthesis converts light energy to chemical energy stored in glucose'
            }
        ],
        'interactions': [
            {'type': 'toggle', 'control': 'light_intensity', 'states': ['low', 'medium', 'high']},
            {'type': 'hover', 'target': 'chloroplast', 'description': 'Explore inside chloroplast'}
        ],
        'real_world_examples': ['Trees producing oxygen', 'Crops growing in farms', 'Algae in oceans', 'House plants cleaning air']
    },
    
    'respiration': {
        'subject': 'biology',
        'scene': 'mitochondria_interior',
        'available_metaphors': ['power_plant', 'petrol_engine', 'gas_stove', 'runner_breathing', 'mobile_battery'],
        'preferred_metaphor': 'gas_stove',
        'entities': ['mitochondria', 'glucose_molecule', 'oxygen_molecules', 'atp_energy', 'co2_waste', 'water_product'],
        'key_concept': 'Cells break down glucose to release energy (ATP)',
        'concept_type': 'transformation',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Cellular respiration is how cells release energy from food. It's the opposite of photosynthesis!",
                'animation': 'mitochondria_intro',
                'entities_visible': ['mitochondria'],
                'highlight': 'mitochondria'
            },
            {
                'stage_id': 'fuel_arrives',
                'duration_ms': 3500,
                'narration': "Glucose (from food) and oxygen (from breathing) enter the mitochondria - the powerhouse of the cell.",
                'animation': 'fuel_entry',
                'entities_visible': ['mitochondria', 'glucose_molecule', 'oxygen_molecules'],
                'highlight': 'glucose_molecule',
                'emphasis': 'Mitochondria = powerhouse of the cell'
            },
            {
                'stage_id': 'energy_release',
                'duration_ms': 4000,
                'narration': "Glucose is broken down step by step. Chemical bonds break, releasing energy that's captured as ATP - the energy currency!",
                'animation': 'glucose_breakdown',
                'entities_visible': ['glucose_molecule', 'oxygen_molecules', 'atp_energy'],
                'highlight': 'atp_energy',
                'interaction': {'type': 'click', 'target': 'glucose', 'description': 'Click to break down glucose'}
            },
            {
                'stage_id': 'waste_products',
                'duration_ms': 3500,
                'narration': "Byproducts: CO2 (we breathe it out) and water. The main product is ATP - energy for all cell activities!",
                'animation': 'products_exit',
                'entities_visible': ['atp_energy', 'co2_waste', 'water_product'],
                'highlight': 'atp_energy',
                'emphasis': 'ATP powers everything: movement, growth, thinking!'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Equation: C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP. Respiration releases energy. It happens 24/7 in every living cell!",
                'animation': 'equation_cycle',
                'entities_visible': ['glucose_molecule', 'atp_energy', 'co2_waste'],
                'emphasis': 'Respiration is controlled burning - releasing energy from glucose safely'
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'oxygen_level', 'range': [0, 100], 'unit': '%', 'description': 'Adjust oxygen to see respiration rate'}
        ],
        'real_world_examples': ['Breathing during exercise', 'Muscle cells generating ATP', 'Brain cells using 20% of body energy']
    },
    
    # ========================================================================
    # MATHEMATICS CONCEPTS
    # ========================================================================
    
    'quadratic': {
        'subject': 'mathematics',
        'scene': 'graph_coordinate_space',
        'available_metaphors': ['cricket_ball_arc', 'fountain_water', 'bridge_arch', 'profit_curve', 'satellite_dish'],
        'preferred_metaphor': 'cricket_ball_arc',
        'entities': ['parabola_curve', 'vertex_point', 'x_axis', 'y_axis', 'roots', 'equation_label'],
        'key_concept': 'Quadratic equations create parabolic (U-shaped or inverted-U) curves',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Quadratic equations have x² (x-squared). They create beautiful U-shaped curves called parabolas.",
                'animation': 'parabola_draw',
                'entities_visible': ['x_axis', 'y_axis', 'parabola_curve'],
                'highlight': 'parabola_curve'
            },
            {
                'stage_id': 'equation_form',
                'duration_ms': 3500,
                'narration': "Standard form: y = ax² + bx + c. The 'a' value determines if parabola opens up (a>0) or down (a<0).",
                'animation': 'equation_display',
                'entities_visible': ['parabola_curve', 'equation_label'],
                'highlight': 'equation_label',
                'emphasis': 'x² term creates the curve!'
            },
            {
                'stage_id': 'vertex',
                'duration_ms': 4000,
                'narration': "The vertex is the turning point - highest or lowest point on the parabola. It's located at x = -b/(2a).",
                'animation': 'vertex_highlight',
                'entities_visible': ['parabola_curve', 'vertex_point', 'x_axis', 'y_axis'],
                'highlight': 'vertex_point',
                'interaction': {'type': 'hover', 'target': 'vertex_point', 'description': 'Hover to see vertex coordinates'}
            },
            {
                'stage_id': 'roots',
                'duration_ms': 3500,
                'narration': "Roots (or zeros) are where the parabola crosses x-axis. A quadratic can have 0, 1, or 2 real roots!",
                'animation': 'roots_display',
                'entities_visible': ['parabola_curve', 'roots', 'x_axis'],
                'highlight': 'roots',
                'emphasis': 'Roots satisfy ax² + bx + c = 0'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Quadratics model many real things: projectile paths, profit curves, area problems. Master the parabola!",
                'animation': 'real_world_overlay',
                'entities_visible': ['parabola_curve', 'vertex_point', 'roots'],
                'interaction': {'type': 'slider', 'control': 'a_value', 'range': [-5, 5], 'description': 'Change a to reshape parabola'}
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'a_value', 'range': [-5, 5], 'unit': '', 'step': 0.5},
            {'type': 'slider', 'control': 'b_value', 'range': [-10, 10], 'unit': '', 'step': 1},
            {'type': 'slider', 'control': 'c_value', 'range': [-10, 10], 'unit': '', 'step': 1}
        ],
        'real_world_examples': ['Projectile motion', 'Profit optimization', 'Bridge arches', 'Satellite dishes']
    },
    
    'linear': {
        'subject': 'mathematics',
        'scene': 'graph_coordinate_space',
        'available_metaphors': ['rickshaw_meter', 'mobile_recharge', 'vegetable_pricing', 'stairs_climbing', 'water_filling'],
        'preferred_metaphor': 'rickshaw_meter',
        'entities': ['line', 'slope_triangle', 'y_intercept_point', 'x_axis', 'y_axis', 'equation_label'],
        'key_concept': 'Linear equations create straight lines with constant slope',
        'concept_type': 'process',
        'stages': [
            {
                'stage_id': 'intro',
                'duration_ms': 2500,
                'narration': "Linear equations create straight lines. They show constant rate of change - like climbing a hill at steady pace.",
                'animation': 'line_draw',
                'entities_visible': ['x_axis', 'y_axis', 'line'],
                'highlight': 'line'
            },
            {
                'stage_id': 'slope',
                'duration_ms': 3500,
                'narration': "Slope (m) tells you how steep the line is. Slope = rise/run = change in y / change in x.",
                'animation': 'slope_demo',
                'entities_visible': ['line', 'slope_triangle', 'x_axis', 'y_axis'],
                'highlight': 'slope_triangle',
                'emphasis': 'Slope = rise ÷ run'
            },
            {
                'stage_id': 'y_intercept',
                'duration_ms': 4000,
                'narration': "Y-intercept (b) is where the line crosses y-axis. That's the starting value when x = 0.",
                'animation': 'intercept_highlight',
                'entities_visible': ['line', 'y_intercept_point', 'y_axis'],
                'highlight': 'y_intercept_point',
                'interaction': {'type': 'hover', 'target': 'y_intercept_point', 'description': 'See y-intercept value'}
            },
            {
                'stage_id': 'equation',
                'duration_ms': 3500,
                'narration': "Equation: y = mx + b. 'm' is slope, 'b' is y-intercept. This simple form describes any straight line!",
                'animation': 'equation_display',
                'entities_visible': ['line', 'equation_label', 'slope_triangle', 'y_intercept_point'],
                'emphasis': 'y = mx + b is the slope-intercept form'
            },
            {
                'stage_id': 'summary',
                'duration_ms': 2500,
                'narration': "Linear relationships are everywhere: speed over time, cost vs quantity, temperature conversion. Lines are fundamental!",
                'animation': 'real_examples',
                'entities_visible': ['line', 'x_axis', 'y_axis'],
                'interaction': {'type': 'slider', 'control': 'slope', 'range': [-5, 5], 'description': 'Change slope to see line tilt'}
            }
        ],
        'interactions': [
            {'type': 'slider', 'control': 'slope', 'range': [-5, 5], 'unit': '', 'step': 0.5},
            {'type': 'slider', 'control': 'y_intercept', 'range': [-10, 10], 'unit': '', 'step': 1}
        ],
        'real_world_examples': ['Distance = speed × time', 'Cost = price × quantity', 'Temperature conversion F = 1.8C + 32']
    }
}

# ============================================================================
# CONCEPT TYPE PATTERNS (for auto-generation of unknown concepts)
# ============================================================================

CONCEPT_TYPE_TEMPLATES = {
    'comparison': {
        'stage_pattern': ['intro', 'item_1_detail', 'item_2_detail', 'differences', 'summary'],
        'narration_templates': {
            'intro': "Let's compare {concept} to understand the key differences.",
            'item_1_detail': "First, let's examine {element_1} carefully.",
            'item_2_detail': "Now, let's look at {element_2}.",
            'differences': "Notice the important differences between them.",
            'summary': "Remember these key distinctions when comparing {concept}."
        }
    },
    'process': {
        'stage_pattern': ['intro', 'step_1', 'step_2', 'step_3', 'step_4', 'summary'],
        'narration_templates': {
            'intro': "Let's understand {concept} step by step.",
            'step_n': "Step {n}: {element}",
            'summary': "That's the complete process of {concept}. Let's review the key steps."
        }
    },
    'transformation': {
        'stage_pattern': ['intro', 'initial_state', 'transformation', 'final_state', 'summary'],
        'narration_templates': {
            'intro': "Watch how {concept} transforms from one state to another.",
            'initial_state': "We start with {element_1}.",
            'transformation': "Now observe the transformation happening.",
            'final_state': "We arrive at {element_2}.",
            'summary': "This transformation is key to understanding {concept}."
        }
    },
    'cause_effect': {
        'stage_pattern': ['intro', 'cause', 'mechanism', 'effect', 'summary'],
        'narration_templates': {
            'intro': "Let's explore the cause-effect relationship in {concept}.",
            'cause': "The cause is {element_1}.",
            'mechanism': "Here's how the cause leads to the effect.",
            'effect': "This results in {element_2}.",
            'summary': "Understanding this cause-effect helps us predict and control {concept}."
        }
    }
}

# ============================================================================
# CONCEPT NAME ALIASES (for flexible matching)
# ============================================================================

CONCEPT_ALIASES = {
    # Physics aliases
    'projectile motion': 'projectile',
    'projectile trajectory': 'projectile',
    'newton first law': 'newton_first',
    "newton's first law": 'newton_first',
    'newtons first law': 'newton_first',
    'first law of motion': 'newton_first',
    'law of inertia': 'newton_first',
    
    # Chemistry aliases
    'valency electron': 'valency',
    'valence electron': 'valency',
    'combining capacity': 'valency',
    'acid strength': 'acids_strength',
    'chemical bonding': 'bonding',
    'covalent bonding': 'bonding',
    'ionic bonding': 'bonding',
    
    # Biology aliases
    'photosynthetic process': 'photosynthesis',
    'cellular respiration': 'respiration',
    'aerobic respiration': 'respiration',
    
    # Math aliases
    'quadratic equation': 'quadratic',
    'quadratic function': 'quadratic',
    'parabola': 'quadratic',
    'linear equation': 'linear',
    'linear function': 'linear',
    'straight line': 'linear',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_concept_name(concept_name: str) -> str:
    """
    Normalize concept name to match library entries
    Handles aliases and variations
    """
    concept_lower = concept_name.lower().strip()
    
    # Check direct alias match
    if concept_lower in CONCEPT_ALIASES:
        return CONCEPT_ALIASES[concept_lower]
    
    # Remove common suffixes
    for suffix in [' equation', ' function', ' motion', ' process', ' law', ' reaction']:
        if concept_lower.endswith(suffix):
            base = concept_lower.replace(suffix, '').strip()
            if base in CONCEPT_LIBRARY:
                return base
    
    return concept_lower

def get_concept_content(concept_name: str) -> Optional[Dict[str, Any]]:
    """
    Get content for a specific concept
    Uses normalization to handle aliases
    """
    normalized = normalize_concept_name(concept_name)
    return CONCEPT_LIBRARY.get(normalized)

def get_concept_list_by_subject(subject: str) -> List[str]:
    """Get list of concepts for a subject"""
    return [
        concept_name
        for concept_name, data in CONCEPT_LIBRARY.items()
        if data['subject'].lower() == subject.lower()
    ]

def has_concept_content(concept_name: str) -> bool:
    """
    Check if concept has full content
    Uses normalization to handle aliases
    """
    normalized = normalize_concept_name(concept_name)
    return normalized in CONCEPT_LIBRARY

def get_concept_summary(concept_name: str) -> str:
    """Get one-line summary of concept"""
    concept = CONCEPT_LIBRARY.get(concept_name.lower())
    if concept:
        return concept.get('key_concept', 'No summary available')
    return 'Concept not in library'

