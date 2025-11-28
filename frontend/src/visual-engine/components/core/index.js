/**
 * Core Visual Engine Components - Index
 * 
 * Exports all Phase 1-7 components for easy importing
 */

// Phase 1: Context & Layers
export { default as ContextLayer, CONTEXT_DATA } from './ContextLayer';
export { default as LayeredVisual, LAYER_CONFIG } from './LayeredVisual';

// Phase 2: Professor Avatar
export { default as ProfessorAvatar, GESTURES, EXPRESSIONS } from './ProfessorAvatar';

// Phase 4: Formula Binding & Graphs
export { default as LiveGraph, MiniGraph, generateFunctionData } from './LiveGraph';

// Phase 5: Concept Navigation
export { default as ConceptNavigator } from './ConceptNavigator';

// Phase 7: Try Yourself Mode
export { default as TryYourselfMode } from './TryYourselfMode';



