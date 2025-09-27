import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import Dashboard from './components/Dashboard';
import AITutor from './components/AITutor';
import MockTests from './components/MockTests';
import Analytics from './components/Analytics';
import StressManagement from './components/StressManagement';
import AutoNoteMentor from './components/AutoNoteMentor';
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
          <div className="flex h-screen bg-gray-50">
            <Navigation />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/tutor" element={<AITutor />} />
                <Route path="/tests" element={<MockTests />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/wellness" element={<StressManagement />} />
                <Route path="/auto-notes" element={<AutoNoteMentor />} />
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