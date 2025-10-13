import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools'; // Temporarily disabled
import './App.css';

// Components
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import StudentDashboard from './components/StudentDashboard';
import AITutor from './components/AITutor';
import MockTests from './components/MockTests';
// Removed: Analytics and StressManagement components - not essential for core exam preparation
import AutoNoteMentor from './components/AutoNoteMentor';
import Subscription from './components/Subscription';
import ProfileSettings from './components/ProfileSettings';
import Navigation from './components/Navigation';
import { Toaster } from './components/ui/toaster';
import { PageLoader } from './components/ui/loading';

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SubscriptionProvider, useSubscription } from './contexts/SubscriptionContext';
// UpsellModal removed - duplicate of UpgradeModal (now using unified UpgradeModal in components)

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Create React Query client with optimized config for low-connectivity students
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2, // Retry failed requests twice
      staleTime: 3 * 60 * 1000, // 3 minutes - data considered fresh
      cacheTime: 10 * 60 * 1000, // 10 minutes - keep in cache
      refetchOnWindowFocus: true, // Refetch when user returns to tab
      refetchOnReconnect: true, // Refetch when network reconnects
      refetchOnMount: false, // Don't refetch on component mount if data is fresh
    },
    mutations: {
      retry: 1, // Retry mutations once on failure
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <SubscriptionProvider>
          <Router>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
              <AppContent />
              <Toaster />
            </div>
          </Router>
        </SubscriptionProvider>
      </AuthProvider>
      {/* React Query DevTools - temporarily disabled due to compatibility issues */}
      {/* {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />} */}
    </QueryClientProvider>
  );
}

function AppContent() {
  const { user, loading } = useAuth();
  const { upsellModal, setUpsellModal } = useSubscription();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading) {
    return <PageLoader message="Authenticating..." />;
  }

  return (
    <>
      <Routes>
        {/* Landing Page - Public Home Route */}
        <Route 
          path="/" 
          element={<LandingPage />} 
        />
        <Route 
          path="/login" 
          element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/register" 
          element={!user ? <RegisterPage /> : <Navigate to="/dashboard" />} 
        />
        
        {/* Protected Routes */}
        <Route path="/*" element={
          user ? (
            <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
              <Navigation 
                mobileMenuOpen={mobileMenuOpen} 
                setMobileMenuOpen={setMobileMenuOpen} 
              />
              <main className="flex-1 overflow-auto bg-gradient-to-br from-white/40 to-blue-50/60 backdrop-blur-sm lg:ml-0">
                {/* Mobile Header with Hamburger */}
                <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
                  <button
                    onClick={() => setMobileMenuOpen(true)}
                    className="hamburger-menu min-h-12 min-w-12 p-3 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center justify-center mobile-transition"
                    aria-label="Open navigation menu"
                    aria-controls="mobile-menu"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </button>
                  <div className="flex items-center">
                    <svg className="h-8 w-8 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <h1 className="text-lg font-bold text-gray-900">Dhruv AI</h1>
                  </div>
                  <div className="w-10" /> {/* Spacer for centering */}
                </div>
                
                <Routes>
                  <Route path="/dashboard" element={<StudentDashboard />} />
                  <Route path="/tutor" element={<AITutor />} />
                  <Route path="/tests" element={<MockTests />} />
                  {/* Removed: Analytics and Wellness routes - not essential for core exam preparation */}
                  <Route path="/auto-notes" element={<AutoNoteMentor />} />
                  <Route path="/subscription" element={<Subscription />} />
                  <Route path="/profile" element={<ProfileSettings />} />
                  <Route path="*" element={<Navigate to="/dashboard" />} />
                </Routes>
              </main>
            </div>
          ) : (
            <Navigate to="/login" />
          )
        } />
      </Routes>
      
      {/* Global Upsell Modal removed - each component now manages its own UpgradeModal for better context */}
    </>
  );
}

export default App;