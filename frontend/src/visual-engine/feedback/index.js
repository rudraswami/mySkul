/**
 * Feedback Index
 * Export all feedback components for the SketchSense V6 engine
 * Integrated with Validators (Phase 7)
 */

// Legacy V5 exports
export {
  default,
  FeedbackController,
  getFeedbackController,
  resetFeedbackController,
  FEEDBACK_TYPES,
  MENTOR_PERSONAS,
} from './FeedbackController';

// Phase 7: Validator Integration
export { ValidationFeedback, ValidationStatusIndicator } from './ValidationFeedback';
export { useValidationFeedback } from './useValidationFeedback';


  