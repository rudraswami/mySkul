/**
 * 🔮 NETRA v3.0 - Intent-Driven Visual Reasoning Engine
 * ======================================================
 * 
 * "नेत्र" = Eye — Seeing concepts clearly
 * 
 * A Gemini-level visual intelligence engine for education.
 * 
 * v3.0 KEY FEATURES:
 * ✅ INTENT-DRIVEN: Same topic + different question = different visual
 * ✅ SUBJECT-AGNOSTIC: One reasoning layer for all domains
 * ✅ DYNAMIC FORMS: Visual structure chosen at runtime
 * ✅ LAYOUT VARIATION: Never the same layout twice
 * ✅ ANIMATION INTELLIGENCE: Reveal strategy matches intent
 * 
 * Pipeline:
 * Question → Intent → Form → Content → Layout → Animation → Visual
 * 
 * Usage:
 * import { NetraEngine, generateVisual } from './netra';
 * 
 * // As React component
 * <NetraEngine
 *   question="What if there was no friction?"
 *   context={{ subject: 'physics' }}
 * />
 * 
 * // Programmatically
 * const result = await generateVisual('Compare static vs kinetic friction');
 * console.log(result.reasoning.intent); // → 'comparative'
 * console.log(result.reasoning.form);   // → 'comparison'
 */

// ============================================
// MAIN COMPONENT
// ============================================

export { default as NetraEngine, NetraEngine as default } from './NetraEngine';

// ============================================
// CORE
// ============================================

export {
  Orchestrator,
  createOrchestrator,
  getOrchestrator,
  generateVisual,
} from './core/Orchestrator';

export {
  ConceptGraph,
  createForceGraph,
  createProcessGraph,
  createStructureGraph,
  ENTITY_TYPES,
  RELATIONSHIP_TYPES,
  CONSTRAINT_TYPES,
} from './core/ConceptGraph';

// ============================================
// UNDERSTANDING
// ============================================

export {
  SemanticParser,
  createSemanticParser,
  parseQuestion,
} from './understanding/SemanticParser';

// ============================================
// SEMANTICS
// ============================================

export {
  VISUAL_FORMS,
  PHYSICS_ONTOLOGY,
  CHEMISTRY_ONTOLOGY,
  BIOLOGY_ONTOLOGY,
  MATH_ONTOLOGY,
  getVisualSpec,
  getDomainConcepts,
  findVisualSpec,
} from './semantics/VisualOntology';

// ============================================
// COMPOSITION
// ============================================

export {
  CompositionEngine,
  createCompositionEngine,
  composeScene,
  SceneGraph,
  SceneNode,
  COMPOSITION_STRATEGIES,
} from './composition/CompositionEngine';

// ============================================
// RENDERING
// ============================================

export {
  default as SVGRenderer,
  NETRA_THEME,
  SketchFilters,
} from './rendering/SVGRenderer';

export {
  default as AnimatedRenderer,
} from './rendering/AnimatedRenderer';

// ============================================
// NARRATIVE - Teaching Beat System
// ============================================

export {
  TeachingBeatEngine,
  createTeachingBeatEngine,
  TeachingBeat,
  TeachingSequence,
  BEAT_TYPES,
} from './narrative/TeachingBeatEngine';

// ============================================
// SEMANTIC POSITIONING
// ============================================

export {
  SemanticPositioner,
  createSemanticPositioner,
} from './composition/SemanticPositioner';

// ============================================
// VISUAL REASONING LAYER (v3.0)
// ============================================

export {
  // Intent Classification
  IntentClassifier,
  createIntentClassifier,
  INTENT_TYPES,
  
  // Form Selection
  FormSelector,
  createFormSelector,
  STRUCTURAL_FORMS,
  FORM_SPECIFICATIONS,
  
  // Content Mapping
  ContentMapper,
  createContentMapper,
  
  // Layout Variation
  LayoutVariator,
  createLayoutVariator,
  LAYOUT_VARIANTS,
  
  // Animation Direction
  AnimationDirector,
  createAnimationDirector,
  ANIMATION_STRATEGIES,
  
  // Pipeline Factory
  createReasoningPipeline,
} from './reasoning';

// ============================================
// PRIMITIVES - ALL SUBJECTS
// ============================================

// Universal primitives (work for all subjects)
export {
  UniversalBox,
  UniversalArrow,
  UniversalCircle,
  UniversalLine,
  UniversalLabel,
  UniversalContainer,
  VSDivider,
  TimelineMarker,
  HierarchyNode,
  PRIMITIVE_THEMES,
  PRIMITIVE_REGISTRY,
  getPrimitive,
} from './primitives/UniversalPrimitives';

// Physics primitives
export {
  default as ForceVector,
  ActionReactionPair,
  ForceSystem,
} from './primitives/physics/ForceVector';

export {
  default as RigidBody,
} from './primitives/physics/RigidBody';

// Chemistry primitives
export {
  Atom,
  Molecule,
  ReactionArrow,
  Orbital,
  Beaker,
  CHEMISTRY_PRIMITIVES,
} from './primitives/chemistry/ChemistryPrimitives';

// Biology primitives
export {
  Cell,
  DNAHelix,
  Organ,
  Membrane,
  EcosystemLevel,
  BIOLOGY_PRIMITIVES,
} from './primitives/biology/BiologyPrimitives';

// Math primitives
export {
  CoordinateAxes,
  GraphCurve,
  EquationBox,
  GeometricShape,
  NumberLine,
  SetDiagram,
  MATH_PRIMITIVES,
} from './primitives/math/MathPrimitives';

// History primitives
export {
  EraBlock,
  HistoricalTimeline,
  MapRegion,
  FigureIcon,
  CauseEffectChain,
  HISTORY_PRIMITIVES,
} from './primitives/history/HistoryPrimitives';

// Geography primitives
export {
  Mountain,
  River,
  Landmass,
  ClimateZone,
  CompassRose,
  ScaleBar,
  PopulationIndicator,
  GEOGRAPHY_PRIMITIVES,
} from './primitives/geography/GeographyPrimitives';

// Master registry
export {
  MASTER_PRIMITIVE_REGISTRY,
  getPrimitiveBySubject,
  getSubjectTheme,
} from './primitives';

// ============================================
// INTEGRATION
// ============================================

export {
  default as SmartBoardAdapter,
  useNetraWithSmartBoard,
} from './integration/SmartBoardAdapter';



