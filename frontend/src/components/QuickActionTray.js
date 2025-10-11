/**
 * QuickActionTray Component
 * Enhanced action buttons with animations and micro-interactions
 */
import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  Target, 
  Copy, 
  ThumbsUp, 
  ThumbsDown,
  Sparkles,
  Eye,
  RefreshCw,
  Play
} from 'lucide-react';

const QuickActionTray = ({ 
  responseData,
  onSaveToNotes,
  onPracticeSimilar,
  onExplainDifferently,
  onShowVisual,
  onCopyResponse,
  onFeedback,
  className = ''
}) => {
  const [actionStates, setActionStates] = useState({});
  const [showConfetti, setShowConfetti] = useState(false);

  // Handle action with animation feedback
  const handleAction = useCallback(async (actionType, actionFn) => {
    if (!actionFn) return;

    setActionStates(prev => ({ 
      ...prev, 
      [actionType]: { loading: true, success: false } 
    }));

    try {
      await actionFn(responseData);
      
      setActionStates(prev => ({ 
        ...prev, 
        [actionType]: { loading: false, success: true } 
      }));

      // Show success feedback
      if (actionType === 'save' || actionType === 'copy') {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 1000);
      }

      // Reset success state after animation
      setTimeout(() => {
        setActionStates(prev => ({ 
          ...prev, 
          [actionType]: { loading: false, success: false } 
        }));
      }, 2000);

    } catch (error) {
      console.error(`Action ${actionType} failed:`, error);
      setActionStates(prev => ({ 
        ...prev, 
        [actionType]: { loading: false, success: false, error: true } 
      }));
    }
  }, [responseData]);

  // Action definitions
  const actions = [
    {
      id: 'save',
      label: 'Save to Notes',
      icon: BookOpen,
      onClick: () => handleAction('save', onSaveToNotes),
      color: 'blue',
      description: 'Auto-tag topic + difficulty'
    },
    {
      id: 'practice',
      label: 'Practice Similar',
      icon: Target,
      onClick: () => handleAction('practice', onPracticeSimilar),
      color: 'green',
      description: '3-question quiz modal',
      glow: true // Special glow effect
    },
    {
      id: 'explain',
      label: 'Explain Differently',
      icon: RefreshCw,
      onClick: () => handleAction('explain', onExplainDifferently),
      color: 'purple',
      description: 'Alternative explanation'
    },
    {
      id: 'visual',
      label: 'Show Visual',
      icon: Eye,
      onClick: () => handleAction('visual', onShowVisual),
      color: 'amber',
      description: 'Enhanced concept visual'
    },
    {
      id: 'copy',
      label: 'Copy',
      icon: Copy,
      onClick: () => handleAction('copy', onCopyResponse),
      color: 'gray',
      description: 'Copy response'
    }
  ];

  // Color configurations
  const getColorClasses = (color, state = {}) => {
    const { loading, success, error } = state;
    
    if (success) {
      return {
        bg: 'bg-green-100',
        border: 'border-green-300',
        text: 'text-green-700',
        icon: 'text-green-600'
      };
    }
    
    if (error) {
      return {
        bg: 'bg-red-100',
        border: 'border-red-300',
        text: 'text-red-700',
        icon: 'text-red-600'
      };
    }

    if (loading) {
      return {
        bg: 'bg-gray-100',
        border: 'border-gray-300',
        text: 'text-gray-700',
        icon: 'text-gray-600'
      };
    }

    const colorMap = {
      blue: {
        bg: 'bg-blue-50 hover:bg-blue-100',
        border: 'border-blue-200 hover:border-blue-300',
        text: 'text-blue-700',
        icon: 'text-blue-600'
      },
      green: {
        bg: 'bg-green-50 hover:bg-green-100',
        border: 'border-green-200 hover:border-green-300',
        text: 'text-green-700',
        icon: 'text-green-600'
      },
      purple: {
        bg: 'bg-purple-50 hover:bg-purple-100',
        border: 'border-purple-200 hover:border-purple-300',
        text: 'text-purple-700',
        icon: 'text-purple-600'
      },
      amber: {
        bg: 'bg-amber-50 hover:bg-amber-100',
        border: 'border-amber-200 hover:border-amber-300',
        text: 'text-amber-700',
        icon: 'text-amber-600'
      },
      gray: {
        bg: 'bg-gray-50 hover:bg-gray-100',
        border: 'border-gray-200 hover:border-gray-300',
        text: 'text-gray-700',
        icon: 'text-gray-600'
      }
    };

    return colorMap[color] || colorMap.gray;
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        staggerChildren: 0.1
      }
    }
  };

  const actionVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  const glowVariants = {
    glow: {
      boxShadow: [
        "0 0 0px rgba(34, 197, 94, 0)",
        "0 0 20px rgba(34, 197, 94, 0.4)",
        "0 0 0px rgba(34, 197, 94, 0)"
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className={`bg-white rounded-xl border border-gray-200 p-4 shadow-sm ${className}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-gray-800 flex items-center">
            <Sparkles className="w-4 h-4 mr-2 text-purple-500" />
            Quick Actions
          </h4>
          
          {/* Feedback Buttons */}
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onFeedback?.(true)}
              className="p-1.5 rounded-lg bg-green-50 hover:bg-green-100 text-green-600 transition-colors"
              title="Helpful"
            >
              <ThumbsUp className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onFeedback?.(false)}
              className="p-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 transition-colors"
              title="Not helpful"
            >
              <ThumbsDown className="w-4 h-4" />
            </motion.button>
          </div>
        </div>

        {/* Action Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {actions.map((action) => {
            const state = actionStates[action.id] || {};
            const colors = getColorClasses(action.color, state);
            const ActionIcon = action.icon;

            return (
              <motion.button
                key={action.id}
                variants={actionVariants}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                animate={action.glow && !state.loading ? "glow" : ""}
                variants={action.glow ? glowVariants : actionVariants}
                onClick={action.onClick}
                disabled={state.loading}
                className={`
                  relative p-3 rounded-xl border transition-all duration-200
                  ${colors.bg} ${colors.border} ${colors.text}
                  disabled:opacity-50 disabled:cursor-not-allowed
                  group
                `}
                title={action.description}
              >
                {/* Loading Spinner */}
                {state.loading && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className={`absolute inset-0 flex items-center justify-center ${colors.icon}`}
                  >
                    <RefreshCw className="w-4 h-4" />
                  </motion.div>
                )}

                {/* Success Checkmark */}
                {state.success && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute inset-0 flex items-center justify-center text-green-600"
                  >
                    ✓
                  </motion.div>
                )}

                {/* Normal State */}
                {!state.loading && !state.success && (
                  <>
                    <ActionIcon className={`w-4 h-4 mx-auto mb-1 ${colors.icon}`} />
                    <div className="text-xs font-medium">{action.label}</div>
                  </>
                )}

                {/* Hover Description */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                  {action.description}
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>

      {/* Confetti Animation */}
      {showConfetti && (
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0 }}
          className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center"
        >
          <div className="text-6xl animate-bounce">🎉</div>
        </motion.div>
      )}
    </>
  );
};

export default QuickActionTray;