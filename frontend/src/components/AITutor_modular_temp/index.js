/**
 * AITutor - Main Container (Modular Version)
 * 
 * Orchestrates all AI Tutor functionality using custom hooks and modular components
 * Replaces the legacy 3,399-line monolithic component
 * 
 * @version 2.0.0
 * @date January 17, 2025
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';

// Custom Hooks
import useAITutorSession from '../../hooks/useAITutorSession';
import useAITutorMessages from '../../hooks/useAITutorMessages';
import useAIGeneration from '../../hooks/useAIGeneration';
import useVoiceInput from '../../hooks/useVoiceInput';
import usePersonalization from '../../hooks/usePersonalization';
import useSubscriptionCheck from '../../hooks/useSubscriptionCheck';

// UI Components
import AITutorChat from './AITutorChat';
import ChatInput from './ChatInput';
import SessionSidebar from './SessionSidebar';
import SubjectSelector from './SubjectSelector';
import PersonalizationPanel from './PersonalizationPanel';
import UpgradeModal from '../UpgradeModal';

// Utils
import { handleSubscriptionError } from '../../utils/subscriptionErrorHandler';

const AITutor = () => {
  const { user } = useAuth();
  const { currentTier } = useSubscription();

  // UI State
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState('Mathematics');
  const [aiMode, setAiMode] = useState('dual');
  const [depthLevel, setDepthLevel] = useState('standard');
  const [examMode, setExamMode] = useState('JEE');

  // Initialize hooks
  const sessionHook = useAITutorSession();
  const messagesHook = useAITutorMessages(sessionHook.currentSession);
  const generationHook = useAIGeneration();
  const voiceHook = useVoiceInput();
  const personalizationHook = usePersonalization();
  const subscriptionHook = useSubscriptionCheck();

  /**
   * Load messages when session changes
   */
  useEffect(() => {
    if (sessionHook.currentSession) {
      messagesHook.loadMessages(sessionHook.currentSession);
    } else {
      messagesHook.clearMessages();
    }
  }, [sessionHook.currentSession]);

  /**
   * Handle voice transcript updates
   */
  useEffect(() => {
    // Voice transcript is passed directly to ChatInput
    // No additional handling needed here
  }, [voiceHook.transcript]);

  /**
   * Detect topic from message (simple keyword matching)
   */
  const detectTopicFromMessage = useCallback((message) => {
    const lowerMessage = message.toLowerCase();
    
    // Subject detection
    if (lowerMessage.includes('math') || lowerMessage.includes('calculus') || lowerMessage.includes('algebra')) {
      return 'Mathematics';
    }
    if (lowerMessage.includes('physics') || lowerMessage.includes('force') || lowerMessage.includes('motion')) {
      return 'Physics';
    }
    if (lowerMessage.includes('chemistry') || lowerMessage.includes('reaction') || lowerMessage.includes('molecule')) {
      return 'Chemistry';
    }
    if (lowerMessage.includes('biology') || lowerMessage.includes('cell') || lowerMessage.includes('organism')) {
      return 'Biology';
    }
    
    return selectedSubject || 'General';
  }, [selectedSubject]);

  /**
   * Handle sending a message
   */
  const handleSendMessage = useCallback(async (message) => {
    try {
      // 1. Check subscription access
      const accessCheck = await subscriptionHook.checkFeatureAccess('ai_sessions_monthly');
      
      if (!accessCheck.has_access) {
        setShowUpgradeModal(true);
        return;
      }

      // 2. Add user message optimistically
      const tempId = messagesHook.addUserMessage(message);

      // 3. Create or get session
      let sessionId = sessionHook.currentSession;
      
      if (!sessionId) {
        const detectedTopic = detectTopicFromMessage(message);
        sessionId = await sessionHook.createSession(
          message, 
          detectedTopic, 
          aiMode, 
          selectedSubject
        );
        
        if (!sessionId) {
          throw new Error('Failed to create session');
        }
      }

      // 4. Generate AI response
      const aiResponse = await generationHook.generateResponse({
        message,
        subject: selectedSubject,
        sessionId,
        aiMode,
        depthLevel,
        examMode
      });

      if (!aiResponse) {
        throw new Error('Failed to generate AI response');
      }

      // 5. Update message with AI response
      messagesHook.addAIResponse(tempId, aiResponse);

      // 6. Save to backend
      await messagesHook.saveMessage(sessionId, message, aiResponse);

      // 7. Handle XP gain if present
      if (aiResponse.xp_result) {
        personalizationHook.handleXPGain(aiResponse.xp_result);
      }

      // 8. Track usage
      subscriptionHook.trackUsage('ai_sessions_monthly');

      // 9. Update session title if first message
      if (messagesHook.messages.length === 0) {
        const detectedTopic = aiResponse.topic || detectTopicFromMessage(message);
        await sessionHook.updateSessionTitle(sessionId, detectedTopic, message);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Handle subscription errors
      if (error.response?.status === 403) {
        const upgradeInfo = await handleSubscriptionError(error);
        if (upgradeInfo) {
          setShowUpgradeModal(true);
        }
      }
      
      // Show error to user (you can add toast notification here)
      alert(error.message || 'Failed to send message. Please try again.');
    }
  }, [
    sessionHook,
    messagesHook,
    generationHook,
    subscriptionHook,
    personalizationHook,
    selectedSubject,
    aiMode,
    depthLevel,
    examMode,
    detectTopicFromMessage
  ]);

  /**
   * Handle new session creation
   */
  const handleNewSession = useCallback(() => {
    sessionHook.setCurrentSession(null);
    messagesHook.clearMessages();
  }, [sessionHook, messagesHook]);

  /**
   * Handle session selection
   */
  const handleSessionSelect = useCallback((sessionId) => {
    sessionHook.switchSession(sessionId);
  }, [sessionHook]);

  /**
   * Handle session deletion
   */
  const handleDeleteSession = useCallback(async (sessionId) => {
    await sessionHook.deleteSession(sessionId);
  }, [sessionHook]);

  /**
   * Handle voice toggle
   */
  const handleVoiceToggle = useCallback(() => {
    voiceHook.toggleListening();
  }, [voiceHook]);

  /**
   * Toggle sidebar
   */
  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed(prev => !prev);
  }, []);

  // Combined loading state
  const isLoading = generationHook.generating || messagesHook.loading;

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Subject & Mode Selector */}
      <SubjectSelector
        subject={selectedSubject}
        aiMode={aiMode}
        depthLevel={depthLevel}
        examMode={examMode}
        onSubjectChange={setSelectedSubject}
        onAIModeChange={setAiMode}
        onDepthLevelChange={setDepthLevel}
        onExamModeChange={setExamMode}
        disabled={isLoading}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Session Sidebar */}
        <SessionSidebar
          sessions={sessionHook.sessions}
          currentSession={sessionHook.currentSession}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
          loading={sessionHook.loading}
          collapsed={sidebarCollapsed}
          onToggleCollapse={toggleSidebar}
        />

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <AITutorChat
            messages={messagesHook.messages}
            loading={isLoading}
          />
          
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading}
            loading={isLoading}
            voiceEnabled={voiceHook.isSupported}
            isListening={voiceHook.isListening}
            onVoiceToggle={handleVoiceToggle}
            voiceTranscript={voiceHook.transcript}
          />
        </div>

        {/* Personalization Panel (Desktop only) */}
        <div className="hidden lg:block w-80 bg-gray-50 dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
          <PersonalizationPanel
            xpInfo={personalizationHook.xpInfo}
            streakInfo={personalizationHook.streakInfo}
            topicMastery={personalizationHook.topicMastery}
            loading={personalizationHook.loading}
          />
        </div>
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        upgradeHint={subscriptionHook.upgradeHint}
        accessInfo={subscriptionHook.usage}
        currentTier={currentTier}
      />

      {/* Error Display */}
      {(generationHook.error || messagesHook.error || sessionHook.error) && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-20 right-4 bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg max-w-md z-50"
        >
          <p className="text-sm font-medium">
            {generationHook.error || messagesHook.error || sessionHook.error}
          </p>
          <button
            onClick={() => {
              generationHook.clearError();
              messagesHook.clearMessages();
            }}
            className="mt-2 text-xs underline"
          >
            Dismiss
          </button>
        </motion.div>
      )}
    </div>
  );
};

export default AITutor;
