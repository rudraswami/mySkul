/**
 * 🎨 VISUAL TEMPLATES ENGINE
 * ==========================
 * 
 * 8 Core Template Types for ANY STEM Concept
 * 
 * Template Types:
 * 1. RaceTemplate      - Comparison visualizations (velocity, force)
 * 2. ProcessTemplate   - Flow/transformation (reactions, digestion)
 * 3. CycleTemplate     - Circular processes (krebs, water cycle)
 * 4. GraphTemplate     - Mathematical relationships (v-t, s-t graphs)
 * 5. StructureTemplate - Anatomy/components (cell, atom)
 * 6. CauseEffectTemplate - Before/after comparisons
 * 7. ScaleTemplate     - Spectrum/range (pH scale, EM spectrum)
 * 8. TimelineTemplate  - Sequence of events
 */

export { default as RaceTemplate } from './RaceTemplate';
export { default as ProcessTemplate } from './ProcessTemplate';
export { default as CycleTemplate } from './CycleTemplate';
export { default as GraphTemplate } from './GraphTemplate';
export { default as StructureTemplate } from './StructureTemplate';
export { default as CauseEffectTemplate } from './CauseEffectTemplate';
export { default as ScaleTemplate } from './ScaleTemplate';
export { default as TimelineTemplate } from './TimelineTemplate';

// Template type constants
export const TEMPLATE_TYPES = {
  RACE: 'race_comparison',
  PROCESS: 'process_flow',
  CYCLE: 'cycle',
  GRAPH: 'graph_relationship',
  STRUCTURE: 'structure_anatomy',
  CAUSE_EFFECT: 'cause_effect',
  SCALE: 'scale_spectrum',
  TIMELINE: 'sequence_timeline',
};

// Template selector function
export const getTemplate = (templateType) => {
  const templateMap = {
    [TEMPLATE_TYPES.RACE]: require('./RaceTemplate').default,
    [TEMPLATE_TYPES.PROCESS]: require('./ProcessTemplate').default,
    [TEMPLATE_TYPES.CYCLE]: require('./CycleTemplate').default,
    [TEMPLATE_TYPES.GRAPH]: require('./GraphTemplate').default,
    [TEMPLATE_TYPES.STRUCTURE]: require('./StructureTemplate').default,
    [TEMPLATE_TYPES.CAUSE_EFFECT]: require('./CauseEffectTemplate').default,
    [TEMPLATE_TYPES.SCALE]: require('./ScaleTemplate').default,
    [TEMPLATE_TYPES.TIMELINE]: require('./TimelineTemplate').default,
  };
  
  return templateMap[templateType] || templateMap[TEMPLATE_TYPES.RACE];
};

