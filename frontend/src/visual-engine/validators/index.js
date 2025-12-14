/**
 * 🛡️ Validators
 * ==============
 * 
 * Subject-specific validation engines
 */

// IMPORT first (so variables are in scope for use below)
import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE, createRangeRule, createComparisonRule } from './BaseValidator';
import { PhysicsValidator, validatePhysics } from './PhysicsValidator';
import { ChemistryValidator, validateChemistry } from './ChemistryValidator';
import { MathValidator, validateMath } from './MathValidator';
import { BiologyValidator, validateBiology } from './BiologyValidator';

// RE-EXPORT for external consumers
export { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE, createRangeRule, createComparisonRule } from './BaseValidator';
export { PhysicsValidator, validatePhysics } from './PhysicsValidator';
export { ChemistryValidator, validateChemistry } from './ChemistryValidator';
export { MathValidator, validateMath } from './MathValidator';
export { BiologyValidator, validateBiology } from './BiologyValidator';

// Default class exports
export { default as BaseValidatorDefault } from './BaseValidator';
export { default as PhysicsValidatorDefault } from './PhysicsValidator';
export { default as ChemistryValidatorDefault } from './ChemistryValidator';
export { default as MathValidatorDefault } from './MathValidator';
export { default as BiologyValidatorDefault } from './BiologyValidator';

/**
 * Get validator by subject
 */
export function getValidator(subject) {
  const validators = {
    physics: PhysicsValidator,
    chemistry: ChemistryValidator,
    math: MathValidator,
    mathematics: MathValidator,
    biology: BiologyValidator,
  };
  
  const ValidatorClass = validators[subject.toLowerCase()];
  return ValidatorClass ? new ValidatorClass() : new BaseValidator({ subject });
}

/**
 * Quick validation helper
 */
export function quickValidate(value, property, subject, context = {}) {
  const validator = getValidator(subject);
  return validator.validate(value, { ...context, property });
}

export default {
  BaseValidator,
  PhysicsValidator,
  ChemistryValidator,
  MathValidator,
  BiologyValidator,
  getValidator,
  quickValidate,
  VALIDATION_STATUS,
  FEEDBACK_TYPE,
};
