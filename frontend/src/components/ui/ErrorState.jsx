/**
 * Error State Component
 * Displays user-friendly error messages with retry option
 */
import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, MessageCircle, WifiOff } from 'lucide-react';

const errorTypes = {
  network: {
    icon: WifiOff,
    title: 'Connection Lost',
    description: 'Unable to reach the server. Please check your internet connection.',
    color: 'red'
  },
  timeout: {
    icon: AlertTriangle,
    title: 'Request Timed Out',
    description: 'The server took too long to respond. Please try again.',
    color: 'amber'
  },
  general: {
    icon: AlertTriangle,
    title: 'Something Went Wrong',
    description: 'An unexpected error occurred. Please try again.',
    color: 'red'
  },
  notFound: {
    icon: MessageCircle,
    title: 'Not Found',
    description: "The resource you're looking for doesn't exist.",
    color: 'gray'
  }
};

const ErrorState = ({
  type = 'general',
  title,
  description,
  onRetry,
  onDismiss,
  showRetry = true,
  compact = false
}) => {
  const errorConfig = errorTypes[type] || errorTypes.general;
  const Icon = errorConfig.icon;
  const displayTitle = title || errorConfig.title;
  const displayDescription = description || errorConfig.description;
  
  const colorClasses = {
    red: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      icon: 'text-red-500',
      title: 'text-red-800 dark:text-red-200',
      text: 'text-red-700 dark:text-red-300',
      button: 'bg-red-500 hover:bg-red-600 text-white'
    },
    amber: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      border: 'border-amber-200 dark:border-amber-800',
      icon: 'text-amber-500',
      title: 'text-amber-800 dark:text-amber-200',
      text: 'text-amber-700 dark:text-amber-300',
      button: 'bg-amber-500 hover:bg-amber-600 text-white'
    },
    gray: {
      bg: 'bg-gray-50 dark:bg-gray-800',
      border: 'border-gray-200 dark:border-gray-700',
      icon: 'text-gray-500',
      title: 'text-gray-800 dark:text-gray-200',
      text: 'text-gray-600 dark:text-gray-400',
      button: 'bg-gray-500 hover:bg-gray-600 text-white'
    }
  };

  const colors = colorClasses[errorConfig.color] || colorClasses.red;

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex items-center gap-3 px-4 py-3 rounded-xl ${colors.bg} border ${colors.border}`}
      >
        <Icon className={`w-5 h-5 flex-shrink-0 ${colors.icon}`} />
        <p className={`text-sm font-medium ${colors.text} flex-1`}>
          {displayTitle}
        </p>
        {showRetry && onRetry && (
          <button
            onClick={onRetry}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${colors.button}`}
          >
            Retry
          </button>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl overflow-hidden ${colors.bg} border ${colors.border}`}
    >
      <div className="p-6">
        <div className="flex items-start gap-4">
          <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${colors.bg} flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${colors.icon}`} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-semibold ${colors.title} mb-1`}>
              {displayTitle}
            </h3>
            <p className={`text-sm ${colors.text} mb-4`}>
              {displayDescription}
            </p>
            
            <div className="flex items-center gap-3">
              {showRetry && onRetry && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={onRetry}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${colors.button}`}
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </motion.button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ErrorState;






