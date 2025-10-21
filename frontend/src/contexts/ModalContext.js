import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

/**
 * Global Modal Context for managing all modals/popups/alerts across the application
 * Provides centralized state management, scroll locking, and consistent UX
 */

const ModalContext = createContext(undefined);

/**
 * Modal types for different use cases
 */
export const ModalType = {
  DIALOG: 'dialog',           // Standard dialog with content
  CONFIRM: 'confirm',         // Confirmation dialog with Yes/No
  ALERT: 'alert',             // Alert/notification
  UPGRADE: 'upgrade',         // Subscription upgrade modal
  RESULTS: 'results',         // Test results modal
  CUSTOM: 'custom',           // Custom modal with component
};

export const ModalProvider = ({ children }) => {
  const [modals, setModals] = useState([]);
  const [scrollLocked, setScrollLocked] = useState(false);

  // Lock body scroll when modals are open
  useEffect(() => {
    if (modals.length > 0 && !scrollLocked) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
      setScrollLocked(true);
    } else if (modals.length === 0 && scrollLocked) {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      setScrollLocked(false);
    }

    return () => {
      if (modals.length === 0) {
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
      }
    };
  }, [modals.length, scrollLocked]);

  /**
   * Open a modal
   * @param {Object} modalConfig - Modal configuration
   * @returns {string} Modal ID for programmatic control
   */
  const openModal = useCallback((modalConfig) => {
    const modalId = `modal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const modal = {
      id: modalId,
      type: modalConfig.type || ModalType.DIALOG,
      title: modalConfig.title,
      content: modalConfig.content,
      component: modalConfig.component,
      size: modalConfig.size || 'medium', // small, medium, large, full
      closable: modalConfig.closable !== false,
      onClose: modalConfig.onClose,
      onConfirm: modalConfig.onConfirm,
      confirmText: modalConfig.confirmText || 'Confirm',
      cancelText: modalConfig.cancelText || 'Cancel',
      showCancel: modalConfig.showCancel !== false,
      variant: modalConfig.variant || 'default', // default, success, warning, error, info
      customActions: modalConfig.customActions,
      backdrop: modalConfig.backdrop !== false,
      backdropBlur: modalConfig.backdropBlur !== false,
      animation: modalConfig.animation || 'fade-scale', // fade, fade-scale, slide-up, slide-down
      zIndex: 9000 + modals.length,
      metadata: modalConfig.metadata || {},
    };

    setModals(prev => [...prev, modal]);
    return modalId;
  }, [modals.length]);

  /**
   * Close a specific modal
   */
  const closeModal = useCallback((modalId) => {
    const modal = modals.find(m => m.id === modalId);
    if (modal?.onClose) {
      modal.onClose();
    }
    setModals(prev => prev.filter(m => m.id !== modalId));
  }, [modals]);

  /**
   * Close the top-most modal
   */
  const closeTopModal = useCallback(() => {
    if (modals.length > 0) {
      const topModal = modals[modals.length - 1];
      closeModal(topModal.id);
    }
  }, [modals, closeModal]);

  /**
   * Close all modals
   */
  const closeAllModals = useCallback(() => {
    modals.forEach(modal => {
      if (modal.onClose) {
        modal.onClose();
      }
    });
    setModals([]);
  }, [modals]);

  /**
   * Update a modal's configuration
   */
  const updateModal = useCallback((modalId, updates) => {
    setModals(prev => 
      prev.map(modal => 
        modal.id === modalId ? { ...modal, ...updates } : modal
      )
    );
  }, []);

  const value = {
    modals,
    openModal,
    closeModal,
    closeTopModal,
    closeAllModals,
    updateModal,
  };

  return (
    <ModalContext.Provider value={value}>
      {children}
    </ModalContext.Provider>
  );
};

/**
 * Hook to use modal context
 */
export const useModal = () => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
};

/**
 * Convenience hooks for specific modal types
 */
export const useConfirm = () => {
  const { openModal } = useModal();

  return useCallback(({
    title = 'Confirm Action',
    content,
    onConfirm,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    variant = 'warning',
  }) => {
    return openModal({
      type: ModalType.CONFIRM,
      title,
      content,
      onConfirm,
      confirmText,
      cancelText,
      variant,
      size: 'small',
    });
  }, [openModal]);
};

export const useAlert = () => {
  const { openModal } = useModal();

  return useCallback(({
    title,
    content,
    variant = 'info',
    onClose,
  }) => {
    return openModal({
      type: ModalType.ALERT,
      title,
      content,
      variant,
      onClose,
      size: 'small',
      showCancel: false,
      confirmText: 'OK',
    });
  }, [openModal]);
};

export default ModalContext;
