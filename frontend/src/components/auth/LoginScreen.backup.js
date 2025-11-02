import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Brain, LogIn, Mail, Lock, User, Calendar } from 'lucide-react';
import PremiumShowcase from './PremiumShowcase';
import '../../styles/auth.css';

export default function LoginScreen() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authMode, setAuthMode] = useState('google'); // 'google' or 'email'
  const [showSignup, setShowSignup] = useState(false);
  
  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Signup form state
  const [signupData, setSignupData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    exam_type: 'JEE',
    target_year: new Date().getFullYear() + 1,
    grade: ''
  });

  const handleGoogleLogin = () => {
    setLoading(true);
    setError('');
    
    // Direct Google OAuth through our backend
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    if (!backendUrl) {
      setError('Backend URL not configured');
      setLoading(false);
      return;
    }
    window.location.href = `${backendUrl}/api/auth/google/login`;
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store token in localStorage
      localStorage.setItem('dhruv_ai_token', data.token);
      localStorage.setItem('dhruv_ai_user', JSON.stringify(data.user));

      // Navigate based on profile completion
      if (data.user.profile_completed === false) {
        navigate('/profile-setup');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (signupData.password !== signupData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (signupData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          full_name: signupData.full_name,
          email: signupData.email,
          password: signupData.password,
          exam_type: signupData.exam_type,
          target_year: parseInt(signupData.target_year),
          grade: signupData.grade || null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Store token and user data
      localStorage.setItem('dhruv_ai_token', data.token);
      localStorage.setItem('dhruv_ai_user', JSON.stringify(data.user));

      // Navigate to profile setup or dashboard
      navigate('/profile-setup');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Premium Showcase */}
      <PremiumShowcase />

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Logo & Branding */}
          <div className="text-center mb-8 fade-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 mb-4 pulse-glow">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Sign in to Dhruv AI
            </h2>
            <p className="text-gray-600">
              Start your intelligent learning journey
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm fade-in">
              {error}
            </div>
          )}

          {/* Auth Mode Toggle */}
          {!showSignup && (
            <div className="flex mb-6 bg-white p-1 rounded-xl shadow-sm">
              <button
                onClick={() => setAuthMode('google')}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                  authMode === 'google'
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Google Sign In
              </button>
              <button
                onClick={() => setAuthMode('email')}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                  authMode === 'email'
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }
              <LogIn className="h-4 w-4" />
              <span>Secure authentication powered by Google</span>
            </div>
          </div>

          {/* Benefits */}
          <div className="mt-8 space-y-3 fade-in-delay-3">
            <div className="flex items-center space-x-3 text-sm text-gray-600">
              <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="w-3 h-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>No password required - just your Gmail</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-gray-600">
              <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="w-3 h-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>Instant access to AI mentor & mock tests</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-gray-600">
              <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="w-3 h-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>Personalized learning experience</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
