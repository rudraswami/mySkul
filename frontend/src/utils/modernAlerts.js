/**
 * Replace legacy alert() calls with modern toast notifications
 * 
 * Usage:
 * import { showAlert, showConfirm } from './utils/modernAlerts';
 * 
 * showAlert.success('Success!', 'Your changes have been saved');
 * showAlert.error('Error', 'Something went wrong');
 * 
 * const result = await showConfirm('Delete this item?', 'This cannot be undone');
 * if (result) {
 *   // User confirmed
 * }
 */

// This will be initialized by App.js
let toastContext = null;
let modalContext = null;

export const initializeAlerts = (toast, modal) => {
  toastContext = toast;
  modalContext = modal;
};

/**
 * Modern toast-based alerts
 */
export const showAlert = {
  success: (title, message) => {
    if (toastContext) {
      toastContext.success(title, message);
    } else {
      console.warn('[showAlert] Toast context not initialized');
      alert(`${title}: ${message}`);
    }
  },

  error: (title, message) => {
    if (toastContext) {
      toastContext.error(title, message);
    } else {
      console.error('[showAlert] Toast context not initialized');
      alert(`Error - ${title}: ${message}`);
    }
  },

  warning: (title, message) => {
    if (toastContext) {
      toastContext.warning(title, message);
    } else {
      console.warn('[showAlert] Toast context not initialized');
      alert(`Warning - ${title}: ${message}`);
    }
  },

  info: (title, message) => {
    if (toastContext) {
      toastContext.info(title, message);
    } else {
      console.info('[showAlert] Toast context not initialized');
      alert(`${title}: ${message}`);
    }
  },
};

/**
 * Modern modal-based confirmation
 * Returns a Promise that resolves to true/false
 */
export const showConfirm = (title, message, options = {}) => {
  return new Promise((resolve) => {
    if (modalContext) {
      modalContext.openModal({
        type: 'confirm',
        title: title || 'Confirm Action',
        content: message,
        variant: options.variant || 'warning',
        confirmText: options.confirmText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        onConfirm: () => {
          resolve(true);
        },
        onClose: () => {
          resolve(false);
        },
        size: 'small',
      });
    } else {
      console.warn('[showConfirm] Modal context not initialized');
      resolve(window.confirm(`${title}\n\n${message}`));
    }
  });
};

/**
 * Replace window.alert with toast
 */
export const replaceGlobalAlert = () => {
  const originalAlert = window.alert;
  
  window.alert = (message) => {
    if (toastContext) {
      toastContext.info('Alert', message);
    } else {
      originalAlert.call(window, message);
    }
  };
  
  // Store original for restoration
  window._originalAlert = originalAlert;
};

/**
 * Restore window.alert
 */
export const restoreGlobalAlert = () => {
  if (window._originalAlert) {
    window.alert = window._originalAlert;
    delete window._originalAlert;
  }
};

export default showAlert;
