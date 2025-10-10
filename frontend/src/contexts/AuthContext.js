import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// SECURITY: Remove console logging for production
// console.log('AuthContext - Backend URL:', BACKEND_URL);
// console.log('AuthContext - API URL:', API);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('dhruv_ai_token'));

  // Configure axios for both cookie-based AND Bearer token authentication
  useEffect(() => {
    // Send cookies with all requests (for secure httpOnly cookie auth)
    axios.defaults.withCredentials = true;
    
    // Also set Authorization header for Bearer token fallback
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is logged in on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/user/profile`);
          setUser(response.data);
          // SECURITY: Remove sensitive auth data logging
          // console.log('Auth check successful:', response.data.email);
        } catch (error) {
          // SECURITY: Only log errors in development
          if (process.env.NODE_ENV === 'development') {
            console.error('Auth check failed:', error.response?.status);
          }
          
          // Only logout for actual auth errors (401, 403), not network errors
          if (error.response?.status === 401 || error.response?.status === 403) {
            // User session invalid - clear user state and token
            logout();
          }
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      // SECURITY: Remove sensitive login data from logs
      const response = await axios.post(`${API}/auth/login`, { email, password });
      
      const { token: newToken, user: userData } = response.data;
      
      // Set both token (for Bearer auth fallback) and user state
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('dhruv_ai_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      // SECURITY: httpOnly cookie is also set automatically by backend
      return { success: true };
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
      const response = await axios.post(`${API}/auth/register`, userData);
      const { token: newToken, user: newUser } = response.data;
      
      // Set both token (for Bearer auth fallback) and user state
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('dhruv_ai_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
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
      // Call logout endpoint to clear cookie
      await axios.post(`${API}/auth/logout`);
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
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const updateUser = (updatedUserData) => {
    setUser(updatedUserData);
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateUser,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}