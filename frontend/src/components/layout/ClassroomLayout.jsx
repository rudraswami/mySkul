/**
 * ClassroomLayout - Digital Classroom Split-Screen Layout
 * ========================================================
 * 
 * The main layout orchestrator for the learning workspace.
 * 
 * Features:
 * - Collapsible SmartBoard (Dynamic Layout)
 * - Split-screen on desktop (30-35% chat, 65-70% board)
 * - Tab-based navigation on mobile
 * - Collapsible history sidebar
 * - Sticky SmartBoard (non-scrollable)
 * - Auto-open board when visual arrives
 * - "Zen Mode" - centered chat when board is closed
 * 
 * Zones:
 * 1. Left Panel (Chat Stream) - Scrollable chat interface
 * 2. Right Panel (SmartBoard) - Fixed visual display (collapsible)
 * 3. Overlay (History Drawer) - Slide-out sidebar
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu,
  MessageCircle,
  Palette,
  X,
  ChevronLeft,
  ChevronRight,
  PanelRightClose,
  PanelRightOpen,
  Settings,
  Bell,
  User,
  Sparkles,
  Maximize2,
  Minimize2,
  Columns,
  Eye
} from 'lucide-react';

// Import layout components
import HistorySidebar from '../chat/HistorySidebar';
import SmartBoard, { VisualToast } from '../visuals/SmartBoard';

// Active tab enum for mobile
const ACTIVE_TAB = {
  CHAT: 'CHAT',
  BOARD: 'BOARD'
};

// Header Component with Board Toggle - Premium Glassmorphic Design
const ClassroomHeader = ({ 
  onMenuClick, 
  title = 'AI Sathi',
  showBackButton = false,
  onBack,
  rightActions,
  isBoardOpen,
  onToggleBoard,
  hasVisual = false
}) => {
  return (
    <header className="flex-shrink-0 h-16 px-4 bg-white/80 backdrop-blur-lg border-b border-gray-200/50 flex items-center justify-between sticky top-0 z-20 shadow-sm">
      {/* Left Section */}
      <div className="flex items-center gap-3">
        {showBackButton ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onBack}
            className="p-2 -ml-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </motion.button>
        ) : (
          <motion.button
            whileHover={{ scale: 1.05, rotate: 5 }}
            whileTap={{ scale: 0.95 }}
            onClick={onMenuClick}
            className="p-2.5 -ml-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-xl transition-all"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5" />
          </motion.button>
        )}
        
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <motion.div 
            whileHover={{ rotate: [0, -10, 10, 0] }}
            transition={{ duration: 0.5 }}
            className="w-10 h-10 bg-gradient-to-br from-purple-500 via-purple-600 to-orange-400 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20"
          >
            <Sparkles className="w-5 h-5 text-white" />
          </motion.div>
          <div>
            <h1 
              className="font-bold text-gray-800 text-lg leading-tight"
              style={{ fontFamily: "'Inter', 'Segoe UI', sans-serif" }}
            >
              {title}
            </h1>
            <p className="text-[10px] text-gray-400 font-medium tracking-wide uppercase">
              Learning Workspace
            </p>
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {rightActions}
        
        {/* Board Toggle Button - Desktop Only */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onToggleBoard}
          className={`hidden md:flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
            isBoardOpen 
              ? 'text-gray-600 bg-gray-100 hover:bg-gray-200' 
              : 'text-purple-700 bg-purple-100 hover:bg-purple-200 shadow-sm'
          }`}
          title={isBoardOpen ? 'Focus Mode (Hide Board)' : 'Show SmartBoard'}
        >
          {isBoardOpen ? (
            <>
              <Eye className="w-4 h-4" />
              <span className="hidden lg:inline">Focus</span>
            </>
          ) : (
            <>
              <Columns className="w-4 h-4" />
              <span className="hidden lg:inline">SmartBoard</span>
              {hasVisual && (
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500"></span>
                </span>
              )}
            </>
          )}
        </motion.button>
      </div>
    </header>
  );
};

// Mobile Bottom Tab Bar - Premium Design
const MobileTabBar = ({ activeTab, onTabChange, hasNewVisual = false }) => {
  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-gray-200/50 z-30 safe-area-pb shadow-lg shadow-gray-200/50">
      <div className="flex items-stretch h-16">
        {/* Chat Tab */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={() => onTabChange(ACTIVE_TAB.CHAT)}
          className={`relative flex-1 flex flex-col items-center justify-center gap-1 transition-all duration-200 ${
            activeTab === ACTIVE_TAB.CHAT 
              ? 'text-purple-600' 
              : 'text-gray-400 hover:text-gray-600'
          }`}
        >
          {activeTab === ACTIVE_TAB.CHAT && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full"
            />
          )}
          <div className={`p-2 rounded-xl transition-all ${
            activeTab === ACTIVE_TAB.CHAT ? 'bg-purple-100' : ''
          }`}>
            <MessageCircle className={`w-5 h-5 ${activeTab === ACTIVE_TAB.CHAT ? 'fill-purple-200' : ''}`} />
          </div>
          <span className={`text-xs font-semibold ${
            activeTab === ACTIVE_TAB.CHAT ? 'text-purple-600' : 'text-gray-500'
          }`}>
            Chat
          </span>
        </motion.button>

        {/* Center Divider */}
        <div className="w-px bg-gray-200 my-3" />

        {/* Board Tab */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={() => onTabChange(ACTIVE_TAB.BOARD)}
          className={`relative flex-1 flex flex-col items-center justify-center gap-1 transition-all duration-200 ${
            activeTab === ACTIVE_TAB.BOARD 
              ? 'text-purple-600' 
              : 'text-gray-400 hover:text-gray-600'
          }`}
        >
          {activeTab === ACTIVE_TAB.BOARD && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full"
            />
          )}
          <div className={`relative p-2 rounded-xl transition-all ${
            activeTab === ACTIVE_TAB.BOARD ? 'bg-purple-100' : ''
          }`}>
            <Palette className={`w-5 h-5 ${activeTab === ACTIVE_TAB.BOARD ? 'fill-purple-200' : ''}`} />
            {/* New Visual Indicator - Red Dot */}
            {hasNewVisual && activeTab !== ACTIVE_TAB.BOARD && (
              <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-red-500 border-2 border-white"></span>
              </span>
            )}
          </div>
          <span className={`text-xs font-semibold ${
            activeTab === ACTIVE_TAB.BOARD ? 'text-purple-600' : 'text-gray-500'
          }`}>
            Board
          </span>
        </motion.button>
      </div>
    </div>
  );
};

// Main ClassroomLayout Component
export default function ClassroomLayout({
  children, // The ChatInterface component
  chatHistory = [],
  activeSessionId,
  onChatSelect,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onPinChat,
  isLoadingHistory = false,
  visualArtifact = null,
  onVisualFullscreen,
  headerTitle = 'AI Sathi',
  headerRightActions,
  hasStartedChat = true, // NEW: Controls whether to show split layout or full-width welcome
  welcomeScreen = null, // NEW: Optional custom welcome screen component
}) {
  // State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(ACTIVE_TAB.CHAT);
  const [showVisualToast, setShowVisualToast] = useState(false);
  const [hasNewVisual, setHasNewVisual] = useState(false);
  
  // NEW: Collapsible SmartBoard state - Default to closed (Zen Mode)
  const [isBoardOpen, setIsBoardOpen] = useState(false);
  
  // Track previous visual artifact for auto-open logic
  const prevVisualRef = useRef(visualArtifact);

  // AUTO-OPEN: When visual artifact changes from null to something
  useEffect(() => {
    const prevVisual = prevVisualRef.current;
    const hasNewArtifact = !prevVisual && visualArtifact;
    
    if (hasNewArtifact) {
      // Visual just arrived - auto-open the board
      setIsBoardOpen(true);
      setHasNewVisual(true);
    }
    
    // Update ref
    prevVisualRef.current = visualArtifact;
  }, [visualArtifact]);

  // Track visual changes for mobile notification
  useEffect(() => {
    if (visualArtifact && activeTab === ACTIVE_TAB.CHAT) {
      setShowVisualToast(true);
      setHasNewVisual(true);
      
      // Auto-hide toast after 4 seconds
      const timer = setTimeout(() => {
        setShowVisualToast(false);
      }, 4000);
      
      return () => clearTimeout(timer);
    }
  }, [visualArtifact, activeTab]);

  // Clear new visual indicator when switching to board
  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === ACTIVE_TAB.BOARD) {
      setHasNewVisual(false);
      setShowVisualToast(false);
    }
  }, []);

  // Toggle SmartBoard
  const toggleBoard = useCallback(() => {
    setIsBoardOpen(prev => !prev);
    if (!isBoardOpen) {
      setHasNewVisual(false);
    }
  }, [isBoardOpen]);

  // Open sidebar
  const openSidebar = useCallback(() => {
    setIsSidebarOpen(true);
  }, []);

  // Close sidebar
  const closeSidebar = useCallback(() => {
    setIsSidebarOpen(false);
  }, []);

  return (
    <div className="flex-1 h-full w-full flex flex-col bg-gray-50 overflow-hidden">
      {/* Header */}
      <ClassroomHeader
        onMenuClick={openSidebar}
        title={headerTitle}
        rightActions={headerRightActions}
        isBoardOpen={isBoardOpen}
        onToggleBoard={toggleBoard}
        hasVisual={!!visualArtifact && !isBoardOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* === WELCOME MODE (Full Width, Centered) - No Chat Yet === */}
        {!hasStartedChat ? (
          <div className="flex-1 flex flex-col bg-white overflow-y-auto">
            <div className="flex-1 flex items-center justify-center">
              <div className="w-full max-w-4xl mx-auto px-6 py-8">
                {welcomeScreen || children}
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* === DESKTOP LAYOUT === */}
            <div className="hidden md:flex flex-1 overflow-hidden">
              {/* Left Panel - Chat (Full Width OR Split Mode) */}
              <div 
                className={`flex flex-col overflow-hidden transition-all duration-500 ease-in-out bg-white ${
                  isBoardOpen 
                    ? 'w-[35%] lg:w-[32%] min-w-[380px] border-r border-gray-200' 
                    : 'flex-1'
                }`}
              >
                {/* Chat Content - Children handle their own scrolling */}
                {children}
              </div>

              {/* Right Panel - SmartBoard */}
              <div 
                className={`overflow-hidden transition-all duration-500 ease-in-out bg-slate-50 ${
                  isBoardOpen 
                    ? 'flex flex-1' 
                    : 'hidden w-0'
                }`}
              >
                <SmartBoard
                  artifact={visualArtifact}
                  onFullscreen={onVisualFullscreen}
                  className="h-full w-full"
                />
              </div>
            </div>

            {/* === MOBILE LAYOUT === */}
            <div className="md:hidden flex-1 flex flex-col overflow-hidden pb-16">
              <AnimatePresence mode="wait">
                {activeTab === ACTIVE_TAB.CHAT ? (
                  <motion.div
                    key="chat"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2, ease: 'easeOut' }}
                    className="flex-1 flex flex-col bg-white overflow-hidden"
                  >
                    {children}
                  </motion.div>
                ) : (
                  <motion.div
                    key="board"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2, ease: 'easeOut' }}
                    className="flex-1 overflow-hidden"
                  >
                    <SmartBoard
                      artifact={visualArtifact}
                      onFullscreen={onVisualFullscreen}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </>
        )}
      </div>

      {/* Mobile Tab Bar */}
      <MobileTabBar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        hasNewVisual={hasNewVisual}
      />

      {/* History Sidebar Overlay */}
      <HistorySidebar
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
        chats={chatHistory}
        activeSessionId={activeSessionId}
        onChatSelect={(chat) => {
          onChatSelect?.(chat);
          closeSidebar();
        }}
        onNewChat={() => {
          onNewChat?.();
          closeSidebar();
        }}
        onRenameChat={onRenameChat}
        onDeleteChat={onDeleteChat}
        onPinChat={onPinChat}
        isLoading={isLoadingHistory}
      />

      {/* Visual Toast (Mobile Only) */}
      <VisualToast
        show={showVisualToast}
        onClose={() => {
          setShowVisualToast(false);
          handleTabChange(ACTIVE_TAB.BOARD);
        }}
      />
    </div>
  );
}

// Export the active tab enum for external use
export { ACTIVE_TAB };
