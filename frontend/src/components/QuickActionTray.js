import React from 'react';
import { motion } from 'framer-motion';
import { Bookmark, Target, RefreshCw, Image as ImageIcon, Save } from 'lucide-react';

/**
 * QuickActionTray - Context-aware quick actions for AI responses
 * Save to Notes, Practice Similar, Explain Differently, Show Visual
 */
const QuickActionTray = ({ actions, onAction, messageData }) => {
  const iconMap = {
    bookmark: Bookmark,
    target: Target,
    refresh: RefreshCw,
    image: ImageIcon,
    save: Save
  };

  const handleAction = (action) => {
    if (onAction) {
      onAction(action, messageData);
    }
  };

  if (!actions || actions.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="flex flex-wrap gap-2 mt-3"
    >
      {actions.map((action, index) => {
        const Icon = iconMap[action.icon] || Save;
        return (
          <motion.button
            key={action.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleAction(action)}
            className="flex items-center space-x-2 px-3 py-1.5 bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-gray-700 hover:text-blue-700 rounded-lg transition-all text-sm"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index }}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{action.label}</span>
          </motion.button>
        );
      })}
    </motion.div>
  );
};

export default QuickActionTray;