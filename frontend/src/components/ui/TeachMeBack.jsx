/**
 * TeachMeBack - Feynman Technique Learning Feature
 * 
 * "If you can explain it simply, you understand it."
 * 
 * Design:
 * - Appears as a gentle invitation after complex explanations
 * - NOT a button cluster - a natural conversation extension
 * - Student explains → AI gives constructive feedback
 * - Focus: What did they understand? What to strengthen?
 */
import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Send, 
  CheckCircle2, 
  Lightbulb,
  ArrowRight,
  X
} from 'lucide-react';

/**
 * Gentle invitation prompt - appears contextually
 */
const TeachMeBackInvite = ({ onAccept, onDismiss, concept = 'this concept' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mt-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl border border-amber-200 dark:border-amber-800"
    >
      <div className="flex items-start gap-3">
        <div className="text-2xl">💭</div>
        <div className="flex-1">
          <p className="text-amber-800 dark:text-amber-200 font-medium">
            Think you got it?
          </p>
          <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
            Try explaining {concept} in your own words. I'll help you spot any gaps.
          </p>
          
          <div className="flex items-center gap-3 mt-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onAccept}
              className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-medium text-sm transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              Let me try
            </motion.button>
            
            <button
              onClick={onDismiss}
              className="text-sm text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300"
            >
              Maybe later
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Input mode for student explanation
 */
const TeachMeBackInput = ({ concept, onSubmit, onCancel }) => {
  const [explanation, setExplanation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const textareaRef = useRef(null);

  const handleSubmit = async () => {
    if (!explanation.trim() || isSubmitting) return;
    setIsSubmitting(true);
    await onSubmit(explanation);
    setIsSubmitting(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mt-6 p-4 bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 rounded-2xl border border-violet-200 dark:border-violet-800"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">🎓</span>
          <span className="font-medium text-violet-800 dark:text-violet-200">
            Your turn to explain
          </span>
        </div>
        <button
          onClick={onCancel}
          className="p-1 rounded-lg hover:bg-violet-100 dark:hover:bg-violet-800 transition-colors"
        >
          <X className="w-4 h-4 text-violet-500" />
        </button>
      </div>
      
      <p className="text-sm text-violet-600 dark:text-violet-400 mb-3">
        Explain <strong>{concept || 'this concept'}</strong> as if teaching a friend. 
        Don't worry about being perfect!
      </p>
      
      <textarea
        ref={textareaRef}
        value={explanation}
        onChange={(e) => setExplanation(e.target.value)}
        placeholder="In my own words, this concept is about..."
        className="w-full p-3 bg-white dark:bg-gray-800 border border-violet-200 dark:border-violet-700 rounded-xl text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none"
        rows={4}
        autoFocus
      />
      
      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-violet-500">
          {explanation.length > 0 ? `${explanation.split(' ').length} words` : 'Start typing...'}
        </span>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSubmit}
          disabled={!explanation.trim() || isSubmitting}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all ${
            explanation.trim() && !isSubmitting
              ? 'bg-violet-600 hover:bg-violet-700 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isSubmitting ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
              />
              Analyzing...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Check my understanding
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
};

/**
 * Feedback display - constructive, encouraging, specific
 */
const TeachMeBackFeedback = ({ feedback, onContinue, onTryAgain }) => {
  const { 
    understood = [], 
    gaps = [], 
    tip = '', 
    encouragement = '',
    score = null // We don't show this - it's for internal use
  } = feedback;

  const hasGaps = gaps.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 space-y-4"
    >
      {/* Encouragement header */}
      <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-2xl border border-emerald-200 dark:border-emerald-800">
        <div className="flex items-start gap-3">
          <div className="text-2xl">
            {hasGaps ? '💪' : '🌟'}
          </div>
          <div>
            <p className="font-medium text-emerald-800 dark:text-emerald-200">
              {encouragement || (hasGaps ? "Good effort! Let's strengthen your understanding." : "Excellent! You've got a solid grasp!")}
            </p>
          </div>
        </div>
      </div>

      {/* What you understood well */}
      {understood.length > 0 && (
        <div className="p-4 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            <span className="font-medium text-gray-800 dark:text-gray-200">
              What you nailed:
            </span>
          </div>
          <ul className="space-y-1 ml-7">
            {understood.map((point, i) => (
              <li key={i} className="text-sm text-gray-600 dark:text-gray-400">
                • {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas to strengthen */}
      {gaps.length > 0 && (
        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            <span className="font-medium text-amber-800 dark:text-amber-200">
              To strengthen:
            </span>
          </div>
          <ul className="space-y-1 ml-7">
            {gaps.map((gap, i) => (
              <li key={i} className="text-sm text-amber-700 dark:text-amber-300">
                • {gap}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Quick tip */}
      {tip && (
        <div className="p-3 bg-violet-50 dark:bg-violet-900/20 rounded-xl border border-violet-200 dark:border-violet-800">
          <p className="text-sm text-violet-700 dark:text-violet-300">
            <strong>💡 Quick tip:</strong> {tip}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        {hasGaps && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onTryAgain}
            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-medium text-sm transition-colors"
          >
            Try explaining again
          </motion.button>
        )}
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onContinue}
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium text-sm transition-colors"
        >
          Continue learning
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </div>
    </motion.div>
  );
};

/**
 * Main TeachMeBack Component
 * 
 * States:
 * - idle: Not shown
 * - invite: Gentle invitation
 * - input: Student typing explanation
 * - feedback: Showing AI feedback
 */
const TeachMeBack = ({ 
  isVisible = false,
  concept = 'this concept',
  onEvaluate, // async (explanation) => feedback
  onComplete,
  onDismiss
}) => {
  const [state, setState] = useState('invite'); // invite | input | feedback
  const [feedback, setFeedback] = useState(null);

  const handleAcceptInvite = () => {
    setState('input');
  };

  const handleSubmitExplanation = async (explanation) => {
    // Call parent's evaluate function
    const result = await onEvaluate?.(explanation);
    setFeedback(result || {
      understood: ['You have the basic idea'],
      gaps: [],
      tip: 'Keep practicing!',
      encouragement: 'Good effort!'
    });
    setState('feedback');
  };

  const handleTryAgain = () => {
    setFeedback(null);
    setState('input');
  };

  const handleContinue = () => {
    setState('idle');
    onComplete?.();
  };

  const handleDismiss = () => {
    setState('idle');
    onDismiss?.();
  };

  if (!isVisible || state === 'idle') return null;

  return (
    <AnimatePresence mode="wait">
      {state === 'invite' && (
        <TeachMeBackInvite
          key="invite"
          concept={concept}
          onAccept={handleAcceptInvite}
          onDismiss={handleDismiss}
        />
      )}
      
      {state === 'input' && (
        <TeachMeBackInput
          key="input"
          concept={concept}
          onSubmit={handleSubmitExplanation}
          onCancel={handleDismiss}
        />
      )}
      
      {state === 'feedback' && feedback && (
        <TeachMeBackFeedback
          key="feedback"
          feedback={feedback}
          onContinue={handleContinue}
          onTryAgain={handleTryAgain}
        />
      )}
    </AnimatePresence>
  );
};

export default TeachMeBack;



