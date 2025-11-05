/**
 * Streaming AI Response Hook
 * Handles Server-Sent Events for progressive AI response rendering
 * 
 * Features:
 * - Text streaming: <2s to first token
 * - Visual fallback tiers: cache → SVG → AI → emoji
 * - Progress tracking
 */
import { useState, useCallback, useRef } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useStreamingAI = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [progress, setProgress] = useState({
    visual: null,
    visualTier: 0,
    textChunks: [],
    complete: false,
    cached: false,
    error: null
  });
  const eventSourceRef = useRef(null);

  const streamMentorResponse = useCallback(async ({
    message,
    subject,
    sessionId,
    examMode = 'JEE'
  }) => {
    setIsStreaming(true);
    setProgress({
      visual: null,
      visualTier: 0,
      textChunks: [],
      complete: false,
      cached: false,
      error: null
    });

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      // Create EventSource for SSE
      const url = `${BACKEND_URL}/api/ai/neuro-symbolic/stream`;
      const eventSource = new EventSource(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      eventSourceRef.current = eventSource;

      // Handle visual fallback event (Tier 1: SVG template)
      eventSource.addEventListener('visual_fallback', (e) => {
        const data = JSON.parse(e.data);
        console.log('📸 Visual fallback (Tier 1):', data);
        setProgress(prev => ({
          ...prev,
          visual: {
            type: 'fallback',
            tier: data.tier,
            url: data.visual_url,
            emoji: data.placeholder_emoji,
            colorTheme: data.color_theme
          },
          visualTier: data.tier
        }));
      });

      // Handle cache hit event
      eventSource.addEventListener('cache_hit', (e) => {
        const data = JSON.parse(e.data);
        console.log('⚡ Cache hit:', data);
        setProgress(prev => ({
          ...prev,
          cached: true
        }));
      });

      // Handle text chunk streaming
      eventSource.addEventListener('text_chunk', (e) => {
        const data = JSON.parse(e.data);
        console.log('📝 Text chunk received:', data);
        setProgress(prev => ({
          ...prev,
          textChunks: [...prev.textChunks, data]
        }));
      });

      // Handle visual upgrade (Tier 2: AI-generated)
      eventSource.addEventListener('visual_upgrade', (e) => {
        const data = JSON.parse(e.data);
        console.log('🎨 Visual upgraded (Tier 2):', data);
        setProgress(prev => ({
          ...prev,
          visual: {
            type: 'ai_generated',
            tier: data.tier,
            url: data.visual_url
          },
          visualTier: data.tier
        }));
      });

      // Handle visual timeout (keep Tier 1)
      eventSource.addEventListener('visual_timeout', (e) => {
        const data = JSON.parse(e.data);
        console.log('⏱️ Visual timeout, using fallback:', data);
      });

      // Handle completion
      eventSource.addEventListener('complete', (e) => {
        const data = JSON.parse(e.data);
        console.log('✅ Streaming complete:', data);
        setProgress(prev => ({
          ...prev,
          complete: true
        }));
        setIsStreaming(false);
        eventSource.close();
      });

      // Handle errors
      eventSource.addEventListener('error', (e) => {
        const data = e.data ? JSON.parse(e.data) : { error: 'Stream error' };
        console.error('❌ Stream error:', data);
        setProgress(prev => ({
          ...prev,
          error: data.error,
          complete: true
        }));
        setIsStreaming(false);
        eventSource.close();
      });

      // Handle connection errors
      eventSource.onerror = (error) => {
        console.error('❌ EventSource error:', error);
        setProgress(prev => ({
          ...prev,
          error: 'Connection lost',
          complete: true
        }));
        setIsStreaming(false);
        eventSource.close();
      };

    } catch (error) {
      console.error('❌ Streaming setup error:', error);
      setProgress(prev => ({
        ...prev,
        error: error.message,
        complete: true
      }));
      setIsStreaming(false);
    }
  }, []);

  const cancelStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  // Build final response from chunks
  const getFinalResponse = useCallback(() => {
    if (progress.textChunks.length === 0) return null;

    const defaultView = progress.textChunks.find(chunk => chunk.type === 'default_view');
    const progressiveSections = progress.textChunks.find(chunk => chunk.type === 'progressive_sections');

    return {
      default_view: defaultView?.data || {},
      progressive_sections: progressiveSections?.data || {},
      visual: progress.visual,
      cached: progress.cached
    };
  }, [progress]);

  return {
    isStreaming,
    progress,
    streamMentorResponse,
    cancelStream,
    getFinalResponse
  };
};
