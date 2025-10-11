import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
// Upsell modal is rendered globally in App.js via SubscriptionContext
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import FormattedAIResponse, { DualResponseContainer, formatMathExpressions, formatVisualResponse, formatProfessorMentorResponse } from './FormattedAIResponse';
import { handleSubscriptionError, handlePostUpgradeRetry, animateSubscriptionUnlock } from '../utils/subscriptionErrorHandler';
import AITutor20 from './AITutor20';
import { 
  Brain, 
  Send, 
  MessageCircle, 
  BookOpen, 
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  Clock,
  Zap,
  GraduationCap,
  Heart,
  Users,
  Shield,
  Target,
  Sparkles,
  FileText,
  Star,
  Mic,
  MicOff,
  Upload,
  ImageIcon,
  FileIcon,
  X,
  Pin,
  Link,
  History,
  Plus,
  TrendingDown,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Edit,
  MoreVertical,
  Trash2,
  Crown,
  Menu,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AITutor() {
  const { user } = useAuth();
  const { 
    subscriptionInfo, 
    dailyUsage, 
    checkFeatureAccess, 
    trackFeatureUsage,
    fetchSubscriptionInfo,
    upsellModal,
    setUpsellModal,
    currentTier,
    getFeatureUsage,
    getFeatureLimit,
    getFeatureRemaining,
    isFeatureUnlimited,
    triggerFeatureUpsell
  } = useSubscription();
  
  // Feature toggle state for AI Tutor 2.0
  const [useAITutor20, setUseAITutor20] = useState(false);
  
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('Mathematics');
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [aiMode, setAiMode] = useState('dual'); // 'dual', 'mentor', 'professor'
  const [lastScenarioType, setLastScenarioType] = useState('');
  const messagesEndRef = useRef(null);
  
  // Phase 3: Enhanced functionality states
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [showSessionSearch, setShowSessionSearch] = useState(false);
  const [bookmarkedResponses, setBookmarkedResponses] = useState([]);
  const [showQuickSuggestions, setShowQuickSuggestions] = useState(false);
  const [sessionActions, setSessionActions] = useState({
    showMenu: null, // session_id of the session showing action menu
    isRenaming: null // session_id of the session being renamed
  });
  const [renameValue, setRenameValue] = useState('');
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const [lastFailedAction, setLastFailedAction] = useState(null);
  
  // ============= ENGAGEMENT & GAMIFICATION STATES =============
  const [streakInfo, setStreakInfo] = useState({ current_streak: 0, longest_streak: 0 });
  const [xpInfo, setXPInfo] = useState({ total_xp: 0, current_level: 1, progress_percentage: 0 });
  const [showXPPopup, setShowXPPopup] = useState(false);
  const [lastXPGain, setLastXPGain] = useState(null);
  const [verificationBadge, setVerificationBadge] = useState("✓ 100% Hallucination-Free AI");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceAnimation, setVoiceAnimation] = useState(false);
  const [modeTransition, setModeTransition] = useState(false);

  // Phase A: Complete Input Methods states
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [showContextPin, setShowContextPin] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [contextPinData, setContextPinData] = useState([]);
  const [selectedContext, setSelectedContext] = useState(null);
  const [availableContexts, setAvailableContexts] = useState([]);
  const fileInputRef = useRef(null);

  // Phase B: Personalization states
  const [studentProfile, setStudentProfile] = useState(null);
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [topicMastery, setTopicMastery] = useState({});
  const [errorPatterns, setErrorPatterns] = useState([]);
  const [lastFeedback, setLastFeedback] = useState(null);
  const [personalizedDifficulty, setPersonalizedDifficulty] = useState(0.5);
  const [feedbackSentiment, setFeedbackSentiment] = useState('neutral');
  
  // Phase E: Wellness Integration State
  const [showWellnessCheck, setShowWellnessCheck] = useState(false);
  const [wellnessData, setWellnessData] = useState({
    stress_level: 5,
    motivation_level: 7,
    confidence_level: 6,
    study_satisfaction: 7
  });

  const subjects = {
    'JEE': ['Mathematics', 'Physics', 'Chemistry'],
    'NEET': ['Physics', 'Chemistry', 'Biology'],
    'UPSC': ['General Studies', 'Current Affairs', 'History', 'Geography', 'Polity']
  };

  useEffect(() => {
    fetchChatSessions();
    loadPersonalizationData();
    initializeSpeechRecognition();
    fetchEngagementData();
  }, []);

  useEffect(() => {
    // Filter sessions based on search query
    if (searchQuery.trim()) {
      const filtered = sessions.filter(session => 
        session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.subject.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSessions(filtered);
    } else {
      setFilteredSessions(sessions);
    }
  }, [searchQuery, sessions]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Close session action menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sessionActions.showMenu && !event.target.closest('.session-action-menu')) {
        setSessionActions({ ...sessionActions, showMenu: null });
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sessionActions.showMenu]);
  
  // If AI Tutor 2.0 is enabled, render the new component
  if (useAITutor20) {
    return (
      <AITutor20 
        onBackToV1={() => setUseAITutor20(false)}
        className="h-full"
      />
    );
  }
  
  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'success' });
    }, 3000);
  };

  // ============= ENGAGEMENT & GAMIFICATION STATES =============
  const [streakInfo, setStreakInfo] = useState({ current_streak: 0, longest_streak: 0 });
  const [xpInfo, setXPInfo] = useState({ total_xp: 0, current_level: 1, progress_percentage: 0 });
  const [showXPPopup, setShowXPPopup] = useState(false);
  const [lastXPGain, setLastXPGain] = useState(null);
  const [verificationBadge, setVerificationBadge] = useState("✓ 100% Hallucination-Free AI");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceAnimation, setVoiceAnimation] = useState(false);
  const [modeTransition, setModeTransition] = useState(false);

  // Phase A: Complete Input Methods states
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [showContextPin, setShowContextPin] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [contextPinData, setContextPinData] = useState([]);
  const [selectedContext, setSelectedContext] = useState(null);
  const [availableContexts, setAvailableContexts] = useState([]);
  const fileInputRef = useRef(null);

  // Phase B: Personalization states
  const [studentProfile, setStudentProfile] = useState(null);
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [topicMastery, setTopicMastery] = useState({});
  const [errorPatterns, setErrorPatterns] = useState([]);
  const [lastFeedback, setLastFeedback] = useState(null);
  const [personalizedDifficulty, setPersonalizedDifficulty] = useState(0.5);
  const [feedbackSentiment, setFeedbackSentiment] = useState('neutral');
  
  // Phase E: Wellness Integration State
  const [showWellnessCheck, setShowWellnessCheck] = useState(false);
  const [wellnessData, setWellnessData] = useState({
    stress_level: 5,
    motivation_level: 7,
    confidence_level: 6,
    study_satisfaction: 7
  });

  const subjects = {
    'JEE': ['Mathematics', 'Physics', 'Chemistry'],
    'NEET': ['Physics', 'Chemistry', 'Biology'],
    'UPSC': ['General Studies', 'Current Affairs', 'History', 'Geography', 'Polity']
  };

  useEffect(() => {
    fetchChatSessions();
    loadPersonalizationData();
    initializeSpeechRecognition();
    fetchEngagementData();
  }, []);

  useEffect(() => {
    // Filter sessions based on search query
    if (searchQuery.trim()) {
      const filtered = sessions.filter(session => 
        session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.subject.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSessions(filtered);
    } else {
      setFilteredSessions(sessions);
    }
  }, [searchQuery, sessions]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Close session action menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sessionActions.showMenu && !event.target.closest('.session-action-menu')) {
        setSessionActions({ ...sessionActions, showMenu: null });
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sessionActions.showMenu]);

  // Phase 3: Keyboard shortcuts
  useEffect(() => {
    const handleKeyboardShortcuts = (e) => {
      // Ctrl/Cmd + / to toggle quick suggestions
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        setShowQuickSuggestions(!showQuickSuggestions);
      }
      
      // Ctrl/Cmd + E to export conversation
      if ((e.ctrlKey || e.metaKey) && e.key === 'e' && messages.length > 0) {
        e.preventDefault();
        exportConversation();
      }
      
      // Ctrl/Cmd + N for new chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        startNewSession();
      }
    };

    document.addEventListener('keydown', handleKeyboardShortcuts);
    return () => document.removeEventListener('keydown', handleKeyboardShortcuts);
  }, [showQuickSuggestions, messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Phase 3: Speech Recognition Setup
  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
      };
      
      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setCurrentMessage(transcript);
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
    }
  };

  const startVoiceInput = () => {
    if (recognition) {
      recognition.start();
    }
  };

  const stopVoiceInput = () => {
    if (recognition) {
      recognition.stop();
    }
  };

  const fetchChatSessions = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await axios.get(`${API}/chat/sessions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch chat sessions:', error);
      setSessions([]);
    }
  };

  // Create new session in backend
  const createNewSession = async (firstMessage, detectedTopic) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return null;

      // Determine the subject from detected topic or use 'General'
      const topicSubject = detectedTopic && detectedTopic !== 'General' ? detectedTopic : 'General';
      
      // Create meaningful session title based on topic and message content
      let sessionTitle;
      if (detectedTopic && detectedTopic !== 'General') {
        // Use topic with a short excerpt from the message
        const messageExcerpt = firstMessage.substring(0, 30).trim();
        sessionTitle = `${detectedTopic}: ${messageExcerpt}${messageExcerpt.length < 30 ? '' : '...'}`;
      } else {
        // Use just the message excerpt for General topics
        sessionTitle = firstMessage.substring(0, 50).trim() + (firstMessage.length > 50 ? '...' : '');
      }
      
      const response = await axios.post(`${API}/chat/sessions`, {
        title: sessionTitle,
        subject: topicSubject, // Use detected topic as subject, not dropdown value
        topic: detectedTopic || 'General',
        ai_mode: aiMode
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      return response.data.session_id;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  };

  // Update session title if topic is detected
  const updateSessionTitleIfNeeded = async (sessionId, detectedTopic, firstMessage) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token || !detectedTopic || detectedTopic === 'General') return;

      // Create a more specific title based on detected topic
      const messageExcerpt = firstMessage.substring(0, 30).trim();
      const newTitle = `${detectedTopic}: ${messageExcerpt}${messageExcerpt.length < 30 ? '' : '...'}`;

      await axios.put(`${API}/chat/${sessionId}/rename`, {
        title: newTitle
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Failed to update session title:', error);
    }
  };

  // Save message to session - extract clean text only
  const saveMessageToSession = async (sessionId, message, aiResponse) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      // Extract clean response text for storage
      let cleanResponse = '';
      if (aiResponse && typeof aiResponse === 'object') {
        // Extract primary response from dual_response structure
        if (aiResponse.dual_response && aiResponse.dual_response.primary) {
          cleanResponse = aiResponse.dual_response.primary.response || '';
        }
        // Fallback to other response structures
        else if (aiResponse.response) {
          cleanResponse = aiResponse.response;
        }
        // If no clean text found, store the whole object (fallback)
        else {
          cleanResponse = aiResponse;
        }
      } else {
        cleanResponse = aiResponse;
      }

      await axios.post(`${API}/chat/${sessionId}/messages`, {
        user_message: message,
        ai_response: cleanResponse,
        timestamp: new Date().toISOString()
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Failed to save message:', error);
    }
  };

  const loadPersonalizationData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      const response = await axios.get(`${API}/personalization/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data) {
        setStudentProfile(response.data.profile);
        setTopicMastery(response.data.topic_mastery || {});
        setErrorPatterns(response.data.error_patterns || []);
        setPersonalizedDifficulty(response.data.difficulty_level || 0.5);
      }
    } catch (error) {
      console.error('Failed to load personalization data:', error);
    }
  };

  // ============= ENGAGEMENT & GAMIFICATION FUNCTIONS =============
  
  const fetchEngagementData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      const response = await axios.get(`${API}/engagement/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data) {
        setStreakInfo(response.data.streak);
        setXPInfo(response.data.xp);
        setVerificationBadge(response.data.badge_status);
      }
    } catch (error) {
      console.error('Failed to fetch engagement data:', error);
    }
  };

  const handleXPGain = (xpResult) => {
    if (xpResult && xpResult.xp_awarded > 0) {
      setLastXPGain(xpResult);
      setShowXPPopup(true);
      
      // Update XP info
      setXPInfo(prev => ({
        ...prev,
        total_xp: xpResult.total_xp,
        current_level: xpResult.level,
        progress_percentage: ((xpResult.total_xp - getXPForLevel(xpResult.level)) / 
          (getXPForLevel(xpResult.level + 1) - getXPForLevel(xpResult.level))) * 100
      }));
      
      // Auto-hide popup after animation
      setTimeout(() => setShowXPPopup(false), 3000);
      
      // Trigger celebration if level up
      if (xpResult.level_up) {
        showToast(`🎉 Level Up! You're now Level ${xpResult.level}!`, 'success');
      }
      
      if (xpResult.milestone_achieved) {
        showToast(`🏆 Milestone: ${xpResult.milestone_achieved}`, 'success');
      }
    }
  };

  const getXPForLevel = (level) => {
    if (level <= 1) return 0;
    return (level - 1) ** 2 * 100;
  };

  const enhancedStartVoiceInput = async () => {
    setIsRecording(true);
    setVoiceAnimation(true);
    
    if (recognition) {
      recognition.start();
    }
  };

  const enhancedStopVoiceInput = async () => {
    setIsRecording(false);
    setVoiceAnimation(false);
    
    if (recognition) {
      recognition.stop();
    }
  };
  // Enhanced AI Mode Transition with Animation
  const handleAiModeTransition = async (newMode) => {
    if (newMode === aiMode) return; // No change needed
    
    // Start transition animation
    setModeTransition(true);
    
    // Brief delay for visual feedback
    setTimeout(() => {
      setAiMode(newMode);
      
      // Show mode change notification
      const modeNames = {
        'mentor': '💙 Mentor Mode',
        'professor': '🎓 Professor Mode', 
        'dual': '👥 Dual Mode'
      };
      showToast(`Switched to ${modeNames[newMode]}`, 'success');
      
      // End transition animation
      setTimeout(() => {
        setModeTransition(false);
      }, 300);
    }, 150);
  };

  // Helper function to parse and clean message response
  const parseMessageResponse = (message) => {
    try {
      // If the response is a string that looks like JSON, try to parse it
      if (typeof message.response === 'string' && message.response.startsWith('{')) {
        const parsedResponse = JSON.parse(message.response);
        
        // If it's a parsed object with dual_response structure, use it
        if (parsedResponse.dual_response && parsedResponse.dual_response.primary) {
          return {
            ...message,
            dual_response: parsedResponse.dual_response,
            guardrails: parsedResponse.guardrails,
            action_buttons: parsedResponse.action_buttons,
            analytics: parsedResponse.analytics,
            disagreement_alert: parsedResponse.disagreement_alert,
            response: parsedResponse.dual_response.primary.response // Clean text for fallback
          };
        }
        // If it has a simple response field, use that
        else if (parsedResponse.response) {
          return {
            ...message,
            response: parsedResponse.response
          };
        }
      }
      
      // If response is already clean text or not JSON, return as is
      return message;
    } catch (error) {
      // If parsing fails, return the original message
      console.warn('Failed to parse message response:', error);
      return message;
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        console.error('No auth token found');
        return;
      }

      const response = await axios.get(`${API}/chat/${sessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Parse and clean all loaded messages
      const cleanedMessages = response.data.messages.map(parseMessageResponse);
      
      setMessages(cleanedMessages);
      setCurrentSession(sessionId);
      
      // Show success message
      showToast('Chat session loaded', 'success');
    } catch (error) {
      console.error('Failed to load session:', error);
      showToast('Failed to load chat session. Please try again.', 'error');
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    // Note: We still check access but the backend will also check
    // This prevents most cases but backend is the final authority
    // Use unified global trigger to ensure consistent modal hydration
    const wasTriggered = await triggerFeatureUpsell('ai_tutor_daily');
    if (wasTriggered) {
      // Modal shown – stop flow here
      return;
    }

    setLoading(true);
    const messageToSend = currentMessage;
    setCurrentMessage('');

    try {
      let response;
      let sessionId = currentSession;
      
      // Create new session if this is the first message or if no current session exists
      if (!sessionId) {
        // Detect topic from message (simple approach)
        const detectedTopic = detectTopicFromMessage(messageToSend);
        
        // Always create a new session when starting a new conversation
        // This ensures proper session isolation
        sessionId = await createNewSession(messageToSend, detectedTopic);
        if (sessionId) {
          setCurrentSession(sessionId);
        } else {
          // Fallback to local session ID if backend fails
          sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          setCurrentSession(sessionId);
        }
      }
      
      // Choose API endpoint based on AI mode
      const token = localStorage.getItem('dhruv_ai_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      if (aiMode === 'dual') {
        response = await axios.post(`${API}/ai/dual-response`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        }, { headers });
      } else if (aiMode === 'mentor') {
        response = await axios.post(`${API}/ai/mentor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        }, { headers });
      } else { // professor
        response = await axios.post(`${API}/ai/professor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        }, { headers });
      }

      // If any endpoint returned 402/429 via axios intercepts (unlikely here), ensure modal opens
      if (response?.status === 402 || response?.status === 429) {
        setUpsellModal({ featureName: 'ai_tutor_daily', upsellInfo: response.data?.detail?.upsell_info || {}, currentUsage: 0, limit: 0 });
        return;
      }

      const newMessage = response.data;
      
      // Update session title if AI detected a more specific topic
      if (newMessage.topic_detected && newMessage.topic_detected !== 'General') {
        await updateSessionTitleIfNeeded(sessionId, newMessage.topic_detected, messageToSend);
      }
      
      // Save message to backend session
      await saveMessageToSession(sessionId, messageToSend, newMessage);
      
      // Refresh sessions list to show updated chat
      fetchChatSessions();

      // Track scenario type for dual mode
      if (aiMode === 'dual' && newMessage.dual_response?.scenario_type) {
        setLastScenarioType(newMessage.dual_response.scenario_type);
      }

      // Add personalization info to the message
      const enhancedMessage = {
        ...newMessage,
        user_message: messageToSend,
        personalized: newMessage.dual_response?.personalized || false,
        difficulty_level: newMessage.dual_response?.user_difficulty_level || personalizedDifficulty,
        topic_detected: newMessage.topic_detected || 'General',
        timestamp: new Date().toISOString()
      };

      // Add message to current conversation
      setMessages(prev => [...prev, enhancedMessage]);
      
      // Update personalized difficulty if provided
      if (newMessage.dual_response?.user_difficulty_level) {
        setPersonalizedDifficulty(newMessage.dual_response.user_difficulty_level);
      }

      // Handle engagement results (XP, streak, etc.)
      if (newMessage.engagement) {
        if (newMessage.engagement.xp_awarded) {
          handleXPGain(newMessage.engagement.xp_awarded);
        }
        if (newMessage.engagement.streak_updated) {
          fetchEngagementData(); // Refresh engagement data
        }
      }

      // Track feature usage for subscription system and refresh usage count
      await trackFeatureUsage('ai_tutor_daily');
      
      // Force refresh subscription info to update usage counter display
      setTimeout(() => {
        fetchSubscriptionInfo();
      }, 500);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Check if this is a subscription-related error first
      if (error.response?.status === 402 || error.response?.status === 429) {
        console.log('Subscription limit reached in catch block - triggering global modal');
        
        // Store failed action for retry after upgrade
        const failedAction = () => {
          setCurrentMessage(messageToSend);
          setTimeout(() => sendMessage(), 100);
        };
        setLastFailedAction(failedAction);
        
        // Trigger the shared upsell flow so UI/data is consistent
        await triggerFeatureUpsell('ai_tutor_daily');
        return; // Don't add error messages to chat
      }
      
      // For server errors, add user-friendly message but prevent duplicates
      if (error.response?.status >= 500) {
        // Check if we already have recent error messages to prevent spam
        const recentErrors = messages.filter(msg => 
          msg.type === 'system_error' && 
          new Date() - new Date(msg.timestamp) < 5000 // 5 seconds
        );
        
        if (recentErrors.length === 0) {
          const errorMessage = {
            type: 'system_error',
            message: "I'm temporarily having trouble processing your message. Please try again in a moment, or contact support if the issue persists.",
            timestamp: new Date().toISOString()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        
        // Don't put message back for server errors
        showToast('Server temporarily unavailable. Please try again.', 'error');
      } else {
        // For other errors (network, etc.), put message back in input
        setCurrentMessage(messageToSend);
        showToast('Failed to send message. Please check your connection.', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  // Enhanced topic detection with more sophisticated keywords
  const detectTopicFromMessage = (message) => {
    const lowerMessage = message.toLowerCase();
    
    // Advanced keyword mapping with weights and context
    const topicKeywords = {
      'Mathematics': {
        primary: ['algebra', 'calculus', 'geometry', 'trigonometry', 'statistics', 'probability', 'matrix', 'vector'],
        secondary: ['derivative', 'integral', 'limit', 'equation', 'solve', 'calculate', 'function', 'graph', 'polynomial', 'quadratic', 'logarithm', 'exponential'],
        symbols: ['x²', '∫', '∑', 'π', 'θ', '√', 'sin', 'cos', 'tan', 'log']
      },
      'Physics': {
        primary: ['mechanics', 'thermodynamics', 'optics', 'electromagnetism', 'quantum', 'relativity'],
        secondary: ['force', 'energy', 'momentum', 'wave', 'electric', 'magnetic', 'velocity', 'acceleration', 'mass', 'gravity', 'pressure', 'temperature'],
        symbols: ['newton', 'joule', 'watt', 'volt', 'ampere', 'ohm', 'f=ma', 'v=u+at']
      },
      'Chemistry': {
        primary: ['organic', 'inorganic', 'physical chemistry', 'biochemistry', 'analytical'],
        secondary: ['molecule', 'reaction', 'bond', 'element', 'compound', 'acid', 'base', 'ph', 'oxidation', 'reduction', 'catalyst', 'equilibrium'],
        symbols: ['h2o', 'co2', 'nacl', 'ch4', 'h+', 'oh-']
      },
      'Biology': {
        primary: ['genetics', 'ecology', 'evolution', 'anatomy', 'physiology', 'botany', 'zoology'],
        secondary: ['cell', 'dna', 'rna', 'protein', 'enzyme', 'photosynthesis', 'respiration', 'mitosis', 'meiosis'],
        symbols: ['atp', 'dna', 'rna', 'co2', 'o2']
      }
    };
    
    let topicScores = {};
    
    // Calculate scores for each topic
    Object.keys(topicKeywords).forEach(topic => {
      let score = 0;
      const keywords = topicKeywords[topic];
      
      // Primary keywords (high weight)
      keywords.primary.forEach(keyword => {
        if (lowerMessage.includes(keyword)) score += 3;
      });
      
      // Secondary keywords (medium weight)
      keywords.secondary.forEach(keyword => {
        if (lowerMessage.includes(keyword)) score += 2;
      });
      
      // Symbols and formulas (medium weight)
      keywords.symbols.forEach(symbol => {
        if (lowerMessage.includes(symbol)) score += 2;
      });
      
      topicScores[topic] = score;
    });
    
    // Find the topic with highest score
    const maxScore = Math.max(...Object.values(topicScores));
    const detectedTopic = Object.keys(topicScores).find(topic => topicScores[topic] === maxScore);
    
    // Return detected topic if score is significant, otherwise return General
    return maxScore >= 2 ? detectedTopic : 'General';
  };

  // Session isolation: Always create new session for new conversations
  // This ensures messages don't get mixed between different chat sessions

  const startNewSession = () => {
    setMessages([]);
    setCurrentSession(null);
    setSessionActions({ showMenu: null, isRenaming: null });
  };

  // Session Management Actions
  const renameSession = async (sessionId, newTitle) => {
    if (!newTitle.trim()) {
      showToast('Session name cannot be empty', 'error');
      return;
    }

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      await axios.put(`${API}/chat/${sessionId}/rename`, {
        title: newTitle.trim()
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      // Update sessions list immediately
      setSessions(prevSessions => 
        prevSessions.map(session => 
          session.session_id === sessionId 
            ? { ...session, title: newTitle.trim() }
            : session
        )
      );

      setSessionActions({ showMenu: null, isRenaming: null });
      setRenameValue('');
      showToast('Session renamed successfully', 'success');
    } catch (error) {
      console.error('Failed to rename session:', error);
      showToast('Failed to rename session', 'error');
    }
  };

  const deleteSession = async (sessionId) => {
    const session = sessions.find(s => s.session_id === sessionId);
    const sessionTitle = session ? session.title : 'this conversation';

    const confirmed = window.confirm(`Are you sure you want to delete "${sessionTitle}"? This action cannot be undone.`);
    if (!confirmed) return;

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      await axios.delete(`${API}/chat/${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      // If this was the current session, clear it
      if (currentSession === sessionId) {
        setMessages([]);
        setCurrentSession(null);
      }

      // Update sessions list immediately
      setSessions(prevSessions => 
        prevSessions.filter(session => session.session_id !== sessionId)
      );

      setSessionActions({ showMenu: null, isRenaming: null });
      showToast(`"${sessionTitle}" deleted successfully`, 'success');
    } catch (error) {
      console.error('Failed to delete session:', error);
      showToast('Failed to delete session', 'error');
    }
  };

  const togglePinSession = async (sessionId, isPinned) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const newPinnedState = !isPinned;

      await axios.put(`${API}/chat/${sessionId}/pin`, {
        pinned: newPinnedState
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      // Update sessions list immediately
      setSessions(prevSessions => 
        prevSessions.map(session => 
          session.session_id === sessionId 
            ? { ...session, pinned: newPinnedState }
            : session
        )
      );

      setSessionActions({ showMenu: null, isRenaming: null });
      const action = newPinnedState ? 'pinned to top' : 'unpinned';
      showToast(`Session ${action}`, 'success');
    } catch (error) {
      console.error('Failed to pin/unpin session:', error);
      showToast('Failed to update session', 'error');
    }
  };

  const toggleBookmarkSession = async (sessionId, isBookmarked) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const newBookmarkedState = !isBookmarked;

      await axios.put(`${API}/chat/${sessionId}/bookmark`, {
        bookmarked: newBookmarkedState
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      // Update sessions list immediately
      setSessions(prevSessions => 
        prevSessions.map(session => 
          session.session_id === sessionId 
            ? { ...session, bookmarked: newBookmarkedState }
            : session
        )
      );

      setSessionActions({ showMenu: null, isRenaming: null });
      const action = newBookmarkedState ? 'bookmarked' : 'removed from bookmarks';
      showToast(`Session ${action}`, 'success');
    } catch (error) {
      console.error('Failed to bookmark/unbookmark session:', error);
      showToast('Failed to update bookmark', 'error');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Phase 3: Enhanced functionality methods
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Could add a toast notification here
  };

  const bookmarkResponse = (messageIndex) => {
    const response = messages[messageIndex];
    setBookmarkedResponses(prev => [...prev, { ...response, bookmarkedAt: new Date() }]);
  };

  // Phase D: Enhanced Action Button Handlers
  const handlePracticeMore = async (originalQuestion, subject, topic) => {
    try {
      showToast('🎯 Generating similar problems...', 'info');
      
      // Generate similar practice problems
      const response = await axios.post(`${API}/actions/practice-more`, {
        original_question: originalQuestion,
        subject: subject || selectedSubject,
        topic: topic || 'General',
        difficulty_level: 'medium' // You could make this dynamic based on user level
      });
      
      console.log('Practice problems generated:', response.data);
      
      // Add the practice problems as a new message in the chat
      if (response.data && response.data.practice_problems) {
        const practiceMessage = {
          message: `Here are some similar practice problems for you:`,
          response: response.data.practice_problems.join('\n\n'),
          timestamp: new Date().toISOString(),
          persona: 'mentor',
          is_practice: true
        };
        setMessages(prev => [...prev, practiceMessage]);
        showToast('✅ Practice problems ready!', 'success');
      }
      
    } catch (error) {
      console.error('Failed to generate practice problems:', error);
      showToast('❌ Failed to generate problems. Try again later.', 'error');
    }
  };

  const handleAddToNotes = async (title, content, subject, topic, interactionId) => {
    try {
      const response = await axios.post(`${API}/actions/add-to-notes`, {
        title: title || `${subject} Notes - ${new Date().toLocaleDateString()}`,
        content: content,
        subject: subject || selectedSubject,
        topic: topic || 'General',
        interaction_id: interactionId
      });
      
      // Show success feedback to student
      showToast('📝 Saved to your notes!', 'success');
      console.log('Note saved:', response.data);
      
    } catch (error) {
      console.error('Failed to save note:', error);
      showToast('❌ Failed to save note. Try again later.', 'error');
    }
  };

  const handleCreateFlashcards = async (title, content, subject, topic, interactionId) => {
    try {
      const response = await axios.post(`${API}/actions/create-flashcards`, {
        title: title || `${subject} Flashcards - ${topic}`,
        content: content,
        subject: subject || selectedSubject,
        topic: topic || 'General',
        interaction_id: interactionId
      });
      
      console.log('Flashcard deck created:', response.data);
      // You could show the flashcards in a modal or navigate to flashcard section
      
    } catch (error) {
      console.error('Failed to create flashcard deck:', error);
    }
  };

  const handleScheduleRevision = async (contentId, contentType, title, difficulty) => {
    try {
      const response = await axios.post(`${API}/actions/schedule-revision`, {
        content_id: contentId || `msg_${Date.now()}`,
        content_type: contentType || 'concept',
        title: title || 'AI Tutor Concept',
        difficulty_level: difficulty || 0.5
      });
      
      console.log('Revision scheduled:', response.data);
      // You could show the scheduled revision time
      
    } catch (error) {
      console.error('Failed to schedule revision:', error);
    }
  };

  // Phase E: Wellness Check Handler
  const handleWellnessCheck = async () => {
    try {
      const response = await axios.post(`${API}/analytics/wellness-check`, {
        ...wellnessData,
        session_id: currentSession || `session_${Date.now()}`
      });
      
      console.log('Wellness check completed:', response.data);
      
      // Show recommendations if any
      if (response.data.motivational_content_suggested) {
        // You could show this in a notification or modal
        console.log('Motivational content:', response.data.motivational_content_suggested);
      }
      
      if (response.data.break_recommendation) {
        // Suggest a break to the user
        console.log('Break recommended based on wellness check');
      }
      
      setShowWellnessCheck(false);
      
    } catch (error) {
      console.error('Failed to conduct wellness check:', error);
    }
  };

  // Phase E: Trigger Wellness Check Periodically
  useEffect(() => {
    const checkWellnessInterval = setInterval(() => {
      // Show wellness check every 30 minutes of active usage
      if (messages.length > 0 && messages.length % 10 === 0) { // Every 10 interactions
        setShowWellnessCheck(true);
      }
    }, 30 * 60 * 1000); // 30 minutes

    return () => clearInterval(checkWellnessInterval);
  }, [messages.length]);

  const exportConversation = () => {
    const conversationText = messages.map(msg => {
      if (msg.dual_response) {
        return `User: ${msg.message}\n\nProfessor: ${msg.dual_response.primary.response}\n\nMentor: ${msg.dual_response.secondary.reasoning}\n\n---\n\n`;
      } else {
        return `User: ${msg.message}\n\nAI: ${msg.response}\n\n---\n\n`;
      }
    }).join('');
    
    const blob = new Blob([conversationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dhruv-ai-conversation-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Phase A: Advanced File Upload Functionality with Cutting-Edge Technology
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      processSelectedFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      processSelectedFile(file);
    }
  };

  const processSelectedFile = (file) => {
    console.log('📁 File selected:', file.name, file.type, file.size, 'bytes');
    
    // Enhanced validation with more specific error messages
    const supportedTypes = {
      'image/jpeg': 'JPEG Image',
      'image/jpg': 'JPG Image', 
      'image/png': 'PNG Image',
      'image/webp': 'WebP Image',
      'application/pdf': 'PDF Document'
    };

    if (!supportedTypes[file.type]) {
      alert(`❌ Unsupported file type: ${file.type}\n\n✅ Supported formats:\n• JPEG/JPG Images\n• PNG Images\n• WebP Images\n• PDF Documents`);
      return;
    }

    // Check file size (25MB limit for better performance)
    const maxSize = 25 * 1024 * 1024; // 25MB
    if (file.size > maxSize) {
      alert(`❌ File too large: ${(file.size / 1024 / 1024).toFixed(2)} MB\n\n✅ Maximum allowed: 25MB`);
      return;
    }

    console.log('✅ File validation passed');
    setSelectedFile(file);
    
    // Auto-process immediately for better UX
    setTimeout(() => {
      processFileUpload(file);
    }, 500);
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const processFileUpload = async (fileToProcess = selectedFile) => {
    if (!fileToProcess) {
      console.error('❌ No file to process');
      return;
    }

    console.log('🚀 Starting file processing:', fileToProcess.name);
    setLoading(true);
    setUploadProgress(5);

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const formData = new FormData();
      formData.append('file', fileToProcess);
      formData.append('subject', selectedSubject);
      formData.append('ai_mode', aiMode);
      
      if (selectedContext) {
        formData.append('context_id', selectedContext.id);
        formData.append('context_type', selectedContext.type);
        console.log('🔗 Context attached:', selectedContext.title);
      }

      setUploadProgress(20);
      console.log('📤 Uploading file to AI analysis...');

      const response = await fetch(`${API}/ai/process-file`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      setUploadProgress(60);
      console.log('📡 Response received, status:', response.status);

      if (response.ok) {
        const result = await response.json();
        console.log('✅ AI analysis complete:', result);
        
        setUploadProgress(90);

        // Create a properly formatted message object for display
        const messageToAdd = {
          ...result,
          message: `📁 Analyzed file: ${fileToProcess.name}`,
          timestamp: new Date().toISOString(),
          file_processed: true,
          file_name: fileToProcess.name,
          file_type: fileToProcess.type
        };
        
        // Add the AI response to messages
        setMessages(prev => [...prev, messageToAdd]);
        
        // Update current session if it's a new one
        if (!currentSession && result.session_id) {
          setCurrentSession(result.session_id);
          fetchChatSessions();
        }

        // Clear the uploaded file
        clearSelectedFile();
        
        setUploadProgress(100);
        console.log('🎉 File processing completed successfully!');
        
      } else {
        const errorData = await response.json();
        const errorMessage = errorData.detail || 'Failed to process file';
        console.error('❌ Server error:', errorMessage);
        alert(`❌ Processing failed: ${errorMessage}`);
      }
      
    } catch (error) {
      console.error('❌ Upload error:', error);
      alert(`❌ Upload failed: ${error.message}\n\nPlease check your connection and try again.`);
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  // Phase A: Context Pin Functionality
  const loadAvailableContexts = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/ai/available-contexts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        const contexts = data.contexts.map(context => ({
          ...context,
          icon: context.type === 'chat_session' ? MessageCircle : 
               context.type === 'note_session' ? FileText : Target
        }));
        
        setAvailableContexts(contexts);
      } else {
        console.error('Failed to load contexts');
        setAvailableContexts([]);
      }
      
    } catch (error) {
      console.error('Error loading available contexts:', error);
      setAvailableContexts([]);
    }
  };

  const selectContext = (context) => {
    setSelectedContext(context);
    setShowContextPin(false);
  };

  const clearContext = () => {
    setSelectedContext(null);
  };

  // Phase B: Personalization Functions
  const updatePersonalizationProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/personalization/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        setStudentProfile(result.profile);
        console.log('✅ Profile updated successfully');
        return true;
      } else {
        console.error('Failed to update profile');
        return false;
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      return false;
    }
  };

  const submitUserFeedback = async (sessionId, feedbackType, topicName = null) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/personalization/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          subject: selectedSubject,
          feedback_type: feedbackType,
          topic_name: topicName
        })
      });

      if (response.ok) {
        setLastFeedback({ type: feedbackType, timestamp: Date.now() });
        // Reload personalization data to reflect updates
        loadPersonalizationData();
        console.log('✅ Feedback submitted successfully');
        return true;
      } else {
        console.error('Failed to submit feedback');
        return false;
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return false;
    }
  };
  const generatePracticeProblems = async (topicName) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/ai/practice-problems`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          topic: topicName,
          subject: selectedSubject,
          difficulty_level: personalizedDifficulty
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Add practice problems as a new message
        const practiceMessage = {
          message: `Generated practice problems for: ${topicName}`,
          response: result.problems,
          timestamp: new Date().toISOString(),
          session_id: currentSession,
          persona: 'professor'
        };
        setMessages(prev => [...prev, practiceMessage]);
        console.log('✅ Practice problems generated successfully');
        return true;
      } else {
        console.error('Failed to generate practice problems');
        return false;
      }
    } catch (error) {
      console.error('Error generating practice problems:', error);
      return false;
    }
  };

  const addToAutoNotes = async (message) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/notes/auto-add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: message.dual_response ? 
            `${message.dual_response.primary.response}\n\n${message.dual_response.secondary.reasoning}` : 
            message.response,
          topic: message.topic_detected || 'General',
          subject: selectedSubject,
          session_id: message.session_id
        })
      });

      if (response.ok) {
        console.log('✅ Added to auto notes successfully');
        // Could show a toast notification here
        return true;
      } else {
        console.error('Failed to add to auto notes');
        return false;
      }
    } catch (error) {
      console.error('Error adding to auto notes:', error);
      return false;
    }
  };

  const getDifficultyDisplay = (level) => {
    if (level < 0.3) return { label: 'Beginner', color: 'bg-green-500', emoji: '🌱' };
    if (level < 0.7) return { label: 'Intermediate', color: 'bg-yellow-500', emoji: '📚' };
    return { label: 'Advanced', color: 'bg-red-500', emoji: '🏆' };
  };

  const getMasteryColor = (mastery) => {
    if (mastery < 0.3) return 'text-red-500';
    if (mastery < 0.7) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getSubjectSuggestions = () => {
    const suggestions = {
      'Mathematics': [
        "Explain the concept of derivatives and their applications",
        "How do I solve complex integration problems?",
        "What are the key trigonometric identities I should memorize?",
        "Help me understand matrices and determinants",
        "Explain coordinate geometry concepts for JEE"
      ],
      'Physics': [
        "Explain Newton's laws with real-world examples",
        "How does electromagnetic induction work?",
        "What are the key concepts in thermodynamics?",
        "Help me understand wave optics and interference",
        "Explain quantum mechanics basics for competitive exams"
      ],
      'Chemistry': [
        "What are the important organic reaction mechanisms?",
        "Explain chemical bonding and molecular structures",
        "How do I balance complex chemical equations?",
        "What are the key concepts in electrochemistry?",
        "Help me understand thermodynamics in chemistry"
      ],
      'Biology': [
        "Explain the process of photosynthesis in detail",
        "What are the key concepts in genetics and heredity?",
        "How does the human circulatory system work?",
        "Explain cellular respiration and energy production",
        "What are the important topics in ecology?"
      ]
    };
    return suggestions[selectedSubject] || [];
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Group sessions by subject automatically, with pinned sessions at top
  // Maintain order from backend (already sorted by last_updated descending)
  const groupedSessions = React.useMemo(() => {
    const groups = {};
    
    // Separate pinned and regular sessions while preserving order
    const pinnedSessions = filteredSessions.filter(session => session.pinned);
    const regularSessions = filteredSessions.filter(session => !session.pinned);
    
    // Add pinned section if there are pinned sessions (maintain order)
    if (pinnedSessions.length > 0) {
      groups['📌 Pinned'] = pinnedSessions;
    }
    
    // Group regular sessions by intelligent subject detection
    regularSessions.forEach(session => {
      // Priority: Use topic if meaningful, fallback to subject, then General
      let displaySubject = 'General';
      
      if (session.topic && session.topic !== 'General' && session.topic.trim() !== '') {
        displaySubject = session.topic;
      } else if (session.subject && session.subject !== 'Mathematics' && session.subject.trim() !== '') {
        // Only use subject if it's not the default "Mathematics"
        displaySubject = session.subject;
      } else {
        // Extract subject from title if it starts with a subject name
        const titleSubject = session.title?.split(':')[0]?.trim();
        if (titleSubject && titleSubject.length < 30) {
          displaySubject = titleSubject;
        }
      }
      
      if (!groups[displaySubject]) {
        groups[displaySubject] = [];
      }
      groups[displaySubject].push(session);
    });
    
    // Sort each subject group by last_updated (latest first) to ensure proper ordering
    Object.keys(groups).forEach(subject => {
      if (subject !== '📌 Pinned') {
        groups[subject].sort((a, b) => {
          const dateA = new Date(a.last_updated || a.created_at);
          const dateB = new Date(b.last_updated || b.created_at);
          return dateB - dateA; // Descending order (latest first)
        });
      }
    });
    
    return groups;
  }, [filteredSessions]);

  return (
    <div className="flex h-screen bg-white">
      {/* Feature Toggle Header - AI Tutor 2.0 Beta */}
      <div className="fixed top-4 right-4 z-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-lg shadow-lg border border-purple-200 p-3"
        >
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-700">
              Try AI Tutor 2.0
            </span>
            <button
              onClick={() => setUseAITutor20(true)}
              className="flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-purple-600 text-white text-xs font-medium rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all duration-200"
            >
              <Sparkles className="w-3 h-3" />
              <span>Beta</span>
            </button>
          </div>
        </motion.div>
      </div>

      {/* Sidebar - Chat Sessions - Hidden on mobile */}
      <div className="hidden lg:flex w-80 bg-white border-r border-gray-100 flex-col">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Dhruv AI</h2>
            </div>
            <Button 
              size="sm" 
              onClick={startNewSession}
              className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200"
              variant="outline"
            >
              <Plus className="h-4 w-4 mr-1" />
              New
            </Button>
          </div>
          
          {/* Subject Selector */}
          <div className="relative mb-4">
            <Select value={selectedSubject} onValueChange={setSelectedSubject}>
              <SelectTrigger className="bg-gray-50 border-gray-200 text-gray-900">
                <BookOpen className="h-4 w-4 mr-2 text-blue-600" />
                <SelectValue placeholder="Select subject" />
              </SelectTrigger>
              <SelectContent>
                {subjects[user?.exam_type]?.map(subject => (
                  <SelectItem key={subject} value={subject}>
                    {subject}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Search */}
          <div className="relative">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="bg-gray-50 border-gray-200 text-gray-900 pl-9"
            />
            <MessageCircle className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
          
          {filteredSessions.length > 0 && (
            <div className="flex items-center justify-between text-xs text-gray-500 mt-3">
              <span>
                {searchQuery ? `Found ${filteredSessions.length}` : 'Chat History'}
              </span>
              {sessions.length > 0 && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={exportConversation}
                  disabled={messages.length === 0}
                  className="text-gray-400 hover:text-blue-600 h-6 w-6 p-0"
                  title="Export conversation"
                >
                  <FileText className="h-3 w-3" />
                </Button>
              )}
            </div>
          )}
        </div>
        
        {/* Chat History - Grouped by Subject */}
        <div className="space-y-4 flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-700">
              {searchQuery ? `Found ${filteredSessions.length}` : 'Chat History'}
            </h3>
            {sessions.length > 0 && (
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <span>{sessions.length} total</span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={exportConversation}
                  disabled={messages.length === 0}
                  className="text-gray-400 hover:text-blue-600 h-6 w-6 p-0"
                  title="Export conversation"
                >
                  <FileText className="h-3 w-3" />
                </Button>
              </div>
            )}
          </div>
          
          <div className="space-y-4">
            {Object.keys(groupedSessions).length > 0 ? (
              Object.entries(groupedSessions).map(([subject, subjectSessions]) => (
                <div key={subject} className="space-y-1">
                  <div className="flex items-center space-x-2 px-2 py-1">
                    <BookOpen className="h-3 w-3 text-blue-600" />
                    <h4 className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                      {subject}
                    </h4>
                    <div className="flex-1 h-px bg-gray-100"></div>
                    <span className="text-xs text-gray-400">{subjectSessions.length}</span>
                  </div>
                  
                  {subjectSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className={`flex items-center justify-between px-3 py-2 ml-4 rounded-lg transition-colors text-sm group ${
                        currentSession === session.session_id
                          ? 'bg-blue-50 text-blue-900 border border-blue-200'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <div 
                        className="flex items-center flex-1 min-w-0 cursor-pointer"
                        onClick={() => loadSession(session.session_id)}
                      >
                        {/* Session Status Icons */}
                        <div className="flex items-center mr-2">
                          {session.pinned && <Pin className="h-3 w-3 text-blue-600 mr-1" />}
                          {session.bookmarked && <Star className="h-3 w-3 text-yellow-500 mr-1" />}
                          <MessageCircle className="h-3 w-3 text-gray-400" />
                        </div>
                        
                        {/* Session Title - Editable */}
                        {sessionActions.isRenaming === session.session_id ? (
                          <input
                            type="text"
                            value={renameValue}
                            onChange={(e) => setRenameValue(e.target.value)}
                            onBlur={() => {
                              if (renameValue.trim() && renameValue.trim() !== session.title) {
                                renameSession(session.session_id, renameValue.trim());
                              } else {
                                setSessionActions({ ...sessionActions, isRenaming: null });
                                setRenameValue('');
                              }
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.target.blur();
                              } else if (e.key === 'Escape') {
                                setSessionActions({ ...sessionActions, isRenaming: null });
                                setRenameValue('');
                              }
                            }}
                            className="flex-1 text-sm bg-white border-2 border-blue-300 rounded px-2 py-1 mr-2 focus:outline-none focus:border-blue-500"
                            autoFocus
                            placeholder="Enter session name..."
                          />
                        ) : (
                          <span className="truncate font-medium flex-1">{session.title}</span>
                        )}
                      </div>
                      
                      {/* Session Actions */}
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-400 flex-shrink-0">
                          {formatTime(session.last_updated)}
                        </span>
                        
                        {/* Three-dot menu */}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSessionActions({
                              ...sessionActions,
                              showMenu: sessionActions.showMenu === session.session_id ? null : session.session_id
                            });
                          }}
                          className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600 transition-colors"
                          title="Session actions"
                        >
                          <MoreVertical className="h-3 w-3" />
                        </Button>
                        
                        {/* Action Menu */}
                        {sessionActions.showMenu === session.session_id && (
                          <div className="session-action-menu absolute right-0 top-8 w-48 bg-white rounded-lg shadow-xl border border-gray-200 z-50 animate-in fade-in-0 zoom-in-95">
                            <div className="py-2">
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  setRenameValue(session.title);
                                  setSessionActions({ 
                                    showMenu: null, 
                                    isRenaming: session.session_id 
                                  });
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                                type="button"
                              >
                                <Edit className="h-4 w-4 mr-3 text-gray-500" />
                                Rename
                              </button>
                              
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  setSessionActions({ showMenu: null, isRenaming: null });
                                  togglePinSession(session.session_id, session.pinned || false);
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                                type="button"
                              >
                                <Pin className={`h-4 w-4 mr-3 ${session.pinned ? 'text-blue-600' : 'text-gray-500'}`} />
                                {session.pinned ? 'Unpin' : 'Pin to top'}
                              </button>
                              
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  setSessionActions({ showMenu: null, isRenaming: null });
                                  toggleBookmarkSession(session.session_id, session.bookmarked || false);
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                                type="button"
                              >
                                <Star className={`h-4 w-4 mr-3 ${session.bookmarked ? 'text-yellow-500 fill-current' : 'text-gray-500'}`} />
                                {session.bookmarked ? 'Remove bookmark' : 'Add bookmark'}
                              </button>
                              
                              <hr className="my-1 border-gray-100" />
                              
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  setSessionActions({ showMenu: null, isRenaming: null });
                                  deleteSession(session.session_id);
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                type="button"
                              >
                                <Trash2 className="h-4 w-4 mr-3" />
                                Delete conversation
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <MessageCircle className="h-8 w-8 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-1">No conversations yet</p>
                <p className="text-xs text-gray-400">Start chatting to see your history</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {showMobileSidebar && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={() => setShowMobileSidebar(false)}
          />
          
          {/* Sidebar */}
          <div className="absolute left-0 top-0 h-full w-80 max-w-[80vw] bg-white shadow-xl flex flex-col">
            {/* Header with close button */}
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Brain className="h-5 w-5 text-white" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">Dhruv AI</h2>
                </div>
                <Button 
                  size="sm" 
                  onClick={() => setShowMobileSidebar(false)}
                  className="bg-gray-50 hover:bg-gray-100 text-gray-600 border-gray-200"
                  variant="outline"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="space-y-3">
                {/* New Chat Button */}
                <Button 
                  size="sm" 
                  onClick={() => {
                    startNewSession();
                    setShowMobileSidebar(false);
                  }}
                  className="w-full bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200"
                  variant="outline"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Chat
                </Button>
                
                {/* Subject Selector */}
                <div className="relative">
                  <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                    <SelectTrigger className="bg-gray-50 border-gray-200 text-gray-900">
                      <BookOpen className="h-4 w-4 mr-2 text-blue-600" />
                      <SelectValue placeholder="Select subject" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects[user?.exam_type]?.map(subject => (
                        <SelectItem key={subject} value={subject}>
                          {subject}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Search */}
                <div className="relative">
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search conversations..."
                    className="bg-gray-50 border-gray-200 text-gray-900 pl-9"
                  />
                  <MessageCircle className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                </div>
              </div>
            </div>

            {/* Mobile Chat History - Same as desktop but scrollable */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-700">
                  {searchQuery ? `Found ${filteredSessions.length}` : 'Chat History'}
                </h3>
                {sessions.length > 0 && (
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{sessions.length} total</span>
                  </div>
                )}
              </div>

              {Object.keys(groupedSessions).length > 0 ? (
                Object.entries(groupedSessions).map(([subject, sessionGroup]) => (
                  <div key={subject} className="mb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-xs font-medium text-gray-600">{subject}</h4>
                      <div className="flex-1 h-px bg-gray-200"></div>
                      <span className="text-xs text-gray-400">{sessionGroup.length}</span>
                    </div>
                    <div className="space-y-2">
                      {sessionGroup.map((session) => (
                        <div
                          key={session.session_id}
                          onClick={() => {
                            loadSession(session.session_id);
                            setShowMobileSidebar(false);
                          }}
                          className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                            currentSession?.session_id === session.session_id
                              ? 'bg-blue-50 border-blue-200'
                              : 'bg-white border-gray-200 hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-2 mb-1">
                                {session.is_pinned && (
                                  <Pin className="h-3 w-3 text-blue-500" />
                                )}
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {session.title || 'New conversation'}
                                </p>
                              </div>
                              <p className="text-xs text-gray-500 mb-1">
                                {session.created_at ? formatDate(session.created_at) : 'No date'}
                              </p>
                              {session.last_message_preview && (
                                <p className="text-xs text-gray-600 line-clamp-2">
                                  {session.last_message_preview}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <MessageCircle className="h-8 w-8 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 mb-1">No conversations yet</p>
                  <p className="text-xs text-gray-400">Start chatting to see your history</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white lg:w-auto w-full">
        {/* Enhanced Header with Engagement Features */}
        <div className="bg-gradient-to-r from-white via-blue-50 to-purple-50 border-b border-gray-100 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {/* Mobile Hamburger Menu */}
              <Button
                onClick={() => setShowMobileSidebar(true)}
                className="lg:hidden mr-3 bg-white hover:bg-gray-50 text-gray-600 border border-gray-200 p-2"
                variant="outline"
                size="sm"
              >
                <Menu className="h-5 w-5" />
              </Button>
              
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                  <GraduationCap className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    AI Tutor
                  </h1>
                  <div className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                    <span className="hidden sm:inline">100% Hallucination-Free</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Essential Student Stats */}
            <div className="flex items-center space-x-4">
              {/* Usage Remaining */}
              <div className="flex items-center text-sm text-gray-600">
                <Brain className="h-4 w-4 text-blue-500 mr-1" />
                <span>
                  {isFeatureUnlimited('ai_tutor_daily') ? 'Unlimited' : `${getFeatureRemaining('ai_tutor_daily')} left today`}
                </span>
              </div>
              
              {/* Streak & XP Combined */}
              <div className="flex items-center space-x-3 text-sm">
                <div className="flex items-center text-orange-600">
                  <Zap className="h-4 w-4 mr-1" />
                  <span>{streakInfo.current_streak} day streak</span>
                </div>
                <div className="flex items-center text-purple-600">
                  <Star className="h-4 w-4 mr-1" />
                  <span>Level {xpInfo.current_level}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 bg-white" data-testid="chat-container">
          <div className="max-w-5xl mx-auto space-y-8">
            {messages.length === 0 ? (
              // Clean Welcome State
              <div className="text-center py-16">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ask Mentor or Professor anything – doubts, concepts, or exam prep.
                </h3>
                <p className="text-gray-600 mb-8">
                  Get personalized help for {selectedSubject} from our AI tutors
                </p>
                
                {/* Enhanced Scrollable Prompt Cards */}
                <div className="max-w-4xl mx-auto">
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3 text-center">
                      Popular Questions for {selectedSubject}
                    </h4>
                    <div className="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide">
                      {getSubjectSuggestions().map((suggestion, index) => (
                        <div
                          key={index}
                          onClick={() => setCurrentMessage(suggestion)}
                          className="flex-shrink-0 w-72 bg-white border border-gray-200 rounded-lg p-4 cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-lg hover:border-blue-300 hover:-translate-y-1 group"
                        >
                          <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                              <Lightbulb className="h-4 w-4 text-blue-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 line-clamp-3 group-hover:text-blue-700 transition-colors">
                                {suggestion}
                              </p>
                              <div className="mt-2 flex items-center text-xs text-gray-500 group-hover:text-blue-500 transition-colors">
                                <MessageCircle className="h-3 w-3 mr-1" />
                                Click to ask
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Quick Action Buttons */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    <Button 
                      onClick={() => setCurrentMessage("Explain this concept step by step")}
                      className="h-auto p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 text-gray-700 hover:from-blue-100 hover:to-indigo-100 hover:border-blue-300 justify-start text-left group transition-all duration-300 hover:scale-105"
                      variant="outline"
                    >
                      <div className="flex items-center w-full">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mr-4 group-hover:bg-blue-600 transition-colors">
                          <GraduationCap className="h-5 w-5 text-white" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium text-gray-900 group-hover:text-blue-700">Professor Mode</div>
                          <div className="text-sm text-gray-600">Detailed explanations & theory</div>
                        </div>
                      </div>
                    </Button>
                    
                    <Button 
                      onClick={() => setCurrentMessage("Help me stay motivated and plan my studies")}
                      className="h-auto p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-gray-700 hover:from-green-100 hover:to-emerald-100 hover:border-green-300 justify-start text-left group transition-all duration-300 hover:scale-105"
                      variant="outline"
                    >
                      <div className="flex items-center w-full">
                        <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center mr-4 group-hover:bg-green-600 transition-colors">
                          <Heart className="h-5 w-5 text-white" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium text-gray-900 group-hover:text-green-700">Mentor Mode</div>
                          <div className="text-sm text-gray-600">Motivation & study guidance</div>
                        </div>
                      </div>
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              // Chat Messages
              messages.map((message, index) => (
                <div key={index} className="space-y-4">
                  {/* Handle system error messages differently */}
                  {message.type === 'system_error' ? (
                    <div className="flex justify-center">
                      <div className="max-w-2xl bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 shadow-sm">
                        <div className="flex items-center">
                          <AlertCircle className="h-4 w-4 mr-2 text-red-500" />
                          <p className="text-sm leading-relaxed">{message.message}</p>
                        </div>
                        <div className="flex items-center justify-center mt-2 text-xs text-red-500">
                          <Clock className="h-3 w-3 mr-1" />
                          <span>{formatTime(message.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      {/* Clean User Message */}
                      <div className="flex justify-end">
                        <div className="max-w-2xl bg-blue-500 text-white rounded-2xl rounded-br-md p-4 shadow-sm">
                          <p className="text-sm leading-relaxed">{message.message}</p>
                          <div className="flex items-center justify-end mt-2 text-xs text-blue-100">
                            <Clock className="h-3 w-3 mr-1" />
                            <span>{formatTime(message.timestamp)}</span>
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  {/* Only show AI response for non-system-error messages */}
                  {message.type !== 'system_error' && (
                  <div className="flex justify-start">
                    <div className="max-w-5xl w-full">
                      {message.dual_response ? (
                        /* Enhanced Dual Response Layout */
                        <DualResponseContainer
                          primaryResponse={message.dual_response.primary}
                          secondaryResponse={message.dual_response.secondary}
                          scenarioType={message.dual_response.scenario_type}
                          confidence={message.dual_response.confidence}
                          timestamp={formatTime(message.timestamp)}
                          
                          // Phase C: Guardrails Data
                          guardrails={message.guardrails}
                          disagreementAlert={message.disagreement_alert}
                          
                          // Phase D: Action Buttons Data
                          actionButtons={message.action_buttons}
                          
                          // Phase E: Analytics Data  
                          analytics={message.analytics}
                          
                          // Event Handlers
                          onFeedback={(feedback) => submitUserFeedback(message.session_id, feedback, message.topic_detected)}
                          onPracticMore={() => handlePracticeMore(message.message, message.subject, message.topic_detected)}
                          onAddToNotes={() => handleAddToNotes(
                            `${message.subject} - ${message.topic_detected}`,
                            message.dual_response.primary.response,
                            message.subject,
                            message.topic_detected,
                            message.session_id
                          )}
                          onCreateFlashcards={() => handleCreateFlashcards(
                            `${message.subject} Flashcards - ${message.topic_detected}`,
                            message.dual_response.primary.response,
                            message.subject,
                            message.topic_detected,
                            message.session_id
                          )}
                          onScheduleRevision={() => handleScheduleRevision(
                            message.session_id,
                            'concept',
                            `${message.subject} - ${message.topic_detected}`,
                            0.6
                          )}
                        />
                      ) : (
                        /* Single Response Layout (mentor-only or professor-only) */
                        <div>
                          <div className="flex items-center mb-2">
                            {message.persona === 'professor' ? (
                              <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                            ) : message.persona === 'mentor' ? (
                              <Heart className="h-5 w-5 text-green-600 mr-2" />
                            ) : (
                              <Brain className="h-5 w-5 text-blue-600 mr-2" />
                            )}
                            <span className="text-sm font-medium text-gray-700">
                              {message.persona === 'professor' ? 'Professor' : message.persona === 'mentor' ? 'Mentor' : 'Dhruv AI'}
                            </span>
                            {message.confidence && (
                              <Badge variant="outline" className="ml-2 text-xs">
                                {Math.round(message.confidence * 100)}% confident
                              </Badge>
                            )}
                          </div>
                          
                          <div className="bg-white rounded-lg shadow-sm">
                            <div className="max-w-none">
                              {/* Use structured formatting for Professor and Mentor responses */}
                              {(message.persona === 'professor' || message.persona === 'mentor') ? (
                                <div 
                                  className="structured-ai-response"
                                  dangerouslySetInnerHTML={{
                                    __html: formatProfessorMentorResponse(message.response, message.persona)
                                  }}
                                />
                              ) : (
                                <div className="p-4">
                                  <div 
                                    className="whitespace-pre-wrap text-gray-800"
                                    dangerouslySetInnerHTML={{
                                      __html: formatMathExpressions(message.response)
                                    }}
                                  />
                                </div>
                              )}
                            </div>

                            {message.reasoning && (
                              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center mb-1">
                                  <Lightbulb className="h-4 w-4 text-yellow-600 mr-1" />
                                  <span className="text-xs font-medium text-gray-600">Reasoning</span>
                                </div>
                                <p className="text-xs text-gray-600">{message.reasoning}</p>
                              </div>
                            )}

                            {/* Enhanced Action Buttons */}
                            <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
                              <div className="flex items-center space-x-2">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => copyToClipboard(message.response)}
                                  className="text-gray-500 hover:text-blue-600"
                                  title="Copy response"
                                >
                                  <BookOpen className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => bookmarkResponse(index)}
                                  className="text-gray-500 hover:text-yellow-600"
                                  title="Bookmark response"
                                >
                                  <Star className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="text-gray-500 hover:text-green-600"
                                  title="Helpful"
                                >
                                  <ThumbsUp className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="text-gray-500 hover:text-red-600"
                                  title="Not helpful"
                                >
                                  <ThumbsDown className="h-4 w-4" />
                                </Button>
                              </div>
                              
                              <div className="flex items-center space-x-3 text-xs text-gray-500">
                                <button
                                  onClick={() => setCurrentMessage(`Can you explain more about: ${message.response.substring(0, 50)}...`)}
                                  className="hover:text-blue-600 transition-colors"
                                  title="Ask follow-up question"
                                >
                                  Follow up
                                </button>
                                <div className="flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  {formatTime(message.timestamp)}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  )}
                </div>
              ))
            )}
            
            {/* Clean Loading indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100 max-w-sm">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Brain className="h-4 w-4 text-blue-600 animate-pulse" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-700">AI is thinking</span>
                        <div className="flex space-x-1">
                          <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
                          <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Clean Personalization Status */}
        {studentProfile && (
          <div className="bg-blue-50 border border-blue-100 p-3 mx-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <Target className="h-3 w-3 text-blue-600" />
                </div>
                <div>
                  <span className="text-sm font-medium text-blue-800">Personalized Learning Active</span>
                  <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                    <span>Language: <span className="font-medium text-blue-700">{studentProfile.preferred_language}</span></span>
                    <span>Style: <span className="font-medium text-blue-700">{studentProfile.learning_style}</span></span>
                    <span>Level: <span className="font-medium text-blue-700">{getDifficultyDisplay(personalizedDifficulty).label}</span></span>
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                onClick={() => setShowPersonalization(!showPersonalization)}
                className="text-purple-600 border-purple-300 hover:bg-purple-50"
              >
                {showPersonalization ? 'Hide Details' : 'Customize'}
              </Button>
            </div>
          </div>
        )}

        {/* Phase B: Personalization Settings Panel */}
        {showPersonalization && studentProfile && (
          <div className="bg-white border border-gray-200 p-6 mx-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <span>Learning Personalization</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Language Preference */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Language
                </label>
                <select 
                  value={studentProfile.preferred_language} 
                  onChange={(e) => {
                    const newProfile = { ...studentProfile, preferred_language: e.target.value };
                    setStudentProfile(newProfile);
                    updatePersonalizationProfile(newProfile);
                  }}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="english">English</option>
                  <option value="hindi">हिंदी (Hindi)</option>
                  <option value="hinglish">Hinglish</option>
                </select>
              </div>

              {/* Learning Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Learning Style
                </label>
                <select 
                  value={studentProfile.learning_style} 
                  onChange={(e) => {
                    const newProfile = { ...studentProfile, learning_style: e.target.value };
                    setStudentProfile(newProfile);
                    updatePersonalizationProfile(newProfile);
                  }}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="visual">Visual Learner</option>
                  <option value="analytical">Analytical Learner</option>
                  <option value="practical">Practical Learner</option>
                  <option value="balanced">Balanced Approach</option>
                </select>
              </div>

              {/* Response Length */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Response Detail Level
                </label>
                <select 
                  value={studentProfile.response_length_preference} 
                  onChange={(e) => {
                    const newProfile = { ...studentProfile, response_length_preference: e.target.value };
                    setStudentProfile(newProfile);
                    updatePersonalizationProfile(newProfile);
                  }}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="short">Short & Concise</option>
                  <option value="medium">Medium Detail</option>
                  <option value="detailed">Detailed Explanations</option>
                </select>
              </div>

              {/* Difficulty Preference */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Preference
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={studentProfile.difficulty_preference}
                  onChange={(e) => {
                    const newProfile = { ...studentProfile, difficulty_preference: parseFloat(e.target.value) };
                    setStudentProfile(newProfile);
                    updatePersonalizationProfile(newProfile);
                  }}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Beginner</span>
                  <span>Intermediate</span>
                  <span>Advanced</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* File Upload Section - Clean and Professional */}

        {/* Phase A: File Upload & Context Pin Area */}
        {(selectedFile || selectedContext || showContextPin) && (
          <div className="bg-gray-50 border-t border-gray-200 p-4">
            <div className="max-w-4xl mx-auto space-y-4">
              
              {/* Enhanced File Upload Area */}
              {!selectedFile && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-dashed border-blue-300 p-6 text-center hover:border-blue-400 transition-colors">
                  <div className="flex flex-col items-center space-y-3">
                    <div className="bg-blue-100 rounded-full p-3">
                      <Upload className="h-8 w-8 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        📄 Upload Documents & Images
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Upload your study materials for instant AI analysis and help
                      </p>
                      <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <ImageIcon className="h-4 w-4 text-green-500" />
                          <span>Images</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <FileIcon className="h-4 w-4 text-red-500" />
                          <span>PDF Files</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Selected File Display */}
              {selectedFile && (
                <div className="bg-white rounded-lg border border-blue-200 p-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        {selectedFile.type.startsWith('image/') ? (
                          <ImageIcon className="h-10 w-10 text-blue-500" />
                        ) : (
                          <FileIcon className="h-10 w-10 text-red-500" />
                        )}
                        {loading && (
                          <div className="absolute -top-1 -right-1 h-4 w-4 bg-blue-500 rounded-full animate-pulse"></div>
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 flex items-center space-x-2">
                          <span>{selectedFile.name}</span>
                          {loading && <span className="text-blue-600 text-sm">🤖 AI Analyzing...</span>}
                        </p>
                        <p className="text-sm text-gray-500">
                          Ready for analysis
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {!loading && (
                        <Button
                          onClick={() => processFileUpload(selectedFile)}
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
                        >
                          🚀 Analyze with AI
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        onClick={clearSelectedFile}
                        disabled={loading}
                        className="hover:bg-red-50 hover:border-red-300"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  {uploadProgress > 0 && (
                    <div className="mt-4">
                      <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <div className="flex justify-between items-center mt-2">
                        <p className="text-sm font-medium text-blue-600">
                          {uploadProgress < 30 ? '📤 Uploading...' : 
                           uploadProgress < 70 ? '🤖 AI Processing...' : 
                           uploadProgress < 95 ? '✨ Generating Response...' : '✅ Complete!'}
                        </p>
                        <span className="text-sm font-bold text-blue-600">{uploadProgress}%</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Selected Context Display */}
              {selectedContext && (
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <selectedContext.icon className="h-6 w-6 text-purple-500" />
                      <div>
                        <p className="font-medium text-gray-900">{selectedContext.title}</p>
                        <p className="text-sm text-gray-500">{selectedContext.description}</p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={clearContext}
                      size="sm"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              {/* Context Pin Selection */}
              {showContextPin && (
                <div className="bg-white rounded-lg border border-gray-200 p-4 max-h-64 overflow-y-auto">
                  <h4 className="font-medium text-gray-900 mb-3">Connect with Previous Content</h4>
                  <div className="space-y-2">
                    {availableContexts.map((context) => (
                      <div
                        key={`${context.type}-${context.id}`}
                        onClick={() => selectContext(context)}
                        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                      >
                        <context.icon className="h-5 w-5 text-gray-500" />
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900">{context.title}</p>
                          <p className="text-xs text-gray-500">{context.description}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {context.type.replace('_', ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  {availableContexts.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No previous content available</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* XP Gain Popup */}
        {showXPPopup && lastXPGain && (
          <div className="fixed top-20 right-6 z-50 animate-in slide-in-from-top-5 fade-in-0 duration-500">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg shadow-lg p-4 min-w-[200px] border border-white/20">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center mr-2">
                    <Sparkles className="h-5 w-5 text-white animate-pulse" />
                  </div>
                  <span className="font-bold">+{lastXPGain.xp_awarded} XP</span>
                </div>
                {lastXPGain.level_up && (
                  <Badge className="bg-yellow-400 text-yellow-900 border-yellow-300">
                    Level Up!
                  </Badge>
                )}
              </div>
              
              <div className="text-sm opacity-90 mb-2">
                Total: {lastXPGain.total_xp} XP • Level {lastXPGain.level}
              </div>
              
              {/* XP Progress Bar */}
              <div className="w-full bg-white/20 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${xpInfo.progress_percentage}%` }}
                ></div>
              </div>
              
              <div className="text-xs opacity-75 mt-1">
                {lastXPGain.xp_to_next_level} XP to next level
              </div>
              
              {lastXPGain.milestone_achieved && (
                <div className="mt-2 text-xs bg-white/10 rounded px-2 py-1">
                  🏆 {lastXPGain.milestone_achieved}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Clean Input Area */}
        <div className="bg-white border-t border-gray-100 p-6">
          <div className="max-w-4xl mx-auto">
            {/* Mode Selection Pills */}
            <div className="flex items-center justify-center mb-4">
              <div className={`flex items-center bg-gray-50 rounded-full p-1 border border-gray-200 transition-all duration-300 ${
                modeTransition ? 'ring-2 ring-blue-200 ring-opacity-50' : ''
              }`}>
                <Button
                  onClick={() => handleAiModeTransition('mentor')}
                  variant={aiMode === 'mentor' ? 'default' : 'ghost'}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
                    aiMode === 'mentor' 
                      ? 'bg-blue-500 text-white shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                  } ${modeTransition ? 'scale-95 opacity-75' : 'scale-100 opacity-100'}`}
                >
                  <Heart className="h-4 w-4 mr-2" />
                  Mentor
                </Button>
                <Button
                  onClick={() => handleAiModeTransition('professor')}
                  variant={aiMode === 'professor' ? 'default' : 'ghost'}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
                    aiMode === 'professor' 
                      ? 'bg-blue-500 text-white shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                  } ${modeTransition ? 'scale-95 opacity-75' : 'scale-100 opacity-100'}`}
                >
                  <GraduationCap className="h-4 w-4 mr-2" />
                  Professor
                </Button>
                <Button
                  onClick={() => handleAiModeTransition('dual')}
                  variant={aiMode === 'dual' ? 'default' : 'ghost'}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
                    aiMode === 'dual' 
                      ? 'bg-blue-500 text-white shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                  } ${modeTransition ? 'scale-95 opacity-75' : 'scale-100 opacity-100'}`}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Both
                </Button>
              </div>
            </div>

            {/* Chat Input Bar */}
            <div className="flex items-center space-x-3">
              <div className="flex-1 relative">
                <Textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  placeholder={
                    dragOver 
                      ? 'Drop your file here...' 
                      : loading 
                        ? 'AI is thinking...' 
                        : 'Type your doubt here...'
                  }
                  className={`message-input chat-input resize-none border min-h-12 text-base md:text-sm pr-20 ${
                    dragOver 
                      ? 'border-blue-300 bg-blue-50' 
                      : isListening 
                        ? 'border-red-300 bg-red-50' 
                        : loading
                          ? 'border-gray-300 bg-gray-50'
                          : 'border-gray-200 focus:border-blue-300 hover:border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-blue-100 transition-all mobile-transition`}
                  rows={2}
                  disabled={loading}
                />
                
                {/* Input Icons */}
                <div className="absolute bottom-2 right-2 flex items-center space-x-1">
                  {recognition && (
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={isRecording ? enhancedStopVoiceInput : enhancedStartVoiceInput}
                      className={`voice-button chat-action-button relative min-h-10 min-w-10 md:h-7 md:w-7 p-2 md:p-0 transition-all duration-300 mobile-transition ${
                        isRecording
                          ? 'text-red-500 scale-110 animate-pulse'
                          : 'text-gray-400 hover:text-blue-600'
                      }`}
                      disabled={loading}
                      title={isRecording ? 'Stop recording' : 'Start voice input'}
                      aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
                    >
                      {/* Voice Animation Rings */}
                      {voiceAnimation && (
                        <>
                          <div className="absolute inset-0 rounded-md bg-red-400 animate-ping opacity-25"></div>
                          <div className="absolute inset-0 rounded-md bg-red-400 animate-ping opacity-20" style={{animationDelay: '0.2s'}}></div>
                          <div className="absolute inset-0 rounded-md bg-red-400 animate-ping opacity-15" style={{animationDelay: '0.4s'}}></div>
                        </>
                      )}
                      
                      <div className="relative z-10">
                        {isRecording ? (
                          <MicOff className="h-4 w-4" />
                        ) : (
                          <Mic className="h-4 w-4" />
                        )}
                      </div>
                    </Button>
                  )}

                  {/* Voice Status Indicator */}
                  {isRecording && (
                    <div className="flex items-center ml-2 text-red-600 animate-pulse">
                      <div className="w-2 h-2 bg-red-500 rounded-full mr-1 animate-ping"></div>
                      <span className="text-xs font-medium">Recording...</span>
                    </div>
                  )}
                  
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => fileInputRef.current?.click()}
                    className="chat-action-button min-h-10 min-w-10 md:h-7 md:w-7 p-2 md:p-0 text-gray-400 hover:text-blue-600 mobile-transition"
                    disabled={loading}
                    aria-label="Upload file"
                  >
                    <Upload className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowQuickSuggestions(!showQuickSuggestions)}
                    className="chat-action-button min-h-10 min-w-10 md:h-7 md:w-7 p-2 md:p-0 text-gray-400 hover:text-blue-600 mobile-transition"
                    title="⋯ More options"
                    disabled={loading}
                    aria-label="More options"
                  >
                    <AlertCircle className="h-4 w-4" />
                  </Button>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp,application/pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
              
              <Button 
                onClick={sendMessage}
                disabled={loading || !currentMessage.trim()}
                className="send-button bg-blue-500 hover:bg-blue-600 min-h-12 min-w-12 px-4 py-3 rounded-lg mobile-transition disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Clean Suggestions Panel */}
            {showQuickSuggestions && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Quick Questions</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowQuickSuggestions(false)}
                    className="h-5 w-5 p-0 text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
                <div className="grid grid-cols-1 gap-1 max-h-32 overflow-y-auto">
                  {getSubjectSuggestions().map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setCurrentMessage(suggestion);
                        setShowQuickSuggestions(false);
                      }}
                      className="text-left text-xs p-2 bg-white rounded hover:bg-blue-50 transition-colors border border-gray-100 hover:border-blue-200"
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Clean Footer */}
            <div className="flex items-center justify-center mt-3">
              <span className="text-xs text-gray-400">Press Enter to send, Shift+Enter for new line</span>
            </div>
          </div>
        </div>
      </div>

      {/* Phase E: Wellness Check Modal */}
      {showWellnessCheck && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Heart className="h-5 w-5 mr-2 text-red-500" />
              Quick Wellness Check
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Taking a moment to check in helps us personalize your learning experience better.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stress Level (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={wellnessData.stress_level}
                  onChange={(e) => setWellnessData(prev => ({
                    ...prev,
                    stress_level: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Very Low</span>
                  <span className="font-medium">{wellnessData.stress_level}</span>
                  <span>Very High</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motivation Level (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={wellnessData.motivation_level}
                  onChange={(e) => setWellnessData(prev => ({
                    ...prev,
                    motivation_level: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Very Low</span>
                  <span className="font-medium">{wellnessData.motivation_level}</span>
                  <span>Very High</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confidence Level (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={wellnessData.confidence_level}
                  onChange={(e) => setWellnessData(prev => ({
                    ...prev,
                    confidence_level: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Very Low</span>
                  <span className="font-medium">{wellnessData.confidence_level}</span>
                  <span>Very High</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Study Satisfaction (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={wellnessData.study_satisfaction}
                  onChange={(e) => setWellnessData(prev => ({
                    ...prev,
                    study_satisfaction: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Very Low</span>
                  <span className="font-medium">{wellnessData.study_satisfaction}</span>
                  <span>Very High</span>
                </div>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <Button
                variant="outline"
                onClick={() => setShowWellnessCheck(false)}
                className="flex-1"
              >
                Skip for Now
              </Button>
              <Button
                onClick={handleWellnessCheck}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                Submit Check-in
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast.show && (
        <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-5 fade-in-0 duration-300">
          <div className={`rounded-lg shadow-lg p-4 min-w-[250px] border ${
            toast.type === 'success' 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : toast.type === 'error'
              ? 'bg-red-50 border-red-200 text-red-800'
              : 'bg-blue-50 border-blue-200 text-blue-800'
          }`}>
            <div className="flex items-center">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-3 ${
                toast.type === 'success' 
                  ? 'bg-green-500' 
                  : toast.type === 'error'
                  ? 'bg-red-500'
                  : 'bg-blue-500'
              }`}>
                {toast.type === 'success' ? (
                  <CheckCircle className="h-3 w-3 text-white" />
                ) : toast.type === 'error' ? (
                  <X className="h-3 w-3 text-white" />
                ) : (
                  <Lightbulb className="h-3 w-3 text-white" />
                )}
              </div>
              <span className="font-medium">{toast.message}</span>
            </div>
          </div>
        </div>
      )}


      {/* Global Upsell Modal is rendered in App.js; single reusable popup */}
    </div>
  );
}