/**
 * useChatSession Hook
 * Manages chat session state and operations
 */
import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export function useChatSession(userId) {
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all sessions for the user
  const fetchSessions = useCallback(async () => {
    if (!userId) return;
    
    try {
      setLoading(true);
      const response = await apiClient.get(`/tutor/sessions`);
      setSessions(response.data.sessions || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Create a new session
  const createSession = useCallback(async (subject, examType = 'JEE') => {
    try {
      setLoading(true);
      const response = await apiClient.post('/tutor/sessions', {
        subject,
        exam_type: examType
      });
      const newSession = response.data.session;
      setCurrentSession(newSession);
      setSessions(prev => [newSession, ...prev]);
      setError(null);
      return newSession;
    } catch (err) {
      console.error('Failed to create session:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Switch to an existing session
  const switchSession = useCallback((session) => {
    setCurrentSession(session);
  }, []);

  // Delete a session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      await apiClient.delete(`/tutor/sessions/${sessionId}`);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to delete session:', err);
      setError(err.message);
      throw err;
    }
  }, [currentSession]);

  // Load sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    currentSession,
    sessions,
    loading,
    error,
    createSession,
    switchSession,
    deleteSession,
    refreshSessions: fetchSessions
  };
}

export default useChatSession;
