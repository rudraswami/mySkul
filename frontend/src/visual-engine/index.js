/**
 * 🎨 DRUV AI VISUAL ENGINE V6.0 (SketchSense Magic Notebook)
 * ===========================================================
 * 
 * "A personal AI tutor sketching explanations for you in a magical notebook."
 * 
 * THE WORLD'S FIRST "GENERATIVE MAGIC NOTEBOOK" FOR EDUCATION.
 * 
 * V6.0 - MAGIC NOTEBOOK ENGINE (RoughJS + Live Drawing):
 * - Hand-drawn visuals with RoughJS
 * - Live-drawing animations (pathLength)
 * - Stick figures + playful motion
 * - Highlighter marks + doodles
 * - Cinematic reveal sequences
 * - Ghost Mentor feedback
 * - Cultural asset swapping (India-first)
 * 
 * NO boxes. NO corporate UI. Just magic! ✨
 * 
 * V5.1 EVOLUTION (Intelligence Layer):
 * - Quiz Mode: Hide labels, drag-and-drop assessment
 * - Bloom's Taxonomy: recall → understand → apply
 * - Physics Validation: Real-time constraint checking
 * - Cultural Theming: Indian context asset swapping
 * - Misconception Detection: Catches impossible states
 * - Progressive Disclosure: Step-by-step scaffolding
 * 
 * V5.0 FEATURES:
 * - Multi-mode rendering (auto-detected from artifact)
 * - Dynamic layout engine (radial, vertical, horizontal)
 * - Math plot support (inline expression parsing)
 * - Physics trajectory rendering
 * - Concept map visualization
 * - Balance/scale comparisons
 * - Professor output integration
 * - Intelligent styling
 * 
 * RENDERING MODES:
 * - classic       : Original 8-template system
 * - concept_map   : Radial node layout with relationships
 * - process_flow  : Linear step sequences
 * - math_plot     : Function graphs with expression parsing
 * - trajectory    : Physics projectile motion
 * - balance_scale : Comparison visualizations
 * - timeline      : Chronological events
 * - structure     : Anatomy/component diagrams
 * 
 * INTERACTION MODES:
 * - learn         : Full visual with all labels
 * - quiz          : Labels hidden, drag-and-drop targets
 * 
 * DIFFICULTY LEVELS (Bloom's Taxonomy):
 * - recall        : Empty structure, fill labels
 * - understand    : Auto-fill after response
 * - apply         : Full interactive simulation
 * 
 * Architecture:
 * ├── components/
 * │   ├── RevolutionarySketch.jsx  (Legacy - still works)
 * │   └── ConfigDrivenSketch.jsx   (V5.1 Universal + Intelligence)
 * ├── logic/                        (V5.1 Intelligence Layer)
 * │   └── PhysicsValidator.js       (Constraint validation)
 * ├── templates/                    (8 template types)
 * │   ├── RaceTemplate.jsx
 * │   ├── ProcessTemplate.jsx
 * │   ├── CycleTemplate.jsx
 * │   ├── GraphTemplate.jsx
 * │   ├── StructureTemplate.jsx
 * │   ├── CauseEffectTemplate.jsx
 * │   ├── ScaleTemplate.jsx
 * │   └── TimelineTemplate.jsx
 * └── primitives/                   (15+ reusable components)
 *     ├── Vehicle, Ball, Arrow
 *     ├── Formula, Label, Counter
 *     ├── Track, Wave, Atom, Cell
 *     └── Graph, Cycle, Container...
 * 
 * Usage (V5.1 with Intelligence):
 * import { ConfigDrivenSketch, INTERACTION_MODES, DIFFICULTY_LEVELS } from './visual-engine';
 * 
 * // Quiz mode with recall difficulty
 * <ConfigDrivenSketch 
 *   blueprint={config}
 *   mode={INTERACTION_MODES.QUIZ}
 *   difficultyLevel={DIFFICULTY_LEVELS.RECALL}
 *   onQuizAnswer={(result) => console.log(result)}
 * />
 * 
 * // Learn mode with physics validation
 * <ConfigDrivenSketch 
 *   blueprint={config}
 *   onValidationFeedback={(feedback) => showToast(feedback)}
 * />
 * 
 * Supports: Physics, Chemistry, Biology, Mathematics
 * 
 * BACKWARDS COMPATIBLE: All V4.0/V5.0 configurations still work!
 */

// ============ SKETCHSENSE V6 - MAGIC NOTEBOOK ENGINE ============
// The NEW default renderer - hand-drawn, animated, ALIVE!
export { 
  default as UniversalSketchCanvas,
  NotebookPaper,
  GhostMentor,
  SketchSlider,
  BlueprintRenderer,
  NOTEBOOK_THEME,
} from './sketch/UniversalSketchCanvasV6';

// Sketch Primitives - RoughJS-powered components
export {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchHighlight,
  SketchStickFigure,
  SketchDoodle,
  SketchLine,
  SketchFilters,
  drawVariants,
  fadeInVariants,
  popVariants,
} from './sketch/SketchPrimitives';

// Reveal Sequence Engine - Cinematic animation flow
export {
  default as RevealSequenceEngine,
  SequenceBuilder,
  TIMING,
  ELEMENT_TYPES,
  PRESET_SEQUENCES,
  createSequence,
  buildSequence,
} from './sketch/RevealSequenceEngine';

// ============ LEGACY COMPONENTS (V5.x - Still work) ============
// ConfigDrivenSketch - V5.1 Universal + Intelligence
// RevolutionarySketch - V4 renderer
export { default as RevolutionarySketch } from './components/RevolutionarySketch';
export { 
  default as ConfigDrivenSketch,
  INTERACTION_MODES,
  DIFFICULTY_LEVELS,
} from './components/ConfigDrivenSketch';

// ============ INTELLIGENCE LAYER (V5.1 - Legacy Logic) ============
// Physics validation from logic folder (backwards compatibility)
export {
  physicsValidator as legacyPhysicsValidator,
  PhysicsValidator,
  PHYSICS_CONSTRAINTS,
  VALIDATION_STATUS as LEGACY_VALIDATION_STATUS,
  FEEDBACK_TYPE,
  validateParameter as legacyValidateParameter,
  validateAllParameters,
  crossValidateParameters,
  getParameterExplanation,
} from './logic';

// ============ TEMPLATES ============
// 8 template types for any STEM concept
export {
  RaceTemplate,
  ProcessTemplate,
  CycleTemplate,
  GraphTemplate,
  StructureTemplate,
  CauseEffectTemplate,
  ScaleTemplate,
  TimelineTemplate,
  TEMPLATE_TYPES,
  getTemplate,
} from './templates';

// ============ SKETCHSENSE TEMPLATES (V5.2 - Split Panel) ============
// Legacy hand-drawn sketch templates with comparison layouts
export { 
  default as SplitComparisonTemplate,
  SketchPad,
  VSConnector,
  SketchSlider as LegacySketchSlider, // Renamed to avoid conflict with V6
  DrawInSVG,
  AnimatedPath as SketchAnimatedPath,
  AnimatedLabel,
} from '../components/visuals/templates/SplitComparisonTemplate';

export { default as ForceComparisonTemplate } from '../components/visuals/templates/ForceComparisonTemplate';
export { SketchyFilterDefs, getSketchyFilter } from '../components/visuals/templates/SketchyFilters';

// ============ UNIVERSAL SKETCH CANVAS (V5.0 Mode Router - Legacy) ============
// Legacy mode router (V6 UniversalSketchCanvas is now the default)
export { 
  default as LegacyUniversalSketchCanvas, // Renamed to avoid conflict with V6
  MASTER_MODES,
  SKETCH_THEME,
  detectModeFromBlueprint,
  detectSubject,
} from './UniversalSketchCanvas';

// ============ VALIDATOR ENGINE (V5.0 Intelligence) ============
// Universal validation with subject-specific plugins
export {
  default as validatorEngine,
  ValidatorEngine,
  physicsValidator,
  chemistryValidator,
  biologyValidator,
  mathematicsValidator,
  getValidatorForSubject,
  validateParameter,
  VALIDATION_STATUS,
  VISUAL_EFFECTS,
} from './validators/ValidatorEngine';

// ============ FEEDBACK CONTROLLER (V5.0 Teaching Layer) ============
// Feedback loop for micro-feedback, scaffold upgrades, hints
export {
  default as FeedbackController,
  getFeedbackController,
  resetFeedbackController,
  FEEDBACK_TYPES,
  MENTOR_PERSONAS,
} from './feedback/FeedbackController';

// ============ PRIMITIVES ============
// Reusable building blocks
export {
  COLORS,
  SUBJECT_THEMES,
  ANIMATIONS,
} from './primitives';

// Individual primitives
export { default as Vehicle } from './primitives/Vehicle';
export { default as Ball } from './primitives/Ball';
export { default as Arrow } from './primitives/Arrow';
export { default as Formula } from './primitives/Formula';
export { default as Label } from './primitives/Label';
export { default as Counter } from './primitives/Counter';
export { default as Track } from './primitives/Track';
export { default as Wave } from './primitives/Wave';
export { default as Atom } from './primitives/Atom';
export { default as Cell } from './primitives/Cell';
export { default as Graph } from './primitives/Graph';
export { default as Cycle } from './primitives/Cycle';
export { default as Container } from './primitives/Container';
export { default as FlowArrow } from './primitives/FlowArrow';
export { default as MemoryHook } from './primitives/MemoryHook';
export { default as HandText } from './primitives/HandText';
export { default as AnimatedPath } from './primitives/AnimatedPath';

// Default export - ConfigDrivenSketch is the new standard
export { default } from './components/ConfigDrivenSketch';
