/**
 * AITutor - Modular Version
 * Refactored into smaller components with hooks
 * Uses virtualized scrolling, HTML sanitization, and modern React patterns
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useChatSession } from '../../hooks/useChatSession';
import { useChatMessages } from '../../hooks/useChatMessages';
import { useAIGeneration } from '../../hooks/useAIGeneration';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { ChatWindow } from './ChatWindow';
import { ChatInput } from './ChatInput';
import { Brain, MessageCircle, Plus, GraduationCap } from 'lucide-react';
import UpgradeModal from '../UpgradeModal';

export default function AITutorModular() {
  const { user } = useAuth();
  const { upsellModal, setUpsellModal, currentTier } = useSubscription();
  
  // State
  const [selectedSubject, setSelectedSubject] = useState('Mathematics');
  const [examMode, setExamMode] = useState(user?.exam_type || 'JEE');
  const [aiMode, setAiMode] = useState('dual');
  const [depthLevel, setDepthLevel] = useState('standard');

  // Custom hooks
  const { 
    currentSession, 
    sessions,
    createSession,
    switchSession,
    deleteSession 
  } = useChatSession(user?.user_id);

  const {
    messages,
    loading: messagesLoading,
    sendMessage,
    addAIMessage,
    deleteMessage
  } = useChatMessages(currentSession?.id);

  const {
    generating,
    generateResponse
  } = useAIGeneration();

  // Create initial session on mount
  useEffect(() => {
    if (user && !currentSession && sessions.length === 0) {
      createSession(selectedSubject, examMode);
    }
  }, [user, currentSession, sessions, selectedSubject, examMode, createSession]);

  // Handle sending a message
  const handleSendMessage = async (content) => {
    try {
      // Send user message
      await sendMessage(content, {
        subject: selectedSubject,
        exam_mode: examMode
      });

      // Generate AI response
      const response = await generateResponse(currentSession.id, content, {
        mode: aiMode,
        depthLevel,
        examType: examMode,
        subject: selectedSubject
      });

      // Add AI response to messages
      if (response.response) {
        addAIMessage(response.response, {
          mode: response.mode,
          scenario_type: response.scenario_type
        });
      }
    } catch (error) {
      console.error('Failed to process message:', error);
      // Error handling done by hooks
    }
  };

  // Handle message reactions
  const handleMessageReact = async (messageId, reaction) => {
    console.log('Message reaction:', messageId, reaction);
    // TODO: Implement reaction tracking
  };

  // Handle starting a new session
  const handleNewSession = async () => {
    await createSession(selectedSubject, examMode);
  };

  const subjects = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'English',
    'History',
    'Geography',
    'Economics',
    'Computer Science'
  ];

  const examModes = ['JEE', 'NEET', 'UPSC', 'CBSE', 'Others'];
  const aiModes = [
    { value: 'dual', label: 'Dual Mode (Balanced)' },
    { value: 'professor', label: 'Professor Mode (Detailed)' },
    { value: 'mentor', label: 'Mentor Mode (Supportive)' }
  ];

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI Tutor</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {currentTier?.toUpperCase() || 'FREE'} Plan • {selectedSubject}
              </p>
            </div>
          </div>

          <Button
            onClick={handleNewSession}
            size="sm"
            className="gap-2"
            aria-label="Start new chat session"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </Button>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
          {/* Subject Selector */}
          <Select value={selectedSubject} onValueChange={setSelectedSubject}>
            <SelectTrigger className="dark:bg-gray-700 dark:text-white dark:border-gray-600">
              <SelectValue placeholder="Select subject" />
            </SelectTrigger>
            <SelectContent>
              {subjects.map(subject => (
                <SelectItem key={subject} value={subject}>
                  {subject}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Exam Mode */}
          <Select value={examMode} onValueChange={setExamMode}>
            <SelectTrigger className="dark:bg-gray-700 dark:text-white dark:border-gray-600">
              <SelectValue placeholder="Exam type" />
            </SelectTrigger>
            <SelectContent>
              {examModes.map(mode => (
                <SelectItem key={mode} value={mode}>
                  {mode}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* AI Mode */}
          <Select value={aiMode} onValueChange={setAiMode}>
            <SelectTrigger className="dark:bg-gray-700 dark:text-white dark:border-gray-600">
              <SelectValue placeholder="AI Mode" />
            </SelectTrigger>
            <SelectContent>
              {aiModes.map(mode => (
                <SelectItem key={mode.value} value={mode.value}>
                  {mode.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Chat Window */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow
          messages={messages}
          loading={generating}
          onMessageReact={handleMessageReact}
          onMessageDelete={deleteMessage}
        />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0">
        <ChatInput
          onSend={handleSendMessage}
          disabled={generating || !currentSession}
          placeholder={`Ask about ${selectedSubject}...`}
        />
      </div>

      {/* Upgrade Modal */}
      {upsellModal && (
        <UpgradeModal
          isOpen={!!upsellModal}
          onClose={() => setUpsellModal(null)}
          feature={upsellModal.featureName}
          currentTier={currentTier}
          upgradeMessage={upsellModal.upsellInfo?.upgrade_message}
          benefits={upsellModal.benefits}
        />
      )}
    </div>
  );
}
