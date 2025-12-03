/**
 * Enhanced Chat Input - Premium Input Experience
 * Features: Stop button, proper alignment, image attach, auto-resize
 */
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Square, 
  Image as ImageIcon, 
  X,
  Paperclip,
  Sparkles
} from 'lucide-react';

export default function EnhancedChatInput({
  value,
  onChange,
  onSubmit,
  onStop,
  isLoading = false,
  placeholder = "Ask a question...",
  onImageAttach,
  imagePreview,
  onRemoveImage,
  disabled = false
}) {
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [value]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (value.trim() && !isLoading && !disabled) {
      onSubmit?.(value);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onImageAttach) {
      onImageAttach(file);
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-4">
        {/* Image Preview */}
        <AnimatePresence>
          {imagePreview && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="mb-3"
            >
              <div className="inline-flex items-start gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                <img
                  src={imagePreview}
                  alt="Upload preview"
                  className="h-16 w-16 object-cover rounded-lg"
                />
                <button
                  onClick={onRemoveImage}
                  className="p-1 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Input Container - ENHANCED with visual depth */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end gap-3 bg-white dark:bg-gray-800 rounded-2xl border-2 border-gray-200 dark:border-gray-700 focus-within:border-violet-400 dark:focus-within:border-violet-500 focus-within:ring-4 focus-within:ring-violet-100 dark:focus-within:ring-violet-900/30 focus-within:bg-white shadow-sm hover:shadow-md focus-within:shadow-lg transition-all duration-200">
            {/* Image Attach Button - ENHANCED */}
            <button
              type="button"
              onClick={handleImageClick}
              disabled={isLoading || disabled}
              className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-xl text-gray-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Attach image (Ctrl+U)"
              aria-label="Attach image"
            >
              <ImageIcon className="w-5 h-5" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />

            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading || disabled}
              rows={1}
              className="flex-1 py-3 bg-transparent border-0 focus:ring-0 resize-none text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-sm leading-relaxed max-h-[150px] disabled:opacity-50"
              style={{ outline: 'none' }}
            />

            {/* Send / Stop Button */}
            <div className="flex-shrink-0 p-2">
              {isLoading ? (
                <motion.button
                  type="button"
                  onClick={onStop}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center justify-center w-10 h-10 bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-lg shadow-red-500/30 transition-all duration-200"
                  title="Stop generating"
                >
                  <Square className="w-4 h-4 fill-current" />
                </motion.button>
              ) : (
                <motion.button
                  type="submit"
                  disabled={!value.trim() || disabled}
                  whileHover={{ scale: value.trim() ? 1.05 : 1, y: value.trim() ? -1 : 0 }}
                  whileTap={{ scale: value.trim() ? 0.95 : 1 }}
                  className={`flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 ${
                    value.trim() && !disabled
                      ? 'bg-gradient-to-br from-violet-500 via-purple-500 to-violet-600 hover:from-violet-600 hover:via-purple-600 hover:to-violet-700 text-white shadow-lg shadow-violet-500/40 hover:shadow-violet-500/50'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                  }`}
                  title="Send message (Enter)"
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5" />
                </motion.button>
              )}
            </div>
          </div>

          {/* Helper Text */}
          <div className="flex items-center justify-between mt-2 px-1">
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Press <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-gray-500 dark:text-gray-400 font-mono text-[10px]">Enter</kbd> to send • <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-gray-500 dark:text-gray-400 font-mono text-[10px]">Shift+Enter</kbd> for new line
            </p>
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-1.5 text-xs text-purple-500"
              >
                <Sparkles className="w-3 h-3 animate-pulse" />
                <span>Thinking...</span>
              </motion.div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}


