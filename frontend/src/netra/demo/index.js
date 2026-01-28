/**
 * 🎬 NETRA DEMO VISUAL SYSTEM
 * ===========================
 * 
 * Hardcoded, bulletproof demo visuals for VC presentations.
 * Ensures 100% reliability with premium, cinematic quality.
 * 
 * Supported Questions:
 * 1. "Explain how electricity flows in a circuit with a visual"
 * 2. "Explain photosynthesis with a visual"
 * 
 * @author Netra Team
 * @version 1.0.0 (VC Demo)
 */

export { default as DemoVisualRenderer } from './DemoVisualRenderer';
export { 
  getDemoConfig, 
  isDemoQuestion, 
  getAvailableDemoQuestions,
  default as DemoInterceptor 
} from './DemoInterceptor';

// Re-export individual visuals for testing
export { default as CircuitVisual } from './visuals/CircuitVisual';
export { default as PhotosynthesisVisual } from './visuals/PhotosynthesisVisual';
