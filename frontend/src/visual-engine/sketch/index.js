/**
 * 🎨 SKETCHSENSE V6 - Magic Notebook Engine
 * ==========================================
 * 
 * Export all SketchSense V6 components
 */

// Main Canvas
export { default as UniversalSketchCanvas } from './UniversalSketchCanvasV6';
export { 
  NotebookPaper, 
  GhostMentor, 
  SketchSlider,
  BlueprintRenderer,
  NOTEBOOK_THEME as MAGIC_NOTEBOOK_THEME,
} from './UniversalSketchCanvasV6';

// Sketch Primitives
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
  NOTEBOOK_THEME,
  drawVariants,
  fadeInVariants,
  popVariants,
} from './SketchPrimitives';

// Reveal Sequence Engine
export {
  default as RevealSequenceEngine,
  SequenceBuilder,
  TIMING,
  ELEMENT_TYPES,
  PRESET_SEQUENCES,
  createSequence,
  buildSequence,
} from './RevealSequenceEngine';


