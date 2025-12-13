/**
 * 🎬 Narrative Engine
 * ===================
 * 
 * 5-beat teaching system with hand drawing
 */

// DrawingHand (Phase 3 - COMPLETE)
export { default as DrawingHand, HandIdle, HandDrawing, HandPointing } from './DrawingHand';
export { FloatingHandVariants, DrawingHandVariants, PointingHandVariants } from './DrawingHand';

// TextBubble (Phase 3 - COMPLETE)
export { default as TextBubble } from './TextBubble';
export { HintBubble, InsightBubble, EncouragementBubble, MemoryHookBubble } from './TextBubble';

// HandMotionPath (Phase 3 - COMPLETE)
export { default as HandMotionPath } from './HandMotionPath';
export {
  calculateBezierPath,
  calculateSmoothPath,
  getPositionAlongPath,
  getPositionAlongBezier,
  generateWaypointsFromBlueprint,
  calculateHandRotation,
  applyEasing,
  synchronizeHandWithStroke,
  generateHandTimeline,
  getHandStateAtTime,
} from './HandMotionPath';

// NarrativeEngine (Phase 4 - COMPLETE)
export { default as NarrativeEngine, NarrativeEngine as NarrativeEngineClass } from './NarrativeEngine';
export { BEATS, BEAT_TIMINGS, BEAT_PHASES, createNarrativeEngine, validateBeats } from './NarrativeEngine';

// React wrapper (Phase 4 - COMPLETE)
export { default as NarrativePlayer, useNarrativeEngine } from './NarrativeEngineReact';

// Default export
export { default } from './DrawingHand';

