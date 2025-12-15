/**
 * 🔮 NETRA v4.0 - Visual Intelligence Engine
 * ==========================================
 * 
 * Production-grade visual intelligence module that generates
 * unique, modern, edtech-grade visuals for any educational question.
 * 
 * Usage:
 * import { NetraEngineV4, generateVisual } from './netra/v4';
 * 
 * // As React component
 * <NetraEngineV4
 *   question="Explain photosynthesis"
 *   onGenerated={(result) => console.log(result)}
 * />
 * 
 * // Programmatically
 * const result = await generateVisual({ question: 'Explain photosynthesis' });
 */

// Main component
export { default as NetraEngineV4, NetraEngineV4 as default } from './NetraEngineV4';

// Teaching overlay
export { TeachingOverlay, Hotspot, Annotation } from './TeachingOverlay';

// API functions
export {
  generateVisual,
  analyzeQuestion,
  generateSimple,
  checkHealth,
  getMetrics,
} from './api';

// Version
export const VERSION = '4.0.0';

