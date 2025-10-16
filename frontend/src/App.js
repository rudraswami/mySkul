import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools'; // Temporarily disabled
import './App.css';

// Eagerly loaded components (critical path)
import LandingPage from './components/LandingPage';
import LoginScreen from './components/auth/LoginScreen';
import OAuthCallback from './components/auth/OAuthCallback';
import ProfileSetup from './components/auth/ProfileSetup';
import Navigation from './components/Navigation';
import { Toaster } from './components/ui/toaster';
import { PageLoader } from './components/ui/loading';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';
import { SkipToContent } from './utils/accessibility';

// Lazy loaded components (code splitting for better initial load)
const StudentDashboard = lazy(() => import('./components/StudentDashboard'));
const AITutor = lazy(() => import('./components/AITutor')); // Large component - lazy load
const MockTests = lazy(() => import('./components/MockTests'));
const AutoNoteMentor = lazy(() => import('./components/AutoNoteMentor'));
const Subscription = lazy(() => import('./components/Subscription'));
const ProfileSettings = lazy(() => import('./components/ProfileSettings'));

// Policy pages (lazy loaded)
const PrivacyPolicy = lazy(() => import('./pages/policies/PrivacyPolicy'));
const TermsAndConditions = lazy(() => import('./pages/policies/TermsAndConditions'));
const RefundPolicy = lazy(() => import('./pages/policies/RefundPolicy'));
const ShippingPolicy = lazy(() => import('./pages/policies/ShippingPolicy'));
const ContactUs = lazy(() => import('./pages/policies/ContactUs'));

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SubscriptionProvider, useSubscription } from './contexts/SubscriptionContext';
import { ThemeProvider } from './contexts/ThemeContext';
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
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <Router>
              <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
                <AppContent />
                <Toaster />
              </div>
            </Router>
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
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
      <SkipToContent />
      <Routes>
        {/* Landing Page - Public Home Route */}
        <Route 
          path="/" 
          element={<LandingPage />} 
        />
        
        {/* New Gmail-Only Auth Routes */}
        <Route 
          path="/login" 
          element={
            <PublicRoute>
              <LoginScreen />
            </PublicRoute>
          } 
        />
        
        {/* OAuth Callback Route - PUBLIC (must be accessible without auth) */}
        <Route 
          path="/auth/callback" 
          element={<OAuthCallback />} 
        />
        
        {/* Profile Setup - Required after first Gmail login */}
        <Route 
          path="/profile-setup" 
          element={
            user ? (
              !user.profile_completed ? <ProfileSetup /> : <Navigate to="/dashboard" />
            ) : (
              <Navigate to="/login" />
            )
          } 
        />
        
        {/* Legacy routes - redirect to new login */}
        <Route 
          path="/register" 
          element={<Navigate to="/login" replace />} 
        />
        <Route 
          path="/signin" 
          element={<Navigate to="/login" replace />} 
        />
        <Route 
          path="/signup" 
          element={<Navigate to="/login" replace />} 
        />
        
        {/* Policy Pages - Public Routes */}
        <Route path="/policies/privacy" element={
          <Suspense fallback={<PageLoader message="Loading Privacy Policy..." />}>
            <PrivacyPolicy />
          </Suspense>
        } />
        <Route path="/policies/terms" element={
          <Suspense fallback={<PageLoader message="Loading Terms..." />}>
            <TermsAndConditions />
          </Suspense>
        } />
        <Route path="/policies/refund" element={
          <Suspense fallback={<PageLoader message="Loading Refund Policy..." />}>
            <RefundPolicy />
          </Suspense>
        } />
        <Route path="/policies/shipping" element={
          <Suspense fallback={<PageLoader message="Loading Shipping Policy..." />}>
            <ShippingPolicy />
          </Suspense>
        } />
        <Route path="/policies/contact" element={
          <Suspense fallback={<PageLoader message="Loading Contact Page..." />}>
            <ContactUs />
          </Suspense>
        } />
        <Route path="/contact" element={<Navigate to="/policies/contact" replace />} />
        
        {/* Protected Routes - All require authentication */}
        <Route path="/*" element={
          <ProtectedRoute>
            <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
              <Navigation 
                mobileMenuOpen={mobileMenuOpen} 
                setMobileMenuOpen={setMobileMenuOpen} 
              />
              <main id="main-content" className="flex-1 overflow-auto bg-gradient-to-br from-white/40 to-blue-50/60 backdrop-blur-sm lg:ml-0 dark:from-gray-900/40 dark:to-gray-800/60">
                {/* Mobile Header with Hamburger */}
                <div className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
                  <button
                    onClick={() => setMobileMenuOpen(true)}
                    className="hamburger-menu min-h-12 min-w-12 p-3 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center justify-center mobile-transition"
                    aria-label="Open navigation menu"
                    aria-controls="mobile-menu"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </button>
                  <div className="flex items-center">
                    <svg className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <h1 className="text-lg font-bold text-gray-900 dark:text-white">Dhruv AI</h1>
                  </div>
                  <div className="w-10" /> {/* Spacer for centering */}
                </div>
                
                <Routes>
                  <Route path="/dashboard" element={
                    <Suspense fallback={<PageLoader message="Loading dashboard..." />}>
                      <StudentDashboard />
                    </Suspense>
                  } />
                  <Route path="/tutor" element={
                    <Suspense fallback={<PageLoader message="Loading AI Tutor..." />}>
                      <AITutor />
                    </Suspense>
                  } />
                  <Route path="/tests" element={
                    <Suspense fallback={<PageLoader message="Loading Mock Tests..." />}>
                      <MockTests />
                    </Suspense>
                  } />
                  {/* Removed: Analytics and Wellness routes - not essential for core exam preparation */}
                  <Route path="/auto-notes" element={
                    <Suspense fallback={<PageLoader message="Loading Auto Notes..." />}>
                      <AutoNoteMentor />
                    </Suspense>
                  } />
                  <Route path="/subscription" element={
                    <Suspense fallback={<PageLoader message="Loading Subscription..." />}>
                      <Subscription />
                    </Suspense>
                  } />
                  <Route path="/profile" element={
                    <Suspense fallback={<PageLoader message="Loading Profile..." />}>
                      <ProfileSettings />
                    </Suspense>
                  } />
                  <Route path="*" element={<Navigate to="/dashboard" />} />
                </Routes>
              </main>
            </div>
          </ProtectedRoute>
        } />
      </Routes>
      
      {/* Global Upsell Modal removed - each component now manages its own UpgradeModal for better context */}
    </>
  );
}

export default App;