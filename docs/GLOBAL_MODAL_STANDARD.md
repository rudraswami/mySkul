# Global Modal Standardization

## Overview

This document explains the global modal behavior system implemented across the Dhruv AI application. The system provides consistent behavior, animations, and accessibility features for all modals without requiring component restructuring.

## Architecture

### Core Files

1. **`/src/config/modalConfig.js`** - Global configuration constants
   - Animation settings (duration, easing, Framer Motion variants)
   - Backdrop styling (color, blur)
   - Visual styling (border radius, shadows, max width)
   - Keyboard behavior (ESC key, focus trap)
   - Click behavior (outside click to close)
   - Z-index layering
   - Accessibility attributes

2. **`/src/utils/modalBehavior.js`** - Behavior utility functions
   - `applyGlobalModalBehavior()` - Main utility to apply consistent behavior
   - `enableFocusTrap()` - Internal focus trapping logic
   - `getModalAnimationProps()` - Helper for Framer Motion props
   - `getBackdropStyle()` - Helper for backdrop styling
   - `getModalStyle()` - Helper for modal container styling

## How It Works

### The Non-Invasive Approach

Instead of creating a new modal framework, we created a **behavior layer** that existing modals adopt. This means:

✅ **Keep**: All existing modal components, props, handlers, and logic
✅ **Add**: Import and call `applyGlobalModalBehavior()` in a useEffect
✅ **Result**: Consistent behavior without breaking existing functionality

### What Gets Standardized

1. **Scroll Lock** - Body scroll is locked when modal is open
2. **Focus Trap** - Tab key cycles through modal elements only
3. **ESC Key** - Closes modal (configurable per modal)
4. **Outside Click** - Closes modal when clicking backdrop (configurable)
5. **Animations** - 150ms ease-in-out transitions
6. **Backdrop** - rgba(0,0,0,0.4) with 6px blur
7. **Accessibility** - Proper ARIA attributes automatically applied

## Usage Guide

### Basic Integration

```javascript
import { useEffect, useRef } from 'react';
import { applyGlobalModalBehavior } from '../utils/modalBehavior';

function MyModal({ isOpen, onClose }) {
  const modalRef = useRef(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      return applyGlobalModalBehavior(modalRef.current, {
        trapFocus: true,
        outsideClick: true,
        onClose,
        scrollLock: true,
        closeOnEsc: true
      });
    }
  }, [isOpen, onClose]);

  return (
    <div ref={modalRef} className="modal-container">
      {/* Your existing modal content */}
    </div>
  );
}
```

### With Framer Motion

```javascript
import { motion, AnimatePresence } from 'framer-motion';
import { getModalAnimationProps, getBackdropStyle } from '../utils/modalBehavior';

function MyAnimatedModal({ isOpen, onClose }) {
  const modalRef = useRef(null);
  const backdropAnimation = getModalAnimationProps('backdrop');
  const modalAnimation = getModalAnimationProps('modal');

  useEffect(() => {
    if (isOpen && modalRef.current) {
      return applyGlobalModalBehavior(modalRef.current, {
        trapFocus: true,
        outsideClick: true,
        onClose
      });
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            {...backdropAnimation}
            style={getBackdropStyle()}
            className="fixed inset-0 z-50"
            data-modal-backdrop="true"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            {...modalAnimation}
            ref={modalRef}
            className="fixed inset-0 z-50 flex items-center justify-center"
          >
            {/* Your content */}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### Configuration Options

```javascript
applyGlobalModalBehavior(element, {
  trapFocus: true,        // Enable focus trapping (default: true)
  outsideClick: true,     // Close on outside click (default: true)
  onClose: handleClose,   // Required: callback to close modal
  scrollLock: true,       // Lock body scroll (default: true)
  closeOnEsc: true        // Close on ESC key (default: true)
});
```

### Modal Presets

For common modal types, use predefined presets:

```javascript
import { MODAL_PRESETS } from '../config/modalConfig';

// Confirmation Dialog
const confirmationOptions = MODAL_PRESETS.confirmation;

// Full Content Modal (e.g., exam results)
const fullContentOptions = MODAL_PRESETS.fullContent;

// Alert Modal (no accidental close)
const alertOptions = MODAL_PRESETS.alert;

// Exam/Test Modal (strict - no ESC, no outside click)
const examOptions = MODAL_PRESETS.exam;
```

## Integrated Modals

The following modals have been integrated with the global behavior system:

### 1. UpgradeModal (`/components/UpgradeModal.js`)
**Purpose**: Subscription upgrade prompts
**Configuration**:
- ✅ Focus trap enabled
- ✅ Outside click to close
- ✅ ESC key to close
- ✅ Scroll lock

**Usage**: AI Tutor, Mock Tests when user hits limits

### 2. EnhancedResultsModal (`/components/EnhancedResultsModal.js`)
**Purpose**: Exam/test results display
**Configuration**:
- ✅ Focus trap enabled
- ❌ Outside click disabled (prevent accidental close)
- ❌ ESC key disabled (force user interaction)
- ✅ Scroll lock

**Usage**: Mock Tests completion

### 3. MotivationalPopup (`/components/MotivationalPopup.js`)
**Purpose**: Encouraging messages after tests
**Configuration**:
- ✅ Focus trap enabled
- ✅ Outside click to close
- ✅ ESC key to close
- ✅ Scroll lock

**Usage**: Post-test motivation

## Best Practices

### DO ✅

1. **Always use `useEffect`** for behavior application
   ```javascript
   useEffect(() => {
     if (isOpen && modalRef.current) {
       return applyGlobalModalBehavior(modalRef.current, options);
     }
   }, [isOpen, onClose]);
   ```

2. **Return the cleanup function** from `applyGlobalModalBehavior()`
   - This removes event listeners and restores scroll

3. **Add `data-modal-backdrop="true"`** to backdrop elements
   - Helps the utility identify backdrop clicks

4. **Use `ref` on the modal container** (not the backdrop)
   - The container is where focus trap and accessibility apply

5. **Configure per modal needs**:
   - Exam/test modals: `outsideClick: false`, `closeOnEsc: false`
   - Confirmation dialogs: `outsideClick: true`, `closeOnEsc: true`
   - Alert modals: `outsideClick: false`, `closeOnEsc: false`

### DON'T ❌

1. **Don't manually manage body scroll**
   ```javascript
   // ❌ OLD WAY
   useEffect(() => {
     document.body.style.overflow = 'hidden';
     return () => { document.body.style.overflow = ''; };
   }, []);

   // ✅ NEW WAY
   // Scroll lock handled by applyGlobalModalBehavior()
   ```

2. **Don't implement custom ESC handlers**
   ```javascript
   // ❌ OLD WAY
   useEffect(() => {
     const handleEsc = (e) => {
       if (e.key === 'Escape') onClose();
     };
     document.addEventListener('keydown', handleEsc);
     return () => document.removeEventListener('keydown', handleEsc);
   }, []);

   // ✅ NEW WAY
   // ESC handling built into applyGlobalModalBehavior()
   ```

3. **Don't hardcode animation values**
   ```javascript
   // ❌ OLD WAY
   <motion.div
     initial={{ opacity: 0, scale: 0.9 }}
     animate={{ opacity: 1, scale: 1 }}
     transition={{ duration: 0.2 }}
   >

   // ✅ NEW WAY
   const modalAnimation = getModalAnimationProps('modal');
   <motion.div {...modalAnimation}>
   ```

4. **Don't create custom focus trap logic**
   - The utility handles focus trapping automatically

## Migration Checklist

When integrating a modal with the global behavior system:

- [ ] Import `applyGlobalModalBehavior` from `../utils/modalBehavior`
- [ ] Add `useRef` for modal container
- [ ] Add `useEffect` to apply behavior when `isOpen` changes
- [ ] Add `ref={modalRef}` to modal container element
- [ ] Remove manual scroll lock code
- [ ] Remove manual ESC key handlers
- [ ] Remove manual focus trap logic (if any)
- [ ] Update animations to use `getModalAnimationProps()` (optional but recommended)
- [ ] Add `data-modal-backdrop="true"` to backdrop element
- [ ] Test: Open modal, press ESC, click outside, press Tab
- [ ] Verify all existing props and handlers still work

## Animation Constants

All modals use these standardized values (from `modalConfig.js`):

```javascript
animation: {
  duration: 0.15,          // 150ms
  easing: "easeInOut",     // No bounce or spring
}

backdrop: {
  color: "rgba(0, 0, 0, 0.4)",
  blur: true,
  blurAmount: "6px"
}

style: {
  borderRadius: "16px",
  shadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
}
```

## Troubleshooting

### Modal not closing on ESC
- Check `closeOnEsc: true` is set in options
- Verify `onClose` callback is provided
- Ensure modal is not nested inside another element capturing keyboard events

### Modal closing when it shouldn't
- For exam/test modals, use `outsideClick: false` and `closeOnEsc: false`
- Check backdrop has `data-modal-backdrop="true"` attribute

### Focus not trapped
- Verify `ref={modalRef}` is on the correct container element
- Check modal has focusable elements (buttons, inputs, links)
- Ensure `trapFocus: true` in options

### Scroll still working in background
- Verify `scrollLock: true` in options
- Check cleanup function is returned from `applyGlobalModalBehavior()`
- Ensure modal unmounts properly (not just hidden with `display: none`)

## Future Enhancements

Potential improvements for the global modal system:

1. **Nested Modal Support** - Handle modals opening on top of modals
2. **Animation Presets** - More animation variants (slide, fade, zoom)
3. **Mobile Gestures** - Swipe down to close on mobile
4. **History Integration** - Use browser history for modal state
5. **Performance Monitoring** - Track modal open/close performance

## Support

For questions or issues with modal integration:
- Check this documentation first
- Review integrated modals for reference examples
- Test in isolation before integrating into larger components

---

**Last Updated**: January 22, 2025  
**Commit Tag**: `feat/ui-global-modal-standardization-v1`
