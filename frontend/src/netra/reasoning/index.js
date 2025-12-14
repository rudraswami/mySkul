/**
 * 🧠 REASONING MODULE
 * ===================
 * 
 * The Visual Reasoning Layer for NETRA.
 * 
 * This is what makes NETRA an INTELLIGENT visual engine,
 * not a template-based diagram generator.
 * 
 * Pipeline:
 * Question → Intent → Form → Content → Layout → Animation → Visual
 * 
 * Each layer is subject-agnostic and question-driven.
 */

// Intent Classification
export {
  IntentClassifier,
  createIntentClassifier,
  INTENT_TYPES,
} from './IntentClassifier';

// Form Selection
export {
  FormSelector,
  createFormSelector,
  STRUCTURAL_FORMS,
  FORM_SPECIFICATIONS,
} from './FormSelector';

// Content Mapping
export {
  ContentMapper,
  createContentMapper,
} from './ContentMapper';

// Layout Variation
export {
  LayoutVariator,
  createLayoutVariator,
  LAYOUT_VARIANTS,
} from './LayoutVariator';

// Animation Direction
export {
  AnimationDirector,
  createAnimationDirector,
  ANIMATION_STRATEGIES,
} from './AnimationDirector';

/**
 * Create the complete reasoning pipeline
 */
export function createReasoningPipeline(options = {}) {
  return {
    intentClassifier: createIntentClassifier(options.intent || {}),
    formSelector: createFormSelector(options.form || {}),
    contentMapper: createContentMapper(options.content || {}),
    layoutVariator: createLayoutVariator(options.layout || {}),
    animationDirector: createAnimationDirector(options.animation || {}),
  };
}

