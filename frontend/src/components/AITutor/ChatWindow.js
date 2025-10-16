/**
 * ChatWindow Component
 * Displays messages using virtualized scrolling for performance
 */
import React, { useEffect, useRef } from 'react';
import { VirtualizedMessageList } from '../VirtualizedMessageList';
import { MessageItem } from './MessageItem';
import { Loader2 } from 'lucide-react';

export function ChatWindow({ 
  messages = [], 
  loading = false,
  onMessageReact,
  onMessageDelete,
  className = ''
}) {
  const scrollRef = useRef(null);

  // Render individual message
  const renderMessage = (message, index) => (
    <MessageItem
      key={message.id || index}
      message={message}
      onReact={onMessageReact}
      onDelete={onMessageDelete}
      showActions={true}
    />
  );

  // Empty state
  if (!loading && messages.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center h-full text-center p-8 ${className}`}>
        <div className="w-16 h-16 mb-4 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
          <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Start a Conversation
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          Ask me anything about your studies. I'm here to help you learn and understand better!
        </p>
      </div>
    );
  }

  return (
    <div className={`relative h-full ${className}`}>
      {/* Messages with virtual scrolling */}
      <VirtualizedMessageList
        messages={messages}
        renderMessage={renderMessage}
        defaultItemSize={150}
        scrollToBottom={true}
        className="p-4 space-y-4"
      />

      {/* Loading indicator */}
      {loading && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="flex items-center gap-2 bg-white dark:bg-gray-800 shadow-lg rounded-full px-4 py-2">
            <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
            <span className="text-sm text-gray-700 dark:text-gray-300">AI is thinking...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatWindow;
