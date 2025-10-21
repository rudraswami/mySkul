/**
 * Production-safe logging utility
 * Only logs warnings and errors in production
 */

const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
  // Always log errors (critical for debugging)
  error: (...args) => {
    console.error('[ERROR]', ...args);
  },

  // Always log warnings
  warn: (...args) => {
    console.warn('[WARN]', ...args);
  },

  // Only log info in development
  info: (...args) => {
    if (isDevelopment) {
      console.log('[INFO]', ...args);
    }
  },

  // Only log debug in development
  debug: (...args) => {
    if (isDevelopment) {
      console.log('[DEBUG]', ...args);
    }
  },

  // Always log (use sparingly for critical user-facing info)
  log: (...args) => {
    console.log(...args);
  },
};

export default logger;
