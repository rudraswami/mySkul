/**
 * ChatMessage Component
 * 
 * Displays a single chat message (user or AI) with proper formatting
 * Supports dual-response format, semantic rendering, and loading states
 */

import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot, Sparkles } from 'lucide-react';
import SemanticAIResponse from '../SemanticAIResponse';
import { formatProfessorMentorResponse } from '../FormattedAIResponse';

const ChatMessage = ({ 
  message, 
  isLoading = false,
  showTimestamp = true 
}) => {
  const isUser = message.role === 'user';
  const isAI = message.role === 'assistant' || message.role === 'ai';

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Render AI response based on format
  const renderAIResponse = () => {
    if (isLoading) {
      return (
        <div className="flex items-center space-x-2 text-gray-500">
          <div className="animate-pulse">●</div>
          <div className="animate-pulse delay-100">●</div>
          <div className="animate-pulse delay-200">●</div>
          <span className="ml-2">AI is thinking...</span>
        </div>
      );
    }

    const aiResponse = message.aiResponse;

    // Handle dual response format (mentor + professor)
    if (aiResponse?.dual_response) {
      return (
        <div className="space-y-4">
          {/* Mentor Response */}
          {aiResponse.dual_response.mentor_response && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border-l-4 border-blue-500">
              <div className="flex items-center space-x-2 mb-2">
                <Sparkles className="h-4 w-4 text-blue-600" />
                <span className="font-semibold text-blue-900 dark:text-blue-100">
                  Mentor (Friendly)
                </span>
              </div>
              <div className="text-gray-800 dark:text-gray-200">
                <SemanticAIResponse 
                  response={aiResponse.dual_response.mentor_response}
                  role="mentor"
                />
              </div>
            </div>
          )}

          {/* Professor Response */}
          {aiResponse.dual_response.professor_response && (
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border-l-4 border-purple-500">
              <div className="flex items-center space-x-2 mb-2">
                <Bot className="h-4 w-4 text-purple-600" />
                <span className="font-semibold text-purple-900 dark:text-purple-100">
                  Professor (Technical)
                </span>
              </div>
              <div className="text-gray-800 dark:text-gray-200">
                <SemanticAIResponse 
                  response={aiResponse.dual_response.professor_response}
                  role="professor"
                />
              </div>
            </div>
          )}

          {/* Scenario Type */}
          {aiResponse.scenario_type && (
            <div className="text-xs text-gray-500 dark:text-gray-400 italic">
              Scenario: {aiResponse.scenario_type}
            </div>
          )}
        </div>
      );
    }

    // Handle single response format
    if (aiResponse?.response) {
      return (
        <div className="text-gray-800 dark:text-gray-200">
          <SemanticAIResponse 
            response={aiResponse.response}
            role="assistant"
          />
        </div>
      );
    }

    // Fallback for plain text
    if (typeof aiResponse === 'string') {
      return (
        <div className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
          {aiResponse}
        </div>
      );
    }

    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-start space-x-3 max-w-[85%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white'
        }`}>
          {isUser ? (
            <User className="h-5 w-5" />
          ) : (
            <Bot className="h-5 w-5" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Message Bubble */}
          <div className={`rounded-2xl px-4 py-3 ${
            isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm'
          }`}>
            {isUser ? (
              <p className="text-white whitespace-pre-wrap">{message.content}</p>
            ) : (
              renderAIResponse()
            )}
          </div>

          {/* Timestamp */}
          {showTimestamp && message.timestamp && (
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 px-2">
              {formatTime(message.timestamp)}
            </span>
          )}

          {/* Pending indicator */}
          {message.pending && (
            <span className="text-xs text-gray-400 mt-1 px-2 italic">
              Sending...
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Memoize to prevent unnecessary re-renders
export default React.memo(ChatMessage);
