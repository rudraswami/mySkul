/**
 * 📝 Response Components
 * ======================
 * 
 * Enhanced AI response rendering system.
 */

export { default as AdaptiveResponseCard } from './AdaptiveResponseCard';
export { default as ResponseFormatter, formatResponse } from './ResponseFormatter';

// Individual section exports for custom compositions
export {
  ResponseSection,
  HookSection,
  DefinitionSection,
  FormulaSection,
  ExamFocusSection,
  MemorySection,
  IndianContextSection,
  CommonMistakesSection,
  TopperTipsSection,
  StepsSection,
  QuickRecallSection,
  ProgressSection,
} from './AdaptiveResponseCard';

