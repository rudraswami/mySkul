/**
 * conceptGraph.js
 * Phase 5: Concept relationship graph for cross-concept linking
 * 
 * Defines:
 * - Prerequisites for each concept
 * - Related concepts
 * - Learning paths
 * - Concept hierarchies
 */

export const CONCEPT_GRAPH = {
  // ============ PHYSICS ============
  physics: {
    // Mechanics
    force: {
      prerequisites: ['mass', 'acceleration'],
      leads_to: ['momentum', 'work', 'friction'],
      related: ['newton_laws', 'gravity', 'pressure'],
      difficulty: 'medium',
      chapter: 'Mechanics',
      class: [9, 11],
    },
    
    mass: {
      prerequisites: [],
      leads_to: ['force', 'momentum', 'density'],
      related: ['weight', 'inertia'],
      difficulty: 'easy',
      chapter: 'Mechanics',
      class: [9],
    },
    
    acceleration: {
      prerequisites: ['velocity', 'time'],
      leads_to: ['force', 'motion_equations'],
      related: ['deceleration', 'gravity'],
      difficulty: 'medium',
      chapter: 'Kinematics',
      class: [9, 11],
    },
    
    velocity: {
      prerequisites: ['displacement', 'time'],
      leads_to: ['acceleration', 'momentum'],
      related: ['speed', 'distance'],
      difficulty: 'easy',
      chapter: 'Kinematics',
      class: [9],
    },
    
    motion: {
      prerequisites: ['distance', 'time'],
      leads_to: ['velocity', 'acceleration', 'motion_equations'],
      related: ['rest', 'displacement'],
      difficulty: 'easy',
      chapter: 'Kinematics',
      class: [9],
    },
    
    motion_equations: {
      prerequisites: ['velocity', 'acceleration', 'time'],
      leads_to: ['projectile_motion', 'circular_motion'],
      related: ['kinematics', 'graphs'],
      difficulty: 'medium',
      chapter: 'Kinematics',
      class: [9, 11],
    },
    
    momentum: {
      prerequisites: ['mass', 'velocity'],
      leads_to: ['impulse', 'collision'],
      related: ['force', 'kinetic_energy'],
      difficulty: 'medium',
      chapter: 'Mechanics',
      class: [9, 11],
    },
    
    gravity: {
      prerequisites: ['force', 'mass'],
      leads_to: ['weight', 'free_fall', 'orbital_motion'],
      related: ['acceleration', 'potential_energy'],
      difficulty: 'medium',
      chapter: 'Gravitation',
      class: [9, 11],
    },
    
    friction: {
      prerequisites: ['force', 'normal_force'],
      leads_to: ['motion_on_surface', 'work'],
      related: ['coefficient_of_friction', 'air_resistance'],
      difficulty: 'medium',
      chapter: 'Mechanics',
      class: [9, 11],
    },
    
    work: {
      prerequisites: ['force', 'displacement'],
      leads_to: ['energy', 'power'],
      related: ['kinetic_energy', 'potential_energy'],
      difficulty: 'medium',
      chapter: 'Work & Energy',
      class: [9, 11],
    },
    
    energy: {
      prerequisites: ['work'],
      leads_to: ['kinetic_energy', 'potential_energy', 'conservation_of_energy'],
      related: ['power', 'heat'],
      difficulty: 'medium',
      chapter: 'Work & Energy',
      class: [9, 11],
    },
    
    kinetic_energy: {
      prerequisites: ['mass', 'velocity', 'energy'],
      leads_to: ['work_energy_theorem', 'collision'],
      related: ['potential_energy', 'momentum'],
      difficulty: 'medium',
      chapter: 'Work & Energy',
      class: [9, 11],
    },
    
    potential_energy: {
      prerequisites: ['mass', 'height', 'energy'],
      leads_to: ['conservation_of_energy', 'spring_potential'],
      related: ['kinetic_energy', 'gravity'],
      difficulty: 'medium',
      chapter: 'Work & Energy',
      class: [9, 11],
    },
    
    // Waves & Light
    wave: {
      prerequisites: ['frequency', 'wavelength'],
      leads_to: ['sound', 'light', 'interference'],
      related: ['oscillation', 'vibration'],
      difficulty: 'medium',
      chapter: 'Waves',
      class: [9, 11, 12],
    },
    
    light: {
      prerequisites: ['wave'],
      leads_to: ['reflection', 'refraction', 'lens'],
      related: ['electromagnetic_spectrum', 'color'],
      difficulty: 'medium',
      chapter: 'Optics',
      class: [10, 12],
    },
    
    reflection: {
      prerequisites: ['light'],
      leads_to: ['mirror', 'image_formation'],
      related: ['refraction', 'laws_of_reflection'],
      difficulty: 'easy',
      chapter: 'Optics',
      class: [10, 12],
    },
    
    refraction: {
      prerequisites: ['light', 'medium'],
      leads_to: ['lens', 'prism', 'total_internal_reflection'],
      related: ['snells_law', 'refractive_index'],
      difficulty: 'medium',
      chapter: 'Optics',
      class: [10, 12],
    },
    
    // Electricity
    electricity: {
      prerequisites: ['charge'],
      leads_to: ['current', 'voltage', 'resistance'],
      related: ['magnetism', 'circuit'],
      difficulty: 'medium',
      chapter: 'Electricity',
      class: [10, 12],
    },
    
    current: {
      prerequisites: ['charge', 'time'],
      leads_to: ['ohms_law', 'circuit'],
      related: ['voltage', 'resistance'],
      difficulty: 'medium',
      chapter: 'Electricity',
      class: [10, 12],
    },
    
    ohms_law: {
      prerequisites: ['current', 'voltage', 'resistance'],
      leads_to: ['circuit_analysis', 'power'],
      related: ['conductivity', 'resistivity'],
      difficulty: 'medium',
      chapter: 'Electricity',
      class: [10, 12],
    },
  },

  // ============ CHEMISTRY ============
  chemistry: {
    atom: {
      prerequisites: [],
      leads_to: ['electron', 'proton', 'neutron', 'atomic_structure'],
      related: ['element', 'molecule'],
      difficulty: 'easy',
      chapter: 'Atomic Structure',
      class: [9, 11],
    },
    
    electron: {
      prerequisites: ['atom'],
      leads_to: ['electron_configuration', 'chemical_bonding'],
      related: ['proton', 'neutron', 'charge'],
      difficulty: 'easy',
      chapter: 'Atomic Structure',
      class: [9, 11],
    },
    
    chemical_bonding: {
      prerequisites: ['electron', 'valence'],
      leads_to: ['ionic_bond', 'covalent_bond', 'metallic_bond'],
      related: ['molecule', 'compound'],
      difficulty: 'medium',
      chapter: 'Chemical Bonding',
      class: [10, 11],
    },
    
    ionic_bond: {
      prerequisites: ['chemical_bonding', 'electron_transfer'],
      leads_to: ['ionic_compounds', 'crystal_structure'],
      related: ['covalent_bond', 'electronegativity'],
      difficulty: 'medium',
      chapter: 'Chemical Bonding',
      class: [10, 11],
    },
    
    covalent_bond: {
      prerequisites: ['chemical_bonding', 'electron_sharing'],
      leads_to: ['molecular_compounds', 'organic_chemistry'],
      related: ['ionic_bond', 'polar_bond'],
      difficulty: 'medium',
      chapter: 'Chemical Bonding',
      class: [10, 11],
    },
    
    chemical_reaction: {
      prerequisites: ['chemical_bonding', 'reactants_products'],
      leads_to: ['balancing_equations', 'types_of_reactions'],
      related: ['catalyst', 'rate_of_reaction'],
      difficulty: 'medium',
      chapter: 'Chemical Reactions',
      class: [10, 11],
    },
    
    acid_base: {
      prerequisites: ['chemical_reaction', 'pH'],
      leads_to: ['neutralization', 'buffer'],
      related: ['indicator', 'salt'],
      difficulty: 'medium',
      chapter: 'Acids & Bases',
      class: [10, 11],
    },
    
    periodic_table: {
      prerequisites: ['atom', 'electron_configuration'],
      leads_to: ['periodic_trends', 'groups_periods'],
      related: ['element', 'atomic_number'],
      difficulty: 'medium',
      chapter: 'Periodic Table',
      class: [10, 11],
    },
    
    mole_concept: {
      prerequisites: ['atom', 'molecular_mass'],
      leads_to: ['stoichiometry', 'concentration'],
      related: ['avogadro_number', 'molar_mass'],
      difficulty: 'medium',
      chapter: 'Mole Concept',
      class: [9, 11],
    },
  },

  // ============ BIOLOGY ============
  biology: {
    cell: {
      prerequisites: [],
      leads_to: ['cell_organelles', 'cell_division'],
      related: ['tissue', 'organism'],
      difficulty: 'easy',
      chapter: 'Cell Biology',
      class: [9, 11],
    },
    
    cell_organelles: {
      prerequisites: ['cell'],
      leads_to: ['nucleus', 'mitochondria', 'chloroplast'],
      related: ['cell_membrane', 'cytoplasm'],
      difficulty: 'medium',
      chapter: 'Cell Biology',
      class: [9, 11],
    },
    
    nucleus: {
      prerequisites: ['cell_organelles'],
      leads_to: ['dna', 'chromosome', 'cell_division'],
      related: ['nucleolus', 'nuclear_membrane'],
      difficulty: 'medium',
      chapter: 'Cell Biology',
      class: [9, 11],
    },
    
    dna: {
      prerequisites: ['nucleus'],
      leads_to: ['gene', 'dna_replication', 'protein_synthesis'],
      related: ['rna', 'chromosome'],
      difficulty: 'hard',
      chapter: 'Genetics',
      class: [10, 12],
    },
    
    photosynthesis: {
      prerequisites: ['chloroplast', 'light'],
      leads_to: ['light_reaction', 'dark_reaction'],
      related: ['respiration', 'glucose'],
      difficulty: 'medium',
      chapter: 'Plant Physiology',
      class: [10, 11],
    },
    
    respiration: {
      prerequisites: ['mitochondria', 'glucose'],
      leads_to: ['glycolysis', 'krebs_cycle', 'electron_transport'],
      related: ['photosynthesis', 'atp'],
      difficulty: 'medium',
      chapter: 'Respiration',
      class: [10, 11],
    },
    
    digestive_system: {
      prerequisites: ['cell', 'tissue'],
      leads_to: ['digestion', 'absorption', 'enzymes'],
      related: ['nutrition', 'excretion'],
      difficulty: 'medium',
      chapter: 'Human Physiology',
      class: [10, 11],
    },
    
    circulatory_system: {
      prerequisites: ['cell', 'tissue'],
      leads_to: ['heart', 'blood', 'blood_vessels'],
      related: ['respiratory_system', 'lymphatic_system'],
      difficulty: 'medium',
      chapter: 'Human Physiology',
      class: [10, 11],
    },
    
    evolution: {
      prerequisites: ['genetics', 'natural_selection'],
      leads_to: ['speciation', 'adaptation'],
      related: ['variation', 'inheritance'],
      difficulty: 'hard',
      chapter: 'Evolution',
      class: [10, 12],
    },
  },

  // ============ MATHEMATICS ============
  mathematics: {
    // Algebra
    equation: {
      prerequisites: ['variable', 'expression'],
      leads_to: ['linear_equation', 'quadratic_equation'],
      related: ['inequality', 'identity'],
      difficulty: 'easy',
      chapter: 'Algebra',
      class: [8, 9],
    },
    
    linear_equation: {
      prerequisites: ['equation'],
      leads_to: ['system_of_equations', 'graphs'],
      related: ['slope', 'intercept'],
      difficulty: 'easy',
      chapter: 'Algebra',
      class: [8, 9],
    },
    
    quadratic_equation: {
      prerequisites: ['equation', 'polynomial'],
      leads_to: ['quadratic_formula', 'parabola'],
      related: ['discriminant', 'roots'],
      difficulty: 'medium',
      chapter: 'Algebra',
      class: [10, 11],
    },
    
    polynomial: {
      prerequisites: ['expression', 'variable'],
      leads_to: ['factorization', 'division'],
      related: ['degree', 'coefficient'],
      difficulty: 'medium',
      chapter: 'Algebra',
      class: [9, 10],
    },
    
    // Geometry
    triangle: {
      prerequisites: ['angle', 'line'],
      leads_to: ['pythagoras', 'trigonometry', 'area'],
      related: ['quadrilateral', 'polygon'],
      difficulty: 'easy',
      chapter: 'Geometry',
      class: [9, 10],
    },
    
    pythagoras: {
      prerequisites: ['triangle', 'right_angle'],
      leads_to: ['distance_formula', 'trigonometry'],
      related: ['hypotenuse', 'pythagorean_triplets'],
      difficulty: 'easy',
      chapter: 'Geometry',
      class: [10],
    },
    
    circle: {
      prerequisites: ['point', 'distance'],
      leads_to: ['area_circle', 'circumference', 'arc'],
      related: ['radius', 'diameter', 'chord'],
      difficulty: 'easy',
      chapter: 'Geometry',
      class: [9, 10],
    },
    
    // Trigonometry
    trigonometry: {
      prerequisites: ['triangle', 'ratio'],
      leads_to: ['sine', 'cosine', 'tangent'],
      related: ['angle', 'unit_circle'],
      difficulty: 'medium',
      chapter: 'Trigonometry',
      class: [10, 11],
    },
    
    sine: {
      prerequisites: ['trigonometry'],
      leads_to: ['sine_rule', 'graphs'],
      related: ['cosine', 'tangent'],
      difficulty: 'medium',
      chapter: 'Trigonometry',
      class: [10, 11],
    },
    
    // Calculus
    derivative: {
      prerequisites: ['limit', 'function'],
      leads_to: ['differentiation_rules', 'applications'],
      related: ['rate_of_change', 'slope'],
      difficulty: 'hard',
      chapter: 'Calculus',
      class: [11, 12],
    },
    
    integral: {
      prerequisites: ['derivative', 'antiderivative'],
      leads_to: ['definite_integral', 'area_under_curve'],
      related: ['integration_rules', 'applications'],
      difficulty: 'hard',
      chapter: 'Calculus',
      class: [12],
    },
    
    limit: {
      prerequisites: ['function', 'continuity'],
      leads_to: ['derivative', 'infinite_limits'],
      related: ['convergence', 'divergence'],
      difficulty: 'hard',
      chapter: 'Calculus',
      class: [11, 12],
    },
    
    // Statistics
    probability: {
      prerequisites: ['sets', 'counting'],
      leads_to: ['conditional_probability', 'bayes_theorem'],
      related: ['statistics', 'combinations'],
      difficulty: 'medium',
      chapter: 'Probability',
      class: [10, 11, 12],
    },
    
    statistics: {
      prerequisites: ['data', 'mean'],
      leads_to: ['standard_deviation', 'distribution'],
      related: ['probability', 'graphs'],
      difficulty: 'medium',
      chapter: 'Statistics',
      class: [10, 11],
    },
  },
};

// Helper functions

/**
 * Get all prerequisites for a concept (recursive)
 */
export function getAllPrerequisites(subject, concept, visited = new Set()) {
  if (visited.has(concept)) return [];
  visited.add(concept);
  
  const conceptData = CONCEPT_GRAPH[subject]?.[concept];
  if (!conceptData) return [];
  
  const direct = conceptData.prerequisites || [];
  const all = [...direct];
  
  direct.forEach(prereq => {
    all.push(...getAllPrerequisites(subject, prereq, visited));
  });
  
  return [...new Set(all)];
}

/**
 * Get learning path from one concept to another
 */
export function getLearningPath(subject, fromConcept, toConcept) {
  const graph = CONCEPT_GRAPH[subject];
  if (!graph) return null;
  
  // BFS to find shortest path
  const queue = [[fromConcept]];
  const visited = new Set([fromConcept]);
  
  while (queue.length > 0) {
    const path = queue.shift();
    const current = path[path.length - 1];
    
    if (current === toConcept) return path;
    
    const conceptData = graph[current];
    if (!conceptData) continue;
    
    const neighbors = [...(conceptData.leads_to || []), ...(conceptData.related || [])];
    
    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push([...path, neighbor]);
      }
    }
  }
  
  return null; // No path found
}

/**
 * Get suggested next concepts to learn
 */
export function getNextConcepts(subject, masteredConcepts = []) {
  const graph = CONCEPT_GRAPH[subject];
  if (!graph) return [];
  
  const suggestions = [];
  
  Object.entries(graph).forEach(([concept, data]) => {
    if (masteredConcepts.includes(concept)) return;
    
    // Check if all prerequisites are mastered
    const prereqs = data.prerequisites || [];
    const allPrereqsMastered = prereqs.every(p => masteredConcepts.includes(p));
    
    if (allPrereqsMastered) {
      suggestions.push({
        concept,
        ...data,
        readiness: prereqs.length === 0 ? 1 : prereqs.length / masteredConcepts.length,
      });
    }
  });
  
  // Sort by difficulty and readiness
  return suggestions.sort((a, b) => {
    const diffOrder = { easy: 0, medium: 1, hard: 2 };
    return (diffOrder[a.difficulty] || 1) - (diffOrder[b.difficulty] || 1);
  });
}

/**
 * Get concept details with enriched data
 */
export function getConceptDetails(subject, concept) {
  const data = CONCEPT_GRAPH[subject]?.[concept];
  if (!data) return null;
  
  return {
    name: concept.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    ...data,
    allPrerequisites: getAllPrerequisites(subject, concept),
    totalConnections: (data.prerequisites?.length || 0) + 
                      (data.leads_to?.length || 0) + 
                      (data.related?.length || 0),
  };
}

/**
 * Get related concepts grouped by relationship type
 */
export function getRelatedConcepts(subject, concept) {
  const data = CONCEPT_GRAPH[subject]?.[concept];
  if (!data) return null;
  
  return {
    prerequisites: data.prerequisites || [],
    leads_to: data.leads_to || [],
    related: data.related || [],
  };
}

export default CONCEPT_GRAPH;



