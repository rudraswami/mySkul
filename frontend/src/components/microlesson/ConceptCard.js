import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';

/**
 * ConceptCard - Hero title card with gradient background for concept overview
 * AI Tutor 2.1 micro-lesson component
 */
const ConceptCard = ({ content, sentiment = 'neutral' }) => {
  const getGradient = (sentiment) => {
    const gradients = {
      confusion: 'from-orange-50 to-yellow-50',
      confidence: 'from-green-50 to-emerald-50',
      frustration: 'from-red-50 to-pink-50',
      curiosity: 'from-purple-50 to-indigo-50',
      neutral: 'from-blue-50 to-indigo-50'
    };
    return gradients[sentiment] || gradients.neutral;
  };

  if (!content) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`p-8 rounded-2xl bg-gradient-to-br ${getGradient(sentiment)} border-2 border-blue-200 shadow-lg hover:shadow-xl transition-shadow`}
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">
          <div className="w-14 h-14 rounded-xl bg-white flex items-center justify-center shadow-md">
            <span className="text-4xl">📘</span>
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 font-poppins flex items-center">
            Core Concept
            <span className="ml-2 text-2xl">✨</span>
          </h3>
          <p className="text-gray-800 leading-relaxed font-inter text-lg">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ConceptCard;