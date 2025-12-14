/**
 * 🎨 VISUAL ONTOLOGY
 * ==================
 * 
 * The knowledge base that knows HOW concepts should LOOK.
 * 
 * This is NOT a template database. It's a semantic mapping from
 * conceptual understanding to visual representation.
 * 
 * Each concept has:
 * - Primary visual form (what it LOOKS like)
 * - Visual properties (color, size, style rules)
 * - Composition rules (how it relates to other visuals)
 * - Variation strategies (different ways to show it)
 * - Context adaptations (changes based on surrounding concepts)
 */

// ============================================
// VISUAL FORM TYPES
// ============================================

export const VISUAL_FORMS = {
  // Vectors & Arrows
  ARROW: 'arrow',                      // Simple directional arrow
  VECTOR: 'vector',                    // Arrow with magnitude indication
  DOUBLE_ARROW: 'double_arrow',        // Bidirectional
  CURVED_ARROW: 'curved_arrow',        // Curved path
  DASHED_ARROW: 'dashed_arrow',        // Implied or potential
  
  // Lines & Paths
  LINE: 'line',                        // Simple line
  PATH: 'path',                        // Curved/complex path
  TRAJECTORY: 'trajectory',            // Motion path
  WAVE: 'wave',                        // Sinusoidal
  HELIX: 'helix',                      // 3D spiral
  
  // Shapes
  CIRCLE: 'circle',                    // For point-like things
  ELLIPSE: 'ellipse',                  // For orbits, perspectives
  RECTANGLE: 'rectangle',              // Containers, blocks
  POLYGON: 'polygon',                  // Multi-sided
  BLOB: 'blob',                        // Organic shapes
  
  // Complex forms
  BODY: 'body',                        // Rigid body with shape
  STRUCTURE: 'structure',              // Organized multi-part
  NETWORK: 'network',                  // Connected nodes
  FIELD: 'field',                      // Gradient/field lines
  REGION: 'region',                    // Bounded area
  
  // Domain-specific
  ATOM: 'atom',                        // Bohr model
  MOLECULE: 'molecule',                // Ball-stick model
  CELL: 'cell',                        // Biological cell
  ORGAN: 'organ',                      // Anatomical shape
  GRAPH: 'graph',                      // Mathematical plot
  CIRCUIT: 'circuit',                  // Circuit diagram
};

// ============================================
// PHYSICS VISUAL ONTOLOGY
// ============================================

export const PHYSICS_ONTOLOGY = {
  // ========== FORCES ==========
  force: {
    primaryForm: VISUAL_FORMS.VECTOR,
    properties: {
      color: '#E74C3C',                // Red for forces
      strokeWidth: 3,
      headSize: 12,
      showMagnitude: true,
    },
    composition: {
      attachTo: 'body',                // Attaches to object's surface
      originAt: 'center_of_mass',      // Or 'surface', 'point_of_contact'
      direction: 'from_physics',       // Direction from physics
    },
    variations: {
      gravitational: { color: '#2C3E50', label: 'mg', direction: 'down' },
      normal: { color: '#3498DB', label: 'N', direction: 'perpendicular_to_surface' },
      friction: { color: '#E67E22', label: 'f', direction: 'opposite_to_motion' },
      tension: { color: '#9B59B6', label: 'T', direction: 'along_rope' },
      applied: { color: '#E74C3C', label: 'F', direction: 'specified' },
      spring: { color: '#27AE60', label: 'kx', direction: 'toward_equilibrium' },
    },
  },

  // ========== MOTION ==========
  velocity: {
    primaryForm: VISUAL_FORMS.VECTOR,
    properties: {
      color: '#3498DB',                // Blue for velocity
      strokeWidth: 2,
      headSize: 10,
      dashed: false,
      showMagnitude: true,
    },
    composition: {
      attachTo: 'body',
      originAt: 'center',
      tangentTo: 'path',               // Tangent to trajectory
    },
  },

  acceleration: {
    primaryForm: VISUAL_FORMS.VECTOR,
    properties: {
      color: '#9B59B6',                // Purple for acceleration
      strokeWidth: 2,
      headSize: 10,
      dashed: true,                    // Often shown dashed
    },
    composition: {
      attachTo: 'body',
      originAt: 'center',
    },
  },

  trajectory: {
    primaryForm: VISUAL_FORMS.TRAJECTORY,
    properties: {
      color: '#7F8C8D',
      strokeWidth: 1.5,
      dashed: true,                    // Path is often dashed
      showPoints: true,                // Dots along path
    },
    variations: {
      projectile: { pathType: 'parabola' },
      circular: { pathType: 'circle' },
      linear: { pathType: 'line' },
      oscillatory: { pathType: 'sinusoid' },
    },
  },

  // ========== OBJECTS ==========
  object: {
    primaryForm: VISUAL_FORMS.BODY,
    properties: {
      fill: '#ECF0F1',
      stroke: '#2C3E50',
      strokeWidth: 2,
    },
    variations: {
      block: { shape: 'rectangle', aspectRatio: 1.2 },
      ball: { shape: 'circle' },
      car: { shape: 'car_silhouette' },
      rocket: { shape: 'rocket_silhouette' },
      person: { shape: 'stick_figure' },
      planet: { shape: 'circle', size: 'large' },
    },
  },

  ground: {
    primaryForm: VISUAL_FORMS.LINE,
    properties: {
      color: '#2C3E50',
      strokeWidth: 2,
      hatching: true,                  // Hatched below line
      hatchAngle: -45,
    },
    composition: {
      position: 'bottom',
      span: 'full_width',
    },
  },

  incline: {
    primaryForm: VISUAL_FORMS.POLYGON,
    properties: {
      fill: '#ECF0F1',
      stroke: '#2C3E50',
      strokeWidth: 2,
      shape: 'right_triangle',
      showAngle: true,
    },
    composition: {
      anchorAt: 'base',
    },
  },

  // ========== SPRINGS & CONNECTORS ==========
  spring: {
    primaryForm: 'spring',             // Special zigzag shape
    properties: {
      color: '#2C3E50',
      strokeWidth: 2,
      coils: 8,
    },
    states: {
      equilibrium: { stretch: 0 },
      stretched: { stretch: '+' },
      compressed: { stretch: '-' },
    },
  },

  rope: {
    primaryForm: VISUAL_FORMS.LINE,
    properties: {
      color: '#8B4513',
      strokeWidth: 2,
      tension: 'taut',                 // or 'slack'
    },
  },

  pulley: {
    primaryForm: 'pulley',             // Circle with groove
    properties: {
      fill: '#BDC3C7',
      stroke: '#2C3E50',
      radius: 20,
      showAxle: true,
    },
  },

  // ========== WAVES & FIELDS ==========
  wave: {
    primaryForm: VISUAL_FORMS.WAVE,
    properties: {
      color: '#3498DB',
      strokeWidth: 2,
      amplitude: 30,
      wavelength: 60,
    },
    variations: {
      transverse: { direction: 'perpendicular' },
      longitudinal: { direction: 'parallel', showCompression: true },
      electromagnetic: { dualWave: true, colors: ['#E74C3C', '#3498DB'] },
    },
  },

  electric_field: {
    primaryForm: VISUAL_FORMS.FIELD,
    properties: {
      lineColor: '#E74C3C',
      lineSpacing: 30,
      showArrows: true,
    },
    patterns: {
      point_charge_positive: { radial: 'outward' },
      point_charge_negative: { radial: 'inward' },
      uniform: { parallel: true },
      dipole: { fieldLines: 'dipole_pattern' },
    },
  },

  magnetic_field: {
    primaryForm: VISUAL_FORMS.FIELD,
    properties: {
      lineColor: '#27AE60',
      showDirection: true,
    },
    symbols: {
      into_page: '⊗',
      out_of_page: '⊙',
    },
  },

  // ========== LIGHT ==========
  light_ray: {
    primaryForm: VISUAL_FORMS.ARROW,
    properties: {
      color: '#F1C40F',
      strokeWidth: 2,
      dashed: false,
    },
    behaviors: {
      reflection: { angleIn: 'equals', angleOut: true },
      refraction: { bendToward: 'normal', snellsLaw: true },
    },
  },

  mirror: {
    primaryForm: VISUAL_FORMS.LINE,
    properties: {
      color: '#7F8C8D',
      strokeWidth: 3,
      reflective: true,
      hatchBehind: true,
    },
    variations: {
      plane: { shape: 'line' },
      concave: { shape: 'arc_concave' },
      convex: { shape: 'arc_convex' },
    },
  },

  lens: {
    primaryForm: 'lens',
    properties: {
      fill: 'rgba(52, 152, 219, 0.2)',
      stroke: '#3498DB',
    },
    variations: {
      convex: { shape: 'biconvex' },
      concave: { shape: 'biconcave' },
    },
  },
};

// ============================================
// CHEMISTRY VISUAL ONTOLOGY
// ============================================

export const CHEMISTRY_ONTOLOGY = {
  atom: {
    primaryForm: VISUAL_FORMS.ATOM,
    properties: {
      showNucleus: true,
      showElectronShells: true,
      electronDots: true,
    },
    variations: {
      bohr_model: { shells: 'circular', electrons: 'dots' },
      lewis_dot: { showShells: false, valenceOnly: true },
      simplified: { justSymbol: true, charge: 'superscript' },
    },
  },

  molecule: {
    primaryForm: VISUAL_FORMS.MOLECULE,
    properties: {
      bondStyle: 'stick',
      atomStyle: 'ball',
      showBondAngles: false,
    },
    variations: {
      ball_and_stick: { atomSize: 'proportional' },
      structural: { flatRepresentation: true, showBonds: true },
      skeletal: { hideCarbon: true, hideHydrogen: true },
    },
  },

  chemical_bond: {
    primaryForm: VISUAL_FORMS.LINE,
    properties: {
      strokeWidth: 2,
    },
    variations: {
      single: { lines: 1 },
      double: { lines: 2, spacing: 3 },
      triple: { lines: 3, spacing: 2 },
      ionic: { dashed: true, showCharges: true },
      hydrogen: { dashed: true, color: '#3498DB' },
    },
  },

  reaction_arrow: {
    primaryForm: VISUAL_FORMS.ARROW,
    properties: {
      color: '#2C3E50',
      strokeWidth: 2,
    },
    variations: {
      forward: { direction: 'right' },
      reversible: { doubleHeaded: true },
      equilibrium: { arrows: 2, stacked: true },
    },
  },

  energy_diagram: {
    primaryForm: VISUAL_FORMS.GRAPH,
    properties: {
      xAxis: 'Reaction Progress',
      yAxis: 'Energy',
      showActivationEnergy: true,
    },
    elements: {
      reactants: { position: 'left', level: 'initial' },
      products: { position: 'right', level: 'final' },
      transition_state: { position: 'peak', marker: '‡' },
    },
  },

  beaker: {
    primaryForm: 'beaker',
    properties: {
      fill: 'rgba(52, 152, 219, 0.3)',
      showLiquidLevel: true,
      showGraduation: true,
    },
  },

  test_tube: {
    primaryForm: 'test_tube',
    properties: {
      fill: 'rgba(46, 204, 113, 0.3)',
      showLiquidLevel: true,
    },
  },
};

// ============================================
// BIOLOGY VISUAL ONTOLOGY
// ============================================

export const BIOLOGY_ONTOLOGY = {
  cell: {
    primaryForm: VISUAL_FORMS.CELL,
    properties: {
      membrane: true,
      nucleus: true,
    },
    variations: {
      animal: { shape: 'irregular', organelles: ['nucleus', 'mitochondria', 'er', 'golgi'] },
      plant: { shape: 'rectangular', cellWall: true, chloroplast: true, vacuole: 'large' },
      prokaryotic: { nucleus: false, shape: 'oval' },
    },
  },

  organelle: {
    primaryForm: VISUAL_FORMS.BLOB,
    variations: {
      nucleus: { shape: 'circle', fill: '#9B59B6', label: 'Nucleus' },
      mitochondria: { shape: 'oval', innerMembrane: 'folded', fill: '#E74C3C' },
      chloroplast: { shape: 'oval', thylakoids: true, fill: '#27AE60' },
      ribosome: { shape: 'small_dot', fill: '#3498DB' },
      endoplasmic_reticulum: { shape: 'wavy_network', rough: 'with_ribosomes' },
      golgi_apparatus: { shape: 'stacked_discs', fill: '#F39C12' },
      vacuole: { shape: 'large_circle', fill: 'rgba(52, 152, 219, 0.2)' },
    },
  },

  dna: {
    primaryForm: VISUAL_FORMS.HELIX,
    properties: {
      doubleHelix: true,
      showBasePairs: true,
      basePairColors: { AT: '#E74C3C', GC: '#3498DB' },
    },
    variations: {
      double_helix: { full3D: true },
      ladder: { flat: true, showBases: true },
      simplified: { singleLine: true, label: 'DNA' },
    },
  },

  chromosome: {
    primaryForm: 'chromosome',
    properties: {
      xShape: true,
      showCentromere: true,
    },
  },

  heart: {
    primaryForm: VISUAL_FORMS.ORGAN,
    properties: {
      chambers: 4,
      showValves: true,
      showBloodFlow: true,
      colors: { oxygenated: '#E74C3C', deoxygenated: '#3498DB' },
    },
  },

  neuron: {
    primaryForm: 'neuron',
    properties: {
      showDendrites: true,
      showAxon: true,
      showSynapses: true,
      showMyelinSheath: true,
    },
  },

  process_cycle: {
    primaryForm: VISUAL_FORMS.NETWORK,
    properties: {
      circular: true,
      showArrows: true,
      showSteps: true,
    },
    variations: {
      krebs_cycle: { steps: 8, enzymes: true },
      calvin_cycle: { steps: 3, showCO2: true },
      water_cycle: { naturalistic: true },
      cell_cycle: { phases: ['G1', 'S', 'G2', 'M'] },
    },
  },
};

// ============================================
// MATH VISUAL ONTOLOGY
// ============================================

export const MATH_ONTOLOGY = {
  coordinate_plane: {
    primaryForm: VISUAL_FORMS.GRAPH,
    properties: {
      showAxes: true,
      showGrid: true,
      showLabels: true,
      axisColor: '#2C3E50',
      gridColor: '#ECF0F1',
    },
    variations: {
      standard: { xRange: [-10, 10], yRange: [-10, 10] },
      first_quadrant: { xRange: [0, 10], yRange: [0, 10] },
      polar: { type: 'polar' },
    },
  },

  function_curve: {
    primaryForm: VISUAL_FORMS.PATH,
    properties: {
      color: '#3498DB',
      strokeWidth: 2,
      smooth: true,
    },
    variations: {
      linear: { expression: 'ax + b' },
      quadratic: { expression: 'ax² + bx + c' },
      cubic: { expression: 'ax³ + ...' },
      exponential: { expression: 'a^x' },
      logarithmic: { expression: 'log(x)' },
      trigonometric: { expression: 'sin/cos/tan' },
    },
  },

  geometric_shape: {
    primaryForm: VISUAL_FORMS.POLYGON,
    properties: {
      showLabels: true,
      showMeasurements: true,
    },
    variations: {
      triangle: { vertices: 3, showAngles: true },
      square: { vertices: 4, rightAngles: true },
      rectangle: { vertices: 4, showDimensions: true },
      circle: { shape: 'circle', showRadius: true },
      polygon: { vertices: 'n', regular: true },
    },
  },

  angle: {
    primaryForm: 'angle_arc',
    properties: {
      showArc: true,
      showMeasure: true,
      arcRadius: 20,
    },
    markers: {
      right_angle: '□',
      congruent: '≅',
    },
  },

  vector_math: {
    primaryForm: VISUAL_FORMS.VECTOR,
    properties: {
      color: '#E74C3C',
      showComponents: true,
      showMagnitude: true,
    },
  },

  number_line: {
    primaryForm: VISUAL_FORMS.LINE,
    properties: {
      showTicks: true,
      showLabels: true,
      arrowEnds: true,
    },
  },

  venn_diagram: {
    primaryForm: 'venn',
    properties: {
      circles: 2,
      showLabels: true,
      showIntersection: true,
      fillOpacity: 0.3,
    },
  },

  bar_graph: {
    primaryForm: 'bar_graph',
    properties: {
      orientation: 'vertical',
      showValues: true,
      showAxes: true,
    },
  },

  pie_chart: {
    primaryForm: 'pie_chart',
    properties: {
      showLabels: true,
      showPercentages: true,
    },
  },
};

// ============================================
// UNIFIED ONTOLOGY ACCESS
// ============================================

const UNIFIED_ONTOLOGY = {
  physics: PHYSICS_ONTOLOGY,
  chemistry: CHEMISTRY_ONTOLOGY,
  biology: BIOLOGY_ONTOLOGY,
  math: MATH_ONTOLOGY,
  mathematics: MATH_ONTOLOGY,
};

/**
 * Get visual specification for a concept
 * @param {string} domain - physics, chemistry, biology, math
 * @param {string} concept - The concept name (e.g., 'force', 'atom')
 * @param {string} variation - Optional specific variation
 */
export function getVisualSpec(domain, concept, variation = null) {
  const domainOntology = UNIFIED_ONTOLOGY[domain.toLowerCase()];
  if (!domainOntology) {
    console.warn(`Unknown domain: ${domain}`);
    return null;
  }

  const conceptSpec = domainOntology[concept.toLowerCase()];
  if (!conceptSpec) {
    console.warn(`Unknown concept: ${concept} in domain ${domain}`);
    return null;
  }

  // Apply variation if specified
  if (variation && conceptSpec.variations) {
    const variantSpec = conceptSpec.variations[variation.toLowerCase()];
    if (variantSpec) {
      return {
        ...conceptSpec,
        properties: { ...conceptSpec.properties, ...variantSpec },
        appliedVariation: variation,
      };
    }
  }

  return conceptSpec;
}

/**
 * Get all concepts for a domain
 */
export function getDomainConcepts(domain) {
  const domainOntology = UNIFIED_ONTOLOGY[domain.toLowerCase()];
  if (!domainOntology) return [];
  return Object.keys(domainOntology);
}

/**
 * Search for matching visual spec across domains
 */
export function findVisualSpec(concept) {
  const conceptLower = concept.toLowerCase();
  
  for (const [domain, ontology] of Object.entries(UNIFIED_ONTOLOGY)) {
    if (ontology[conceptLower]) {
      return {
        domain,
        concept: conceptLower,
        spec: ontology[conceptLower],
      };
    }
  }

  // Try partial matching
  for (const [domain, ontology] of Object.entries(UNIFIED_ONTOLOGY)) {
    for (const [name, spec] of Object.entries(ontology)) {
      if (name.includes(conceptLower) || conceptLower.includes(name)) {
        return { domain, concept: name, spec };
      }
    }
  }

  return null;
}

export default {
  VISUAL_FORMS,
  PHYSICS_ONTOLOGY,
  CHEMISTRY_ONTOLOGY,
  BIOLOGY_ONTOLOGY,
  MATH_ONTOLOGY,
  getVisualSpec,
  getDomainConcepts,
  findVisualSpec,
};



