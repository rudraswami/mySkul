import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
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
  Menu
} from 'lucide-react';
import SemanticAIResponse from './SemanticAIResponse';
import UpgradeModal from './UpgradeModal';

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
  const [loading, setLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  
  // FIX: Track user interaction to prevent welcome screen flash
  const [hasInteraction, setHasInteraction] = useState(false);
  const [sentMessageIds, setSentMessageIds] = useState(new Set());
  
  // UI State
  const [showSidebar, setShowSidebar] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalData, setUpgradeModalData] = useState(null);
  
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
  
  // Initialize
  useEffect(() => {
    loadInitialData();
  }, []);
  
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
  
  /**
   * Load initial data: sessions, chat history, metrics
   */
  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadSessions(),
        loadMetrics()
      ]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };
  
  /**
   * Load user sessions from backend
   */
  const loadSessions = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      const response = await axios.get(`${API}/ai/chat/sessions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const sessionList = response.data.sessions || [];
      setSessions(sessionList);
      
      // Auto-load most recent session if exists
      if (sessionList.length > 0 && !currentSession) {
        loadSession(sessionList[0].session_id);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setSessions([]);
    }
  };
  
  /**
   * Load specific session's chat history
   * CRITICAL: Fixed message parsing and prevents welcome screen flash
   */
  const loadSession = async (sessionId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      setLoading(true);
      const response = await axios.get(`${API}/ai/chat/${sessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const sessionData = response.data;
      setCurrentSession(sessionId);
      
      // Parse messages correctly - handle BOTH old format (combined) and new format (split)
      const parsedMessages = [];
      const messageIds = new Set();
      
      if (sessionData.messages && Array.isArray(sessionData.messages)) {
        sessionData.messages.forEach(msg => {
          // NEW FORMAT: Messages with user_message field store user + AI together
          if (msg.user_message) {
            // Add user message
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
            
            // Add AI response (if exists)
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
          } 
          // OLD FORMAT: Separate user and AI message objects
          else if (msg.message && !msg.response) {
            // User message only
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
            // AI response only
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
      
      // FIX: Set hasInteraction if messages exist to prevent welcome screen
      if (parsedMessages.length > 0) {
        setHasInteraction(true);
      } else {
        setHasInteraction(false);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      setMessages([]);
      setSentMessageIds(new Set());
      setHasInteraction(false);
    } finally {
      setLoading(false);
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
   * Create new session
   */
  const createNewSession = async (firstMessage) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return null;
      
      const title = firstMessage.substring(0, 50) + (firstMessage.length > 50 ? '...' : '');
      
      const response = await axios.post(`${API}/ai/chat/sessions`, {
        title,
        subject: selectedSubject,
        topic: 'General',
        ai_mode: aiMode
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const sessionId = response.data.session_id;
      setCurrentSession(sessionId);
      await loadSessions(); // Refresh session list
      
      return sessionId;
    } catch (error) {
      console.error('Failed to create session:', error);
      return `local_${Date.now()}`;
    }
  };
  
  /**
   * Send message to AI - FIXED to prevent duplicates and welcome screen flash
   * Includes depth_level and exam_mode for structured student-centric responses
   * Backend now auto-saves messages, so we don't need manual save
   */
  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;
    
    // FIX: Set interaction immediately to prevent welcome screen flash
    setHasInteraction(true);
    
    // Check access
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
    
    const messageToSend = inputMessage;
    setInputMessage('');
    setLoading(true);
    
    try {
      // CRITICAL: ALWAYS create session before sending message
      let sessionId = currentSession;
      if (!sessionId) {
        sessionId = await createNewSession(messageToSend);
        
        // If session creation fails, generate temporary ID
        if (!sessionId) {
          sessionId = `temp_${Date.now()}_${Math.random().toString(36).substring(7)}`;
          setCurrentSession(sessionId);
          console.warn('⚠️ Using temporary session ID:', sessionId);
        }
      }
      
      // Add user message immediately to UI with unique ID
      const userMsgId = `user_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      const userMsg = {
        type: 'user',
        content: messageToSend,
        timestamp: new Date().toISOString(),
        message_id: userMsgId
      };
      
      // FIX: Check for duplicates before adding
      if (!sentMessageIds.has(userMsgId)) {
        setMessages(prev => [...prev, userMsg]);
        setSentMessageIds(prev => new Set([...prev, userMsgId]));
      }
      
      // Call AI API with ALL required parameters for structured responses
      const token = localStorage.getItem('dhruv_ai_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const requestBody = {
        message: messageToSend,
        subject: selectedSubject,
        session_id: sessionId,
        depth_level: 'standard',
        exam_mode: 'JEE'
      };
      
      let response;
      if (aiMode === 'dual') {
        response = await axios.post(`${API}/ai/dual-response`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      } else if (aiMode === 'mentor') {
        response = await axios.post(`${API}/ai/mentor-only`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      } else {
        response = await axios.post(`${API}/ai/professor-only`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      }
      
      const aiResponse = response.data;
      
      // Add AI response to UI with unique ID
      const aiMsgId = aiResponse.message_id || `ai_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      const aiMsg = {
        type: 'ai',
        ...aiResponse,
        timestamp: new Date().toISOString(),
        message_id: aiMsgId
      };
      
      // FIX: Check for duplicates before adding
      if (!sentMessageIds.has(aiMsgId)) {
        setMessages(prev => [...prev, aiMsg]);
        setSentMessageIds(prev => new Set([...prev, aiMsgId]));
      }
      
      // Track usage and refresh metrics
      await trackFeatureUsage('ai_sessions_monthly');
      await loadMetrics();
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMsgId = `error_${Date.now()}`;
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to get AI response. Please try again.',
        timestamp: new Date().toISOString(),
        message_id: errorMsgId
      }]);
    } finally {
      setLoading(false);
    }
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
   * Handle follow-up question or predefined question
   * Now actually sends the message instead of just populating input
   */
  const handleFollowUp = (content) => {
    if (!content.trim() || loading) return;
    
    // Set the input message
    setInputMessage(content);
    
    // Immediately trigger send with this content
    handleQuickSend(content);
  };
  
  /**
   * Quick send for predefined questions
   */
  const handleQuickSend = async (messageContent) => {
    if (!messageContent.trim() || loading) return;
    
    // Clear input and send
    setInputMessage('');
    setLoading(true);
    
    // Check access
    const accessCheck = await checkFeatureAccess('ai_sessions_monthly');
    if (!accessCheck.has_access) {
      setUpgradeModalData({
        feature: 'AI Tutor',
        used: accessCheck.used,
        limit: accessCheck.limit,
        tier: accessCheck.subscription_tier
      });
      setShowUpgradeModal(true);
      setLoading(false);
      return;
    }
    
    try {
      // CRITICAL: ALWAYS create session before sending message
      let sessionId = currentSession;
      if (!sessionId) {
        sessionId = await createNewSession(messageContent);
        
        // If session creation fails, generate temporary ID
        if (!sessionId) {
          sessionId = `temp_${Date.now()}_${Math.random().toString(36).substring(7)}`;
          setCurrentSession(sessionId);
          console.warn('⚠️ Using temporary session ID:', sessionId);
        }
      }
      
      // Add user message immediately to UI
      const userMsg = {
        type: 'user',
        content: messageContent,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, userMsg]);
      
      // Call AI API
      const token = localStorage.getItem('dhruv_ai_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const requestBody = {
        message: messageContent,
        subject: selectedSubject,
        session_id: sessionId,
        depth_level: 'standard',
        exam_mode: 'JEE'
      };
      
      let response;
      if (aiMode === 'dual') {
        response = await axios.post(`${API}/ai/dual-response`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      } else if (aiMode === 'mentor') {
        response = await axios.post(`${API}/ai/mentor-only`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      } else {
        response = await axios.post(`${API}/ai/professor-only`, requestBody, { 
          headers, 
          timeout: 45000 
        });
      }
      
      const aiResponse = response.data;
      
      // Add AI response to UI
      const aiMsg = {
        type: 'ai',
        ...aiResponse,
        timestamp: new Date().toISOString(),
        message_id: aiResponse.message_id || `msg_${Date.now()}`
      };
      
      setMessages(prev => [...prev, aiMsg]);
      
      // Track usage and refresh metrics
      await trackFeatureUsage('ai_sessions_monthly');
      await loadMetrics();
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to get AI response. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
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
   * Start new chat
   */
  const startNewChat = () => {
    setCurrentSession(null);
    setMessages([]);
    setInputMessage('');
  };
  
  // Message animation variants
  const messageVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3 }
    }
  };
  
  return (
    <div className="flex h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900">
      
      {/* Sidebar - Sessions */}
      {showSidebar && (
        <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={startNewChat}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all"
            >
              <Plus className="h-5 w-5" />
              <span className="font-semibold">New Chat</span>
            </button>
          </div>
          
          {/* Sessions List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {sessions.map(session => (
              <button
                key={session.session_id}
                onClick={() => loadSession(session.session_id)}
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
              </button>
            ))}
            
            {sessions.length === 0 && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No chat sessions yet</p>
                <p className="text-xs mt-1">Start a new chat to begin!</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Main Chat Area - 75% width */}
      <div className="flex-1 flex flex-col" style={{ maxWidth: showSidebar ? '75%' : '100%' }}>
        
        {/* Header with Dynamic Metrics */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center space-x-3">
              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                {showSidebar ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
              
              <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI Tutor</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Your personal learning companion</p>
              </div>
            </div>
            
            {/* Dynamic Metrics */}
            <div className="hidden md:flex items-center space-x-6">
              {/* Sessions Left */}
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">
                    {metrics.sessionsLeft} left today
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    of {metrics.totalSessions}
                  </div>
                </div>
              </div>
              
              {/* Streak */}
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                  <Flame className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">
                    {metrics.currentStreak} day streak
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Keep it up! 🔥
                  </div>
                </div>
              </div>
              
              {/* Level */}
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <Target className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">
                    Level {metrics.level}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {metrics.xp} XP
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6" style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          <AnimatePresence>
            {messages.length === 0 ? (
              // Empty state
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="p-6 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-3xl mb-6">
                  <Brain className="h-16 w-16 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Welcome to AI Tutor!
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md">
                  Ask me anything about {selectedSubject}. I'm here to help you learn and ace your exams!
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
                  {[
                    'Explain quadratic equations',
                    'Help me with calculus',
                    'What is photosynthesis?',
                    'Solve this problem for me'
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleFollowUp(suggestion)}
                      className="p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-500 dark:hover:border-purple-500 transition-all text-left"
                    >
                      <Sparkles className="h-4 w-4 text-purple-600 mb-2" />
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{suggestion}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Messages
              messages.map((message, index) => (
                <motion.div
                  key={index}
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {/* CRITICAL: Render message based on OLD structure */}
                  {message.type === 'user' ? (
                    // Simple user message (sent before AI response)
                    <div className="flex justify-end">
                      <div className="max-w-2xl bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-br-md p-4 shadow-lg">
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content || message.message}</p>
                        <div className="flex items-center justify-end mt-2 text-xs text-blue-100 opacity-75">
                          <Clock className="h-3 w-3 mr-1" />
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
                    // AI response from new messages (already split into user + AI)
                    <div className="flex justify-start">
                      <div className="max-w-4xl w-full space-y-4">
                        {message.dual_response ? (
                          // Dual Response (Professor + Mentor)
                          <div className="space-y-4">
                            {/* Professor Response */}
                            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-2xl p-6 shadow-lg">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                  <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                  <span className="font-semibold text-gray-900 dark:text-white">Professor</span>
                                </div>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="h-3 w-3 mr-1" />
                                  <span>{formatTime(message.timestamp)}</span>
                                </div>
                              </div>
                              <SemanticAIResponse 
                                content={message.dual_response.primary?.raw_text || message.dual_response.primary?.response}
                                type="professor"
                              />
                            </div>
                            
                            {/* Mentor Response */}
                            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900 dark:to-pink-900 rounded-2xl p-6 shadow-lg">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                  <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                  <span className="font-semibold text-gray-900 dark:text-white">Mentor</span>
                                </div>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="h-3 w-3 mr-1" />
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
                          // Single Response (Mentor or Professor only)
                          <div className={`rounded-2xl p-6 shadow-lg ${
                            message.persona === 'professor' 
                              ? 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900'
                              : 'bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900 dark:to-pink-900'
                          }`}>
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center space-x-2">
                                {message.persona === 'professor' ? (
                                  <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                ) : (
                                  <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                )}
                                <span className="font-semibold text-gray-900 dark:text-white">
                                  {message.persona === 'professor' ? 'Professor' : 'Mentor'}
                                </span>
                              </div>
                              <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                <Clock className="h-3 w-3 mr-1" />
                                <span>{formatTime(message.timestamp)}</span>
                              </div>
                            </div>
                            <div className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
                              {message.response}
                            </div>
                          </div>
                        )}
                        
                        {/* Feedback & Follow-up Buttons */}
                        <div className="flex items-center justify-between px-2">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleFeedback(message.message_id, 'positive')}
                              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                              title="Helpful"
                            >
                              <ThumbsUp className="h-4 w-4 text-gray-400 group-hover:text-green-500" />
                            </button>
                            <button
                              onClick={() => handleFeedback(message.message_id, 'negative')}
                              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                              title="Not helpful"
                            >
                              <ThumbsDown className="h-4 w-4 text-gray-400 group-hover:text-red-500" />
                            </button>
                          </div>
                          <button
                            onClick={() => handleFollowUp('Can you explain this in more detail?')}
                            className="px-3 py-1.5 text-xs font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900 rounded-lg transition-colors"
                          >
                            Ask Follow-up
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : message.user_message ? (
                    // COMPLETE message with user_message AND AI response (OLD format)
                    <React.Fragment>
                      {/* User Message */}
                      <div className="flex justify-end mb-6">
                        <div className="max-w-2xl bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-br-md p-4 shadow-lg">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.user_message}</p>
                          <div className="flex items-center justify-end mt-2 text-xs text-blue-100 opacity-75">
                            <Clock className="h-3 w-3 mr-1" />
                            <span>{formatTime(message.timestamp)}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* AI Response - Uses SemanticAIResponse for structured rendering */}
                      <div className="flex justify-start">
                        <div className="max-w-4xl w-full space-y-4">
                          {message.dual_response ? (
                            // Dual Response (Professor + Mentor) - RESTORED OLD FORMAT
                            <div className="space-y-4">
                              {/* Professor Response */}
                              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-2xl p-6 shadow-lg">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center space-x-2">
                                    <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                    <span className="font-semibold text-gray-900 dark:text-white">Professor</span>
                                  </div>
                                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <Clock className="h-3 w-3 mr-1" />
                                    <span>{formatTime(message.timestamp)}</span>
                                  </div>
                                </div>
                                <SemanticAIResponse 
                                  content={message.dual_response.primary?.raw_text || message.dual_response.primary?.response}
                                  type="professor"
                                />
                              </div>
                              
                              {/* Mentor Response */}
                              <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900 dark:to-pink-900 rounded-2xl p-6 shadow-lg">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center space-x-2">
                                    <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                    <span className="font-semibold text-gray-900 dark:text-white">Mentor</span>
                                  </div>
                                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <Clock className="h-3 w-3 mr-1" />
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
                            // Single Response (Mentor or Professor only)
                            <div className={`rounded-2xl p-6 shadow-lg ${
                              message.persona === 'professor' 
                                ? 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900'
                                : 'bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900 dark:to-pink-900'
                            }`}>
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                  {message.persona === 'professor' ? (
                                    <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                  ) : (
                                    <Heart className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                  )}
                                  <span className="font-semibold text-gray-900 dark:text-white">
                                    {message.persona === 'professor' ? 'Professor' : 'Mentor'}
                                  </span>
                                </div>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="h-3 w-3 mr-1" />
                                  <span>{formatTime(message.timestamp)}</span>
                                </div>
                              </div>
                              <div className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
                                {message.response}
                              </div>
                            </div>
                          )}
                          
                          {/* Feedback & Follow-up Buttons */}
                          <div className="flex items-center justify-between px-2">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => handleFeedback(message.message_id, 'positive')}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                                title="Helpful"
                              >
                                <ThumbsUp className="h-4 w-4 text-gray-400 group-hover:text-green-500" />
                              </button>
                              <button
                                onClick={() => handleFeedback(message.message_id, 'negative')}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                                title="Not helpful"
                              >
                                <ThumbsDown className="h-4 w-4 text-gray-400 group-hover:text-red-500" />
                              </button>
                            </div>
                            <button
                              onClick={() => handleFollowUp('Can you explain this in more detail?')}
                              className="px-3 py-1.5 text-xs font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900 rounded-lg transition-colors"
                            >
                              Ask Follow-up
                            </button>
                          </div>
                        </div>
                      </div>
                    </React.Fragment>
                  ) : null}
                </motion.div>
              ))
            )}
          </AnimatePresence>
          
          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3">
                  <Loader className="h-5 w-5 text-purple-600 animate-spin" />
                  <span className="text-sm text-gray-600 dark:text-gray-300">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Area - Auto-resize */}
        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Ask me anything..."
                  className="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  style={{ minHeight: '56px', maxHeight: '200px' }}
                  rows={1}
                  disabled={loading}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || loading}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Send className="h-5 w-5" />
                <span className="font-semibold">Send</span>
              </button>
            </div>
            
            {/* Subject & Mode Selectors */}
            <div className="mt-3 flex items-center flex-wrap gap-3">
              <div className="flex items-center space-x-2">
                <BookOpen className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="Mathematics">Mathematics</option>
                  <option value="Physics">Physics</option>
                  <option value="Chemistry">Chemistry</option>
                  <option value="Biology">Biology</option>
                  <option value="General">General</option>
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
                >
                  Mentor
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
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
