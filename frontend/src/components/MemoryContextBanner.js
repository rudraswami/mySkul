/**
 * Memory Context Banner
 * Displays student's learning context (mastery, continuation, weak topics)
 * Makes memory system visible and valuable to students
 */
import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Link2, AlertCircle, Sparkles } from 'lucide-react';

export default function MemoryContextBanner({ memoryContext }) {
  if (!memoryContext) return null;
  
  const {
    mastery_level = 0,
    mastery_bucket = 'beginner',
    is_continuation = false,
    last_topic = '',
    weak_topics = []
  } = memoryContext;
  
  // Don't show if no meaningful context
  if (mastery_level === 0 && !is_continuation && weak_topics.length === 0) {
    return null;
  }
  
  // Mastery color coding
  const getMasteryColor = (level) => {
    if (level < 30) return 'from-red-500 to-orange-500';
    if (level < 70) return 'from-yellow-500 to-amber-500';
    return 'from-green-500 to-emerald-500';
  };
  
  const getMasteryLabel = (bucket) => {
    const labels = {
      beginner: '🌱 Building Foundation',
      intermediate: '📈 Growing Strong',
      advanced: '🚀 Mastery Level'
    };
    return labels[bucket] || '📚 Learning';
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 space-y-2"
    >
      {/* Mastery Level Indicator */}
      {mastery_level > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-bold text-gray-900">
                Your Progress
              </span>
            </div>
            <span className="text-xs font-semibold text-purple-600">
              {getMasteryLabel(mastery_bucket)}
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${mastery_level}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={`h-full bg-gradient-to-r ${getMasteryColor(mastery_level)}`}
            />
          </div>
          
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-600">
              Mastery Level: <span className="font-bold text-gray-900">{mastery_level}/100</span>
            </span>
            <span className="text-xs text-gray-500">
              {mastery_level < 30 && 'Keep practicing! 💪'}
              {mastery_level >= 30 && mastery_level < 70 && 'Great progress! 🎯'}
              {mastery_level >= 70 && 'You\'re crushing it! 🔥'}
            </span>
          </div>
        </div>
      )}
      
      {/* Continuation Banner */}
      {is_continuation && last_topic && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-3 flex items-center gap-3"
        >
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Link2 className="h-4 w-4 text-blue-600" />
            </div>
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-900">
              Continuing from last time
            </p>
            <p className="text-xs text-gray-600 mt-0.5">
              We were discussing: <span className="font-bold text-blue-700">{last_topic.replace(/_/g, ' ')}</span>
            </p>
          </div>
        </motion.div>
      )}
      
      {/* Weak Topics Suggestion */}
      {weak_topics.length > 0 && mastery_level > 0 && mastery_level < 50 && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-3 flex items-center gap-3"
        >
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
              <AlertCircle className="h-4 w-4 text-amber-600" />
            </div>
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-900">
              💡 Suggested Practice
            </p>
            <p className="text-xs text-gray-600 mt-0.5">
              Need more practice: <span className="font-bold text-amber-700">
                {weak_topics.slice(0, 2).map(t => t.replace(/_/g, ' ')).join(', ')}
              </span>
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

