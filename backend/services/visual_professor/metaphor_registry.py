"""
Metaphor Registry - Dynamic Metaphor Selection System
Each concept has 5-10 metaphors that are selected dynamically based on:
- Student profile (interests, region, age)
- Concept difficulty
- Cultural context
- Previous effectiveness
NO hardcoded metaphors per concept!
"""
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# METAPHOR REGISTRY - 5-10 METAPHORS PER CONCEPT
# ============================================================================

METAPHOR_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    # ========================================================================
    # PHYSICS CONCEPTS
    # ========================================================================
    
    'velocity': [
        {
            'id': 'delhi_metro',
            'name': 'Delhi Metro Train on Purple Line',
            'scene': 'urban_metro_station',
            'entities': ['metro_train', 'platform', 'direction_board', 'tracks', 'speed_display'],
            'cultural_fit': 0.95,  # Very Indian
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['Delhi', 'NCR', 'North India'],
            'keywords': ['metro', 'delhi', 'purple line', 'train', 'station']
        },
        {
            'id': 'cricket_ball_bowling',
            'name': 'Fast Bowler Delivering Ball',
            'scene': 'cricket_stadium',
            'entities': ['cricket_ball', 'bowler', 'trajectory_line', 'speed_gun', 'stumps'],
            'cultural_fit': 1.0,  # Extremely Indian
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['cricket', 'bowling', 'ball', 'fast bowler', 'delivery']
        },
        {
            'id': 'auto_rickshaw_traffic',
            'name': 'Auto-Rickshaw in Bangalore Traffic',
            'scene': 'city_traffic',
            'entities': ['auto', 'traffic_signals', 'roads', 'speed_meter', 'direction_signs'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['Bangalore', 'South India'],
            'keywords': ['auto', 'rickshaw', 'traffic', 'bangalore']
        },
        {
            'id': 'local_train_mumbai',
            'name': 'Mumbai Local Train',
            'scene': 'railway_platform',
            'entities': ['local_train', 'platform', 'crowd', 'tracks', 'clock'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['Mumbai', 'Maharashtra', 'West India'],
            'keywords': ['local', 'mumbai', 'train', 'railway']
        },
        {
            'id': 'river_flow',
            'name': 'River Ganga Flow',
            'scene': 'river_landscape',
            'entities': ['river', 'boat', 'current_arrows', 'landmarks'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.8,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['North India', 'all'],
            'keywords': ['river', 'ganga', 'flow', 'current']
        },
        {
            'id': 'drone_delivery',
            'name': 'Drone Delivering Package',
            'scene': 'urban_skyline',
            'entities': ['drone', 'package', 'buildings', 'gps_path', 'speed_meter'],
            'cultural_fit': 0.7,  # Modern, tech-savvy
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.9,
            'age_group': 'high_school',
            'regions': ['metro_cities'],
            'keywords': ['drone', 'delivery', 'flying', 'technology']
        },
        {
            'id': 'cyclist_morning',
            'name': 'Morning Cyclist in Park',
            'scene': 'park_path',
            'entities': ['cyclist', 'bicycle', 'path', 'trees', 'milestones'],
            'cultural_fit': 0.8,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.75,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['cycling', 'bicycle', 'park', 'morning']
        },
        {
            'id': 'bullet_train',
            'name': 'Bullet Train (Vande Bharat)',
            'scene': 'modern_railway',
            'entities': ['bullet_train', 'modern_station', 'speed_display', 'tracks'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.8,
            'engagement': 0.9,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['bullet train', 'vande bharat', 'fast', 'modern']
        }
    ],
    
    'projectile': [
        {
            'id': 'cricket_six',
            'name': 'Dhoni Hitting a Six',
            'scene': 'cricket_stadium_boundary',
            'entities': ['cricket_ball', 'bat', 'trajectory_arc', 'boundary_rope', 'crowd'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['cricket', 'six', 'dhoni', 'boundary', 'hit']
        },
        {
            'id': 'water_fountain',
            'name': 'Water Fountain in India Gate',
            'scene': 'fountain_plaza',
            'entities': ['water_jets', 'fountain', 'arc_paths', 'pool'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.8,
            'engagement': 0.75,
            'age_group': 'all',
            'regions': ['Delhi', 'North India'],
            'keywords': ['fountain', 'water', 'india gate', 'spray']
        },
        {
            'id': 'football_goal',
            'name': 'Football Free Kick Goal',
            'scene': 'football_field',
            'entities': ['football', 'player', 'trajectory', 'goal_post', 'goalkeeper'],
            'cultural_fit': 0.7,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['football', 'goal', 'kick', 'soccer']
        },
        {
            'id': 'kite_flying',
            'name': 'Kite Flying on Makar Sankranti',
            'scene': 'rooftop_sky',
            'entities': ['kite', 'string', 'wind', 'rooftop', 'other_kites'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.8,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['Gujarat', 'North India'],
            'keywords': ['kite', 'makar sankranti', 'flying', 'festival']
        },
        {
            'id': 'stone_skipping',
            'name': 'Skipping Stones on Lake',
            'scene': 'lake_shore',
            'entities': ['stone', 'water', 'ripples', 'trajectory', 'shore'],
            'cultural_fit': 0.75,
            'difficulty': 'medium',
            'real_world_relevance': 0.7,
            'engagement': 0.7,
            'age_group': 'middle_school',
            'regions': ['all'],
            'keywords': ['stone', 'skipping', 'lake', 'water']
        }
    ],
    
    'newton_first': [
        {
            'id': 'bus_sudden_brake',
            'name': 'City Bus Sudden Brake (Inertia)',
            'scene': 'city_bus_interior',
            'entities': ['bus', 'passengers', 'hand_rails', 'brake_pedal', 'inertia_arrows'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.95,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['bus', 'brake', 'inertia', 'passengers', 'jerking']
        },
        {
            'id': 'train_leaving_station',
            'name': 'Train Leaving Platform',
            'scene': 'railway_platform',
            'entities': ['train', 'passengers', 'platform', 'luggage'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['train', 'station', 'platform', 'leaving']
        },
        {
            'id': 'table_cloth_trick',
            'name': 'Pulling Tablecloth Magic Trick',
            'scene': 'dining_table',
            'entities': ['tablecloth', 'plates', 'glasses', 'table'],
            'cultural_fit': 0.8,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['tablecloth', 'magic', 'trick', 'inertia']
        },
        {
            'id': 'car_highway_cruise',
            'name': 'Car on Highway with Cruise Control',
            'scene': 'highway_road',
            'entities': ['car', 'highway', 'trees', 'speed_constant'],
            'cultural_fit': 0.75,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['metro_cities'],
            'keywords': ['car', 'highway', 'cruise', 'constant speed']
        },
        {
            'id': 'hockey_puck',
            'name': 'Hockey Puck Sliding on Ice',
            'scene': 'ice_rink',
            'entities': ['puck', 'ice', 'player', 'stick'],
            'cultural_fit': 0.6,
            'difficulty': 'medium',
            'real_world_relevance': 0.7,
            'engagement': 0.7,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['hockey', 'puck', 'ice', 'sliding']
        }
    ],
    
    # ========================================================================
    # CHEMISTRY CONCEPTS
    # ========================================================================
    
    'valency': [
        {
            'id': 'cricket_team_formation',
            'name': 'Cricket Team Slot Filling',
            'scene': 'team_selection_board',
            'entities': ['player_slots', 'players', 'team_board', 'positions'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['cricket', 'team', 'slots', 'players', 'formation']
        },
        {
            'id': 'friendship_bonds',
            'name': 'Friend Groups and Connections',
            'scene': 'social_circle_diagram',
            'entities': ['people', 'connection_lines', 'friend_groups'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 0.9,
            'age_group': 'middle_school',
            'regions': ['all'],
            'keywords': ['friends', 'connections', 'bonds', 'relationships']
        },
        {
            'id': 'plug_socket',
            'name': 'Electrical Plug and Socket',
            'scene': 'wall_socket',
            'entities': ['plug', 'socket', 'pins', 'holes'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['plug', 'socket', 'electrical', 'pins']
        },
        {
            'id': 'lego_blocks',
            'name': 'LEGO Blocks Connecting',
            'scene': 'play_table',
            'entities': ['lego_pieces', 'studs', 'connection_points'],
            'cultural_fit': 0.75,
            'difficulty': 'easy',
            'real_world_relevance': 0.8,
            'engagement': 0.85,
            'age_group': 'middle_school',
            'regions': ['metro_cities'],
            'keywords': ['lego', 'blocks', 'connecting', 'building']
        },
        {
            'id': 'hand_holding',
            'name': 'Holding Hands (Multiple People)',
            'scene': 'circle_formation',
            'entities': ['hands', 'people', 'connections'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.8,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['hands', 'holding', 'connections', 'people']
        },
        {
            'id': 'magnet_pairing',
            'name': 'Magnets Attracting/Repelling',
            'scene': 'physics_lab',
            'entities': ['magnets', 'poles', 'force_lines', 'iron_filings'],
            'cultural_fit': 0.7,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.8,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['magnet', 'poles', 'attraction', 'repulsion']
        },
        {
            'id': 'key_lock',
            'name': 'Key Fitting into Lock',
            'scene': 'door_lock',
            'entities': ['key', 'lock', 'pins', 'mechanism'],
            'cultural_fit': 0.85,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.75,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['key', 'lock', 'fitting', 'mechanism']
        }
    ],
    
    'acids_strength': [
        {
            'id': 'spice_levels_indian',
            'name': 'Indian Food Spice Levels',
            'scene': 'street_food_stall',
            'entities': ['chili_meter', 'dishes', 'spice_scale', 'flames'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['spicy', 'chili', 'food', 'indian', 'mirchi']
        },
        {
            'id': 'tea_strength',
            'name': 'Chai Strength (Kadak vs Light)',
            'scene': 'tea_stall',
            'entities': ['tea_cups', 'color_gradient', 'strength_meter', 'kettle'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 0.95,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['chai', 'tea', 'kadak', 'strength']
        },
        {
            'id': 'battery_power',
            'name': 'Battery Power Levels',
            'scene': 'electronic_device',
            'entities': ['battery', 'charge_bars', 'voltage_meter'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.9,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['battery', 'charge', 'power', 'voltage']
        },
        {
            'id': 'water_pressure',
            'name': 'Water Tank Pressure',
            'scene': 'water_tank_system',
            'entities': ['tank', 'pipes', 'pressure_gauge', 'water_flow'],
            'cultural_fit': 0.9,
            'difficulty': 'medium',
            'real_world_relevance': 0.9,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['water', 'pressure', 'tank', 'flow']
        },
        {
            'id': 'soap_cleaning',
            'name': 'Soap Cleaning Power',
            'scene': 'washing_area',
            'entities': ['soap_bars', 'bubbles', 'dirt', 'cleaning_scale'],
            'cultural_fit': 0.85,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.7,
            'age_group': 'middle_school',
            'regions': ['all'],
            'keywords': ['soap', 'cleaning', 'bubbles', 'washing']
        }
    ],
    
    'bonding': [
        {
            'id': 'friendship_bracelets',
            'name': 'Friendship Bracelets Exchange',
            'scene': 'classroom_friends',
            'entities': ['friends', 'bracelets', 'hands', 'connections'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.95,
            'age_group': 'middle_school',
            'regions': ['all'],
            'keywords': ['friendship', 'bracelets', 'bonds', 'sharing']
        },
        {
            'id': 'rakhi_bandhan',
            'name': 'Raksha Bandhan Thread',
            'scene': 'rakhi_ceremony',
            'entities': ['rakhi', 'brother', 'sister', 'bond_thread'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['rakhi', 'raksha bandhan', 'bond', 'thread', 'festival']
        },
        {
            'id': 'train_coaches',
            'name': 'Train Coaches Coupled',
            'scene': 'railway_yard',
            'entities': ['coaches', 'couplings', 'connectors', 'train'],
            'cultural_fit': 0.9,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.8,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['train', 'coaches', 'coupling', 'connecting']
        },
        {
            'id': 'chain_links',
            'name': 'Bicycle Chain Links',
            'scene': 'bicycle_mechanics',
            'entities': ['chain', 'links', 'gears', 'bicycle'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.8,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['chain', 'links', 'bicycle', 'connecting']
        },
        {
            'id': 'hands_holding',
            'name': 'People Holding Hands in Circle',
            'scene': 'group_activity',
            'entities': ['people', 'hands', 'circle', 'connections'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['hands', 'holding', 'circle', 'together']
        }
    ],
    
    # ========================================================================
    # BIOLOGY CONCEPTS
    # ========================================================================
    
    'photosynthesis': [
        {
            'id': 'solar_panel_home',
            'name': 'Rooftop Solar Panel',
            'scene': 'house_rooftop',
            'entities': ['solar_panels', 'sun_rays', 'battery', 'electricity_flow'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['solar', 'panel', 'energy', 'electricity']
        },
        {
            'id': 'kitchen_cooking',
            'name': 'Kitchen Making Food from Raw Materials',
            'scene': 'home_kitchen',
            'entities': ['raw_ingredients', 'stove', 'fire', 'cooked_food'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.95,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['kitchen', 'cooking', 'food', 'raw', 'cooked']
        },
        {
            'id': 'factory_production',
            'name': 'Factory Converting Raw to Product',
            'scene': 'small_factory',
            'entities': ['raw_materials', 'machines', 'workers', 'finished_products'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.9,
            'engagement': 0.8,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['factory', 'production', 'manufacturing', 'conversion']
        },
        {
            'id': 'atm_machine',
            'name': 'ATM Converting Card to Cash',
            'scene': 'atm_booth',
            'entities': ['atm', 'card', 'cash', 'screen'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 0.85,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['atm', 'cash', 'card', 'money']
        },
        {
            'id': 'charging_phone',
            'name': 'Phone Charging from Sunlight',
            'scene': 'window_sill',
            'entities': ['phone', 'solar_charger', 'sunlight', 'battery_icon'],
            'cultural_fit': 0.85,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.85,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['phone', 'charging', 'solar', 'sunlight']
        }
    ],
    
    'respiration': [
        {
            'id': 'power_plant',
            'name': 'Power Plant Burning Coal',
            'scene': 'thermal_power_station',
            'entities': ['coal', 'furnace', 'steam', 'turbine', 'electricity'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.9,
            'engagement': 0.8,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['power plant', 'coal', 'energy', 'electricity']
        },
        {
            'id': 'petrol_engine',
            'name': 'Car Engine Burning Petrol',
            'scene': 'car_engine_cutaway',
            'entities': ['petrol', 'cylinder', 'spark', 'exhaust', 'motion'],
            'cultural_fit': 0.9,
            'difficulty': 'medium',
            'real_world_relevance': 0.95,
            'engagement': 0.85,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['engine', 'petrol', 'car', 'combustion']
        },
        {
            'id': 'gas_stove',
            'name': 'Gas Stove Burning LPG',
            'scene': 'kitchen_stove',
            'entities': ['lpg_cylinder', 'burner', 'flame', 'heat', 'co2'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.95,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['gas', 'stove', 'lpg', 'flame', 'cooking']
        },
        {
            'id': 'runner_breathing',
            'name': 'Runner Breathing Hard After Race',
            'scene': 'running_track',
            'entities': ['runner', 'lungs', 'oxygen', 'energy', 'sweat'],
            'cultural_fit': 0.85,
            'difficulty': 'easy',
            'real_world_relevance': 0.95,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['running', 'breathing', 'oxygen', 'energy']
        },
        {
            'id': 'mobile_battery',
            'name': 'Mobile Phone Battery Discharge',
            'scene': 'phone_screen',
            'entities': ['battery', 'apps', 'energy_consumption', 'percentage'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.9,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['phone', 'battery', 'discharge', 'energy']
        }
    ],
    
    # ========================================================================
    # MATHEMATICS CONCEPTS
    # ========================================================================
    
    'quadratic': [
        {
            'id': 'cricket_ball_arc',
            'name': 'Cricket Ball Parabolic Path',
            'scene': 'cricket_field_side',
            'entities': ['ball', 'trajectory', 'parabola', 'graph_overlay'],
            'cultural_fit': 1.0,
            'difficulty': 'medium',
            'real_world_relevance': 0.95,
            'engagement': 1.0,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['cricket', 'parabola', 'arc', 'trajectory']
        },
        {
            'id': 'fountain_water',
            'name': 'Fountain Water Arc',
            'scene': 'park_fountain',
            'entities': ['water_jets', 'arc_paths', 'parabola_shape'],
            'cultural_fit': 0.85,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.8,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['fountain', 'water', 'arc', 'parabola']
        },
        {
            'id': 'bridge_arch',
            'name': 'Bridge Arch Structure',
            'scene': 'bridge_side_view',
            'entities': ['bridge', 'arch', 'parabola_shape', 'support_points'],
            'cultural_fit': 0.8,
            'difficulty': 'medium',
            'real_world_relevance': 0.9,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['bridge', 'arch', 'parabola', 'structure']
        },
        {
            'id': 'profit_curve',
            'name': 'Shop Profit vs Price Curve',
            'scene': 'shop_graph',
            'entities': ['graph', 'price_axis', 'profit_axis', 'curve'],
            'cultural_fit': 0.85,
            'difficulty': 'hard',
            'real_world_relevance': 0.9,
            'engagement': 0.8,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['profit', 'price', 'optimization', 'business']
        },
        {
            'id': 'satellite_dish',
            'name': 'Satellite Dish Parabolic Shape',
            'scene': 'rooftop_satellite',
            'entities': ['dish', 'parabola', 'signals', 'receiver'],
            'cultural_fit': 0.8,
            'difficulty': 'medium',
            'real_world_relevance': 0.85,
            'engagement': 0.75,
            'age_group': 'high_school',
            'regions': ['all'],
            'keywords': ['satellite', 'dish', 'parabola', 'signals']
        }
    ],
    
    'linear': [
        {
            'id': 'rickshaw_meter',
            'name': 'Auto Rickshaw Fare Meter',
            'scene': 'auto_interior',
            'entities': ['meter', 'distance_display', 'fare_display', 'graph'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 1.0,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['auto', 'rickshaw', 'fare', 'meter', 'distance']
        },
        {
            'id': 'mobile_recharge',
            'name': 'Mobile Recharge Plans',
            'scene': 'recharge_screen',
            'entities': ['plans', 'price', 'data', 'graph_line'],
            'cultural_fit': 0.95,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.95,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['mobile', 'recharge', 'plans', 'price', 'data']
        },
        {
            'id': 'vegetable_pricing',
            'name': 'Vegetable Market Pricing',
            'scene': 'market_stall',
            'entities': ['vegetables', 'weighing_scale', 'price_board', 'rupees'],
            'cultural_fit': 1.0,
            'difficulty': 'easy',
            'real_world_relevance': 1.0,
            'engagement': 0.9,
            'age_group': 'middle_school',
            'regions': ['all'],
            'keywords': ['vegetables', 'market', 'price', 'weight', 'rupees']
        },
        {
            'id': 'stairs_climbing',
            'name': 'Climbing Building Stairs',
            'scene': 'staircase',
            'entities': ['stairs', 'person', 'height_markers', 'slope'],
            'cultural_fit': 0.85,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.8,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['stairs', 'climbing', 'slope', 'height']
        },
        {
            'id': 'water_filling',
            'name': 'Water Tank Filling Over Time',
            'scene': 'water_tank',
            'entities': ['tank', 'water_level', 'time_clock', 'pipe'],
            'cultural_fit': 0.9,
            'difficulty': 'easy',
            'real_world_relevance': 0.9,
            'engagement': 0.8,
            'age_group': 'all',
            'regions': ['all'],
            'keywords': ['water', 'tank', 'filling', 'time', 'rate']
        }
    ]
}

# ============================================================================
# METAPHOR SELECTOR - DYNAMIC SELECTION ENGINE
# ============================================================================

@dataclass
class SelectedMetaphor:
    """Result of metaphor selection"""
    metaphor_id: str
    name: str
    scene: str
    entities: List[str]
    selection_score: float
    selection_reasons: List[str]

class MetaphorSelector:
    """
    Dynamically selects the best metaphor for a concept based on:
    - Student profile (interests, region, age)
    - Concept difficulty
    - Cultural context
    - Previous effectiveness
    """
    
    def __init__(self):
        self.registry = METAPHOR_REGISTRY
        self.selection_history: Dict[str, List[str]] = {}  # Track what was used
    
    def select_metaphor(
        self,
        concept: str,
        student_profile: Optional[Dict[str, Any]] = None,
        difficulty: str = 'medium',
        complexity: str = 'medium'
    ) -> SelectedMetaphor:
        """
        Select best metaphor for concept and student
        
        Args:
            concept: Concept name (e.g., 'velocity')
            student_profile: Student info (region, interests, age)
            difficulty: Concept difficulty level
            complexity: Teaching complexity
            
        Returns:
            SelectedMetaphor with scene and entities
        """
        concept_lower = concept.lower()
        
        # Get available metaphors for concept
        metaphors = self.registry.get(concept_lower, [])
        
        if not metaphors:
            logger.warning(f"⚠️ No metaphors found for concept: {concept}, using fallback")
            return self._fallback_metaphor(concept)
        
        # Score each metaphor
        scored_metaphors = []
        for metaphor in metaphors:
            score = self._score_metaphor(metaphor, student_profile, difficulty, complexity)
            scored_metaphors.append((score, metaphor))
        
        # Sort by score (highest first)
        scored_metaphors.sort(key=lambda x: x[0], reverse=True)
        
        # Select top metaphor (with some randomness to avoid repetition)
        best_score, best_metaphor = scored_metaphors[0]
        
        # Check if we've used this recently
        used_count = self.selection_history.get(concept_lower, []).count(best_metaphor['id'])
        if used_count > 2 and len(scored_metaphors) > 1:
            # Use second best to add variety
            best_score, best_metaphor = scored_metaphors[1]
            logger.info(f"🔄 Using alternative metaphor for variety: {best_metaphor['name']}")
        
        # Track selection
        if concept_lower not in self.selection_history:
            self.selection_history[concept_lower] = []
        self.selection_history[concept_lower].append(best_metaphor['id'])
        
        logger.info(f"✅ Selected metaphor: {best_metaphor['name']} (score: {best_score:.2f})")
        
        return SelectedMetaphor(
            metaphor_id=best_metaphor['id'],
            name=best_metaphor['name'],
            scene=best_metaphor['scene'],
            entities=best_metaphor['entities'],
            selection_score=best_score,
            selection_reasons=self._get_selection_reasons(best_metaphor, student_profile)
        )
    
    def _score_metaphor(
        self,
        metaphor: Dict[str, Any],
        student_profile: Optional[Dict[str, Any]],
        difficulty: str,
        complexity: str
    ) -> float:
        """
        Score a metaphor based on multiple factors
        Returns score between 0 and 1
        """
        score = 0.0
        
        # Factor 1: Cultural fit (30%)
        score += metaphor.get('cultural_fit', 0.5) * 0.3
        
        # Factor 2: Difficulty match (25%)
        difficulty_match = 1.0 if metaphor.get('difficulty', 'medium') == difficulty else 0.7
        score += difficulty_match * 0.25
        
        # Factor 3: Real-world relevance (20%)
        score += metaphor.get('real_world_relevance', 0.5) * 0.2
        
        # Factor 4: Engagement potential (15%)
        score += metaphor.get('engagement', 0.5) * 0.15
        
        # Factor 5: Student profile match (10%)
        if student_profile:
            profile_score = self._match_student_profile(metaphor, student_profile)
            score += profile_score * 0.1
        else:
            score += 0.05  # Neutral if no profile
        
        return min(score, 1.0)
    
    def _match_student_profile(
        self,
        metaphor: Dict[str, Any],
        student_profile: Dict[str, Any]
    ) -> float:
        """Match metaphor to student profile"""
        match_score = 0.5  # Base score
        
        # Check region match
        student_region = student_profile.get('region', '')
        metaphor_regions = metaphor.get('regions', ['all'])
        if 'all' in metaphor_regions or student_region in metaphor_regions:
            match_score += 0.3
        
        # Check interests match
        student_interests = student_profile.get('interests', [])
        metaphor_keywords = metaphor.get('keywords', [])
        interest_overlap = any(
            interest.lower() in ' '.join(metaphor_keywords).lower()
            for interest in student_interests
        )
        if interest_overlap:
            match_score += 0.2
        
        return min(match_score, 1.0)
    
    def _get_selection_reasons(
        self,
        metaphor: Dict[str, Any],
        student_profile: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate human-readable reasons for selection"""
        reasons = []
        
        if metaphor.get('cultural_fit', 0) > 0.9:
            reasons.append("High cultural relevance for Indian students")
        
        if metaphor.get('engagement', 0) > 0.9:
            reasons.append("Highly engaging and memorable")
        
        if metaphor.get('real_world_relevance', 0) > 0.9:
            reasons.append("Direct real-world application")
        
        if student_profile and student_profile.get('region') in metaphor.get('regions', []):
            reasons.append(f"Matches your region ({student_profile.get('region')})")
        
        return reasons or ["Best fit for this concept"]
    
    def _fallback_metaphor(self, concept: str) -> SelectedMetaphor:
        """Fallback metaphor when none found in registry"""
        return SelectedMetaphor(
            metaphor_id='generic',
            name=f'Generic {concept} Explanation',
            scene='chalkboard',
            entities=['diagram', 'labels', 'arrows'],
            selection_score=0.5,
            selection_reasons=['Fallback generic metaphor']
        )
    
    def get_metaphor_count(self, concept: str) -> int:
        """Get number of available metaphors for a concept"""
        return len(self.registry.get(concept.lower(), []))
    
    def list_metaphors(self, concept: str) -> List[str]:
        """List all metaphor names for a concept"""
        metaphors = self.registry.get(concept.lower(), [])
        return [m['name'] for m in metaphors]

