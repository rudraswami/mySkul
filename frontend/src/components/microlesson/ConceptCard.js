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
      transition={{ duration: 0.3 }}
      className={`p-6 rounded-xl bg-gradient-to-br ${getGradient(sentiment)} border border-blue-100 shadow-sm mb-4`}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center shadow-sm">
            <span className="text-2xl">📘</span>
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 font-poppins">
            Concept Overview
          </h3>
          <p className="text-gray-700 leading-relaxed font-inter">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ConceptCard;