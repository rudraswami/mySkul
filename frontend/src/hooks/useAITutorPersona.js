/**
 * AI Tutor Persona Hook
 * Manages persona blending and emotion-aware responses
 */
import { useState, useEffect, useCallback } from 'react';
import { analyzeSentiment, getPersonaConfig, getMotivationalMessage } from '../utils/sentimentAnalysis';

export function useAITutorPersona() {
  const [currentPersona, setCurrentPersona] = useState('hybrid');
  const [personaConfig, setPersonaConfig] = useState(null);
  const [motivationalMessage, setMotivationalMessage] = useState('');
  const [sentimentHistory, setSentimentHistory] = useState([]);

  /**
   * Analyze user input and adapt persona
   * @param {string} userInput - User's question or message
   * @returns {Object} - Persona analysis result
   */
  const analyzeAndAdapt = useCallback((userInput) => {
    if (!userInput) return currentPersona;

    // Analyze sentiment
    const sentiment = analyzeSentiment(userInput);
    
    // Get persona configuration
    const config = getPersonaConfig(sentiment);
    
    // Generate motivational message
    const message = getMotivationalMessage(sentiment);
    
    // Update state
    setCurrentPersona(sentiment.persona);
    setPersonaConfig(config);
    setMotivationalMessage(message);
    
    // Update sentiment history (keep last 5 entries)
    setSentimentHistory(prev => {
      const newHistory = [...prev, sentiment];
      return newHistory.slice(-5);
    });

    return {
      persona: sentiment.persona,
      config,
      message,
      sentiment,
      emotion: sentiment.emotion
    };
  }, [currentPersona]);

  /**
   * Get persona styles for UI components
   * @returns {Object} - Style configuration
   */
  const getPersonaStyles = useCallback(() => {
    if (!personaConfig) {
      return {
        gradient: 'from-purple-500 to-purple-600',
        accentColor: '#9E7BF5',
        backgroundColor: '#F8F9FA',
        textColor: '#374151'
      };
    }

    const colorMap = {
      blue: {
        gradient: 'from-blue-500 to-blue-600',
        accentColor: '#5E81F4',
        backgroundColor: '#EBF4FF',
        textColor: '#1E40AF'
      },
      green: {
        gradient: 'from-green-500 to-green-600',
        accentColor: '#57D2A9',
        backgroundColor: '#ECFDF5',
        textColor: '#065F46'
      },
      purple: {
        gradient: 'from-purple-500 to-purple-600',
        accentColor: '#9E7BF5',
        backgroundColor: '#F5F3FF',
        textColor: '#6B21A8'
      }
    };

    return colorMap[personaConfig.colorScheme] || colorMap.purple;
  }, [personaConfig]);

  /**
   * Get adaptive response tone guidance
   * @param {string} aiResponse - AI's response content
   * @returns {Object} - Response adaptation guidance
   */
  const getResponseTone = useCallback((aiResponse = '') => {
    if (!personaConfig) {
      return {
        tone: 'balanced',
        emphasis: 'normal',
        supportLevel: 'medium'
      };
    }

    const { persona } = personaConfig;
    let tone = 'balanced';
    let emphasis = 'normal';
    let supportLevel = 'medium';

    switch (persona) {
      case 'professor':
        tone = 'academic';
        emphasis = 'conceptual';
        supportLevel = 'low';
        break;
      case 'mentor':
        tone = 'supportive';
        emphasis = 'encouraging';
        supportLevel = 'high';
        break;
      default:
        tone = 'balanced';
        emphasis = 'adaptive';
        supportLevel = 'medium';
    }

    // Adjust based on recent sentiment history
    const recentFrustration = sentimentHistory.slice(-2).some(s => 
      s.emotion === 'frustrated' || s.emotion === 'discouraged'
    );
    
    if (recentFrustration) {
      supportLevel = 'high';
      emphasis = 'encouraging';
    }

    return { tone, emphasis, supportLevel };
  }, [personaConfig, sentimentHistory]);

  /**
   * Reset persona to default state
   */
  const resetPersona = useCallback(() => {
    setCurrentPersona('hybrid');
    setPersonaConfig(null);
    setMotivationalMessage('');
    setSentimentHistory([]);
  }, []);

  return {
    currentPersona,
    personaConfig,
    motivationalMessage,
    sentimentHistory,
    analyzeAndAdapt,
    getPersonaStyles,
    getResponseTone,
    resetPersona
  };
}