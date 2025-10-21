/**
 * useAIGeneration Hook
 * 
 * Handles AI response generation - calling backend APIs, retry logic, streaming support
 * 
 * @returns {Object} Generation state and operations
 */

import { useState, useCallback } from 'react';
import axios from 'axios';

// CRITICAL: Fail fast if BACKEND_URL not configured
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
if (!BACKEND_URL) {
  throw new Error('REACT_APP_BACKEND_URL environment variable is required');
}
const API = `${BACKEND_URL}/api`;

// Configuration
const TIMEOUT_DURATION = 45000; // 45 seconds
const RETRY_ATTEMPTS = 2;

export const useAIGeneration = () => {
  const [generating, setGenerating] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  /**
   * Generate AI response based on mode
   * 
   * @param {Object} params - Generation parameters
   * @param {string} params.message - User message
   * @param {string} params.subject - Subject/topic
   * @param {string} params.sessionId - Session ID
   * @param {string} params.aiMode - AI mode (dual, mentor, professor)
   * @param {string} params.depthLevel - Depth level (quick, standard, deep)
   * @param {string} params.examMode - Exam mode (JEE, NEET, CBSE)
   * @returns {Object|null} - AI response or null if failed
   */
  const generateResponse = useCallback(async ({
    message,
    subject = 'General',
    sessionId = null,
    aiMode = 'dual',
    depthLevel = 'standard',
    examMode = 'JEE'
  }) => {
    if (!message || !message.trim()) {
      setError('Message cannot be empty');
      return null;
    }

    try {
      setGenerating(true);
      setStreaming(false);
      setError(null);
      setProgress(0);

      const token = localStorage.getItem('dhruv_ai_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      let lastError = null;
      let response = null;

      // Retry logic
      for (let attempt = 1; attempt <= RETRY_ATTEMPTS; attempt++) {
        try {
          console.log(`🔄 AI API call - attempt ${attempt}/${RETRY_ATTEMPTS}`);
          
          // Update progress
          setProgress((attempt - 1) * 50);

          // Choose endpoint based on AI mode
          let endpoint = '/ai/dual-response';
          if (aiMode === 'mentor') {
            endpoint = '/ai/mentor-only';
          } else if (aiMode === 'professor') {
            endpoint = '/ai/professor-only';
          }

          const requestBody = {
            message,
            subject,
            session_id: sessionId,
            depth_level: depthLevel,
            exam_mode: examMode
          };

          response = await axios.post(`${API}${endpoint}`, requestBody, { 
            headers,
            timeout: TIMEOUT_DURATION
          });

          // Success - break retry loop
          setProgress(100);
          console.log('✅ AI response received successfully');
          break;

        } catch (attemptError) {
          lastError = attemptError;
          console.error(`❌ Attempt ${attempt} failed:`, attemptError.message);
          
          // If this was the last attempt, throw the error
          if (attempt === RETRY_ATTEMPTS) {
            throw attemptError;
          }
          
          // Wait before retry (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }

      if (!response) {
        throw lastError || new Error('Failed to generate AI response');
      }

      // Extract response data based on AI mode
      let aiResponse;
      if (aiMode === 'dual') {
        aiResponse = response.data;
      } else {
        aiResponse = {
          response: response.data.response || response.data.message,
          scenario_type: response.data.scenario_type,
          topic: response.data.topic
        };
      }

      return aiResponse;

    } catch (err) {
      console.error('❌ AI generation failed:', err);
      
      let errorMessage = 'Failed to generate AI response';
      
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        errorMessage = 'Request timed out. The AI is taking longer than expected. Please try again.';
      } else if (err.response?.status === 401) {
        errorMessage = 'Authentication required. Please log in again.';
      } else if (err.response?.status === 429) {
        errorMessage = 'Rate limit exceeded. Please wait a moment and try again.';
      } else if (err.response?.status === 403) {
        errorMessage = 'You have reached your AI session limit. Please upgrade your plan.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      return null;

    } finally {
      setGenerating(false);
      setProgress(0);
    }
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    generating,
    streaming,
    error,
    progress,
    
    // Operations
    generateResponse,
    clearError
  };
};

export default useAIGeneration;
