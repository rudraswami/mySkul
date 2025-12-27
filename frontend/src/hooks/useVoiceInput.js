/**
 * useVoiceInput Hook
 * 
 * Manages speech recognition for voice input using Web Speech API
 * WITH EXPLICIT STOP CONTROL - No auto-stop on silence
 * 
 * @returns {Object} Voice input state and operations
 */

import { useState, useCallback, useEffect, useRef } from 'react';

export const useVoiceInput = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef(null);
  const shouldBeListeningRef = useRef(false); // 🎯 EXPLICIT STOP FLAG
  const restartTimeoutRef = useRef(null); // For debouncing restarts

  /**
   * Initialize speech recognition on mount
   */
  useEffect(() => {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSupported(false);
      setError('Speech recognition is not supported in this browser');
      return;
    }

    setIsSupported(true);

    // Initialize recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening - don't stop after one sentence
    recognition.interimResults = true; // Get results while speaking
    recognition.lang = 'en-US';
    
    // 🎯 ENHANCED VOICE CAPTURE - Maximum clarity and accuracy
    // These settings improve recognition quality significantly
    if ('webkitSpeechRecognition' in window) {
      // Chrome-specific optimizations for better clarity
      try {
        recognition.maxAlternatives = 3; // Get multiple alternatives, pick best
        // Note: Chrome's implementation is optimized for natural speech
        // It handles pauses, background noise, and distance variations well
      } catch (e) {
        console.warn('Some voice recognition settings not supported:', e);
      }
    }
    
    // Alternative language options for better Indian English recognition
    // Uncomment to use Indian English variant:
    // recognition.lang = 'en-IN'; // Better for Indian accents

    // Event handlers
    recognition.onresult = (event) => {
      console.log('🎤 [onresult] Event received, resultIndex:', event.resultIndex, 'total results:', event.results.length);
      
      // 🎯 INTELLIGENT TRANSCRIPT STATE MACHINE v3
      // KEY INSIGHT: Interim results are PROGRESSIVE REFINEMENTS, not new segments!
      // Browser: "hel" → "hello" → "hello world" (same segment being refined)
      
      // Build the complete transcript from ALL results
      let finalParts = [];
      let currentInterim = '';
      
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript.trim();
        
        if (!text) continue;
        
        if (result.isFinal) {
          // This segment is finalized - add to final parts
          console.log(`✅ [${i}] FINAL: "${text}"`);
          finalParts.push(text);
        } else {
          // This is the current interim (being refined by browser)
          // There should only be ONE active interim at a time
          console.log(`📝 [${i}] INTERIM: "${text}"`);
          currentInterim = text; // REPLACE, don't append
        }
      }
      
      // Combine all final parts
      let finalText = finalParts.join(' ').trim();
      
      // Apply deduplication to final text
      if (finalText) {
        finalText = removeWordRepetitions(finalText);
        finalText = formatTranscript(finalText);
      }
      
      // Display = all finals + current interim (if any)
      const displayText = currentInterim
        ? (finalText + ' ' + currentInterim).trim()
        : finalText;
      
      console.log(`🎙️ Display: "${displayText}" (finals: "${finalText}", interim: "${currentInterim}")`);
      
      // Only update if we have something to show
      if (displayText) {
        setTranscript(displayText);
      }
    };
    
    // 🎯 HELPER: Remove consecutive word repetitions (e.g., "okay okay okay" → "okay")
    const removeWordRepetitions = (text) => {
      if (!text) return text;
      
      const words = text.split(/\s+/);
      const result = [];
      let lastWord = '';
      
      for (const word of words) {
        const normalized = word.toLowerCase().replace(/[.,!?;:]/g, '');
        if (normalized !== lastWord) {
          result.push(word);
          lastWord = normalized;
        }
      }
      
      return result.join(' ');
    };
    
    // 🎯 HELPER: Format transcript for human-level clarity
    const formatTranscript = (text) => {
      if (!text) return text;
      
      // Remove triple+ consecutive word repetitions via regex
      let formatted = text.replace(/\b(\w+)(\s+\1){2,}\b/gi, '$1');
      
      // Capitalize first letter
      formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);
      
      // Capitalize after sentence endings
      formatted = formatted.replace(/([.!?]\s+)(\w)/g, (match, p1, p2) => p1 + p2.toUpperCase());
      
      return formatted;
    };

    recognition.onstart = () => {
      console.log('🎤 ✅ Recognition STARTED - browser is listening');
      setIsListening(true);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      // 🎯 CRITICAL: Don't stop on 'no-speech' if user explicitly wants to keep listening
      if (event.error === 'no-speech') {
        if (shouldBeListeningRef.current) {
          console.log('🎤 No speech detected, but keeping mic active (explicit mode)');
          // Don't show error, don't stop listening - user will stop when ready
          return;
        }
      }
      
      let errorMessage = 'Speech recognition error';
      
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not accessible. Please check permissions.';
          shouldBeListeningRef.current = false; // Can't continue without mic
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied.';
          shouldBeListeningRef.current = false; // User denied permission
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          // Don't stop - will auto-retry
          break;
        case 'aborted':
          // Normal stop, don't show error
          return;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }
      
      setError(errorMessage);
      
      // Only stop if it's a fatal error
      if (event.error === 'audio-capture' || event.error === 'not-allowed') {
        setIsListening(false);
      }
    };

    recognition.onend = () => {
      console.log('🎤 Recognition ended, shouldBeListening:', shouldBeListeningRef.current);
      
      // 🎯 CRITICAL FIX: Auto-restart if user hasn't explicitly stopped
      if (shouldBeListeningRef.current) {
        console.log('🔄 Auto-restarting recognition (explicit stop not triggered)');
        
        // Clear any pending restart
        if (restartTimeoutRef.current) {
          clearTimeout(restartTimeoutRef.current);
        }
        
        // Restart after a short delay to avoid rapid restart loops
        restartTimeoutRef.current = setTimeout(() => {
          if (shouldBeListeningRef.current && recognitionRef.current) {
            try {
                    recognitionRef.current.start();
              console.log('✅ Recognition restarted successfully');
            } catch (err) {
              if (!err.message.includes('already started')) {
                console.error('Failed to restart recognition:', err);
                setError('Voice input stopped unexpectedly. Click mic to restart.');
                setIsListening(false);
                shouldBeListeningRef.current = false;
              }
            }
          }
        }, 100); // Small delay to avoid immediate restart issues
      } else {
        // User explicitly stopped - update UI state
        setIsListening(false);
      }
    };

    recognitionRef.current = recognition;

    // Cleanup
    return () => {
      shouldBeListeningRef.current = false; // Prevent restarts during unmount
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (err) {
          // Ignore errors on cleanup
        }
      }
    };
  }, []);

  /**
   * Start listening to voice input
   * 🎯 EXPLICIT START - Sets flag to keep listening until user stops
   */
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition is not supported');
      return;
    }

    if (!recognitionRef.current) {
      setError('Speech recognition not initialized');
      return;
    }

    try {
      setError(null);
      setTranscript(''); // Clear display transcript
      shouldBeListeningRef.current = true; // 🎯 Set explicit listening flag
      recognitionRef.current.start();
      setIsListening(true);
      console.log('🎤 Started listening (explicit mode, clean state)');
    } catch (err) {
      if (err.message.includes('already started')) {
        // Already listening, just update state
        shouldBeListeningRef.current = true;
        setIsListening(true);
        console.log('🎤 Already listening, flag updated');
      } else {
        console.error('Failed to start speech recognition:', err);
        setError('Failed to start voice input');
        shouldBeListeningRef.current = false;
      }
    }
  }, [isSupported]);

  /**
   * Stop listening to voice input
   * 🎯 EXPLICIT STOP - Clears flag to prevent auto-restart
   */
  const stopListening = useCallback(() => {
    console.log('🛑 Explicit stop requested');
    shouldBeListeningRef.current = false; // 🎯 Clear explicit listening flag FIRST
    
    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error('Failed to stop speech recognition:', err);
      }
    }
    setIsListening(false);
  }, []);

  /**
   * Toggle listening state
   */
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  /**
   * Clear transcript
   */
  const clearTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    isListening,
    transcript,
    error,
    isSupported,
    
    // Operations
    startListening,
    stopListening,
    toggleListening,
    clearTranscript,
    clearError
  };
};

export default useVoiceInput;
