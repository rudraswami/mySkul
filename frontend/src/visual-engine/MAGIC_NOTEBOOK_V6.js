/**
 * ✨ MAGIC NOTEBOOK ENGINE V6
 * ============================
 * 
 * Complete Export - All 10 Phases
 * 
 * This is the MAIN ENTRY POINT for Magic Notebook Engine
 */

// ============================================
// MAIN ENGINE (Phase 10)
// ============================================
export { default as MagicNotebookEngine } from './MagicNotebookEngine';

// ============================================
// CORE (Phase 1)
// ============================================
export { default as UniversalSketchRenderer } from './core/UniversalSketchRenderer';
export * from './sketch/SketchPrimitives';

// ============================================
// CONTROLS (Phase 2)
// ============================================
export * from './controls';

// ============================================
// NARRATIVE (Phase 3 & 4)
// ============================================
export * from './narrative';

// ============================================
// INTELLIGENCE (Phase 5 & 6)
// ============================================
export * from './intelligence';

// ============================================
// VALIDATORS (Phase 7)
// ============================================
export * from './validators';

// ============================================
// METAPHORS (Phase 8)
// ============================================
export * from './metaphors';

// ============================================
// MODES (Phase 9)
// ============================================
export * from './modes';

// ============================================
// FEEDBACK
// ============================================
export * from './feedback';

// ============================================
// DEFAULT EXPORT
// ============================================
export { default } from './MagicNotebookEngine';

