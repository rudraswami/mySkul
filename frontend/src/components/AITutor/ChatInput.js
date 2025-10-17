/**
 * ChatInput Component
 * 
 * Input field for sending messages with voice input support
 * Handles keyboard shortcuts, character limits, and validation
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Loader } from 'lucide-react';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';

const MAX_MESSAGE_LENGTH = 2000;

const ChatInput = ({ 
  onSend, 
  disabled = false,
  loading = false,
  voiceEnabled = false,
  isListening = false,
  onVoiceToggle,
  voiceTranscript = '',
  placeholder = "Ask me anything about your studies..."
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  // Update message from voice transcript
  useEffect(() => {
    if (voiceTranscript && isListening) {
      setMessage(voiceTranscript);
    }
  }, [voiceTranscript, isListening]);

  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  /**
   * Handle send message
   */
  const handleSend = () => {
    const trimmedMessage = message.trim();
    
    if (!trimmedMessage || disabled || loading) return;
    if (trimmedMessage.length > MAX_MESSAGE_LENGTH) return;

    onSend(trimmedMessage);
    setMessage('');
    
    // Refocus textarea
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }, 100);
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e) => {
    // Enter to send (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    
    // Ctrl/Cmd + Enter to send
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= MAX_MESSAGE_LENGTH) {
      setMessage(value);
    }
  };

  /**
   * Calculate character count color
   */
  const getCharCountColor = () => {
    const percentage = (message.length / MAX_MESSAGE_LENGTH) * 100;
    if (percentage >= 95) return 'text-red-600';
    if (percentage >= 80) return 'text-orange-600';
    return 'text-gray-500';
  };

  const charCount = message.length;
  const canSend = message.trim().length > 0 && !disabled && !loading;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="flex items-end space-x-2">
        {/* Voice Input Button */}
        {voiceEnabled && onVoiceToggle && (
          <Button
            type="button"
            variant={isListening ? "default" : "outline"}
            size="icon"
            onClick={onVoiceToggle}
            disabled={disabled || loading}
            className={`flex-shrink-0 ${isListening ? 'bg-red-600 hover:bg-red-700 animate-pulse' : ''}`}
            title={isListening ? "Stop listening" : "Start voice input"}
          >
            {isListening ? (
              <MicOff className="h-5 w-5" />
            ) : (
              <Mic className="h-5 w-5" />
            )}
          </Button>
        )}

        {/* Text Input */}
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={isListening ? "Listening..." : placeholder}
            disabled={disabled || loading}
            rows={1}
            className="min-h-[44px] max-h-[200px] resize-none pr-16"
            style={{ 
              height: 'auto',
              overflow: message.length > 100 ? 'auto' : 'hidden'
            }}
          />
          
          {/* Character Count */}
          <div className={`absolute bottom-2 right-2 text-xs ${getCharCountColor()}`}>
            {charCount}/{MAX_MESSAGE_LENGTH}
          </div>
        </div>

        {/* Send Button */}
        <Button
          type="button"
          onClick={handleSend}
          disabled={!canSend}
          size="icon"
          className="flex-shrink-0 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Send message (Enter)"
        >
          {loading ? (
            <Loader className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </div>

      {/* Helper Text */}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>
          Press <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">Enter</kbd> to send
          {!disabled && !loading && ', '}
          <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">Shift + Enter</kbd> for new line
        </span>
        
        {isListening && (
          <span className="text-red-600 animate-pulse">
            🔴 Recording...
          </span>
        )}
      </div>
    </div>
  );
};

export default React.memo(ChatInput);
