/**
 * useAITutorMessages Hook
 * 
 * Manages chat messages for AI Tutor sessions - loading, sending, and persisting messages
 * 
 * @returns {Object} Message state and operations
 */

import { useState, useCallback } from 'react';
import client from '../api/client';

export const useAITutorMessages = (sessionId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load messages for the current session
   * 
   * @param {string} sid - Session ID to load messages from
   */
  const loadMessages = useCallback(async (sid) => {
    const targetSessionId = sid || sessionId;
    
    if (!targetSessionId) {
      setMessages([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await client.get(`/chat/${targetSessionId}/messages`);
      
      // Transform backend messages to component format
      const transformedMessages = (response.data.messages || []).map(msg => ({
        id: msg.message_id || msg._id,
        role: 'user',
        content: msg.user_message,
        timestamp: msg.timestamp,
        aiResponse: msg.ai_response
      }));

      setMessages(transformedMessages);
    } catch (err) {
      console.error('Failed to load messages:', err);
      
      // Don't show error for authentication issues
      if (err.response?.status === 401 || err.response?.status === 403) {
        console.log('ℹ️ Messages fetch requires authentication');
        setMessages([]);
      } else {
        setError(err.message || 'Failed to load messages');
        setMessages([]);
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /**
   * Add a user message to the local state (optimistic update)
   * 
   * @param {string} message - User message content
   * @returns {string} - Temporary message ID
   */
  const addUserMessage = useCallback((message) => {
    const tempId = `temp-${Date.now()}`;
    const newMessage = {
      id: tempId,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      pending: true
    };
    
    setMessages(prev => [...prev, newMessage]);
    return tempId;
  }, []);

  /**
   * Add AI response to the local state
   * 
   * @param {string} tempId - Temporary message ID to update
   * @param {Object} aiResponse - AI response object
   */
  const addAIResponse = useCallback((tempId, aiResponse) => {
    setMessages(prev => prev.map(msg => 
      msg.id === tempId 
        ? { ...msg, aiResponse, pending: false }
        : msg
    ));
  }, []);

  /**
   * Update a message (for streaming responses)
   * 
   * @param {string} messageId - Message ID to update
   * @param {Object} updates - Updates to apply
   */
  const updateMessage = useCallback((messageId, updates) => {
    setMessages(prev => prev.map(msg =>
      msg.id === messageId
        ? { ...msg, ...updates }
        : msg
    ));
  }, []);

  /**
   * Save message to backend (persisting to database)
   * 
   * @param {string} sid - Session ID
   * @param {string} userMessage - User message content
   * @param {Object} aiResponse - AI response object
   */
  const saveMessage = useCallback(async (sid, userMessage, aiResponse) => {
    const targetSessionId = sid || sessionId;
    
    if (!targetSessionId) {
      console.warn('Cannot save message: No session ID');
      return;
    }

    try {
      // Prepare AI response for storage
      let responseToStore = aiResponse;
      
      // If aiResponse has dual_response structure, preserve it entirely
      if (aiResponse && typeof aiResponse === 'object' && aiResponse.dual_response) {
        responseToStore = aiResponse;
      }
      // For other structures, save the complete object
      else if (aiResponse && typeof aiResponse === 'object') {
        responseToStore = aiResponse;
      }
      // If it's just text, wrap it in a simple structure
      else {
        responseToStore = { response: aiResponse };
      }

      await client.post(`/chat/${targetSessionId}/messages`, {
        user_message: userMessage,
        ai_response: responseToStore,
        timestamp: new Date().toISOString()
      });
    } catch (err) {
      console.error('Failed to save message:', err);
      // Non-critical error, message is already shown in UI
    }
  }, [sessionId]);

  /**
   * Clear all messages (for new session or reset)
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Remove a specific message
   * 
   * @param {string} messageId - Message ID to remove
   */
  const removeMessage = useCallback((messageId) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, []);

  return {
    // State
    messages,
    loading,
    error,
    
    // Operations
    loadMessages,
    addUserMessage,
    addAIResponse,
    updateMessage,
    saveMessage,
    clearMessages,
    removeMessage,
    setMessages
  };
};

export default useAITutorMessages;
