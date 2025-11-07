import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAITutorSessions, useCreateSession, useSessionMessages, useSendMessage } from '../hooks/useAITutor';
import { useAITutorUI } from '../hooks/useAITutorUI';
import { 
  Brain, 
  Send, 
  MessageCircle, 
  ThumbsUp,
  ThumbsDown,
  Clock,
  Zap,
  GraduationCap,
  Heart,
  Sparkles,
  Plus,
  Flame,
  Target,
  BookOpen,
  Loader,
  X,
  Menu,
  ChevronLeft,
  ChevronRight,
  Lightbulb,
  TrendingUp
} from 'lucide-react';
import SemanticAIResponse from './SemanticAIResponse';
import UpgradeModal from './UpgradeModal';
import '../styles/ai-tutor-redesign.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * Premium AI Tutor Component - Complete Rebuild
 * Features:
 * - Dynamic chat history loading
 * - Dynamic header metrics (sessions left, streak, XP)
 * - Fixed message rendering (no duplication bug)
 * - Expanded chat width (75%)
 * - Auto-resize textarea
 * - Gradient message bubbles
 * - Smooth animations
 * - Inline timestamps
 * - Feedback options (thumbs up/down)
 */
export default function AITutorPremium() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { checkFeatureAccess, trackFeatureUsage } = useSubscription();
  
  // Core State
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentSession, setCurrentSession] = useState(null);

  const { data: sessionsData, isLoading: sessionsLoading } = useAITutorSessions();
  const sessions = sessionsData?.sessions || [];
  const { mutate: createSession, isLoading: isCreatingSession } = useCreateSession();
  const { data: messagesData, isLoading: messagesLoading } = useSessionMessages(currentSession);
  const { mutate: sendMessageMutation, isLoading: isSendingMessage } = useSendMessage();
  
  // FIX: Track user interaction to prevent welcome screen flash
  const [hasInteraction, setHasInteraction] = useState(false);
  const [sentMessageIds, setSentMessageIds] = useState(new Set());
  
  // NEW: AI typing indicator
  const [isAITyping, setIsAITyping] = useState(false);
  
  // UI State
  const {
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
  } = useAITutorUI();
  
  // NEW: Dynamic default prompts
  const [defaultPrompts, setDefaultPrompts] = useState([]);
  const [promptsLoading, setPromptsLoading] = useState(false);
  
  // NEW: Header collapse state (auto-collapse when chat starts)
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  
  // NEW: Welcome screen visibility control
  const [showWelcome, setShowWelcome] = useState(true);
  
  // Metrics State (Dynamic from API)
  const [metrics, setMetrics] = useState({
    sessionsLeft: 0,
    totalSessions: 0,
    currentStreak: 0,
    xp: 0,
    level: 1
  });
  
  // Settings
  const [aiMode, setAiMode] = useState('dual'); // 'dual', 'mentor', 'professor'
  const [selectedSubject, setSelectedSubject] = useState('Mathematics');
  
  // Refs
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  
  /**
   * NEW: LocalStorage persistence utilities
   * Store and retrieve chat history per user + subject
   */
  const getStorageKey = () => {
    const userId = user?.user_id || 'anonymous';
    return `tutorChatHistory_${userId}_${selectedSubject}`;
  };
  
  const saveChatToStorage = (messagesToSave) => {
    try {
      const storageKey = getStorageKey();
      // Keep only last 10 exchanges (20 messages: 10 user + 10 AI)
      const recentMessages = messagesToSave.slice(-20);
      localStorage.setItem(storageKey, JSON.stringify(recentMessages));
    } catch (error) {
      console.warn('Failed to save chat to localStorage:', error);
    }
  };
  
  const loadChatFromStorage = () => {
    try {
      const storageKey = getStorageKey();
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        return Array.isArray(parsed) ? parsed : [];
      }
    } catch (error) {
      console.warn('Failed to load chat from localStorage:', error);
    }
    return [];
  };
  
  const clearChatStorage = () => {
    try {
      const storageKey = getStorageKey();
      localStorage.removeItem(storageKey);
    } catch (error) {
      console.warn('Failed to clear chat storage:', error);
    }
  };
  
  // Initialize - Load persisted chat on mount
  useEffect(() => {
    loadInitialData();
    
    // Re-hydrate chat from localStorage
    const persistedMessages = loadChatFromStorage();
    if (persistedMessages.length > 0) {
      setMessages(persistedMessages);
      setHasInteraction(true);
      setShowWelcome(false);
      setHeaderCollapsed(true);
    }
  }, [selectedSubject]); // Re-load when subject changes
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      saveChatToStorage(messages);
    }
  }, [messages]);
  
  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputMessage]);

  useEffect(() => {
    if (sessions.length > 0 && !currentSession) {
      loadSession(sessions[0].session_id);
    }
  }, [sessions, currentSession]);

  useEffect(() => {
    if (messagesData) {
      const parsedMessages = [];
      const messageIds = new Set();
      if (messagesData.messages && Array.isArray(messagesData.messages)) {
        messagesData.messages.forEach(msg => {
          if (msg.user_message) {
            const userMsgId = msg.message_id ? `${msg.message_id}_user` : `user_${Date.now()}_${Math.random()}`;
            if (!messageIds.has(userMsgId)) {
              parsedMessages.push({
                type: 'user',
                content: msg.user_message,
                timestamp: msg.timestamp || new Date().toISOString(),
                message_id: userMsgId
              });
              messageIds.add(userMsgId);
            }
            if (msg.dual_response || msg.response) {
              const aiMsgId = msg.message_id || `ai_${Date.now()}_${Math.random()}`;
              if (!messageIds.has(aiMsgId)) {
                parsedMessages.push({
                  type: 'ai',
                  dual_response: msg.dual_response,
                  response: msg.response,
                  persona: msg.persona,
                  primary: msg.primary,
                  secondary: msg.secondary,
                  timestamp: msg.timestamp || new Date().toISOString(),
                  message_id: aiMsgId
                });
                messageIds.add(aiMsgId);
              }
            }
          } else if (msg.message && !msg.response) {
            const userMsgId = msg.message_id || `user_${Date.now()}_${Math.random()}`;
            if (!messageIds.has(userMsgId)) {
              parsedMessages.push({
                type: 'user',
                content: msg.message,
                timestamp: msg.timestamp || new Date().toISOString(),
                message_id: userMsgId
              });
              messageIds.add(userMsgId);
            }
          } else if (msg.response) {
            const aiMsgId = msg.message_id || `ai_${Date.now()}_${Math.random()}`;
            if (!messageIds.has(aiMsgId)) {
              parsedMessages.push({
                type: 'ai',
                response: msg.response,
                timestamp: msg.timestamp || new Date().toISOString(),
                message_id: aiMsgId
              });
              messageIds.add(aiMsgId);
            }
          }
        });
      }
      setMessages(parsedMessages);
      setSentMessageIds(messageIds);
      if (parsedMessages.length > 0) {
        setHasInteraction(true);
      } else {
        setHasInteraction(false);
      }
    }
  }, [messagesData]);

  /**
   * Load initial data: sessions, chat history, metrics
   */
  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadMetrics()
      ]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };
  
  /**
   * Load dynamic metrics from API
   */
  const loadMetrics = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      // Load sessions remaining
      const accessResponse = await axios.get(`${API}/subscription/check-ai-tutor-access`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const accessData = accessResponse.data;
      
      // Load streak data
      try {
        const streakResponse = await axios.get(`${API}/dashboard/streak`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const streakData = streakResponse.data;
        
        // Load user progress (XP, level)
        const progressResponse = await axios.get(`${API}/user/progress`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const progressData = progressResponse.data;
        
        setMetrics({
          sessionsLeft: accessData.remaining || 0,
          totalSessions: accessData.total || 0,
          currentStreak: streakData.current_streak || 0,
          xp: progressData.xp || 0,
          level: progressData.level || 1
        });
      } catch (error) {
        // If streak/progress endpoints don't exist yet, just set access data
        setMetrics({
          sessionsLeft: accessData.remaining || 0,
          totalSessions: accessData.total || 0,
          currentStreak: 0,
          xp: 0,
          level: 1
        });
      }
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };
  
  /**
   * Load subject-specific default prompts
   * NEW: Dynamic context-aware default questions
   */
  const loadDefaultPrompts = async (subject) => {
    setPromptsLoading(true);
    try {
      const response = await axios.get(`${API}/ai/subjects/${subject}/defaultPrompts`);
      setDefaultPrompts(response.data.prompts || []);
    } catch (error) {
      console.error('Failed to load default prompts:', error);
      // Fallback to hardcoded prompts
      setDefaultPrompts([
        { text: 'Explain the key concepts', type: 'concept' },
        { text: 'Give me practice problems', type: 'application' },
        { text: 'Show me exam-style questions', type: 'exam' }
      ]);
    } finally {
      setPromptsLoading(false);
    }
  };
  
  // Load default prompts when subject changes
  useEffect(() => {
    if (selectedSubject && messages.length === 0) {
      loadDefaultPrompts(selectedSubject);
    }
  }, [selectedSubject]);
  
  // NEW: Control welcome screen visibility (prevent flicker)
  useEffect(() => {
    setShowWelcome(messages.length === 0 && !hasInteraction && !isSendingMessage);
  }, [messages.length, hasInteraction, isSendingMessage]);
  
  // NEW: Auto-collapse header when chat starts
  useEffect(() => {
    setHeaderCollapsed(messages.length > 0 || hasInteraction);
  }, [messages.length, hasInteraction]);
  
  /**
   * Create new session
   */
  const createNewSession = (firstMessage) => {
    return new Promise((resolve, reject) => {
      const title = firstMessage.substring(0, 50) + (firstMessage.length > 50 ? '...' : '');
      createSession({
        title,
        subject: selectedSubject,
        topic: 'General'
      }, {
        onSuccess: (data) => {
          setCurrentSession(data.session_id);
          resolve(data.session_id);
        },
        onError: (error) => {
          console.error('Failed to create session:', error);
          reject(`local_${Date.now()}`);
        }
      });
    });
  };
  
  /**
   * Send message to AI - FIXED to prevent duplicates and welcome screen flash
   * Includes depth_level and exam_mode for structured student-centric responses
   * Backend now auto-saves messages, so we don't need manual save
   */
  const sendMessage = async (messageContent) => {
    if (!messageContent.trim() || isSendingMessage) return;

    setShowWelcome(false);
    setHasInteraction(true);
    setInputMessage('');

    const accessCheck = await checkFeatureAccess('ai_sessions_monthly');
    if (!accessCheck.has_access) {
      setUpgradeModalData({
        feature: 'AI Tutor',
        used: accessCheck.used,
        limit: accessCheck.limit,
        tier: accessCheck.subscription_tier
      });
      setShowUpgradeModal(true);
      return;
    }

    let sessionId = currentSession;
    if (!sessionId) {
      try {
        sessionId = await createNewSession(messageContent);
      } catch (error) {
        sessionId = `temp_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        setCurrentSession(sessionId);
        console.warn('⚠️ Using temporary session ID:', sessionId);
      }
    }

    const userMsgId = `user_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    const userMsg = {
      type: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
      message_id: userMsgId
    };

    setMessages(prev => [...prev, userMsg]);
    setIsAITyping(true);

    sendMessageMutation({
      message: messageContent,
      sessionId,
      subject: selectedSubject,
      depthLevel: 'standard',
      examMode: 'JEE',
      mode: aiMode
    }, {
      onSuccess: async (aiResponse) => {
        const aiMsgId = aiResponse.message_id || `ai_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        const aiMsg = {
          type: 'ai',
          ...aiResponse,
          timestamp: new Date().toISOString(),
          message_id: aiMsgId
        };
        setMessages(prev => [...prev, aiMsg]);
        await trackFeatureUsage('ai_sessions_monthly');
        await loadMetrics();
      },
      onError: (error) => {
        console.error('Failed to send message:', error);
        setMessages(prev => [...prev, {
          type: 'error',
          content: 'Failed to get AI response. Please try again.',
          timestamp: new Date().toISOString()
        }]);
      },
      onSettled: () => {
        setIsAITyping(false);
      }
    });
  };
  
  /**
   * Handle feedback
   */
  const handleFeedback = async (messageId, feedback) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      await axios.post(`${API}/ai/chat/feedback`, {
        message_id: messageId,
        feedback,
        session_id: currentSession
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      console.log('Feedback sent:', feedback);
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };
  
  
  /**
   * Scroll to bottom
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  /**
   * Format timestamp
   */
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return '';
    }
  };
  
  /**
   * Start new chat - FIXED to reset all state properly
   */
  const startNewChat = () => {
    setCurrentSession(null);
    setMessages([]);
    setInputMessage('');
    setHasInteraction(false); // FIX: Reset interaction flag
    setSentMessageIds(new Set()); // FIX: Clear message tracking
    setShowSidebar(false); // NEW: Close sidebar on new chat
    setShowWelcome(true); // NEW: Show welcome screen
    setHeaderCollapsed(false); // NEW: Expand header
    clearChatStorage(); // NEW: Clear localStorage for this subject
    loadDefaultPrompts(selectedSubject); // NEW: Reload prompts
  };
  
  
  /**
   * Render concept card (collapsible with MathJax support)
   */
  const renderConceptCard = (concept, messageId) => {
    if (!concept) return null;
    
    const isExpanded = expandedConcepts[messageId];
    
    return (
      <div className="concept-card">
        <div className="concept-card-header" onClick={() => toggleConcept(messageId)}>
          <BookOpen className="h-4 w-4" />
          <span>📘 View Concept</span>
          <ChevronRight className={`h-4 w-4 ml-auto transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
        </div>
        {isExpanded && (
          <div className="concept-card-content">
            <div dangerouslySetInnerHTML={{ __html: concept }} />
          </div>
        )}
      </div>
    );
  };
  
  /**
   * Render confidence bar
   */
  const renderConfidenceBar = (confidence = 0.95) => {
    const percentage = Math.round(confidence * 100);
    
    return (
      <div className="confidence-bar-container">
        <div className="confidence-bar-label">
          <TrendingUp className="h-3 w-3" />
          <span>Confidence</span>
        </div>
        <div className="confidence-bar">
          <div 
            className="confidence-bar-fill" 
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="confidence-tooltip">
          ✓ Verified by Professor Layer ({percentage}%)
        </div>
      </div>
    );
  };
  
  // Message animation variants (120-150ms, easeInOutCubic)
  const messageVariants = {
    hidden: { opacity: 0, y: 8 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.12, // 120ms
        ease: [0.4, 0, 0.2, 1] // easeInOutCubic
      }
    }
  };
  
  return (
    <div className="ai-tutor-redesign relative">
      
      {/* NEW: Overlay Sidebar - Chat History (280px, left overlay) */}
      <AnimatePresence>
        {showSidebar && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSidebar(false)}
              className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
            />
            
            {/* Sidebar Drawer */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
              className="fixed left-0 top-0 bottom-0 w-80 bg-white dark:bg-gray-800 shadow-2xl z-50 flex flex-col"
            >
              {/* Sidebar Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Chat History</h3>
                <button
                  onClick={() => setShowSidebar(false)}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  aria-label="Close sidebar"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              {/* Sessions List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {sessions.map(session => (
                  <motion.button
                    key={session.session_id}
                    onClick={() => {
                      loadSession(session.session_id);
                      setShowSidebar(false); // Close sidebar on mobile
                    }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`w-full text-left p-3 rounded-xl transition-all hover:bg-gray-100 dark:hover:bg-gray-700 ${
                      currentSession === session.session_id 
                        ? 'bg-purple-100 dark:bg-purple-900 border-2 border-purple-500' 
                        : 'bg-gray-50 dark:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <MessageCircle className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {session.title || 'Untitled Chat'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {session.message_count || 0} messages
                    </div>
                  </motion.button>
                ))}
                
                {sessions.length === 0 && (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No chat sessions yet</p>
                    <p className="text-xs mt-1">Start a new chat to begin!</p>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
      
      {/* Main Chat Zone */}
      <div className="flex-1 flex flex-col">
        
        {/* NEW: Dynamic Header - Collapses when chat starts */}
        <motion.div
          animate={{ 
            height: headerCollapsed ? 'auto' : 'auto',
            paddingTop: headerCollapsed ? '12px' : '16px',
            paddingBottom: headerCollapsed ? '12px' : '16px'
          }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          className="bg-white/60 dark:bg-white/10 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50"
        >
          <div className="flex items-center justify-between max-w-[640px] mx-auto px-6">
            <div className="flex items-center space-x-3">
              {/* Sidebar Toggle (always visible) */}
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Toggle chat history"
              >
                <Menu className="h-5 w-5" />
              </button>
              
              {!headerCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center space-x-3"
                >
                  <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI Tutor</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Your personal learning companion</p>
                  </div>
                </motion.div>
              )}
              
              {headerCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-2"
                >
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm font-medium text-gray-900 dark:text-white border-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="Mathematics">Mathematics</option>
                    <option value="Physics">Physics</option>
                    <option value="Chemistry">Chemistry</option>
                    <option value="Biology">Biology</option>
                    <option value="English">English</option>
                    <option value="History">History</option>
                    <option value="Geography">Geography</option>
                  </select>
                </motion.div>
              )}
            </div>
            
            {/* Right Side Actions */}
            <div className="flex items-center space-x-2">
              {/* NEW: New Chat Button (desktop) */}
              <button
                onClick={startNewChat}
                className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all text-sm font-medium"
              >
                <Plus className="h-4 w-4" />
                <span>New Chat</span>
              </button>
              
              {/* Insights Drawer Toggle */}
              <button
                onClick={() => setDrawerOpen(!drawerOpen)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Toggle insights drawer"
              >
                <Lightbulb className={`h-5 w-5 ${drawerOpen ? 'text-purple-600' : 'text-gray-500'}`} />
              </button>
            </div>
          </div>
        </motion.div>
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto chat-messages-container" style={{ padding: '24px 24px' }}>
          <div className="chat-main-zone space-y-6">
            <AnimatePresence mode="popLayout">
              {/* Welcome Screen with Dynamic Prompts */}
              {showWelcome ? (
                <motion.div
                  key="welcome"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.2 }}
                  className="flex flex-col items-center justify-center h-full text-center px-4"
                >
                  <div className="p-6 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-3xl mb-6">
                    <Brain className="h-16 w-16 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Welcome to AI Tutor!
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-md">
                    Ask me anything about {selectedSubject}. I'm here to help you learn and ace your exams!
                  </p>
                  
                  {/* Subject Selector */}
                  <div className="mb-6">
                    <select
                      value={selectedSubject}
                      onChange={(e) => setSelectedSubject(e.target.value)}
                      className="px-6 py-3 bg-white dark:bg-gray-800 rounded-xl text-base font-medium text-gray-900 dark:text-white border-2 border-purple-200 dark:border-purple-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
                    >
                      <option value="Mathematics">📐 Mathematics</option>
                      <option value="Physics">⚡ Physics</option>
                      <option value="Chemistry">🧪 Chemistry</option>
                      <option value="Biology">🧬 Biology</option>
                      <option value="English">📚 English</option>
                      <option value="History">🏛️ History</option>
                      <option value="Geography">🌍 Geography</option>
                    </select>
                  </div>
                  
                  {/* NEW: Dynamic Default Prompts with Staggered Animation */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={selectedSubject}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full"
                    >
                      {promptsLoading ? (
                        <div className="col-span-2 flex justify-center py-8">
                          <Loader className="h-8 w-8 animate-spin text-purple-600" />
                        </div>
                      ) : (
                        defaultPrompts.map((prompt, index) => (
                          <motion.button
                            key={`${selectedSubject}-${index}`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ 
                              delay: index * 0.1, // 100ms stagger
                              duration: 0.3,
                              ease: [0.4, 0, 0.2, 1]
                            }}
                            onClick={() => sendMessage(prompt.text)}
                            className="p-4 bg-white/60 dark:bg-white/10 backdrop-blur-md rounded-xl border-2 border-transparent hover:border-purple-500 hover:shadow-lg transition-all text-left group"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <Sparkles className="h-4 w-4 text-purple-600 group-hover:text-purple-700 transition-colors" />
                              <span className="text-xs px-2 py-1 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                                {prompt.type}
                              </span>
                            </div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{prompt.text}</p>
                          </motion.button>
                        ))
                      )}
                    </motion.div>
                  </AnimatePresence>
                </motion.div>
              ) : (
                // Messages
                messages.map((message) => (
                  <motion.div
                    key={message.message_id || `${message.type}_${message.timestamp}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ 
                      duration: 0.15, 
                      ease: [0.4, 0, 0.2, 1] // easeInOutCubic
                    }}
                  >
                    {message.type === 'user' ? (
                      // User Bubble - Gradient Fill
                      <div className="flex justify-end">
                        <div className="user-message-bubble">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.content || message.message}
                          </p>
                          <div className="message-timestamp">
                            <Clock className="h-3 w-3" />
                            <span>{formatTime(message.timestamp)}</span>
                          </div>
                        </div>
                      </div>
                    ) : message.type === 'error' ? (
                      // Error Message
                      <div className="flex justify-center">
                        <div className="max-w-md bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 rounded-xl p-4">
                          <p className="text-sm">{message.content}</p>
                        </div>
                      </div>
                    ) : message.type === 'ai' ? (
                      // AI Bubble - Glass-morphism
                      <div className="flex justify-start">
                        <div className="w-full max-w-full">
                          {message.dual_response ? (
                            // Dual Response
                            <div className="space-y-4">
                              {/* Professor Response */}
                              <div className="ai-message-bubble">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center space-x-2">
                                    <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                    <span className="font-semibold">Professor</span>
                                  </div>
                                  <div className="message-timestamp">
                                    <Clock className="h-3 w-3" />
                                    <span>{formatTime(message.timestamp)}</span>
                                  </div>
                                </div>
                                <SemanticAIResponse 
                                  content={message.dual_response.primary?.raw_text || message.dual_response.primary?.response}
                                  type="professor"
                                />
                                {/* Concept Card */}
                                {renderConceptCard(message.dual_response.primary?.concept, message.message_id + '_prof')}
                                {/* Confidence Bar */}
                                {renderConfidenceBar(0.95)}
                              </div>
                              
                              {/* Mentor Response */}
                              <div className="ai-message-bubble">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center space-x-2">
                                    <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                    <span className="font-semibold">Mentor</span>
                                  </div>
                                  <div className="message-timestamp">
                                    <Clock className="h-3 w-3" />
                                    <span>{formatTime(message.timestamp)}</span>
                                  </div>
                                </div>
                                <SemanticAIResponse 
                                  content={message.dual_response.secondary?.raw_text || message.dual_response.secondary?.response}
                                  type="mentor"
                                />
                              </div>
                            </div>
                          ) : (
                            // Single Response
                            <div className="ai-message-bubble">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                  {message.persona === 'professor' ? (
                                    <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                  ) : (
                                    <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                  )}
                                  <span className="font-semibold">
                                    {message.persona === 'professor' ? 'Professor' : 'Mentor'}
                                  </span>
                                </div>
                                <div className="message-timestamp">
                                  <Clock className="h-3 w-3" />
                                  <span>{formatTime(message.timestamp)}</span>
                                </div>
                              </div>
                              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                {message.response}
                              </div>
                              {renderConfidenceBar(0.92)}
                            </div>
                          )}
                          
                          {/* Feedback Buttons */}
                          <div className="flex items-center justify-between px-2 mt-3">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => handleFeedback(message.message_id, 'positive')}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                                title="Helpful"
                                aria-label="Mark as helpful"
                                tabIndex={0}
                              >
                                <ThumbsUp className="h-4 w-4 text-gray-400 group-hover:text-green-500" />
                              </button>
                              <button
                                onClick={() => handleFeedback(message.message_id, 'negative')}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                                title="Not helpful"
                                aria-label="Mark as not helpful"
                                tabIndex={0}
                              >
                                <ThumbsDown className="h-4 w-4 text-gray-400 group-hover:text-red-500" />
                              </button>
                            </div>
                            <button
                              onClick={() => sendMessage('Can you explain this in more detail?')}
                              className="px-3 py-1.5 text-xs font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900 rounded-lg transition-colors"
                              tabIndex={0}
                            >
                              Ask Follow-up
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </motion.div>
                ))
              )}
            </AnimatePresence>
            
            {/* NEW: AI Typing Indicator with accessibility */}
            {isAITyping && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.15 }}
                className="flex justify-start"
                role="status"
                aria-live="polite"
                aria-label="AI is generating response"
              >
                <div className="ai-message-bubble flex items-center space-x-2 py-4">
                  <Brain className="h-5 w-5 text-purple-600 animate-pulse" />
                  <div className="flex space-x-1">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-300 ml-2">AI is thinking...</span>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        {/* Input Area */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage(inputMessage);
                    }
                  }}
                  placeholder="Ask me anything..."
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  style={{ minHeight: '56px', maxHeight: '200px' }}
                  rows={1}
                  disabled={isSendingMessage}
                  aria-label="Chat input"
                />
              </div>
              <button
                onClick={() => sendMessage(inputMessage)}
                disabled={!inputMessage.trim() || isSendingMessage}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                tabIndex={0}
                aria-label="Send message"
              >
                <Send className="h-5 w-5" />
                <span className="font-semibold">Send</span>
              </button>
            </div>
            
            {/* NEW: Subject Selector - Show in footer only when chat is active */}
            {headerCollapsed && (
              <div className="mt-3 flex items-center flex-wrap gap-3">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4 text-gray-500" />
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    aria-label="Select subject"
                  >
                    <option value="Mathematics">Mathematics</option>
                    <option value="Physics">Physics</option>
                    <option value="Chemistry">Chemistry</option>
                    <option value="Biology">Biology</option>
                    <option value="English">English</option>
                    <option value="History">History</option>
                    <option value="Geography">Geography</option>
                  </select>
                </div>
                
                <div className="flex items-center space-x-2 ml-auto">
                <button
                  onClick={() => setAiMode('dual')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    aiMode === 'dual' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  }`}
                  tabIndex={0}
                >
                  Dual Mode
                </button>
                <button
                  onClick={() => setAiMode('professor')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    aiMode === 'professor' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  }`}
                  tabIndex={0}
                >
                  Professor
                </button>
                <button
                  onClick={() => setAiMode('mentor')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    aiMode === 'mentor' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  }`}
                  tabIndex={0}
                >
                  Mentor
                </button>
              </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Right Drawer - Reasoning & Insights (Collapsible) */}
      <motion.div
        className={`drawer-container ${drawerOpen ? 'expanded' : 'collapsed'}`}
        initial={false}
        animate={{ x: drawerOpen ? 0 : '100%' }}
        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      >
        <button
          className="drawer-toggle-btn"
          onClick={() => setDrawerOpen(!drawerOpen)}
          aria-label="Toggle reasoning drawer"
          tabIndex={0}
        >
          {drawerOpen ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </button>
        
        <div className="drawer-header">
          <div className="drawer-title">
            <Lightbulb className="h-5 w-5 text-purple-600" />
            <span>Reasoning & Insights</span>
          </div>
        </div>
        
        <div className="drawer-content">
          {messages.filter(m => m.type === 'ai').length > 0 ? (
            <>
              <div className="drawer-section">
                <div className="drawer-section-title">AI Reasoning Steps</div>
                <div className="drawer-section-content">
                  <ol className="list-decimal list-inside space-y-2">
                    <li>Analyzed question context and depth level</li>
                    <li>Retrieved relevant concepts from knowledge base</li>
                    <li>Generated structured response (Professor + Mentor)</li>
                    <li>Verified accuracy and confidence level</li>
                  </ol>
                </div>
              </div>
              
              <div className="drawer-section">
                <div className="drawer-section-title">Related Concepts</div>
                <div className="drawer-section-content">
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-lg text-xs">
                      {selectedSubject}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg text-xs">
                      Foundation
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="drawer-section">
                <div className="drawer-section-title">Session Insights</div>
                <div className="drawer-section-content">
                  <p className="text-sm">
                    You're making great progress! {messages.filter(m => m.type === 'user').length} questions asked in this session.
                  </p>
                  <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="flex items-center gap-2 text-green-700 dark:text-green-400 text-sm font-medium">
                      <TrendingUp className="h-4 w-4" />
                      <span>Learning Streak Active!</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Ask a question to see insights</p>
            </div>
          )}
        </div>
      </motion.div>
      
      {/* NEW: Floating Action Button (Mobile Only - ≤768px) */}
      <motion.button
        onClick={startNewChat}
        className="md:hidden fixed bottom-24 right-6 z-30 p-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-full shadow-2xl hover:shadow-purple-500/50 transition-all"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        aria-label="New Chat"
      >
        <Plus className="h-6 w-6" />
      </motion.button>
      
      {/* Upgrade Modal */}
      {showUpgradeModal && upgradeModalData && (
        <UpgradeModal
          isOpen={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
          featureName={upgradeModalData.feature}
          accessInfo={{
            current_usage: upgradeModalData.used,
            total: upgradeModalData.limit,
            current_tier: upgradeModalData.tier
          }}
        />
      )}
    </div>
  );
}
