/**
 * 🎨 NETRA PRIMITIVES - MASTER INDEX
 * ===================================
 * 
 * Universal visual building blocks for ALL subjects.
 * 
 * Architecture:
 * ┌─────────────────────────────────────────────────────────┐
 * │  REASONING LAYER (Subject-Agnostic)                     │
 * │  IntentClassifier → FormSelector → LayoutVariator       │
 * │  "What visual FORM should I use?"                       │
 * ├─────────────────────────────────────────────────────────┤
 * │  SCENE PRIMITIVES (Rich Visual Scenes) ← NEW!          │
 * │  "How should this LOOK as a SCENE?"                     │
 * │  - Environments, Surfaces, Actors, Effects              │
 * ├─────────────────────────────────────────────────────────┤
 * │  PRIMITIVES (Subject-Specific Visuals)                  │
 * │  "How should this LOOK?"                                │
 * │  - Physics: Forces, Bodies, Circuits                    │
 * │  - Chemistry: Atoms, Molecules, Reactions               │
 * │  - Biology: Cells, DNA, Organs                          │
 * │  - Math: Graphs, Equations, Shapes                      │
 * │  - History: Timelines, Eras, Figures                    │
 * │  - Geography: Maps, Landmasses, Climate                 │
 * └─────────────────────────────────────────────────────────┘
 * 
 * The reasoning layer is SUBJECT-AGNOSTIC.
 * Primitives provide subject-specific APPEARANCE only.
 */

// ============================================
// SCENE PRIMITIVES (Rich Visual Scenes) - NEW!
// ============================================

export {
  // Environments
  OutdoorEnvironment,
  LabEnvironment,
  RoomEnvironment,
  
  // Surfaces
  GroundSurface,
  IceSurface,
  CarpetSurface,
  MicroscopicSurface,
  
  // Actors
  SlidingBlock,
  RollingBall,
  PersonFigure,
  CarFigure,
  
  // Forces
  ForceArrow,
  
  // Effects
  MotionTrail,
  ChaosScatter,
  
  // UI
  SceneDivider,
  SceneLabel,
  
  // Registry
  SCENE_PRIMITIVE_REGISTRY,
  getScenePrimitive,
} from './ScenePrimitives';

// ============================================
// UNIVERSAL PRIMITIVES (Work for ALL subjects)
// ============================================

export {
  // Base components
  UniversalBox,
  UniversalArrow,
  UniversalCircle,
  UniversalLine,
  UniversalLabel,
  UniversalContainer,
  VSDivider,
  TimelineMarker,
  HierarchyNode,
  
  // Theme system
  PRIMITIVE_THEMES,
  
  // Registry
  PRIMITIVE_REGISTRY,
  getPrimitive,
} from './UniversalPrimitives';

// ============================================
// PHYSICS PRIMITIVES
// ============================================

export {
  default as ForceVector,
  ActionReactionPair,
  ForceSystem,
} from './physics/ForceVector';

export {
  default as RigidBody,
} from './physics/RigidBody';

// ============================================
// CHEMISTRY PRIMITIVES
// ============================================

export {
  Atom,
  Molecule,
  ReactionArrow,
  Orbital,
  Beaker,
  CHEMISTRY_PRIMITIVES,
} from './chemistry/ChemistryPrimitives';

// ============================================
// BIOLOGY PRIMITIVES
// ============================================

export {
  Cell,
  DNAHelix,
  Organ,
  Membrane,
  EcosystemLevel,
  BIOLOGY_PRIMITIVES,
} from './biology/BiologyPrimitives';

// ============================================
// MATH PRIMITIVES
// ============================================

export {
  CoordinateAxes,
  GraphCurve,
  EquationBox,
  GeometricShape,
  NumberLine,
  SetDiagram,
  MATH_PRIMITIVES,
} from './math/MathPrimitives';

// ============================================
// HISTORY PRIMITIVES
// ============================================

export {
  EraBlock,
  HistoricalTimeline,
  MapRegion,
  FigureIcon,
  CauseEffectChain,
  HISTORY_PRIMITIVES,
} from './history/HistoryPrimitives';

// ============================================
// GEOGRAPHY PRIMITIVES
// ============================================

export {
  Mountain,
  River,
  Landmass,
  ClimateZone,
  CompassRose,
  ScaleBar,
  PopulationIndicator,
  GEOGRAPHY_PRIMITIVES,
} from './geography/GeographyPrimitives';

// ============================================
// MASTER REGISTRY
// ============================================

import { PRIMITIVE_REGISTRY } from './UniversalPrimitives';
import { CHEMISTRY_PRIMITIVES } from './chemistry/ChemistryPrimitives';
import { BIOLOGY_PRIMITIVES } from './biology/BiologyPrimitives';
import { MATH_PRIMITIVES } from './math/MathPrimitives';
import { HISTORY_PRIMITIVES } from './history/HistoryPrimitives';
import { GEOGRAPHY_PRIMITIVES } from './geography/GeographyPrimitives';

/**
 * Master registry combining all subject-specific primitives
 */
export const MASTER_PRIMITIVE_REGISTRY = {
  // Universal (base)
  ...PRIMITIVE_REGISTRY,
  
  // Subject-specific
  ...CHEMISTRY_PRIMITIVES,
  ...BIOLOGY_PRIMITIVES,
  ...MATH_PRIMITIVES,
  ...HISTORY_PRIMITIVES,
  ...GEOGRAPHY_PRIMITIVES,
};

/**
 * Get primitive by type with subject context
 */
export const getPrimitiveBySubject = (type, subject = 'general') => {
  // First try subject-specific
  const subjectRegistries = {
    physics: PRIMITIVE_REGISTRY, // Physics uses universal + ForceVector, RigidBody
    chemistry: CHEMISTRY_PRIMITIVES,
    biology: BIOLOGY_PRIMITIVES,
    math: MATH_PRIMITIVES,
    mathematics: MATH_PRIMITIVES,
    history: HISTORY_PRIMITIVES,
    geography: GEOGRAPHY_PRIMITIVES,
  };
  
  const subjectRegistry = subjectRegistries[subject?.toLowerCase()];
  if (subjectRegistry && subjectRegistry[type]) {
    return subjectRegistry[type];
  }
  
  // Fall back to master registry
  return MASTER_PRIMITIVE_REGISTRY[type] || PRIMITIVE_REGISTRY.box;
};

/**
 * Get theme for subject
 */
export const getSubjectTheme = (subject) => {
  const themes = {
    physics: 'physics',
    chemistry: 'chemistry',
    biology: 'biology',
    math: 'math',
    mathematics: 'math',
    history: 'history',
    geography: 'geography',
    civics: 'history',
    economics: 'math',
    environmental: 'geography',
  };
  
  return themes[subject?.toLowerCase()] || 'default';
};
