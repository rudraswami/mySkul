/**
 * Interactive Practice Problem Component
 * Features: Answer input, AI-powered checking, feedback, hints
 */
import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Lightbulb,
  Send,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Loader2
} from 'lucide-react';

const InteractivePractice = ({
  question,
  hint,
  expectedAnswer,
  subject,
  onCheckAnswer,
  onAskForHelp,
  difficulty = 'medium'
}) => {
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [attempts, setAttempts] = useState(0);

  const difficultyColors = {
    easy: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
    medium: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
    hard: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' }
  };

  const colors = difficultyColors[difficulty] || difficultyColors.medium;

  const handleCheck = useCallback(async () => {
    if (!userAnswer.trim() || isChecking) return;

    setIsChecking(true);
    setAttempts(prev => prev + 1);

    try {
      // If custom check handler provided, use it
      if (onCheckAnswer) {
        const result = await onCheckAnswer(userAnswer, expectedAnswer, question);
        setFeedback(result);
      } else {
        // Simple local check (can be enhanced with AI)
        const isCorrect = expectedAnswer && 
          userAnswer.toLowerCase().trim().includes(expectedAnswer.toLowerCase().trim());
        
        setFeedback({
          status: isCorrect ? 'correct' : 'incorrect',
          message: isCorrect 
            ? 'Great job! That\'s correct! 🎉' 
            : 'Not quite right. Try again or ask for a hint!',
          explanation: isCorrect ? null : 'Think about the core concept and try again.'
        });
      }
    } catch (error) {
      setFeedback({
        status: 'error',
        message: 'Could not check your answer. Please try again.'
      });
    } finally {
      setIsChecking(false);
    }
  }, [userAnswer, expectedAnswer, question, onCheckAnswer, isChecking]);

  const handleReset = () => {
    setUserAnswer('');
    setFeedback(null);
    setShowHint(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCheck();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="sathi-practice-card bg-white rounded-2xl overflow-hidden border-2 border-blue-200 shadow-sm"
    >
      {/* Header */}
      <div className={`flex items-center justify-between gap-3 px-5 py-4 ${colors.bg} border-b ${colors.border}`}>
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-blue-500 rounded-xl text-white">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-base">Practice Problem</h3>
            {subject && (
              <span className="text-xs font-medium text-gray-500">{subject}</span>
            )}
          </div>
        </div>
        
        {/* Difficulty badge */}
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.bg} ${colors.text} border ${colors.border}`}>
          {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
        </span>
      </div>

      {/* Question */}
      <div className="px-5 py-4 border-b border-gray-100">
        <p className="text-gray-800 leading-relaxed text-[15px]">
          {question}
        </p>
      </div>

      {/* Hint Section */}
      {hint && (
        <div className="px-5 py-3 border-b border-gray-100 bg-amber-50/50">
          <button
            onClick={() => setShowHint(!showHint)}
            className="flex items-center gap-2 text-sm font-medium text-amber-700 hover:text-amber-800 transition-colors"
          >
            <Lightbulb className="w-4 h-4" />
            <span>{showHint ? 'Hide Hint' : 'Need a Hint?'}</span>
            {showHint ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          <AnimatePresence>
            {showHint && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <p className="mt-3 text-sm text-amber-800 bg-amber-100/50 rounded-lg p-3 border border-amber-200">
                  💡 {hint}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Answer Input */}
      <div className="px-5 py-4 bg-gray-50/50">
        <label className="block text-sm font-medium text-gray-600 mb-2">
          Your Answer:
        </label>
        <div className="flex gap-3">
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your answer here..."
            disabled={feedback?.status === 'correct'}
            className="flex-1 px-4 py-3 bg-white border-2 border-gray-200 rounded-xl text-gray-800 text-[15px] placeholder-gray-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none transition-all resize-none disabled:opacity-50 disabled:cursor-not-allowed"
            rows={2}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-2">
            {attempts > 0 && (
              <span className="text-xs text-gray-500">
                Attempts: {attempts}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {(feedback || userAnswer) && (
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 px-3 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg text-sm font-medium transition-all"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            )}
            
            <button
              onClick={handleCheck}
              disabled={!userAnswer.trim() || isChecking || feedback?.status === 'correct'}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-xl text-sm font-semibold transition-all disabled:cursor-not-allowed"
            >
              {isChecking ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Checking...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Check Answer
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Feedback */}
      <AnimatePresence>
        {feedback && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div
              className={`px-5 py-4 ${
                feedback.status === 'correct'
                  ? 'bg-green-50 border-t border-green-200'
                  : feedback.status === 'incorrect'
                  ? 'bg-red-50 border-t border-red-200'
                  : feedback.status === 'partial'
                  ? 'bg-amber-50 border-t border-amber-200'
                  : 'bg-gray-50 border-t border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                {feedback.status === 'correct' && (
                  <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                )}
                {feedback.status === 'incorrect' && (
                  <XCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                )}
                {feedback.status === 'partial' && (
                  <AlertCircle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
                )}
                
                <div className="flex-1">
                  <p className={`font-semibold ${
                    feedback.status === 'correct' ? 'text-green-800' :
                    feedback.status === 'incorrect' ? 'text-red-800' :
                    'text-amber-800'
                  }`}>
                    {feedback.message}
                  </p>
                  
                  {feedback.explanation && (
                    <p className={`mt-2 text-sm ${
                      feedback.status === 'correct' ? 'text-green-700' :
                      feedback.status === 'incorrect' ? 'text-red-700' :
                      'text-amber-700'
                    }`}>
                      {feedback.explanation}
                    </p>
                  )}
                  
                  {/* Action buttons based on feedback */}
                  {feedback.status !== 'correct' && (
                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => onAskForHelp?.(question)}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
                      >
                        Ask Sathi for help →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default InteractivePractice;

