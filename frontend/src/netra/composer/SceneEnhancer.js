/**
 * 🎬 SCENE ENHANCER v2.0
 * ======================
 * 
 * Transforms "diagram-like" LLM outputs into IMMERSIVE SIMULATIONS.
 * 
 * CRITICAL: This is the last line of defense against PowerPoint-style visuals.
 * 
 * DETECTION: Identifies diagram-style outputs by:
 * - Scattered small circles/boxes with labels
 * - No clear hero object
 * - No INPUT → PROCESS → OUTPUT flow
 * - No movement behaviors (only fadeIn/show)
 * 
 * TRANSFORMATION: Converts diagrams into simulations by:
 * 1. Identifying the hero concept (largest or most central atom)
 * 2. Reorganizing atoms into INPUT → PROCESS → OUTPUT zones
 * 3. Adding movement behaviors (inputs flow to center, outputs flow out)
 * 4. Adding environment context
 * 5. Enforcing large sizes for hero object
 */

// Canvas dimensions (match MagicBook)
const CANVAS_WIDTH = 720;
const CANVAS_HEIGHT = 520;

// Zone definitions for INPUT → PROCESS → OUTPUT layout
const ZONES = {
  input: { xMin: 60, xMax: 180, yCenter: 280 },
  process: { xCenter: 360, yCenter: 280 },
  output: { xMin: 540, xMax: 660, yCenter: 280 },
};

// Target coverage
const TARGET_COVERAGE = 0.85; // Fill 85% of canvas

// Minimum atom sizes (simulation, not diagram)
const MIN_ATOM_SIZES = {
  RigidBody: { width: 180, height: 120 },
  Entity: { width: 150, height: 100 },
  Surface: { width: 600, height: 30 },
  Region: { width: 400, height: 300 },
  ForceVector: { magnitude: 100 },
  Label: { fontSize: 18 },
  Connector: { strokeWidth: 4 },
};

// Hero object minimum size
const HERO_MIN_SIZE = { width: 200, height: 150 };

// Environment presets by domain
const ENVIRONMENT_PRESETS = {
  physics: {
    surface: {
      id: 'env_surface',
      type: 'Surface',
      params: {
        width: 650,
        height: 25,
        fill: '#64748B',
        stroke: '#475569',
        texture: 'rough',
        friction: 0.5,
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT - 60 },
      zIndex: -1,
    },
    backgroundRegion: {
      id: 'env_background',
      type: 'Region',
      params: {
        width: 700,
        height: 400,
        fill: 'rgba(241, 245, 249, 0.5)',
        stroke: 'transparent',
        cornerRadius: 20,
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 - 30 },
      zIndex: -10,
      initialState: { visible: true, opacity: 0.5 },
    },
  },
  chemistry: {
    backgroundRegion: {
      id: 'env_container',
      type: 'Region',
      params: {
        width: 500,
        height: 350,
        fill: 'rgba(219, 234, 254, 0.3)',
        stroke: '#93C5FD',
        strokeWidth: 2,
        cornerRadius: 15,
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
      zIndex: -5,
    },
  },
  biology: {
    backgroundRegion: {
      id: 'env_cell',
      type: 'Region',
      params: {
        width: 550,
        height: 380,
        fill: 'rgba(220, 252, 231, 0.4)',
        stroke: '#86EFAC',
        strokeWidth: 2,
        cornerRadius: 200, // Circular
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
      zIndex: -5,
    },
  },
  math: {
    backgroundRegion: {
      id: 'env_grid',
      type: 'Region',
      params: {
        width: 600,
        height: 400,
        fill: 'rgba(249, 250, 251, 0.8)',
        stroke: '#E5E7EB',
        strokeWidth: 1,
        cornerRadius: 8,
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
      zIndex: -10,
    },
  },
  default: {
    backgroundRegion: {
      id: 'env_ambient',
      type: 'Region',
      params: {
        width: 680,
        height: 450,
        fill: 'rgba(248, 250, 252, 0.6)',
        stroke: 'transparent',
        cornerRadius: 30,
      },
      position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
      zIndex: -10,
      initialState: { visible: true, opacity: 0.4 },
    },
  },
};

/**
 * Main enhancement function
 */
export function enhanceComposition(composition, options = {}) {
  console.log('🎬 [SceneEnhancer v2] Enhancing composition...');
  
  if (!composition || !composition.atoms) {
    console.warn('🎬 [SceneEnhancer] No composition to enhance');
    return composition;
  }
  
  const domain = options.domain || composition.context?.domain || 'physics';
  let enhanced = JSON.parse(JSON.stringify(composition)); // Deep clone
  
  // Step 0: DETECT if this is a diagram-style output
  const isDiagram = detectDiagramStyle(enhanced);
  console.log(`🎬 [SceneEnhancer] Diagram detected: ${isDiagram}`);
  
  if (isDiagram) {
    console.log('🎬 [SceneEnhancer] ⚠️ DIAGRAM DETECTED - Applying full transformation...');
    // Transform diagram into INPUT → PROCESS → OUTPUT simulation
    enhanced = transformDiagramToSimulation(enhanced, domain);
  }
  
  // Step 1: Calculate current bounds
  const bounds = calculateBounds(enhanced.atoms);
  console.log('🎬 [SceneEnhancer] Current bounds:', bounds);
  
  // Step 2: Calculate aggressive scale to fill 85% of canvas
  const transform = calculateAggressiveTransform(bounds, enhanced.atoms);
  console.log('🎬 [SceneEnhancer] Transform:', transform);
  
  // Step 3: Apply transform to all atoms (only if not already transformed by diagram fix)
  if (!isDiagram) {
    enhanced.atoms = enhanced.atoms.map(atom => transformAtom(atom, transform));
  }
  
  // Step 4: Enforce minimum sizes
  enhanced.atoms = enhanced.atoms.map(enforceMinimumSize);
  
  // Step 5: Add environment if missing
  enhanced.atoms = addEnvironmentIfMissing(enhanced.atoms, domain);
  
  // Step 6: Ensure hero object exists and is prominent
  enhanced.atoms = ensureHeroObject(enhanced.atoms, domain);
  
  // Step 7: Add flow behaviors if missing
  enhanced.behaviors = ensureFlowBehaviors(enhanced.behaviors || [], enhanced.atoms);
  
  // Step 8: Ensure 3 narration cues
  enhanced.narration = ensureNarration(enhanced.narration || [], domain);
  
  // Step 9: Update stage settings for immersive feel
  enhanced.stage = enhanceStage(enhanced.stage || {});
  
  // Log enhancement results
  const newBounds = calculateBounds(enhanced.atoms);
  console.log('🎬 [SceneEnhancer v2] Enhanced bounds:', newBounds);
  console.log('🎬 [SceneEnhancer v2] ✅ Enhancement complete:', {
    atomCount: enhanced.atoms.length,
    behaviorCount: enhanced.behaviors.length,
    narrationCount: enhanced.narration.length,
    coverage: `${(((newBounds.width * newBounds.height) / (CANVAS_WIDTH * CANVAS_HEIGHT)) * 100).toFixed(1)}%`,
    heroFound: enhanced.atoms.some(a => a.params?.isHero),
    environmentAdded: enhanced.atoms.some(a => a.id?.startsWith('env_')),
    wasDiagram: isDiagram,
  });
  
  return enhanced;
}

/**
 * Detect if composition looks like a diagram (scattered labeled boxes)
 */
function detectDiagramStyle(composition) {
  const atoms = composition.atoms || [];
  const behaviors = composition.behaviors || [];
  
  // Check 1: All atoms are small (< 100px)
  const smallAtoms = atoms.filter(a => {
    const w = a.params?.width || a.params?.radius * 2 || 50;
    return w < 100;
  });
  const mostlySmall = smallAtoms.length > atoms.length * 0.6;
  
  // Check 2: No clear hero (nothing > 150px wide)
  const hasHero = atoms.some(a => {
    const w = a.params?.width || a.params?.radius * 2 || 0;
    return w >= 150;
  });
  
  // Check 3: No movement behaviors (only fadeIn, show, scaleIn)
  const staticBehaviors = ['fadeIn', 'fadeOut', 'show', 'hide', 'scaleIn', 'scaleOut'];
  const hasMovement = behaviors.some(b => !staticBehaviors.includes(b.action?.type));
  
  // Check 4: Atoms are scattered (not in clear zones)
  const positions = atoms.map(a => a.position).filter(Boolean);
  const xPositions = positions.map(p => p.x);
  const yPositions = positions.map(p => p.y);
  const xSpread = Math.max(...xPositions) - Math.min(...xPositions);
  const ySpread = Math.max(...yPositions) - Math.min(...yPositions);
  const isScattered = xSpread > 200 && ySpread > 200 && !hasHero;
  
  // Check 5: Many Label or Entity atoms with similar sizes (diagram pattern)
  const entityAtoms = atoms.filter(a => a.type === 'Entity');
  const similarSizes = entityAtoms.length > 3 && 
    entityAtoms.every(a => {
      const w = a.params?.width || 60;
      return w >= 50 && w <= 100; // All similar small sizes
    });
  
  console.log('🎬 [DiagramDetect]', {
    mostlySmall,
    hasHero,
    hasMovement,
    isScattered,
    similarSizes,
  });
  
  // It's a diagram if: mostly small, no hero, no movement, OR similar-sized entities
  return (mostlySmall && !hasHero) || (!hasMovement && similarSizes) || (isScattered && similarSizes);
}

/**
 * Transform a diagram into INPUT → PROCESS → OUTPUT simulation
 */
function transformDiagramToSimulation(composition, domain) {
  const atoms = composition.atoms || [];
  const behaviors = composition.behaviors || [];
  
  console.log('🎬 [Transform] Converting diagram to simulation...');
  
  // Step 1: Identify the hero (largest or most "central" concept)
  let heroAtom = findHeroAtom(atoms);
  
  // Step 2: Classify remaining atoms as inputs or outputs
  const { inputs, outputs, hero } = classifyAtoms(atoms, heroAtom);
  
  console.log('🎬 [Transform] Classification:', {
    hero: hero?.id,
    inputs: inputs.map(a => a.id),
    outputs: outputs.map(a => a.id),
  });
  
  // Step 3: Reposition atoms into zones
  const repositionedAtoms = [];
  
  // Add hero at center (LARGE)
  if (hero) {
    const enhancedHero = {
      ...hero,
      position: { x: ZONES.process.xCenter, y: ZONES.process.yCenter },
      params: {
        ...hero.params,
        width: Math.max(hero.params?.width || 100, HERO_MIN_SIZE.width),
        height: Math.max(hero.params?.height || 80, HERO_MIN_SIZE.height),
        glow: true,
        isHero: true,
      },
      emphasis: 'high',
    };
    repositionedAtoms.push(enhancedHero);
  }
  
  // Position inputs on left, staggered vertically
  inputs.forEach((atom, i) => {
    const yOffset = (i - (inputs.length - 1) / 2) * 100;
    repositionedAtoms.push({
      ...atom,
      position: { x: ZONES.input.xMin + Math.random() * 60, y: ZONES.input.yCenter + yOffset },
      params: {
        ...atom.params,
        width: Math.max(atom.params?.width || 60, 70),
        height: Math.max(atom.params?.height || 60, 70),
      },
    });
  });
  
  // Position outputs on right (initially hidden at hero position)
  outputs.forEach((atom, i) => {
    const yOffset = (i - (outputs.length - 1) / 2) * 100;
    repositionedAtoms.push({
      ...atom,
      position: { x: ZONES.process.xCenter, y: ZONES.process.yCenter }, // Start at hero
      params: {
        ...atom.params,
        width: Math.max(atom.params?.width || 60, 65),
        height: Math.max(atom.params?.height || 60, 65),
      },
      initialState: { visible: false, opacity: 0 },
      _targetPosition: { x: ZONES.output.xMin + Math.random() * 60, y: ZONES.output.yCenter + yOffset },
    });
  });
  
  // Step 4: Generate flow behaviors
  const flowBehaviors = generateFlowBehaviors(repositionedAtoms, hero?.id);
  
  // Return transformed composition
  return {
    ...composition,
    atoms: repositionedAtoms,
    behaviors: flowBehaviors,
    _transformed: true,
  };
}

/**
 * Find the most likely hero atom
 */
function findHeroAtom(atoms) {
  // Priority 1: Explicitly marked hero
  const markedHero = atoms.find(a => a.params?.isHero || a.id?.includes('hero'));
  if (markedHero) return markedHero;
  
  // Priority 2: Largest atom
  let largestAtom = null;
  let maxArea = 0;
  atoms.forEach(atom => {
    if (atom.type === 'Label' || atom.type === 'Connector') return; // Skip labels/connectors
    const w = atom.params?.width || atom.params?.radius * 2 || 50;
    const h = atom.params?.height || atom.params?.radius * 2 || 50;
    const area = w * h;
    if (area > maxArea) {
      maxArea = area;
      largestAtom = atom;
    }
  });
  
  // Priority 3: Most central atom
  if (!largestAtom) {
    const centerX = CANVAS_WIDTH / 2;
    const centerY = CANVAS_HEIGHT / 2;
    let closestAtom = null;
    let minDist = Infinity;
    atoms.forEach(atom => {
      if (atom.type === 'Label' || atom.type === 'Connector') return;
      const pos = atom.position || { x: 0, y: 0 };
      const dist = Math.sqrt((pos.x - centerX) ** 2 + (pos.y - centerY) ** 2);
      if (dist < minDist) {
        minDist = dist;
        closestAtom = atom;
      }
    });
    largestAtom = closestAtom;
  }
  
  return largestAtom;
}

/**
 * Classify atoms into inputs, outputs, and hero
 */
function classifyAtoms(atoms, heroAtom) {
  const inputs = [];
  const outputs = [];
  
  atoms.forEach(atom => {
    if (atom.id === heroAtom?.id) return; // Skip hero
    if (atom.type === 'Label' || atom.type === 'Connector' || atom.type === 'Region' || atom.type === 'Surface') return;
    
    const label = (atom.params?.label || atom.id || '').toLowerCase();
    
    // Heuristic: Certain keywords indicate input/output
    const inputKeywords = ['input', 'energy', 'light', 'sun', 'co2', 'h2o', 'water', 'force', 'heat', 'reactant'];
    const outputKeywords = ['output', 'product', 'result', 'o2', 'oxygen', 'glucose', 'sugar', 'effect'];
    
    const isInput = inputKeywords.some(kw => label.includes(kw));
    const isOutput = outputKeywords.some(kw => label.includes(kw));
    
    if (isInput) {
      inputs.push(atom);
    } else if (isOutput) {
      outputs.push(atom);
    } else {
      // Default: left half = input, right half = output based on position
      const pos = atom.position || { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 };
      if (pos.x < CANVAS_WIDTH / 2) {
        inputs.push(atom);
      } else {
        outputs.push(atom);
      }
    }
  });
  
  // Ensure at least 1 input and 1 output
  if (inputs.length === 0 && outputs.length > 1) {
    inputs.push(outputs.shift());
  }
  if (outputs.length === 0 && inputs.length > 1) {
    outputs.push(inputs.pop());
  }
  
  return { inputs, outputs, hero: heroAtom };
}

/**
 * Generate flow behaviors for INPUT → PROCESS → OUTPUT
 */
function generateFlowBehaviors(atoms, heroId) {
  const behaviors = [];
  let delay = 0;
  
  // ACT 1: Environment + Hero appear
  behaviors.push({
    trigger: { type: 'scene_ready', delay: 0 },
    action: { type: 'fadeIn', target: 'env_container', duration: 400 },
  });
  
  behaviors.push({
    trigger: { type: 'scene_ready', delay: 200 },
    action: { type: 'scaleIn', target: heroId, duration: 600 },
  });
  delay = 800;
  
  // ACT 1: Inputs fade in
  const inputs = atoms.filter(a => !a.params?.isHero && !a.initialState?.visible === false && !a.id?.startsWith('env_'));
  inputs.forEach((atom, i) => {
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 150 },
      action: { type: 'fadeIn', target: atom.id, duration: 300 },
    });
  });
  delay += inputs.length * 150 + 400;
  
  // ACT 2: Inputs move to process zone
  inputs.forEach((atom, i) => {
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 200 },
      action: { type: 'moveTo', target: atom.id, x: 280, y: ZONES.process.yCenter + (i - 1) * 50, duration: 1000 },
    });
  });
  delay += inputs.length * 200 + 1000;
  
  // ACT 2: Hero pulses (reaction)
  behaviors.push({
    trigger: { type: 'scene_ready', delay: delay },
    action: { type: 'pulse', target: heroId, duration: 800, scale: 1.1 },
  });
  delay += 800;
  
  // ACT 2: Outputs appear
  const outputs = atoms.filter(a => a.initialState?.visible === false);
  outputs.forEach((atom, i) => {
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 200 },
      action: { type: 'show', target: atom.id },
    });
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 200 + 100 },
      action: { type: 'fadeIn', target: atom.id, duration: 300 },
    });
  });
  delay += outputs.length * 200 + 400;
  
  // ACT 3: Outputs move to output zone
  outputs.forEach((atom, i) => {
    const targetPos = atom._targetPosition || { x: 580, y: ZONES.output.yCenter + (i - 1) * 80 };
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 200 },
      action: { type: 'moveTo', target: atom.id, x: targetPos.x, y: targetPos.y, duration: 1000 },
    });
  });
  delay += outputs.length * 200 + 1000;
  
  // ACT 3: Highlight outputs
  outputs.forEach((atom, i) => {
    behaviors.push({
      trigger: { type: 'scene_ready', delay: delay + i * 300 },
      action: { type: 'highlight', target: atom.id, duration: 2000 },
    });
  });
  
  return behaviors;
}

/**
 * Ensure flow behaviors exist
 */
function ensureFlowBehaviors(behaviors, atoms) {
  // Check if moveTo behaviors exist
  const hasMovement = behaviors.some(b => b.action?.type === 'moveTo');
  if (hasMovement) return behaviors;
  
  // Add basic flow behaviors if missing
  const inputAtoms = atoms.filter(a => 
    !a.params?.isHero && 
    !a.id?.startsWith('env_') && 
    a.type !== 'Region' && 
    a.type !== 'Surface'
  );
  
  if (inputAtoms.length > 0) {
    console.log('🎬 [SceneEnhancer] Adding flow behaviors for', inputAtoms.length, 'atoms');
    // Add moveTo for first non-hero, non-env atom
    behaviors.push({
      trigger: { type: 'scene_ready', delay: 1500 },
      action: { type: 'moveTo', target: inputAtoms[0].id, x: 300, y: 280, duration: 1200 },
    });
  }
  
  return behaviors;
}

/**
 * Ensure 3 narration cues exist
 */
function ensureNarration(narration, domain) {
  if (narration.length >= 3) return narration;
  
  const defaultNarration = [
    {
      trigger: { type: 'scene_ready', delay: 500 },
      text: 'Watch as the process begins...',
      emphasis: 'normal',
    },
    {
      trigger: { type: 'scene_ready', delay: 2500 },
      text: 'The transformation is happening now',
      emphasis: 'high',
    },
    {
      trigger: { type: 'scene_ready', delay: 5000 },
      text: 'See the results of this process',
      emphasis: 'normal',
    },
  ];
  
  // Merge with existing, keeping first few from original
  const merged = [...narration];
  while (merged.length < 3) {
    merged.push(defaultNarration[merged.length]);
  }
  
  return merged;
}

/**
 * Calculate bounding box of all atoms
 */
function calculateBounds(atoms) {
  const positions = atoms
    .map(a => a.position)
    .filter(Boolean);
  
  if (positions.length === 0) {
    return { minX: 0, maxX: CANVAS_WIDTH, minY: 0, maxY: CANVAS_HEIGHT, width: CANVAS_WIDTH, height: CANVAS_HEIGHT };
  }
  
  // Include atom sizes in bounds
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  
  atoms.forEach(atom => {
    if (!atom.position) return;
    const x = atom.position.x || 0;
    const y = atom.position.y || 0;
    const w = atom.params?.width || atom.params?.radius * 2 || 50;
    const h = atom.params?.height || atom.params?.radius * 2 || 50;
    
    minX = Math.min(minX, x - w / 2);
    maxX = Math.max(maxX, x + w / 2);
    minY = Math.min(minY, y - h / 2);
    maxY = Math.max(maxY, y + h / 2);
  });
  
  return {
    minX,
    maxX,
    minY,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
    centerX: (minX + maxX) / 2,
    centerY: (minY + maxY) / 2,
  };
}

/**
 * Calculate AGGRESSIVE transform to fill canvas
 */
function calculateAggressiveTransform(bounds, atoms) {
  const targetWidth = CANVAS_WIDTH * TARGET_COVERAGE;
  const targetHeight = CANVAS_HEIGHT * TARGET_COVERAGE;
  
  // Calculate scale needed to fill target area
  let scaleX = bounds.width > 0 ? targetWidth / bounds.width : 1;
  let scaleY = bounds.height > 0 ? targetHeight / bounds.height : 1;
  
  // Use the smaller scale to maintain aspect ratio
  let scale = Math.min(scaleX, scaleY);
  
  // 🔥 AGGRESSIVE: If content is small, scale up MORE (up to 4x)
  // If content is already large, don't scale down below 0.8x
  scale = Math.max(0.8, Math.min(4.0, scale));
  
  // Force minimum scale of 1.5 if content is tiny (< 30% of canvas)
  const currentCoverage = (bounds.width * bounds.height) / (CANVAS_WIDTH * CANVAS_HEIGHT);
  if (currentCoverage < 0.3) {
    scale = Math.max(scale, 2.0);
    console.log('🎬 [SceneEnhancer] 🔥 Tiny content detected, forcing scale >= 2.0');
  }
  
  // Calculate offset to center scaled content
  const scaledWidth = bounds.width * scale;
  const scaledHeight = bounds.height * scale;
  const offsetX = (CANVAS_WIDTH - scaledWidth) / 2 - bounds.minX * scale;
  const offsetY = (CANVAS_HEIGHT - scaledHeight) / 2 - bounds.minY * scale;
  
  return { scale, offsetX, offsetY };
}

/**
 * Transform atom position and size
 */
function transformAtom(atom, transform) {
  const transformed = { ...atom };
  
  // Transform position
  if (transformed.position) {
    transformed.position = {
      x: transformed.position.x * transform.scale + transform.offsetX,
      y: transformed.position.y * transform.scale + transform.offsetY,
    };
  } else {
    // If no position, center it
    transformed.position = {
      x: CANVAS_WIDTH / 2,
      y: CANVAS_HEIGHT / 2,
    };
  }
  
  // Scale params
  if (transformed.params) {
    if (transformed.params.width) {
      transformed.params.width *= transform.scale;
    }
    if (transformed.params.height) {
      transformed.params.height *= transform.scale;
    }
    if (transformed.params.radius) {
      transformed.params.radius *= transform.scale;
    }
    if (transformed.params.magnitude) {
      transformed.params.magnitude *= transform.scale;
    }
    if (transformed.params.fontSize && transform.scale > 1) {
      // Only scale up font, not down
      transformed.params.fontSize = Math.min(
        transformed.params.fontSize * Math.sqrt(transform.scale),
        32
      );
    }
  }
  
  return transformed;
}

/**
 * Enforce minimum sizes for atoms
 */
function enforceMinimumSize(atom) {
  const minSize = MIN_ATOM_SIZES[atom.type];
  if (!minSize) return atom;
  
  const enforced = { ...atom, params: { ...atom.params } };
  
  if (minSize.width && enforced.params.width < minSize.width) {
    console.log(`🎬 [SceneEnhancer] Enforcing min width for ${atom.id}: ${enforced.params.width} → ${minSize.width}`);
    enforced.params.width = minSize.width;
  }
  if (minSize.height && enforced.params.height < minSize.height) {
    console.log(`🎬 [SceneEnhancer] Enforcing min height for ${atom.id}: ${enforced.params.height} → ${minSize.height}`);
    enforced.params.height = minSize.height;
  }
  if (minSize.magnitude && enforced.params.magnitude < minSize.magnitude) {
    enforced.params.magnitude = minSize.magnitude;
  }
  if (minSize.fontSize && enforced.params.fontSize < minSize.fontSize) {
    enforced.params.fontSize = minSize.fontSize;
  }
  
  return enforced;
}

/**
 * Add environment elements if missing
 */
function addEnvironmentIfMissing(atoms, domain) {
  // Check if environment already exists
  const hasSurface = atoms.some(a => a.type === 'Surface');
  const hasRegion = atoms.some(a => a.type === 'Region');
  const hasEnvironment = hasSurface || hasRegion;
  
  if (hasEnvironment) {
    console.log('🎬 [SceneEnhancer] Environment already present');
    return atoms;
  }
  
  console.log(`🎬 [SceneEnhancer] Adding environment for domain: ${domain}`);
  
  const preset = ENVIRONMENT_PRESETS[domain] || ENVIRONMENT_PRESETS.default;
  const envAtoms = [];
  
  // Add background region
  if (preset.backgroundRegion) {
    envAtoms.push(preset.backgroundRegion);
  }
  
  // Add surface for physics-like domains
  if (preset.surface && ['physics', 'default'].includes(domain)) {
    envAtoms.push(preset.surface);
  }
  
  // Add env atoms at the beginning (low z-index)
  return [...envAtoms, ...atoms];
}

/**
 * Ensure a hero object exists and is prominent
 */
function ensureHeroObject(atoms, domain = 'physics') {
  // Check if hero already exists
  const existingHero = atoms.find(a => a.params?.isHero);
  if (existingHero) {
    console.log(`🎬 [SceneEnhancer] Hero already exists: ${existingHero.id}`);
    // Just ensure it's large enough
    return atoms.map(a => {
      if (a.params?.isHero) {
        return {
          ...a,
          params: {
            ...a.params,
            width: Math.max(a.params.width || 100, HERO_MIN_SIZE.width),
            height: Math.max(a.params.height || 80, HERO_MIN_SIZE.height),
            glow: true,
          },
          position: a.position || { x: ZONES.process.xCenter, y: ZONES.process.yCenter },
          emphasis: 'high',
        };
      }
      return a;
    });
  }
  
  // Find the largest non-environment atom
  const contentAtoms = atoms.filter(a => !a.id?.startsWith('env_') && a.type !== 'Label' && a.type !== 'Connector' && a.type !== 'Region');
  
  if (contentAtoms.length === 0) {
    console.log('🎬 [SceneEnhancer] No content atoms found - creating default hero');
    // Create a default hero
    const domainColors = {
      physics: '#3B82F6',
      chemistry: '#8B5CF6',
      biology: '#10B981',
      math: '#6366F1',
    };
    atoms.push({
      id: 'hero_process',
      type: 'Entity',
      position: { x: ZONES.process.xCenter, y: ZONES.process.yCenter },
      params: {
        shape: 'ellipse',
        width: HERO_MIN_SIZE.width,
        height: HERO_MIN_SIZE.height,
        fill: domainColors[domain] || '#3B82F6',
        stroke: '#1D4ED8',
        strokeWidth: 4,
        label: 'Process',
        labelColor: '#FFFFFF',
        glow: true,
        isHero: true,
      },
      emphasis: 'high',
      zIndex: 5,
    });
    return atoms;
  }
  
  // Find the largest atom by area
  let heroAtom = null;
  let maxArea = 0;
  
  contentAtoms.forEach(atom => {
    const w = atom.params?.width || atom.params?.radius * 2 || 50;
    const h = atom.params?.height || atom.params?.radius * 2 || 50;
    const area = w * h;
    if (area > maxArea) {
      maxArea = area;
      heroAtom = atom;
    }
  });
  
  if (heroAtom) {
    console.log(`🎬 [SceneEnhancer] Hero object: ${heroAtom.id} (${heroAtom.params?.width}x${heroAtom.params?.height})`);
    
    // Mark as hero, enlarge, and add emphasis
    return atoms.map(a => {
      if (a.id === heroAtom.id) {
        return {
          ...a,
          params: {
            ...a.params,
            width: Math.max(a.params?.width || 100, HERO_MIN_SIZE.width),
            height: Math.max(a.params?.height || 80, HERO_MIN_SIZE.height),
            isHero: true,
            glow: true,
            shadow: true,
          },
          position: a.position || { x: ZONES.process.xCenter, y: ZONES.process.yCenter },
          emphasis: 'high',
        };
      }
      return a;
    });
  }
  
  return atoms;
}

/**
 * Enhance behaviors with visual effects
 */
function enhanceBehaviors(behaviors) {
  // Check if behaviors already have effects
  const hasEffects = behaviors.some(b => 
    ['pulse', 'glow', 'particles'].includes(b.action?.type)
  );
  
  if (hasEffects || behaviors.length === 0) {
    return behaviors;
  }
  
  // Add a subtle pulse to the first atom after scene loads
  const firstShowBehavior = behaviors.find(b => 
    b.trigger?.type === 'scene_ready' && b.action?.type === 'fadeIn'
  );
  
  if (firstShowBehavior) {
    // Add a follow-up pulse
    behaviors.push({
      trigger: {
        type: 'scene_ready',
        delay: 1500,
      },
      action: {
        type: 'pulse',
        target: firstShowBehavior.action?.target,
        loop: true,
        duration: 2000,
      },
    });
  }
  
  return behaviors;
}

/**
 * Enhance stage settings
 */
function enhanceStage(stage) {
  return {
    ...stage,
    width: CANVAS_WIDTH,
    height: CANVAS_HEIGHT,
    background: {
      type: 'gradient',
      value: ['#FAFBFC', '#F1F5F9'],
      direction: 'vertical',
      forceBackground: false, // Keep transparent for MagicBook
    },
  };
}

export default { enhanceComposition };
