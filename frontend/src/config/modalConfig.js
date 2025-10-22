/**
 * Global Modal Configuration
 * 
 * Shared constants for consistent modal behavior across the application.
 * All modals should reference these values instead of hardcoding styles/durations.
 * 
 * Usage:
 *   import { MODAL_BEHAVIOR } from '../config/modalConfig';
 *   duration: MODAL_BEHAVIOR.animation.duration
 */

export const MODAL_BEHAVIOR = {
  // Animation settings
  animation: {
    duration: 0.15, // 150ms - snappy but perceptible
    easing: "easeInOut", // No bounce or spring
    
    // Framer Motion variants
    backdrop: {
      initial: { opacity: 0 },
      animate: { opacity: 1 },
      exit: { opacity: 0 }
    },
    modal: {
      initial: { opacity: 0, scale: 0.95, y: 10 },
      animate: { opacity: 1, scale: 1, y: 0 },
      exit: { opacity: 0, scale: 0.95, y: 10 }
    }
  },
  
  // Backdrop settings
  backdrop: {
    color: "rgba(0, 0, 0, 0.4)", // Semi-transparent black
    blur: true, // Apply backdrop-filter blur
    blurAmount: "6px"
  },
  
  // Visual styling
  style: {
    borderRadius: "16px", // Consistent rounded corners
    shadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)", // Elevation shadow
    maxWidth: "600px", // Default max width (can be overridden)
  },
  
  // Keyboard behavior
  keyboard: {
    closeOnEsc: true, // ESC key closes modal
    focusTrap: true, // Trap focus within modal
  },
  
  // Click behavior
  outsideClick: {
    enabled: true, // Click outside closes modal (can be overridden per modal)
  },
  
  // Z-index layering (must align with existing CSS)
  // Updated to enforce global viewport visibility
  zIndex: {
    backdrop: 9490,      // Backdrop layer
    modal: 9500,         // Base modal layer
    nested: 9600,        // For modals that open on top of other modals
    floatingUI: 9400     // Floating UI elements below modals
  },
  
  // Viewport constraints
  viewport: {
    maxHeight: "90vh",         // Maximum modal height
    verticalMargin: "2rem",    // Vertical spacing from viewport edges
    horizontalMargin: "1rem"   // Horizontal spacing from viewport edges
  },
  
  // Accessibility
  a11y: {
    role: "dialog",
    ariaModal: true,
    ariaLabelledBy: "modal-title", // ID of modal title element
    ariaDescribedBy: "modal-description", // ID of modal description
  }
};

/**
 * Modal Type Presets
 * 
 * Common modal configurations for different use cases
 */
export const MODAL_PRESETS = {
  // Standard confirmation dialog
  confirmation: {
    ...MODAL_BEHAVIOR,
    outsideClick: { enabled: true },
    style: { ...MODAL_BEHAVIOR.style, maxWidth: "400px" }
  },
  
  // Full-screen or large content modals
  fullContent: {
    ...MODAL_BEHAVIOR,
    outsideClick: { enabled: false }, // Prevent accidental close
    style: { ...MODAL_BEHAVIOR.style, maxWidth: "900px" }
  },
  
  // Alert/notification modals
  alert: {
    ...MODAL_BEHAVIOR,
    outsideClick: { enabled: false }, // Force user interaction
    keyboard: { ...MODAL_BEHAVIOR.keyboard, closeOnEsc: false }
  },
  
  // Exam/Test modals (no accidental close)
  exam: {
    ...MODAL_BEHAVIOR,
    outsideClick: { enabled: false },
    keyboard: { ...MODAL_BEHAVIOR.keyboard, closeOnEsc: false }
  }
};

/**
 * CSS Class Names
 * 
 * Consistent class names for modal elements
 */
export const MODAL_CLASSES = {
  backdrop: "modal-backdrop",
  container: "modal-container",
  content: "modal-content",
  header: "modal-header",
  body: "modal-body",
  footer: "modal-footer",
  closeButton: "modal-close-btn"
};
