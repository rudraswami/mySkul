/**
 * Keyboard Shortcuts Hook
 * Manages global keyboard shortcuts for the AI Tutor
 */
import { useEffect, useCallback, useState } from 'react';

const DEFAULT_SHORTCUTS = {
  newChat: { key: 'n', modifiers: ['ctrl'], description: 'Start new chat' },
  focusInput: { key: '/', modifiers: [], description: 'Focus input' },
  toggleSidebar: { key: 'b', modifiers: ['ctrl'], description: 'Toggle sidebar' },
  escape: { key: 'Escape', modifiers: [], description: 'Close modal/panel' },
  search: { key: 'k', modifiers: ['ctrl'], description: 'Search chats' },
  sendMessage: { key: 'Enter', modifiers: [], description: 'Send message' },
  newLine: { key: 'Enter', modifiers: ['shift'], description: 'New line' },
  stopGeneration: { key: 'Escape', modifiers: [], description: 'Stop AI generation' }
};

export const useKeyboardShortcuts = (handlers = {}, enabled = true) => {
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false);

  const handleKeyDown = useCallback((event) => {
    if (!enabled) return;
    
    // Don't trigger shortcuts when typing in inputs (except for specific ones)
    const isInputFocused = ['INPUT', 'TEXTAREA', 'SELECT'].includes(
      document.activeElement?.tagName
    );
    
    const { key, ctrlKey, metaKey, shiftKey, altKey } = event;
    const modCtrl = ctrlKey || metaKey; // Support both Ctrl and Cmd (Mac)

    // New Chat: Ctrl/Cmd + N
    if (modCtrl && key.toLowerCase() === 'n' && !isInputFocused) {
      event.preventDefault();
      handlers.onNewChat?.();
      return;
    }

    // Focus Input: / (when not in input)
    if (key === '/' && !isInputFocused) {
      event.preventDefault();
      handlers.onFocusInput?.();
      return;
    }

    // Toggle Sidebar: Ctrl/Cmd + B
    if (modCtrl && key.toLowerCase() === 'b') {
      event.preventDefault();
      handlers.onToggleSidebar?.();
      return;
    }

    // Search: Ctrl/Cmd + K
    if (modCtrl && key.toLowerCase() === 'k') {
      event.preventDefault();
      handlers.onSearch?.();
      return;
    }

    // Escape: Close modal/panel or stop generation
    if (key === 'Escape') {
      if (handlers.onStopGeneration) {
        handlers.onStopGeneration();
      }
      handlers.onEscape?.();
      setShowShortcutsHelp(false);
      return;
    }

    // Show shortcuts help: Ctrl/Cmd + /
    if (modCtrl && key === '/') {
      event.preventDefault();
      setShowShortcutsHelp(prev => !prev);
      return;
    }

    // Send message: Enter (when in textarea and not with shift)
    if (key === 'Enter' && !shiftKey && isInputFocused) {
      // This is handled by the input component directly
      return;
    }

  }, [enabled, handlers]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    showShortcutsHelp,
    setShowShortcutsHelp,
    shortcuts: DEFAULT_SHORTCUTS
  };
};

/**
 * Keyboard Shortcuts Help Panel Component
 */
export const ShortcutsHelpPanel = ({ show, onClose }) => {
  if (!show) return null;

  const shortcuts = [
    { keys: ['Ctrl', 'N'], description: 'Start new chat' },
    { keys: ['/'], description: 'Focus input' },
    { keys: ['Ctrl', 'B'], description: 'Toggle sidebar' },
    { keys: ['Ctrl', 'K'], description: 'Search chats' },
    { keys: ['Enter'], description: 'Send message' },
    { keys: ['Shift', 'Enter'], description: 'New line' },
    { keys: ['Esc'], description: 'Stop generation / Close' },
    { keys: ['Ctrl', '/'], description: 'Show shortcuts' }
  ];

  return (
    <div 
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[600] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Keyboard Shortcuts
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Speed up your workflow
          </p>
        </div>
        
        <div className="px-6 py-4 space-y-3">
          {shortcuts.map(({ keys, description }) => (
            <div 
              key={keys.join('+')} 
              className="flex items-center justify-between"
            >
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {description}
              </span>
              <div className="flex items-center gap-1">
                {keys.map((key, i) => (
                  <span key={i}>
                    <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono text-gray-700 dark:text-gray-300 shadow-sm">
                      {key}
                    </kbd>
                    {i < keys.length - 1 && (
                      <span className="text-gray-400 mx-0.5">+</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-900/50 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Press <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Esc</kbd> or click outside to close
          </p>
        </div>
      </div>
    </div>
  );
};

export default useKeyboardShortcuts;






