/**
 * Visual Generator Hook
 * Manages SVG generation and fallback to Gemini image generation
 */
import { useState, useCallback } from 'react';
import { generateConceptSVG, getGeminiPrompt } from '../utils/svgGenerator';

export function useVisualGenerator() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [visualCache, setVisualCache] = useState(new Map());

  /**
   * Generate visual for a concept
   * @param {string} topic - The topic/concept
   * @param {string} subject - The subject area
   * @param {boolean} useGeminiFallback - Whether to use Gemini as fallback
   * @returns {Promise<Object>} - Visual generation result
   */
  const generateVisual = useCallback(async (topic, subject = 'general', useGeminiFallback = true) => {
    if (!topic) {
      return {
        type: 'svg',
        content: generateConceptSVG('', subject),
        success: true
      };
    }

    const cacheKey = `${topic}-${subject}`;
    
    // Check cache first
    if (visualCache.has(cacheKey)) {
      return visualCache.get(cacheKey);
    }

    setIsLoading(true);
    setError(null);

    try {
      // Primary: Generate SVG programmatically
      const svgContent = generateConceptSVG(topic, subject);
      
      const result = {
        type: 'svg',
        content: svgContent,
        success: true,
        topic,
        subject,
        timestamp: Date.now()
      };

      // Cache the result
      setVisualCache(prev => {
        const newCache = new Map(prev);
        newCache.set(cacheKey, result);
        
        // Keep cache size reasonable (max 50 items)
        if (newCache.size > 50) {
          const oldestKey = Array.from(newCache.keys())[0];
          newCache.delete(oldestKey);
        }
        
        return newCache;
      });

      setIsLoading(false);
      return result;

    } catch (error) {
      console.warn('SVG generation failed:', error);
      
      // Fallback: Try Gemini image generation if enabled
      if (useGeminiFallback) {
        try {
          const geminiResult = await generateGeminiImage(topic, subject);
          setIsLoading(false);
          return geminiResult;
        } catch (geminiError) {
          console.warn('Gemini fallback failed:', geminiError);
        }
      }

      // Final fallback: Return default SVG
      const fallbackResult = {
        type: 'svg',
        content: generateConceptSVG('', 'general'),
        success: false,
        error: error.message,
        topic,
        subject
      };

      setError(error.message);
      setIsLoading(false);
      return fallbackResult;
    }
  }, [visualCache]);

  /**
   * Generate image using Gemini (fallback method)
   * @param {string} topic - The topic
   * @param {string} subject - The subject
   * @returns {Promise<Object>} - Generation result
   */
  const generateGeminiImage = useCallback(async (topic, subject) => {
    // This would integrate with Gemini image generation API
    // For now, return SVG fallback
    const prompt = getGeminiPrompt(topic, subject);
    
    // TODO: Implement actual Gemini API call when integration is ready
    // const response = await geminiAPI.generateImage(prompt);
    
    // For now, return enhanced SVG
    return {
      type: 'svg',
      content: generateConceptSVG(topic, subject),
      success: true,
      fallback: true,
      prompt,
      topic,
      subject
    };
  }, []);

  /**
   * Get visual for quick concepts (optimized for performance)
   * @param {string} concept - Simple concept name
   * @returns {string} - SVG content
   */
  const getQuickVisual = useCallback((concept) => {
    return generateConceptSVG(concept, 'general');
  }, []);

  /**
   * Preload visuals for common concepts
   * @param {Array<string>} concepts - Array of concept topics
   * @param {string} subject - Subject area
   */
  const preloadVisuals = useCallback(async (concepts, subject = 'general') => {
    const preloadPromises = concepts.map(concept => 
      generateVisual(concept, subject, false) // No Gemini fallback for preload
    );
    
    try {
      await Promise.all(preloadPromises);
    } catch (error) {
      console.warn('Preload failed for some visuals:', error);
    }
  }, [generateVisual]);

  /**
   * Clear visual cache
   */
  const clearCache = useCallback(() => {
    setVisualCache(new Map());
  }, []);

  /**
   * Get cache statistics
   * @returns {Object} - Cache stats
   */
  const getCacheStats = useCallback(() => {
    return {
      size: visualCache.size,
      keys: Array.from(visualCache.keys()),
      totalSizeMB: visualCache.size * 0.01 // Rough estimate
    };
  }, [visualCache]);

  return {
    generateVisual,
    getQuickVisual,
    preloadVisuals,
    clearCache,
    getCacheStats,
    isLoading,
    error,
    cacheSize: visualCache.size
  };
}