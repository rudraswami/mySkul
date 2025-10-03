import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Brain } from 'lucide-react';
import axios from 'axios';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    console.log('Form submitted!', { email, password: password ? 'present' : 'missing' });
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    setLoading(true);
    setError('');

    console.log('Calling login function...');
    const result = await login(email, password);
    console.log('Login result:', result);
    
    if (result.success) {
      console.log('Login successful, navigating to dashboard...');
      navigate('/dashboard');
    } else {
      console.log('Login failed:', result.error);
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-blue-600 to-indigo-700 items-center justify-center p-12">
        <div className="max-w-md text-white">
          <div className="flex items-center mb-8">
            <Brain className="h-12 w-12 mr-4" />
            <h1 className="text-4xl font-bold">Dhruv AI</h1>
          </div>
          
          <p className="text-xl mb-4 text-blue-100 font-medium">
            The trusted, hallucination-free AI mentor that turns every class into verified notes, flashcards and personalised prep — at a fraction of coaching fees.
          </p>

          <div className="space-y-6 mt-8">
            <div className="flex items-start">
              <div className="h-6 w-6 mr-3 mt-0.5 bg-green-400 rounded-full flex items-center justify-center">
                <span className="text-green-900 text-xs font-bold">✓</span>
              </div>
              <div>
                <span className="text-white font-semibold">Trust</span>
                <p className="text-blue-100 text-sm">Verified, hallucination-free, accurate AI mentoring</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="h-6 w-6 mr-3 mt-0.5 bg-purple-400 rounded-full flex items-center justify-center">
                <span className="text-purple-900 text-xs font-bold">♥</span>
              </div>
              <div>
                <span className="text-white font-semibold">Personalisation</span>
                <p className="text-blue-100 text-sm">Adaptive, empathetic, one-to-one learning experience</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="h-6 w-6 mr-3 mt-0.5 bg-yellow-400 rounded-full flex items-center justify-center">
                <span className="text-yellow-900 text-xs font-bold">⚡</span>
              </div>
              <div>
                <span className="text-white font-semibold">Empowerment</span>
                <p className="text-blue-100 text-sm">Accessible, affordable success for independent learners</p>
              </div>
            </div>
          </div>

          <div className="mt-12 p-4 bg-blue-500/30 rounded-lg border border-blue-400/30">
            <p className="text-sm text-blue-100">
              "Dhruv AI's verified notes and hallucination-free AI helped me crack JEE at 10% of coaching center costs. The personalized approach made all the difference!"
            </p>
            <p className="text-xs mt-2 font-medium text-blue-200">- Priya S., IIT Delhi (2024)</p>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="bg-white shadow-xl rounded-lg p-8 border-0">
            <div className="text-center pb-8">
              <div className="flex justify-center mb-4 lg:hidden">
                <Brain className="h-10 w-10 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                Welcome Back
              </h2>
              <p className="text-gray-600 mt-2">
                Sign in to continue your learning journey
              </p>
            </div>

            <div>
              {error && (
                <div className="mb-6 p-4 border border-red-200 bg-red-50 rounded-md">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <div className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your email"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your password"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => {
                    console.log('BUTTON CLICKED!');
                    handleSubmit();
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
                      Signing In...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
                
                <button
                  type="button"
                  onClick={() => console.log('TEST BUTTON CLICKED')}
                  className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-md mt-2"
                >
                  Test Button
                </button>
              </div>

              <div className="mt-6 text-center">
                <p className="text-gray-600">
                  Don't have an account?{' '}
                  <Link 
                    to="/register" 
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Create Account
                  </Link>
                </p>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-3">Trusted by 50,000+ students across India</p>
                  <div className="flex justify-center items-center space-x-4 text-xs text-gray-600 mb-3">
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-green-500 rounded-full mr-1"></div>
                      <span>Hallucination-Free AI</span>
                    </div>
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
                      <span>Verified Content</span>
                    </div>
                  </div>
                  <div className="flex justify-center space-x-8 text-xs text-gray-400">
                    <span>JEE • NEET • UPSC</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}