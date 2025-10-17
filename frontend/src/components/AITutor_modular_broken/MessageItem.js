/**
 * MessageItem Component
 * Displays a single message with sanitized content
 */
import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { createSafeHTML } from '../../utils/sanitize';
import { ThumbsUp, ThumbsDown, User, Brain, Trash2 } from 'lucide-react';
import { Button } from '../ui/button';

export const MessageItem = memo(({ 
  message, 
  onReact, 
  onDelete,
  showActions = true 
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 p-4 rounded-lg ${
        isUser 
          ? 'bg-blue-50 dark:bg-blue-900/20 ml-auto max-w-[80%]' 
          : 'bg-white dark:bg-gray-800 max-w-full'
      }`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 ${isUser ? 'order-2' : ''}`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-blue-600 dark:bg-blue-500' 
            : 'bg-gradient-to-br from-purple-600 to-blue-600'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Brain className="w-4 h-4 text-white" />
          )}
        </div>
      </div>

      {/* Content */}
      <div className={`flex-1 ${isUser ? 'order-1' : ''}`}>
        {/* Message Content - Sanitized HTML */}
        <div 
          className={`prose prose-sm max-w-none ${
            isUser 
              ? 'text-gray-900 dark:text-gray-100' 
              : 'text-gray-800 dark:text-gray-200'
          }`}
          dangerouslySetInnerHTML={createSafeHTML(message.content)}
        />

        {/* Metadata */}
        {message.timestamp && (
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        )}

        {/* Actions */}
        {showActions && isAssistant && (
          <div className="flex gap-2 mt-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onReact && onReact(message.id, 'thumbs_up')}
              className="h-7 px-2"
              aria-label="Like this response"
            >
              <ThumbsUp className="w-3 h-3 mr-1" />
              <span className="text-xs">Helpful</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onReact && onReact(message.id, 'thumbs_down')}
              className="h-7 px-2"
              aria-label="Dislike this response"
            >
              <ThumbsDown className="w-3 h-3 mr-1" />
              <span className="text-xs">Not helpful</span>
            </Button>
          </div>
        )}

        {/* Delete button (for user messages) */}
        {showActions && isUser && onDelete && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(message.id)}
            className="h-7 px-2 mt-2 text-red-600 hover:text-red-700 dark:text-red-400"
            aria-label="Delete message"
          >
            <Trash2 className="w-3 h-3 mr-1" />
            <span className="text-xs">Delete</span>
          </Button>
        )}
      </div>
    </motion.div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;
