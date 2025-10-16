/**
 * useChatMessages Hook
 * Manages messages for a chat session
 */
import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../api/client';

export function useChatMessages(sessionId) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);

  // Fetch messages for the current session
  const fetchMessages = useCallback(async () => {
    if (!sessionId) {
      setMessages([]);
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.get(`/tutor/sessions/${sessionId}/messages`);
      setMessages(response.data.messages || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Send a user message
  const sendMessage = useCallback(async (content, metadata = {}) => {
    if (!sessionId || !content.trim()) return null;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
      ...metadata
    };

    // Optimistically add user message
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await apiClient.post(`/tutor/sessions/${sessionId}/messages`, {
        content: userMessage.content,
        role: 'user',
        ...metadata
      });
      
      // Update with server response if different
      if (response.data.message) {
        setMessages(prev => 
          prev.map(msg => msg.id === userMessage.id ? response.data.message : msg)
        );
      }

      setError(null);
      return response.data.message || userMessage;
    } catch (err) {
      console.error('Failed to send message:', err);
      // Remove failed message
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      setError(err.message);
      throw err;
    }
  }, [sessionId]);

  // Add an AI response (from streaming or batch response)
  const addAIMessage = useCallback((content, metadata = {}) => {
    const aiMessage = {
      id: Date.now().toString() + '-ai',
      role: 'assistant',
      content,
      timestamp: new Date().toISOString(),
      ...metadata
    };

    setMessages(prev => [...prev, aiMessage]);
    return aiMessage;
  }, []);

  // Update a message (for streaming)
  const updateMessage = useCallback((messageId, updates) => {
    setMessages(prev =>
      prev.map(msg => msg.id === messageId ? { ...msg, ...updates } : msg)
    );
  }, []);

  // Delete a message
  const deleteMessage = useCallback(async (messageId) => {
    try {
      await apiClient.delete(`/tutor/messages/${messageId}`);
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
      setError(null);
    } catch (err) {
      console.error('Failed to delete message:', err);
      setError(err.message);
      throw err;
    }
  }, []);

  // Clear all messages (local only)
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Load messages when session changes
  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  return {
    messages,
    loading,
    streaming,
    error,
    sendMessage,
    addAIMessage,
    updateMessage,
    deleteMessage,
    clearMessages,
    refreshMessages: fetchMessages,
    setStreaming
  };
}

export default useChatMessages;
