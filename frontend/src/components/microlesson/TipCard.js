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
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className={`p-8 rounded-2xl bg-gradient-to-br ${style.gradient} border-2 ${style.border} shadow-lg hover:shadow-xl transition-all`}
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">
          <div className="w-14 h-14 rounded-xl bg-white flex items-center justify-center shadow-md">
            <span className="text-4xl">{style.emoji}</span>
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 font-poppins flex items-center">
            <Lightbulb className="w-6 h-6 mr-2 text-yellow-500" />
            {type === 'mentor' ? 'Mentor Wisdom' : 'Pro Tip'}
            <span className="ml-2">✨</span>
          </h3>
          <p className="text-gray-800 leading-relaxed font-inter text-lg">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default TipCard;