import React, { useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, CheckCircle, Info, AlertCircle } from 'lucide-react';
import { useModal, ModalType } from '../contexts/ModalContext';
import { Button } from './ui/button';

/**
 * Global Modal Renderer
 * Renders all active modals with consistent styling and animations
 */

const Modal = ({ modal }) => {
  const { closeModal } = useModal();
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);

  // Save previous focus element and trap focus
  useEffect(() => {
    previousFocusRef.current = document.activeElement;

    // Set initial focus to modal
    if (modalRef.current) {
      modalRef.current.focus();
    }

    // Focus trap
    const handleTabKey = (e) => {
      if (!modalRef.current) return;

      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    // ESC key to close
    const handleEscKey = (e) => {
      if (e.key === 'Escape' && modal.closable) {
        closeModal(modal.id);
      }
    };

    document.addEventListener('keydown', handleTabKey);
    document.addEventListener('keydown', handleEscKey);

    return () => {
      document.removeEventListener('keydown', handleTabKey);
      document.removeEventListener('keydown', handleEscKey);
      
      // Restore previous focus
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    };
  }, [modal, closeModal]);

  // Modal size classes
  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-2xl',
    large: 'max-w-4xl',
    xlarge: 'max-w-6xl',
    full: 'max-w-full mx-4',
  };

  // Variant styles
  const variantStyles = {
    default: {
      headerBg: 'bg-gradient-to-r from-purple-600 to-blue-600',
      icon: null,
    },
    success: {
      headerBg: 'bg-gradient-to-r from-green-500 to-teal-500',
      icon: CheckCircle,
    },
    error: {
      headerBg: 'bg-gradient-to-r from-red-500 to-pink-500',
      icon: AlertCircle,
    },
    warning: {
      headerBg: 'bg-gradient-to-r from-yellow-500 to-orange-500',
      icon: AlertTriangle,
    },
    info: {
      headerBg: 'bg-gradient-to-r from-blue-500 to-indigo-500',
      icon: Info,
    },
  };

  // Animation variants
  const animations = {
    'fade': {
      initial: { opacity: 0 },
      animate: { opacity: 1 },
      exit: { opacity: 0 },
    },
    'fade-scale': {
      initial: { opacity: 0, scale: 0.95 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.95 },
    },
    'slide-up': {
      initial: { opacity: 0, y: 50 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: 50 },
    },
    'slide-down': {
      initial: { opacity: 0, y: -50 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -50 },
    },
  };

  const variant = variantStyles[modal.variant] || variantStyles.default;
  const Icon = variant.icon;
  const animation = animations[modal.animation] || animations['fade-scale'];

  const handleConfirm = async () => {
    if (modal.onConfirm) {
      const result = await modal.onConfirm();
      // Only close if confirm handler doesn't return false
      if (result !== false) {
        closeModal(modal.id);
      }
    } else {
      closeModal(modal.id);
    }
  };

  const handleClose = () => {
    closeModal(modal.id);
  };

  // Render custom component if provided
  if (modal.component) {
    const Component = modal.component;
    return (
      <div
        className="fixed inset-0 flex items-center justify-center p-4"
        style={{ zIndex: modal.zIndex }}
        onClick={(e) => e.stopPropagation()}
      >
        <Component
          modal={modal}
          onClose={handleClose}
          {...modal.metadata}
        />
      </div>
    );
  }

  return (
    <motion.div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby={`modal-title-${modal.id}`}
      tabIndex={-1}
      className={`fixed inset-0 flex items-center justify-center p-4 ${sizeClasses[modal.size]}`}
      style={{ zIndex: modal.zIndex, margin: 'auto' }}
      onClick={(e) => e.stopPropagation()}
      {...animation}
      transition={{ duration: 0.2 }}
    >
      <div className="bg-white rounded-2xl shadow-2xl overflow-hidden w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        {modal.title && (
          <div className={`${variant.headerBg} p-6 text-white relative`}>
            {modal.closable && (
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            )}

            <div className="flex items-center space-x-3">
              {Icon && <Icon className="w-8 h-8" />}
              <h2 id={`modal-title-${modal.id}`} className="text-2xl font-bold">
                {modal.title}
              </h2>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {typeof modal.content === 'string' ? (
            <p className="text-gray-700 leading-relaxed">{modal.content}</p>
          ) : (
            modal.content
          )}
        </div>

        {/* Footer with actions */}
        {(modal.type === ModalType.CONFIRM || modal.type === ModalType.ALERT || modal.customActions) && (
          <div className="p-6 bg-gray-50 border-t border-gray-200">
            {modal.customActions ? (
              <div className="flex flex-col sm:flex-row gap-3">
                {modal.customActions}
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={handleConfirm}
                  className={`flex-1 py-3 rounded-xl font-semibold ${
                    modal.variant === 'error' || modal.variant === 'warning'
                      ? 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
                  } text-white shadow-lg hover:shadow-xl transition-all`}
                >
                  {modal.confirmText}
                </Button>

                {modal.showCancel && (
                  <Button
                    onClick={handleClose}
                    variant="outline"
                    className="flex-1 py-3 rounded-xl font-semibold hover:bg-gray-100 transition-all"
                  >
                    {modal.cancelText}
                  </Button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

const ModalRenderer = () => {
  const { modals } = useModal();

  // Find modal root or create it
  const modalRoot = document.getElementById('modal-root') || (() => {
    const root = document.createElement('div');
    root.id = 'modal-root';
    document.body.appendChild(root);
    return root;
  })();

  return ReactDOM.createPortal(
    <AnimatePresence>
      {modals.map((modal, index) => (
        <React.Fragment key={modal.id}>
          {/* Backdrop */}
          {modal.backdrop && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-40"
              style={{ 
                zIndex: modal.zIndex - 1,
                backdropFilter: modal.backdropBlur ? 'blur(6px)' : 'none',
                WebkitBackdropFilter: modal.backdropBlur ? 'blur(6px)' : 'none',
              }}
              onClick={() => modal.closable && modal.closeModal(modal.id)}
            />
          )}

          {/* Modal */}
          <Modal modal={modal} />
        </React.Fragment>
      ))}
    </AnimatePresence>,
    modalRoot
  );
};

export default ModalRenderer;
