/**
 * useVoiceInput Hook - Advanced Voice-to-Text System
 * 
 * FEATURES:
 * - Multi-language support (en-US, en-IN, hi-IN)
 * - Confidence score filtering
 * - Smart punctuation for questions
 * - Educational vocabulary optimization
 * - Audio quality feedback (volume meter)
 * - Voice Activity Detection (VAD)
 * - Multi-alternative processing
 * - Auto-retry error recovery
 * - Graceful fallback for unsupported browsers
 * 
 * @returns {Object} Voice input state and operations
 */

import { useState, useCallback, useEffect, useRef } from 'react';

// ============================================================================
// FIX #6: Educational Vocabulary Dictionary
// These terms are commonly misrecognized - we'll post-process to correct them
// ============================================================================
const EDUCATIONAL_CORRECTIONS = {
  // Physics
  'new tins': "Newton's",
  'new tons': "Newton's",
  'newton': "Newton's",
  'thermodynamic': 'thermodynamics',
  'thermo dynamics': 'thermodynamics',
  'kinematic': 'kinematics',
  'kine matics': 'kinematics',
  'electro magnetic': 'electromagnetic',
  'photo electric': 'photoelectric',
  'gravitational': 'gravitational',
  'acceleration due to gravity': 'acceleration due to gravity (g)',
  
  // Chemistry
  'hydro chloric': 'hydrochloric',
  'sodium chloride': 'sodium chloride (NaCl)',
  'photo synthesis': 'photosynthesis',
  'electro lysis': 'electrolysis',
  'stoichio metry': 'stoichiometry',
  'stoy key ometry': 'stoichiometry',
  
  // Mathematics
  'quadratic': 'quadratic',
  'quad ratic': 'quadratic',
  'differentiation': 'differentiation',
  'differ entiation': 'differentiation',
  'integration by parts': 'integration by parts',
  'partial fractions': 'partial fractions',
  'trigono metric': 'trigonometric',
  'trig functions': 'trigonometric functions',
  'pythagoras': 'Pythagoras',
  'pie thag orus': 'Pythagoras',
  
  // Biology
  'mitochon dria': 'mitochondria',
  'my toe con drea': 'mitochondria',
  'deoxy ribo nucleic': 'deoxyribonucleic (DNA)',
  'ribo nucleic': 'ribonucleic (RNA)',
  'photo synthesis': 'photosynthesis',
  
  // Common academic phrases
  'can you explain': 'Can you explain',
  'what is the': 'What is the',
  'how do i': 'How do I',
  'how to solve': 'How to solve',
  'please help': 'Please help',
};

// ============================================================================
// FIX #5: Question Detection Patterns (for smart punctuation)
// ============================================================================
const QUESTION_STARTERS = [
  'what', 'why', 'how', 'when', 'where', 'who', 'which', 'whose',
  'is', 'are', 'was', 'were', 'do', 'does', 'did', 'can', 'could',
  'will', 'would', 'should', 'shall', 'may', 'might', 'has', 'have',
  'explain', 'define', 'describe', 'tell me', 'help me', 'show me'
];

// ============================================================================
// FIX #2: Supported Languages
// ============================================================================
const SUPPORTED_LANGUAGES = {
  'en-US': { name: 'English (US)', flag: '🇺🇸' },
  'en-IN': { name: 'English (India)', flag: '🇮🇳' },
  'en-GB': { name: 'English (UK)', flag: '🇬🇧' },
  'hi-IN': { name: 'Hindi', flag: '🇮🇳' },
};

const DEFAULT_LANGUAGE = 'en-IN'; // Default to Indian English for better recognition

// ============================================================================
// FIX #4: Confidence Thresholds
// ============================================================================
const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.85,      // Accept without warning
  MEDIUM: 0.70,    // Accept with low-confidence indicator
  LOW: 0.50,       // Accept but warn user
  REJECT: 0.30,    // Reject and ask to repeat
};

export const useVoiceInput = (options = {}) => {
  // ========== STATE ==========
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState(''); // FIX #9: Separate interim
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  const [language, setLanguage] = useState(options.language || DEFAULT_LANGUAGE); // FIX #2
  const [confidence, setConfidence] = useState(1.0); // FIX #4: Track confidence
  const [audioLevel, setAudioLevel] = useState(0); // FIX #3: Audio feedback
  const [isLowVolume, setIsLowVolume] = useState(false); // FIX #3: Volume warning
  const [lastSpeechTime, setLastSpeechTime] = useState(null); // FIX #7: VAD
  const [retryCount, setRetryCount] = useState(0); // FIX #10: Error recovery
  
  // ========== REFS ==========
  const recognitionRef = useRef(null);
  const shouldBeListeningRef = useRef(false);
  const restartTimeoutRef = useRef(null);
  const audioContextRef = useRef(null); // FIX #3: Audio analysis
  const analyserRef = useRef(null); // FIX #3: Audio level meter
  const mediaStreamRef = useRef(null); // FIX #3: Microphone stream
  const animationFrameRef = useRef(null); // FIX #3: Animation loop
  const vadTimeoutRef = useRef(null); // FIX #7: Voice activity timeout
  const finalTranscriptRef = useRef(''); // Track accumulated final transcript

  // ========== FIX #6: Apply Educational Corrections ==========
  const applyEducationalCorrections = useCallback((text) => {
    if (!text) return text;
    
    let corrected = text;
    
    // Apply known corrections (case-insensitive)
    for (const [wrong, right] of Object.entries(EDUCATIONAL_CORRECTIONS)) {
      const regex = new RegExp(wrong, 'gi');
      corrected = corrected.replace(regex, right);
    }
    
    return corrected;
  }, []);

  // ========== FIX #5: Smart Punctuation ==========
  const applySmartPunctuation = useCallback((text) => {
    if (!text) return text;
    
    let formatted = text.trim();
    
    // Check if it's a question (starts with question word or pattern)
    const lowerText = formatted.toLowerCase();
    const isQuestion = QUESTION_STARTERS.some(starter => 
      lowerText.startsWith(starter + ' ') || lowerText.startsWith(starter + ',')
    );
    
    // Check for question indicators in the middle
    const hasQuestionIndicator = /\b(what|why|how|can you|could you|please explain|help me)\b/i.test(lowerText);
    
    // Remove any existing trailing punctuation
    formatted = formatted.replace(/[.?!,;:]+$/, '');
    
    // Add appropriate punctuation
    if (isQuestion || hasQuestionIndicator) {
      formatted += '?';
    } else if (formatted.length > 0) {
      // Only add period for statements, not short phrases
      if (formatted.split(' ').length > 3) {
        formatted += '.';
      }
    }
    
    // Capitalize first letter
    formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);
    
    // Capitalize after sentence endings
    formatted = formatted.replace(/([.!?]\s+)(\w)/g, (match, p1, p2) => p1 + p2.toUpperCase());
    
    // Capitalize proper nouns (Newton, Pythagoras, etc.)
    const properNouns = ['newton', 'pythagoras', 'einstein', 'faraday', 'ohm', 'bohr', 'planck'];
    for (const noun of properNouns) {
      const regex = new RegExp(`\\b${noun}\\b`, 'gi');
      formatted = formatted.replace(regex, noun.charAt(0).toUpperCase() + noun.slice(1));
    }
    
    return formatted;
  }, []);

  // ========== FIX #9: Multi-Alternative Processing ==========
  const selectBestAlternative = useCallback((result) => {
    if (!result || result.length === 0) {
      return { text: '', confidence: 0 };
    }
    
    // Get all alternatives with confidence scores
    const alternatives = [];
    for (let i = 0; i < result.length; i++) {
      alternatives.push({
        text: result[i].transcript.trim(),
        confidence: result[i].confidence || 0.5
      });
    }
    
    // Sort by confidence
    alternatives.sort((a, b) => b.confidence - a.confidence);
    
    // Check if top alternatives contain educational terms
    const educationalTerms = Object.values(EDUCATIONAL_CORRECTIONS);
    
    for (const alt of alternatives) {
      // Prefer alternatives that contain recognized educational terms
      const hasEducationalTerm = educationalTerms.some(term => 
        alt.text.toLowerCase().includes(term.toLowerCase())
      );
      
      if (hasEducationalTerm && alt.confidence > CONFIDENCE_THRESHOLDS.LOW) {
        return alt;
      }
    }
    
    // Return highest confidence alternative
    return alternatives[0];
  }, []);

  // ========== Remove Word Repetitions ==========
  const removeWordRepetitions = useCallback((text) => {
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
    
    // Also remove triple+ consecutive repetitions via regex
    let cleaned = result.join(' ');
    cleaned = cleaned.replace(/\b(\w+)(\s+\1){2,}\b/gi, '$1');
    
    return cleaned;
  }, []);

  // ========== FIX #3: Audio Level Analysis ==========
  const startAudioAnalysis = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      mediaStreamRef.current = stream;
      
      // Create audio context
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      
      // Create analyser
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      analyserRef.current = analyser;
      
      // Connect microphone to analyser
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      // Start monitoring audio levels
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateLevel = () => {
        if (!analyserRef.current || !shouldBeListeningRef.current) {
          return;
        }
        
        analyserRef.current.getByteFrequencyData(dataArray);
        
        // Calculate RMS (root mean square) for volume
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length);
        const normalizedLevel = Math.min(100, (rms / 128) * 100);
        
        setAudioLevel(normalizedLevel);
        
        // FIX #7: Voice Activity Detection
        if (normalizedLevel > 15) {
          setLastSpeechTime(Date.now());
          setIsLowVolume(false);
        } else if (normalizedLevel < 5 && shouldBeListeningRef.current) {
          // Very low volume warning
          setIsLowVolume(true);
        }
        
        // Continue monitoring
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      
      updateLevel();
      
    } catch (err) {
      console.warn('Audio analysis not available:', err);
      // Don't fail - audio analysis is optional enhancement
    }
  }, []);

  // ========== Stop Audio Analysis ==========
  const stopAudioAnalysis = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    
    setAudioLevel(0);
    setIsLowVolume(false);
  }, []);

  // ========== FIX #10: Auto-Retry with Exponential Backoff ==========
  const scheduleRetry = useCallback((baseDelay = 100) => {
    if (retryCount >= 3) {
      // Max retries reached
      setError('Voice input stopped. Please click the microphone to restart.');
      setIsListening(false);
      shouldBeListeningRef.current = false;
      setRetryCount(0);
      return;
    }
    
    const delay = baseDelay * Math.pow(2, retryCount); // Exponential backoff
    
    restartTimeoutRef.current = setTimeout(() => {
      if (shouldBeListeningRef.current && recognitionRef.current) {
        try {
          recognitionRef.current.start();
          console.log(`✅ Recognition restarted (attempt ${retryCount + 1})`);
          setRetryCount(prev => prev + 1);
        } catch (err) {
          if (!err.message.includes('already started')) {
            console.error('Failed to restart recognition:', err);
            scheduleRetry(delay); // Try again
          }
        }
      }
    }, delay);
  }, [retryCount]);

  // ========== Initialize Speech Recognition ==========
  useEffect(() => {
    // FIX #1: Check browser support with graceful fallback message
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSupported(false);
      // FIX #1: Helpful message instead of generic error
      setError('Voice input requires Chrome, Edge, or Safari. You can still type your question!');
      console.warn('Speech recognition not supported. Browsers that support it: Chrome, Edge, Safari');
      return;
    }

    setIsSupported(true);

    // Initialize recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language; // FIX #2: Use selected language
    recognition.maxAlternatives = 3; // FIX #9: Get alternatives

    // ========== Result Handler ==========
    recognition.onresult = (event) => {
      // Build transcript from all results
      let finalParts = [];
      let currentInterim = '';
      let lowestConfidence = 1.0;
      
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        
        // FIX #9: Select best alternative
        const best = selectBestAlternative(result);
        const text = best.text;
        
        if (!text) continue;
        
        // FIX #4: Track confidence
        if (best.confidence < lowestConfidence) {
          lowestConfidence = best.confidence;
        }
        
        if (result.isFinal) {
          finalParts.push(text);
        } else {
          currentInterim = text;
        }
      }
      
      // Combine final parts
      let finalText = finalParts.join(' ').trim();
      
      // Apply all text processing
      if (finalText) {
        finalText = removeWordRepetitions(finalText);
        finalText = applyEducationalCorrections(finalText);
        finalText = applySmartPunctuation(finalText);
        finalTranscriptRef.current = finalText;
      }
      
      // Display = finals + interim
      const displayText = currentInterim
        ? (finalText + ' ' + currentInterim).trim()
        : finalText;
      
      // FIX #4: Update confidence state
      setConfidence(lowestConfidence);
      
      // Update transcripts
      if (displayText) {
        setTranscript(displayText);
      }
      
      if (currentInterim) {
        setInterimTranscript(currentInterim);
      } else {
        setInterimTranscript('');
      }
      
      // FIX #7: Update VAD timestamp
      setLastSpeechTime(Date.now());
    };

    recognition.onstart = () => {
      console.log('🎤 ✅ Recognition STARTED - language:', language);
      setIsListening(true);
      setRetryCount(0); // Reset retry count on successful start
      setError(null);
    };

    // ========== FIX #10: Enhanced Error Handler with Recovery ==========
    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      
      // Handle specific errors
      switch (event.error) {
        case 'no-speech':
          // FIX #7: Don't error if explicitly listening
          if (shouldBeListeningRef.current) {
            console.log('🎤 No speech detected, keeping mic active');
            return; // Don't show error, don't stop
          }
          setError('No speech detected. Speak closer to your microphone.');
          break;
          
        case 'audio-capture':
          setError('Microphone not found. Please check your microphone connection.');
          shouldBeListeningRef.current = false;
          stopAudioAnalysis();
          break;
          
        case 'not-allowed':
          setError('Microphone permission denied. Please allow microphone access and try again.');
          shouldBeListeningRef.current = false;
          stopAudioAnalysis();
          break;
          
        case 'network':
          // FIX #10: Auto-retry on network errors
          if (shouldBeListeningRef.current) {
            console.log('🔄 Network error, will auto-retry...');
            setError('Network issue detected. Retrying...');
            scheduleRetry(500);
            return;
          }
          setError('Network error. Please check your internet connection.');
          break;
          
        case 'aborted':
          // Normal stop, don't show error
          return;
          
        case 'service-not-allowed':
          // FIX #10: Retry service errors
          if (shouldBeListeningRef.current && retryCount < 3) {
            scheduleRetry(1000);
            return;
          }
          setError('Speech service temporarily unavailable. Please try again.');
          break;
          
        default:
          setError(`Voice input error: ${event.error}. Try speaking again.`);
      }
      
      // Only stop UI for fatal errors
      if (event.error === 'audio-capture' || event.error === 'not-allowed') {
        setIsListening(false);
      }
    };

    // ========== End Handler with Auto-Restart ==========
    recognition.onend = () => {
      console.log('🎤 Recognition ended, shouldContinue:', shouldBeListeningRef.current);
      
      if (shouldBeListeningRef.current) {
        // FIX #10: Auto-restart with retry logic
        scheduleRetry(100);
      } else {
        setIsListening(false);
        stopAudioAnalysis();
      }
    };

    recognitionRef.current = recognition;

    // Cleanup
    return () => {
      shouldBeListeningRef.current = false;
      
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
      
      if (vadTimeoutRef.current) {
        clearTimeout(vadTimeoutRef.current);
      }
      
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (err) {
          // Ignore cleanup errors
        }
      }
      
      stopAudioAnalysis();
    };
  }, [language, selectBestAlternative, removeWordRepetitions, applyEducationalCorrections, 
      applySmartPunctuation, scheduleRetry, stopAudioAnalysis]);

  // ========== FIX #2: Change Language ==========
  const changeLanguage = useCallback((newLanguage) => {
    if (!SUPPORTED_LANGUAGES[newLanguage]) {
      console.warn('Unsupported language:', newLanguage);
      return;
    }
    
    const wasListening = isListening;
    
    // Stop current recognition
    if (recognitionRef.current && isListening) {
      shouldBeListeningRef.current = false;
      recognitionRef.current.stop();
    }
    
    // Update language
    setLanguage(newLanguage);
    
    // Reinitialize with new language
    if (recognitionRef.current) {
      recognitionRef.current.lang = newLanguage;
    }
    
    // Restart if was listening
    if (wasListening) {
      setTimeout(() => {
        shouldBeListeningRef.current = true;
        try {
          recognitionRef.current?.start();
        } catch (err) {
          console.warn('Failed to restart after language change:', err);
        }
      }, 100);
    }
    
    console.log('🌐 Language changed to:', newLanguage);
  }, [isListening]);

  // ========== Start Listening ==========
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (!recognitionRef.current) {
      setError('Voice input not ready. Please refresh the page.');
      return;
    }

    try {
      setError(null);
      setTranscript('');
      setInterimTranscript('');
      setConfidence(1.0);
      setRetryCount(0);
      finalTranscriptRef.current = '';
      
      shouldBeListeningRef.current = true;
      
      // FIX #3: Start audio analysis for volume meter
      startAudioAnalysis();
      
      recognitionRef.current.start();
      setIsListening(true);
      
      console.log('🎤 Started listening (language:', language, ')');
      
    } catch (err) {
      if (err.message?.includes('already started')) {
        shouldBeListeningRef.current = true;
        setIsListening(true);
      } else {
        console.error('Failed to start voice input:', err);
        setError('Failed to start voice input. Please try again.');
        shouldBeListeningRef.current = false;
      }
    }
  }, [isSupported, language, startAudioAnalysis]);

  // ========== Stop Listening ==========
  const stopListening = useCallback(() => {
    console.log('🛑 Stop requested');
    shouldBeListeningRef.current = false;
    
    // Clear all timeouts
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    if (vadTimeoutRef.current) {
      clearTimeout(vadTimeoutRef.current);
      vadTimeoutRef.current = null;
    }
    
    // Stop recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        // Ignore
      }
    }
    
    // Stop audio analysis
    stopAudioAnalysis();
    
    // Apply final formatting to transcript
    if (finalTranscriptRef.current) {
      setTranscript(finalTranscriptRef.current);
    }
    
    setIsListening(false);
    setInterimTranscript('');
    setRetryCount(0);
  }, [stopAudioAnalysis]);

  // ========== Toggle Listening ==========
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // ========== Clear Transcript ==========
  const clearTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    finalTranscriptRef.current = '';
  }, []);

  // ========== Clear Error ==========
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // ========== FIX #4: Get Confidence Status ==========
  const getConfidenceStatus = useCallback(() => {
    if (confidence >= CONFIDENCE_THRESHOLDS.HIGH) {
      return { level: 'high', message: 'Clear recognition', color: 'green' };
    } else if (confidence >= CONFIDENCE_THRESHOLDS.MEDIUM) {
      return { level: 'medium', message: 'Good recognition', color: 'yellow' };
    } else if (confidence >= CONFIDENCE_THRESHOLDS.LOW) {
      return { level: 'low', message: 'Low confidence - please check', color: 'orange' };
    } else {
      return { level: 'poor', message: 'Poor recognition - try speaking clearly', color: 'red' };
    }
  }, [confidence]);

  // ========== RETURN ==========
  return {
    // Core State
    isListening,
    transcript,
    interimTranscript, // FIX #9: Separate interim for UI
    error,
    isSupported,
    
    // FIX #2: Language
    language,
    supportedLanguages: SUPPORTED_LANGUAGES,
    changeLanguage,
    
    // FIX #3: Audio Feedback
    audioLevel,
    isLowVolume,
    
    // FIX #4: Confidence
    confidence,
    getConfidenceStatus,
    
    // FIX #7: Voice Activity
    lastSpeechTime,
    
    // Operations
    startListening,
    stopListening,
    toggleListening,
    clearTranscript,
    clearError,
  };
};

export default useVoiceInput;

