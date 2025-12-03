/**
 * Loading State Components
 * Skeleton loaders and spinners for various UI states
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Brain, Sparkles } from 'lucide-react';

// Shimmer animation keyframes
const shimmerAnimation = {
  initial: { backgroundPosition: '-200% 0' },
  animate: { backgroundPosition: '200% 0' },
  transition: { 
    duration: 1.5, 
    repeat: Infinity, 
    ease: 'linear' 
  }
};

/**
 * Skeleton Text - For loading text content
 */
export const SkeletonText = ({ lines = 3, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <motion.div
        key={i}
        className="h-4 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
        style={{
          backgroundSize: '200% 100%',
          width: i === lines - 1 ? '60%' : '100%'
        }}
        {...shimmerAnimation}
      />
    ))}
  </div>
);

/**
 * Skeleton Card - For loading card content
 */
export const SkeletonCard = ({ className = '' }) => (
  <div className={`rounded-2xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-6 ${className}`}>
    <div className="flex items-start gap-4 mb-4">
      <motion.div
        className="w-12 h-12 rounded-xl bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
        style={{ backgroundSize: '200% 100%' }}
        {...shimmerAnimation}
      />
      <div className="flex-1 space-y-2">
        <motion.div
          className="h-4 w-32 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
          style={{ backgroundSize: '200% 100%' }}
          {...shimmerAnimation}
        />
        <motion.div
          className="h-3 w-24 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
          style={{ backgroundSize: '200% 100%' }}
          {...shimmerAnimation}
        />
      </div>
    </div>
    <SkeletonText lines={4} />
  </div>
);

/**
 * Skeleton Chat Item - For loading chat history items
 */
export const SkeletonChatItem = () => (
  <div className="p-3 rounded-lg">
    <div className="flex items-start gap-3">
      <motion.div
        className="w-9 h-9 rounded-lg bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 flex-shrink-0"
        style={{ backgroundSize: '200% 100%' }}
        {...shimmerAnimation}
      />
      <div className="flex-1 space-y-2">
        <motion.div
          className="h-4 w-full rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
          style={{ backgroundSize: '200% 100%' }}
          {...shimmerAnimation}
        />
        <div className="flex items-center gap-2">
          <motion.div
            className="h-3 w-16 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
            style={{ backgroundSize: '200% 100%' }}
            {...shimmerAnimation}
          />
          <motion.div
            className="h-3 w-12 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700"
            style={{ backgroundSize: '200% 100%' }}
            {...shimmerAnimation}
          />
        </div>
      </div>
    </div>
  </div>
);

/**
 * AI Thinking Indicator - Premium animated loading for AI responses
 */
export const AIThinkingIndicator = ({ text = 'Thinking...' }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="flex items-center gap-3 p-4"
  >
    <div className="relative">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/30"
      >
        <Brain className="w-5 h-5 text-white" />
      </motion.div>
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="absolute inset-0 rounded-xl bg-violet-500 blur-md -z-10"
      />
    </div>
    <div className="flex flex-col">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
        {text}
      </span>
      <div className="flex items-center gap-1 mt-1">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.4, 1, 0.4]
            }}
            transition={{ 
              duration: 0.6, 
              repeat: Infinity, 
              delay: i * 0.15 
            }}
            className="w-1.5 h-1.5 rounded-full bg-violet-500"
          />
        ))}
      </div>
    </div>
  </motion.div>
);

/**
 * Spinner - Simple loading spinner
 */
export const Spinner = ({ 
  size = 'md', 
  color = 'violet',
  className = '' 
}) => {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-10 h-10 border-3'
  };

  const colors = {
    violet: 'border-violet-500',
    gray: 'border-gray-500',
    white: 'border-white'
  };

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={`rounded-full border-gray-200 dark:border-gray-700 ${sizes[size]} ${className}`}
      style={{ borderTopColor: colors[color]?.split('-')[1] || 'violet' }}
    />
  );
};

/**
 * Button Loading State
 */
export const ButtonLoader = () => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
  >
    <Loader2 className="w-4 h-4" />
  </motion.div>
);

/**
 * Full Page Loading
 */
export const FullPageLoader = ({ text = 'Loading...' }) => (
  <div className="fixed inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50 flex items-center justify-center">
    <div className="text-center">
      <motion.div
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: [0, 5, -5, 0]
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: 'easeInOut'
        }}
        className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-violet-500/30"
      >
        <Sparkles className="w-8 h-8 text-white" />
      </motion.div>
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
        {text}
      </p>
    </div>
  </div>
);

export default {
  SkeletonText,
  SkeletonCard,
  SkeletonChatItem,
  AIThinkingIndicator,
  Spinner,
  ButtonLoader,
  FullPageLoader
};

