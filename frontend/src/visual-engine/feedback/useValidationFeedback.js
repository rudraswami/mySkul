/**
 * 🛡️ USE VALIDATION FEEDBACK
 * ===========================
 * 
 * React hook for validation feedback
 */

import { useState, useCallback, useRef } from 'react';
import { getValidator } from '../validators';

export function useValidationFeedback(subject = 'general') {
  const [validation, setValidation] = useState(null);
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const validatorRef = useRef(null);
  
  // Initialize validator
  if (!validatorRef.current) {
    validatorRef.current = getValidator(subject);
  }
  
  /**
   * Validate a value
   */
  const validate = useCallback((value, property, context = {}) => {
    const result = validatorRef.current.validate(value, { ...context, property });
    
    setValidation(result);
    
    // Add to history
    if (!result.valid) {
      setFeedbackHistory(prev => [
        ...prev.slice(-9), // Keep last 10
        {
          timestamp: Date.now(),
          value,
          property,
          result,
        },
      ]);
    }
    
    return result;
  }, []);
  
  /**
   * Clear validation state
   */
  const clear = useCallback(() => {
    setValidation(null);
  }, []);
  
  /**
   * Clear history
   */
  const clearHistory = useCallback(() => {
    setFeedbackHistory([]);
  }, []);
  
  /**
   * Get validator instance
   */
  const getValidatorInstance = useCallback(() => {
    return validatorRef.current;
  }, []);
  
  return {
    validation,
    validate,
    clear,
    feedbackHistory,
    clearHistory,
    validator: getValidatorInstance(),
    isValid: validation?.valid ?? true,
    errors: validation?.results.filter(r => r.status === 'error') || [],
    warnings: validation?.results.filter(r => r.status === 'warning') || [],
  };
}

export default useValidationFeedback;

