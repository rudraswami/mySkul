/**
 * 🧠 NuroSpark Neural Thinking Indicator
 * =======================================
 * 
 * A premium, compact thinking animation that represents AI cognitive processing.
 * Follows NuroSpark brand identity: neural ignition aesthetic.
 * 
 * Design Principles:
 * - No emoji faces or cartoon visuals
 * - Compact horizontal element (max 32px height)
 * - 3-5 dots with neural-style motion (pulse, wave, connect, spark)
 * - Brand colors with soft glow
 * - Organic animation timing (0.3s-1.2s variance)
 */

import React, { useMemo } from 'react';
import './NeuralThinkingIndicator.css';

// NuroSpark Brand Colors
const BRAND_COLORS = {
  electricBlue: '#2F6BFF',
  sparkPurple: '#7A42FF',
  neonYellow: '#FFD438'
};

/**
 * Neural Thinking Indicator - Compact inline version
 * Use this directly below the AI response area
 */
export function NeuralThinkingIndicator({ isLoading = true, variant = 'default' }) {
  // Generate unique animation delays for organic feel
  const animationDelays = useMemo(() => {
    return [0, 0.15, 0.3, 0.45, 0.6].map(base => base + Math.random() * 0.1);
  }, []);

  if (!isLoading) return null;

  return (
    <div className="neural-thinking-container" role="status" aria-label="AI is processing">
      <div className={`neural-thinking-indicator neural-thinking--${variant}`}>
        {/* Neural dots with staggered animations */}
        <div className="neural-dots">
          {[0, 1, 2, 3, 4].map((index) => (
            <span
              key={index}
              className={`neural-dot neural-dot--${index}`}
              style={{
                '--delay': `${animationDelays[index]}s`,
                '--color-primary': index % 2 === 0 ? BRAND_COLORS.electricBlue : BRAND_COLORS.sparkPurple,
                '--color-accent': BRAND_COLORS.neonYellow
              }}
            />
          ))}
        </div>
        
        {/* Neural connection lines (spark effect) */}
        <div className="neural-connections">
          <span className="neural-spark neural-spark--1" />
          <span className="neural-spark neural-spark--2" />
        </div>
      </div>
      
      {/* Screen reader text */}
      <span className="sr-only">AI is thinking</span>
    </div>
  );
}

/**
 * Neural Pulse Indicator - Alternative minimal version
 * 3 dots with pulse-wave motion
 */
export function NeuralPulseIndicator({ isLoading = true }) {
  if (!isLoading) return null;

  return (
    <div className="neural-pulse-container" role="status" aria-label="Processing">
      <div className="neural-pulse-indicator">
        <span className="neural-pulse-dot" style={{ '--i': 0 }} />
        <span className="neural-pulse-dot" style={{ '--i': 1 }} />
        <span className="neural-pulse-dot" style={{ '--i': 2 }} />
      </div>
    </div>
  );
}

/**
 * Neural Flicker Indicator - Subtle neural network style
 * Shows intelligent processing with connection flickers
 */
export function NeuralFlickerIndicator({ isLoading = true }) {
  if (!isLoading) return null;

  return (
    <div className="neural-flicker-container" role="status" aria-label="AI processing">
      <div className="neural-flicker-indicator">
        <span className="neural-node neural-node--active" />
        <span className="neural-link" />
        <span className="neural-node" />
        <span className="neural-link" />
        <span className="neural-node" />
        <span className="neural-link" />
        <span className="neural-node neural-node--active" />
      </div>
    </div>
  );
}

/**
 * Neural Spark Indicator - Most compact version
 * Electric spark effect with brand colors
 */
export function NeuralSparkIndicator({ isLoading = true, size = 'default' }) {
  if (!isLoading) return null;

  const sizeClass = size === 'small' ? 'neural-spark-indicator--sm' : '';

  return (
    <div className="neural-spark-container" role="status" aria-label="Thinking">
      <div className={`neural-spark-indicator ${sizeClass}`}>
        <span className="spark-core" />
        <span className="spark-ring spark-ring--1" />
        <span className="spark-ring spark-ring--2" />
        <span className="spark-ring spark-ring--3" />
      </div>
    </div>
  );
}

// Default export
export default NeuralThinkingIndicator;
