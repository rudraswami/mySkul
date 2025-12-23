/**
 * ContextPanel - Right-side learning context panel for Sathi
 * Shows session progress, tips, and suggestions
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  BookOpen, 
  Clock, 
  Target, 
  Lightbulb,
  TrendingUp,
  ChevronRight
} from 'lucide-react';

// Topic Card in Context
const TopicTag = ({ topic, active }) => (
  <span 
    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mr-2 mb-2 ${
      active 
        ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' 
        : 'bg-slate-700/50 text-slate-400 border border-slate-600/30'
    }`}
  >
    {topic}
  </span>
);

// Session Progress Card
const SessionProgressCard = ({ questionsAsked = 0, topicsExplored = 0, sessionTime = '0m' }) => (
  <div className="sathi-context-card">
    <div className="flex items-center gap-2 mb-3">
      <Clock size={16} className="text-indigo-400" />
      <span className="text-sm font-medium text-slate-200">This Session</span>
    </div>
    <div className="grid grid-cols-3 gap-4 text-center">
      <div>
        <div className="text-lg font-bold text-white">{questionsAsked}</div>
        <div className="text-xs text-slate-500">Questions</div>
      </div>
      <div>
        <div className="text-lg font-bold text-white">{topicsExplored}</div>
        <div className="text-xs text-slate-500">Topics</div>
      </div>
      <div>
        <div className="text-lg font-bold text-white">{sessionTime}</div>
        <div className="text-xs text-slate-500">Time</div>
      </div>
    </div>
  </div>
);

// Quick Tips Card
const QuickTipsCard = ({ tips = [] }) => (
  <div className="sathi-context-card">
    <div className="flex items-center gap-2 mb-3">
      <Lightbulb size={16} className="text-yellow-400" />
      <span className="text-sm font-medium text-slate-200">Quick Tips</span>
    </div>
    <ul className="space-y-2">
      {tips.map((tip, index) => (
        <li key={index} className="flex items-start gap-2 text-xs text-slate-400">
          <ChevronRight size={12} className="mt-0.5 text-indigo-400 flex-shrink-0" />
          <span>{tip}</span>
        </li>
      ))}
    </ul>
  </div>
);

// Suggestions Card
const SuggestionsCard = ({ suggestions = [], onSelect }) => (
  <div className="sathi-context-card">
    <div className="flex items-center gap-2 mb-3">
      <Target size={16} className="text-green-400" />
      <span className="text-sm font-medium text-slate-200">Try Asking</span>
    </div>
    <div className="space-y-2">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onSelect?.(suggestion)}
          className="w-full text-left px-3 py-2 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 
                     text-xs text-slate-300 hover:text-white transition-colors border border-transparent
                     hover:border-indigo-500/30"
        >
          {suggestion}
        </button>
      ))}
    </div>
  </div>
);

// Main Context Panel
const ContextPanel = ({ 
  isOpen, 
  onClose, 
  currentTopics = [],
  sessionStats = {},
  onSuggestionSelect 
}) => {
  const defaultTips = [
    "Ask 'explain like I'm 5' for simpler explanations",
    "Request cricket analogies for complex concepts",
    "Say 'test me' for quick knowledge checks",
    "Ask for step-by-step solutions to problems"
  ];

  const defaultSuggestions = [
    "Can you explain this with an example?",
    "What's the intuition behind this?",
    "Give me a practice problem",
    "Summarize what we've covered"
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="sathi-context-panel open"
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        >
          <div className="sathi-context-header">
            <h3 className="sathi-context-title">Learning Context</h3>
            <button 
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Current Topics */}
          {currentTopics.length > 0 && (
            <div className="sathi-context-section">
              <div className="sathi-context-section-title">Current Topics</div>
              <div className="flex flex-wrap">
                {currentTopics.map((topic, index) => (
                  <TopicTag key={index} topic={topic} active={index === 0} />
                ))}
              </div>
            </div>
          )}

          {/* Session Progress */}
          <div className="sathi-context-section">
            <div className="sathi-context-section-title">Progress</div>
            <SessionProgressCard {...sessionStats} />
          </div>

          {/* Quick Tips */}
          <div className="sathi-context-section">
            <div className="sathi-context-section-title">Tips</div>
            <QuickTipsCard tips={defaultTips} />
          </div>

          {/* Suggestions */}
          <div className="sathi-context-section">
            <div className="sathi-context-section-title">Suggestions</div>
            <SuggestionsCard 
              suggestions={defaultSuggestions} 
              onSelect={onSuggestionSelect} 
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ContextPanel;


