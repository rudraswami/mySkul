/**
 * Simple Thinking Indicator
 * =========================
 * 
 * Three pulsing dots - clean and professional.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Simple Thinking Indicator - Three dots bouncing
 */
export function NeuralThinkingIndicator({ isLoading = false }) {
  return (
    <AnimatePresence mode="wait">
      {isLoading && (
        <motion.div
          key="thinking-indicator"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.15 }}
          className="inline-flex items-center gap-1.5 px-4 py-3 bg-gray-100 rounded-2xl"
          role="status"
          aria-label="AI is thinking"
        >
          {[0, 1, 2].map((i) => (
            <motion.span
              key={i}
              className="w-2 h-2 bg-violet-500 rounded-full"
              animate={{
                y: [0, -6, 0],
              }}
              transition={{
                duration: 0.5,
                repeat: Infinity,
                delay: i * 0.12,
                ease: 'easeInOut',
              }}
            />
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Backward compatible exports
export const AgenticThinkingIndicator = NeuralThinkingIndicator;
export const AgenticThinkingCompact = NeuralThinkingIndicator;

export default NeuralThinkingIndicator;
