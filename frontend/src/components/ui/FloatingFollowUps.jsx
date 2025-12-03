/**
 * Floating Follow-up Suggestions Component
 * Appears above the input area with smooth animations
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronRight, MessageCircle } from 'lucide-react';

const FloatingFollowUps = ({
  suggestions = [],
  onSuggestionClick,
  show = true,
  maxSuggestions = 3
}) => {
  const displayedSuggestions = suggestions.slice(0, maxSuggestions);

  if (!displayedSuggestions.length || !show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.2 }}
      className="px-4 py-3"
    >
      {/* Label */}
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-4 h-4 text-violet-500" />
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          Continue Learning
        </span>
      </div>
      
      {/* Suggestions */}
      <div className="flex flex-wrap gap-2">
        <AnimatePresence mode="popLayout">
          {displayedSuggestions.map((suggestion, index) => {
            const text = typeof suggestion === 'string' ? suggestion : suggestion.text;
            
            return (
              <motion.button
                key={text}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSuggestionClick?.(text)}
                className="group flex items-center gap-2 px-4 py-2.5 bg-white hover:bg-violet-50 border border-gray-200 hover:border-violet-300 rounded-full shadow-sm transition-all duration-200"
              >
                <MessageCircle className="w-3.5 h-3.5 text-gray-400 group-hover:text-violet-500 transition-colors" />
                <span className="text-sm font-medium text-gray-700 group-hover:text-violet-700 transition-colors truncate max-w-[200px]">
                  {text}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-gray-300 group-hover:text-violet-400 transition-colors" />
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default FloatingFollowUps;

