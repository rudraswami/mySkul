import { useState } from 'react';

export const useAITutorUI = () => {
  const [showSidebar, setShowSidebar] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalData, setUpgradeModalData] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [expandedConcepts, setExpandedConcepts] = useState({});

  const toggleConcept = (messageId) => {
    setExpandedConcepts(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  return {
    showSidebar,
    setShowSidebar,
    showUpgradeModal,
    setShowUpgradeModal,
    upgradeModalData,
    setUpgradeModalData,
    drawerOpen,
    setDrawerOpen,
    expandedConcepts,
    toggleConcept
  };
};
