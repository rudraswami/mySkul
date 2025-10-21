import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { useToast, ToastType, ToastPosition } from '../contexts/ToastContext';

/**
 * Global Toast Renderer
 * Renders notification toasts in consistent positions
 */

const Toast = ({ toast }) => {
  const { removeToast } = useToast();

  // Auto-close timer display
  useEffect(() => {
    return () => {
      // Cleanup
    };
  }, []);

  const icons = {
    [ToastType.SUCCESS]: {
      Icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-200',
    },
    [ToastType.ERROR]: {
      Icon: AlertCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
    },
    [ToastType.WARNING]: {
      Icon: AlertTriangle,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
    },
    [ToastType.INFO]: {
      Icon: Info,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
    },
  };

  const { Icon, color, bg, border } = icons[toast.type] || icons[ToastType.INFO];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`${bg} ${border} border-2 rounded-xl shadow-xl p-4 mb-3 min-w-[300px] max-w-md`}
    >
      <div className="flex items-start gap-3">
        <Icon className={`${color} w-5 h-5 flex-shrink-0 mt-0.5`} />
        
        <div className="flex-1 min-w-0">
          {toast.title && (
            <h4 className="font-semibold text-gray-900 mb-1">{toast.title}</h4>
          )}
          {toast.message && (
            <p className="text-sm text-gray-700 leading-relaxed">{toast.message}</p>
          )}
          {toast.action && (
            <button
              onClick={toast.action.onClick}
              className={`mt-2 text-sm font-medium ${color} hover:underline`}
            >
              {toast.action.label}
            </button>
          )}
        </div>

        <button
          onClick={() => removeToast(toast.id)}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
};

const ToastRenderer = () => {
  const { toasts } = useToast();

  // Group toasts by position
  const toastsByPosition = toasts.reduce((acc, toast) => {
    const position = toast.position || ToastPosition.TOP_RIGHT;
    if (!acc[position]) {
      acc[position] = [];
    }
    acc[position].push(toast);
    return acc;
  }, {});

  // Position styles
  const positionClasses = {
    [ToastPosition.TOP_LEFT]: 'top-4 left-4',
    [ToastPosition.TOP_CENTER]: 'top-4 left-1/2 -translate-x-1/2',
    [ToastPosition.TOP_RIGHT]: 'top-4 right-4',
    [ToastPosition.BOTTOM_LEFT]: 'bottom-4 left-4',
    [ToastPosition.BOTTOM_CENTER]: 'bottom-4 left-1/2 -translate-x-1/2',
    [ToastPosition.BOTTOM_RIGHT]: 'bottom-4 right-4',
  };

  // Find toast root or create it
  const toastRoot = document.getElementById('toast-root') || (() => {
    const root = document.createElement('div');
    root.id = 'toast-root';
    document.body.appendChild(root);
    return root;
  })();

  return ReactDOM.createPortal(
    <>
      {Object.entries(toastsByPosition).map(([position, positionToasts]) => (
        <div
          key={position}
          className={`fixed ${positionClasses[position]} z-[10000] pointer-events-none`}
        >
          <div className="pointer-events-auto">
            <AnimatePresence>
              {positionToasts.map(toast => (
                <Toast key={toast.id} toast={toast} />
              ))}
            </AnimatePresence>
          </div>
        </div>
      ))}
    </>,
    toastRoot
  );
};

export default ToastRenderer;
