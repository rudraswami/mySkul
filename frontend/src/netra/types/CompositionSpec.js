/**
 * 🎬 NETRA CompositionSpec v1.0
 * ==============================
 * 
 * The single source of truth for dynamic visual compositions.
 * 
 * CompositionSpec defines WHAT to render, not HOW.
 * - Atoms: behavioral visual elements
 * - Behaviors: event-driven rules
 * - Narration: synced explanations
 * - Interactions: user controls
 * 
 * All specs are:
 * - Validated against AtomRegistry
 * - Bounded with min/max constraints
 * - Deterministic (same input → same output)
 */

// ============================================
// VALIDATION CONSTANTS
// ============================================

export const COMPOSITION_LIMITS = {
  MAX_ATOMS: 12,
  MAX_BEHAVIORS: 20,
  MAX_NARRATION_CUES: 10,
  MAX_INTERACTIONS: 5,
  MAX_ID_LENGTH: 32,
  MAX_NARRATION_TEXT: 200,
  
  STAGE_WIDTH_MIN: 400,
  STAGE_WIDTH_MAX: 1200,
  STAGE_HEIGHT_MIN: 300,
  STAGE_HEIGHT_MAX: 800,
  
  GRAVITY_MIN: -20,
  GRAVITY_MAX: 20,
};

// ============================================
// ATOM TYPES
// ============================================

/**
 * Atom Types - Multi-domain, behavioral primitives
 * 
 * Universal: Work across all domains
 * Physics: Support physics simulation
 * Structure: Containment/hierarchy
 * Math: Graphing/functions
 * Flow: Processes/sequences
 */
export const ATOM_TYPES = [
  // === Universal (5) ===
  "Entity",        // Generic object/concept (shape, color, label)
  "Label",         // Text annotation
  "Connector",     // Line/arrow between atoms
  "Region",        // Bounded area/zone
  "Annotation",    // Formula/equation overlay
  
  // === Physics-capable (5) ===
  "RigidBody",     // Physics-enabled body (mass, velocity, forces)
  "ForceVector",   // Force arrow with magnitude/direction
  "Surface",       // Ground/boundary with friction
  "Particle",      // Small point/dot (for particle systems)
  "Wave",          // Oscillating wave visualization
  
  // === Structure (3) ===
  "Container",     // Holds other atoms (cell, beaker, box)
  "Membrane",      // Semi-permeable boundary
  "Layer",         // Stacked layer (for cross-sections)
  
  // === Math/Data (3) ===
  "Graph",         // Coordinate system with axes
  "Function",      // Plotted function curve
  "DataPoint",     // Point on graph
  
  // === Flow (2) ===
  "FlowArrow",     // Directional flow indicator
  "Pathway",       // Sequence/process path
];

// ============================================
// INTENT & DOMAIN TYPES
// ============================================

export const INTENT_TYPES = [
  "conceptual",
  "causal_inquiry",
  "mechanistic",
  "comparative",
  "counterfactual",
  "quantitative",
  "intuitive",
  "temporal",
  "structural"
];

export const DOMAIN_TYPES = [
  "physics",
  "chemistry",
  "biology",
  "math",
  "general"
];

export const DIFFICULTY_LEVELS = [
  "basic",
  "intermediate",
  "advanced"
];

// ============================================
// TRIGGER & ACTION TYPES
// ============================================

export const TRIGGER_TYPES = [
  "event",         // Atom/scene event fired
  "state",         // State condition met
  "time",          // Time elapsed
  "interaction",   // User interaction
  "scene_ready"    // Scene fully loaded
];

export const ACTION_TYPES = [
  "show",          // Make visible
  "hide",          // Make invisible
  "animate",       // Trigger animation
  "setState",      // Update atom state
  "emit",          // Emit custom event
  "highlight",     // Visual emphasis
  "moveTo",        // Animate position
  "applyForce"     // Physics force (RigidBody only)
];

// ============================================
// INTERACTION TYPES
// ============================================

export const INTERACTION_TYPES = [
  "drag",          // Drag atom
  "slider",        // Adjust parameter
  "toggle",        // On/off switch
  "tap"            // Click/tap action
];

// ============================================
// ANCHOR POINTS
// ============================================

export const ANCHOR_POINTS = [
  "center",
  "top-left",
  "top-center",
  "top-right",
  "left-center",
  "right-center",
  "bottom-left",
  "bottom-center",
  "bottom-right"
];

// ============================================
// VALIDATION HELPERS
// ============================================

/** Valid ID pattern: lowercase alphanumeric + underscore */
export const ID_PATTERN = /^[a-z][a-z0-9_]{0,31}$/;

/** Check if atom type is valid */
export function isValidAtomType(type) {
  return ATOM_TYPES.includes(type);
}

/** Check if ID format is valid */
export function isValidId(id) {
  return ID_PATTERN.test(id);
}

/** Check if intent type is valid */
export function isValidIntentType(intent) {
  return INTENT_TYPES.includes(intent);
}

/** Check if domain type is valid */
export function isValidDomainType(domain) {
  return DOMAIN_TYPES.includes(domain);
}

// ============================================
// FACTORY HELPERS
// ============================================

/** Create empty CompositionSpec template */
export function createEmptyComposition(context = {}) {
  return {
    $schema: "netra/composition/v1",
    version: "1.0.0",
    id: "",
    generatedAt: new Date().toISOString(),
    context: {
      question: context.question || "",
      intent: context.intent || "conceptual",
      domain: context.domain || "general",
      difficulty: context.difficulty || "intermediate",
      ...context
    },
    atoms: [],
    behaviors: [],
    narration: [],
    interactions: [],
    stage: {
      width: 800,
      height: 600,
      background: { type: "gradient", value: ["#f8fafc", "#e2e8f0"] },
      physics: { enabled: false },
      theme: "light"
    }
  };
}

/** Create a simple atom definition */
export function createAtomDef(id, type, params = {}, position = null) {
  const atom = {
    id,
    type,
    params
  };
  
  if (position) {
    atom.position = position;
  }
  
  return atom;
}

/** Create a behavior rule */
export function createBehavior(id, trigger, action, options = {}) {
  return {
    id,
    trigger,
    action,
    once: options.once || false,
    enabled: options.enabled !== false
  };
}

/** Create a narration cue */
export function createNarrationCue(id, trigger, text, options = {}) {
  return {
    id,
    trigger,
    text: text.substring(0, COMPOSITION_LIMITS.MAX_NARRATION_TEXT),
    emphasis: options.emphasis || "normal",
    duration: options.duration || 3000,
    highlightAtoms: options.highlightAtoms || []
  };
}

// ============================================
// VALIDATION FUNCTIONS
// ============================================

/** Validate a complete CompositionSpec */
export function validateComposition(spec) {
  const errors = [];
  
  // Check required fields
  if (!spec.$schema || spec.$schema !== "netra/composition/v1") {
    errors.push("Invalid or missing $schema");
  }
  
  if (!spec.id) {
    errors.push("Missing id");
  }
  
  if (!spec.context?.question) {
    errors.push("Missing context.question");
  }
  
  // Validate atoms
  if (!Array.isArray(spec.atoms)) {
    errors.push("atoms must be an array");
  } else {
    if (spec.atoms.length > COMPOSITION_LIMITS.MAX_ATOMS) {
      errors.push(`Too many atoms (max ${COMPOSITION_LIMITS.MAX_ATOMS})`);
    }
    
    spec.atoms.forEach((atom, i) => {
      if (!atom.id) {
        errors.push(`Atom ${i}: missing id`);
      } else if (!isValidId(atom.id)) {
        errors.push(`Atom ${i}: invalid id format "${atom.id}"`);
      }
      
      if (!isValidAtomType(atom.type)) {
        errors.push(`Atom ${i}: invalid type "${atom.type}"`);
      }
    });
  }
  
  // Validate behaviors
  if (spec.behaviors && spec.behaviors.length > COMPOSITION_LIMITS.MAX_BEHAVIORS) {
    errors.push(`Too many behaviors (max ${COMPOSITION_LIMITS.MAX_BEHAVIORS})`);
  }
  
  // Validate narration
  if (spec.narration && spec.narration.length > COMPOSITION_LIMITS.MAX_NARRATION_CUES) {
    errors.push(`Too many narration cues (max ${COMPOSITION_LIMITS.MAX_NARRATION_CUES})`);
  }
  
  // Validate stage
  if (spec.stage) {
    if (spec.stage.width < COMPOSITION_LIMITS.STAGE_WIDTH_MIN || 
        spec.stage.width > COMPOSITION_LIMITS.STAGE_WIDTH_MAX) {
      errors.push(`Stage width out of range (${COMPOSITION_LIMITS.STAGE_WIDTH_MIN}-${COMPOSITION_LIMITS.STAGE_WIDTH_MAX})`);
    }
    
    if (spec.stage.height < COMPOSITION_LIMITS.STAGE_HEIGHT_MIN || 
        spec.stage.height > COMPOSITION_LIMITS.STAGE_HEIGHT_MAX) {
      errors.push(`Stage height out of range (${COMPOSITION_LIMITS.STAGE_HEIGHT_MIN}-${COMPOSITION_LIMITS.STAGE_HEIGHT_MAX})`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

export default {
  COMPOSITION_LIMITS,
  ATOM_TYPES,
  INTENT_TYPES,
  DOMAIN_TYPES,
  DIFFICULTY_LEVELS,
  TRIGGER_TYPES,
  ACTION_TYPES,
  INTERACTION_TYPES,
  ANCHOR_POINTS,
  isValidAtomType,
  isValidId,
  isValidIntentType,
  isValidDomainType,
  createEmptyComposition,
  createAtomDef,
  createBehavior,
  createNarrationCue,
  validateComposition
};
