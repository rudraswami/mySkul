/**
 * 🎨 Visual Modes
 * ================
 * 
 * 8 Master Modes for different types of educational content
 */

// Individual modes (Phase 9 - COMPLETE)
export { default as SceneMode } from './SceneMode';
export { default as ComparisonMode } from './ComparisonMode';
export { default as ProcessMode } from './ProcessMode';
export { default as CycleMode } from './CycleMode';
export { default as StructureMode } from './StructureMode';
export { default as GraphMode } from './GraphMode';
export { default as TimelineMode } from './TimelineMode';
export { default as HierarchyMode } from './HierarchyMode';

// Mode Router (Phase 9 - COMPLETE)
export { default as ModeRouter, ModeRouter as ModeRouterComponent } from './ModeRouter';
export { MODES, getModeComponent, getModeMetadata, getAllModes } from './ModeRouter';

// Default export
export { default } from './ModeRouter';
