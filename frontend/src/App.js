import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
          <AppContent />
          <Toaster />
        </div>
      </Router>
    </AuthProvider>
  );
}

function AppContent() {
  const { user, loading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading) {
    return <PageLoader message="Authenticating..." />;
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} 
      />
      <Route 
        path="/register" 
        element={!user ? <RegisterPage /> : <Navigate to="/dashboard" />} 
      />
      <Route 
        path="/" 
        element={!user ? <Navigate to="/login" /> : <Navigate to="/dashboard" />} 
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
                  className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
  );
}

export default App;