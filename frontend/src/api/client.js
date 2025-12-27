/**
 * Shared API client for DRON AI
 * Centralized configuration for all API calls with React Query
 */
import axios from 'axios';

// Get backend URL from environment - required for production
// Prefer env; fallback to common local dev URL to avoid blank UI
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
if (!process.env.REACT_APP_BACKEND_URL) {
  // Non-fatal warning to help local dev
  // eslint-disable-next-line no-console
  console.warn('REACT_APP_BACKEND_URL not set. Falling back to http://localhost:8001');
}

/**
 * Create axios instance with default configuration
 */
export const apiClient = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for hybrid auth
});

// CSRF token management - Double-Submit Cookie pattern
let csrfToken = null;
let csrfFetchPromise = null; // Prevent parallel fetches

/**
 * Get CSRF token from cookie (Double-Submit pattern)
 */
const getCsrfFromCookie = () => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrf_token') {
      return decodeURIComponent(value);
    }
  }
  return null;
};

/**
 * Fetch and store CSRF token
 * Uses cookie value if available, otherwise fetches from endpoint
 */
const fetchCsrfToken = async () => {
  // Check cookie first (most reliable for Double-Submit pattern)
  const cookieToken = getCsrfFromCookie();
  if (cookieToken) {
    csrfToken = cookieToken;
    return csrfToken;
  }
  
  // Prevent parallel fetch requests
  if (csrfFetchPromise) {
    return csrfFetchPromise;
  }
  
  csrfFetchPromise = (async () => {
    try {
      const response = await apiClient.get('/auth/csrf-token');
      // Token is set via cookie by server; also available in response
      csrfToken = response?.data?.csrf_token || response?.headers?.['x-csrf-token'] || getCsrfFromCookie();
      return csrfToken;
    } catch (error) {
      console.warn('Failed to fetch CSRF token:', error);
      return null;
    } finally {
      csrfFetchPromise = null;
    }
  })();
  
  return csrfFetchPromise;
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
    
    // Add CSRF token for state-changing requests (Double-Submit Cookie pattern)
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method?.toUpperCase())) {
      // Try to get token from cookie first
      let tokenToUse = getCsrfFromCookie() || csrfToken;
      
      // Fetch CSRF token if not available
      if (!tokenToUse) {
        tokenToUse = await fetchCsrfToken();
      }
      
      if (tokenToUse) {
        config.headers['X-CSRF-Token'] = tokenToUse;
        csrfToken = tokenToUse; // Cache for future requests
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle errors globally with retry logic
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle CSRF token errors - Single retry with fresh token
    if (error.response?.status === 403 && 
        (error.response.data?.detail?.includes('CSRF') || error.response.data?.detail?.includes('csrf'))) {
      // Prevent infinite retry loops
      if (!originalRequest._csrfRetry) {
        console.warn('CSRF token expired/missing, refreshing...');
        originalRequest._csrfRetry = true;
        
        // Clear cached token and fetch fresh one
        csrfToken = null;
        await fetchCsrfToken();
        
        // Retry the original request with fresh token
        const freshToken = getCsrfFromCookie() || csrfToken;
        if (freshToken) {
          originalRequest.headers['X-CSRF-Token'] = freshToken;
          return apiClient.request(originalRequest);
        }
      }
    }
    
    // Handle 500 errors with user-friendly messages
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
      
      // Add user-friendly error message
      error.userMessage = 'Something went wrong on our end. Our team has been notified. Please try again in a moment.';
      
      // Retry once for 500 errors if not already retried
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        // Wait 1 second before retry
        await new Promise(resolve => setTimeout(resolve, 1000));
        return apiClient.request(originalRequest);
      }
    }
    
    // Handle authentication errors (token expired)
    if (error.response?.status === 401) {
      const errorDetail = error.response.data?.detail || '';
      const requestUrl = error.config?.url || '';
      
      // Don't clear/redirect for auth validation endpoints - let AuthContext handle those
      const isAuthValidation = requestUrl.includes('/user/profile') || 
                               requestUrl.includes('/auth/session');
      
      if (!isAuthValidation) {
        console.warn('🔒 401 Unauthorized on protected API call');
        
        // Clear auth data on 401 from non-auth-validation endpoints
        // This handles mid-session token expiry
        localStorage.removeItem('dhruv_ai_token');
        localStorage.removeItem('dhruv_ai_user');
        
        // Redirect to login for non-auth-validation 401s
        // This handles cases where user's session expires while using the app
        if (typeof window !== 'undefined' && 
            !window.location.pathname.includes('/login') && 
            !window.location.pathname.includes('/auth/callback') &&
            window.location.pathname !== '/') {
          console.log('🔄 Session expired, redirecting to login');
          window.location.href = '/login';
        }
      }
      
      // Check if token is expired for user message
      if (errorDetail.includes('expired') || errorDetail.includes('invalid')) {
        error.userMessage = 'Your session has expired. Please log in again.';
      } else {
        error.userMessage = 'Authentication required. Please log in.';
      }
    }
    
    // Handle subscription/payment errors
    if (error.response?.status === 402) {
      console.log('Subscription limit reached:', error.response.data);
      error.userMessage = 'Please upgrade your plan to continue using this feature.';
      // Don't throw - let components handle subscription modals
    }
    
    // Handle rate limiting
    if (error.response?.status === 429) {
      console.warn('Rate limit exceeded');
      error.userMessage = 'Too many requests. Please slow down and try again in a moment.';
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
    apiClient.get('/ai/chat/sessions'),
  
  sendMessage: (messageData) => {
    // Prefer session-scoped message route if session_id provided
    if (messageData?.session_id) {
      return apiClient.post(`/ai/chat/${messageData.session_id}/messages`, messageData);
    }
    // Fallback to dual-response generator when no session context
    return apiClient.post('/ai/dual-response', messageData);
  },
  
  createSession: (sessionData) =>
    apiClient.post('/ai/chat/sessions', sessionData),
  
  // Guardrails
  validateMath: (expression) =>
    apiClient.post('/ai/guardrails/validate-math', { expression }),
  
  verifyCitation: (subject, topic) =>
    apiClient.get(`/ai/guardrails/citations/${subject}/${topic}`),
  
  verifyFact: (statement, subject) =>
    apiClient.post('/ai/guardrails/fact-verification', { statement, subject }),
  
  // Visual Engine - Magic Notebook (Phase 6)
  breakConcept: (question, context) =>
    apiClient.post('/ai/visual-engine/concept-break', { question, context, model: 'gpt-4o-mini' }),
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

// ==================== STUDY PLANNER ====================
export const studyPlannerAPI = {
  getTodayPlan: () =>
    apiClient.get('/study-planner/today'),
  
  generatePlan: (date, availableHours) =>
    apiClient.post('/study-planner/generate', { date, available_hours: availableHours }),
  
  updateProgress: (blockIndex, completed, actualDuration) =>
    apiClient.post('/study-planner/progress', { 
      block_index: blockIndex, 
      completed, 
      actual_duration_minutes: actualDuration 
    }),
  
  getHistory: (days = 7) =>
    apiClient.get(`/study-planner/history?days=${days}`),
  
  updatePreferences: (dailyHours, energyPattern) =>
    apiClient.post('/study-planner/preferences', {
      daily_study_hours: dailyHours,
      energy_pattern: energyPattern
    }),
};

export default apiClient;
