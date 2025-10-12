/**
 * Shared API client for Dhruv AI
 * Centralized configuration for all API calls with React Query
 */
import axios from 'axios';

// Get backend URL from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 */
export const apiClient = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 10000, // Reduce timeout during local debugging to surface hangs faster
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for hybrid auth
});

// CSRF token management
let csrfToken = null;

/**
 * Fetch and store CSRF token
 */
const fetchCsrfToken = async () => {
  try {
    const response = await apiClient.get('/auth/csrf-token');
    csrfToken = response.data.csrf_token;
    return csrfToken;
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error);
    return null;
  }
};

/**
 * Request interceptor - Add authentication token and CSRF token
 */
apiClient.interceptors.request.use(
  async (config) => {
    // Get JWT token from localStorage
    const token = localStorage.getItem('dhruv_ai_token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add CSRF token for state-changing requests
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method?.toUpperCase())) {
      // Fetch CSRF token if not available
      if (!csrfToken) {
        await fetchCsrfToken();
      }
      
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle CSRF token errors
    if (error.response?.status === 403 && error.response.data?.detail?.includes('CSRF')) {
      const originalRequest = error.config;

      if (!originalRequest) {
        return Promise.reject(error);
      }

      if (originalRequest._csrfRetry) {
        return Promise.reject(error);
      }

      console.warn('CSRF token expired, refreshing...');

      // Clear expired token and retry once per request
      originalRequest._csrfRetry = true;
      csrfToken = null;
      await fetchCsrfToken();

      if (csrfToken) {
        originalRequest.headers = {
          ...(originalRequest.headers || {}),
          'X-CSRF-Token': csrfToken,
        };

        return apiClient.request(originalRequest);
      }

      return Promise.reject(error);
    }
    
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Don't auto-logout here - let components handle it
      // This allows React Query to retry properly
      console.warn('Authentication error:', error.response.data);
    }
    
    // Handle subscription/payment errors
    if (error.response?.status === 402) {
      console.log('Subscription limit reached:', error.response.data);
      // Don't throw - let components handle subscription modals
    }
    
    return Promise.reject(error);
  }
);

/**
 * API methods organized by module
 */

// ==================== AUTHENTICATION ====================
export const authAPI = {
  login: (email, password) =>
    apiClient.post('/auth/login', { email, password }),
  
  register: (userData) =>
    apiClient.post('/auth/register', userData),
  
  logout: () =>
    apiClient.post('/auth/logout'),
  
  getCsrfToken: () =>
    apiClient.get('/auth/csrf-token'),
};

// ==================== USER ====================
export const userAPI = {
  getProfile: () =>
    apiClient.get('/user/profile'),
  
  updateProfile: (profileData) =>
    apiClient.put('/user/profile', profileData),
};

// ==================== SUBSCRIPTION ====================
export const subscriptionAPI = {
  getPlans: () =>
    apiClient.get('/subscription/plans'),
  
  getCurrentSubscription: () =>
    apiClient.get('/subscription/current'),
  
  getSubscriptionInfo: () =>
    apiClient.get('/subscription/info'),
  
  checkAccess: (featureName) =>
    apiClient.post('/subscription/check-access', { feature_name: featureName }),
  
  trackUsage: (featureName, amount = 1) =>
    apiClient.post('/subscription/track-usage', { feature_name: featureName, amount }),
  
  upgradeSubscription: (targetTier, billingCycle) =>
    apiClient.post(`/subscription/upgrade?target_tier=${targetTier}&billing_cycle=${billingCycle}`),
};

// ==================== AI TUTOR ====================
export const aiAPI = {
  getAvailableContexts: () =>
    apiClient.get('/ai/available-contexts'),
  
  getChatSessions: () =>
    apiClient.get('/chat/sessions'),
  
  sendMessage: (messageData) =>
    apiClient.post('/chat/message', messageData),
  
  createSession: (sessionData) =>
    apiClient.post('/chat/sessions', sessionData),
  
  // Guardrails
  validateMath: (expression) =>
    apiClient.post('/guardrails/validate-math', { expression }),
  
  verifyCitation: (subject, topic) =>
    apiClient.get(`/guardrails/citations/${subject}/${topic}`),
  
  verifyFact: (statement, subject) =>
    apiClient.post('/guardrails/fact-verification', { statement, subject }),
};

// ==================== ANALYTICS ====================
export const analyticsAPI = {
  getDashboard: () =>
    apiClient.get('/analytics/dashboard'),
  
  getDailyGoals: () =>
    apiClient.get('/analytics/daily-goals'),
  
  getSubjectProgress: () =>
    apiClient.get('/analytics/subject-progress'),
  
  getWellnessCheck: () =>
    apiClient.get('/analytics/wellness-check'),
};

// ==================== AUTO-NOTES ====================
export const autoNotesAPI = {
  startSession: (sessionData) =>
    apiClient.post('/auto-notes/start-session', sessionData),
  
  getSessions: () =>
    apiClient.get('/auto-notes/sessions'),
  
  getSession: (sessionId) =>
    apiClient.get(`/auto-notes/${sessionId}`),
  
  getAnalytics: () =>
    apiClient.get('/auto-notes/analytics'),
  
  getClassSeries: () =>
    apiClient.get('/auto-notes/class-series'),
};

// ==================== MOCK TESTS ====================
export const mockTestsAPI = {
  getLibrary: () =>
    apiClient.get('/mock-tests/library'),
  
  getRecentTests: () =>
    apiClient.get('/mock-tests/library/recent'),
  
  getDashboard: () =>
    apiClient.get('/mock-tests/dashboard'),
  
  getPerformanceTrends: () =>
    apiClient.get('/mock-tests/performance-trends'),
  
  getSubjects: (examType) =>
    apiClient.get(`/mock-tests/subjects?exam_type=${examType}`),
  
  getDetailedReview: (testId) =>
    apiClient.get(`/mock-tests/${testId}/detailed-review`),
  
  getResumeTests: () =>
    apiClient.get('/mock-tests/resume'),
};

export default apiClient;
