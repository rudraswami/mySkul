/**
 * AITutorChat Component
 * 
 * Main chat window displaying messages with auto-scroll and virtual scrolling
 * Optimized for performance with large message lists
 */

import React, { useEffect, useRef, useMemo } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Sparkles } from 'lucide-react';
import ChatMessage from './ChatMessage';

const AITutorChat = ({ 
  messages = [],
  loading = false,
  onLoadMore = null,
  showScrollToBottom = true
}) => {
  const chatContainerRef = useRef(null);
  const bottomRef = useRef(null);
  const isUserScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef(null);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    if (bottomRef.current && !isUserScrollingRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  /**
   * Detect user scrolling
   */
  const handleScroll = () => {
    if (!chatContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

    // If user is near bottom, enable auto-scroll
    isUserScrollingRef.current = !isNearBottom;

    // Clear existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    // Reset scrolling flag after user stops scrolling
    scrollTimeoutRef.current = setTimeout(() => {
      if (isNearBottom) {
        isUserScrollingRef.current = false;
      }
    }, 1000);

    // Load more messages if scrolled to top
    if (scrollTop === 0 && onLoadMore) {
      onLoadMore();
    }
  };

  /**
   * Scroll to bottom manually
   */
  const scrollToBottom = () => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
      isUserScrollingRef.current = false;
    }
  };

  /**
   * Cleanup
   */
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  /**
   * Empty state
   */
  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", duration: 0.5 }}
        className="mb-6"
      >
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <Sparkles className="h-12 w-12 text-white" />
        </div>
      </motion.div>

      <motion.h3
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-2xl font-bold text-gray-900 dark:text-white mb-3"
      >
        Start a Conversation
      </motion.h3>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-gray-600 dark:text-gray-300 max-w-md mb-6"
      >
        Ask me anything about your studies! I can help with homework, explain concepts, 
        solve problems, and prepare you for exams.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl"
      >
        {[
          { icon: '📚', text: 'Explain a difficult concept' },
          { icon: '🧮', text: 'Solve a math problem' },
          { icon: '🧪', text: 'Help with science homework' },
          { icon: '📝', text: 'Prepare for an exam' }
        ].map((item, idx) => (
          <div
            key={idx}
            className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 transition-colors cursor-pointer"
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="text-sm text-gray-700 dark:text-gray-300">{item.text}</span>
          </div>
        ))}
      </motion.div>
    </div>
  );

  /**
   * Loading indicator
   */
  const renderLoadingIndicator = () => (
    <div className="flex justify-start mb-4">
      <div className="flex items-start space-x-3 max-w-[85%]">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
          <MessageSquare className="h-5 w-5 text-white" />
        </div>
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 shadow-sm">
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="animate-bounce">●</div>
            <div className="animate-bounce delay-100">●</div>
            <div className="animate-bounce delay-200">●</div>
            <span className="ml-2">Thinking...</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Memoize messages to prevent unnecessary re-renders
  const renderedMessages = useMemo(() => {
    return messages.map((msg, index) => (
      <ChatMessage 
        key={msg.id || index}
        message={msg}
        showTimestamp={true}
      />
    ));
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Chat Messages Container */}
      <div
        ref={chatContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 scroll-smooth"
        style={{ scrollBehavior: 'smooth' }}
      >
        {messages.length === 0 ? (
          renderEmptyState()
        ) : (
          <>
            {renderedMessages}
            {loading && renderLoadingIndicator()}
            {/* Scroll anchor */}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* Scroll to Bottom Button */}
      {showScrollToBottom && isUserScrollingRef.current && messages.length > 3 && (
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          onClick={scrollToBottom}
          className="absolute bottom-24 right-8 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 shadow-lg z-10"
          title="Scroll to bottom"
        >
          ↓
        </motion.button>
      )}
    </div>
  );
};

export default React.memo(AITutorChat);
