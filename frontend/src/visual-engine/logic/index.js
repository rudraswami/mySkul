/**
 * 🧠 SKETCHSENSE LOGIC LAYER
 * ==========================
 * 
 * Intelligence modules for the visual engine.
 * 
 * Modules:
 * - PhysicsValidator: Validates physical constraints, provides feedback
 * - (Future) MisconceptionDetector: Identifies common learning errors
 * - (Future) ProgressiveDisclosure: Bloom's taxonomy-based scaffolding
 */

// Import default and re-export as named
import physicsValidatorDefault, {
  PhysicsValidator,
  PHYSICS_CONSTRAINTS,
  VALIDATION_STATUS,
  FEEDBACK_TYPE,
  validateParameter,
  validateAllParameters,
  crossValidateParameters,
  getParameterExplanation,
} from './PhysicsValidator';

// Re-export everything
export {
  physicsValidatorDefault as physicsValidator,
  PhysicsValidator,
  PHYSICS_CONSTRAINTS,
  VALIDATION_STATUS,
  FEEDBACK_TYPE,
  validateParameter,
  validateAllParameters,
  crossValidateParameters,
  getParameterExplanation,
};

