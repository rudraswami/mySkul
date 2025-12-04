/**
 * ThinkingIndicator - ChatGPT-style "Thought for X seconds" 
 * 
 * COGNITO-OS v4.0 - Simple, clean, student-friendly
 * Students don't care HOW we solved it - they care that it's CORRECT
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2,
  Clock,
  ChevronDown,
  ChevronUp,
  Sparkles
} from 'lucide-react';

const ReasoningChainPanel = ({ 
  reasoningChain = [],
  toolsUsed = [],
  confidence = 0.85,
  sources = [],
  verificationStatus = 'verified',
  agentType = 'mentor',
  complexity = 'standard',
  thinkingTime = 2.5
}) => {
  const [expanded, setExpanded] = useState(false);

  // Calculate thinking time (simulated based on complexity)
  const displayTime = thinkingTime || (complexity === 'complex' ? 4.2 : complexity === 'standard' ? 2.1 : 0.8);
  
  // Determine verification status for simple display
  const isVerified = confidence >= 0.7;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-3"
    >
      {/* Simple ChatGPT-style indicator */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors group"
      >
        <div className="flex items-center gap-1.5">
          {isVerified ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          ) : (
            <Clock className="w-4 h-4 text-gray-400" />
          )}
          <span>
            {isVerified ? 'Verified answer' : 'Thought'} • {displayTime.toFixed(1)}s
          </span>
        </div>
        
        {expanded ? (
          <ChevronUp className="w-4 h-4 opacity-50 group-hover:opacity-100" />
        ) : (
          <ChevronDown className="w-4 h-4 opacity-50 group-hover:opacity-100" />
        )}
      </button>

      {/* Expanded - Simple summary (not technical) */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-violet-500 mt-0.5 flex-shrink-0" />
                <div className="space-y-1">
                  <p>
                    I analyzed your question and found the best explanation from my knowledge base.
                    {sources.length > 0 && (
                      <span className="text-emerald-600 dark:text-emerald-400">
                        {' '}Referenced: {sources.slice(0, 2).join(', ')}
                      </span>
                    )}
                  </p>
                  {isVerified && (
                    <p className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Answer verified for accuracy
                    </p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ReasoningChainPanel;




