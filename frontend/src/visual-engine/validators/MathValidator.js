/**
 * 🔢 MATH VALIDATOR
 * ==================
 * 
 * Validates mathematical expressions and operations
 * - Domain restrictions
 * - Division by zero
 * - Square root of negatives
 * - Logarithm domain
 * - Asymptote detection
 */

import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE } from './BaseValidator';

// ============================================
// MATH VALIDATOR
// ============================================

export class MathValidator extends BaseValidator {
  constructor(options = {}) {
    super({ subject: 'math', ...options });
    this.initializeRules();
  }
  
  /**
   * Initialize math validation rules
   */
  initializeRules() {
    // Rule 1: No division by zero
    this.addRule({
      id: 'no_division_by_zero',
      name: 'Division by Zero',
      description: 'Cannot divide by zero',
      check: (value, context) => {
        if (context.operation === 'divide' && context.denominator !== undefined) {
          return Math.abs(context.denominator) > 1e-10; // Small epsilon for floating point
        }
        return true;
      },
      message: () => `Cannot divide by zero! 🚫 Division by zero is undefined.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: () => 'Change the denominator to a non-zero value.',
    });
    
    // Rule 2: Square root domain
    this.addRule({
      id: 'sqrt_domain',
      name: 'Square Root Domain',
      description: 'Square root requires non-negative input (for real numbers)',
      check: (value, context) => {
        if (context.operation === 'sqrt') {
          return value >= 0;
        }
        return true;
      },
      message: (value) => `√${value} is not a real number! 🔢 Square root of negative numbers involves imaginary numbers (i).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: () => 'Use a non-negative number, or explore complex numbers (a + bi).',
    });
    
    // Rule 3: Logarithm domain
    this.addRule({
      id: 'log_domain',
      name: 'Logarithm Domain',
      description: 'Logarithm requires positive input',
      check: (value, context) => {
        if (context.operation === 'log' || context.operation === 'ln') {
          return value > 0;
        }
        return true;
      },
      message: (value) => `log(${value}) is undefined! 📊 Logarithm only works for positive numbers.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: () => 'Use a positive value (e.g., log(10) = 1).',
    });
    
    // Rule 4: Tan asymptotes
    this.addRule({
      id: 'tan_asymptote',
      name: 'Tangent Asymptotes',
      description: 'Tan is undefined at π/2, 3π/2, etc.',
      check: (value, context) => {
        if (context.function === 'tan') {
          const normalized = value % Math.PI;
          const halfPi = Math.PI / 2;
          return Math.abs(normalized - halfPi) > 0.01; // Small epsilon
        }
        return true;
      },
      message: (value) => `tan(${value.toFixed(2)}) approaches ±∞! 📈 Vertical asymptote at x = π/2 + nπ.`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
      suggestion: () => 'Avoid values near π/2, 3π/2, etc.',
    });
    
    // Rule 5: Probability range
    this.addRule({
      id: 'probability_range',
      name: 'Probability Range',
      description: 'Probability must be between 0 and 1',
      check: (value, context) => {
        if (context.property === 'probability') {
          return value >= 0 && value <= 1;
        }
        return true;
      },
      message: (value) => `Probability = ${value.toFixed(2)} is invalid! 🎲 Probability is between 0 (impossible) and 1 (certain).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
    });
    
    // Rule 6: Factorial domain
    this.addRule({
      id: 'factorial_domain',
      name: 'Factorial Domain',
      description: 'Factorial requires non-negative integer',
      check: (value, context) => {
        if (context.operation === 'factorial') {
          return value >= 0 && Number.isInteger(value);
        }
        return true;
      },
      message: (value) => `${value}! is undefined! ❗ Factorial only works for non-negative integers (0, 1, 2, ...).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: () => 'Use a non-negative integer like 5 (5! = 120).',
    });
    
    // Rule 7: Percentage range warning
    this.addRule({
      id: 'percentage_unusual',
      name: 'Unusual Percentage',
      description: 'Percentage over 100% or negative is unusual',
      check: (value, context) => {
        if (context.property === 'percentage') {
          return value >= 0 && value <= 100;
        }
        return true;
      },
      message: (value) => `${value.toFixed(1)}% is unusual! 💯 Percentages are typically 0-100%.`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
      suggestion: () => 'Double-check your calculation. Sometimes >100% is valid (e.g., growth rate).',
    });
    
    // Rule 8: Angle range (degrees)
    this.addRule({
      id: 'angle_range',
      name: 'Angle Range',
      description: 'Angle should be normalized',
      check: (value, context) => {
        if (context.property === 'angle' && context.unit === 'degrees') {
          // Just a warning if > 360
          return true; // Always pass, but may generate warning elsewhere
        }
        return true;
      },
    });
  }
  
  /**
   * Validate a mathematical expression
   */
  validateExpression(expression, variables = {}) {
    const results = {
      valid: true,
      errors: [],
      warnings: [],
      expression,
    };
    
    // Check for division by zero
    if (expression.includes('/')) {
      // Simplified check - in production, parse the expression properly
      const parts = expression.split('/');
      if (parts.length > 1 && parts[1].trim() === '0') {
        results.valid = false;
        results.errors.push({
          message: 'Division by zero detected!',
          feedback: FEEDBACK_TYPE.SCRIBBLE,
        });
      }
    }
    
    return results;
  }
  
  /**
   * Safe evaluate (with domain checking)
   */
  safeEvaluate(operation, value, context = {}) {
    const validation = this.validate(value, { ...context, operation });
    
    if (!validation.valid) {
      return {
        success: false,
        result: null,
        validation,
      };
    }
    
    let result;
    switch (operation) {
      case 'sqrt':
        result = Math.sqrt(value);
        break;
      case 'log':
        result = Math.log10(value);
        break;
      case 'ln':
        result = Math.log(value);
        break;
      case 'factorial':
        result = this.factorial(value);
        break;
      default:
        result = value;
    }
    
    return {
      success: true,
      result,
      validation,
    };
  }
  
  /**
   * Calculate factorial
   */
  factorial(n) {
    if (n === 0 || n === 1) return 1;
    let result = 1;
    for (let i = 2; i <= n; i++) {
      result *= i;
    }
    return result;
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Quick math validation
 */
export function validateMath(value, operation, context = {}) {
  const validator = new MathValidator();
  return validator.validate(value, { ...context, operation });
}

export default MathValidator;

