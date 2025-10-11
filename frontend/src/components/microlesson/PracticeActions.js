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
      transition={{ duration: 0.4, delay: 0.3 }}
      className="p-6 bg-gradient-to-r from-purple-50 via-blue-50 to-indigo-50 rounded-2xl border-2 border-purple-200"
    >
      <div className="flex items-center space-x-3 mb-5">
        <div className="w-10 h-10 rounded-lg bg-purple-500 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 font-poppins">
          Ready to Practice? 🎯
        </h3>
      </div>
      
      <div className="flex flex-wrap gap-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              whileHover={{ scale: 1.08, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => action.onClick && action.onClick(messageData)}
              className={`flex items-center space-x-2 px-5 py-3 rounded-xl border-2 transition-all shadow-md hover:shadow-lg font-semibold ${getColorClasses(action.color)}`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-base">{action.label}</span>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default PracticeActions;