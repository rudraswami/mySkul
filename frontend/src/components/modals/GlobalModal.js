import React, { useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  applyGlobalModalBehavior,
  getBackdropStyle,
  getModalContainerStyle,
  getModalContentStyle,
  getModalAnimationProps
} from '../../utils/modalBehavior';

/**
 * GlobalModal
 * Provides a consistent modal shell with scroll locking, focus trap, and z-index handling.
 */
const GlobalModal = ({
  isOpen,
  onClose,
  children,
  maxWidth = '36rem',
  closeOnBackdrop = true,
  trapFocus = true,
  closeOnEsc = true,
  scrollLock = true,
  ariaLabel = 'dialog'
}) => {
  const contentRef = useRef(null);

  useEffect(() => {
    if (isOpen && contentRef.current) {
      return applyGlobalModalBehavior(contentRef.current, {
        trapFocus,
        outsideClick: closeOnBackdrop,
        onClose,
        scrollLock,
        closeOnEsc,
        ensureInView: true
      });
    }
  }, [isOpen, trapFocus, closeOnBackdrop, onClose, scrollLock, closeOnEsc]);

  if (!isOpen) return null;

  const backdropStyle = getBackdropStyle();
  const containerStyle = getModalContainerStyle();
  const contentStyle = getModalContentStyle({ maxWidth });
  const backdropAnimation = getModalAnimationProps('backdrop');
  const modalAnimation = getModalAnimationProps('modal');

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            {...backdropAnimation}
            style={backdropStyle}
            className="fixed inset-0"
            data-modal-backdrop="true"
            onClick={() => {
              if (closeOnBackdrop && onClose) {
                onClose();
              }
            }}
          />
          <motion.div
            {...modalAnimation}
            style={containerStyle}
            className="fixed inset-0 p-4 pointer-events-none"
          >
            <div
              ref={contentRef}
              style={contentStyle}
              className="pointer-events-auto bg-white rounded-2xl shadow-2xl overflow-hidden"
              role="dialog"
              aria-label={ariaLabel}
            >
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default GlobalModal;

