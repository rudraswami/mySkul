"""
Scene Builder - Visual Environments and Entity Library
Defines scenes, entities, and SVG components for Visual Professor Engine
Supports custom scenes with entity composition
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# ============================================================================
# SCENE DEFINITIONS
# ============================================================================

SCENES: Dict[str, Dict[str, Any]] = {
    # PHYSICS SCENES
    'delhi_metro_road': {
        'subject': 'physics',
        'background': 'city_skyline_gradient',
        'ambient': 'urban',
        'color_scheme': ['#7c3aed', '#a78bfa', '#ddd6fe'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'metro_train': {
                'type': 'vehicle',
                'sprite_type': 'svg_component',
                'animation_paths': ['move_straight', 'turn_corner', 'stop'],
                'size': {'width': 120, 'height': 60},
                'initial_position': {'x': 100, 'y': 400}
            },
            'direction_arrow': {
                'type': 'indicator',
                'sprite_type': 'svg_component',
                'animation_paths': ['rotate', 'pulse', 'fade'],
                'size': {'width': 80, 'height': 80},
                'initial_position': {'x': 400, 'y': 200}
            },
            'speedometer': {
                'type': 'gauge',
                'sprite_type': 'svg_component',
                'animation_paths': ['needle_rotate', 'digital_count'],
                'size': {'width': 100, 'height': 100},
                'initial_position': {'x': 650, 'y': 100}
            },
            'landmark_a': {
                'type': 'marker',
                'sprite_type': 'svg_component',
                'size': {'width': 40, 'height': 60},
                'initial_position': {'x': 50, 'y': 450}
            },
            'landmark_b': {
                'type': 'marker',
                'sprite_type': 'svg_component',
                'size': {'width': 40, 'height': 60},
                'initial_position': {'x': 700, 'y': 450}
            }
        },
        'lottie_pack': 'physics/motion',
        'description': 'Urban road with metro train for motion concepts'
    },
    
    'cricket_field': {
        'subject': 'physics',
        'background': 'stadium_grass',
        'ambient': 'outdoor_sports',
        'color_scheme': ['#15803d', '#22c55e', '#86efac'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'cricket_ball': {
                'type': 'projectile',
                'sprite_type': 'svg_component',
                'animation_paths': ['arc_motion', 'rotate_spin', 'bounce'],
                'size': {'width': 30, 'height': 30},
                'initial_position': {'x': 100, 'y': 500}
            },
            'trajectory_arc': {
                'type': 'path',
                'sprite_type': 'svg_path',
                'animation_paths': ['draw_path', 'fade_in'],
                'stroke_dasharray': '5,5'
            },
            'velocity_vectors': {
                'type': 'vector_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['vector_show', 'vector_decompose'],
                'size': {'width': 150, 'height': 150}
            },
            'gravity_arrow': {
                'type': 'force_indicator',
                'sprite_type': 'svg_component',
                'animation_paths': ['pulse', 'point_down'],
                'size': {'width': 60, 'height': 100}
            },
            'ground': {
                'type': 'reference_line',
                'sprite_type': 'svg_line',
                'position_y': 550
            }
        },
        'lottie_pack': 'physics/projectile',
        'description': 'Cricket stadium for projectile motion'
    },
    
    'highway_road': {
        'subject': 'physics',
        'background': 'highway_landscape',
        'ambient': 'outdoor_road',
        'color_scheme': ['#1e40af', '#3b82f6', '#93c5fd'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'car': {
                'type': 'vehicle',
                'sprite_type': 'svg_component',
                'animation_paths': ['drive_forward', 'brake', 'stop'],
                'size': {'width': 100, 'height': 50},
                'initial_position': {'x': 100, 'y': 450}
            },
            'friction_arrows': {
                'type': 'force_indicator',
                'sprite_type': 'svg_component',
                'animation_paths': ['show_friction', 'increase_magnitude'],
                'size': {'width': 80, 'height': 40}
            },
            'velocity_arrow': {
                'type': 'vector',
                'sprite_type': 'svg_component',
                'animation_paths': ['extend', 'shrink', 'fade'],
                'size': {'width': 120, 'height': 40}
            },
            'obstacle': {
                'type': 'marker',
                'sprite_type': 'svg_component',
                'size': {'width': 60, 'height': 80},
                'initial_position': {'x': 600, 'y': 430}
            }
        },
        'lottie_pack': 'physics/forces',
        'description': 'Highway for Newton laws and motion'
    },
    
    # CHEMISTRY SCENES
    'electron_shell_space': {
        'subject': 'chemistry',
        'background': 'atom_space_gradient',
        'ambient': 'molecular',
        'color_scheme': ['#059669', '#10b981', '#6ee7b7'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'atom_nucleus': {
                'type': 'nucleus',
                'sprite_type': 'svg_component',
                'animation_paths': ['pulse_glow', 'rotate'],
                'size': {'width': 60, 'height': 60},
                'initial_position': {'x': 400, 'y': 300}
            },
            'electron_shells': {
                'type': 'orbital_rings',
                'sprite_type': 'svg_component',
                'animation_paths': ['rotate_orbits', 'highlight_valence'],
                'shells': [1, 2, 3]
            },
            'electrons': {
                'type': 'particle_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['orbit_motion', 'jump_shell', 'glow'],
                'count': 10,
                'size': {'width': 20, 'height': 20}
            },
            'empty_slots': {
                'type': 'placeholder_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['pulse', 'highlight'],
                'size': {'width': 20, 'height': 20}
            },
            'bonding_hand': {
                'type': 'indicator',
                'sprite_type': 'svg_component',
                'animation_paths': ['extend', 'retract', 'point'],
                'size': {'width': 80, 'height': 80}
            }
        },
        'lottie_pack': 'chemistry/bonding',
        'description': 'Atom with electron shells for valency'
    },
    
    'laboratory_bench': {
        'subject': 'chemistry',
        'background': 'lab_bench_surface',
        'ambient': 'laboratory',
        'color_scheme': ['#dc2626', '#ef4444', '#fca5a5'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'ph_scale': {
                'type': 'gauge',
                'sprite_type': 'svg_component',
                'animation_paths': ['indicator_slide', 'color_change'],
                'size': {'width': 400, 'height': 80},
                'initial_position': {'x': 200, 'y': 100}
            },
            'test_tubes': {
                'type': 'container_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['fill_liquid', 'bubble', 'change_color'],
                'count': 3,
                'size': {'width': 40, 'height': 120}
            },
            'acid_molecules': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['dissociate', 'move_random', 'release_ion'],
                'count': 15,
                'size': {'width': 25, 'height': 25}
            },
            'indicator_paper': {
                'type': 'test_strip',
                'sprite_type': 'svg_component',
                'animation_paths': ['dip', 'color_change'],
                'size': {'width': 30, 'height': 100}
            },
            'color_gradient': {
                'type': 'visual_aid',
                'sprite_type': 'svg_gradient',
                'colors': ['#dc2626', '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#06b6d4', '#3b82f6']
            }
        },
        'lottie_pack': 'chemistry/reactions',
        'description': 'Laboratory setup for acid-base experiments'
    },
    
    'molecule_space': {
        'subject': 'chemistry',
        'background': 'molecular_void',
        'ambient': 'molecular',
        'color_scheme': ['#7c3aed', '#a78bfa', '#ddd6fe'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'atom_1': {
                'type': 'atom',
                'sprite_type': 'svg_component',
                'animation_paths': ['move_closer', 'vibrate', 'glow'],
                'size': {'width': 80, 'height': 80},
                'initial_position': {'x': 250, 'y': 300}
            },
            'atom_2': {
                'type': 'atom',
                'sprite_type': 'svg_component',
                'animation_paths': ['move_closer', 'vibrate', 'glow'],
                'size': {'width': 80, 'height': 80},
                'initial_position': {'x': 550, 'y': 300}
            },
            'electron_cloud': {
                'type': 'cloud',
                'sprite_type': 'svg_component',
                'animation_paths': ['overlap', 'pulse', 'merge'],
                'size': {'width': 150, 'height': 100}
            },
            'bond_line': {
                'type': 'bond',
                'sprite_type': 'svg_line',
                'animation_paths': ['draw', 'strengthen', 'pulse'],
                'stroke_width_range': [2, 6]
            },
            'shared_electrons': {
                'type': 'particle_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['orbit_both', 'highlight'],
                'count': 2,
                'size': {'width': 15, 'height': 15}
            }
        },
        'lottie_pack': 'chemistry/bonding',
        'description': 'Molecular space for bonding visualization'
    },
    
    # BIOLOGY SCENES
    'leaf_cross_section': {
        'subject': 'biology',
        'background': 'leaf_interior',
        'ambient': 'cellular',
        'color_scheme': ['#15803d', '#22c55e', '#86efac'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'chloroplast': {
                'type': 'organelle',
                'sprite_type': 'svg_component',
                'animation_paths': ['pulse_glow', 'highlight', 'zoom_in'],
                'size': {'width': 120, 'height': 80},
                'initial_position': {'x': 400, 'y': 300}
            },
            'sunlight_rays': {
                'type': 'energy_indicator',
                'sprite_type': 'svg_component',
                'animation_paths': ['beam_down', 'pulse', 'scatter'],
                'count': 5,
                'size': {'width': 10, 'height': 200}
            },
            'co2_molecules': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['enter_stomata', 'move_to_chloroplast'],
                'count': 8,
                'size': {'width': 25, 'height': 25}
            },
            'water_molecules': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['flow_up', 'enter_chloroplast'],
                'count': 10,
                'size': {'width': 20, 'height': 20}
            },
            'glucose': {
                'type': 'molecule',
                'sprite_type': 'svg_component',
                'animation_paths': ['form', 'glow', 'move_out'],
                'size': {'width': 60, 'height': 60}
            },
            'oxygen': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['form', 'float_up', 'exit_stomata'],
                'count': 6,
                'size': {'width': 30, 'height': 30}
            }
        },
        'lottie_pack': 'biology/photosynthesis',
        'description': 'Cross-section of leaf for photosynthesis'
    },
    
    'mitochondria_interior': {
        'subject': 'biology',
        'background': 'organelle_interior',
        'ambient': 'cellular',
        'color_scheme': ['#dc2626', '#f87171', '#fecaca'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'mitochondria': {
                'type': 'organelle',
                'sprite_type': 'svg_component',
                'animation_paths': ['pulse', 'cristae_highlight', 'glow'],
                'size': {'width': 200, 'height': 150},
                'initial_position': {'x': 400, 'y': 300}
            },
            'glucose_molecule': {
                'type': 'molecule',
                'sprite_type': 'svg_component',
                'animation_paths': ['enter', 'break_apart', 'fade'],
                'size': {'width': 60, 'height': 60}
            },
            'oxygen_molecules': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['enter', 'combine', 'react'],
                'count': 6,
                'size': {'width': 30, 'height': 30}
            },
            'atp_energy': {
                'type': 'energy_unit',
                'sprite_type': 'svg_component',
                'animation_paths': ['form', 'pulse_bright', 'accumulate'],
                'count': 10,
                'size': {'width': 40, 'height': 40}
            },
            'co2_waste': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['form', 'float_out', 'fade'],
                'count': 6,
                'size': {'width': 25, 'height': 25}
            },
            'water_product': {
                'type': 'molecule_group',
                'sprite_type': 'svg_component',
                'animation_paths': ['form', 'disperse'],
                'count': 4,
                'size': {'width': 20, 'height': 20}
            }
        },
        'lottie_pack': 'biology/respiration',
        'description': 'Mitochondria interior for cellular respiration'
    },
    
    # MATHEMATICS SCENES
    'graph_coordinate_space': {
        'subject': 'mathematics',
        'background': 'grid_paper',
        'ambient': 'analytical',
        'color_scheme': ['#2563eb', '#60a5fa', '#bfdbfe'],
        'dimensions': {'width': 800, 'height': 600},
        'entities': {
            'x_axis': {
                'type': 'axis',
                'sprite_type': 'svg_line',
                'animation_paths': ['draw', 'extend'],
                'with_arrows': True,
                'position_y': 500
            },
            'y_axis': {
                'type': 'axis',
                'sprite_type': 'svg_line',
                'animation_paths': ['draw', 'extend'],
                'with_arrows': True,
                'position_x': 100
            },
            'parabola_curve': {
                'type': 'function_curve',
                'sprite_type': 'svg_path',
                'animation_paths': ['draw_smooth', 'highlight'],
                'stroke_width': 3
            },
            'line': {
                'type': 'function_curve',
                'sprite_type': 'svg_line',
                'animation_paths': ['draw', 'extend', 'highlight'],
                'stroke_width': 3
            },
            'vertex_point': {
                'type': 'point',
                'sprite_type': 'svg_circle',
                'animation_paths': ['appear', 'pulse', 'label_show'],
                'radius': 8
            },
            'roots': {
                'type': 'point_group',
                'sprite_type': 'svg_circle',
                'animation_paths': ['appear', 'pulse'],
                'count': 2,
                'radius': 6
            },
            'slope_triangle': {
                'type': 'indicator',
                'sprite_type': 'svg_path',
                'animation_paths': ['draw', 'label_sides'],
                'size': {'width': 80, 'height': 60}
            },
            'y_intercept_point': {
                'type': 'point',
                'sprite_type': 'svg_circle',
                'animation_paths': ['appear', 'pulse', 'label_show'],
                'radius': 8
            },
            'equation_label': {
                'type': 'text_label',
                'sprite_type': 'svg_text',
                'animation_paths': ['fade_in', 'highlight'],
                'font_size': 24
            }
        },
        'lottie_pack': 'math/graphs',
        'description': 'Coordinate plane for graphing functions'
    }
}

# ============================================================================
# SVG ENTITY COMPONENTS (Complete SVG code for each entity type)
# ============================================================================

SVG_COMPONENTS: Dict[str, str] = {
    # PHYSICS ENTITIES
    'metro_train': '''
<g id="metro-train" class="entity-metro-train">
  <rect x="0" y="20" width="120" height="40" rx="8" fill="#7c3aed" stroke="#5b21b6" stroke-width="2"/>
  <rect x="10" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
  <rect x="45" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
  <rect x="85" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
  <circle cx="30" cy="62" r="6" fill="#1e293b"/>
  <circle cx="90" cy="62" r="6" fill="#1e293b"/>
  <path d="M 0 30 L -10 40 L -10 50 L 0 60" fill="#5b21b6"/>
  <text x="60" y="42" text-anchor="middle" fill="white" font-size="12" font-weight="bold">METRO</text>
</g>
''',
    
    'direction_arrow': '''
<g id="direction-arrow" class="entity-direction-arrow">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#dc2626"/>
    </marker>
  </defs>
  <line x1="10" y1="40" x2="70" y2="40" stroke="#dc2626" stroke-width="4" marker-end="url(#arrowhead)"/>
  <text x="40" y="25" text-anchor="middle" fill="#dc2626" font-size="14" font-weight="bold">DIRECTION</text>
  <circle cx="40" cy="40" r="35" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="5,5" opacity="0.5"/>
</g>
''',
    
    'speedometer': '''
<g id="speedometer" class="entity-speedometer">
  <circle cx="50" cy="60" r="45" fill="white" stroke="#1e293b" stroke-width="3"/>
  <circle cx="50" cy="60" r="38" fill="none" stroke="#e2e8f0" stroke-width="2"/>
  <!-- Speed marks -->
  <line x1="50" y1="25" x2="50" y2="30" stroke="#475569" stroke-width="2"/>
  <line x1="78" y1="32" x2="74" y2="36" stroke="#475569" stroke-width="2"/>
  <line x1="88" y1="60" x2="83" y2="60" stroke="#475569" stroke-width="2"/>
  <line x1="78" y1="88" x2="74" y2="84" stroke="#475569" stroke-width="2"/>
  <line x1="50" y1="95" x2="50" y2="90" stroke="#475569" stroke-width="2"/>
  <line x1="22" y1="88" x2="26" y2="84" stroke="#475569" stroke-width="2"/>
  <line x1="12" y1="60" x2="17" y2="60" stroke="#475569" stroke-width="2"/>
  <line x1="22" y1="32" x2="26" y2="36" stroke="#475569" stroke-width="2"/>
  <!-- Needle -->
  <line x1="50" y1="60" x2="70" y2="45" stroke="#dc2626" stroke-width="3" stroke-linecap="round" class="speedometer-needle"/>
  <circle cx="50" cy="60" r="5" fill="#dc2626"/>
  <!-- Label -->
  <text x="50" y="80" text-anchor="middle" fill="#1e293b" font-size="12" font-weight="bold">km/h</text>
</g>
''',
    
    'cricket_ball': '''
<g id="cricket-ball" class="entity-cricket-ball">
  <circle cx="15" cy="15" r="14" fill="#dc2626" stroke="#991b1b" stroke-width="2"/>
  <path d="M 5 8 Q 15 12 25 8" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M 5 22 Q 15 18 25 22" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="15" cy="15" r="14" fill="none" stroke="#991b1b" stroke-width="1" opacity="0.3"/>
</g>
''',
    
    'car': '''
<g id="car" class="entity-car">
  <rect x="10" y="20" width="80" height="20" rx="4" fill="#3b82f6" stroke="#1e40af" stroke-width="2"/>
  <rect x="20" y="10" width="25" height="12" rx="3" fill="#60a5fa" opacity="0.7"/>
  <rect x="50" y="10" width="30" height="12" rx="3" fill="#60a5fa" opacity="0.7"/>
  <circle cx="25" cy="42" r="6" fill="#1e293b"/>
  <circle cx="25" cy="42" r="3" fill="#64748b"/>
  <circle cx="75" cy="42" r="6" fill="#1e293b"/>
  <circle cx="75" cy="42" r="3" fill="#64748b"/>
  <circle cx="88" cy="25" r="4" fill="#fef08a" opacity="0.9"/>
  <circle cx="88" cy="25" r="2" fill="#fde047"/>
</g>
''',
    
    # CHEMISTRY ENTITIES
    'atom_nucleus': '''
<g id="atom-nucleus" class="entity-atom-nucleus">
  <circle cx="30" cy="30" r="25" fill="url(#nucleus-gradient)" stroke="#059669" stroke-width="3"/>
  <defs>
    <radialGradient id="nucleus-gradient">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </radialGradient>
  </defs>
  <circle cx="22" cy="24" r="8" fill="#10b981" opacity="0.7"/>
  <circle cx="38" cy="28" r="8" fill="#10b981" opacity="0.7"/>
  <circle cx="30" cy="36" r="8" fill="#10b981" opacity="0.7"/>
  <text x="30" y="35" text-anchor="middle" fill="white" font-size="14" font-weight="bold">+</text>
  <circle cx="30" cy="30" r="28" fill="none" stroke="#6ee7b7" stroke-width="1" opacity="0.4" class="nucleus-glow"/>
</g>
''',
    
    'electron': '''
<g id="electron" class="entity-electron">
  <circle cx="10" cy="10" r="8" fill="#3b82f6" stroke="#1e40af" stroke-width="2"/>
  <circle cx="10" cy="10" r="6" fill="url(#electron-gradient)"/>
  <defs>
    <radialGradient id="electron-gradient">
      <stop offset="0%" stop-color="#93c5fd"/>
      <stop offset="100%" stop-color="#3b82f6"/>
    </radialGradient>
  </defs>
  <text x="10" y="13" text-anchor="middle" fill="white" font-size="10" font-weight="bold">e⁻</text>
  <circle cx="10" cy="10" r="12" fill="none" stroke="#60a5fa" stroke-width="1" opacity="0.3" class="electron-glow"/>
</g>
''',
    
    'electron_shell': '''
<g id="electron-shell" class="entity-electron-shell">
  <circle cx="400" cy="300" r="{radius}" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="5,5" opacity="0.6" class="electron-shell-ring"/>
</g>
''',
    
    'test_tube': '''
<g id="test-tube" class="entity-test-tube">
  <rect x="15" y="10" width="10" height="100" rx="5" fill="none" stroke="#64748b" stroke-width="2"/>
  <rect x="15" y="{liquid_level}" width="10" height="{liquid_height}" fill="{liquid_color}" opacity="0.7"/>
  <rect x="12" y="5" width="16" height="8" rx="2" fill="#94a3b8"/>
  <circle cx="20" cy="115" r="8" fill="none" stroke="#64748b" stroke-width="2"/>
</g>
''',
    
    'ph_scale': '''
<g id="ph-scale" class="entity-ph-scale">
  <rect x="0" y="0" width="400" height="60" rx="8" fill="url(#ph-gradient)" stroke="#64748b" stroke-width="2"/>
  <defs>
    <linearGradient id="ph-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#dc2626"/>
      <stop offset="15%" stop-color="#f59e0b"/>
      <stop offset="30%" stop-color="#eab308"/>
      <stop offset="45%" stop-color="#84cc16"/>
      <stop offset="50%" stop-color="#22c55e"/>
      <stop offset="65%" stop-color="#06b6d4"/>
      <stop offset="85%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
  </defs>
  <!-- pH markers -->
  <text x="28" y="45" text-anchor="middle" fill="white" font-size="16" font-weight="bold">0</text>
  <text x="114" y="45" text-anchor="middle" fill="white" font-size="16" font-weight="bold">3</text>
  <text x="200" y="45" text-anchor="middle" fill="white" font-size="16" font-weight="bold">7</text>
  <text x="286" y="45" text-anchor="middle" fill="white" font-size="16" font-weight="bold">10</text>
  <text x="372" y="45" text-anchor="middle" fill="white" font-size="16" font-weight="bold">14</text>
  <!-- Indicator pointer -->
  <polygon points="200,-10 195,0 205,0" fill="#1e293b" class="ph-indicator"/>
</g>
''',
    
    # BIOLOGY ENTITIES
    'chloroplast': '''
<g id="chloroplast" class="entity-chloroplast">
  <ellipse cx="60" cy="40" rx="55" ry="35" fill="#22c55e" stroke="#15803d" stroke-width="3" opacity="0.9"/>
  <ellipse cx="60" cy="40" rx="50" ry="30" fill="url(#chloroplast-gradient)"/>
  <defs>
    <radialGradient id="chloroplast-gradient">
      <stop offset="0%" stop-color="#86efac"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </radialGradient>
  </defs>
  <!-- Grana stacks -->
  <rect x="30" y="25" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
  <rect x="32" y="28" width="11" height="2" fill="#052e16" opacity="0.8"/>
  <rect x="55" y="32" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
  <rect x="57" y="35" width="11" height="2" fill="#052e16" opacity="0.8"/>
  <rect x="75" y="20" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
  <rect x="77" y="23" width="11" height="2" fill="#052e16" opacity="0.8"/>
  <ellipse cx="60" cy="40" rx="58" ry="38" fill="none" stroke="#86efac" stroke-width="2" opacity="0.4" class="chloroplast-glow"/>
</g>
''',
    
    'mitochondria': '''
<g id="mitochondria" class="entity-mitochondria">
  <ellipse cx="100" cy="75" rx="95" ry="70" fill="#ef4444" stroke="#dc2626" stroke-width="3" opacity="0.9"/>
  <ellipse cx="100" cy="75" rx="90" ry="65" fill="url(#mitochondria-gradient)"/>
  <defs>
    <radialGradient id="mitochondria-gradient">
      <stop offset="0%" stop-color="#fca5a5"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </radialGradient>
  </defs>
  <!-- Cristae folds -->
  <path d="M 30 50 Q 40 60 30 70 Q 40 80 30 90" stroke="#991b1b" stroke-width="2" fill="none" opacity="0.7"/>
  <path d="M 50 45 Q 60 55 50 65 Q 60 75 50 85 Q 60 95 50 105" stroke="#991b1b" stroke-width="2" fill="none" opacity="0.7"/>
  <path d="M 70 50 Q 80 60 70 70 Q 80 80 70 90" stroke="#991b1b" stroke-width="2" fill="none" opacity="0.7"/>
  <path d="M 120 50 Q 130 60 120 70 Q 130 80 120 90" stroke="#991b1b" stroke-width="2" fill="none" opacity="0.7"/>
  <path d="M 150 45 Q 160 55 150 65 Q 160 75 150 85 Q 160 95 150 105" stroke="#991b1b" stroke-width="2" fill="none" opacity="0.7"/>
  <ellipse cx="100" cy="75" rx="98" ry="73" fill="none" stroke="#fca5a5" stroke-width="2" opacity="0.4" class="mitochondria-glow"/>
</g>
''',
    
    # MATH ENTITIES
    'axis': '''
<g id="axis" class="entity-axis">
  <line x1="50" y1="{y}" x2="750" y2="{y}" stroke="#64748b" stroke-width="2"/>
  <polygon points="750,{y} 745,{y_minus_5} 745,{y_plus_5}" fill="#64748b"/>
  <line x1="{x}" y1="50" x2="{x}" y2="550" stroke="#64748b" stroke-width="2"/>
  <polygon points="{x},50 {x_minus_5},55 {x_plus_5},55" fill="#64748b"/>
</g>
''',
    
    'point': '''
<g id="point" class="entity-point">
  <circle cx="0" cy="0" r="8" fill="#dc2626" stroke="#991b1b" stroke-width="2"/>
  <circle cx="0" cy="0" r="6" fill="#ef4444"/>
  <circle cx="0" cy="0" r="12" fill="none" stroke="#fca5a5" stroke-width="2" opacity="0.4" class="point-glow"/>
</g>
''',
    
    'parabola': '''
<path id="parabola" class="entity-parabola" 
  d="M {start_x} {start_y} Q {control_x} {control_y} {end_x} {end_y}" 
  stroke="#3b82f6" stroke-width="3" fill="none" stroke-linecap="round"/>
''',
    
    'line': '''
<line id="line" class="entity-line" 
  x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
  stroke="#3b82f6" stroke-width="3" stroke-linecap="round"/>
'''
}

# ============================================================================
# CUSTOM SCENE BUILDER
# ============================================================================

@dataclass
class CustomScene:
    """Custom scene configuration"""
    name: str
    subject: str
    background: str
    dimensions: Dict[str, int]
    entities: Dict[str, Any]
    color_scheme: List[str]
    lottie_pack: Optional[str] = None
    
def create_custom_scene(
    name: str,
    subject: str,
    background: str = 'gradient_default',
    dimensions: Optional[Dict[str, int]] = None,
    color_scheme: Optional[List[str]] = None
) -> CustomScene:
    """
    Create a custom scene with default settings
    Allows full customization while providing sensible defaults
    """
    return CustomScene(
        name=name,
        subject=subject,
        background=background,
        dimensions=dimensions or {'width': 800, 'height': 600},
        entities={},
        color_scheme=color_scheme or ['#3b82f6', '#60a5fa', '#93c5fd'],
        lottie_pack=None
    )

def add_entity_to_scene(
    scene: CustomScene,
    entity_id: str,
    entity_type: str,
    position: Dict[str, int],
    size: Optional[Dict[str, int]] = None,
    animation_paths: Optional[List[str]] = None
) -> CustomScene:
    """Add a custom entity to a scene"""
    scene.entities[entity_id] = {
        'type': entity_type,
        'sprite_type': 'svg_component',
        'initial_position': position,
        'size': size or {'width': 60, 'height': 60},
        'animation_paths': animation_paths or ['fade_in', 'pulse']
    }
    return scene

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_scene(scene_name: str) -> Optional[Dict[str, Any]]:
    """Get scene definition by name"""
    return SCENES.get(scene_name)

def get_svg_component(component_name: str, **kwargs) -> str:
    """
    Get SVG component with template variable substitution
    
    Args:
        component_name: Name of the component
        **kwargs: Template variables to substitute
    
    Returns:
        SVG string with variables replaced
    """
    template = SVG_COMPONENTS.get(component_name, '')
    # Simple template variable substitution
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template

def list_scenes_by_subject(subject: str) -> List[str]:
    """List all scenes for a given subject"""
    return [
        name
        for name, scene in SCENES.items()
        if scene['subject'].lower() == subject.lower()
    ]

def get_scene_entities(scene_name: str) -> List[str]:
    """Get list of entity names in a scene"""
    scene = SCENES.get(scene_name)
    if scene:
        return list(scene['entities'].keys())
    return []

