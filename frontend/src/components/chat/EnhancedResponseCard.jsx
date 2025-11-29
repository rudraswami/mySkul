/**
 * Enhanced Response Card - Premium AI Response Display
 * Features: Copy, Feedback, Follow-ups, Dynamic Avatar, Timestamps
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Copy, 
  Check, 
  ThumbsUp, 
  ThumbsDown, 
  Sparkles,
  BookOpen,
  GraduationCap,
  Clock,
  ChevronRight,
  Zap,
  MessageCircle
} from 'lucide-react';
import AdaptiveMarkdown from '../AdaptiveMarkdown';

// Dynamic avatar based on response type
const ResponseAvatar = ({ type = 'mentor', emotion = 'neutral' }) => {
  const avatarConfig = {
    mentor: {
      bg: 'from-emerald-400 to-teal-500',
      icon: '🤝',
      label: 'Sathi'
    },
    professor: {
      bg: 'from-blue-500 to-indigo-600',
      icon: '🎓',
      label: 'Professor'
    },
    excited: {
      bg: 'from-orange-400 to-pink-500',
      icon: '🚀',
      label: 'Sathi'
    },
    confused_support: {
      bg: 'from-purple-400 to-pink-500',
      icon: '💪',
      label: 'Sathi'
    }
  };

  const config = avatarConfig[type] || avatarConfig.mentor;

  return (
    <div className="flex items-center gap-3 mb-3">
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${config.bg} flex items-center justify-center shadow-lg`}>
        <span className="text-lg">{config.icon}</span>
      </div>
      <div>
        <p className="font-semibold text-gray-800 dark:text-gray-100 text-sm">
          {config.label}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Just now
        </p>
      </div>
    </div>
  );
};

// Follow-up question chip
const FollowUpChip = ({ text, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.02, y: -1 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className="flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-purple-50 dark:hover:bg-purple-900/20 border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 rounded-xl text-sm text-gray-700 dark:text-gray-300 hover:text-purple-700 dark:hover:text-purple-300 transition-all duration-200"
  >
    <ChevronRight className="w-3 h-3" />
    <span className="truncate max-w-[200px]">{text}</span>
  </motion.button>
);

// Copy button with feedback
const CopyButton = ({ content }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={handleCopy}
      className={`p-2 rounded-lg transition-all duration-200 ${
        copied 
          ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' 
          : 'bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
      }`}
      title={copied ? 'Copied!' : 'Copy response'}
    >
      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </motion.button>
  );
};

// Feedback buttons
const FeedbackButtons = ({ onFeedback, messageId }) => {
  const [feedback, setFeedback] = useState(null);

  const handleFeedback = (type) => {
    setFeedback(type);
    onFeedback?.(messageId, type);
  };

  return (
    <div className="flex items-center gap-1">
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => handleFeedback('up')}
        className={`p-2 rounded-lg transition-all duration-200 ${
          feedback === 'up'
            ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20'
        }`}
        title="Good response"
      >
        <ThumbsUp className="w-4 h-4" />
      </motion.button>
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => handleFeedback('down')}
        className={`p-2 rounded-lg transition-all duration-200 ${
          feedback === 'down'
            ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20'
        }`}
        title="Needs improvement"
      >
        <ThumbsDown className="w-4 h-4" />
      </motion.button>
    </div>
  );
};

// Main Enhanced Response Card
export default function EnhancedResponseCard({
  content,
  subject,
  emotion = 'neutral',
  responseType = 'mentor',
  followUps = [],
  onFollowUpClick,
  onFeedback,
  messageId,
  generationTime,
  showActions = true
}) {
  const plainTextContent = typeof content === 'string' 
    ? content 
    : content?.content || JSON.stringify(content);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden"
    >
      {/* Subject Badge (if available) */}
      {subject && (
        <div className="px-4 pt-4">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold rounded-lg">
            <BookOpen className="w-3 h-3" />
            {subject}
          </span>
        </div>
      )}

      {/* Avatar & Header */}
      <div className="px-4 pt-4">
        <ResponseAvatar type={responseType} emotion={emotion} />
      </div>

      {/* Main Content */}
      <div className="px-4 pb-3">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <AdaptiveMarkdown content={plainTextContent} />
        </div>
      </div>

      {/* Follow-up Questions */}
      {followUps && followUps.length > 0 && (
        <div className="px-4 pb-4">
          <div className="flex items-center gap-2 mb-2">
            <MessageCircle className="w-4 h-4 text-purple-500" />
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Continue Learning
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {followUps.slice(0, 3).map((followUp, index) => (
              <FollowUpChip
                key={index}
                text={followUp.text || followUp}
                onClick={() => onFollowUpClick?.(followUp.text || followUp)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Action Bar */}
      {showActions && (
        <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
          {/* Left: Generation time */}
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            {generationTime && (
              <>
                <Zap className="w-3 h-3 text-yellow-500" />
                <span>{generationTime}s</span>
              </>
            )}
          </div>

          {/* Right: Copy & Feedback */}
          <div className="flex items-center gap-2">
            <CopyButton content={plainTextContent} />
            <div className="w-px h-5 bg-gray-200 dark:bg-gray-700" />
            <FeedbackButtons onFeedback={onFeedback} messageId={messageId} />
          </div>
        </div>
      )}
    </motion.div>
  );
}

// Export individual components for flexibility
export { ResponseAvatar, FollowUpChip, CopyButton, FeedbackButtons };


