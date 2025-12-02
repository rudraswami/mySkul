/**
 * NuroSpark Neural Thinking Indicator
 * ====================================
 * 
 * Single, consistent AI cognitive processing animation.
 * Used across the entire app for thinking/loading states.
 * 
 * Brand: Electric Blue #2F6BFF, Spark Purple #7A42FF, Neon Yellow #FFD438
 * Max height: 32px | Centered | No emoji | Professional
 */

import React from 'react';
import './NeuralThinkingIndicator.css';

export function NeuralThinkingIndicator({ isLoading = true }) {
  if (!isLoading) return null;

  return (
    <div className="neural-thinking-container" role="status" aria-label="AI is processing">
      <div className="neural-thinking-indicator">
        <span className="neural-dot" style={{ '--i': 0 }} />
        <span className="neural-dot" style={{ '--i': 1 }} />
        <span className="neural-dot" style={{ '--i': 2 }} />
        <span className="neural-dot" style={{ '--i': 3 }} />
        <span className="neural-dot" style={{ '--i': 4 }} />
      </div>
      <span className="sr-only">AI is thinking</span>
    </div>
  );
}

export default NeuralThinkingIndicator;
