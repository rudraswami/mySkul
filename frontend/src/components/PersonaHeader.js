import React from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, Heart } from 'lucide-react';

/**
 * PersonaHeader - Displays adaptive persona blend for AI Tutor 2.0
 * Shows Professor/Mentor weight distribution with animated visual indicator
 */
const PersonaHeader = ({ personaBlend, sentimentAnalysis }) => {
  const professorWeight = personaBlend?.professor || 0.5;
  const mentorWeight = personaBlend?.mentor || 0.5;
  
  const getToneGradient = (sentiment) => {
    const gradients = {
      confusion: 'from-orange-400 to-yellow-400',
      confidence: 'from-green-400 to-emerald-400',
      frustration: 'from-red-400 to-pink-400',
      curiosity: 'from-purple-400 to-indigo-400'
    };
    return gradients[sentiment] || 'from-blue-400 to-indigo-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Adaptive Learning Mode</span>
          {sentimentAnalysis?.primary_sentiment && (
            <span className="text-xs px-2 py-0.5 bg-white rounded-full text-gray-600">
              {sentimentAnalysis.primary_sentiment}
            </span>
          )}
        </div>
      </div>

      {/* Persona Blend Indicator */}
      <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: '50%' }}
          animate={{ width: `${professorWeight * 100}%` }}
          transition={{ duration: 0.5 }}
          className={`h-full bg-gradient-to-r ${getToneGradient(sentimentAnalysis?.primary_sentiment)}`}
        />
      </div>

      {/* Labels */}
      <div className="flex items-center justify-between mt-2 text-xs">
        <div className="flex items-center space-x-1">
          <GraduationCap className="w-3 h-3 text-blue-600" />
          <span className="text-gray-600">Professor {Math.round(professorWeight * 100)}%</span>
        </div>
        <div className="flex items-center space-x-1">
          <Heart className="w-3 h-3 text-pink-500" />
          <span className="text-gray-600">Mentor {Math.round(mentorWeight * 100)}%</span>
        </div>
      </div>
    </motion.div>
  );
};

export default PersonaHeader;