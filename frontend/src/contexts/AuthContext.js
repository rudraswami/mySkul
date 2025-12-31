import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient, authAPI } from '../api/client';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// SECURITY: Remove console logging for production
// console.log('AuthContext - Backend URL:', BACKEND_URL);
// console.log('AuthContext - API URL:', API);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    // Initialize user from localStorage if available
    const storedUser = localStorage.getItem('dhruv_ai_user');
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('dhruv_ai_token'));

  // Configure apiClient for authentication
  useEffect(() => {
    // apiClient already handles withCredentials and CSRF tokens
    // Just need to ensure token is available for the interceptor
    if (token) {
      localStorage.setItem('dhruv_ai_token', token);
    } else {
      localStorage.removeItem('dhruv_ai_token');
    }
  }, [token]);

  // Check if user is logged in on app load
  useEffect(() => {
    const checkAuth = async () => {
      // CRITICAL: Check if session_token is in URL (OAuth redirect)
      const params = new URLSearchParams(window.location.search);
      const sessionToken = params.get('session_token');
      
      if (sessionToken) {
        console.log('🍪 OAuth redirect detected - setting session token');
        
        // CRITICAL FIX: Store token in localStorage for reliable access
        // This ensures subsequent API calls can include the token even if cookies fail
        localStorage.setItem('dhruv_ai_token', sessionToken);
        setToken(sessionToken);
        
        // Also try to set session cookie (may work in same-domain scenarios)
        const domain = window.location.hostname.includes('emergent.host') 
          ? '.emergent.host' 
          : window.location.hostname;
        
        try {
          const cookieString = `dhruv_ai_session=${sessionToken}; path=/; domain=${domain}; secure; samesite=none; max-age=604800`;
          document.cookie = cookieString;
          console.log('✅ Session cookie set via document.cookie');
        } catch (e) {
          console.warn('⚠️ Cookie setting failed (cross-domain), using localStorage only:', e);
        }
        
        console.log('✅ Session token stored in localStorage');
        
        // Clean URL by removing session_token parameter
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      
      // Get current token from localStorage (may have been set by OAuth redirect above)
      const currentToken = localStorage.getItem('dhruv_ai_token');
      
      let sessionValidated = false;
      
      // PERFORMANCE FIX: Parallel auth checks (3-5s → 1-2s)
      const headers = {
        'Content-Type': 'application/json',
      };
      
      if (currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
      }
      
      // Run session check and JWT validation in parallel
      const [sessionResult, jwtResult] = await Promise.allSettled([
        fetch(`${BACKEND_URL}/api/auth/session`, {
          credentials: 'include',
          headers,
        }),
        currentToken ? apiClient.get('/user/profile') : Promise.reject(new Error('No token'))
      ]);
      
      // Use session check if successful
      if (sessionResult.status === 'fulfilled' && sessionResult.value.ok) {
        try {
          const data = await sessionResult.value.json();
          setUser(data.user);
          localStorage.setItem('dhruv_ai_user', JSON.stringify(data.user));
          console.log('✅ Session validated, user loaded:', data.user.email);
          sessionValidated = true;
        } catch (error) {
          console.warn('Failed to parse session response:', error);
        }
      }
      
      // If session failed, try JWT result
      if (!sessionValidated && jwtResult.status === 'fulfilled') {
        setUser(jwtResult.value.data);
        localStorage.setItem('dhruv_ai_user', JSON.stringify(jwtResult.value.data));
        console.log('✅ JWT validated, user loaded:', jwtResult.value.data.email);
        sessionValidated = true;
      }
      
      // If both failed with auth errors, clear everything
      if (!sessionValidated && jwtResult.status === 'rejected') {
        const error = jwtResult.reason;
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          console.log('⚠️ Auth invalid (401/403), clearing auth data');
          setUser(null);
          localStorage.removeItem('dhruv_ai_user');
          localStorage.removeItem('dhruv_ai_token');
        } else if (currentToken) {
          // Other error (network, 500, etc.) - keep existing user data
          console.warn('Auth validation failed with non-auth error, keeping cached user');
        }
      }
      
      // If no session validated AND no token exists, user is not logged in
      if (!sessionValidated && !currentToken) {
        console.log('ℹ️ No active session and no token found');
        // Only clear if there's stale user data without any token
        const storedUser = localStorage.getItem('dhruv_ai_user');
        if (storedUser) {
          console.log('🧹 Clearing orphaned user data (no token)');
          setUser(null);
          localStorage.removeItem('dhruv_ai_user');
        }
      }
      
      setLoading(false);
    };

    checkAuth();
  }, []); // Only run on mount, not when token changes

  const loginWithGoogle = async (sessionData) => {
    try {
      // Send Google session data to our backend
      const response = await fetch(`${BACKEND_URL}/api/auth/google/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(sessionData)
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        
        // Store temporary user info for ProfileSetup screen
        sessionStorage.setItem('temp_user_info', JSON.stringify({
          name: sessionData.name,
          email: sessionData.email,
          photo_url: sessionData.picture
        }));
        
        return { 
          success: true, 
          user: data.user,
          needsProfileSetup: !data.user.profile_completed 
        };
      } else {
        const error = await response.json();
        return { 
          success: false, 
          error: error.detail || 'Google login failed' 
        };
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Google login error:', error);
      }
      return { 
        success: false, 
        error: error.message || 'Google login failed' 
      };
    }
  };

  const login = async (email, password) => {
    try {
      // Use authAPI with CSRF token handling
      const response = await authAPI.login(email, password);
      
      const { token: newToken, user: userData } = response.data;
      
      // Store in localStorage FIRST before setting state
      localStorage.setItem('dhruv_ai_token', newToken);
      localStorage.setItem('dhruv_ai_user', JSON.stringify(userData));
      
      // Then set React state
      setToken(newToken);
      setUser(userData);
      
      // SECURITY: httpOnly cookie is also set automatically by backend
      return { success: true, user: userData };
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Login error:', error.response?.status);
      }
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { token: newToken, user: newUser } = response.data;
      
      // Set both token (for Bearer auth fallback) and user state
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('dhruv_ai_token', newToken);
      localStorage.setItem('dhruv_ai_user', JSON.stringify(newUser));
      
      return { success: true, user: newUser };
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Registration error:', error.response?.status);
      }
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      // Call logout endpoint to clear cookie using authAPI
      await authAPI.logout();
    } catch (error) {
      // Logout should proceed even if API call fails
      if (process.env.NODE_ENV === 'development') {
        console.error('Logout API error:', error.response?.status);
      }
    } finally {
      // Clear both token and user state
      setUser(null);
      setToken(null);
      localStorage.removeItem('dhruv_ai_token');
      localStorage.removeItem('dhruv_ai_user'); // FIX: Clear persisted user data
    }
  };

  const updateUser = (updatedUserData) => {
    setUser(updatedUserData);
  };

  const value = {
    user,
    login,
    register,
    loginWithGoogle,
    logout,
    updateUser,
    loading,
    token  // Added back for compatibility
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}