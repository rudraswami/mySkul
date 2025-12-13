/**
 * 🎨 Core Rendering Engine
 * ========================
 * 
 * The foundation of Magic Notebook Engine V6
 */

// Main renderer (Phase 1B - COMPLETE)
export { default as UniversalSketchRenderer } from './UniversalSketchRenderer';

// React Context (Phase 1B - COMPLETE)
export { EngineContext, EngineProvider, useEngine } from './EngineContext';

// Blueprint schema (Phase 1B - COMPLETE)
export { 
  BlueprintSchema, 
  validateBlueprint, 
  createEmptyBlueprint,
  mergeBlueprints,
  cloneBlueprint,
} from './BlueprintSchema';

// Top-level orchestrator (Phase 1C - TODO)
// export { default as MagicNotebookEngine } from './MagicNotebookEngine';

// Default export - UniversalSketchRenderer
export { default } from './UniversalSketchRenderer';

