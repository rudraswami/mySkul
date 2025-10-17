/**
 * useAITutorSession Hook
 * 
 * Manages AI Tutor chat sessions - creating, loading, switching, and deleting sessions
 * 
 * @returns {Object} Session state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import client from '../api/client';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

export const useAITutorSession = () => {
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch all chat sessions for the current user
   */
  const fetchSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        setSessions([]);
        return;
      }

      const response = await client.get('/chat/sessions');
      setSessions(response.data.sessions || []);
    } catch (err) {
      console.error('Failed to fetch chat sessions:', err);
      setError(err.message || 'Failed to load sessions');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Create a new chat session
   * 
   * @param {string} firstMessage - The initial message from user
   * @param {string} detectedTopic - Auto-detected topic from AI
   * @param {string} aiMode - AI mode (dual, mentor, professor)
   * @param {string} subject - Selected subject
   * @returns {string|null} - New session ID or null if failed
   */
  const createSession = useCallback(async (firstMessage, detectedTopic, aiMode = 'dual', subject = 'General') => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      // Determine the subject from detected topic or use provided subject
      const topicSubject = detectedTopic && detectedTopic !== 'General' ? detectedTopic : subject;
      
      // Create meaningful session title based on topic and message content
      let sessionTitle;
      if (detectedTopic && detectedTopic !== 'General') {
        const messageExcerpt = firstMessage.substring(0, 30).trim();
        sessionTitle = `${detectedTopic}: ${messageExcerpt}${messageExcerpt.length < 30 ? '' : '...'}`;
      } else {
        sessionTitle = firstMessage.substring(0, 50).trim() + (firstMessage.length > 50 ? '...' : '');
      }
      
      const response = await client.post('/chat/sessions', {
        title: sessionTitle,
        subject: topicSubject,
        topic: detectedTopic || 'General',
        ai_mode: aiMode
      });

      const sessionId = response.data.session_id;
      
      // Refresh sessions list
      await fetchSessions();
      
      // Set as current session
      setCurrentSession(sessionId);
      
      return sessionId;
    } catch (err) {
      console.error('Failed to create session:', err);
      setError(err.message || 'Failed to create session');
      return null;
    } finally {
      setLoading(false);
    }
  }, [fetchSessions]);

  /**
   * Update session title based on detected topic
   * 
   * @param {string} sessionId - Session ID to update
   * @param {string} detectedTopic - Detected topic
   * @param {string} firstMessage - First message for title generation
   */
  const updateSessionTitle = useCallback(async (sessionId, detectedTopic, firstMessage) => {
    try {
      if (!detectedTopic || detectedTopic === 'General') return;

      const messageExcerpt = firstMessage.substring(0, 30).trim();
      const newTitle = `${detectedTopic}: ${messageExcerpt}${messageExcerpt.length < 30 ? '' : '...'}`;

      await client.patch(`/chat/sessions/${sessionId}`, {
        title: newTitle,
        topic: detectedTopic
      });
      
      // Refresh sessions to show updated title
      await fetchSessions();
    } catch (err) {
      console.error('Failed to update session title:', err);
      // Non-critical error, don't show to user
    }
  }, [fetchSessions]);

  /**
   * Switch to a different session
   * 
   * @param {string} sessionId - Session ID to switch to
   */
  const switchSession = useCallback((sessionId) => {
    setCurrentSession(sessionId);
  }, []);

  /**
   * Delete a session
   * 
   * @param {string} sessionId - Session ID to delete
   */
  const deleteSession = useCallback(async (sessionId) => {
    try {
      setLoading(true);
      setError(null);

      await client.delete(`/chat/sessions/${sessionId}`);
      
      // If deleted session was current, clear it
      if (currentSession === sessionId) {
        setCurrentSession(null);
      }
      
      // Refresh sessions list
      await fetchSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
      setError(err.message || 'Failed to delete session');
    } finally {
      setLoading(false);
    }
  }, [currentSession, fetchSessions]);

  /**
   * Load sessions on mount
   */
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    // State
    currentSession,
    sessions,
    loading,
    error,
    
    // Operations
    fetchSessions,
    createSession,
    updateSessionTitle,
    switchSession,
    deleteSession,
    setCurrentSession
  };
};

export default useAITutorSession;
