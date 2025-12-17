/**
 * ClassroomLayout - Digital Classroom Split-Screen Layout
 * =======================================================
 * 
 * The main layout orchestrator for the AI Sathi learning workspace.
 * 
 * Features:
 * - Collapsible SmartBoard (Dynamic Layout)
 * - Split-screen on desktop (30% chat, 70% board)
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

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu,
  MessageSquare,
  Palette,
  Eye,
  Columns,
  Sparkles
} from 'lucide-react';

// Import layout components
import HistorySidebar from '../chat/HistorySidebar';
import SmartBoard, { VisualToast } from '../visuals/SmartBoard';

// Active tab enum for mobile
const ACTIVE_TAB = {
  CHAT: 'chat',
  BOARD: 'board'
};

// ============================================
// FEATURE FLAG: SmartBoard Visibility
// ============================================
// Due to technical limitations, SmartBoard is temporarily disabled for v1 release.
// Set to true to re-enable SmartBoard functionality.
// All SmartBoard code remains intact for future enablement.
const SMARTBOARD_ENABLED = false;

// ============================================
// ClassroomHeader Component
// ============================================
const ClassroomHeader = ({ 
  onMenuClick, 
  title = 'AI Sathi',
  rightActions,
  isBoardOpen,
  onToggleBoard,
  hasVisual = false
}) => {
  return (
    <header className="flex-shrink-0 h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 z-20">
      {/* Left Section */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5 text-gray-600" />
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-orange-400 rounded-xl flex items-center justify-center shadow-sm">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-gray-800">{title}</h1>
            <p className="text-xs text-gray-500 hidden sm:block">LEARNING WORKSPACE</p>
          </div>
        </div>
      </div>
      
      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* SmartBoard Toggle Button - Desktop only */}
        {/* TEMPORARILY HIDDEN: SmartBoard disabled for v1 release */}
        {SMARTBOARD_ENABLED && (
          <button
            onClick={onToggleBoard}
            className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              isBoardOpen 
                ? 'bg-purple-600 text-white hover:bg-purple-700'
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
          </button>
        )}
        
        {rightActions}
      </div>
    </header>
  );
};

// ============================================
// MobileTabBar Component
// ============================================
const MobileTabBar = ({ activeTab, onTabChange, hasNewVisual }) => {
  // TEMPORARILY HIDDEN: SmartBoard disabled for v1 release
  // When SMARTBOARD_ENABLED is false, don't show the mobile tab bar at all
  // (since it's only useful for switching between Chat and Board)
  if (!SMARTBOARD_ENABLED) {
    return null;
  }
  
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white border-t border-gray-200 flex items-center justify-around px-6 z-30">
      <button
        onClick={() => onTabChange(ACTIVE_TAB.CHAT)}
        className={`flex flex-col items-center gap-1 px-6 py-2 rounded-xl transition-all ${
          activeTab === ACTIVE_TAB.CHAT
            ? 'text-purple-600 bg-purple-50'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <MessageSquare className="w-5 h-5" />
        <span className="text-xs font-medium">Chat</span>
      </button>
      
      <button
        onClick={() => onTabChange(ACTIVE_TAB.BOARD)}
        className={`flex flex-col items-center gap-1 px-6 py-2 rounded-xl transition-all relative ${
          activeTab === ACTIVE_TAB.BOARD
            ? 'text-purple-600 bg-purple-50'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <Palette className="w-5 h-5" />
        <span className="text-xs font-medium">Board</span>
        {hasNewVisual && activeTab !== ACTIVE_TAB.BOARD && (
          <span className="absolute top-1 right-4 w-2.5 h-2.5 bg-orange-500 rounded-full animate-pulse" />
        )}
      </button>
    </nav>
  );
};

// ============================================
// Main ClassroomLayout Component
// ============================================
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
  hasStartedChat = true, // Controls whether to show split layout or full-width welcome
  welcomeScreen = null, // Optional custom welcome screen component
  // Concept Card props
  currentTopic = null,
  keyFormula = null,
  currentSubject = null,
  // NEW: Visual loading state
  isGeneratingVisual = false, // True when AI is processing/generating visual
  userQuestion = null, // Current question for fallback
}) {
  // State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(ACTIVE_TAB.CHAT);
  const [showVisualToast, setShowVisualToast] = useState(false);
  const [hasNewVisual, setHasNewVisual] = useState(false);
  
  // Collapsible SmartBoard state - Default to closed (Zen Mode)
  // When SMARTBOARD_ENABLED is false, board is always closed
  const [isBoardOpen, setIsBoardOpen] = useState(false);
  
  // Track previous visual artifact for auto-open logic
  const prevVisualRef = useRef(visualArtifact);

  // Track previous loading state for auto-open logic
  const prevLoadingRef = useRef(isGeneratingVisual);

  // Auto-open board when loading starts or new visual arrives
  // DISABLED when SMARTBOARD_ENABLED is false
  useEffect(() => {
    // Skip auto-open logic when SmartBoard is disabled
    if (!SMARTBOARD_ENABLED) {
      return;
    }
    
    const hasVisual = visualArtifact && (
      visualArtifact.svg || 
      visualArtifact.visual_sketch?.svg || 
      visualArtifact.blueprint ||
      visualArtifact.template ||
      visualArtifact.mode
    );
    
    const prevHasVisual = prevVisualRef.current && (
      prevVisualRef.current.svg || 
      prevVisualRef.current.visual_sketch?.svg || 
      prevVisualRef.current.blueprint ||
      prevVisualRef.current.template ||
      prevVisualRef.current.mode
    );
    
    // NEW: Auto-open board when loading starts (optimistic loading)
    const loadingJustStarted = isGeneratingVisual && !prevLoadingRef.current;
    if (loadingJustStarted) {
      setIsBoardOpen(true);
    }
    
    // New visual arrived - update indicators
    if (hasVisual && !prevHasVisual) {
      setIsBoardOpen(true);
      setHasNewVisual(true);
      // Show toast on mobile
      if (window.innerWidth < 768) {
        setShowVisualToast(true);
      }
    }
    
    prevVisualRef.current = visualArtifact;
    prevLoadingRef.current = isGeneratingVisual;
  }, [visualArtifact, isGeneratingVisual]);

  // Clear "new visual" indicator when board is viewed
  useEffect(() => {
    if (isBoardOpen || activeTab === ACTIVE_TAB.BOARD) {
      setHasNewVisual(false);
    }
  }, [isBoardOpen, activeTab]);

  // Sidebar controls
  const openSidebar = useCallback(() => setIsSidebarOpen(true), []);
  const closeSidebar = useCallback(() => setIsSidebarOpen(false), []);

  // Toggle SmartBoard
  const toggleBoard = useCallback(() => {
    setIsBoardOpen(prev => !prev);
  }, []);

  // Mobile tab change handler
  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === ACTIVE_TAB.BOARD) {
      setHasNewVisual(false);
    }
  }, []);

  // Check if visual exists for header indicator
  const hasVisual = visualArtifact && (
    visualArtifact.svg || 
    visualArtifact.visual_sketch?.svg || 
    visualArtifact.blueprint ||
    visualArtifact.template ||
    visualArtifact.mode
  );

  return (
    <div className="flex-1 h-full w-full flex flex-col bg-gray-50 overflow-hidden">
      {/* Header */}
      <ClassroomHeader
        onMenuClick={openSidebar}
        title={headerTitle}
        rightActions={headerRightActions}
        isBoardOpen={isBoardOpen}
        onToggleBoard={toggleBoard}
        hasVisual={hasVisual && !isBoardOpen}
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
              {/* Left Panel - Chat */}
              {/* ZEN MODE: Full width, content centered inside (like ChatGPT) */}
              {/* LAB MODE: 40% left panel when visual active */}
              {/* SMARTBOARD DISABLED: Always full width */}
              <div 
                className={`flex flex-col overflow-hidden transition-all duration-500 ease-in-out bg-white ${
                  SMARTBOARD_ENABLED && isBoardOpen 
                    ? 'w-[40%] min-w-[400px] border-r border-gray-200' 
                    : 'flex-1'
                }`}
              >
                {/* Chat Content - Children handle their own scrolling */}
                {children}
              </div>

              {/* Right Panel - SmartBoard */}
              {/* LAB MODE: 60% right panel with visual/concept card */}
              {/* TEMPORARILY HIDDEN: SmartBoard disabled for v1 release */}
              {SMARTBOARD_ENABLED && (
                <div 
                  className={`overflow-hidden transition-all duration-500 ease-in-out bg-slate-50 ${
                    isBoardOpen 
                      ? 'flex w-[60%]' 
                      : 'hidden w-0'
                  }`}
                >
                  <SmartBoard
                    artifact={visualArtifact}
                    onFullscreen={onVisualFullscreen}
                    className="h-full w-full"
                    currentTopic={currentTopic}
                    keyFormula={keyFormula}
                    subject={currentSubject}
                    isConversationActive={hasStartedChat}
                    isLoading={isGeneratingVisual}
                    userQuestion={userQuestion}
                  />
                </div>
              )}
            </div>

            {/* === MOBILE LAYOUT === */}
            {/* When SMARTBOARD_ENABLED is false, no bottom padding needed (no tab bar) */}
            <div className={`md:hidden flex-1 flex flex-col overflow-hidden ${SMARTBOARD_ENABLED ? 'pb-16' : ''}`}>
              <AnimatePresence mode="wait">
                {/* When SmartBoard disabled, always show chat */}
                {(!SMARTBOARD_ENABLED || activeTab === ACTIVE_TAB.CHAT) ? (
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
                      currentTopic={currentTopic}
                      keyFormula={keyFormula}
                      subject={currentSubject}
                      isConversationActive={hasStartedChat}
                      isLoading={isGeneratingVisual}
                      userQuestion={userQuestion}
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

      {/* Visual Toast (Mobile Only) - Hidden when SmartBoard disabled */}
      {SMARTBOARD_ENABLED && (
        <VisualToast
          show={showVisualToast}
          onClose={() => {
            setShowVisualToast(false);
            handleTabChange(ACTIVE_TAB.BOARD);
          }}
        />
      )}
    </div>
  );
}
