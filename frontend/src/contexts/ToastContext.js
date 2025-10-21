import React, { createContext, useContext, useState, useCallback } from 'react';

/**
 * Global Toast Context for notifications and alerts
 */

const ToastContext = createContext(undefined);

export const ToastType = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

export const ToastPosition = {
  TOP_LEFT: 'top-left',
  TOP_CENTER: 'top-center',
  TOP_RIGHT: 'top-right',
  BOTTOM_LEFT: 'bottom-left',
  BOTTOM_CENTER: 'bottom-center',
  BOTTOM_RIGHT: 'bottom-right',
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({
    type = ToastType.INFO,
    title,
    message,
    duration = 5000,
    position = ToastPosition.TOP_RIGHT,
    action,
    onClose,
  }) => {
    const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const toast = {
      id: toastId,
      type,
      title,
      message,
      position,
      action,
      onClose,
      timestamp: Date.now(),
    };

    setToasts(prev => [...prev, toast]);

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(toastId);
      }, duration);
    }

    return toastId;
  }, []);

  const removeToast = useCallback((toastId) => {
    const toast = toasts.find(t => t.id === toastId);
    if (toast?.onClose) {
      toast.onClose();
    }
    setToasts(prev => prev.filter(t => t.id !== toastId));
  }, [toasts]);

  const clearAllToasts = useCallback(() => {
    toasts.forEach(toast => {
      if (toast.onClose) {
        toast.onClose();
      }
    });
    setToasts([]);
  }, [toasts]);

  // Convenience methods
  const success = useCallback((title, message, options = {}) => {
    return addToast({ type: ToastType.SUCCESS, title, message, ...options });
  }, [addToast]);

  const error = useCallback((title, message, options = {}) => {
    return addToast({ type: ToastType.ERROR, title, message, ...options });
  }, [addToast]);

  const warning = useCallback((title, message, options = {}) => {
    return addToast({ type: ToastType.WARNING, title, message, ...options });
  }, [addToast]);

  const info = useCallback((title, message, options = {}) => {
    return addToast({ type: ToastType.INFO, title, message, ...options });
  }, [addToast]);

  const value = {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    success,
    error,
    warning,
    info,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export default ToastContext;
