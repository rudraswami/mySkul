/**
 * Virtualized Message List Component
 * Efficiently renders large chat histories with virtual scrolling
 * Only renders visible messages in the viewport
 */
import React, { useRef, useEffect, memo } from 'react';
import { VariableSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

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
  defaultItemSize = 100,
  onScroll,
  scrollToBottom = true,
  className = ''
}) {
  const listRef = useRef(null);
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
      <div className="flex items-center justify-center h-full text-gray-500">
        No messages yet
      </div>
    );
  }

  return (
    <div className={`w-full h-full ${className}`}>
      <AutoSizer>
        {({ height, width }) => (
          <List
            ref={listRef}
            height={height}
            width={width}
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
        )}
      </AutoSizer>
    </div>
  );
}

/**
 * Simple Message List with Fixed Height
 * For uniform message sizes
 */
export function FixedHeightMessageList({
  messages = [],
  renderMessage,
  itemHeight = 100,
  onScroll,
  scrollToBottom = true,
  className = ''
}) {
  return (
    <VirtualizedMessageList
      messages={messages}
      renderMessage={renderMessage}
      defaultItemSize={itemHeight}
      onScroll={onScroll}
      scrollToBottom={scrollToBottom}
      className={className}
    />
  );
}

export default VirtualizedMessageList;
