/**
 * Accessibility Utilities
 * Helpers for keyboard navigation, screen readers, and WCAG compliance
 */

/**
 * Screen reader only class (visually hidden but accessible)
 * Usage: <span className={srOnly()}>Hidden text for screen readers</span>
 */
export function srOnly() {
  return 'sr-only';
}

/**
 * Focus visible class for keyboard navigation
 * Adds visible focus indicators
 */
export function focusVisible() {
  return `
    focus:outline-none
    focus-visible:ring-2
    focus-visible:ring-blue-500
    focus-visible:ring-offset-2
    dark:focus-visible:ring-blue-400
    dark:focus-visible:ring-offset-gray-900
  `.trim().replace(/\s+/g, ' ');
}

/**
 * Skip to main content link for keyboard users
 */
export function SkipToContent() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md"
    >
      Skip to main content
    </a>
  );
}

/**
 * Announce to screen readers dynamically
 * @param {string} message - Message to announce
 * @param {string} priority - 'polite' or 'assertive'
 */
export function announce(message, priority = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Trap focus within a modal or dialog
 * @param {HTMLElement} element - Container element
 * @returns {Function} - Cleanup function
 */
export function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );
  
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];
  
  function handleKeyDown(e) {
    if (e.key !== 'Tab') return;
    
    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        lastFocusable.focus();
        e.preventDefault();
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusable) {
        firstFocusable.focus();
        e.preventDefault();
      }
    }
  }
  
  element.addEventListener('keydown', handleKeyDown);
  
  // Focus first element
  if (firstFocusable) {
    firstFocusable.focus();
  }
  
  // Return cleanup function
  return () => {
    element.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Check if element is visible to screen readers
 */
export function isVisibleToScreenReader(element) {
  return (
    element.offsetParent !== null &&
    getComputedStyle(element).visibility !== 'hidden' &&
    !element.hasAttribute('aria-hidden')
  );
}

/**
 * Get accessible name for element
 */
export function getAccessibleName(element) {
  // Check aria-label
  if (element.hasAttribute('aria-label')) {
    return element.getAttribute('aria-label');
  }
  
  // Check aria-labelledby
  if (element.hasAttribute('aria-labelledby')) {
    const ids = element.getAttribute('aria-labelledby').split(' ');
    return ids.map(id => {
      const labelElement = document.getElementById(id);
      return labelElement ? labelElement.textContent : '';
    }).join(' ');
  }
  
  // Check label element
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) {
      return label.textContent;
    }
  }
  
  // Check alt text for images
  if (element.tagName === 'IMG' && element.hasAttribute('alt')) {
    return element.getAttribute('alt');
  }
  
  // Check title attribute
  if (element.hasAttribute('title')) {
    return element.getAttribute('title');
  }
  
  // Fallback to text content
  return element.textContent;
}

/**
 * Color contrast utilities for WCAG compliance
 */
export const colorContrast = {
  /**
   * Calculate relative luminance
   */
  getLuminance(hex) {
    const rgb = this.hexToRgb(hex);
    const [r, g, b] = rgb.map(val => {
      val = val / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  },
  
  /**
   * Convert hex to RGB
   */
  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
      parseInt(result[1], 16),
      parseInt(result[2], 16),
      parseInt(result[3], 16)
    ] : [0, 0, 0];
  },
  
  /**
   * Calculate contrast ratio
   */
  getContrastRatio(hex1, hex2) {
    const lum1 = this.getLuminance(hex1);
    const lum2 = this.getLuminance(hex2);
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
  },
  
  /**
   * Check if contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large)
   */
  meetsWCAG_AA(fgHex, bgHex, isLargeText = false) {
    const ratio = this.getContrastRatio(fgHex, bgHex);
    return isLargeText ? ratio >= 3 : ratio >= 4.5;
  },
  
  /**
   * Check if contrast meets WCAG AAA (7:1 for normal text, 4.5:1 for large)
   */
  meetsWCAG_AAA(fgHex, bgHex, isLargeText = false) {
    const ratio = this.getContrastRatio(fgHex, bgHex);
    return isLargeText ? ratio >= 4.5 : ratio >= 7;
  }
};

export default {
  srOnly,
  focusVisible,
  SkipToContent,
  announce,
  trapFocus,
  isVisibleToScreenReader,
  getAccessibleName,
  colorContrast
};
