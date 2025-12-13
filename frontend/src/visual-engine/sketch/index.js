/**
 * 🎨 Sketch Components (SketchSense V6)
 * ======================================
 * 
 * Hand-drawn, RoughJS-powered primitives + reveal engine
 */

// Export all primitives (Phase 1B - ENHANCED)
export {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchHighlight,
  SketchStickFigure,
  SketchDoodle,
  SketchLine,
  SketchPath,              // ✨ NEW - Phase 1B
  TypewriterLabel,         // ✨ NEW - Phase 1B
  PulseHighlight,          // ✨ NEW - Phase 1B
  GlowEffect,              // ✨ NEW - Phase 1B
  SketchFilters,
  NOTEBOOK_THEME,
  drawVariants,
  fadeInVariants,
  popVariants,
} from './SketchPrimitives';

// Export reveal engine
export { default as RevealSequenceEngine } from './RevealSequenceEngine';
