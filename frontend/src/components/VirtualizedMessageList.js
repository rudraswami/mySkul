/**
 * Virtualized Message List Component
 * Efficiently renders large chat histories with virtual scrolling
 * Only renders visible messages in the viewport
 */
import React, { useRef, useEffect, memo } from 'react';
import { VariableSizeList as List } from 'react-window';

/**
 * Individual Message Row Component
 * Memoized to prevent unnecessary re-renders
 */
const MessageRow = memo(({ data, index, style }) => {
  const { messages, renderMessage } = data;
  const message = messages[index];
  
  if (!message) return null;
  
  return (
    <div style={style}>
      {renderMessage(message, index)}
    </div>
  );
});

MessageRow.displayName = 'MessageRow';

/**
 * VirtualizedMessageList Component
 * 
 * @param {Array} messages - Array of message objects
 * @param {Function} renderMessage - Function to render each message (message, index) => ReactNode
 * @param {Function} getMessageHeight - Function to calculate message height (message, index) => number
 * @param {number} defaultItemSize - Default height for messages (default: 100)
 * @param {Function} onScroll - Callback when scrolling
 * @param {boolean} scrollToBottom - Auto-scroll to bottom on new messages
 */
export function VirtualizedMessageList({
  messages = [],
  renderMessage,
  getMessageHeight,
  defaultItemSize = 150,
  onScroll,
  scrollToBottom = true,
  className = ''
}) {
  const listRef = useRef(null);
  const containerRef = useRef(null);
  const previousMessageCountRef = useRef(messages.length);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollToBottom && messages.length > previousMessageCountRef.current && listRef.current) {
      // Scroll to bottom with slight delay to ensure rendering
      setTimeout(() => {
        listRef.current?.scrollToItem(messages.length - 1, 'end');
      }, 100);
    }
    previousMessageCountRef.current = messages.length;
  }, [messages.length, scrollToBottom]);

  // Calculate item size for variable height messages
  const getItemSize = (index) => {
    if (getMessageHeight) {
      return getMessageHeight(messages[index], index);
    }
    return defaultItemSize;
  };

  // Handle scroll events
  const handleScroll = ({ scrollDirection, scrollOffset, scrollUpdateWasRequested }) => {
    if (onScroll) {
      onScroll({ scrollDirection, scrollOffset, scrollUpdateWasRequested });
    }
  };

  if (!messages || messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
        No messages yet
      </div>
    );
  }

  // Get container dimensions
  const [dimensions, setDimensions] = React.useState({ width: 800, height: 600 });

  React.useEffect(() => {
    if (containerRef.current) {
      const updateDimensions = () => {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight
        });
      };

      updateDimensions();
      window.addEventListener('resize', updateDimensions);
      return () => window.removeEventListener('resize', updateDimensions);
    }
  }, []);

  return (
    <div ref={containerRef} className={`w-full h-full ${className}`}>
      <List
        ref={listRef}
        height={dimensions.height}
        width={dimensions.width}
        itemCount={messages.length}
        itemSize={getItemSize}
        itemData={{
          messages,
          renderMessage
        }}
        onScroll={handleScroll}
        overscanCount={5} // Render 5 extra items above/below viewport
      >
        {MessageRow}
      </List>
    </div>
  );
}

export default VirtualizedMessageList;
