/**
 * useAIGeneration Hook
 * Handles AI response generation with subscription checks
 */
import { useState, useCallback } from 'react';
import { apiClient } from '../api/client';
import { useSubscription } from '../contexts/SubscriptionContext';

export function useAIGeneration() {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const { checkFeatureAccess, trackFeatureUsage } = useSubscription();

  // Generate AI response
  const generateResponse = useCallback(async (sessionId, userMessage, options = {}) => {
    try {
      // Check subscription access
      const access = await checkFeatureAccess('ai_sessions_monthly');
      if (!access.has_access) {
        // Upsell modal will be shown by SubscriptionContext
        throw new Error('AI Tutor session limit reached. Please upgrade to continue.');
      }

      setGenerating(true);
      setError(null);

      const response = await apiClient.post('/tutor/generate', {
        session_id: sessionId,
        message: userMessage,
        mode: options.mode || 'dual',
        depth_level: options.depthLevel || 'standard',
        exam_type: options.examType || 'JEE',
        ...options
      });

      // Track usage
      await trackFeatureUsage('ai_sessions_monthly');

      return response.data;
    } catch (err) {
      console.error('AI generation failed:', err);
      setError(err.message);
      throw err;
    } finally {
      setGenerating(false);
    }
  }, [checkFeatureAccess, trackFeatureUsage]);

  // Stream AI response (for real-time generation)
  const streamResponse = useCallback(async (sessionId, userMessage, onChunk, options = {}) => {
    try {
      // Check subscription access
      const access = await checkFeatureAccess('ai_sessions_monthly');
      if (!access.has_access) {
        throw new Error('AI Tutor session limit reached. Please upgrade to continue.');
      }

      setGenerating(true);
      setError(null);

      // Note: Implement actual streaming with EventSource or WebSocket
      // For now, using regular request
      const response = await generateResponse(sessionId, userMessage, options);
      
      if (onChunk && response.response) {
        onChunk(response.response);
      }

      return response;
    } catch (err) {
      console.error('AI streaming failed:', err);
      setError(err.message);
      throw err;
    } finally {
      setGenerating(false);
    }
  }, [checkFeatureAccess, generateResponse]);

  return {
    generating,
    error,
    generateResponse,
    streamResponse
  };
}

export default useAIGeneration;
