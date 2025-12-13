/**
 * 🧠 Intelligence Layer
 * =====================
 * 
 * The "brain" that generates visual blueprints
 */

// SceneComposer (Phase 5 - COMPLETE)
export { default as SceneComposer, SceneComposer as SceneComposerClass } from './SceneComposer';
export { createSceneComposer, composeScene } from './SceneComposer';

// ConceptBreaker (Phase 6 - COMPLETE)
export { default as ConceptBreaker, ConceptBreaker as ConceptBreakerClass } from './ConceptBreaker';
export { VISUAL_MODES, conceptBreakerAPI, createConceptBreaker, breakConcept } from './ConceptBreaker';

// MetaphorMapper (Phase 8 - TODO)
// export { default as MetaphorMapper } from './MetaphorMapper';

// ModeDetector (Phase 6 - TODO)
// export { default as ModeDetector } from './ModeDetector';

// Default export
export { default } from './SceneComposer';

