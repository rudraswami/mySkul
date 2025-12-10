/**
 * 🎨 DRUV AI VISUAL ENGINE V5.0 (SketchSense Universal)
 * =====================================================
 * 
 * Enterprise-grade UNIVERSAL visual explanation engine.
 * Built to compete with industry leaders.
 * 
 * V5.0 EVOLUTION:
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
 * Architecture:
 * ├── components/
 * │   ├── RevolutionarySketch.jsx  (Legacy - still works)
 * │   └── ConfigDrivenSketch.jsx   (V5.0 Universal - recommended)
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
 * Usage (V5.0):
 * import { ConfigDrivenSketch } from './visual-engine';
 * 
 * // Auto-detect mode from blueprint
 * <ConfigDrivenSketch blueprint={backendConfig} />
 * 
 * // With professor output integration
 * <ConfigDrivenSketch 
 *   professorOutput={professorResponse}
 *   renderDirectives={directives}
 * />
 * 
 * // Force specific mode
 * <ConfigDrivenSketch blueprint={{ mode: 'concept_map', config: {...} }} />
 * 
 * Supports: Physics, Chemistry, Biology, Mathematics
 * 
 * BACKWARDS COMPATIBLE: All V4.0 configurations still work!
 */

// ============ MAIN COMPONENTS ============
// ConfigDrivenSketch - New dynamic renderer (recommended)
// RevolutionarySketch - Legacy renderer (still works)
export { default as RevolutionarySketch } from './components/RevolutionarySketch';
export { default as ConfigDrivenSketch } from './components/ConfigDrivenSketch';

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
