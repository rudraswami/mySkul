import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb } from 'lucide-react';

/**
 * TipCard - Mentor-tone card with motivational text
 * AI Tutor 2.1 micro-lesson component
 */
const TipCard = ({ content, type = 'mentor' }) => {
  if (!content) return null;

  const getCardStyle = (type) => {
    if (type === 'mentor') {
      return {
        gradient: 'from-green-50 to-emerald-50',
        border: 'border-green-100',
        emoji: '💬'
      };
    }
    return {
      gradient: 'from-amber-50 to-yellow-50',
      border: 'border-amber-100',
      emoji: '💡'
    };
  };

  const style = getCardStyle(type);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className={`p-6 rounded-xl bg-gradient-to-br ${style.gradient} border ${style.border} shadow-sm mb-4`}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center shadow-sm">
            <span className="text-2xl">{style.emoji}</span>
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 font-poppins flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
            {type === 'mentor' ? 'Mentor Tip' : 'Pro Tip'}
          </h3>
          <p className="text-gray-700 leading-relaxed font-inter">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default TipCard;