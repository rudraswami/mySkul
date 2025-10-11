import React from 'react';
import { motion } from 'framer-motion';
import { Target, BookmarkPlus, RefreshCw, Sparkles } from 'lucide-react';

/**
 * PracticeActions - Interactive action buttons for practice and saving
 * AI Tutor 2.1 micro-lesson component
 */
const PracticeActions = ({ onTrySimilar, onSaveToNotes, onExplainDifferently, messageData }) => {
  const actions = [
    {
      id: 'try_similar',
      label: 'Try Similar',
      icon: Target,
      color: 'blue',
      onClick: onTrySimilar
    },
    {
      id: 'save_notes',
      label: 'Save to Notes',
      icon: BookmarkPlus,
      color: 'purple',
      onClick: onSaveToNotes
    },
    {
      id: 'explain_different',
      label: 'Explain Differently',
      icon: RefreshCw,
      color: 'green',
      onClick: onExplainDifferently
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200',
      purple: 'bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200',
      green: 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200'
    };
    return colors[color] || colors.blue;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 }}
      className="mb-4"
    >
      <div className="flex items-center space-x-2 mb-3">
        <Sparkles className="w-4 h-4 text-purple-600" />
        <h3 className="text-sm font-semibold text-gray-700 font-poppins">
          Quick Practice
        </h3>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => action.onClick && action.onClick(messageData)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-all ${getColorClasses(action.color)}`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{action.label}</span>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default PracticeActions;