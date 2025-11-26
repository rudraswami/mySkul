/**
 * Druv AI Visual Builder Engine
 * Interactive, Animated Visual Teaching System
 * 
 * Supports: Physics, Chemistry, Biology, Mathematics
 */

// Configuration
export { CONCEPT_REGISTRY, getConceptConfig, hasVisualSupport } from './config/conceptRegistry';

// Main components
export { default as InteractiveVisualCard } from './components/InteractiveVisualCard';
export { default as CompactPhysicsScene } from './components/CompactPhysicsScene';

// Physics scenes
export { default as MotionVisualScene } from './components/MotionVisualScene';
export { default as GravityVisualScene } from './components/GravityVisualScene';
export { default as InteractivePhysicsScene } from './components/InteractivePhysicsScene';
export { default as ForceVisualScene } from './components/ForceVisualScene';
export { default as EnhancedForceScene } from './components/EnhancedForceScene';
export { default as CinematicForceScene } from './components/CinematicForceScene';

// Chemistry scenes
export { default as ChemistryAtomScene } from './components/subjects/ChemistryAtomScene';

// Biology scenes
export { default as BiologyCellScene } from './components/subjects/BiologyCellScene';

// Mathematics scenes
export { default as MathPythagorasScene } from './components/subjects/MathPythagorasScene';

// Core (legacy)
export { default as VisualSceneV2 } from './components/VisualSceneV2';
export { TOONParser } from './core/TOONParser';
export { AnimationTimeline } from './core/AnimationTimeline';

// Templates
export { forceTOON, frictionTOON } from './templates/force.toon';
export { motionTOON, velocityTOON, accelerationTOON } from './templates/motion.toon';
export { gravityTOON, freeFallTOON } from './templates/gravity.toon';

// Utilities
export { 
  getTOONTemplateForConcept, 
  generateTOONFromConcept,
  hasTemplate, 
  getAvailableConcepts,
  extractConceptFromQuestion,
} from './utils/conceptToTOON';

export { 
  getIndianContext, 
  getAnalogy, 
  toHinglish, 
  getProfessorSpeech 
} from './utils/indianContext';
