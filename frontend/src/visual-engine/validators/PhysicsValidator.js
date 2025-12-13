/**
 * ⚛️ PHYSICS VALIDATOR
 * =====================
 * 
 * Validates physics concepts and prevents impossible scenarios
 * - Forces and motion
 * - Energy conservation
 * - Friction and mass constraints
 * - Velocity and acceleration limits
 */

import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE, createRangeRule } from './BaseValidator';

// ============================================
// PHYSICS CONSTANTS
// ============================================

const PHYSICS_CONSTANTS = {
  GRAVITY: 9.8,                    // m/s²
  SPEED_OF_LIGHT: 299792458,       // m/s
  MAX_REALISTIC_VELOCITY: 1000,    // m/s (for everyday scenarios)
  MIN_FRICTION: 0,
  MAX_FRICTION: 1,
  MIN_MASS: 0.001,                 // kg (very light objects)
  MAX_MASS: 1000000,               // kg (very heavy objects)
};

// ============================================
// PHYSICS VALIDATOR
// ============================================

export class PhysicsValidator extends BaseValidator {
  constructor(options = {}) {
    super({ subject: 'physics', ...options });
    this.initializeRules();
  }
  
  /**
   * Initialize physics validation rules
   */
  initializeRules() {
    // Rule 1: Mass must be positive
    this.addRule({
      id: 'mass_positive',
      name: 'Positive Mass',
      description: 'Mass must be greater than zero',
      check: (value, context) => {
        if (context.property === 'mass') {
          return value > 0;
        }
        return true;
      },
      message: (value) => `Mass cannot be ${value}. Objects have positive mass! 📦`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: () => 'Try a positive value like 5 kg or 10 kg',
    });
    
    // Rule 2: Friction coefficient range
    this.addRule({
      id: 'friction_range',
      name: 'Friction Coefficient Range',
      description: 'Friction coefficient must be between 0 and 1',
      check: (value, context) => {
        if (context.property === 'friction') {
          return value >= PHYSICS_CONSTANTS.MIN_FRICTION && value <= PHYSICS_CONSTANTS.MAX_FRICTION;
        }
        return true;
      },
      message: (value) => `Friction = ${value.toFixed(2)} is unrealistic. Friction is between 0 (ice) and 1 (rubber). 🧊`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: (value) => {
        if (value < 0) return 'Friction cannot be negative. Try 0.1 (smooth) or 0.8 (rough).';
        return 'Friction cannot exceed 1. Try 0.8 for rough surfaces.';
      },
    });
    
    // Rule 3: Velocity cannot exceed speed of light
    this.addRule({
      id: 'velocity_limit',
      name: 'Velocity Limit',
      description: 'Velocity cannot exceed speed of light',
      check: (value, context) => {
        if (context.property === 'velocity') {
          return Math.abs(value) < PHYSICS_CONSTANTS.SPEED_OF_LIGHT;
        }
        return true;
      },
      message: () => `Whoa! Nothing travels faster than light! 💡 Einstein says no!`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
    });
    
    // Rule 4: Realistic velocity warning
    this.addRule({
      id: 'velocity_realistic',
      name: 'Realistic Velocity',
      description: 'Velocity should be realistic for everyday scenarios',
      check: (value, context) => {
        if (context.property === 'velocity' && context.scenario === 'everyday') {
          return Math.abs(value) <= PHYSICS_CONSTANTS.MAX_REALISTIC_VELOCITY;
        }
        return true;
      },
      message: (value) => `Velocity = ${value.toFixed(0)} m/s is very high! 🚀 Are you launching a rocket?`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
      suggestion: () => 'For everyday objects, try velocities under 100 m/s (360 km/h).',
    });
    
    // Rule 5: Force direction consistency
    this.addRule({
      id: 'force_direction',
      name: 'Force Direction',
      description: 'Forces must have consistent direction with motion',
      check: (value, context) => {
        if (context.property === 'force' && context.velocity !== undefined) {
          // If friction force, it should oppose motion
          if (context.forceType === 'friction') {
            return (value > 0 && context.velocity < 0) || (value < 0 && context.velocity > 0) || (context.velocity === 0);
          }
        }
        return true;
      },
      message: () => `Friction force should oppose motion! 🤔 It slows things down, not speeds them up.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: () => 'Reverse the direction of the friction force.',
    });
    
    // Rule 6: Energy conservation
    this.addRule({
      id: 'energy_conservation',
      name: 'Energy Conservation',
      description: 'Total energy must be conserved',
      check: (value, context) => {
        if (context.property === 'energy' && context.initialEnergy !== undefined) {
          const tolerance = 0.1; // 10% tolerance for numerical errors
          const ratio = value / context.initialEnergy;
          return ratio >= (1 - tolerance) && ratio <= (1 + tolerance);
        }
        return true;
      },
      message: (value, context) => {
        const initial = context.initialEnergy.toFixed(1);
        const current = value.toFixed(1);
        return `Energy changed from ${initial}J to ${current}J! ⚡ Energy is conserved (no creation or destruction).`;
      },
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
      suggestion: () => 'Check if potential energy + kinetic energy remains constant.',
    });
    
    // Rule 7: Acceleration reasonable
    this.addRule({
      id: 'acceleration_reasonable',
      name: 'Reasonable Acceleration',
      description: 'Acceleration should be reasonable for scenario',
      check: (value, context) => {
        if (context.property === 'acceleration') {
          // For human scenarios, acceleration > 50 m/s² is extreme
          if (context.scenario === 'human') {
            return Math.abs(value) <= 50;
          }
        }
        return true;
      },
      message: (value) => `Acceleration = ${value.toFixed(1)} m/s² is extreme! 🎢 Humans can only handle ~10 m/s² comfortably.`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
    });
    
    // Rule 8: Time must be positive
    this.addRule({
      id: 'time_positive',
      name: 'Positive Time',
      description: 'Time must be positive',
      check: (value, context) => {
        if (context.property === 'time') {
          return value >= 0;
        }
        return true;
      },
      message: () => `Time cannot be negative! ⏰ No time travel (yet)!`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
    });
  }
  
  /**
   * Validate a physics scenario
   * @param {Object} scenario - Complete physics scenario
   */
  validateScenario(scenario) {
    const results = {
      valid: true,
      errors: [],
      warnings: [],
    };
    
    // Validate each property
    for (const [property, value] of Object.entries(scenario)) {
      const validation = this.validate(value, { ...scenario, property });
      
      if (!validation.valid) {
        results.valid = false;
        validation.results.forEach(result => {
          if (result.status === VALIDATION_STATUS.ERROR) {
            results.errors.push(result);
          } else if (result.status === VALIDATION_STATUS.WARNING) {
            results.warnings.push(result);
          }
        });
      }
    }
    
    return results;
  }
  
  /**
   * Calculate F = ma and validate
   */
  validateNewtonSecondLaw(force, mass, acceleration) {
    const expectedForce = mass * acceleration;
    const tolerance = 0.01 * expectedForce; // 1% tolerance
    
    const isValid = Math.abs(force - expectedForce) <= tolerance;
    
    return {
      valid: isValid,
      message: isValid
        ? `✓ F = ma: ${force.toFixed(2)}N = ${mass}kg × ${acceleration.toFixed(2)}m/s²`
        : `✗ F ≠ ma: ${force.toFixed(2)}N ≠ ${mass}kg × ${acceleration.toFixed(2)}m/s² = ${expectedForce.toFixed(2)}N`,
      expectedForce,
      actualForce: force,
      error: Math.abs(force - expectedForce),
    };
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Quick physics validation
 */
export function validatePhysics(value, property, context = {}) {
  const validator = new PhysicsValidator();
  return validator.validate(value, { ...context, property });
}

export default PhysicsValidator;

