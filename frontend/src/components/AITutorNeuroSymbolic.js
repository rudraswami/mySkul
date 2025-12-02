/**
 * AI Tutor - Neuro-Symbolic v3.0
 * Indian Student-Centric, Karnataka-Friendly Learning Experience
 * 
 * GAMIFICATION INTEGRATED: XP, Streaks, Micro-rewards, Levels
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useToast } from '../contexts/ToastContext';
import { 
  Brain,
  Send,
  Plus,
  Menu,
  ChevronLeft,
  Loader,
  Book,
  Sparkles,
  MessageCircle,
  Edit2,
  Pin,
  Bookmark,
  Trash2,
  RefreshCw,
  Check,
  X,
  MoreVertical,
  ArrowRight,
  Image as ImageIcon,
  Paperclip,
  XCircle,
  Flame,
  Zap,
  Trophy
} from 'lucide-react';
import NeuroSymbolicResponse from './neuro-symbolic/NeuroSymbolicResponse';
import MentorResponseV2 from './mentor-v2/MentorResponseV2';
import SmartResponse from './SmartResponse';
import UpgradeModal from './UpgradeModal';
import OnboardingTour from './OnboardingTour';
import apiClient from '../api/client';
import '../styles/ai-tutor-redesign.css'; // Shared scroll stability styles

// V1 Enhancement Components
import VisualSketchViewer from './visual/VisualSketchViewer';
import SubjectBadge from './visual/SubjectBadge';
import FollowUpQuestions from './visual/FollowUpQuestions';
import ShareButtons from './visual/ShareButtons';
import MemoryContextBanner from './MemoryContextBanner';

// Sathi Navigation Menu - Integrated nav for full-screen chat experience
import SathiNavMenu from './chat/SathiNavMenu';

// Gamification Components
import MicroReward, { LevelUpCelebration, StreakCelebration } from './gamification/MicroReward';
import { useGamification } from '../hooks/useGamification';

// NuroSpark Neural Thinking Animation
import { NeuralThinkingIndicator } from './chat/NeuralThinkingIndicator';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Helper: Format relative time consistently
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
    
    // For older dates, show short date
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
};

// 🧠 NuroSpark Neural Thinking Indicator
// Premium, compact cognitive processing animation (max 32px height)
// Uses: NeuralThinkingIndicator from ./chat/NeuralThinkingIndicator
function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.15 }}
      className="flex justify-center w-full"
    >
      <NeuralThinkingIndicator isLoading={true} variant="glow" />
    </motion.div>
  );
}

export default function AITutorNeuroSymbolic() {
  const { user } = useAuth();
  const { checkFeatureAccess, trackFeatureUsage } = useSubscription();
  const { success: toastSuccess, error: toastError } = useToast();
  
  // 🎮 GAMIFICATION - Hook for XP, streaks, rewards
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

  // Core state
  const [messages, setMessages] = useState([]);
  
  // Follow-up suggestions (shown near input, not in response)
  const [floatingFollowUps, setFloatingFollowUps] = useState([]);
  
  // Poll for async visual generation
  const pollForVisual = async (taskId, messageId, retries = 0) => {
    const maxRetries = 30; // 30 seconds max (1s intervals)
    if (retries >= maxRetries) {
      console.log('Visual generation timeout');
      return;
    }
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/ai/visual/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.status === 'completed' && data.visual_sketch) {
          // Debug: Log visual data structure
          console.log('🎨 Visual data received:', {
            hasSvg: !!data.visual_sketch?.svg,
            svgLength: data.visual_sketch?.svg?.length || 0,
            metaphors: data.visual_sketch?.metaphors,
            structure: Object.keys(data.visual_sketch || {})
          });
          
          // Update message with visual - CRITICAL: Preserve normalized structure
          setMessages(prev => prev.map(msg => {
            if (msg.message_id === messageId) {
              // Ensure content is normalized before updating
              let normalizedContent = msg.content;
              if (typeof normalizedContent === 'string') {
                normalizedContent = normalizeAIContent(normalizedContent);
              } else if (!normalizedContent || typeof normalizedContent !== 'object' || Array.isArray(normalizedContent)) {
                normalizedContent = normalizeAIContent(normalizedContent);
              }
              
              // Ensure visual_sketch has proper structure
              const visualSketch = data.visual_sketch?.svg 
                ? data.visual_sketch  // Already has svg property
                : { svg: data.visual_sketch?.svg || '', ...data.visual_sketch }; // Ensure svg property exists
              
              return {
                ...msg,
                content: {
                  ...normalizedContent,
                  visual_sketch: visualSketch
                },
                visual_sketch: visualSketch
              };
            }
            return msg;
          }));
          console.log('✅ Visual loaded successfully');
        } else if (data.status === 'generating') {
          // Continue polling
          setTimeout(() => pollForVisual(taskId, messageId, retries + 1), 1000);
        } else if (data.status === 'failed') {
          console.log('Visual generation failed:', data.error);
        }
      }
    } catch (error) {
      console.error('Error polling for visual:', error);
      // Retry on error
      if (retries < maxRetries) {
        setTimeout(() => pollForVisual(taskId, messageId, retries + 1), 1000);
      }
    }
  };
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  
  // CRITICAL FIX: Persist currentSession to localStorage for ChatGPT-style persistence
  const [currentSession, setCurrentSessionState] = useState(() => {
    // Initialize from localStorage on mount
    if (typeof window !== 'undefined') {
      return localStorage.getItem('dhruv_ai_current_session') || null;
    }
    return null;
  });
  
  // Wrapper to persist session changes to localStorage
  const setCurrentSession = useCallback((sessionId) => {
    setCurrentSessionState(sessionId);
    if (typeof window !== 'undefined') {
      if (sessionId) {
        localStorage.setItem('dhruv_ai_current_session', sessionId);
      } else {
        localStorage.removeItem('dhruv_ai_current_session');
      }
    }
  }, []);
  
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [sessionLoadingId, setSessionLoadingId] = useState(null);
  const [editing, setEditing] = useState({ id: null, title: '' });
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [confirmDlg, setConfirmDlg] = useState({ open: false, title: '', message: '', onConfirm: null });
  
  // Image upload state
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  // UI state
  const [showSidebar, setShowSidebar] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalData, setUpgradeModalData] = useState(null);

  // Welcome state
  const [showWelcome, setShowWelcome] = useState(true);
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  const [hasInteraction, setHasInteraction] = useState(false);

  // Gamification state - XP and Streak
  const [userProgress, setUserProgress] = useState({
    xp: 0,
    level: 1,
    streak: 0
  });
  
  // Offline detection
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Default quick prompts - Attractive and diverse (cross-subject, exam-focused)
  const [defaultPrompts, setDefaultPrompts] = useState([
    { text: "What is the difference between permutations and combinations?", subject: "Math", emoji: "🔢" },
    { text: "Explain Newton's third law with real-world examples", subject: "Physics", emoji: "🚀" },
    { text: "How do I solve quadratic equations in JEE?", subject: "Math", emoji: "✨" },
    { text: "What happens during photosynthesis step-by-step?", subject: "Biology", emoji: "🌿" },
    { text: "Explain chemical bonding with simple examples", subject: "Chemistry", emoji: "⚗️" },
    { text: "How to solve integration by parts problems?", subject: "Math", emoji: "📐" }
  ]);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  // Scroll state - tracks if user is near bottom
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [shouldScrollOnNewMessage, setShouldScrollOnNewMessage] = useState(false);

  // Available subjects
  const SUBJECTS = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'English',
    'History',
    'Geography'
  ];

  // Load default prompts on mount
  useEffect(() => {
    loadDefaultPrompts();
  }, []);
  
  // Listen for follow-up question events from MentorResponseV2
  useEffect(() => {
    const handleFollowUpQuestion = (event) => {
      const { question } = event.detail;
      setInputMessage(question);
      setTimeout(() => {
        handleSend();
      }, 100);
    };
    
    window.addEventListener('send-question', handleFollowUpQuestion);
    return () => window.removeEventListener('send-question', handleFollowUpQuestion);
  }, []);
  
  // Update floating follow-ups when messages change
  useEffect(() => {
    // Find the last AI message with follow-up suggestions
    const lastAIMessage = [...messages].reverse().find(m => m.type === 'ai');
    if (lastAIMessage?.content?.follow_up_suggestions) {
      const validSuggestions = lastAIMessage.content.follow_up_suggestions
        .filter(followUp => {
          const text = typeof followUp === 'string' ? followUp : followUp.text;
          if (!text) return false;
          const invalidPatterns = ['IMPORTANT:', 'Student Uploaded', 'IMAGE CONTAINS:', '[Student uploaded', '🖼️ Important'];
          return !invalidPatterns.some(pattern => text.toLowerCase().includes(pattern.toLowerCase()));
        })
        .slice(0, 3)
        .map(followUp => typeof followUp === 'string' ? followUp : followUp.text);
      setFloatingFollowUps(validSuggestions);
    } else {
      setFloatingFollowUps([]);
    }
  }, [messages]);
  
  // Offline detection
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toastSuccess('Back online', 'Your connection is restored! 🎉');
    };
    const handleOffline = () => {
      setIsOnline(false);
      toastError('No internet', 'You\'re offline. Messages will be queued. 📡');
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Smart auto-scroll - only scroll when user is near bottom or just sent a message
  useEffect(() => {
    if (shouldScrollOnNewMessage || isNearBottom) {
      // Use requestAnimationFrame for smoother scrolling after DOM updates
      requestAnimationFrame(() => {
        scrollToBottom();
      });
      setShouldScrollOnNewMessage(false);
    }
  }, [messages, shouldScrollOnNewMessage, isNearBottom]);
  
  // Track scroll position to detect if user is near bottom
  useEffect(() => {
    const container = chatContainerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      // Consider "near bottom" if within 150px of bottom
      const nearBottom = scrollHeight - scrollTop - clientHeight < 150;
      setIsNearBottom(nearBottom);
    };
    
    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);
  
  /**
   * Scroll to bottom - smooth and non-jumpy
   */
  const scrollToBottom = (force = false) => {
    const container = chatContainerRef.current;
    if (!container) return;
    
    // If not forced and user has scrolled up, don't auto-scroll
    if (!force && !isNearBottom) return;
    
    const targetScrollTop = container.scrollHeight - container.clientHeight;
    
    // If already at bottom (within 10px), don't animate
    if (Math.abs(container.scrollTop - targetScrollTop) < 10) return;
    
    container.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    });
  };

  // Collapse header when chat starts
  useEffect(() => {
    setHeaderCollapsed(messages.length > 0);
    setShowWelcome(messages.length === 0);
  }, [messages.length]);

  // Load default prompts (generic, not subject-specific)
  const loadDefaultPrompts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai/subjects/Mathematics/defaultPrompts`);
      if (response.ok) {
        const data = await response.json();
        if (data.prompts && data.prompts.length > 0) {
          setDefaultPrompts(data.prompts);
        }
      }
    } catch (error) {
      console.error('Error loading default prompts:', error);
      // Already have fallback in initial state
    }
  };

  // Load sessions
  const loadSessions = async () => {
    try {
      setSessionsLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await apiClient.get('/ai/chat/sessions');
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally { setSessionsLoading(false); }
  };

  // Format last updated (Today, Yesterday, or date)
  const formatLastUpdated = (ts) => {
    if (!ts) return '';
    try {
      const d = new Date(ts);
      const now = new Date();
      const sameDay = d.toDateString() === now.toDateString();
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      const isYesterday = d.toDateString() === yesterday.toDateString();
      if (sameDay) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      if (isYesterday) return 'Yesterday';
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  // Session actions
  const authHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('dhruv_ai_token')}`,
    'Content-Type': 'application/json'
  });

  const renameSession = async (session, title = null) => {
    try {
      const newTitle = title ?? (prompt('Rename chat title:', session.title || 'Untitled Chat') || '').trim();
      if (!newTitle) return;
      const res = await apiClient.put(`/ai/chat/${session.session_id}/rename`, { title: newTitle });
      if (res.status === 200) {
        await loadSessions();
        toastSuccess('Renamed', `Chat renamed to "${newTitle}"`);
      } else {
        toastError('Rename failed', 'Could not rename chat');
      }
    } catch (e) { console.error('Rename failed', e); }
  };

  // Inline rename helpers (desktop)
  const startInlineRename = (session) => setEditing({ id: session.session_id, title: session.title || '' });
  const cancelInlineRename = () => setEditing({ id: null, title: '' });
  const commitInlineRename = async (session) => {
    const t = (editing.title || '').trim();
    if (!t) return cancelInlineRename();
    await renameSession(session, t);
    // Optimistic local update to reflect immediately
    setSessions(prev => prev.map(s => s.session_id === session.session_id ? { ...s, title: t, last_updated: new Date().toISOString() } : s));
    cancelInlineRename();
  };

  const togglePinSession = async (session) => {
    try {
      const res = await apiClient.put(`/ai/chat/${session.session_id}/pin`, { pinned: !session.pinned });
      if (res.status === 200) {
        await loadSessions();
        toastSuccess(session.pinned ? 'Unpinned' : 'Pinned', `Chat ${session.pinned ? 'unpinned' : 'pinned'}`);
      } else {
        toastError('Action failed', 'Could not update pin');
      }
    } catch (e) { console.error('Pin toggle failed', e); }
  };

  const toggleBookmarkSession = async (session) => {
    try {
      const res = await apiClient.put(`/ai/chat/${session.session_id}/bookmark`, { bookmarked: !session.bookmarked });
      if (res.status === 200) {
        await loadSessions();
        toastSuccess(session.bookmarked ? 'Removed bookmark' : 'Bookmarked', `Chat ${session.bookmarked ? 'unbookmarked' : 'bookmarked'}`);
      } else {
        toastError('Action failed', 'Could not update bookmark');
      }
    } catch (e) { console.error('Bookmark toggle failed', e); }
  };

  const deleteSession = async (session) => {
    try {
      let res;
      try {
        res = await apiClient.delete(`/ai/chat/${session.session_id}`);
      } catch (err) {
        if (err?.response?.status === 403) {
          try { await apiClient.get('/auth/csrf-token'); } catch {}
          res = await apiClient.delete(`/ai/chat/${session.session_id}`);
        } else {
          throw err;
        }
      }

      if (res?.status === 200 || res?.status === 204) {
        await loadSessions();
        if (currentSession === session.session_id) {
          setCurrentSession(null);
          setMessages([]);
        }
        toastSuccess('Deleted', 'Chat deleted successfully');
      } else {
        toastError('Delete failed', 'Server did not confirm deletion');
      }
    } catch (e) {
      console.error('Delete failed', e);
      toastError('Delete failed', e?.response?.data?.detail || 'Please try again.');
    }
  };

  const requestDeleteSession = (session) => {
    setMenuOpenId(null);
    setConfirmDlg({
      open: true,
      title: 'Delete Chat?',
      message: `This will permanently delete "${session.title || 'Untitled Chat'}" and all its messages. This action cannot be undone.`,
      onConfirm: async () => {
        // Optimistic removal first
        setSessions(prev => prev.filter(s => s.session_id !== session.session_id));
        if (currentSession === session.session_id) {
          setCurrentSession(null);
          setMessages([]);
        }
        await deleteSession(session);
        setConfirmDlg({ open: false, title: '', message: '', onConfirm: null });
      }
    });
  };

  // Send message
  const handleSend = async (messageText = null) => {
    const messageToSend = messageText || inputMessage.trim();
    if (!messageToSend || loading) return;
    
    // Check if online
    if (!isOnline) {
      toastError('No internet', 'Please check your connection and try again. 📡');
      return;
    }

    // Check feature access
    const access = await checkFeatureAccess('ai_mentor');
    if (!access.has_access) {
      setUpgradeModalData(access);
      setShowUpgradeModal(true);
      return;
    }

    // Signal to scroll to bottom when new message is added
    setShouldScrollOnNewMessage(true);
    
    // Store image data before clearing (needed for user message and API)
    const currentImagePreview = imagePreview;
    const currentSelectedImage = selectedImage;
    
    // Clear input and image immediately (better UX - instant feedback)
    setInputMessage('');
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setHasInteraction(true);
    setShowWelcome(false);

    // Add user message optimistically
    // FIXED: Ensure content is always a plain string
    // Use crypto.randomUUID() for unique IDs
    const userMsg = {
      type: 'user',
      content: String(messageToSend), // Ensure it's always a string
      timestamp: new Date().toISOString(),
      id: `user_${Date.now()}_${crypto.randomUUID()}`,
      // Store image preview separately for display (not in content)
      image_preview: currentImagePreview || null
    };

    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const examMode = user?.exam_type || 'JEE';

      // Create or use existing session
      let sessionId = currentSession;
      if (!sessionId) {
        const sessionResponse = await fetch(`${BACKEND_URL}/api/ai/chat/sessions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            title: messageToSend.substring(0, 50),
            subject: '', // Will be auto-detected
            topic: 'General'
          })
        });

        if (sessionResponse.ok) {
          const sessionData = await sessionResponse.json();
          sessionId = sessionData.session.session_id;
          setCurrentSession(sessionId);
          
          // CRITICAL FIX: Immediately refresh sessions list to show new chat in sidebar
          await loadSessions();
          
          // Optimistic update: Add new session to list immediately for better UX
          const newSession = sessionData.session;
          setSessions(prev => {
            // Check if already exists (avoid duplicates)
            const exists = prev.some(s => s.session_id === sessionId);
            if (exists) return prev;
            // Add to top of list
            return [newSession, ...prev];
          });
        }
      }

      // Prepare request body
      const requestBody = {
        message: messageToSend,
        subject: '', // Auto-detect from question
        session_id: sessionId,
        exam_mode: examMode
      };
      
      // If image was selected, convert to base64 and include
      // Use currentSelectedImage (stored before clearing UI for instant feedback)
      if (currentSelectedImage) {
        const imageBase64 = await imageToBase64(currentSelectedImage);
        requestBody.image_url = imageBase64;
        requestBody.image_context = 'CRITICAL: Student uploaded image. Analyze it carefully and answer based on actual content.';
      }
      
      // ====================================================================
      // STREAMING RESPONSE (Real-time token display like ChatGPT)
      // ====================================================================
      // DISABLED: Streaming endpoint not yet implemented on backend
      // TODO: Re-enable when /api/ai/neuro-symbolic/stream is ready
      const USE_STREAMING = false; // Feature flag for streaming
      
      let data;
      let streamingHandledFlag = false; // Track if streaming handled the message
      
      if (USE_STREAMING) {
        // Create placeholder AI message for streaming
        // Use crypto.randomUUID() for unique IDs (no collisions)
        const streamingMsgId = `ai_${Date.now()}_${crypto.randomUUID()}`;
        const streamingAiMsg = {
          type: 'ai',
          content: {
            default_view: {
              greeting: '',
              main_content: { content: '' },
              metaphor: { text: '' }
            },
            progressive_sections: {},
            streaming: true
          },
          timestamp: new Date().toISOString(),
          message_id: streamingMsgId,
          user_question: messageToSend,
          isStreaming: true
        };
        
        setMessages(prev => [...prev, streamingAiMsg]);
        
        try {
          // Use streaming endpoint
          const response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(requestBody)
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let accumulatedText = '';
          let finalResponse = null;
          
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const eventData = JSON.parse(line.slice(6));
                  
                  if (eventData.type === 'text_chunk' && eventData.content) {
                    accumulatedText += eventData.content;
                    // Update message with accumulated text
                    setMessages(prev => prev.map(msg => 
                      msg.message_id === streamingMsgId 
                        ? {
                            ...msg,
                            content: {
                              ...msg.content,
                              default_view: {
                                ...msg.content.default_view,
                                main_content: { content: accumulatedText }
                              }
                            }
                          }
                        : msg
                    ));
                  } else if (eventData.type === 'complete' && eventData.data) {
                    finalResponse = eventData.data;
                  } else if (eventData.type === 'visual_fallback' && eventData.svg) {
                    // Update with visual
                    setMessages(prev => prev.map(msg => 
                      msg.message_id === streamingMsgId 
                        ? {
                            ...msg,
                            visual_sketch: { svg: eventData.svg }
                          }
                        : msg
                    ));
                  }
                } catch (e) {
                  // Ignore parse errors for incomplete chunks
                }
              }
            }
          }
          
          // Finalize with complete response
          if (finalResponse) {
            data = { response: finalResponse, detected_subject: finalResponse.detected_subject };
            streamingHandledFlag = true; // Mark as handled
            // Update final message
            setMessages(prev => prev.map(msg => 
              msg.message_id === streamingMsgId 
                ? {
                    ...msg,
                    content: normalizeAIContent(finalResponse),
                    isStreaming: false,
                    user_question: messageToSend
                  }
                : msg
            ));
          } else if (accumulatedText.length > 0) {
            // Fallback - use accumulated text
            data = { 
              response: { 
                default_view: { 
                  main_content: { content: accumulatedText },
                  greeting: '',
                  metaphor: { text: '' }
                },
                progressive_sections: {}
              } 
            };
            streamingHandledFlag = true; // Mark as handled
            setMessages(prev => prev.map(msg => 
              msg.message_id === streamingMsgId 
                ? { 
                    ...msg, 
                    isStreaming: false,
                    user_question: messageToSend
                  }
                : msg
            ));
          }
          
        } catch (streamError) {
          console.warn('⚠️ Streaming failed, falling back to regular endpoint:', streamError);
          // Remove streaming message
          setMessages(prev => prev.filter(msg => msg.message_id !== streamingMsgId));
          // Fall through to regular endpoint
        }
      }
      
      // Fallback to non-streaming endpoint if streaming failed or disabled
      if (!data) {
        const response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          if (response.status === 402) {
            const errorData = await response.json();
            setUpgradeModalData(errorData.detail);
            setShowUpgradeModal(true);
            // Remove optimistic user message
            setMessages(prev => prev.filter(m => m.id !== userMsg.id));
            return;
          }
          
          // Better error messages (student-friendly)
          let errorMessage = 'Oops! Something went wrong. Please try again.';
          let canRetry = true;
          
          if (response.status === 429) {
            errorMessage = 'Whoa! You\'re asking too fast! Take a 30-second break and try again. 🧘';
            canRetry = true;
          } else if (response.status === 500) {
            errorMessage = 'Our AI is taking a quick nap. Try again in 1 minute! 😴';
            canRetry = true;
          } else if (response.status === 503) {
            errorMessage = 'Too many students asking right now. Try in 10 seconds! 🚀';
            canRetry = true;
          } else if (response.status === 0 || error.message === 'Failed to fetch') {
            errorMessage = 'Check your internet connection and try again! 📡';
            canRetry = true;
          } else if (response.status === 401) {
            errorMessage = 'Session expired. Please log in again.';
            canRetry = false;
          }
          
          const err = new Error(errorMessage);
          err.canRetry = canRetry;
          err.originalMessage = messageToSend;
          throw err;
        }

        data = await response.json();
      }

      // Debug: Log full response to check for teaching_visual and visual_sketch
      console.log('🎨 FULL API RESPONSE:', data);
      console.log('🎨 Teaching Visual:', data.response?.teaching_visual);
      console.log('🎨 Visual Data:', data.response?.visual_data);
      console.log('🎨 Visual Sketch:', data.response?.visual_sketch);
      console.log('🎨 Whiteboard Visual:', data.response?.whiteboard_visual);

      // Skip creating new AI message if streaming already handled it
      if (!streamingHandledFlag) {
        // Add AI response - CRITICAL: Normalize content to ensure proper structure
        const normalizedResponse = normalizeAIContent(data.response);
        const aiMsg = {
          type: 'ai',
          content: {
            ...normalizedResponse,
            detected_subject: data.detected_subject || normalizedResponse?.detected_subject || data.response?.detected_subject,
            // Include visual_sketch in content for easy access
            visual_sketch: data.response?.visual_sketch || normalizedResponse?.visual_sketch || null
          },
          timestamp: new Date().toISOString(),
          message_id: data.message_id,
          emotion_detected: data.emotion_detected,
          generation_time: data.generation_time,
          // CRITICAL: Extract teaching_visual and visual_sketch from response
          teaching_visual: data.response?.teaching_visual || normalizedResponse?.teaching_visual || null,
          visual_data: data.response?.visual_data || normalizedResponse?.visual_data || null,
          visual_sketch: data.response?.visual_sketch || normalizedResponse?.visual_sketch || null,
          visual_task_id: data.response?.visual_task_id || data.response?.visual_sketch?.task_id || null,
          // NEW: Whiteboard Visual (Next-Gen Sketch Engine)
          whiteboard_visual: data.response?.whiteboard_visual || null,
          // NEW: Store user question for Interactive Visual Engine
          user_question: messageToSend
        };

        setMessages(prev => [...prev, aiMsg]);
        
        // If visual is being generated async, poll for it
        if (aiMsg.visual_task_id) {
          pollForVisual(aiMsg.visual_task_id, aiMsg.message_id);
        }
      }

      // Track usage
      await trackFeatureUsage('ai_mentor');
      
      // 🎮 GAMIFICATION: Process interaction for XP, streaks, rewards
      const responseTime = Date.now() - new Date(userMsg.timestamp).getTime();
      try {
        await processInteraction({
          interactionType: 'question',
          isCorrect: true, // Questions are always "correct" - they're learning!
          responseTimeMs: responseTime,
          concept: data.detected_subject || '',
          subject: data.detected_subject || ''
        });
      } catch (gamificationError) {
        console.warn('Gamification processing failed:', gamificationError);
        // Don't block the main flow
      }
      
      // Clear image after successful send
      handleRemoveImage();
      
      // Refresh session list to show updated message count
      loadSessions();
      
      // Auto-focus input for next question
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);

    } catch (error) {
      console.error('Error sending message:', error);
      // Add friendly error message with retry option
      const errorMsg = error.message || 'Oops! Something went wrong. Please try again! 😅';
      const canRetry = error.canRetry !== false; // Default to true
      const originalMessage = error.originalMessage || messageToSend;
      
      setMessages(prev => [
        ...prev,
        {
          type: 'error',
          content: errorMsg,
          timestamp: new Date().toISOString(),
          canRetry: canRetry,
          originalMessage: originalMessage,
          id: `error_${Date.now()}`
        }
      ]);
      
      // Also show toast for immediate feedback
      toastError('Message failed', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Handle image upload
  const handleImageSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toastError('File too large', 'Please select an image smaller than 10MB');
      return;
    }
    
    // Check file type
    if (!file.type.startsWith('image/')) {
      toastError('Invalid file', 'Please select an image file (JPG, PNG, etc.)');
      return;
    }
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
      setSelectedImage(file);
    };
    reader.readAsDataURL(file);
  };
  
  // Remove selected image
  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  // Convert image to base64 for API
  const imageToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Extract base64 part (remove data:image/jpeg;base64, prefix)
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Quick send from default prompts
  const handleQuickSend = (prompt) => {
    handleSend(prompt);
  };
  
  // Retry failed message
  const handleRetry = (errorMessage) => {
    if (!errorMessage.originalMessage) return;
    
    // Remove error message
    setMessages(prev => prev.filter(m => m.id !== errorMessage.id));
    
    // Resend original message
    handleSend(errorMessage.originalMessage);
  };

  // Start new chat
  const startNewChat = () => {
    setMessages([]);
    setCurrentSession(null);
    setShowWelcome(true);
    setHeaderCollapsed(false);
    inputRef.current?.focus();
    // Refresh sessions list to ensure it's up-to-date
    loadSessions();
  };

  // Helper function to normalize AI message content
  const normalizeAIContent = (content) => {
    // If content is already a proper object with default_view, return as is
    if (typeof content === 'object' && content !== null && !Array.isArray(content) && content.default_view) {
      return content;
    }
    
    // If content is a string, wrap it in proper structure
    if (typeof content === 'string') {
      return {
        default_view: {
          greeting: content.substring(0, 100),
          main_content: {
            content: content
          }
        },
        progressive_sections: {}
      };
    }
    
    // If content is an object but missing default_view, try to extract meaningful data
    if (typeof content === 'object' && content !== null && !Array.isArray(content)) {
      // Check if it has any response-like structure
      if (content.explanation || content.answer || content.response) {
        return {
          default_view: {
            greeting: content.greeting || 'Here\'s the explanation:',
            main_content: {
              content: content.explanation || content.answer || content.response || JSON.stringify(content)
            }
          },
          progressive_sections: {},
          detected_subject: content.detected_subject || content.subject
        };
      }
      
      // If it's an object with visual_sketch but no default_view, wrap it
      if (content.visual_sketch) {
        return {
          default_view: {
            greeting: 'Visual explanation',
            main_content: {
              content: content.explanation || content.answer || 'Visual explanation provided'
            }
          },
          progressive_sections: {},
          visual_sketch: content.visual_sketch,
          detected_subject: content.detected_subject || content.subject
        };
      }
      
      // Last resort: wrap the entire object
      return {
        default_view: {
          greeting: 'Response',
          main_content: {
            content: JSON.stringify(content)
          }
        },
        progressive_sections: {}
      };
    }
    
    // Fallback for any other type
    return {
      default_view: {
        greeting: 'Response',
        main_content: {
          content: String(content || 'No content available')
        }
      },
      progressive_sections: {}
    };
  };

  // Load session
  const loadSession = async (sessionId) => {
    try {
      setSessionLoadingId(sessionId);
      const res = await apiClient.get(`/ai/chat/${sessionId}/messages`);

      if (res.status === 200) {
        const data = res.data;
        const parsed = [];
        const ids = new Set();
        const list = Array.isArray(data.messages) ? data.messages : [];
        list.forEach(msg => {
          // Combined format: user_message + ai response fields
          if (msg.user_message) {
            const uid = (msg.message_id ? `${msg.message_id}_user` : `user_${Date.now()}_${crypto.randomUUID()}`);
            if (!ids.has(uid)) {
              // Ensure user content is always a string
              const userContent = typeof msg.user_message === 'string' 
                ? msg.user_message 
                : (msg.user_message?.message || String(msg.user_message));
              parsed.push({ 
                type: 'user', 
                content: userContent, 
                timestamp: msg.timestamp || new Date().toISOString(), 
                message_id: uid 
              });
              ids.add(uid);
            }
            const aiPayload = msg.dual_response || msg.response || msg.ai_response;
            if (aiPayload) {
              const aid = msg.message_id || `ai_${Date.now()}_${crypto.randomUUID()}`;
              if (!ids.has(aid)) {
                // CRITICAL: Normalize AI content to ensure it's always a proper object
                parsed.push({ 
                  type: 'ai', 
                  content: normalizeAIContent(aiPayload), 
                  timestamp: msg.timestamp || new Date().toISOString(), 
                  message_id: aid,
                  // Preserve additional fields
                  teaching_visual: msg.teaching_visual || aiPayload?.teaching_visual,
                  visual_data: msg.visual_data || aiPayload?.visual_data,
                  visual_sketch: msg.visual_sketch || aiPayload?.visual_sketch
                });
                ids.add(aid);
              }
            }
          } else if (msg.message && !msg.response && !msg.ai_response) {
            // Separate user message
            const uid = msg.message_id || `user_${Date.now()}_${crypto.randomUUID()}`;
            if (!ids.has(uid)) {
              const userContent = typeof msg.message === 'string' 
                ? msg.message 
                : String(msg.message);
              parsed.push({ 
                type: 'user', 
                content: userContent, 
                timestamp: msg.timestamp || new Date().toISOString(), 
                message_id: uid 
              });
              ids.add(uid);
            }
          } else if (msg.response || msg.ai_response) {
            // Separate AI response
              const aid = msg.message_id || `ai_${Date.now()}_${crypto.randomUUID()}`;
              if (!ids.has(aid)) {
              const aiPayload = msg.response || msg.ai_response;
              // CRITICAL: Normalize AI content to ensure it's always a proper object
              parsed.push({ 
                type: 'ai', 
                content: normalizeAIContent(aiPayload), 
                timestamp: msg.timestamp || new Date().toISOString(), 
                message_id: aid,
                // Preserve additional fields
                teaching_visual: msg.teaching_visual || aiPayload?.teaching_visual,
                visual_data: msg.visual_data || aiPayload?.visual_data,
                visual_sketch: msg.visual_sketch || aiPayload?.visual_sketch
              });
              ids.add(aid);
            }
          }
        });
        setMessages(parsed);
        setCurrentSession(sessionId);
        setShowSidebar(false);
        setHasInteraction(parsed.length > 0);
        setShowWelcome(parsed.length === 0);
        setMenuOpenId(null);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    } finally { setSessionLoadingId(null); }
  };

  // CRITICAL FIX: Restore session messages on mount if we have a persisted session
  // This ensures ChatGPT-style persistence when navigating away and back
  useEffect(() => {
    const restoreSession = async () => {
      const persistedSession = localStorage.getItem('dhruv_ai_current_session');
      if (persistedSession && messages.length === 0) {
        console.log('🔄 Restoring persisted session:', persistedSession);
        await loadSession(persistedSession);
      }
    };
    
    // Small delay to ensure loadSessions runs first
    const timeoutId = setTimeout(restoreSession, 100);
    return () => clearTimeout(timeoutId);
  }, []); // Run once on mount
  
  // Defer sessions load to next tick/idle to keep first paint fast
  useEffect(() => {
    let idleId = null;
    let timeoutId = null;
    const runner = () => loadSessions();
    if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
      // @ts-ignore
      idleId = window.requestIdleCallback(runner);
    } else {
      timeoutId = setTimeout(runner, 0);
    }
    return () => {
      if (idleId && typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
        // @ts-ignore
        window.cancelIdleCallback(idleId);
      }
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, []);

  // Close kebab on outside click
  useEffect(() => {
    const onDocClick = () => setMenuOpenId(null);
    window.addEventListener('click', onDocClick);
    return () => window.removeEventListener('click', onDocClick);
  }, []);

  // Close menu/dialog with Escape
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setMenuOpenId(null);
        setConfirmDlg({ open: false, title: '', message: '', onConfirm: null });
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* 🎮 GAMIFICATION: Micro-Reward Popup */}
      <MicroReward 
        reward={currentReward} 
        onComplete={dismissReward}
        autoHide={true}
        hideAfter={3000}
      />
      
      {/* 🎮 GAMIFICATION: Level Up Celebration */}
      {levelUp && (
        <LevelUpCelebration
          oldLevel={levelUp.old_level}
          newLevel={levelUp.new_level}
          onClose={dismissLevelUp}
        />
      )}
      
      {/* 🎮 GAMIFICATION: Streak Celebration */}
      {streakCelebration && (
        <StreakCelebration
          streakDays={streakCelebration.streakDays}
          badgeEarned={streakCelebration.badgeEarned}
        />
      )}
      
      {/* Offline Banner */}
      {!isOnline && (
        <motion.div
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-red-500 to-orange-500 text-white px-4 py-3 shadow-lg"
        >
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-3">
            <span className="text-xl">📡</span>
            <p className="font-semibold">You're offline. Messages will be queued until connection is restored.</p>
          </div>
        </motion.div>
      )}
      
      {/* Onboarding Tour for First-Time Users */}
      <OnboardingTour onComplete={() => {
        console.log('Onboarding completed');
        // Refresh user progress after onboarding
        loadUserProgress();
      }} />
      
      {/* Persistent Sidebar on large screens - PREMIUM DESIGN */}
      <div className="hidden lg:flex lg:flex-col lg:w-72 bg-gradient-to-b from-slate-50 to-white border-r border-slate-200/80">
        {/* Header with gradient accent */}
        <div className="p-4 border-b border-slate-200/60 bg-white/80 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-md shadow-violet-500/20">
                <MessageCircle className="h-4 w-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-800">Chats</h2>
                <p className="text-[10px] text-slate-500">{sessions.length} conversations</p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => loadSessions()}
              className="p-2 rounded-lg bg-slate-100 hover:bg-violet-100 text-slate-500 hover:text-violet-600 transition-all"
              title="Refresh chat history"
            >
              <RefreshCw className={sessionsLoading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
            </motion.button>
          </div>
        </div>
        
        {/* Chat list with custom scrollbar */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5" style={{ scrollbarWidth: 'thin', scrollbarColor: '#c4b5fd transparent' }}>
          {sessions.map((session, idx) => {
            const isActive = currentSession === session.session_id;
            const subjectColors = {
              'Mathematics': { bg: 'bg-purple-100', text: 'text-purple-700', icon: '📐' },
              'Physics': { bg: 'bg-blue-100', text: 'text-blue-700', icon: '⚛️' },
              'Chemistry': { bg: 'bg-orange-100', text: 'text-orange-700', icon: '🧪' },
              'Biology': { bg: 'bg-green-100', text: 'text-green-700', icon: '🧬' },
              'General': { bg: 'bg-slate-100', text: 'text-slate-600', icon: '💭' }
            };
            const subjectStyle = subjectColors[session.subject] || subjectColors['General'];
            
            return (
              <motion.div
                key={session.session_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: idx * 0.02 }}
                className={`group w-full rounded-xl transition-all duration-200 cursor-pointer ${
                  isActive 
                    ? 'bg-gradient-to-r from-violet-100 via-purple-50 to-violet-100 shadow-md shadow-violet-200/50 border-l-4 border-violet-500' 
                    : 'bg-white hover:bg-slate-50 border-l-4 border-transparent hover:border-violet-300 shadow-sm hover:shadow-md'
                }`}
              >
                <div className="flex items-start justify-between gap-2 p-3">
                  <button onClick={() => loadSession(session.session_id)} className="text-left flex-1 min-w-0">
                    {editing.id === session.session_id ? (
                      <div className="flex items-center gap-2">
                        <input
                          className="flex-1 text-sm border border-violet-300 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-violet-400"
                          value={editing.title}
                          onChange={(e) => setEditing(prev => ({ ...prev, title: e.target.value }))}
                          autoFocus
                          onClick={(e) => e.stopPropagation()}
                        />
                        <button title="Save" onClick={(e) => { e.stopPropagation(); commitInlineRename(session); }} className="p-1.5 bg-green-100 hover:bg-green-200 rounded-lg transition-colors"><Check className="h-3.5 w-3.5 text-green-700" /></button>
                        <button title="Cancel" onClick={(e) => { e.stopPropagation(); cancelInlineRename(); }} className="p-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"><X className="h-3.5 w-3.5 text-slate-600" /></button>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-center gap-1.5 mb-1.5">
                          <span className="text-sm">{subjectStyle.icon}</span>
                          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-md ${subjectStyle.bg} ${subjectStyle.text}`}>
                            {session.subject || 'General'}
                          </span>
                          {session.pinned && <span className="text-amber-500 text-xs">📌</span>}
                          {session.bookmarked && <span className="text-emerald-500 text-xs">🔖</span>}
                        </div>
                        <div className={`font-medium text-sm truncate ${isActive ? 'text-violet-900' : 'text-slate-800'}`} title={session.title || 'Untitled Chat'}>
                          {session.title || 'Untitled Chat'}
                        </div>
                        <div className="flex items-center gap-1.5 mt-1.5 text-[11px] text-slate-500">
                          {sessionLoadingId === session.session_id && <Loader className="h-3 w-3 animate-spin text-violet-500" />}
                          <span>{formatRelativeTime(session.last_updated || session.created_at)}</span>
                        </div>
                      </>
                    )}
                  </button>
                  <div className="relative">
                    <button
                      title="More"
                      onClick={(e) => { e.stopPropagation(); setMenuOpenId(prev => prev === session.session_id ? null : session.session_id); }}
                      className="p-1.5 hover:bg-slate-200/80 rounded-lg text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all"
                      aria-label="More options"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                    <AnimatePresence>
                    {menuOpenId === session.session_id && (
                      <motion.div
                        initial={{ opacity: 0, y: -4, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -4, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute right-0 mt-1 w-40 bg-white border border-slate-200 rounded-xl shadow-xl shadow-slate-200/50 z-20 overflow-hidden"
                      >
                        <button className="w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 flex items-center gap-2 transition-colors" onClick={(e) => { e.stopPropagation(); setEditing({ id: session.session_id, title: session.title || '' }); setMenuOpenId(null); }}>
                          <Edit2 className="h-3.5 w-3.5 text-slate-500" /> Rename
                        </button>
                        <button className="w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 flex items-center gap-2 transition-colors" onClick={(e) => { e.stopPropagation(); togglePinSession(session); setMenuOpenId(null); }}>
                          <Pin className="h-3.5 w-3.5 text-slate-500" /> {session.pinned ? 'Unpin' : 'Pin'}
                        </button>
                        <button className="w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 flex items-center gap-2 transition-colors" onClick={(e) => { e.stopPropagation(); toggleBookmarkSession(session); setMenuOpenId(null); }}>
                          <Bookmark className="h-3.5 w-3.5 text-slate-500" /> {session.bookmarked ? 'Unbookmark' : 'Bookmark'}
                        </button>
                        <div className="border-t border-slate-100" />
                        <button className="w-full text-left px-3 py-2.5 text-sm hover:bg-red-50 text-red-600 flex items-center gap-2 transition-colors" onClick={(e) => { e.stopPropagation(); requestDeleteSession(session); setMenuOpenId(null); }}>
                          <Trash2 className="h-3.5 w-3.5" /> Delete
                        </button>
                      </motion.div>
                    )}
                    </AnimatePresence>
                  </div>
                </div>
              </motion.div>
            );
          })}
          {sessions.length === 0 && !sessionsLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 text-gray-500"
            >
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="text-6xl mb-4"
              >
                📚
              </motion.div>
              <p className="text-lg font-bold text-gray-800 mb-2">Your learning journey starts here!</p>
              <p className="text-sm text-gray-600 mb-6">Ask your first question below to get started</p>
              
              <div className="grid grid-cols-3 gap-3 max-w-md mx-auto mt-4">
                <button
                  onClick={() => {
                    setInputMessage("Help me solve a math problem");
                    inputRef.current?.focus();
                  }}
                  className="p-4 bg-purple-50 hover:bg-purple-100 rounded-xl border-2 border-purple-200 transition-all hover:scale-105"
                >
                  <span className="text-3xl mb-2 block">🔢</span>
                  <span className="text-xs font-medium text-gray-700">Math Problem</span>
                </button>
                <button
                  onClick={() => {
                    setInputMessage("Explain a science concept");
                    inputRef.current?.focus();
                  }}
                  className="p-4 bg-blue-50 hover:bg-blue-100 rounded-xl border-2 border-blue-200 transition-all hover:scale-105"
                >
                  <span className="text-3xl mb-2 block">🔬</span>
                  <span className="text-xs font-medium text-gray-700">Science Question</span>
                </button>
                <button
                  onClick={() => {
                    setInputMessage("Help me prepare for exams");
                    inputRef.current?.focus();
                  }}
                  className="p-4 bg-green-50 hover:bg-green-100 rounded-xl border-2 border-green-200 transition-all hover:scale-105"
                >
                  <span className="text-3xl mb-2 block">📝</span>
                  <span className="text-xs font-medium text-gray-700">Exam Prep</span>
                </button>
              </div>
            </motion.div>
          )}
          {sessionsLoading && sessions.length === 0 && (
            <div className="space-y-3 p-2">
              {/* Skeleton loader for chat items */}
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-3 rounded-lg border border-gray-100 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="flex items-center justify-between">
                    <div className="h-3 bg-gray-100 rounded w-16" />
                    <div className="h-3 bg-gray-100 rounded w-12" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      {/* Overlay Sidebar - Chat History (mobile only) */}
      <div className="lg:hidden">
        <AnimatePresence>
          {showSidebar && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowSidebar(false)}
                className="fixed inset-0 bg-black/30 z-40 backdrop-blur-sm"
              />

              {/* Sidebar - Premium Glassmorphic Design */}
              <motion.div
                initial={{ x: -300 }}
                animate={{ x: 0 }}
                exit={{ x: -300 }}
                transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                className="fixed left-0 top-0 h-full w-72 bg-white/95 backdrop-blur-xl shadow-2xl z-50 p-5 overflow-y-auto border-r border-gray-100"
              >
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-violet-600" />
                    <h2 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">Chats</h2>
                  </div>
                  <div className="flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => loadSessions()}
                    className="text-xs px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white flex items-center gap-2 transition-all shadow-sm"
                    title="Refresh chat history"
                  >
                    <RefreshCw className={sessionsLoading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
                    <span className="font-semibold">Refresh</span>
                  </motion.button>
                    <button
                      onClick={() => setShowSidebar(false)}
                      className="p-2 hover:bg-gray-100 rounded-lg"
                    >
                      <ChevronLeft className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <button
                    onClick={() => loadSessions()}
                    className="w-full text-xs px-3 py-2 rounded-lg bg-purple-50 hover:bg-purple-100 border border-purple-200 text-purple-700 flex items-center justify-center gap-2 transition-all"
                    title="Refresh chat history"
                  >
                    <RefreshCw className={sessionsLoading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
                    <span className="font-medium">Refresh History</span>
                  </button>
                </div>
                <div className="space-y-2">
                  {sessions.map((session, idx) => (
                    <motion.div
                      key={session.session_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: idx * 0.05 }}
                      whileHover={{ x: 5 }}
                      className={`w-full p-4 rounded-xl border-2 transition-all cursor-pointer ${
                        currentSession === session.session_id 
                          ? 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-400 shadow-lg' 
                          : 'bg-white border-gray-200 hover:border-purple-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <button
                          onClick={() => loadSession(session.session_id)}
                          className="text-left flex-1"
                        >
<div 
                                            className="font-medium text-sm text-gray-900 truncate mb-1" 
                                            title={session.title || 'Untitled Chat'}
                                            style={{ maxWidth: '180px' }}
                                          >
                                            {session.title || 'Untitled Chat'}
                                          </div>
                                          <div className="flex items-center justify-between gap-2 text-xs text-gray-500">
                                            <span className="font-medium text-violet-600 bg-violet-50 px-1.5 py-0.5 rounded">{session.subject || 'General'}</span>
                                            <span className="flex items-center gap-1">
                                              {sessionLoadingId === session.session_id && <Loader className="h-3 w-3 animate-spin" />}
                                              {formatRelativeTime(session.created_at || session.updated_at)}
                                            </span>
                                          </div>
                        </button>
                        <div className="flex items-center gap-1">
                          <button title="Rename" onClick={(e) => { e.stopPropagation(); renameSession(session); }} className="p-1 hover:bg-gray-100 rounded"><Edit2 className="h-4 w-4" /></button>
                          <button title={session.pinned ? 'Unpin' : 'Pin'} onClick={(e) => { e.stopPropagation(); togglePinSession(session); }} className={`p-1 rounded ${session.pinned ? 'bg-yellow-100' : 'hover:bg-gray-100'}`}><Pin className="h-4 w-4" /></button>
                          <button title={session.bookmarked ? 'Unbookmark' : 'Bookmark'} onClick={(e) => { e.stopPropagation(); toggleBookmarkSession(session); }} className={`p-1 rounded ${session.bookmarked ? 'bg-green-100' : 'hover:bg-gray-100'}`}><Bookmark className="h-4 w-4" /></button>
                          <button title="Delete" onClick={(e) => { e.stopPropagation(); deleteSession(session); }} className="p-1 hover:bg-red-50 rounded"><Trash2 className="h-4 w-4 text-red-500" /></button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                  {sessions.length === 0 && !sessionsLoading && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-center py-12 text-gray-500"
                    >
                      <motion.div
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="text-6xl mb-4"
                      >
                        📚
                      </motion.div>
                      <p className="text-lg font-bold text-gray-800 mb-2">Your learning journey starts here!</p>
                      <p className="text-sm text-gray-600 mb-6">Ask your first question below to get started</p>
                      
                      <div className="grid grid-cols-3 gap-3 max-w-md mx-auto mt-4">
                        <button
                          onClick={() => {
                            setInputMessage("Help me solve a math problem");
                            setShowSidebar(false);
                            inputRef.current?.focus();
                          }}
                          className="p-4 bg-purple-50 hover:bg-purple-100 rounded-xl border-2 border-purple-200 transition-all hover:scale-105"
                        >
                          <span className="text-3xl mb-2 block">🔢</span>
                          <span className="text-xs font-medium text-gray-700">Math Problem</span>
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("Explain a science concept");
                            setShowSidebar(false);
                            inputRef.current?.focus();
                          }}
                          className="p-4 bg-blue-50 hover:bg-blue-100 rounded-xl border-2 border-blue-200 transition-all hover:scale-105"
                        >
                          <span className="text-3xl mb-2 block">🔬</span>
                          <span className="text-xs font-medium text-gray-700">Science Question</span>
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("Help me prepare for exams");
                            setShowSidebar(false);
                            inputRef.current?.focus();
                          }}
                          className="p-4 bg-green-50 hover:bg-green-100 rounded-xl border-2 border-green-200 transition-all hover:scale-105"
                        >
                          <span className="text-3xl mb-2 block">📝</span>
                          <span className="text-xs font-medium text-gray-700">Exam Prep</span>
                        </button>
                      </div>
                    </motion.div>
                  )}
                  {sessionsLoading && sessions.length === 0 && (
                    <div className="space-y-3 p-2">
                      {/* Skeleton loader for chat items */}
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="p-3 rounded-lg border border-gray-100 animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                          <div className="flex items-center justify-between">
                            <div className="h-3 bg-gray-100 rounded w-16" />
                            <div className="h-3 bg-gray-100 rounded w-12" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Mobile Navigation Section */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <SathiNavMenu compact={false} />
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header - Premium Glassmorphic Design */}
        <motion.div
          animate={{
            height: headerCollapsed ? '70px' : '110px'
          }}
          transition={{ duration: 0.3 }}
          className="bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm"
        >
          <div className="max-w-5xl mx-auto px-6 h-full flex flex-col justify-center py-3">
            {/* Top row - Always visible */}
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {/* Mobile: Chat history toggle */}
                <button
                  onClick={() => setShowSidebar(true)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden flex-shrink-0"
                >
                  <Menu className="h-6 w-6 text-gray-600" />
                </button>
                
                {/* Desktop: Integrated Navigation Menu */}
                <div className="hidden lg:block">
                  <SathiNavMenu />
                </div>
                
                {/* Logo & Brand - "Sathi" Identity - Premium Design */}
                <div className="flex items-center space-x-3 flex-shrink-0">
                  {/* Professional animated Sathi icon */}
                  <div className="relative">
                    <motion.div 
                      className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl blur-md opacity-40"
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    />
                    <div className="relative w-10 h-10 bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
                      <Brain className="w-5 h-5 text-white" />
                    </div>
                    {/* Online indicator with pulse */}
                    <motion.div 
                      className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-white shadow-sm"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                  
                  <div className="min-w-0">
                    <h1 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent tracking-tight">
                      Sathi
                    </h1>
                    <p className="text-[11px] text-gray-500 font-medium tracking-wide">AI Learning Assistant</p>
                  </div>
                </div>
              </div>

              {/* Stats Display - Clean & Professional */}
              <div className="flex items-center gap-3 ml-auto mr-4 flex-shrink-0">
                {/* Streak - Minimal design */}
                {currentStreak > 0 && (
                  <div 
                    className="flex items-center gap-1.5 px-2.5 py-1 bg-orange-50 border border-orange-200 rounded-lg"
                    title={`${currentStreak} day learning streak`}
                  >
                    <Flame className="w-4 h-4 text-orange-500" />
                    <span className="text-sm font-semibold text-orange-700">{currentStreak}</span>
                  </div>
                )}
                
                {/* XP - Minimal design */}
                <div 
                  className="flex items-center gap-1.5 px-2.5 py-1 bg-violet-50 border border-violet-200 rounded-lg"
                  title={`${currentXP || 0} experience points`}
                >
                  <Zap className="w-4 h-4 text-violet-500" />
                  <span className="text-sm font-semibold text-violet-700">{currentXP || 0}</span>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => {
                  startNewChat();
                  setShowWelcome(true);
                }}
                className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white rounded-xl flex items-center space-x-2 shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-200 flex-shrink-0 text-sm font-semibold"
              >
                <Plus className="h-4 w-4" />
                <span>New Chat</span>
              </motion.button>
            </div>

            {/* Expanded header content - Clean tagline */}
            {!headerCollapsed && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2"
              >
                <p className="text-sm text-gray-500 font-medium">
                  🤝 Your AI friend • 🎓 Verified explanations • 🎯 Exam-ready
                </p>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Chat Area - Scrollable container that fills available space */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto overflow-x-hidden"
          style={{ minHeight: 0 }}
        >
          <div className="max-w-4xl mx-auto px-4 py-6 min-h-full flex flex-col">
            {/* Welcome Screen - ULTRA PREMIUM STUDENT-CENTRIC DESIGN */}
            {showWelcome && messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-16 px-4 relative"
              >
                {/* Background gradient mesh effect */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                  <div className="absolute top-0 left-1/4 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl" />
                  <div className="absolute top-20 right-1/4 w-48 h-48 bg-pink-500/10 rounded-full blur-3xl" />
                  <div className="absolute bottom-20 left-1/3 w-56 h-56 bg-blue-500/8 rounded-full blur-3xl" />
                </div>

                {/* Premium Animated Logo - Sathi Identity */}
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', duration: 0.8, bounce: 0.4 }}
                  className="relative inline-block mb-10"
                >
                  {/* Animated outer glow */}
                  <motion.div 
                    className="absolute inset-0 bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 rounded-3xl blur-2xl"
                    animate={{ 
                      opacity: [0.3, 0.5, 0.3],
                      scale: [1.4, 1.6, 1.4]
                    }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  />
                  
                  {/* Main logo container with animated gradient */}
                  <div className="relative w-28 h-28 rounded-3xl shadow-2xl shadow-purple-500/40 overflow-hidden">
                    <motion.div
                      className="absolute inset-0"
                      style={{
                        background: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F97316 100%)',
                        backgroundSize: '200% 200%'
                      }}
                      animate={{
                        backgroundPosition: ['0% 0%', '100% 100%', '0% 0%']
                      }}
                      transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                    />
                    
                    {/* Glass overlay */}
                    <div className="absolute inset-0 bg-white/10 backdrop-blur-[1px]" />
                    
                    {/* Sparkle effects */}
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-0"
                    >
                      <Sparkles className="w-5 h-5 text-white/40 absolute top-3 right-3" />
                      <Sparkles className="w-4 h-4 text-white/30 absolute bottom-4 left-3" />
                    </motion.div>
                    
                    {/* Handshake emoji */}
                    <div className="relative w-full h-full flex items-center justify-center">
                      <motion.span
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="text-6xl"
                      >
                        🤝
                      </motion.span>
                    </div>
                  </div>
                  
                  {/* Online status with pulse */}
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -bottom-1 -right-1 w-7 h-7 bg-emerald-500 rounded-full border-4 border-white shadow-lg shadow-emerald-500/50 flex items-center justify-center"
                  >
                    <motion.div 
                      className="w-2.5 h-2.5 bg-white rounded-full"
                      animate={{ opacity: [1, 0.5, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  </motion.div>
                </motion.div>

                {/* Title with animated gradient */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mb-6"
                >
                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight">
                    <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
                      Hey! Ready to Learn?
                    </span>
                    <motion.span 
                      className="inline-block ml-2"
                      animate={{ rotate: [0, 14, -8, 14, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 3 }}
                    >
                      💪
                    </motion.span>
                  </h1>
                </motion.div>
                
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="text-lg md:text-xl text-gray-600 mb-4 font-medium max-w-lg mx-auto"
                >
                  Your AI friend who explains things in the coolest way!
                </motion.p>
                
                {/* Feature tags - Premium glass design */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="flex flex-wrap items-center justify-center gap-2 mb-12"
                >
                  {[
                    { icon: '🏏', text: 'Cricket analogies' },
                    { icon: '🎯', text: 'Real examples' },
                    { icon: '📝', text: 'Exam tips' },
                    { icon: '🗣️', text: 'Hinglish!' }
                  ].map((tag, i) => (
                    <motion.span
                      key={tag.text}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.6 + i * 0.1 }}
                      className="flex items-center gap-1.5 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 border border-gray-200/80 shadow-sm hover:shadow-md hover:border-violet-200 transition-all cursor-default"
                    >
                      <span>{tag.icon}</span>
                      <span>{tag.text}</span>
                    </motion.span>
                  ))}
                </motion.div>

                {/* Quick prompts - PREMIUM GLASSMORPHIC CARDS */}
                {defaultPrompts.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    {defaultPrompts.map((prompt, index) => {
                      const promptText = typeof prompt === 'string' ? prompt : prompt.text || prompt;
                      
                      // Premium icon and color schemes
                      const cardStyles = [
                        { icon: Book, gradient: 'from-blue-500 to-cyan-500', accent: 'text-blue-500', bg: 'hover:from-blue-50 hover:to-cyan-50' },
                        { icon: Brain, gradient: 'from-violet-500 to-purple-500', accent: 'text-violet-500', bg: 'hover:from-violet-50 hover:to-purple-50' },
                        { icon: Zap, gradient: 'from-orange-500 to-amber-500', accent: 'text-orange-500', bg: 'hover:from-orange-50 hover:to-amber-50' },
                        { icon: Trophy, gradient: 'from-emerald-500 to-teal-500', accent: 'text-emerald-500', bg: 'hover:from-emerald-50 hover:to-teal-50' }
                      ];
                      
                      const style = cardStyles[index % cardStyles.length];
                      const IconComponent = style.icon;
                      
                      return (
                        <motion.button
                          key={index}
                          initial={{ opacity: 0, y: 30, scale: 0.9 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          transition={{ 
                            delay: 0.7 + index * 0.1, 
                            type: 'spring', 
                            stiffness: 100 
                          }}
                          whileHover={{ scale: 1.03, y: -4 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => handleQuickSend(promptText)}
                          className={`group relative flex items-start gap-4 p-5 rounded-2xl text-left overflow-hidden transition-all duration-300 bg-white/80 backdrop-blur-sm border border-gray-200/80 shadow-sm hover:shadow-xl hover:border-transparent hover:bg-gradient-to-r ${style.bg}`}
                        >
                          {/* Accent line on hover */}
                          <motion.div
                            className={`absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b ${style.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
                          />
                          
                          {/* Icon container */}
                          <div className={`flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br ${style.gradient} flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300`}>
                            <IconComponent className="w-6 h-6 text-white" />
                          </div>
                          
                          {/* Text content */}
                          <div className="flex-1 min-w-0 pt-1">
                            <p className="text-sm font-medium text-gray-700 leading-relaxed group-hover:text-gray-900 transition-colors">
                              {promptText}
                            </p>
                          </div>
                          
                          {/* Arrow indicator */}
                          <motion.div className="flex-shrink-0 pt-1">
                            <ArrowRight className={`w-5 h-5 ${style.accent} opacity-40 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-300`} />
                          </motion.div>
                        </motion.button>
                      );
                    })}
                  </div>
                )}
                
                {/* Fun tagline */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.9 }}
                  className="mt-12 text-gray-400 text-sm"
                >
                  <p>Ask anything - I'll explain it like a friend! 💪</p>
                </motion.div>
              </motion.div>
            )}

            {/* Messages - Grows to fill available space */}
            <div className="space-y-6 flex-grow">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id || index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {message.type === 'user' && (
                      <div className="flex justify-end">
                        <motion.div
                          initial={{ opacity: 0, x: 10, scale: 0.95 }}
                          animate={{ opacity: 1, x: 0, scale: 1 }}
                          transition={{ type: "spring", stiffness: 300, damping: 25 }}
                          className="max-w-[75%] bg-gradient-to-br from-gray-900 to-gray-800 text-white rounded-2xl rounded-br-md px-5 py-3.5 shadow-lg shadow-gray-900/20"
                        >
                          {/* Show image if uploaded */}
                          {message.image_preview && (
                            <div className="mb-2 rounded-lg overflow-hidden border border-gray-700">
                              <img
                                src={message.image_preview}
                                alt="Uploaded"
                                className="max-w-full max-h-40 object-contain bg-gray-800"
                              />
                            </div>
                          )}
                          
                          <p className="text-sm leading-relaxed">
                            {(() => {
                              if (typeof message.content === 'string') return message.content;
                              if (typeof message.content === 'object' && message.content !== null) {
                                const question = message.content.message || 
                                                 message.content.text || 
                                                 message.content.query ||
                                                 message.content.question ||
                                                 message.content.user_message;
                                if (question && typeof question === 'string') return question;
                                if (message.content.default_view?.greeting) return message.content.default_view.greeting;
                              }
                              return message.user_question || 'Question';
                            })()}
                          </p>
                        </motion.div>
                      </div>
                    )}

                    {message.type === 'ai' && (() => {
                      return (
                      <div className="flex justify-start">
                        <div className="max-w-3xl w-full">
                          {/* Premium Response Container - Glassmorphic Design */}
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ type: "spring", stiffness: 200, damping: 20 }}
                            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg shadow-gray-200/40 border border-gray-100/80"
                          >
                            {/* Memory Context Banner - Shows learning progress */}
                            {message.content?.memory_context && (
                              <MemoryContextBanner memoryContext={message.content.memory_context} />
                            )}
                            
                            {/* Main Response - SMART ADAPTIVE RESPONSE (Like ChatGPT/Gemini) */}
                            <SmartResponse 
                              response={(() => {
                                // Content should already be normalized, but add safety check
                                let contentObj = message.content;
                                
                                // Double-check: if somehow content is still a string, normalize it
                                if (typeof contentObj === 'string') {
                                  contentObj = normalizeAIContent(contentObj);
                                }
                                
                                // Ensure contentObj is a valid object
                                if (typeof contentObj !== 'object' || contentObj === null || Array.isArray(contentObj)) {
                                  contentObj = normalizeAIContent(contentObj);
                                }
                                
                                // Ensure default_view exists
                                if (!contentObj.default_view) {
                                  contentObj = normalizeAIContent(contentObj);
                                }
                                
                                // Return response object with all necessary fields
                                return {
                                  ...contentObj,
                                  teaching_visual: message.teaching_visual || contentObj?.teaching_visual,
                                  visual_data: message.visual_data || contentObj?.visual_data,
                                  detected_subject: contentObj?.detected_subject || message.content?.detected_subject,
                                  visual_sketch: message.content?.visual_sketch || message.visual_sketch
                                };
                              })()}
                              visualSketch={message.content?.visual_sketch || message.visual_sketch}
                              question={message.user_question || ''}
                              whiteboardVisual={message.whiteboard_visual || message.content?.whiteboard_visual}
                              onFollowUp={(question) => {
                                if (question) {
                                  setInputMessage(question);
                                  inputRef.current?.focus();
                                  setTimeout(() => handleSend(), 100);
                                }
                              }}
                              onInteraction={(action, data) => {
                                console.log('User interaction:', action, data);
                                
                                // Handle share actions
                                if (action === 'share_whatsapp' || action === 'share_visual') {
                                  if (data?.text) {
                                    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(data.text)}`;
                                    window.open(whatsappUrl, '_blank');
                                    toastSuccess('Shared on WhatsApp!');
                                  }
                                }
                                
                                // Track feedback
                                if (action === 'feedback_positive' || action === 'feedback_negative') {
                                  console.log('Feedback:', action);
                                  toastSuccess(action === 'feedback_positive' ? 'Thanks for your feedback! 🙌' : 'We\'ll improve! 💪');
                                }
                              }}
                            />
                            
                            {/* Loading state for async visual generation */}
                            {message.visual_task_id && !(message.content?.visual_sketch?.svg || message.visual_sketch?.svg) && (
                              <div className="mt-4 p-3 bg-violet-50 rounded-lg">
                                <div className="flex items-center space-x-2">
                                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-violet-500 border-t-transparent"></div>
                                  <span className="text-sm text-violet-600">Generating visual...</span>
                                </div>
                              </div>
                            )}
                            
                            {/* Action Buttons - Copy & Feedback */}
                            <div className="mt-4 pt-3 border-t border-gray-100 flex items-center gap-1">
                              {/* Copy Button */}
                              <button
                                onClick={() => {
                                  const textContent = message.content?.default_view?.main_content?.content || 
                                                     message.content?.response || 
                                                     JSON.stringify(message.content);
                                  navigator.clipboard.writeText(textContent);
                                  toastSuccess('Copied!');
                                }}
                                className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all"
                                title="Copy response"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              </button>
                              
                              <div className="w-px h-4 bg-gray-200 mx-1" />
                              
                              {/* Thumbs Up */}
                              <button
                                onClick={() => {
                                  toastSuccess('Thanks for your feedback!');
                                  console.log('Positive feedback for message:', message.id);
                                }}
                                className="p-2 rounded-lg text-gray-400 hover:text-green-600 hover:bg-green-50 transition-all"
                                title="Good response"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                                </svg>
                              </button>
                              
                              {/* Thumbs Down */}
                              <button
                                onClick={() => {
                                  toastSuccess('We\'ll improve!');
                                  console.log('Negative feedback for message:', message.id);
                                }}
                                className="p-2 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all"
                                title="Needs improvement"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                                </svg>
                              </button>
                            </div>
                          </motion.div>
                        </div>
                      </div>
                    );
                    })()}

                    {message.type === 'error' && (
                      <div className="flex justify-center">
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="bg-red-50 border-2 border-red-200 text-red-700 rounded-xl px-6 py-5 max-w-2xl shadow-lg"
                        >
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                                <span className="text-xl">⚠️</span>
                              </div>
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium leading-relaxed">
                                {typeof message.content === 'string' 
                                  ? message.content 
                                  : (message.content?.message || String(message.content || 'An error occurred'))}
                              </p>
                              
                              {/* Retry Button */}
                              {message.canRetry && message.originalMessage && (
                                <motion.button
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                  onClick={() => handleRetry(message)}
                                  className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold flex items-center gap-2 transition-colors"
                                >
                                  <RefreshCw className="h-4 w-4" />
                                  Retry Message
                                </motion.button>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* AI Typing Indicator - Enhanced with tips */}
              {loading && (
                <TypingIndicator />
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        {/* Input Bar with Floating Suggestions - Premium Design */}
        <div className="border-t border-gray-100 bg-gradient-to-t from-gray-50/80 to-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            {/* Floating Follow-up Suggestions - Compact Horizontal Chips */}
            <AnimatePresence>
              {floatingFollowUps.length > 0 && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  transition={{ duration: 0.2 }}
                  className="mb-3"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-slate-500 mr-1">💡</span>
                    {floatingFollowUps.map((suggestion, idx) => {
                      const suggestionText = typeof suggestion === 'string' ? suggestion : suggestion.text || suggestion;
                      return (
                        <motion.button
                          key={idx}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: idx * 0.05 }}
                          whileHover={{ scale: 1.03, y: -1 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => {
                            setInputMessage(suggestionText);
                            setFloatingFollowUps([]);
                            inputRef.current?.focus();
                            setTimeout(() => handleSend(), 100);
                          }}
                          className="px-3 py-1.5 bg-white hover:bg-violet-50 border border-slate-200 hover:border-violet-400 rounded-full text-xs font-medium text-slate-700 hover:text-violet-700 transition-all shadow-sm hover:shadow-md"
                        >
                          {suggestionText}
                        </motion.button>
                      );
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* Image Preview */}
            {imagePreview && (
              <div className="mb-3 relative inline-block">
                <div className="relative rounded-xl overflow-hidden border-2 border-purple-300 shadow-md">
                  <img
                    src={imagePreview}
                    alt="Upload preview"
                    className="max-h-48 max-w-xs object-contain bg-gray-50"
                  />
                  <button
                    type="button"
                    onClick={handleRemoveImage}
                    className="absolute top-2 right-2 p-1.5 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg transition-colors"
                  >
                    <XCircle className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">📷 Image attached - AI will analyze it!</p>
              </div>
            )}
            
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="relative"
            >
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              
              {/* Main Input Container - Premium Glass Design */}
              <div className="flex items-end gap-2 bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200/80 focus-within:border-violet-400 focus-within:ring-4 focus-within:ring-violet-100/50 transition-all duration-300 p-2.5 shadow-lg shadow-gray-200/50 hover:shadow-xl hover:shadow-gray-200/60">
                {/* Image Attach Button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="flex-shrink-0 p-2 text-gray-400 hover:text-violet-600 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50"
                  title="Attach image"
                >
                  <ImageIcon className="w-5 h-5" />
                </button>
                
                {/* Textarea - Premium styling */}
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
                  className="flex-1 px-3 py-2.5 bg-transparent border-0 focus:ring-0 outline-none resize-none text-slate-800 dark:text-gray-100 placeholder-slate-400 dark:placeholder-gray-500 text-sm leading-relaxed max-h-[120px] font-medium"
                  rows="1"
                  disabled={loading}
                  style={{ 
                    minHeight: '44px',
                    height: 'auto',
                    maxHeight: '120px'
                  }}
                />

                {/* Dynamic Send/Stop Button */}
                <div className="flex-shrink-0">
                  {loading ? (
                    <motion.button
                      type="button"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        setLoading(false);
                        toastSuccess('Stopped');
                      }}
                      className="w-9 h-9 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all flex items-center justify-center"
                      title="Stop generating"
                    >
                      <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                        <rect x="6" y="6" width="12" height="12" rx="2" />
                      </svg>
                    </motion.button>
                  ) : (
                    <motion.button
                      type="submit"
                      disabled={!inputMessage.trim() && !selectedImage}
                      whileHover={{ scale: inputMessage.trim() || selectedImage ? 1.05 : 1 }}
                      whileTap={{ scale: inputMessage.trim() || selectedImage ? 0.95 : 1 }}
                      className={`w-10 h-10 rounded-xl transition-all duration-200 flex items-center justify-center ${
                        inputMessage.trim() || selectedImage
                          ? 'bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      }`}
                      title="Send message"
                    >
                      <Send className="h-4 w-4" />
                    </motion.button>
                  )}
                </div>
              </div>
              
              {/* Helper Text - Clean Design */}
              <div className="flex items-center justify-between mt-2 px-1">
                <p className="text-xs text-slate-500 font-medium">
                  Press <kbd className="px-1.5 py-0.5 bg-slate-100 rounded-md text-slate-600 font-mono text-[10px] border border-slate-200">Enter</kbd> to send
                </p>
                {/* Neural processing indicator in helper area */}
                {loading && (
                  <div className="flex items-center gap-2">
                    <NeuralThinkingIndicator isLoading={true} variant="subtle" />
                  </div>
                )}
              </div>
            </form>
          </div>
        </div>

        {/* Mobile FAB - New Chat */}
        <button
          onClick={startNewChat}
          className="lg:hidden fixed bottom-24 right-6 w-14 h-14 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-full shadow-2xl flex items-center justify-center z-30 hover:scale-110 transition-transform"
        >
          <Plus className="h-6 w-6" />
        </button>
      </div>

      {/* Upgrade Modal */}
      {showUpgradeModal && upgradeModalData && (
        <UpgradeModal
          isOpen={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
          upgradeHint={upgradeModalData}
        />
      )}

      {/* Confirm Dialog */}
      {confirmDlg.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setConfirmDlg({ open: false, title: '', message: '', onConfirm: null })} />
          <div className="relative bg-white rounded-xl shadow-2xl border border-gray-200 w-[92%] max-w-sm p-5">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{confirmDlg.title}</h3>
            <p className="text-sm text-gray-600 mb-4">{confirmDlg.message}</p>
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setConfirmDlg({ open: false, title: '', message: '', onConfirm: null })}
                className="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDlg.onConfirm && confirmDlg.onConfirm()}
                className="px-3 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}







