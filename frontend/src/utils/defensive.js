/**
 * Defensive Coding Utilities
 * Helper functions to safely access nested objects and provide fallbacks
 */

/**
 * Safely get nested property with fallback
 * @param {Object} obj - The object to access
 * @param {string} path - Dot-notation path (e.g., 'user.profile.name')
 * @param {*} defaultValue - Fallback value if path doesn't exist
 * @returns {*} The value at path or defaultValue
 */
export const safeGet = (obj, path, defaultValue = null) => {
  if (!obj || typeof obj !== 'object') return defaultValue;
  
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result === null || result === undefined || typeof result !== 'object') {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result === undefined ? defaultValue : result;
};

/**
 * Safely access array with index check
 * @param {Array} arr - The array to access
 * @param {number} index - Index to access
 * @param {*} defaultValue - Fallback value
 * @returns {*} The value at index or defaultValue
 */
export const safeArrayGet = (arr, index, defaultValue = null) => {
  if (!Array.isArray(arr)) return defaultValue;
  if (index < 0 || index >= arr.length) return defaultValue;
  return arr[index] !== undefined ? arr[index] : defaultValue;
};

/**
 * Safely parse number with fallback
 * @param {*} value - Value to parse
 * @param {number} defaultValue - Fallback number
 * @returns {number} Parsed number or defaultValue
 */
export const safeNumber = (value, defaultValue = 0) => {
  const parsed = Number(value);
  return isNaN(parsed) ? defaultValue : parsed;
};

/**
 * Safely parse string with fallback
 * @param {*} value - Value to parse
 * @param {string} defaultValue - Fallback string
 * @returns {string} String value or defaultValue
 */
export const safeString = (value, defaultValue = '') => {
  if (value === null || value === undefined) return defaultValue;
  return String(value);
};

/**
 * Check if object is empty (null, undefined, or empty object/array)
 * @param {*} obj - Object to check
 * @returns {boolean} True if empty
 */
export const isEmpty = (obj) => {
  if (obj === null || obj === undefined) return true;
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  if (typeof obj === 'string') return obj.trim().length === 0;
  return false;
};

/**
 * Ensure array (convert to array if not already)
 * @param {*} value - Value to convert
 * @returns {Array} Array value
 */
export const ensureArray = (value) => {
  if (Array.isArray(value)) return value;
  if (value === null || value === undefined) return [];
  return [value];
};

/**
 * Safe JSON parse with fallback
 * @param {string} jsonString - JSON string to parse
 * @param {*} defaultValue - Fallback value
 * @returns {*} Parsed object or defaultValue
 */
export const safeJsonParse = (jsonString, defaultValue = {}) => {
  try {
    return JSON.parse(jsonString);
  } catch (e) {
    console.warn('JSON parse failed:', e);
    return defaultValue;
  }
};

/**
 * Safe division with zero check
 * @param {number} numerator - Top number
 * @param {number} denominator - Bottom number
 * @param {number} defaultValue - Fallback if division by zero
 * @returns {number} Result or defaultValue
 */
export const safeDivide = (numerator, denominator, defaultValue = 0) => {
  if (denominator === 0) return defaultValue;
  const result = numerator / denominator;
  return isNaN(result) ? defaultValue : result;
};

/**
 * Safely format date with fallback
 * @param {*} dateValue - Date to format
 * @param {string} fallback - Fallback string
 * @returns {string} Formatted date or fallback
 */
export const safeDate = (dateValue, fallback = 'N/A') => {
  if (!dateValue) return fallback;
  try {
    const date = new Date(dateValue);
    if (isNaN(date.getTime())) return fallback;
    return date.toLocaleDateString();
  } catch (e) {
    return fallback;
  }
};

/**
 * Create safe data accessor with default structure
 * @param {Object} data - Data object
 * @param {Object} defaultStructure - Default structure
 * @returns {Object} Merged object with defaults
 */
export const withDefaults = (data, defaultStructure) => {
  if (!data || typeof data !== 'object') return defaultStructure;
  return { ...defaultStructure, ...data };
};

export default {
  safeGet,
  safeArrayGet,
  safeNumber,
  safeString,
  isEmpty,
  ensureArray,
  safeJsonParse,
  safeDivide,
  safeDate,
  withDefaults
};
