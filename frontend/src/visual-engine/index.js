/**
 * Druv AI Visual Builder Engine V2
 * Interactive, Animated Visual Teaching System
 * 
 * Supports: Physics, Chemistry, Biology, Mathematics
 * 
 * Phase 1-8 Complete Implementation
 */

// ============ CONFIGURATION ============
export { CONCEPT_REGISTRY, getConceptConfig, hasVisualSupport } from './config/conceptRegistry';
export { default as CONCEPT_GRAPH, getConceptDetails, getRelatedConcepts, getNextConcepts, getLearningPath } from './config/conceptGraph';
export { PROFESSOR_DIALOGUES, getDialogue, getRandomDialogue } from './config/professorDialogues';

// ============ MAIN COMPONENTS ============
export { default as InteractiveVisualCard } from './components/InteractiveVisualCard';
export { default as CompactPhysicsScene } from './components/CompactPhysicsScene';

// ============ PHASE 1: CONTEXT & LAYERS ============
export { default as ContextLayer, CONTEXT_DATA } from './components/core/ContextLayer';
export { default as LayeredVisual, LAYER_CONFIG } from './components/core/LayeredVisual';

// ============ PHASE 2: PROFESSOR AVATAR ============
export { default as ProfessorAvatar, GESTURES, EXPRESSIONS } from './components/core/ProfessorAvatar';

// ============ PHASE 4: FORMULA BINDING & GRAPHS ============
export { default as LiveGraph, MiniGraph, generateFunctionData } from './components/core/LiveGraph';
export { 
  useFormulaBinding, 
  FORMULA_DEFINITIONS, 
  OBJECT_BINDINGS,
  formatValue,
  getChangeColor,
  valueToPercent,
  percentToValue 
} from './core/FormulaBinding';

// ============ PHASE 5: CONCEPT NAVIGATION ============
export { default as ConceptNavigator } from './components/core/ConceptNavigator';

// ============ PHASE 7: TRY YOURSELF MODE ============
export { default as TryYourselfMode } from './components/core/TryYourselfMode';

// ============ PHYSICS SCENES ============
export { default as MotionVisualScene } from './components/MotionVisualScene';
export { default as GravityVisualScene } from './components/GravityVisualScene';
export { default as InteractivePhysicsScene } from './components/InteractivePhysicsScene';
export { default as ForceVisualScene } from './components/ForceVisualScene';
export { default as EnhancedForceScene } from './components/EnhancedForceScene';
export { default as CinematicForceScene } from './components/CinematicForceScene';
// Phase 8: New Physics Scenes
export { default as RefractionScene } from './components/subjects/RefractionScene';

// ============ CHEMISTRY SCENES ============
export { default as ChemistryAtomScene } from './components/subjects/ChemistryAtomScene';

// ============ BIOLOGY SCENES ============
export { default as BiologyCellScene } from './components/subjects/BiologyCellScene';
// Phase 8: New Biology Scenes
export { default as PhotosynthesisScene } from './components/subjects/PhotosynthesisScene';

// ============ MATHEMATICS SCENES ============
export { default as MathPythagorasScene } from './components/subjects/MathPythagorasScene';

// ============ CORE SYSTEMS ============
export { default as VisualSceneV2 } from './components/VisualSceneV2';
export { TOONParser } from './core/TOONParser';
export { AnimationTimeline } from './core/AnimationTimeline';
export { interactionEngine } from './core/InteractionEngine';
// Phase 1: Enhanced Animation Library
export { 
  ANIMATION_PRESETS, 
  SVG_FILTERS, 
  ParticleSystem, 
  springPhysics, 
  easings,
  microTransitions,
  gestureAnimations,
  celebrationAnimations 
} from './core/AnimationLibrary';

// ============ TEMPLATES ============
export { forceTOON, frictionTOON } from './templates/force.toon';
export { motionTOON, velocityTOON, accelerationTOON } from './templates/motion.toon';
export { gravityTOON, freeFallTOON } from './templates/gravity.toon';

// ============ UTILITIES ============
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
