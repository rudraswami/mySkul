/**
 * 🛡️ BASE VALIDATOR
 * ==================
 * 
 * Abstract base class for subject-specific validators
 * Provides common validation infrastructure
 */

// ============================================
// VALIDATION RESULT TYPES
// ============================================

export const VALIDATION_STATUS = {
  VALID: 'valid',
  WARNING: 'warning',
  ERROR: 'error',
  INFO: 'info',
};

export const FEEDBACK_TYPE = {
  SHAKE: 'shake',           // Visual shake animation
  GLOW: 'glow',             // Glow effect (valid)
  DIM: 'dim',               // Dim effect (invalid)
  SCRIBBLE: 'scribble',     // Red scribble over element
  GHOST_MENTOR: 'ghost_mentor', // Text bubble from mentor
  HIGHLIGHT: 'highlight',   // Yellow highlight
};

// ============================================
// BASE VALIDATOR CLASS
// ============================================

export class BaseValidator {
  constructor(options = {}) {
    this.options = {
      strictMode: false,        // Strict validation (no warnings)
      enableFeedback: true,     // Enable visual feedback
      subject: 'general',       // Subject name
      ...options,
    };
    
    this.rules = [];
    this.feedbackHandlers = new Map();
  }
  
  /**
   * Register a validation rule
   * @param {Object} rule - Rule definition
   */
  addRule(rule) {
    this.rules.push({
      id: rule.id,
      name: rule.name,
      description: rule.description,
      check: rule.check,          // Function: (value, context) => boolean
      message: rule.message,      // Error message or function
      severity: rule.severity || VALIDATION_STATUS.ERROR,
      feedback: rule.feedback || FEEDBACK_TYPE.SHAKE,
      ...rule,
    });
  }
  
  /**
   * Validate a value against all rules
   * @param {any} value - Value to validate
   * @param {Object} context - Additional context
   * @returns {Object} Validation result
   */
  validate(value, context = {}) {
    const results = [];
    let overallStatus = VALIDATION_STATUS.VALID;
    
    for (const rule of this.rules) {
      try {
        const isValid = rule.check(value, context);
        
        if (!isValid) {
          const message = typeof rule.message === 'function'
            ? rule.message(value, context)
            : rule.message;
          
          results.push({
            ruleId: rule.id,
            ruleName: rule.name,
            status: rule.severity,
            message,
            feedback: rule.feedback,
            suggestion: rule.suggestion?.(value, context),
          });
          
          // Update overall status
          if (rule.severity === VALIDATION_STATUS.ERROR) {
            overallStatus = VALIDATION_STATUS.ERROR;
          } else if (rule.severity === VALIDATION_STATUS.WARNING && overallStatus === VALIDATION_STATUS.VALID) {
            overallStatus = VALIDATION_STATUS.WARNING;
          }
        }
      } catch (error) {
        console.error(`Validation rule ${rule.id} failed:`, error);
      }
    }
    
    return {
      valid: overallStatus === VALIDATION_STATUS.VALID,
      status: overallStatus,
      results,
      value,
      context,
    };
  }
  
  /**
   * Register feedback handler
   * @param {string} feedbackType - Type of feedback
   * @param {Function} handler - Handler function
   */
  onFeedback(feedbackType, handler) {
    this.feedbackHandlers.set(feedbackType, handler);
  }
  
  /**
   * Trigger feedback
   * @param {string} feedbackType - Type of feedback
   * @param {Object} data - Feedback data
   */
  triggerFeedback(feedbackType, data) {
    const handler = this.feedbackHandlers.get(feedbackType);
    if (handler) {
      handler(data);
    }
  }
  
  /**
   * Get all rules
   */
  getRules() {
    return this.rules;
  }
  
  /**
   * Clear all rules
   */
  clearRules() {
    this.rules = [];
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Create a simple range validation rule
 */
export function createRangeRule(id, name, min, max, message) {
  return {
    id,
    name,
    check: (value) => value >= min && value <= max,
    message: message || `Value must be between ${min} and ${max}`,
    severity: VALIDATION_STATUS.ERROR,
    feedback: FEEDBACK_TYPE.SHAKE,
  };
}

/**
 * Create a comparison validation rule
 */
export function createComparisonRule(id, name, compareFn, message) {
  return {
    id,
    name,
    check: (value, context) => compareFn(value, context),
    message,
    severity: VALIDATION_STATUS.ERROR,
    feedback: FEEDBACK_TYPE.SHAKE,
  };
}

export default BaseValidator;

