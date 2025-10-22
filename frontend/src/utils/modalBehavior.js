/**
 * Global Modal Behavior Utility
 * 
 * Provides consistent modal behavior across the application:
 * - Focus trap
 * - Scroll lock
 * - ESC key handling
 * - Outside click handling
 * - Backdrop rendering
 * - Accessibility attributes
 * 
 * Usage:
 *   useEffect(() => {
 *     if (isOpen && modalRef.current) {
 *       return applyGlobalModalBehavior(modalRef.current, {
 *         trapFocus: true,
 *         outsideClick: true,
 *         onClose: handleClose
 *       });
 *     }
 *   }, [isOpen]);
 */

import { MODAL_BEHAVIOR } from '../config/modalConfig';

/**
 * Ensure modal is visible within viewport
 * Automatically scrolls modal into view if it's off-viewport
 * 
 * @param {HTMLElement} element - The modal element
 */
export const ensureModalInView = (element) => {
  if (!element) return;
  
  // Use requestAnimationFrame to ensure DOM is painted
  requestAnimationFrame(() => {
    const rect = element.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Check if modal is off-viewport vertically or horizontally
    const isOffViewportVertical = rect.top < 0 || rect.bottom > viewportHeight;
    const isOffViewportHorizontal = rect.left < 0 || rect.right > viewportWidth;
    
    if (isOffViewportVertical || isOffViewportHorizontal) {
      element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center',
        inline: 'center'
      });
    }
  });
};

/**
 * Apply global modal behavior to a modal element
 * 
 * @param {HTMLElement} element - The modal container element
 * @param {Object} options - Configuration options
 * @param {boolean} [options.trapFocus=true] - Enable focus trapping
 * @param {boolean} [options.outsideClick=true] - Close on outside click
 * @param {Function} options.onClose - Callback to close the modal
 * @param {boolean} [options.scrollLock=true] - Lock body scroll
 * @param {boolean} [options.closeOnEsc=true] - Close on ESC key
 * @param {boolean} [options.ensureInView=true] - Ensure modal is visible in viewport
 * @returns {Function} Cleanup function to remove behavior
 */
export const applyGlobalModalBehavior = (element, options = {}) => {
  const {
    trapFocus = MODAL_BEHAVIOR.keyboard.focusTrap,
    outsideClick = MODAL_BEHAVIOR.outsideClick.enabled,
    onClose,
    scrollLock = true,
    closeOnEsc = MODAL_BEHAVIOR.keyboard.closeOnEsc,
    ensureInView = true
  } = options;

  // Store original body overflow
  const originalOverflow = document.body.style.overflow;
  const originalPaddingRight = document.body.style.paddingRight;

  // 1. Lock body scroll
  if (scrollLock) {
    // Get scrollbar width to prevent layout shift
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.overflow = 'hidden';
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }
  }

  // 2. Ensure modal is visible in viewport
  if (ensureInView) {
    ensureModalInView(element);
  }

  // 3. Set accessibility attributes
  element.setAttribute('role', MODAL_BEHAVIOR.a11y.role);
  element.setAttribute('aria-modal', String(MODAL_BEHAVIOR.a11y.ariaModal));
  
  // Try to find and set aria-labelledby
  const titleElement = element.querySelector('h1, h2, h3, [id*="title"], [class*="title"]');
  if (titleElement) {
    if (!titleElement.id) {
      titleElement.id = `modal-title-${Date.now()}`;
    }
    element.setAttribute('aria-labelledby', titleElement.id);
  }

  // 4. Focus trap implementation
  let focusTrapCleanup = null;
  if (trapFocus) {
    focusTrapCleanup = enableFocusTrap(element);
  }

  // 5. ESC key handler
  const handleEscape = (e) => {
    if (closeOnEsc && e.key === 'Escape' && onClose) {
      e.preventDefault();
      e.stopPropagation();
      onClose();
    }
  };
  
  document.addEventListener('keydown', handleEscape, true);

  // 6. Outside click handler (optional)
  let clickHandler = null;
  if (outsideClick && onClose) {
    clickHandler = (e) => {
      // Check if click is outside the modal content
      if (element && !element.contains(e.target)) {
        // Check if click is on backdrop (not on nested elements)
        const backdrop = document.querySelector('.modal-backdrop, [data-modal-backdrop]');
        if (backdrop && (e.target === backdrop || backdrop.contains(e.target))) {
          onClose();
        }
      }
    };
    // Use capture phase to handle before other handlers
    document.addEventListener('mousedown', clickHandler, true);
  }

  // Return cleanup function
  return () => {
    // Restore body scroll
    if (scrollLock) {
      document.body.style.overflow = originalOverflow;
      document.body.style.paddingRight = originalPaddingRight;
    }

    // Remove event listeners
    document.removeEventListener('keydown', handleEscape, true);
    if (clickHandler) {
      document.removeEventListener('mousedown', clickHandler, true);
    }

    // Remove focus trap
    if (focusTrapCleanup) {
      focusTrapCleanup();
    }

    // Remove accessibility attributes
    element.removeAttribute('role');
    element.removeAttribute('aria-modal');
    element.removeAttribute('aria-labelledby');
  };
};

/**
 * Enable focus trap within modal
 * Keeps focus inside modal, cycling through focusable elements
 * 
 * @param {HTMLElement} element - The modal container
 * @returns {Function} Cleanup function
 */
function enableFocusTrap(element) {
  // Get all focusable elements
  const getFocusableElements = () => {
    return element.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
  };

  // Store the element that had focus before modal opened
  const previousActiveElement = document.activeElement;

  // Focus first focusable element in modal
  const focusableElements = getFocusableElements();
  if (focusableElements.length > 0) {
    focusableElements[0].focus();
  }

  // Tab key handler
  const handleTab = (e) => {
    if (e.key !== 'Tab') return;

    const focusable = Array.from(getFocusableElements());
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    if (focusable.length === 0) {
      e.preventDefault();
      return;
    }

    // Shift + Tab
    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
    }
    // Tab
    else {
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  };

  element.addEventListener('keydown', handleTab);

  // Cleanup function
  return () => {
    element.removeEventListener('keydown', handleTab);
    // Restore focus to previous element
    if (previousActiveElement && previousActiveElement.focus) {
      previousActiveElement.focus();
    }
  };
}

/**
 * Get Framer Motion animation props for modal
 * 
 * @param {string} type - Animation type ('modal' or 'backdrop')
 * @returns {Object} Framer Motion props
 */
export const getModalAnimationProps = (type = 'modal') => {
  const animation = MODAL_BEHAVIOR.animation[type];
  return {
    initial: animation.initial,
    animate: animation.animate,
    exit: animation.exit,
    transition: {
      duration: MODAL_BEHAVIOR.animation.duration,
      ease: MODAL_BEHAVIOR.animation.easing
    }
  };
};

/**
 * Get backdrop style based on config
 * 
 * @returns {Object} Style object for backdrop
 */
export const getBackdropStyle = () => {
  const { color, blur, blurAmount } = MODAL_BEHAVIOR.backdrop;
  return {
    backgroundColor: color,
    backdropFilter: blur ? `blur(${blurAmount})` : 'none',
    WebkitBackdropFilter: blur ? `blur(${blurAmount})` : 'none',
    zIndex: MODAL_BEHAVIOR.zIndex.backdrop
  };
};

/**
 * Get modal container style - for the wrapper that centers the modal
 * 
 * @param {Object} overrides - Style overrides
 * @returns {Object} Style object for modal container
 */
export const getModalContainerStyle = (overrides = {}) => {
  return {
    zIndex: MODAL_BEHAVIOR.zIndex.modal,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: MODAL_BEHAVIOR.viewport.verticalMargin,
    ...overrides
  };
};

/**
 * Get modal content style - for the actual modal content with scrolling
 * 
 * @param {Object} overrides - Style overrides
 * @returns {Object} Style object for modal content
 */
export const getModalContentStyle = (overrides = {}) => {
  return {
    maxHeight: MODAL_BEHAVIOR.viewport.maxHeight,
    overflowY: 'auto',
    borderRadius: MODAL_BEHAVIOR.style.borderRadius,
    boxShadow: MODAL_BEHAVIOR.style.shadow,
    maxWidth: MODAL_BEHAVIOR.style.maxWidth,
    ...overrides
  };
};

/**
 * Get modal style based on config (legacy - kept for backward compatibility)
 * 
 * @param {Object} overrides - Style overrides
 * @returns {Object} Style object for modal
 */
export const getModalStyle = (overrides = {}) => {
  return getModalContentStyle(overrides);
};

/**
 * Get CSS class names for modal elements with correct z-index
 * 
 * @returns {Object} Class name strings for modal elements
 */
export const getModalClassNames = () => {
  return {
    backdrop: `fixed inset-0`,
    container: `fixed inset-0 flex items-center justify-center p-4 pointer-events-none`,
    content: `w-full pointer-events-auto max-h-[90vh] overflow-y-auto`,
  };
};

/**
 * Get inline styles for modal elements (for direct style attribute usage)
 * 
 * @returns {Object} Style objects for modal elements
 */
export const getModalInlineStyles = () => {
  return {
    backdrop: {
      ...getBackdropStyle(),
      position: 'fixed',
      inset: 0
    },
    container: {
      ...getModalContainerStyle(),
      position: 'fixed',
      inset: 0,
      pointerEvents: 'none'
    },
    content: {
      ...getModalContentStyle(),
      pointerEvents: 'auto',
      width: '100%'
    }
  };
};

/**
 * Hook for modal behavior (React hook version)
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} Modal behavior utilities
 */
export const useModalBehavior = (options = {}) => {
  const { isOpen, onClose, modalRef } = options;

  React.useEffect(() => {
    if (isOpen && modalRef?.current) {
      return applyGlobalModalBehavior(modalRef.current, {
        ...options,
        onClose
      });
    }
  }, [isOpen, onClose, modalRef, options]);

  return {
    backdropProps: getModalAnimationProps('backdrop'),
    modalProps: getModalAnimationProps('modal'),
    backdropStyle: getBackdropStyle(),
    modalStyle: getModalStyle(options.styleOverrides),
    classNames: getModalClassNames(),
    inlineStyles: getModalInlineStyles()
  };
};
