/**
 * Mastery Indicator Component
 * Shows student's learning progress and mastery levels
 * Part of the Memory System UI
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  BookOpen, 
  Target, 
  ChevronDown,
  Brain,
  Sparkles,
  AlertCircle
} from 'lucide-react';

const MasteryIndicator = ({
  mastery = {},
  recentTopics = [],
  weakAreas = [],
  onTopicClick,
  compact = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Calculate overall mastery percentage
  const masteryValues = Object.values(mastery);
  const overallMastery = masteryValues.length > 0
    ? Math.round(masteryValues.reduce((a, b) => a + b, 0) / masteryValues.length)
    : 0;
  
  // Get mastery level label and color
  const getMasteryLevel = (percent) => {
    if (percent >= 80) return { label: 'Expert', color: 'emerald', emoji: '🏆' };
    if (percent >= 60) return { label: 'Proficient', color: 'blue', emoji: '📈' };
    if (percent >= 40) return { label: 'Developing', color: 'amber', emoji: '🌱' };
    return { label: 'Beginner', color: 'violet', emoji: '🚀' };
  };
  
  const level = getMasteryLevel(overallMastery);
  
  const colorClasses = {
    emerald: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
      bar: 'bg-emerald-500'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-700',
      bar: 'bg-blue-500'
    },
    amber: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-700',
      bar: 'bg-amber-500'
    },
    violet: {
      bg: 'bg-violet-50',
      border: 'border-violet-200',
      text: 'text-violet-700',
      bar: 'bg-violet-500'
    }
  };
  
  const colors = colorClasses[level.color];
  
  if (compact) {
    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        className={`flex items-center gap-2 px-3 py-1.5 ${colors.bg} border ${colors.border} rounded-lg cursor-pointer`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Brain className={`w-4 h-4 ${colors.text}`} />
        <span className={`text-sm font-semibold ${colors.text}`}>
          {overallMastery}%
        </span>
        <span className="text-xs">{level.emoji}</span>
      </motion.div>
    );
  }
  
  return (
    <div className={`rounded-xl overflow-hidden border ${colors.border}`}>
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full flex items-center justify-between p-4 ${colors.bg} transition-colors hover:opacity-90`}
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl ${colors.bar} flex items-center justify-center text-white`}>
            <Brain className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className={`font-semibold ${colors.text}`}>
                Learning Progress
              </span>
              <span>{level.emoji}</span>
            </div>
            <p className="text-xs text-gray-500">
              {level.label} • {overallMastery}% mastery
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Progress ring */}
          <div className="relative w-12 h-12">
            <svg className="w-12 h-12 transform -rotate-90">
              <circle
                cx="24"
                cy="24"
                r="20"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
                className="text-gray-200"
              />
              <circle
                cx="24"
                cy="24"
                r="20"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
                strokeDasharray={`${overallMastery * 1.26} 126`}
                className={colors.text}
                strokeLinecap="round"
              />
            </svg>
            <span className={`absolute inset-0 flex items-center justify-center text-xs font-bold ${colors.text}`}>
              {overallMastery}%
            </span>
          </div>
          
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-5 h-5 text-gray-400" />
          </motion.div>
        </div>
      </button>
      
      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 bg-white border-t border-gray-100 space-y-4">
              {/* Subject Mastery Bars */}
              {Object.entries(mastery).length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Subject Mastery
                  </h4>
                  {Object.entries(mastery).map(([subject, percent]) => {
                    const subjectLevel = getMasteryLevel(percent);
                    return (
                      <div key={subject} className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">{subject}</span>
                          <span className={`font-medium ${colorClasses[subjectLevel.color].text}`}>
                            {percent}%
                          </span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percent}%` }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className={`h-full ${colorClasses[subjectLevel.color].bar} rounded-full`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              
              {/* Weak Areas */}
              {weakAreas.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Focus Areas
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {weakAreas.map((topic, idx) => (
                      <button
                        key={idx}
                        onClick={() => onTopicClick?.(topic)}
                        className="px-3 py-1.5 bg-amber-50 text-amber-700 text-sm font-medium rounded-lg border border-amber-200 hover:bg-amber-100 transition-colors"
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Recent Topics */}
              {recentTopics.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Recently Studied
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {recentTopics.slice(0, 5).map((topic, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Empty state */}
              {Object.keys(mastery).length === 0 && weakAreas.length === 0 && recentTopics.length === 0 && (
                <div className="text-center py-4 text-gray-500">
                  <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Keep learning to build your profile!</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MasteryIndicator;

