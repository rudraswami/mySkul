/**
 * 🛡️ QUALITY GATE AUTO-FIXER
 * ==========================
 * 
 * Local post-processor that ensures ALL compositions meet minimum quality bar.
 * NO API RE-CALLS - all fixes happen locally.
 * 
 * DETECTION → AUTO-FIX → VALIDATE
 * 
 * Rules:
 * - QG001: Diagram Detection → enhanceToProcedural()
 * - QG002: Hero Missing → injectHero()
 * - QG003: Hero Too Small → scaleHero()
 * - QG004: No Environment → generateEnvironment()
 * - QG005: Canvas Underfilled → rescaleScene()
 * - QG006: No Effects → injectEffects()
 * - QG007: No Particles → injectParticles()
 * - QG008: No Interaction → bindDefaultInteraction()
 * - QG009: No Choreography → generateChoreography()
 * - QG010: No 3-Act Structure → inject3ActNarration()
 * - QG011: Flat Composition → assignDepthLayers()
 * - QG012: No Flow Animation → generateFlowAnimations()
 */

// Canvas dimensions
const CANVAS_WIDTH = 720;
const CANVAS_HEIGHT = 520;

// Quality thresholds
const THRESHOLDS = {
  MIN_HERO_WIDTH: 150,
  MIN_HERO_HEIGHT: 100,
  MIN_CANVAS_COVERAGE: 0.6,
  MIN_EFFECTS: 2,
  MIN_PARTICLES_BIOLOGY: 1,
  MIN_CHOREOGRAPHY_BEATS: 3,
  DIAGRAM_BASIC_SHAPE_RATIO: 0.3,  // Lowered from 0.6 - more aggressive diagram detection
};

// Zone definitions for scene composition
const ZONES = {
  hero: { x: 360, y: 280 },
  input: { xMin: 60, xMax: 180, y: 280 },
  output: { xMin: 540, xMax: 660, y: 280 },
  environment: { x: 360, y: 400 },
};

// Domain color palettes
const DOMAIN_COLORS = {
  biology: { primary: '#10B981', secondary: '#34D399', accent: '#FCD34D', bg: ['#ECFDF5', '#D1FAE5'] },
  physics: { primary: '#3B82F6', secondary: '#60A5FA', accent: '#F472B6', bg: ['#EFF6FF', '#DBEAFE'] },
  chemistry: { primary: '#8B5CF6', secondary: '#A78BFA', accent: '#F59E0B', bg: ['#F5F3FF', '#EDE9FE'] },
  math: { primary: '#6366F1', secondary: '#818CF8', accent: '#14B8A6', bg: ['#EEF2FF', '#E0E7FF'] },
  general: { primary: '#6B7280', secondary: '#9CA3AF', accent: '#F59E0B', bg: ['#F9FAFB', '#F3F4F6'] },
};

// ============================================
// MAIN QUALITY GATE FUNCTION
// ============================================

/**
 * Run all quality checks and auto-fix violations
 * @param {object} composition - The composition to validate and fix
 * @param {object} intent - Semantic intent for context
 * @returns {object} - Fixed composition + quality report
 */
export function qualityGateAutoFix(composition, intent = {}) {
  console.log('🛡️ [QualityGate] Starting validation...');
  console.log('🛡️ [QualityGate] Input composition:', {
    atomCount: composition?.atoms?.length || 0,
    domain: intent.domain || composition?.context?.domain,
    isFallback: composition?.context?.isFallback || composition?.metadata?.isFallback,
    atomTypes: composition?.atoms?.map(a => ({ id: a.id, type: a.type, shape: a.params?.shape })),
  });
  
  const domain = intent.domain || composition.context?.domain || 'general';
  const violations = [];
  const fixes = [];
  
  let fixed = JSON.parse(JSON.stringify(composition)); // Deep clone
  
  // ============================================
  // DETECTION PHASE
  // ============================================
  
  const checks = [
    { id: 'QG001', check: () => isDiagram(fixed), severity: 'critical', fix: () => fixed = enhanceToProcedural(fixed, intent, domain) },
    { id: 'QG002', check: () => !hasHero(fixed), severity: 'critical', fix: () => fixed = injectHero(fixed, domain) },
    { id: 'QG003', check: () => isHeroTooSmall(fixed), severity: 'high', fix: () => fixed = scaleHero(fixed) },
    { id: 'QG004', check: () => !hasEnvironment(fixed), severity: 'high', fix: () => fixed = generateEnvironment(fixed, domain) },
    { id: 'QG005', check: () => isCanvasUnderfilled(fixed), severity: 'high', fix: () => fixed = rescaleScene(fixed) },
    { id: 'QG011', check: () => isFlatComposition(fixed), severity: 'medium', fix: () => fixed = assignDepthLayers(fixed) },
    { id: 'QG012', check: () => !hasFlowAnimation(fixed), severity: 'high', fix: () => fixed = generateFlowAnimations(fixed, intent) },
    { id: 'QG009', check: () => !hasChoreography(fixed), severity: 'high', fix: () => fixed = generateChoreography(fixed, intent) },
    { id: 'QG010', check: () => !has3ActStructure(fixed), severity: 'high', fix: () => fixed = inject3ActNarration(fixed, intent) },
    { id: 'QG006', check: () => !hasEffects(fixed), severity: 'medium', fix: () => fixed = injectEffects(fixed, domain) },
    { id: 'QG007', check: () => !hasParticles(fixed, domain), severity: 'medium', fix: () => fixed = injectParticles(fixed, domain) },
    { id: 'QG008', check: () => !hasInteraction(fixed), severity: 'critical', fix: () => fixed = bindDefaultInteraction(fixed, intent) },
  ];
  
  // ============================================
  // AUTO-FIX PHASE
  // ============================================
  
  for (const rule of checks) {
    try {
      if (rule.check()) {
        console.log(`🛡️ [QualityGate] ${rule.id} VIOLATED - applying fix...`);
        violations.push({ ruleId: rule.id, severity: rule.severity });
        rule.fix();
        fixes.push(rule.id);
      }
    } catch (err) {
      console.error(`🛡️ [QualityGate] ${rule.id} fix failed:`, err.message);
    }
  }
  
  // ============================================
  // VALIDATION REPORT
  // ============================================
  
  const passed = violations.filter(v => v.severity === 'critical').length === 0;
  
  console.log('🛡️ [QualityGate] Results:', {
    passed,
    violations: violations.length,
    fixes: fixes.length,
    fixesApplied: fixes,
  });
  
  return {
    composition: fixed,
    qualityReport: {
      passed,
      violations,
      autoFixApplied: fixes,
    },
  };
}

// ============================================
// DETECTION FUNCTIONS
// ============================================

function isDiagram(composition) {
  const atoms = composition.atoms || [];
  const layers = composition.layers || [];
  
  // 🎯 KEY: If NO procedural generators exist, treat as diagram
  const hasAnyGenerator = atoms.some(a => a.params?.generator || a.generator);
  
  // Check atoms (old format)
  if (atoms.length > 0) {
    const basicShapes = atoms.filter(a => 
      a.type === 'Entity' && 
      ['rect', 'circle', 'ellipse'].includes(a.params?.shape) &&
      !a.params?.generator  // Not already procedural
    );
    const hasProcedural = atoms.some(a => a.type === 'procedural' || a.generator || a.params?.generator);
    const hasPath = atoms.some(a => a.type === 'path' || a.d);
    
    // If no procedural at all and domain is biology/chemistry, definitely enhance
    const domain = composition.context?.domain || '';
    const needsProcedural = ['biology', 'chemistry'].includes(domain) && !hasProcedural;
    
    const ratio = basicShapes.length / atoms.length;
    const isDiagramByRatio = ratio > THRESHOLDS.DIAGRAM_BASIC_SHAPE_RATIO && !hasProcedural && !hasPath;
    
    console.log('🛡️ [QG] isDiagram check:', {
      atomCount: atoms.length,
      basicShapeCount: basicShapes.length,
      ratio: ratio.toFixed(2),
      threshold: THRESHOLDS.DIAGRAM_BASIC_SHAPE_RATIO,
      hasProcedural,
      hasPath,
      domain,
      needsProcedural,
      isDiagramByRatio,
      result: isDiagramByRatio || needsProcedural,
    });
    
    // Diagram if: many basic shapes OR biology/chem without procedural
    return isDiagramByRatio || needsProcedural;
  }
  
  // Check layers (new format)
  if (layers.length > 0) {
    const allElements = layers.flatMap(l => l.elements || []);
    const basicShapes = allElements.filter(e => 
      e.type === 'shape' && 
      ['rect', 'circle', 'ellipse'].includes(e.shape)
    );
    const hasProcedural = allElements.some(e => e.type === 'procedural');
    
    return basicShapes.length > allElements.length * THRESHOLDS.DIAGRAM_BASIC_SHAPE_RATIO && 
           !hasProcedural;
  }
  
  // Default: check if domain suggests we need procedural
  const domain = composition.context?.domain || '';
  if (['biology', 'chemistry'].includes(domain) && !hasAnyGenerator) {
    console.log('🛡️ [QG] Domain is biology/chemistry without generators - treating as diagram');
    return true;
  }
  
  return false;
}

function hasHero(composition) {
  const atoms = composition.atoms || [];
  const layers = composition.layers || [];
  
  // Check atoms
  const heroAtom = atoms.find(a => a.params?.isHero || a.role === 'hero' || a.id?.includes('hero'));
  if (heroAtom) return true;
  
  // Check layers
  for (const layer of layers) {
    const heroElement = (layer.elements || []).find(e => e.role === 'hero');
    if (heroElement) return true;
  }
  
  return false;
}

function isHeroTooSmall(composition) {
  const hero = findHero(composition);
  if (!hero) return false;
  
  const width = hero.params?.width || hero.width || 0;
  const height = hero.params?.height || hero.height || 0;
  
  return width < THRESHOLDS.MIN_HERO_WIDTH || height < THRESHOLDS.MIN_HERO_HEIGHT;
}

function hasEnvironment(composition) {
  const atoms = composition.atoms || [];
  const layers = composition.layers || [];
  
  // Check for environment atoms
  const envAtom = atoms.find(a => 
    a.type === 'Surface' || 
    a.type === 'Region' || 
    a.role === 'environment' ||
    a.id?.includes('env')
  );
  if (envAtom) return true;
  
  // Check layers
  for (const layer of layers) {
    const envElement = (layer.elements || []).find(e => e.role === 'environment');
    if (envElement) return true;
  }
  
  // Check for background specification
  if (composition.canvas?.background?.type === 'procedural') return true;
  
  return false;
}

function isCanvasUnderfilled(composition) {
  const bounds = calculateBounds(composition);
  const coverage = (bounds.width * bounds.height) / (CANVAS_WIDTH * CANVAS_HEIGHT);
  return coverage < THRESHOLDS.MIN_CANVAS_COVERAGE;
}

function isFlatComposition(composition) {
  const atoms = composition.atoms || [];
  const layers = composition.layers || [];
  
  // Check if all atoms have same or no zIndex
  if (atoms.length > 0) {
    const zIndices = new Set(atoms.map(a => a.zIndex || 0));
    return zIndices.size <= 1;
  }
  
  // Check layers
  return layers.length <= 1;
}

function hasFlowAnimation(composition) {
  const behaviors = composition.behaviors || [];
  const choreography = composition.choreography || [];
  
  // Check for moveTo behaviors
  const hasMoveTo = behaviors.some(b => b.action?.type === 'moveTo');
  if (hasMoveTo) return true;
  
  // Check choreography
  const hasMove = choreography.some(c => c.action?.type === 'moveTo' || c.action?.type === 'moveBy');
  return hasMove;
}

function hasChoreography(composition) {
  const behaviors = composition.behaviors || [];
  const choreography = composition.choreography || [];
  
  return behaviors.length >= THRESHOLDS.MIN_CHOREOGRAPHY_BEATS || 
         choreography.length >= THRESHOLDS.MIN_CHOREOGRAPHY_BEATS;
}

function has3ActStructure(composition) {
  const narration = composition.narration || [];
  const choreography = composition.choreography || [];
  
  // Check if narration has 3 entries with different delays
  if (narration.length >= 3) {
    const delays = narration.map(n => n.trigger?.delay || 0);
    const hasSpread = Math.max(...delays) - Math.min(...delays) > 2000;
    if (hasSpread) return true;
  }
  
  // Check choreography acts
  const acts = new Set(choreography.map(c => c.act));
  return acts.size >= 3;
}

function hasEffects(composition) {
  const atoms = composition.atoms || [];
  const effects = composition.effects || [];
  
  // Count effects
  let effectCount = effects.length;
  
  // Check atom-level effects
  for (const atom of atoms) {
    if (atom.params?.glow) effectCount++;
    if (atom.effects?.length) effectCount += atom.effects.length;
  }
  
  return effectCount >= THRESHOLDS.MIN_EFFECTS;
}

function hasParticles(composition, domain) {
  if (domain !== 'biology' && domain !== 'chemistry') return true; // Only required for these
  
  const particles = composition.particles || [];
  const behaviors = composition.behaviors || [];
  
  // Check for particle systems
  if (particles.length > 0) return true;
  
  // Check for emit behaviors
  const hasEmit = behaviors.some(b => b.action?.type === 'emit');
  return hasEmit;
}

function hasInteraction(composition) {
  const interactions = composition.interactions || [];
  return interactions.length > 0;
}

// ============================================
// AUTO-FIX FUNCTIONS
// ============================================

function enhanceToProcedural(composition, intent, domain) {
  console.log('🛡️ [AutoFix] Converting diagram to procedural for domain:', domain);
  
  const atoms = composition.atoms || [];
  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
  
  // Determine domain-specific generators
  const domainGenerators = {
    biology: {
      hero: 'organic_shape',
      input: 'molecule',
      output: 'molecule',
      environment: 'leaf',
      default: 'organic_shape',
    },
    chemistry: {
      hero: 'reaction_zone',
      input: 'atom_orbital',
      output: 'atom_orbital',
      environment: null,
      default: 'atom_orbital',
    },
    physics: {
      hero: 'force_field',
      input: null,
      output: 'motion_trail',
      environment: 'surface',
      default: null,
    },
    math: {
      hero: 'graph',
      input: null,
      output: null,
      environment: null,
      default: null,
    },
    general: {
      hero: 'organic_shape',  // Use organic_shape as default for general
      input: 'particle_group',
      output: 'particle_group',
      environment: 'gradient_region',
      default: 'organic_shape',
    },
  };
  
  // 🎯 CRITICAL: Fallback to 'general' if domain not found
  const generators = domainGenerators[domain] || domainGenerators.general;
  
  // Find the main/central Entity to treat as hero
  const entityAtoms = atoms.filter(a => a.type === 'Entity');
  const heroCandidate = entityAtoms.find(a => 
    a.id?.includes('main') || a.id?.includes('concept') || a.id?.includes('hero')
  ) || entityAtoms[0];
  
  console.log('🛡️ [AutoFix] Hero candidate:', heroCandidate?.id);
  
  // Convert atoms to procedural elements based on role
  const enhanced = atoms.map((atom, idx) => {
    // Skip non-Entity atoms
    if (atom.type !== 'Entity') {
      return atom;
    }
    
    const isHero = atom === heroCandidate;
    const role = isHero ? 'hero' : (atom.role || guessRole(atom, intent));
    const generator = isHero ? generators.hero : (generators[role] || generators.default);
    
    console.log(`🛡️ [AutoFix] Processing atom ${atom.id}: isHero=${isHero}, role=${role}, generator=${generator}`);
    
    if (isHero) {
      const heroWidth = Math.max(atom.params?.width || 100, THRESHOLDS.MIN_HERO_WIDTH);
      const heroHeight = Math.max(atom.params?.height || 80, THRESHOLDS.MIN_HERO_HEIGHT);
      
      const generatorParams = domain === 'biology' ? {
        width: heroWidth,
        height: heroHeight,
        irregularity: 0.15,
        membrane: { thickness: 3, double: true, color: colors.primary },
        innerStructures: { type: 'organelles', count: 4, color: colors.secondary },
      } : domain === 'chemistry' ? {
        width: heroWidth,
        height: heroHeight,
        intensity: 0.7,
        color: colors.primary,
      } : domain === 'physics' ? {
        width: heroWidth,
        height: heroHeight,
        direction: 'radial',
        intensity: 0.6,
        color: colors.primary,
      } : {};
      
      return {
        ...atom,
        type: 'Entity',
        role: 'hero',
        params: {
          ...atom.params,
          shape: 'ellipse',
          width: heroWidth,
          height: heroHeight,
          fill: colors.primary,
          stroke: colors.secondary,
          strokeWidth: 3,
          glow: true,
          glowColor: colors.accent,
          glowIntensity: 0.5,
          isHero: true,
          // 🧬 PROCEDURAL GENERATOR
          generator: generator,
          generatorParams: generatorParams,
        },
      };
    }
    
    // For other Entity atoms, apply domain-specific generator
    if (generator) {
      const labelChar = atom.params?.label?.[0] || (role === 'input' ? 'I' : 'O');
      const size = atom.params?.width || 60;
      
      const generatorParams = domain === 'chemistry' ? {
        element: labelChar,
        shellConfig: [2],
        size: size,
      } : domain === 'biology' ? {
        width: size,
        height: size * 0.8,
        irregularity: 0.1,
      } : {};
      
      return {
        ...atom,
        role,
        params: {
          ...atom.params,
          fill: role === 'input' ? colors.secondary : colors.accent,
          stroke: role === 'input' ? colors.primary : colors.secondary,
          strokeWidth: 2,
          // 🧬 PROCEDURAL GENERATOR
          generator: generator,
          generatorParams: generatorParams,
        },
      };
    }
    
    return { ...atom, role };
  });
  
  console.log('🛡️ [AutoFix] Enhanced atoms:', enhanced.map(a => ({ id: a.id, generator: a.params?.generator })));
  
  return { ...composition, atoms: enhanced };
}

function injectHero(composition, domain) {
  console.log('🛡️ [AutoFix] Injecting hero...');
  
  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
  const atoms = composition.atoms || [];
  
  // Determine generator based on domain
  let generator = null;
  let generatorParams = {};
  
  if (domain === 'biology') {
    generator = 'organic_shape';
    generatorParams = {
      width: 220,
      height: 160,
      irregularity: 0.12,
      membrane: { thickness: 3, double: true, color: colors.primary },
      innerStructures: { type: 'organelles', count: 4, color: colors.primary },
    };
  } else if (domain === 'chemistry') {
    generator = 'reaction_zone';
    generatorParams = {
      width: 200,
      height: 150,
      intensity: 0.7,
      color: colors.primary,
    };
  } else if (domain === 'physics') {
    generator = 'force_field';
    generatorParams = {
      width: 180,
      height: 180,
      direction: 'radial',
      intensity: 0.6,
      color: colors.primary,
    };
  }
  
  const heroAtom = {
    id: 'hero_main',
    type: 'Entity',
    params: {
      shape: generator ? 'ellipse' : 'rect',
      width: 220,
      height: 160,
      fill: colors.primary,
      stroke: colors.secondary,
      strokeWidth: 3,
      cornerRadius: domain === 'biology' ? 30 : 12,
      glow: true,
      glowColor: colors.accent,
      glowIntensity: 0.5,
      isHero: true,
      // 🧬 PROCEDURAL GENERATOR
      generator: generator,
      generatorParams: generatorParams,
    },
    position: { x: ZONES.hero.x, y: ZONES.hero.y },
    role: 'hero',
    zIndex: 10,
    initialState: { visible: true, opacity: 1 },
  };
  
  return { ...composition, atoms: [heroAtom, ...atoms] };
}

function scaleHero(composition) {
  console.log('🛡️ [AutoFix] Scaling hero...');
  
  const atoms = (composition.atoms || []).map(atom => {
    if (atom.role === 'hero' || atom.params?.isHero || atom.id?.includes('hero')) {
      const currentWidth = atom.params?.width || atom.generator?.params?.width || 100;
      const currentHeight = atom.params?.height || atom.generator?.params?.height || 80;
      
      const scaleFactor = Math.max(
        THRESHOLDS.MIN_HERO_WIDTH / currentWidth,
        THRESHOLDS.MIN_HERO_HEIGHT / currentHeight,
        1
      );
      
      if (atom.generator?.params) {
        atom.generator.params.width = currentWidth * scaleFactor;
        atom.generator.params.height = currentHeight * scaleFactor;
      }
      if (atom.params) {
        atom.params.width = (atom.params.width || 100) * scaleFactor;
        atom.params.height = (atom.params.height || 80) * scaleFactor;
      }
    }
    return atom;
  });
  
  return { ...composition, atoms };
}

function generateEnvironment(composition, domain) {
  console.log('🛡️ [AutoFix] Generating environment...');
  
  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
  const atoms = composition.atoms || [];
  
  const envAtom = {
    id: 'env_background',
    type: 'Region',
    params: {
      width: 680,
      height: 450,
      fill: `rgba(${hexToRgb(colors.primary)}, 0.08)`,
      stroke: `rgba(${hexToRgb(colors.primary)}, 0.2)`,
      strokeWidth: 2,
      cornerRadius: 30,
    },
    position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
    role: 'environment',
    zIndex: -10,
    initialState: { visible: true, opacity: 0.6 },
  };
  
  // Add surface for physics
  const surfaceAtom = domain === 'physics' ? {
    id: 'env_surface',
    type: 'Surface',
    params: {
      width: 650,
      height: 25,
      fill: '#64748B',
      texture: 'rough',
    },
    position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT - 50 },
    role: 'environment',
    zIndex: -5,
  } : null;
  
  const newAtoms = [envAtom];
  if (surfaceAtom) newAtoms.push(surfaceAtom);
  
  return { ...composition, atoms: [...newAtoms, ...atoms] };
}

function rescaleScene(composition) {
  console.log('🛡️ [AutoFix] Rescaling scene to fill canvas...');
  
  const bounds = calculateBounds(composition);
  if (bounds.width === 0 || bounds.height === 0) return composition;
  
  const targetWidth = CANVAS_WIDTH * 0.85;
  const targetHeight = CANVAS_HEIGHT * 0.85;
  
  const scaleX = targetWidth / bounds.width;
  const scaleY = targetHeight / bounds.height;
  const scale = Math.min(scaleX, scaleY, 2.5); // Cap at 2.5x
  
  const offsetX = (CANVAS_WIDTH - bounds.width * scale) / 2 - bounds.minX * scale;
  const offsetY = (CANVAS_HEIGHT - bounds.height * scale) / 2 - bounds.minY * scale;
  
  const atoms = (composition.atoms || []).map(atom => {
    if (atom.position) {
      atom.position = {
        x: atom.position.x * scale + offsetX,
        y: atom.position.y * scale + offsetY,
      };
    }
    if (atom.params?.width) atom.params.width *= scale;
    if (atom.params?.height) atom.params.height *= scale;
    if (atom.generator?.params?.width) atom.generator.params.width *= scale;
    if (atom.generator?.params?.height) atom.generator.params.height *= scale;
    return atom;
  });
  
  return { ...composition, atoms };
}

function assignDepthLayers(composition) {
  console.log('🛡️ [AutoFix] Assigning depth layers...');
  
  const atoms = (composition.atoms || []).map(atom => {
    const role = atom.role || 'effect';
    
    const zIndexMap = {
      environment: -10,
      connector: 0,
      input: 5,
      output: 5,
      hero: 10,
      label: 15,
      effect: 20,
    };
    
    return { ...atom, zIndex: atom.zIndex ?? zIndexMap[role] ?? 0 };
  });
  
  return { ...composition, atoms };
}

function generateFlowAnimations(composition, intent) {
  console.log('🛡️ [AutoFix] Generating flow animations...');
  
  const atoms = composition.atoms || [];
  const behaviors = composition.behaviors || [];
  
  const inputs = atoms.filter(a => a.role === 'input');
  const outputs = atoms.filter(a => a.role === 'output');
  const hero = findHero(composition);
  
  const newBehaviors = [...behaviors];
  let delay = Math.max(...behaviors.map(b => b.trigger?.delay || 0), 0) + 500;
  
  // Animate inputs toward hero
  for (const input of inputs) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay },
      action: {
        type: 'moveTo',
        target: input.id,
        x: hero?.position?.x || ZONES.hero.x,
        y: (hero?.position?.y || ZONES.hero.y) + (Math.random() - 0.5) * 60,
        duration: 1200,
        easing: 'easeInOut',
      },
    });
    delay += 300;
  }
  
  // Pulse hero
  if (hero) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay },
      action: { type: 'pulse', target: hero.id, duration: 800, scale: 1.1 },
    });
    delay += 1000;
  }
  
  // Animate outputs outward
  for (const output of outputs) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay },
      action: { type: 'show', target: output.id },
    });
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay: delay + 100 },
      action: {
        type: 'moveTo',
        target: output.id,
        x: ZONES.output.xMin + Math.random() * (ZONES.output.xMax - ZONES.output.xMin),
        y: ZONES.output.y + (Math.random() - 0.5) * 100,
        duration: 1000,
        easing: 'easeOut',
      },
    });
    delay += 400;
  }
  
  return { ...composition, behaviors: newBehaviors };
}

function generateChoreography(composition, intent) {
  console.log('🛡️ [AutoFix] Generating choreography...');
  
  const atoms = composition.atoms || [];
  const behaviors = composition.behaviors || [];
  
  if (behaviors.length >= THRESHOLDS.MIN_CHOREOGRAPHY_BEATS) {
    return composition;
  }
  
  const newBehaviors = [];
  const hero = findHero(composition);
  const env = atoms.find(a => a.role === 'environment');
  const inputs = atoms.filter(a => a.role === 'input');
  
  // ACT 1: Setup
  if (env) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay: 0 },
      action: { type: 'fadeIn', target: env.id, duration: 500 },
    });
  }
  
  if (hero) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay: 300 },
      action: { type: 'scaleIn', target: hero.id, duration: 600, fromScale: 0.5 },
    });
  }
  
  // ACT 1: Show inputs
  let delay = 700;
  for (const input of inputs) {
    newBehaviors.push({
      trigger: { type: 'scene_ready', delay },
      action: { type: 'fadeIn', target: input.id, duration: 400 },
    });
    delay += 200;
  }
  
  return { ...composition, behaviors: [...newBehaviors, ...behaviors] };
}

function inject3ActNarration(composition, intent) {
  console.log('🛡️ [AutoFix] Injecting 3-act narration...');
  
  const narration = composition.narration || [];
  
  if (narration.length >= 3) return composition;
  
  const story = intent.story || {};
  
  const defaultNarration = [
    {
      trigger: { type: 'scene_ready', delay: 500 },
      text: story.setup || 'Watch as the process begins...',
      emphasis: 'normal',
    },
    {
      trigger: { type: 'scene_ready', delay: 2500 },
      text: story.action || 'The transformation is happening now.',
      emphasis: 'high',
    },
    {
      trigger: { type: 'scene_ready', delay: 5000 },
      text: story.result || 'See the results of this process.',
      emphasis: 'normal',
    },
  ];
  
  // Merge with existing
  const merged = [...narration];
  for (let i = narration.length; i < 3; i++) {
    merged.push(defaultNarration[i]);
  }
  
  return { ...composition, narration: merged };
}

function injectEffects(composition, domain) {
  console.log('🛡️ [AutoFix] Injecting effects...');
  
  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
  const atoms = (composition.atoms || []).map(atom => {
    if (atom.role === 'hero' && !atom.effects?.some(e => e.type === 'glow')) {
      atom.effects = atom.effects || [];
      atom.effects.push({ type: 'glow', params: { color: colors.accent, intensity: 0.4, radius: 15 } });
    }
    if (!atom.effects?.some(e => e.type === 'shadow')) {
      atom.effects = atom.effects || [];
      atom.effects.push({ type: 'shadow', params: { offsetX: 3, offsetY: 3 } });
    }
    return atom;
  });
  
  return { ...composition, atoms };
}

function injectParticles(composition, domain) {
  console.log('🛡️ [AutoFix] Injecting particles...');
  
  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
  const particles = composition.particles || [];
  const hero = findHero(composition);
  
  if (particles.length > 0 || !hero) return composition;
  
  const newParticles = [
    {
      id: 'energy_particles',
      type: 'ambient',
      emitter: {
        type: 'area',
        position: hero.position || ZONES.hero,
        size: { width: 100, height: 80 },
      },
      particle: {
        shape: 'circle',
        size: [2, 5],
        color: [colors.accent, colors.secondary],
        opacity: [0.8, 0],
      },
      rate: 5,
      lifetime: 2000,
      physics: { gravity: { x: 0, y: -10 } },
      trigger: 'auto',
    },
  ];
  
  return { ...composition, particles: [...particles, ...newParticles] };
}

function bindDefaultInteraction(composition, intent) {
  console.log('🛡️ [AutoFix] Binding default interaction...');
  
  const interactions = composition.interactions || [];
  const hero = findHero(composition);
  
  if (interactions.length > 0) return composition;
  
  // Determine interaction type based on process
  const processType = intent.processType || 'transformation';
  
  const defaultInteraction = {
    id: 'control_main',
    type: 'slider',
    target: hero?.id || 'hero_main',
    property: processType === 'flow' ? 'flowRate' : 'intensity',
    range: { min: 0.5, max: 2.0, step: 0.1, default: 1.0 },
    label: processType === 'flow' ? 'Flow Rate' : 'Process Intensity',
    position: 'auto',
  };
  
  return { ...composition, interactions: [defaultInteraction] };
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function findHero(composition) {
  const atoms = composition.atoms || [];
  return atoms.find(a => a.role === 'hero' || a.params?.isHero || a.id?.includes('hero'));
}

function guessRole(atom, intent) {
  const label = (atom.params?.label || atom.id || '').toLowerCase();
  const inputs = (intent.inputs || []).map(i => i.toLowerCase());
  const outputs = (intent.outputs || []).map(o => o.toLowerCase());
  const transformer = (intent.transformer || '').toLowerCase();
  
  if (inputs.some(i => label.includes(i))) return 'input';
  if (outputs.some(o => label.includes(o))) return 'output';
  if (transformer && label.includes(transformer)) return 'hero';
  
  return 'effect';
}

function calculateBounds(composition) {
  const atoms = composition.atoms || [];
  const positions = atoms.map(a => a.position).filter(Boolean);
  
  if (positions.length === 0) {
    return { minX: 0, maxX: CANVAS_WIDTH, minY: 0, maxY: CANVAS_HEIGHT, width: CANVAS_WIDTH, height: CANVAS_HEIGHT };
  }
  
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  
  for (const atom of atoms) {
    if (!atom.position) continue;
    const x = atom.position.x;
    const y = atom.position.y;
    const w = atom.params?.width || atom.generator?.params?.width || 50;
    const h = atom.params?.height || atom.generator?.params?.height || 50;
    
    minX = Math.min(minX, x - w / 2);
    maxX = Math.max(maxX, x + w / 2);
    minY = Math.min(minY, y - h / 2);
    maxY = Math.max(maxY, y + h / 2);
  }
  
  return {
    minX,
    maxX,
    minY,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result 
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '0, 0, 0';
}

// ============================================
// EXPORTS
// ============================================

export default { qualityGateAutoFix };
