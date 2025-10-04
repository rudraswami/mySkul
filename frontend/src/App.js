import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import StudentDashboard from './components/StudentDashboard';
import AITutor from './components/AITutor';
import MockTests from './components/MockTests';
// Removed: Analytics and StressManagement components - not essential for core exam preparation
import AutoNoteMentor from './components/AutoNoteMentor';
import Subscription from './components/Subscription';
import Navigation from './components/Navigation';
import { Toaster } from './components/ui/toaster';

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
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
            <Navigation />
            <main className="flex-1 overflow-auto bg-gradient-to-br from-white/40 to-blue-50/60 backdrop-blur-sm">
              <Routes>
                <Route path="/dashboard" element={<StudentDashboard />} />
                <Route path="/tutor" element={<AITutor />} />
                <Route path="/tests" element={<MockTests />} />
                {/* Removed: Analytics and Wellness routes - not essential for core exam preparation */}
                <Route path="/auto-notes" element={<AutoNoteMentor />} />
                <Route path="/subscription" element={<Subscription />} />
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