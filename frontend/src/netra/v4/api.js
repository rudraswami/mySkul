/**
 * 🔮 NETRA v4.0 - API Client
 * ==========================
 * 
 * Client for communicating with the NETRA v4 backend API.
 * Handles visual generation, analysis, and health checks.
 */

// Get API base URL from environment
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const NETRA_V4_BASE = `${API_BASE}/api/netra/v4`;

/**
 * Generate a visual for a question
 * @param {Object} params - Generation parameters
 * @param {string} params.question - The student's question
 * @param {string} params.user_level - User level (beginner/intermediate/advanced)
 * @param {string} params.language - Language preference
 * @param {string[]} params.previous_questions - Previous questions in session
 * @param {string} params.force_style - Force specific visual style
 * @param {string} params.force_intent - Force specific teaching intent
 * @returns {Promise<Object>} Visual response
 */
export async function generateVisual({
  question,
  user_level = 'intermediate',
  language = 'en',
  previous_questions = [],
  force_style = null,
  force_intent = null,
}) {
  const response = await fetch(`${NETRA_V4_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      question,
      user_level,
      language,
      previous_questions,
      force_style,
      force_intent,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Analyze a question without generating a visual
 * @param {Object} params - Analysis parameters
 * @param {string} params.question - The student's question
 * @param {string} params.user_level - User level
 * @returns {Promise<Object>} Analysis response
 */
export async function analyzeQuestion({
  question,
  user_level = 'intermediate',
}) {
  const response = await fetch(`${NETRA_V4_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      question,
      user_level,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Quick generation with just a question
 * @param {string} question - The student's question
 * @returns {Promise<Object>} Visual response
 */
export async function generateSimple(question) {
  const response = await fetch(`${NETRA_V4_BASE}/generate-simple?question=${encodeURIComponent(question)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Check NETRA v4 service health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${NETRA_V4_BASE}/health`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Health check failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get quality metrics
 * @returns {Promise<Object>} Quality metrics
 */
export async function getMetrics() {
  const response = await fetch(`${NETRA_V4_BASE}/metrics`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Metrics fetch failed: HTTP ${response.status}`);
  }

  return response.json();
}

// Export all functions
export default {
  generateVisual,
  analyzeQuestion,
  generateSimple,
  checkHealth,
  getMetrics,
};

