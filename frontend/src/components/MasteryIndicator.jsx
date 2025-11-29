/**
 * MasteryIndicator - Shows student's mastery level for topics
 * 
 * Part of the Cognitive OS - visual feedback on learning progress.
 */

import React from 'react';

/**
 * Get color based on mastery level
 */
function getMasteryColor(mastery) {
  if (mastery >= 0.85) return { bg: 'bg-emerald-500', text: 'text-emerald-600', label: 'Mastered' };
  if (mastery >= 0.7) return { bg: 'bg-blue-500', text: 'text-blue-600', label: 'Strong' };
  if (mastery >= 0.5) return { bg: 'bg-amber-500', text: 'text-amber-600', label: 'Learning' };
  if (mastery >= 0.3) return { bg: 'bg-orange-500', text: 'text-orange-600', label: 'Building' };
  return { bg: 'bg-gray-400', text: 'text-gray-500', label: 'Starting' };
}

/**
 * Circular progress indicator
 */
export function MasteryCircle({ mastery, size = 'md', showLabel = true }) {
  const { bg, text, label } = getMasteryColor(mastery);
  const percentage = Math.round(mastery * 100);
  
  const sizes = {
    sm: { outer: 'w-12 h-12', inner: 'w-8 h-8', text: 'text-xs' },
    md: { outer: 'w-16 h-16', inner: 'w-12 h-12', text: 'text-sm' },
    lg: { outer: 'w-24 h-24', inner: 'w-20 h-20', text: 'text-lg' }
  };
  
  const s = sizes[size] || sizes.md;
  
  // Calculate stroke dasharray for circular progress
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - mastery);
  
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`relative ${s.outer}`}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            className={text}
            style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
          />
        </svg>
        {/* Percentage text */}
        <div className={`absolute inset-0 flex items-center justify-center ${s.text} font-semibold ${text}`}>
          {percentage}%
        </div>
      </div>
      {showLabel && (
        <span className={`text-xs font-medium ${text}`}>{label}</span>
      )}
    </div>
  );
}

/**
 * Horizontal progress bar
 */
export function MasteryBar({ mastery, label, showPercentage = true, className = '' }) {
  const { bg, text } = getMasteryColor(mastery);
  const percentage = Math.round(mastery * 100);
  
  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-700">{label}</span>
        {showPercentage && (
          <span className={`text-sm font-medium ${text}`}>{percentage}%</span>
        )}
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${bg} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Subject mastery card
 */
export function SubjectMasteryCard({ subject, topics, overallMastery }) {
  const { text, label } = getMasteryColor(overallMastery);
  
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">{subject}</h3>
        <MasteryCircle mastery={overallMastery} size="sm" showLabel={false} />
      </div>
      
      <div className="space-y-2">
        {topics.slice(0, 3).map((topic, idx) => (
          <MasteryBar 
            key={idx}
            label={topic.name}
            mastery={topic.mastery}
          />
        ))}
      </div>
      
      {topics.length > 3 && (
        <p className="text-xs text-gray-400 mt-2">
          +{topics.length - 3} more topics
        </p>
      )}
    </div>
  );
}

/**
 * Compact mastery indicator for chat interface
 */
export function MasteryBadge({ mastery, topic }) {
  const { bg, text, label } = getMasteryColor(mastery);
  const percentage = Math.round(mastery * 100);
  
  return (
    <div 
      className="inline-flex items-center gap-2 px-2.5 py-1.5 bg-gray-50 rounded-lg border border-gray-100"
      title={`Your mastery of ${topic}: ${percentage}%`}
    >
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${bg}`} />
        <span className="text-xs text-gray-600">{topic}</span>
      </div>
      <span className={`text-xs font-medium ${text}`}>{percentage}%</span>
    </div>
  );
}

/**
 * Learning streak indicator
 */
export function LearningStreak({ days, currentStreak }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-100">
      <span className="text-2xl">🔥</span>
      <div>
        <p className="font-semibold text-amber-700">{currentStreak} Day Streak!</p>
        <p className="text-xs text-amber-600">Keep learning to maintain your streak</p>
      </div>
    </div>
  );
}

/**
 * Quick stats row
 */
export function LearningStats({ stats }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="text-center p-3 bg-blue-50 rounded-lg">
        <p className="text-2xl font-bold text-blue-600">{stats.conceptsLearned || 0}</p>
        <p className="text-xs text-blue-500">Concepts Learned</p>
      </div>
      <div className="text-center p-3 bg-emerald-50 rounded-lg">
        <p className="text-2xl font-bold text-emerald-600">{stats.topicsMastered || 0}</p>
        <p className="text-xs text-emerald-500">Topics Mastered</p>
      </div>
      <div className="text-center p-3 bg-purple-50 rounded-lg">
        <p className="text-2xl font-bold text-purple-600">{stats.studyMinutes || 0}</p>
        <p className="text-xs text-purple-500">Study Minutes</p>
      </div>
    </div>
  );
}

export default MasteryCircle;

