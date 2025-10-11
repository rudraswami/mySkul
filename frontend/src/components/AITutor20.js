/**
 * AI Tutor 2.0 Component
 * Enhanced AI tutor with visual-first, emotion-aware, mentor-professor adaptive UI
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { 
  useAvailableContexts, 
  useChatSessions, 
  useSendMessage 
} from '../hooks/useAI';
import { useAITutorPersona } from '../hooks/useAITutorPersona';
import { useVisualGenerator } from '../hooks/useVisualGenerator';

import PersonaHeader from './PersonaHeader';
import AIResponseCardV2 from './AIResponseCardV2';
import VisualConceptBlock from './VisualConceptBlock';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { LoadingSpinner } from './ui/loading';

import { 
  Brain, 
  Send, 
  MessageCircle, 
  Mic,
  MicOff,
  Plus,
  Settings,
  Sparkles,
  ArrowLeft,
  User
} from 'lucide-react';

const AITutor20 = ({ 
  onBackToV1,
  className = '' 
}) => {
  const { user } = useAuth();
  const { checkFeatureAccess, triggerFeatureUpsell } = useSubscription();
  
  // React Query hooks
  const { data: availableContexts } = useAvailableContexts();
  const { data: chatSessions, refetch: refetchSessions } = useChatSessions();
  const sendMessageMutation = useSendMessage();
  
  // AI Tutor Persona hooks
  const {
    currentPersona,
    personaConfig,
    motivationalMessage,
    analyzeAndAdapt,
    getPersonaStyles,
    resetPersona
  } = useAITutorPersona();
  
  // Visual generator
  const { generateVisual, preloadVisuals } = useVisualGenerator();
  
  // Component state
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedContext, setSelectedContext] = useState('general');
  const [isRecording, setIsRecording] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  // Refs
  const chatContainerRef = useRef(null);
  const messageInputRef = useRef(null);
  
  // User stats for persona header
  const [userStats, setUserStats] = useState({
    streak: 7, // This would come from actual user data
    focus: selectedContext || 'General'
  });

  // Initialize component
  useEffect(() => {
    // Preload common visuals for better performance
    if (selectedContext !== 'general') {
      preloadVisuals([
        'algebra', 'geometry', 'calculus',
        'physics', 'chemistry', 'biology'
      ], selectedContext);
    }
  }, [selectedContext, preloadVisuals]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  // Handle message sending
  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    // Check feature access
    const hasAccess = await checkFeatureAccess('ai_tutor_queries');
    if (!hasAccess) {
      triggerFeatureUpsell('ai_tutor_queries');
      return;
    }

    setIsLoading(true);
    
    try {
      // Analyze sentiment and adapt persona
      const personaAnalysis = analyzeAndAdapt(currentMessage);
      
      // Add user message to chat
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: currentMessage,
        timestamp: new Date(),
        persona: personaAnalysis.persona,
        sentiment: personaAnalysis.sentiment
      };
      
      setChatHistory(prev => [...prev, userMessage]);
      setCurrentMessage('');

      // Send message via React Query
      const response = await sendMessageMutation.mutateAsync({
        message: currentMessage,
        context: selectedContext,
        session_id: activeSessionId,
        persona: personaAnalysis.persona,
        emotion: personaAnalysis.emotion
      });

      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.response || response,
        timestamp: new Date(),
        persona: personaAnalysis.persona,
        confidence: response.confidence,
        sources: response.sources,
        topic: response.topic,
        subject: selectedContext
      };

      setChatHistory(prev => [...prev, aiMessage]);
      
      // Update session ID if new session
      if (response.session_id && !activeSessionId) {
        setActiveSessionId(response.session_id);
        refetchSessions();
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an issue. Please try again.',
        timestamp: new Date()
      };
      
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle quick actions
  const handleSaveToNotes = async (responseData) => {
    // Integrate with existing notes system
    console.log('Saving to notes:', responseData);
    // TODO: Implement save to notes with auto-tagging
  };

  const handlePracticeSimilar = async (responseData) => {
    // Integrate with Mock Tests system for 3-question quiz
    console.log('Opening practice quiz for:', responseData.topic);
    // TODO: Integrate with MockTests component for similar practice
  };

  const handleExplainDifferently = async (responseData) => {
    // Request alternative explanation
    const alternativePrompt = `Explain ${responseData.topic || 'this concept'} in a different way, using ${currentPersona === 'professor' ? 'simpler terms' : 'more detailed examples'}.`;
    setCurrentMessage(alternativePrompt);
    handleSendMessage();
  };

  const handleShowVisual = async (responseData) => {
    // Generate enhanced visual
    const visual = await generateVisual(responseData.topic, responseData.subject, true);
    console.log('Generated visual:', visual);
    // TODO: Display visual in modal or expanded view
  };

  const handleCopyResponse = async (responseData) => {
    try {
      await navigator.clipboard.writeText(responseData.content);
      return true;
    } catch (error) {
      console.error('Failed to copy:', error);
      return false;
    }
  };

  const handleFeedback = (isHelpful, responseData) => {
    console.log(`Feedback: ${isHelpful ? 'helpful' : 'not helpful'}`, responseData);
    // TODO: Send feedback to analytics
  };

  // Handle keyboard shortcuts
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Start new chat session
  const startNewChat = () => {
    setChatHistory([]);
    setActiveSessionId(null);
    resetPersona();
    messageInputRef.current?.focus();
  };

  const personaStyles = getPersonaStyles();

  return (
    <div className={`flex flex-col h-full bg-gray-50 ${className}`}>
      {/* Header with Back Button and Persona */}
      <div className="flex-shrink-0 p-4 bg-white border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={onBackToV1}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Classic</span>
            </Button>
            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
              ✨ AI Tutor 2.0 Beta
            </Badge>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={startNewChat}>
              <Plus className="w-4 h-4 mr-1" />
              New Chat
            </Button>
          </div>
        </div>

        {/* Persona Header */}
        <PersonaHeader
          personaConfig={personaConfig}
          motivationalMessage={motivationalMessage}
          userStats={userStats}
        />
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex">
        {/* Chat History */}
        <div className="flex-1 flex flex-col">
          <div 
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-6 space-y-6"
          >
            <AnimatePresence mode="popLayout">
              {chatHistory.length === 0 ? (
                // Welcome State
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="mb-6">
                    <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${personaStyles.gradient} mx-auto mb-4 flex items-center justify-center`}>
                      <Brain className={`w-8 h-8 text-${personaStyles.accentColor}`} />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">
                      Welcome to AI Tutor 2.0! 
                    </h3>
                    <p className="text-gray-600 max-w-md mx-auto">
                      Ask me anything about your studies. I'll adapt my teaching style to help you learn better.
                    </p>
                  </div>
                  
                  {/* Quick Start Topics */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-w-2xl mx-auto">
                    {[
                      { topic: 'Quadratic Equations', subject: 'mathematics' },
                      { topic: 'Newton\'s Laws', subject: 'physics' },
                      { topic: 'Chemical Bonding', subject: 'chemistry' }
                    ].map((item, index) => (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + index * 0.1 }}
                        onClick={() => setCurrentMessage(`Explain ${item.topic}`)}
                        className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all group"
                      >
                        <VisualConceptBlock 
                          topic={item.topic}
                          subject={item.subject}
                          showTitle={false}
                          animate={false}
                          className="mb-2 bg-transparent border-none shadow-none p-0"
                        />
                        <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600">
                          {item.topic}
                        </span>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                // Chat Messages
                chatHistory.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'user' ? (
                      // User Message
                      <div className="flex items-start space-x-3 max-w-xs md:max-w-md">
                        <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-3">
                          <p className="text-sm">{message.content}</p>
                        </div>
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-blue-600" />
                        </div>
                      </div>
                    ) : message.type === 'ai' ? (
                      // AI Response
                      <div className="max-w-4xl">
                        <AIResponseCardV2
                          response={message}
                          persona={message.persona || currentPersona}
                          onSaveToNotes={handleSaveToNotes}
                          onPracticeSimilar={handlePracticeSimilar}
                          onExplainDifferently={handleExplainDifferently}
                          onShowVisual={handleShowVisual}
                          onCopyResponse={handleCopyResponse}
                          onFeedback={(isHelpful) => handleFeedback(isHelpful, message)}
                        />
                      </div>
                    ) : (
                      // Error Message
                      <div className="max-w-md">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <p className="text-sm text-red-600">{message.content}</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))
              )}
            </AnimatePresence>
            
            {/* Loading Indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </motion.div>
            )}
          </div>

          {/* Message Input */}
          <div className="flex-shrink-0 p-4 bg-white border-t border-gray-200">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <Textarea
                  ref={messageInputRef}
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask me anything about your studies..."
                  className="resize-none border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                  rows={1}
                  disabled={isLoading}
                />
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Voice Input Toggle */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsRecording(!isRecording)}
                  className={`${isRecording ? 'text-red-600 bg-red-50' : 'text-gray-600'}`}
                  disabled={isLoading}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>
                
                {/* Send Button */}
                <Button
                  onClick={handleSendMessage}
                  disabled={!currentMessage.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? (
                    <LoadingSpinner size="sm" className="text-white" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
            
            {/* Context Selector */}
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500">Context:</span>
                <select
                  value={selectedContext}
                  onChange={(e) => {
                    setSelectedContext(e.target.value);
                    setUserStats(prev => ({ ...prev, focus: e.target.value }));
                  }}
                  className="text-xs border-none bg-transparent text-gray-700 focus:ring-0 focus:outline-none"
                >
                  <option value="general">General</option>
                  <option value="mathematics">Mathematics</option>
                  <option value="physics">Physics</option>
                  <option value="chemistry">Chemistry</option>
                  <option value="biology">Biology</option>
                </select>
              </div>
              
              <div className="text-xs text-gray-500">
                {currentPersona} mode • {chatHistory.length} messages
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AITutor20;