/**
 * TeachMeBackModal - Immersive Feynman Technique Experience
 * 
 * TRUE MODAL: Viewport-attached, focused overlay
 * - Dimmed/blurred background
 * - Body scroll locked
 * - 100% student attention on explanation
 */
import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Spinner animation styles
const spinnerStyles = `
@keyframes teachBackSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.teach-back-spinner {
  animation: teachBackSpin 0.8s linear infinite;
}
`;

// Encouraging prompts that rotate
const WRITING_PROMPTS = [
  "Imagine explaining this to a friend who's never heard of it...",
  "What's the simplest way you'd describe this?",
  "If you had to teach this in 30 seconds, what would you say?",
  "Pretend you're the teacher - how would you explain it?"
];

const TeachMeBackModal = ({
  isOpen,
  onClose,
  concept,
  originalExplanation,
  initialPrompt = '',  // Backend-provided prompt (intelligent, context-aware)
  mode = 'quick_check' // Backend-determined mode: quick_check | step_check | deep_teach
}) => {
  const [step, setStep] = useState('input'); // input | loading | result | error
  const [explanation, setExplanation] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);
  const [promptIndex, setPromptIndex] = useState(0);
  const textareaRef = useRef(null);

  // Use backend prompt if provided, otherwise use random fallback
  const displayPrompt = initialPrompt || WRITING_PROMPTS[promptIndex];

  // LOCK BODY SCROLL when modal opens
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY;
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
      document.body.style.overflow = 'hidden';
      
      return () => {
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.overflow = '';
        window.scrollTo(0, scrollY);
      };
    }
  }, [isOpen]);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setStep('input');
      setExplanation('');
      setFeedback(null);
      setError(null);
      // Only set random prompt index if no backend prompt provided
      if (!initialPrompt) {
        setPromptIndex(Math.floor(Math.random() * WRITING_PROMPTS.length));
      }
      setTimeout(() => textareaRef.current?.focus(), 300);
    }
  }, [isOpen, initialPrompt]);

  // Handle escape key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  // Evaluate explanation
  const handleSubmit = async () => {
    if (!explanation.trim() || step === 'loading') return;
    
    setStep('loading');
    setError(null);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      // Add timeout protection (40 seconds)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 40000);
      
      const response = await fetch(`${BACKEND_URL}/api/ai/teach-me-back`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          concept: concept,
          original_explanation: originalExplanation,
          student_explanation: explanation
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setFeedback(data.feedback || {
        understood: ['You made an effort to explain the concept'],
        gaps: [],
        tip: 'Try adding more specific details',
        encouragement: 'Good start! Keep practicing.'
      });
      setStep('result');
    } catch (error) {
      console.error('Evaluation failed:', error);
      
      // Handle specific error types
      if (error.name === 'AbortError') {
        setError('Request took too long. Please try again with a shorter explanation.');
      } else if (error.message.includes('Failed to fetch')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Something went wrong. Please try again.');
      }
      
      setStep('error');
    }
  };
  
  // Retry after error
  const handleRetry = () => {
    setError(null);
    setStep('input');
  };

  const handleTryAgain = () => {
    setStep('input');
    setExplanation('');
    setFeedback(null);
    setError(null);
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  const wordCount = explanation.trim().split(/\s+/).filter(Boolean).length;
  const hasGaps = feedback?.gaps?.length > 0;
  const masteryLevel = feedback ? (hasGaps ? 'building' : 'solid') : null;

  // Portal content
  const modalContent = (
    <AnimatePresence mode="wait">
      {isOpen && (
        <div key="modal-wrapper">
          {/* BACKDROP */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-md"
            onClick={onClose}
          />
          
          {/* MODAL CONTAINER */}
          <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4 sm:p-6 md:p-8 pointer-events-none overflow-y-auto">
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 30 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 30 }}
              transition={{ type: 'spring', damping: 30, stiffness: 400 }}
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden pointer-events-auto my-auto flex flex-col"
              style={{ maxHeight: 'calc(100vh - 4rem)', minHeight: '400px' }}
              role="dialog"
              aria-modal="true"
            >
              {/* HEADER */}
              <div className="px-6 py-5 bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-white flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
                      <span className="text-2xl">🎓</span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">Teach Me Back</h2>
                      <p className="text-amber-100 text-sm">The best way to learn is to teach</p>
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2.5 rounded-xl bg-white/10 hover:bg-white/25 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* CONTENT */}
              <div className="flex-1 overflow-y-auto p-6">
                {/* Topic */}
                <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Topic</p>
                  <p className="text-gray-800 dark:text-gray-200 font-medium">{concept}</p>
                </div>

                {/* INPUT STEP */}
                {step === 'input' && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                      <span>✨</span>
                      <p className="text-sm font-medium">{displayPrompt}</p>
                    </div>

                    <textarea
                      ref={textareaRef}
                      value={explanation}
                      onChange={(e) => setExplanation(e.target.value)}
                      placeholder="Type your explanation here... Don't worry about being perfect!"
                      className="w-full h-48 p-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:border-amber-500 resize-none text-lg"
                    />

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>📖</span>
                        <span>{wordCount} words</span>
                        {wordCount < 10 && <span className="text-amber-500">• Add more detail</span>}
                        {wordCount >= 30 && <span className="text-emerald-500">• Great detail! ✓</span>}
                      </div>

                      <button
                        onClick={handleSubmit}
                        disabled={wordCount < 5}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                          wordCount >= 5
                            ? 'bg-amber-500 hover:bg-amber-600 text-white shadow-lg'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                        Check My Understanding
                      </button>
                    </div>
                  </div>
                )}

                {/* LOADING STEP */}
                {step === 'loading' && (
                  <div className="py-12 text-center">
                    <style>{spinnerStyles}</style>
                    <div className="w-16 h-16 mx-auto mb-4 border-4 border-amber-500 border-t-transparent rounded-full teach-back-spinner" />
                    <p className="text-lg text-gray-600 dark:text-gray-400 animate-pulse">Analyzing your explanation...</p>
                    <p className="text-sm text-gray-500 dark:text-gray-600 mt-2">Finding what you understood and what to strengthen</p>
                  </div>
                )}

                {/* ERROR STEP */}
                {step === 'error' && error && (
                  <div className="py-12 text-center">
                    <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center bg-red-100 dark:bg-red-900/30 rounded-full">
                      <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p className="text-lg text-gray-800 dark:text-gray-200 font-semibold mb-2">Oops!</p>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
                    <button
                      onClick={handleRetry}
                      className="px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-semibold transition-all"
                    >
                      Try Again
                    </button>
                  </div>
                )}

                {/* RESULT STEP - Student-Friendly, Encouraging Design */}
                {step === 'result' && feedback && (
                  <div className="space-y-4">
                    {/* Progress Ring + Celebration Header */}
                    <div className={`p-5 rounded-2xl text-center ${
                      masteryLevel === 'solid' 
                        ? 'bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/30 dark:to-teal-900/30'
                        : 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20'
                    }`}>
                      {/* Animated celebration icon */}
                      <motion.div
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{ type: 'spring', damping: 12, delay: 0.1 }}
                        className="text-5xl mb-3"
                      >
                        {masteryLevel === 'solid' ? '🎉' : '🌱'}
                      </motion.div>
                      
                      <motion.h3 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className={`font-bold text-xl mb-2 ${
                          masteryLevel === 'solid' 
                            ? 'text-emerald-700 dark:text-emerald-300'
                            : 'text-blue-700 dark:text-blue-300'
                        }`}
                      >
                        {masteryLevel === 'solid' ? 'You nailed it!' : 'Great effort!'}
                      </motion.h3>
                      
                      <motion.p 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className={`text-sm ${
                          masteryLevel === 'solid'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-blue-600 dark:text-blue-400'
                        }`}
                      >
                        {masteryLevel === 'solid' 
                          ? feedback.encouragement 
                          : "Every attempt strengthens your understanding. You're building mastery! 💪"}
                      </motion.p>
                      
                      {/* XP Earned indicator */}
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.4 }}
                        className="inline-flex items-center gap-2 mt-3 px-4 py-1.5 bg-white/60 dark:bg-gray-800/60 rounded-full"
                      >
                        <span className="text-lg">⚡</span>
                        <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                          +{masteryLevel === 'solid' ? '15' : hasGaps ? '5' : '10'} XP earned
                        </span>
                      </motion.div>
                    </div>

                    {/* What you understood - Only show if they actually understood something meaningful */}
                    {feedback.understood?.length > 0 && !feedback.understood.every(p => p.toLowerCase().includes('attempt')) && (
                      <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border border-emerald-200 dark:border-emerald-800"
                      >
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xl">✨</span>
                          <h4 className="font-semibold text-emerald-800 dark:text-emerald-200">What's clicking</h4>
                        </div>
                        <ul className="space-y-2">
                          {feedback.understood.map((point, i) => (
                            <li key={i} className="flex items-start gap-2 text-emerald-700 dark:text-emerald-300 text-sm">
                              <span className="text-emerald-500 mt-0.5">✓</span>
                              <span>{point}</span>
                            </li>
                          ))}
                        </ul>
                      </motion.div>
                    )}

                    {/* Areas to strengthen - Reframed as "Let's explore" with softer language */}
                    {hasGaps && (
                      <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800"
                      >
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xl">🧭</span>
                          <h4 className="font-semibold text-indigo-800 dark:text-indigo-200">Let's explore together</h4>
                        </div>
                        <ul className="space-y-2">
                          {feedback.gaps.map((gap, i) => {
                            // Soften harsh language
                            let softenedGap = gap
                              .replace(/doesn't match/gi, "could connect better to")
                              .replace(/random words/gi, "ideas that need organizing")
                              .replace(/lacks coherence/gi, "need a clearer flow")
                              .replace(/incorrect/gi, "could be refined")
                              .replace(/wrong/gi, "worth revisiting");
                            
                            return (
                              <li key={i} className="flex items-start gap-2 text-indigo-700 dark:text-indigo-300 text-sm">
                                <span className="text-indigo-400 mt-0.5">→</span>
                                <span>{softenedGap}</span>
                              </li>
                            );
                          })}
                        </ul>
                      </motion.div>
                    )}

                    {/* Actionable Next Step - Make it prominent! */}
                    {feedback.tip && (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 rounded-xl border-2 border-amber-300 dark:border-amber-700"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">🎯</span>
                          <div>
                            <h4 className="font-semibold text-amber-800 dark:text-amber-200 mb-1">Your next move</h4>
                            <p className="text-amber-700 dark:text-amber-300 text-sm">
                              {feedback.tip}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Encouraging message for students who struggled */}
                    {hasGaps && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="text-center py-2"
                      >
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          💙 Remember: The best learners explain things multiple times. Each try makes you stronger!
                        </p>
                      </motion.div>
                    )}

                    {/* Action buttons - Clearer hierarchy */}
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 }}
                      className="flex flex-col gap-3 pt-2"
                    >
                      {hasGaps ? (
                        <>
                          {/* Primary: Try Again - Make it inviting, not punitive */}
                          <button
                            onClick={handleTryAgain}
                            className="flex items-center justify-center gap-2 w-full px-5 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white rounded-xl font-semibold transition-all shadow-lg shadow-indigo-200 dark:shadow-none"
                          >
                            <span>🚀</span>
                            Give it another shot
                          </button>
                          
                          {/* Secondary: Review */}
                          <button
                            onClick={onClose}
                            className="flex items-center justify-center gap-2 w-full px-5 py-2.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-colors"
                          >
                            Review the explanation first
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                            </svg>
                          </button>
                        </>
                      ) : (
                        <>
                          {/* When they did well - Celebrate! */}
                          <button
                            onClick={onClose}
                            className="flex items-center justify-center gap-2 w-full px-5 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-xl font-semibold transition-all shadow-lg shadow-emerald-200 dark:shadow-none"
                          >
                            <span>🎉</span>
                            Awesome! Keep learning
                          </button>
                          
                          <button
                            onClick={handleTryAgain}
                            className="flex items-center justify-center gap-2 w-full px-5 py-2.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 font-medium transition-colors"
                          >
                            Practice again anyway
                          </button>
                        </>
                      )}
                    </motion.div>
                  </div>
                )}
              </div>

              {/* FOOTER */}
              <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
                <p className="text-xs text-center text-gray-500">
                  Press <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs font-mono">Esc</kbd> to close
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );

  // Render via portal to document.body
  return createPortal(modalContent, document.body);
};

export default TeachMeBackModal;
