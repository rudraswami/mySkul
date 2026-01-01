/**
 * Sathi Classroom - Digital Classroom Layout Integration
 * ======================================================
 * 
 * This component wraps the existing AITutorNeuroSymbolic chat
 * with the new ClassroomLayout for split-screen display.
 * 
 * Features:
 * - Split-screen on desktop (Chat + SmartBoard)
 * - Tab-based navigation on mobile
 * - History sidebar integration
 * - Visual artifact extraction for SmartBoard
 * 
 * Usage: Replace the old AITutorNeuroSymbolic route with this component
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useToast } from '../contexts/ToastContext';
import {
  Send,
  Plus,
  Loader,
  Sparkles,
  MessageCircle,
  Image as ImageIcon,
  XCircle,
  Flame,
  Zap,
  Trophy,
  Bell,
  Settings
} from 'lucide-react';

// Layout Components
import ClassroomLayout from './layout/ClassroomLayout';

// Response Components
import SmartResponse from './SmartResponse';
import MentorResponseV2 from './mentor-v2/MentorResponseV2';
import NeuroSymbolicResponse from './neuro-symbolic/NeuroSymbolicResponse';

// Enhancement Components
import MemoryContextBanner from './MemoryContextBanner';
import NotificationBell from './NotificationBell';
import { NeuralThinkingIndicator } from './chat/NeuralThinkingIndicator';

// ============================================
// PROACTIVE SUGGESTIONS COMPONENT
// Displays follow-up action buttons from AI
// ============================================
const ProactiveSuggestions = ({ suggestions, onSuggestionClick }) => {
  if (!suggestions || suggestions.length === 0) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-slate-700/50"
    >
      {suggestions.map((suggestion, idx) => (
        <button
          key={idx}
          onClick={() => onSuggestionClick(suggestion.action)}
          className="px-3 py-1.5 text-sm bg-violet-500/10 
                     text-violet-300 rounded-full border border-violet-500/30 
                     hover:bg-violet-500/20 hover:border-violet-500/50
                     transition-all duration-200"
        >
          {suggestion.label}
        </button>
      ))}
    </motion.div>
  );
};

// ============================================
// PROACTIVE OPENER COMPONENT
// Shows welcome back, streaks, milestones
// ============================================
const ProactiveOpener = ({ opener }) => {
  if (!opener) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mb-4 p-4 bg-amber-500/10 
                 border border-amber-500/30 rounded-xl"
    >
      <p className="text-amber-300 text-sm font-medium">{opener}</p>
    </motion.div>
  );
};
// WelcomeScreen - Inline fallback if not available
let WelcomeScreen;
try {
  WelcomeScreen = require('./chat/WelcomeScreen').default;
} catch (e) {
  WelcomeScreen = ({ onSuggestionClick }) => (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
      <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-orange-400 rounded-3xl flex items-center justify-center mb-6 shadow-lg">
        <Sparkles className="w-10 h-10 text-white" />
      </div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to Sathi!</h2>
      <p className="text-gray-500 mb-6 max-w-sm">I'm your personal learning companion. Ask me anything about Physics, Chemistry, Biology, or Math!</p>
      <div className="flex flex-wrap justify-center gap-2">
        {['Explain Newton\'s laws', 'What is photosynthesis?', 'Solve x² + 5x + 6 = 0'].map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => onSuggestionClick?.(suggestion)}
            className="px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-full text-sm font-medium transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}

// Gamification
import { useGamification } from '../hooks/useGamification';
import MicroReward, { LevelUpCelebration, StreakCelebration } from './gamification/MicroReward';

// Hooks
import useKeyboardShortcuts from '../hooks/useKeyboardShortcuts';

// API
import apiClient from '../api/client';

// Styles
import '../styles/ai-tutor-redesign.css';
import '../styles/sathi-premium.css';
import '../styles/classroom-layout.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Normalize AI content
const normalizeAIContent = (content) => {
  if (!content) return { main_response: '', sections: {} };
  if (typeof content === 'string') {
    return { main_response: content, sections: {} };
  }
  if (typeof content === 'object') {
    return {
      main_response: content.main_response || content.text || content.answer || '',
      sections: content.sections || {},
      visual_sketch: content.visual_sketch,
      follow_up_questions: content.follow_up_questions || content.followUpQuestions || [],
      ...content
    };
  }
  return { main_response: String(content), sections: {} };
};

// Format relative time
const formatRelativeTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
};

// Chat Message Component
const ChatMessage = ({ message, isUser, onSuggestionClick, userQuestion }) => {
  const content = useMemo(() => normalizeAIContent(message.content), [message.content]);
  
  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[85%] px-4 py-3 bg-purple-600 text-white rounded-2xl rounded-tr-sm shadow-sm">
          <p className="text-sm leading-relaxed">{message.content || message.text}</p>
          {message.image && (
            <img 
              src={message.image} 
              alt="Attached" 
              className="mt-2 rounded-lg max-w-full max-h-48 object-contain"
            />
          )}
        </div>
      </div>
    );
  }

  // 🆕 Extract proactive data from message
  const proactive = message.proactive || {};
  
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[90%]">
        {/* 🆕 Proactive Opener (Welcome back, streaks, etc.) */}
        {proactive.opener && (
          <ProactiveOpener opener={proactive.opener} />
        )}
        
        {/* Main AI Response - FIX: Use correct prop names */}
        <SmartResponse
          response={content}
          question={userQuestion || message.user_question || ''}
          onFollowUp={onSuggestionClick}
        />
        
        {/* 🆕 Proactive Suggestions (Follow-up buttons) */}
        {proactive.suggestions && proactive.suggestions.length > 0 && onSuggestionClick && (
          <ProactiveSuggestions 
            suggestions={proactive.suggestions}
            onSuggestionClick={onSuggestionClick}
          />
        )}
      </div>
    </div>
  );
};

// Main Sathi Classroom Component
export default function SathiClassroom() {
  const { user } = useAuth();
  const { checkFeatureAccess } = useSubscription();
  const { success: toastSuccess, error: toastError } = useToast();
  
  // Gamification
  const {
    stats: gamificationStats,
    currentReward,
    levelUp,
    streakCelebration,
    processInteraction,
    dismissReward,
    dismissLevelUp,
    dismissStreakCelebration,
    level: currentLevel,
    xp: currentXP,
    streak: currentStreak
  } = useGamification(user?.id);

  // Core State
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  // 🆕 Session duration tracking for proactive break suggestions
  const [sessionStartTime] = useState(() => Date.now());

  // Visual State
  const [visualArtifact, setVisualArtifact] = useState(null);
  
  // Image Upload State
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  
  // Refs
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Keyboard shortcuts
  const { showShortcutsHelp } = useKeyboardShortcuts({
    onNewChat: () => handleNewChat(),
    onFocusInput: () => inputRef.current?.focus(),
  }, true);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load chat history
  const loadChatHistory = useCallback(async () => {
    if (!user?.id) return;
    setIsLoadingHistory(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await apiClient.get('/ai/sessions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.sessions) {
        const formattedHistory = response.data.sessions.map(session => ({
          id: session.session_id,
          title: session.title || 'New Chat',
          subject: session.subject || 'General',
          date: formatRelativeTime(session.updated_at || session.created_at),
          updatedAt: session.updated_at,
          createdAt: session.created_at,
          isPinned: session.is_pinned || false
        }));
        setChatHistory(formattedHistory);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadChatHistory();
  }, [loadChatHistory]);

  // Create new chat
  const handleNewChat = useCallback(() => {
    setCurrentSessionId(null);
    setMessages([]);
    setVisualArtifact(null);
    inputRef.current?.focus();
  }, []);

  // Load chat session
  const handleChatSelect = useCallback(async (chat) => {
    if (!chat?.id) return;
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await apiClient.get(`/ai/sessions/${chat.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.messages) {
        setCurrentSessionId(chat.id);
        setMessages(response.data.messages.map(msg => ({
          ...msg,
          content: normalizeAIContent(msg.content)
        })));
        
        // Extract latest visual if available
        const lastAIMessage = response.data.messages
          .filter(m => m.role === 'assistant')
          .pop();
        if (lastAIMessage?.content?.visual_sketch) {
          setVisualArtifact(lastAIMessage.content.visual_sketch);
        }
      }
    } catch (error) {
      toastError('Failed to load chat');
    }
  }, [toastError]);

  // Image handling
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      toastError('Please select an image file');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      toastError('Image must be less than 10MB');
      return;
    }
    
    setSelectedImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Send message - using fetch to match working AITutorNeuroSymbolic pattern
  // FIX: Accept optional messageText parameter to avoid stale closure issues
  const handleSend = useCallback(async (messageText = null) => {
    const messageToSend = messageText || inputMessage.trim();
    if ((!messageToSend && !selectedImage) || loading) return;
    
    const userMessage = {
      role: 'user',
      content: messageToSend,
      image: imagePreview,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // CRITICAL: Create session first if none exists (backend requires session_id as non-null string)
      let sessionId = currentSessionId;
      if (!sessionId) {
        try {
          const sessionResponse = await fetch(`${BACKEND_URL}/api/ai/chat/sessions`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
              title: messageToSend.substring(0, 50),
              subject: '',
              topic: 'General'
            })
          });
          
          if (sessionResponse.ok) {
            const sessionData = await sessionResponse.json();
            sessionId = sessionData.session.session_id;
            setCurrentSessionId(sessionId);
            // Refresh chat history to show new session
            loadChatHistory();
          }
        } catch (sessionError) {
          console.error('Failed to create session:', sessionError);
          // Generate a temporary session ID as fallback
          sessionId = `temp_${Date.now()}`;
        }
      }
      
      let response;
      
      if (selectedImage) {
        // FormData for image upload - convert to base64
        const imageBase64 = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(selectedImage);
        });
        
        response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            message: messageToSend,
            session_id: sessionId,
            subject: '',
            image_url: imageBase64,
            image_context: 'Student uploaded image. Analyze it carefully.',
            // 🆕 Track session duration for proactive break suggestions
            session_minutes: Math.floor((Date.now() - sessionStartTime) / 60000)
          })
        });
      } else {
        // JSON for text-only requests
        response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            message: messageToSend,
            session_id: sessionId,
            subject: '',
            // 🆕 Track session duration for proactive break suggestions
            session_minutes: Math.floor((Date.now() - sessionStartTime) / 60000)
          })
        });
      }

      // Clear image after send
      handleRemoveImage();

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data) {
        const aiContent = normalizeAIContent(data);
        
        // 🆕 Extract proactive intelligence data
        const proactiveData = data.proactive || {};
        const proactiveOpener = proactiveData.opener || null;
        const proactiveSuggestions = proactiveData.suggestions || [];
        
        const aiMessage = {
          role: 'assistant',
          content: aiContent,
          timestamp: new Date().toISOString(),
          message_id: data.message_id,
          // 🆕 Attach proactive insights to message
          proactive: {
            opener: proactiveOpener,
            suggestions: proactiveSuggestions,
            insights: proactiveData.insights || []
          }
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
        // Update session ID if backend returned one different from what we sent
        if (data.session_id && data.session_id !== sessionId) {
          setCurrentSessionId(data.session_id);
          loadChatHistory();
        }
        
        // Extract visual artifact for SmartBoard
        if (aiContent.visual_sketch) {
          setVisualArtifact({
            ...aiContent.visual_sketch,
            concept: aiContent.concept || messageToSend.split(' ').slice(0, 3).join(' '),
            subject: aiContent.subject || 'General'
          });
        }
        
        // Process gamification
        processInteraction?.('question_asked');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toastError('Failed to get response. Please try again.');
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: {
          main_response: "Sorry, I'm having trouble right now. Please try again in a moment.",
          sections: {}
        },
        timestamp: new Date().toISOString(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  }, [inputMessage, selectedImage, currentSessionId, loading, imagePreview, loadChatHistory, processInteraction, toastError]);

  // Header actions
  const headerRightActions = (
    <>
      <NotificationBell />
      <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors">
        <Settings className="w-5 h-5" />
      </button>
    </>
  );

  // Chat content component - Full height flex layout for proper input visibility
  const ChatContent = (
    <div className="flex flex-col h-full min-h-0 max-h-full">
      {/* Messages Area - Scrollable, takes remaining space */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto px-3 sm:px-4 py-3 sm:py-4 min-h-0 overscroll-contain"
      >
        {/* Memory Banner */}
        <MemoryContextBanner />
        
        {/* Welcome or Messages */}
        {messages.length === 0 ? (
          <WelcomeScreen onSuggestionClick={(suggestion) => {
            setInputMessage(suggestion);
            handleSend(suggestion);  // FIX: Pass directly, no setTimeout
          }} />
        ) : (
          <div className="space-y-2">
            {messages.map((msg, idx) => {
              // Find the preceding user message for context
              let userQuestion = '';
              if (msg.role === 'assistant' && idx > 0) {
                for (let i = idx - 1; i >= 0; i--) {
                  if (messages[i].role === 'user') {
                    userQuestion = messages[i].content || messages[i].text || '';
                    break;
                  }
                }
              }
              
              return (
                <ChatMessage
                  key={msg.message_id || msg.timestamp || idx}
                  message={msg}
                  isUser={msg.role === 'user'}
                  userQuestion={userQuestion}
                  onSuggestionClick={(suggestion) => {
                    setInputMessage(suggestion);
                    handleSend(suggestion);
                  }}
                />
              );
            })}
          </div>
        )}
        
        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start mb-4">
            <NeuralThinkingIndicator />
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Properly centered with mobile-safe padding */}
      <div className="flex-shrink-0 border-t border-slate-800/60 bg-gradient-to-t from-slate-900 to-slate-900/95 px-3 sm:px-4 py-3 sm:py-4 pb-[env(safe-area-inset-bottom,12px)]">
        <div className="max-w-3xl mx-auto">
        {/* Image Preview */}
        {imagePreview && (
          <div className="mb-3 relative inline-block">
            <div className="relative rounded-xl overflow-hidden border-2 border-purple-300 shadow-md">
              <img
                src={imagePreview}
                alt="Upload preview"
                className="max-h-32 max-w-xs object-contain bg-slate-800/50 rounded-lg"
              />
              <button
                type="button"
                onClick={handleRemoveImage}
                className="absolute top-2 right-2 p-1.5 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
        
        {/* Input Form */}
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />
          
          <div className="flex items-end gap-3 bg-slate-800/60 rounded-2xl border border-slate-700/50 focus-within:border-violet-500/50 focus-within:ring-2 focus-within:ring-violet-500/20 p-2.5 transition-all shadow-lg">
            {/* Image Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="flex-shrink-0 p-2.5 text-slate-400 hover:text-violet-400 rounded-xl hover:bg-slate-700/50 transition-all disabled:opacity-50"
            >
              <ImageIcon className="w-5 h-5" />
            </button>
            
            {/* Textarea */}
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask anything... I'll explain like a friend 💪"
              className="flex-1 px-2 py-2.5 bg-transparent border-0 focus:ring-0 outline-none resize-none text-slate-100 placeholder-slate-500 text-[15px] leading-relaxed"
              rows={1}
              disabled={loading}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            
            {/* Send Button */}
            <motion.button
              type="submit"
              disabled={(!inputMessage.trim() && !selectedImage) || loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all ${
                inputMessage.trim() || selectedImage
                  ? 'bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-slate-700 text-slate-500 cursor-not-allowed'
              }`}
            >
              {loading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </motion.button>
          </div>
        </form>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <ClassroomLayout
        chatHistory={chatHistory}
        activeSessionId={currentSessionId}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onRenameChat={(id, title) => {
          // TODO: Implement rename
          console.log('Rename chat:', id, title);
        }}
        onDeleteChat={(id) => {
          // TODO: Implement delete
          console.log('Delete chat:', id);
        }}
        onPinChat={(id) => {
          // TODO: Implement pin
          console.log('Pin chat:', id);
        }}
        isLoadingHistory={isLoadingHistory}
        visualArtifact={visualArtifact}
        headerTitle="Sathi"
        headerRightActions={headerRightActions}
      >
        {ChatContent}
      </ClassroomLayout>

      {/* Gamification Celebrations */}
      <AnimatePresence>
        {currentReward && (
          <MicroReward reward={currentReward} onComplete={dismissReward} />
        )}
        {levelUp && (
          <LevelUpCelebration newLevel={levelUp} onComplete={dismissLevelUp} />
        )}
        {streakCelebration && (
          <StreakCelebration streak={streakCelebration} onComplete={dismissStreakCelebration} />
        )}
      </AnimatePresence>
    </>
  );
}

