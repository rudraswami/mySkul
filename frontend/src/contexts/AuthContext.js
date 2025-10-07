import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

console.log('AuthContext - Backend URL:', BACKEND_URL);
console.log('AuthContext - API URL:', API);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('dhruv_ai_token'));

  // Set up axios interceptor for authentication
  useEffect(() => {
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
          console.log('Auth check successful:', response.data.email);
        } catch (error) {
          console.error('Auth check failed:', error);
          console.error('Error status:', error.response?.status);
          console.error('Error message:', error.response?.data?.detail || error.message);
          
          // Only logout for actual auth errors (401, 403), not network errors
          if (error.response?.status === 401 || error.response?.status === 403) {
            console.log('Authentication failed - logging out');
            logout();
          } else {
            console.log('Network error - keeping user logged in');
            // For network errors, we'll keep the user logged in but log the error
          }
        }
      }
      setLoading(false);
    };

    // Prevent race conditions by checking if we already have a token
    if (!loading) {
      checkAuth();
    }
  }, [token, loading]);

  const login = async (email, password) => {
    try {
      console.log('Attempting login with:', { email, API });
      const response = await axios.post(`${API}/auth/login`, { email, password });
      console.log('Login response:', response.data);
      
      const { token: newToken, user: userData } = response.data;
      
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('dhruv_ai_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      console.log('Login successful, token stored:', newToken?.substring(0, 20) + '...');
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
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
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('dhruv_ai_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('dhruv_ai_token');
    delete axios.defaults.headers.common['Authorization'];
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
    loading,
    token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}