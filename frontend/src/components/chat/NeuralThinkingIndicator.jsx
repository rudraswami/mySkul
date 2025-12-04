/**
 * Neural Thinking Indicator
 * =========================
 * 
 * Shows rotating thinking messages like ChatGPT:
 * "Analyzing your question..."
 * "Checking NCERT alignment..."
 * "Preparing explanation..."
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Thinking messages that rotate
const THINKING_MESSAGES = [
  "Analyzing your question...",
  "Searching curriculum...",
  "Checking NCERT content...",
  "Preparing explanation...",
  "Verifying accuracy...",
];

/**
 * Neural Thinking Indicator - Rotating messages with dots
 */
export function NeuralThinkingIndicator({ isLoading = false, subject = '' }) {
  const [messageIndex, setMessageIndex] = useState(0);

  // Rotate messages every 1.5 seconds
  useEffect(() => {
    if (!isLoading) {
      setMessageIndex(0);
      return;
    }
    
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % THINKING_MESSAGES.length);
    }, 1500);

    return () => clearInterval(interval);
  }, [isLoading]);

  return (
    <AnimatePresence mode="wait">
      {isLoading && (
        <motion.div
          key="thinking-indicator"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 rounded-2xl border border-violet-100 dark:border-violet-800"
          role="status"
          aria-label="AI is thinking"
        >
          {/* Animated brain icon */}
          <div className="relative">
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-xl"
            >
              🧠
            </motion.div>
          </div>
          
          {/* Rotating message */}
          <AnimatePresence mode="wait">
            <motion.span
              key={messageIndex}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
              className="text-sm font-medium text-violet-700 dark:text-violet-300"
            >
              {THINKING_MESSAGES[messageIndex]}
            </motion.span>
          </AnimatePresence>
          
          {/* Pulsing dots */}
          <div className="flex items-center gap-1 ml-auto">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="w-1.5 h-1.5 bg-violet-400 rounded-full"
                animate={{
                  opacity: [0.3, 1, 0.3],
                  scale: [0.8, 1, 0.8],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2,
                  ease: 'easeInOut',
                }}
              />
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Backward compatible exports
export const AgenticThinkingIndicator = NeuralThinkingIndicator;
export const AgenticThinkingCompact = NeuralThinkingIndicator;

export default NeuralThinkingIndicator;
