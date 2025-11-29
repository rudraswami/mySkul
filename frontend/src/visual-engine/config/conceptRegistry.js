/**
 * Concept Registry
 * Maps concepts/keywords to visual scene configurations
 * Covers Physics, Chemistry, Biology, Mathematics
 */

export const CONCEPT_REGISTRY = {
  // ============ PHYSICS ============
  physics: {
    // Mechanics
    force: { scene: 'CompactPhysicsScene', formula: 'F = m × a', icon: '🏏' },
    newton: { scene: 'CompactPhysicsScene', formula: 'F = m × a', icon: '🍎' },
    push: { scene: 'CompactPhysicsScene', formula: 'F = m × a', icon: '👋' },
    pull: { scene: 'CompactPhysicsScene', formula: 'F = m × a', icon: '🧲' },
    friction: { scene: 'FrictionScene', formula: 'f = μN', icon: '🛞' },
    
    motion: { scene: 'MotionScene', formula: 'v = d/t', icon: '🚗' },
    velocity: { scene: 'MotionScene', formula: 'v = Δx/Δt', icon: '💨' },
    speed: { scene: 'MotionScene', formula: 's = d/t', icon: '⚡' },
    acceleration: { scene: 'MotionScene', formula: 'a = Δv/Δt', icon: '🚀' },
    
    gravity: { scene: 'GravityScene', formula: 'F = Gm₁m₂/r²', icon: '🌍' },
    weight: { scene: 'GravityScene', formula: 'W = mg', icon: '⚖️' },
    falling: { scene: 'GravityScene', formula: 'h = ½gt²', icon: '🍂' },
    
    momentum: { scene: 'MomentumScene', formula: 'p = mv', icon: '🎱' },
    collision: { scene: 'MomentumScene', formula: 'p₁ + p₂ = p₁\' + p₂\'', icon: '💥' },
    
    energy: { scene: 'EnergyScene', formula: 'E = ½mv²', icon: '⚡' },
    'kinetic energy': { scene: 'EnergyScene', formula: 'KE = ½mv²', icon: '🏃' },
    'potential energy': { scene: 'EnergyScene', formula: 'PE = mgh', icon: '🏔️' },
    work: { scene: 'EnergyScene', formula: 'W = F × d', icon: '🔧' },
    power: { scene: 'EnergyScene', formula: 'P = W/t', icon: '💪' },
    
    // Waves & Light
    wave: { scene: 'WaveScene', formula: 'v = fλ', icon: '🌊' },
    light: { scene: 'LightScene', formula: 'c = fλ', icon: '💡' },
    reflection: { scene: 'LightScene', formula: 'θᵢ = θᵣ', icon: '🪞' },
    refraction: { scene: 'LightScene', formula: 'n₁sinθ₁ = n₂sinθ₂', icon: '🔍' },
    lens: { scene: 'LightScene', formula: '1/f = 1/v - 1/u', icon: '👓' },
    mirror: { scene: 'LightScene', formula: '1/f = 1/v + 1/u', icon: '🪞' },
    
    // Electricity
    electricity: { scene: 'ElectricityScene', formula: 'V = IR', icon: '⚡' },
    current: { scene: 'ElectricityScene', formula: 'I = Q/t', icon: '🔌' },
    voltage: { scene: 'ElectricityScene', formula: 'V = IR', icon: '🔋' },
    resistance: { scene: 'ElectricityScene', formula: 'R = V/I', icon: '🚧' },
    circuit: { scene: 'ElectricityScene', formula: 'V = IR', icon: '🔄' },
    'ohm': { scene: 'ElectricityScene', formula: 'V = IR', icon: 'Ω' },
  },

  // ============ CHEMISTRY ============
  chemistry: {
    atom: { scene: 'AtomScene', formula: 'A = Z + N', icon: '⚛️' },
    electron: { scene: 'AtomScene', formula: 'e⁻', icon: '🔵' },
    proton: { scene: 'AtomScene', formula: 'p⁺', icon: '🔴' },
    neutron: { scene: 'AtomScene', formula: 'n⁰', icon: '⚪' },
    
    molecule: { scene: 'MoleculeScene', formula: 'H₂O', icon: '🧪' },
    bond: { scene: 'BondingScene', formula: 'A-B', icon: '🔗' },
    'covalent bond': { scene: 'BondingScene', formula: 'A:B', icon: '🤝' },
    'ionic bond': { scene: 'BondingScene', formula: 'A⁺B⁻', icon: '🧲' },
    
    reaction: { scene: 'ReactionScene', formula: 'A + B → C', icon: '🧫' },
    'chemical reaction': { scene: 'ReactionScene', formula: 'Reactants → Products', icon: '⚗️' },
    combustion: { scene: 'ReactionScene', formula: 'CH₄ + O₂ → CO₂ + H₂O', icon: '🔥' },
    oxidation: { scene: 'ReactionScene', formula: 'Fe → Fe²⁺ + 2e⁻', icon: '🦠' },
    
    acid: { scene: 'AcidBaseScene', formula: 'pH < 7', icon: '🍋' },
    base: { scene: 'AcidBaseScene', formula: 'pH > 7', icon: '🧼' },
    'ph': { scene: 'AcidBaseScene', formula: 'pH = -log[H⁺]', icon: '📊' },
    
    'periodic table': { scene: 'PeriodicScene', formula: 'Elements', icon: '📋' },
    element: { scene: 'PeriodicScene', formula: 'Z = Atomic Number', icon: '🔤' },
  },

  // ============ BIOLOGY ============
  biology: {
    cell: { scene: 'CellScene', formula: 'Cell Theory', icon: '🔬' },
    nucleus: { scene: 'CellScene', formula: 'DNA Storage', icon: '🟣' },
    mitochondria: { scene: 'CellScene', formula: 'ATP Production', icon: '🔋' },
    
    dna: { scene: 'DNAScene', formula: 'A-T, G-C', icon: '🧬' },
    gene: { scene: 'DNAScene', formula: 'DNA Sequence', icon: '🔠' },
    chromosome: { scene: 'DNAScene', formula: '23 Pairs', icon: '🧵' },
    
    photosynthesis: { scene: 'PhotosynthesisScene', formula: '6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂', icon: '🌱' },
    respiration: { scene: 'RespirationScene', formula: 'C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O', icon: '🫁' },
    
    heart: { scene: 'HeartScene', formula: 'Cardiac Cycle', icon: '❤️' },
    blood: { scene: 'CirculatoryScene', formula: 'RBC + WBC + Plasma', icon: '🩸' },
    digestion: { scene: 'DigestiveScene', formula: 'Food → Nutrients', icon: '🍽️' },
    
    evolution: { scene: 'EvolutionScene', formula: 'Natural Selection', icon: '🦎' },
    'natural selection': { scene: 'EvolutionScene', formula: 'Survival of Fittest', icon: '🌳' },
  },

  // ============ MATHEMATICS ============
  mathematics: {
    // Algebra
    equation: { scene: 'EquationScene', formula: 'ax + b = c', icon: '➕' },
    quadratic: { scene: 'QuadraticScene', formula: 'ax² + bx + c = 0', icon: '📈' },
    'quadratic equation': { scene: 'QuadraticScene', formula: 'x = (-b ± √(b²-4ac))/2a', icon: '📊' },
    polynomial: { scene: 'PolynomialScene', formula: 'aₙxⁿ + ... + a₁x + a₀', icon: '📉' },
    
    // Geometry
    triangle: { scene: 'TriangleScene', formula: 'A = ½bh', icon: '📐' },
    circle: { scene: 'CircleScene', formula: 'A = πr²', icon: '⭕' },
    pythagoras: { scene: 'PythagorasScene', formula: 'a² + b² = c²', icon: '📏' },
    'pythagorean theorem': { scene: 'PythagorasScene', formula: 'a² + b² = c²', icon: '📐' },
    
    // Trigonometry
    trigonometry: { scene: 'TrigScene', formula: 'sin, cos, tan', icon: '📐' },
    sine: { scene: 'TrigScene', formula: 'sin θ = opp/hyp', icon: '〰️' },
    cosine: { scene: 'TrigScene', formula: 'cos θ = adj/hyp', icon: '〰️' },
    tangent: { scene: 'TrigScene', formula: 'tan θ = opp/adj', icon: '〰️' },
    
    // Calculus
    derivative: { scene: 'DerivativeScene', formula: 'dy/dx', icon: '📈' },
    integral: { scene: 'IntegralScene', formula: '∫f(x)dx', icon: '∫' },
    limit: { scene: 'LimitScene', formula: 'lim x→a f(x)', icon: '→' },
    
    // Statistics
    probability: { scene: 'ProbabilityScene', formula: 'P(A) = n(A)/n(S)', icon: '🎲' },
    statistics: { scene: 'StatisticsScene', formula: 'μ, σ, median', icon: '📊' },
    mean: { scene: 'StatisticsScene', formula: 'x̄ = Σx/n', icon: '📊' },
  },
};

/**
 * Get visual config for a concept
 */
export function getConceptConfig(question, detectedSubject = null) {
  if (!question) return null;
  
  const q = question.toLowerCase();
  
  // Determine subject priority
  const subjects = detectedSubject 
    ? [detectedSubject.toLowerCase(), 'physics', 'chemistry', 'biology', 'mathematics']
    : ['physics', 'chemistry', 'biology', 'mathematics'];
  
  // Search through subjects
  for (const subject of subjects) {
    const concepts = CONCEPT_REGISTRY[subject];
    if (!concepts) continue;
    
    for (const [keyword, config] of Object.entries(concepts)) {
      if (q.includes(keyword)) {
        return {
          ...config,
          subject,
          keyword,
        };
      }
    }
  }
  
  return null;
}

/**
 * Get all available concepts for a subject
 */
export function getConceptsForSubject(subject) {
  return CONCEPT_REGISTRY[subject.toLowerCase()] || {};
}

/**
 * Check if a concept has visual support
 */
export function hasVisualSupport(question) {
  return getConceptConfig(question) !== null;
}

export default CONCEPT_REGISTRY;







