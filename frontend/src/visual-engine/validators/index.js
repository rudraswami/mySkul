/**
 * 🛡️ Validators
 * ==============
 * 
 * Subject-specific validation engines
 */

// Base validator (Phase 7 - COMPLETE)
export { default as BaseValidator, BaseValidator as BaseValidatorClass } from './BaseValidator';
export { VALIDATION_STATUS, FEEDBACK_TYPE, createRangeRule, createComparisonRule } from './BaseValidator';

// Subject validators (Phase 7 - COMPLETE)
export { default as PhysicsValidator, PhysicsValidator as PhysicsValidatorClass, validatePhysics } from './PhysicsValidator';
export { default as ChemistryValidator, ChemistryValidator as ChemistryValidatorClass, validateChemistry } from './ChemistryValidator';
export { default as MathValidator, MathValidator as MathValidatorClass, validateMath } from './MathValidator';
export { default as BiologyValidator, BiologyValidator as BiologyValidatorClass, validateBiology } from './BiologyValidator';

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
};
