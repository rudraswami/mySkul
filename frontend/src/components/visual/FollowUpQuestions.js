/**
 * Follow-Up Questions Component
 * Shows contextual follow-up question suggestions after AI response
 */
import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Lightbulb } from 'lucide-react';

const FollowUpQuestions = ({ questions = [], onQuestionClick }) => {
  if (!questions || questions.length === 0) return null;

  // Extract key concepts from questions for better suggestions
  const generateFollowUps = (responseText, originalQuestion) => {
    const followUps = [];
    
    // Extract subject/topic from original question
    const questionLower = originalQuestion.toLowerCase();
    
    // Pattern-based follow-up generation
    if (questionLower.includes('explain') || questionLower.includes('what is')) {
      followUps.push(
        `Can you give me a real-world example of this?`,
        `How is this different from similar concepts?`,
        `Can you solve a practice problem on this?`
      );
    } else if (questionLower.includes('how') || questionLower.includes('why')) {
      followUps.push(
        `What are the key steps involved?`,
        `Can you explain this with a diagram?`,
        `What are common mistakes students make here?`
      );
    } else if (questionLower.includes('solve') || questionLower.includes('calculate')) {
      followUps.push(
        `Can you explain the method step-by-step?`,
        `What if the numbers were different?`,
        `Are there alternative approaches?`
      );
    } else {
      // Generic follow-ups
      followUps.push(
        `Can you explain this in simpler terms?`,
        `What are some real-world applications?`,
        `Can you give me a practice problem?`
      );
    }

    return followUps.slice(0, 3);
  };

  const suggestedQuestions = questions.length > 0 
    ? questions 
    : generateFollowUps('', '');

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900 dark:to-indigo-900 rounded-xl border border-purple-200 dark:border-purple-700"
    >
      <div className="flex items-center space-x-2 mb-3">
        <Lightbulb className="h-4 w-4 text-purple-600 dark:text-purple-400" />
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
          💡 Ask a follow-up question
        </h4>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {suggestedQuestions.map((question, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * index }}
            onClick={() => onQuestionClick && onQuestionClick(question)}
            className="group flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-purple-100 hover:to-indigo-100 dark:hover:from-purple-800 dark:hover:to-indigo-800 hover:shadow-md transition-all hover:scale-105 border border-purple-200 dark:border-purple-700"
          >
            <span>{question}</span>
            <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

export default FollowUpQuestions;













