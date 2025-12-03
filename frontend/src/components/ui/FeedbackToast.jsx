/**
 * Feedback Toast Component
 * Shows confirmation when user gives feedback on AI response
 */
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, ThumbsUp, ThumbsDown, X } from 'lucide-react';

const FeedbackToast = ({ 
  type = 'positive', // 'positive' | 'negative'
  show = false,
  onClose,
  autoHideDuration = 3000
}) => {
  const [isVisible, setIsVisible] = useState(show);

  useEffect(() => {
    setIsVisible(show);
    
    if (show && autoHideDuration) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, autoHideDuration);
      
      return () => clearTimeout(timer);
    }
  }, [show, autoHideDuration, onClose]);

  const config = {
    positive: {
      icon: ThumbsUp,
      title: 'Thanks for your feedback!',
      subtitle: 'This helps us improve 🙌',
      bgColor: 'bg-gradient-to-r from-emerald-500 to-teal-500',
      iconBg: 'bg-emerald-600'
    },
    negative: {
      icon: ThumbsDown,
      title: 'Feedback received',
      subtitle: "We'll work on improving this",
      bgColor: 'bg-gradient-to-r from-slate-700 to-slate-800',
      iconBg: 'bg-slate-600'
    }
  };

  const { icon: Icon, title, subtitle, bgColor, iconBg } = config[type];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          className={`fixed bottom-8 left-1/2 -translate-x-1/2 z-[500] ${bgColor} text-white rounded-2xl shadow-2xl overflow-hidden`}
          style={{ minWidth: '280px', maxWidth: '90vw' }}
        >
          <div className="flex items-center gap-4 px-5 py-4">
            {/* Icon */}
            <div className={`flex-shrink-0 w-11 h-11 ${iconBg} rounded-xl flex items-center justify-center`}>
              <Icon className="w-5 h-5" />
            </div>
            
            {/* Text */}
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-[15px]">{title}</p>
              <p className="text-sm text-white/80 mt-0.5">{subtitle}</p>
            </div>
            
            {/* Close button */}
            <button
              onClick={() => {
                setIsVisible(false);
                onClose?.();
              }}
              className="flex-shrink-0 p-1.5 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          {/* Progress bar */}
          <motion.div
            initial={{ width: '100%' }}
            animate={{ width: '0%' }}
            transition={{ duration: autoHideDuration / 1000, ease: 'linear' }}
            className="h-1 bg-white/30"
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FeedbackToast;

/**
 * Hook for managing feedback toast state
 */
export const useFeedbackToast = () => {
  const [toastState, setToastState] = useState({
    show: false,
    type: 'positive'
  });

  const showFeedbackToast = (type = 'positive') => {
    setToastState({ show: true, type });
  };

  const hideFeedbackToast = () => {
    setToastState(prev => ({ ...prev, show: false }));
  };

  return {
    toastState,
    showFeedbackToast,
    hideFeedbackToast
  };
};

