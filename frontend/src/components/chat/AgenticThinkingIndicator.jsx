/**
 * 🧠 Agentic Thinking Indicator
 * =============================
 * 
 * Shows the actual agentic reasoning process:
 * - Current thinking step
 * - Tools being used
 * - Progress through ReAct loop
 * 
 * This makes the AI feel more human and transparent,
 * showing students HOW it's thinking, not just THAT it's thinking.
 * 
 * UPDATE: Now includes NuroSpark Neural Thinking Indicators
 * for premium, professional AI cognitive processing animation.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Re-export NuroSpark Neural Indicators for unified imports
export { 
  NeuralThinkingIndicator, 
  NeuralPulseIndicator, 
  NeuralFlickerIndicator,
  NeuralSparkIndicator 
} from './NeuralThinkingIndicator';

// Agentic phases with icons and descriptions
const AGENTIC_PHASES = [
  {
    id: 'understand',
    icon: '🤔',
    title: 'Understanding',
    description: 'Reading your question carefully...',
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  },
  {
    id: 'think',
    icon: '💭',
    title: 'Thinking',
    description: 'Breaking down the concept...',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200'
  },
  {
    id: 'search',
    icon: '🔍',
    title: 'Searching',
    description: 'Looking up relevant formulas and facts...',
    color: 'from-amber-500 to-orange-500',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200'
  },
  {
    id: 'calculate',
    icon: '🧮',
    title: 'Calculating',
    description: 'Running calculations to verify...',
    color: 'from-green-500 to-emerald-500',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  {
    id: 'verify',
    icon: '✅',
    title: 'Verifying',
    description: 'Double-checking the answer...',
    color: 'from-teal-500 to-cyan-500',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-200'
  },
  {
    id: 'compose',
    icon: '✍️',
    title: 'Composing',
    description: 'Writing your personalized explanation...',
    color: 'from-indigo-500 to-purple-500',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200'
  }
];

// Tool usage messages
const TOOL_MESSAGES = {
  calculator: '🧮 Using calculator to compute...',
  knowledge_search: '📚 Searching knowledge base...',
  formula_lookup: '📐 Looking up formulas...',
  fact_checker: '🔬 Verifying facts...',
  code_executor: '💻 Running code...'
};

// Fun facts to show during longer waits
const FUN_FACTS = [
  "💡 Did you know? Students who ask 'why' learn 2x faster!",
  "🎯 Top scorers spend 40% of study time on tough concepts",
  "🧠 Your brain creates new connections every time you learn!",
  "⚡ Taking short breaks actually improves memory retention",
  "🌟 Asking questions is a sign of great learners!"
];

/**
 * Main Agentic Thinking Indicator Component
 */
export function AgenticThinkingIndicator({ 
  agenticState = null,  // Real-time state from backend
  isLoading = true,
  questionType = 'general'  // 'math', 'science', 'conceptual', 'general'
}) {
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [showFunFact, setShowFunFact] = useState(false);
  const [funFactIndex, setFunFactIndex] = useState(0);
  const [completedPhases, setCompletedPhases] = useState([]);
  const [currentTool, setCurrentTool] = useState(null);

  // Get relevant phases based on question type
  const getRelevantPhases = useCallback(() => {
    const basePhases = ['understand', 'think'];
    
    switch (questionType) {
      case 'math':
        return [...basePhases, 'calculate', 'verify', 'compose'];
      case 'science':
        return [...basePhases, 'search', 'verify', 'compose'];
      case 'conceptual':
        return [...basePhases, 'search', 'compose'];
      default:
        return [...basePhases, 'search', 'compose'];
    }
  }, [questionType]);

  const relevantPhaseIds = getRelevantPhases();
  const phases = AGENTIC_PHASES.filter(p => relevantPhaseIds.includes(p.id));

  // Handle real-time agentic state updates
  useEffect(() => {
    if (agenticState) {
      // Update current phase based on real agent state
      if (agenticState.phase) {
        const phaseIndex = phases.findIndex(p => p.id === agenticState.phase);
        if (phaseIndex >= 0) {
          setCurrentPhaseIndex(phaseIndex);
          // Mark previous phases as completed
          setCompletedPhases(phases.slice(0, phaseIndex).map(p => p.id));
        }
      }
      
      // Show tool being used
      if (agenticState.tool) {
        setCurrentTool(agenticState.tool);
      }
    }
  }, [agenticState, phases]);

  // Simulated phase progression (when no real-time state)
  useEffect(() => {
    if (!agenticState && isLoading) {
      const phaseInterval = setInterval(() => {
        setCurrentPhaseIndex(prev => {
          const next = prev + 1;
          if (next < phases.length) {
            setCompletedPhases(phases.slice(0, next).map(p => p.id));
            return next;
          }
          return prev;
        });
      }, 2500);

      return () => clearInterval(phaseInterval);
    }
  }, [agenticState, isLoading, phases]);

  // Show fun fact after 6 seconds
  useEffect(() => {
    if (isLoading) {
      const funFactTimer = setTimeout(() => {
        setShowFunFact(true);
      }, 6000);

      const funFactRotator = setInterval(() => {
        setFunFactIndex(prev => (prev + 1) % FUN_FACTS.length);
      }, 4000);

      return () => {
        clearTimeout(funFactTimer);
        clearInterval(funFactRotator);
      };
    }
  }, [isLoading]);

  const currentPhase = phases[currentPhaseIndex] || phases[0];

  if (!isLoading) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex justify-start w-full max-w-2xl"
    >
      <div className={`
        relative overflow-hidden rounded-2xl shadow-lg border-2
        ${currentPhase.bgColor} ${currentPhase.borderColor}
        p-5 w-full
      `}>
        {/* Animated gradient background */}
        <div className={`
          absolute inset-0 opacity-10
          bg-gradient-to-r ${currentPhase.color}
          animate-pulse
        `} />

        {/* Main content */}
        <div className="relative z-10">
          {/* Header with brain icon and phase */}
          <div className="flex items-center gap-4 mb-4">
            {/* Animated brain/thinking icon */}
            <motion.div
              animate={{ 
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="text-4xl"
            >
              {currentPhase.icon}
            </motion.div>

            <div className="flex-1">
              <motion.h4
                key={currentPhase.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`
                  text-lg font-bold bg-gradient-to-r ${currentPhase.color}
                  bg-clip-text text-transparent
                `}
              >
                {currentPhase.title}
              </motion.h4>
              <AnimatePresence mode="wait">
                <motion.p
                  key={currentPhase.description}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="text-sm text-gray-600"
                >
                  {currentTool ? TOOL_MESSAGES[currentTool] : currentPhase.description}
                </motion.p>
              </AnimatePresence>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-2 mb-4">
            {phases.map((phase, index) => (
              <React.Fragment key={phase.id}>
                <motion.div
                  initial={false}
                  animate={{
                    scale: index === currentPhaseIndex ? 1.2 : 1,
                    backgroundColor: 
                      completedPhases.includes(phase.id) ? '#10B981' :
                      index === currentPhaseIndex ? '#8B5CF6' : '#E5E7EB'
                  }}
                  className={`
                    w-3 h-3 rounded-full transition-all duration-300
                    ${index === currentPhaseIndex ? 'ring-2 ring-purple-300 ring-offset-2' : ''}
                  `}
                />
                {index < phases.length - 1 && (
                  <div className={`
                    flex-1 h-0.5 rounded-full
                    ${completedPhases.includes(phase.id) ? 'bg-green-400' : 'bg-gray-200'}
                  `} />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Animated dots */}
          <div className="flex justify-center gap-1 mb-3">
            {[0, 1, 2].map(i => (
              <motion.div
                key={i}
                animate={{
                  y: [0, -8, 0],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: i * 0.15
                }}
                className={`
                  w-2 h-2 rounded-full
                  bg-gradient-to-r ${currentPhase.color}
                `}
              />
            ))}
          </div>

          {/* Fun fact (appears after delay) */}
          <AnimatePresence>
            {showFunFact && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-gray-200"
              >
                <AnimatePresence mode="wait">
                  <motion.p
                    key={funFactIndex}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="text-xs text-gray-500 italic text-center"
                  >
                    {FUN_FACTS[funFactIndex]}
                  </motion.p>
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Agentic badge */}
          <div className="absolute top-2 right-2">
            <span className="
              inline-flex items-center gap-1 px-2 py-0.5
              text-xs font-medium rounded-full
              bg-gradient-to-r from-purple-600 to-pink-600
              text-white shadow-sm
            ">
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
              AI Thinking
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

/**
 * Compact version for inline use
 */
export function AgenticThinkingCompact({ isLoading = true }) {
  const [dotCount, setDotCount] = useState(1);
  const [messageIndex, setMessageIndex] = useState(0);
  
  const messages = [
    "🤔 Thinking",
    "🔍 Analyzing",
    "💭 Reasoning",
    "✨ Composing"
  ];

  useEffect(() => {
    if (isLoading) {
      const dotInterval = setInterval(() => {
        setDotCount(prev => (prev % 3) + 1);
      }, 400);

      const messageInterval = setInterval(() => {
        setMessageIndex(prev => (prev + 1) % messages.length);
      }, 2000);

      return () => {
        clearInterval(dotInterval);
        clearInterval(messageInterval);
      };
    }
  }, [isLoading]);

  if (!isLoading) return null;

  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="inline-flex items-center gap-2 text-sm text-gray-600"
    >
      <motion.span
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      >
        🧠
      </motion.span>
      <span>{messages[messageIndex]}{'.'.repeat(dotCount)}</span>
    </motion.span>
  );
}

export default AgenticThinkingIndicator;



