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
  Trophy,
  Search,
  Pencil,
  Mic,  // 🎙️ Voice input icon
  MicOff  // 🎙️ Mic off icon
} from 'lucide-react';
import NeuroSymbolicResponse from './neuro-symbolic/NeuroSymbolicResponse';
import MentorResponseV2 from './mentor-v2/MentorResponseV2';
import SmartResponse from './SmartResponse';
import UpgradeModal from './UpgradeModal';
import OnboardingTour from './OnboardingTour';
import apiClient from '../api/client';
import '../styles/ai-tutor-redesign.css'; // Shared scroll stability styles
import '../styles/sathi-premium.css'; // Premium Sathi UI redesign
import '../styles/sathi-premium-v2.css'; // Neural Premium Theme
import '../styles/sathi-ux-audit-fixes.css'; // UI/UX Audit Permanent Fixes
import '../styles/ui-comprehensive-fixes.css'; // Comprehensive UI/UX Fixes - ALL ISSUES
import '../styles/classroom-layout.css'; // Digital Classroom Layout

// 🎙️ Voice Input Hook
import { useVoiceInput } from '../hooks/useVoiceInput';

// Premium Welcome Component - Neural AI Interface
import PremiumWelcome from './chat/PremiumWelcome';

// V1 Enhancement Components
import VisualSketchViewer from './visual/VisualSketchViewer';
import SubjectBadge from './visual/SubjectBadge';
import FollowUpQuestions from './visual/FollowUpQuestions';
import ShareButtons from './visual/ShareButtons';
import MemoryContextBanner from './MemoryContextBanner';

// Sathi Navigation Menu - Integrated nav for full-screen chat experience
import SathiNavMenu from './chat/SathiNavMenu';

// 🔔 Notification Bell - CRITICAL for reminders to work!
import NotificationBell from './NotificationBell';

// 🏫 Digital Classroom Layout - NEW UI (uses HistorySidebar internally)
import ClassroomLayout from './layout/ClassroomLayout';
import SmartBoard from './visuals/SmartBoard';

// Gamification Components
import MicroReward, { LevelUpCelebration, StreakCelebration } from './gamification/MicroReward';
import { useGamification } from '../hooks/useGamification';

// Neural Thinking Indicator - Minimal, premium cognitive processing animation
import { NeuralThinkingIndicator } from './chat/NeuralThinkingIndicator';

// New UI Components - Comprehensive Fixes
import FeedbackToast, { useFeedbackToast } from './ui/FeedbackToast';
import FloatingFollowUps from './ui/FloatingFollowUps';
import useKeyboardShortcuts, { ShortcutsHelpPanel } from '../hooks/useKeyboardShortcuts';
import MasteryIndicator from './ui/MasteryIndicator';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Helper: Format sessions for ClassroomLayout's HistorySidebar
const formatSessionsForSidebar = (sessions) => {
  return sessions.map(session => ({
    id: session.session_id,
    title: session.title || 'New Chat',
    subject: session.subject || 'General',
    date: session.last_updated || session.created_at,
    updatedAt: session.last_updated,
    createdAt: session.created_at,
    isPinned: session.pinned || false
  }));
};

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

// ============================================================================
// CRITICAL: Response Sanitization Helpers
// These prevent internal agent traces from ever showing in the UI
// ============================================================================

/**
 * Deep extract text content from any nested object structure
 * NEVER returns JSON - always extracts actual text
 */
const deepExtractTextContent = (obj, maxDepth = 5) => {
  if (!obj || maxDepth <= 0) return '';
  
  // If it's already a string, return it
  if (typeof obj === 'string') return obj;
  
  // If it's not an object, stringify safely
  if (typeof obj !== 'object' || Array.isArray(obj)) {
    return Array.isArray(obj) ? obj.filter(s => typeof s === 'string').join('\n') : '';
  }
  
  // Priority order for content extraction
  const contentPaths = [
    ['default_view', 'main_content', 'content'],
    ['response', 'default_view', 'main_content', 'content'],
    ['progressive_sections', 'explanation'],
    ['main_response'],
    ['content'],
    ['explanation'],
    ['answer'],
    ['text'],
    ['message'],
  ];
  
  for (const path of contentPaths) {
    let value = obj;
    for (const key of path) {
      value = value?.[key];
      if (value === undefined) break;
    }
    if (typeof value === 'string' && value.length > 10) {
      return value;
    }
  }
  
  // Recursively search all string values
  for (const key of Object.keys(obj)) {
    // Skip internal/trace keys
    if (['thought', 'action', 'action_input', 'reasoning_chain', '_debug', '_trace'].includes(key)) {
      continue;
    }
    const value = obj[key];
    if (typeof value === 'string' && value.length > 50) {
      return value;
    }
    if (typeof value === 'object' && value !== null) {
      const extracted = deepExtractTextContent(value, maxDepth - 1);
      if (extracted && extracted.length > 50) {
        return extracted;
      }
    }
  }
  
  return '';
};

/**
 * Sanitize response text to remove any internal traces
 * Uses structural detection - not keyword matching
 * 
 * CRITICAL: This is the FINAL sanitization before content reaches the UI.
 * Must catch any JSON blocks containing internal trace keys at:
 * - START of response
 * - END of response (most common leak point!)
 * - MIDDLE of response
 */
const sanitizeResponseText = (text) => {
  if (!text || typeof text !== 'string') return text || '';
  
  // Internal keys that indicate trace/debug data that should NEVER be shown
  const INTERNAL_KEYS = [
    'thought', 'action', 'action_input', 'confidence', 'observation', 'step',
    'hybrid_reasoning', 'orchestration', 'routing_decision', 'symbolic_proof',
    'reasoning_chain', 'verification_passed', 'graph_context', 'pipeline'
  ];
  
  // Remove any JSON blocks that contain internal trace keys
  // Pattern: { ... "thought" ... } or { ... "confidence" ... } etc.
  const internalKeyPattern = INTERNAL_KEYS.map(k => `"${k}"`).join('|');
  const jsonBlockPattern = new RegExp(`\\{[^{}]*(?:${internalKeyPattern})[^{}]*\\}`, 'gi');
  let cleaned = text.replace(jsonBlockPattern, '');
  
  // CRITICAL: Remove JSON blocks at END of response (common leak point!)
  // Pattern: content ends with { ... } after normal text
  // Look for JSON starting after a complete sentence (period, newline, etc.)
  const endJsonPattern = /[\.\!\?\n]\s*\{[\s\S]*$/g;
  const endMatch = cleaned.match(endJsonPattern);
  if (endMatch) {
    const potentialJson = endMatch[0].substring(endMatch[0].indexOf('{'));
    // Check if it looks like internal JSON (has internal keys or starts with "conf", "hyb", etc.)
    const looksInternal = INTERNAL_KEYS.some(key => 
      potentialJson.toLowerCase().includes(`"${key}"`) || 
      potentialJson.toLowerCase().includes(`"${key.substring(0, 4)}`)
    ) || potentialJson.match(/^\s*\{\s*\n\s*"/);
    
    if (looksInternal) {
      cleaned = cleaned.replace(endJsonPattern, (m) => m[0]); // Keep just the punctuation
    }
  }
  
  // Remove any multi-line JSON-like blocks at START of response
  if (cleaned.trim().startsWith('{')) {
    let depth = 0;
    let endIndex = -1;
    for (let i = 0; i < cleaned.length; i++) {
      if (cleaned[i] === '{') depth++;
      else if (cleaned[i] === '}') {
        depth--;
        if (depth === 0) {
          endIndex = i + 1;
          break;
        }
      }
    }
    if (endIndex > 0 && endIndex < cleaned.length * 0.5) {
      const potentialJson = cleaned.substring(0, endIndex);
      if (INTERNAL_KEYS.some(key => potentialJson.toLowerCase().includes(`"${key}"`))) {
        cleaned = cleaned.substring(endIndex).trim();
      }
    }
  }
  
  // Remove ReAct-style patterns: "Thought: ...", "Action: ...", "Observation: ..."
  const reactPattern = /^(Thought|Action|Observation|Action Input|Step \d+):\s*[^\n]+$/gim;
  cleaned = cleaned.replace(reactPattern, '');
  
  // Remove standalone trace lines
  const traceLinePattern = /^\s*"(?:thought|action|action_input|confidence)":\s*[^\n]+$/gim;
  cleaned = cleaned.replace(traceLinePattern, '');
  
  // Remove incomplete JSON at end (common symptom: response ends with { or {"conf)
  // This catches cases where JSON started rendering but was truncated
  cleaned = cleaned.replace(/\s*\{\s*"?[a-z_]*"?\s*:?\s*$/i, '');
  cleaned = cleaned.replace(/\s*\{\s*$/i, '');
  
  // Remove JSON fragments at end like "}, or "], 
  cleaned = cleaned.replace(/["']?\s*\}\s*,?\s*$/g, '');
  cleaned = cleaned.replace(/["']?\s*\]\s*,?\s*$/g, '');
  
  // ================================================================
  // LATEX/MATH FORMATTING - Critical for student readability
  // ================================================================
  // Remove LONE BACKSLASH lines (these break visual flow)
  cleaned = cleaned.replace(/^\s*\\+\s*$/gm, '');
  cleaned = cleaned.replace(/\\\s*\n\s*\n/g, '\n\n');
  
  // Normalize LaTeX delimiters for KaTeX/MathJax rendering
  // Convert \[ ... \] to $$ ... $$ (block math)
  cleaned = cleaned.replace(/\\\[\s*/g, '\n$$');
  cleaned = cleaned.replace(/\s*\\\]/g, '$$\n');
  
  // Convert \( ... \) to $ ... $ (inline math)
  cleaned = cleaned.replace(/\\\(\s*/g, '$');
  cleaned = cleaned.replace(/\s*\\\)/g, '$');
  
  // Fix double-escaped backslashes in LaTeX (\\int → \int)
  cleaned = cleaned.replace(/\$\$([^$]+)\$\$/g, (match, content) => {
    return '$$' + content.replace(/\\\\([a-zA-Z]+)/g, '\\$1') + '$$';
  });
  
  // Clean up excessive newlines
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
  
  // Remove leading/trailing stray braces or backslashes that are orphaned
  cleaned = cleaned.replace(/^\s*[\{\}\\]+\s*$/gm, '');
  cleaned = cleaned.replace(/^\s*\{\s*\n\s*\\/gm, '');
  
  // Remove trailing commas, quotes, braces at very end
  cleaned = cleaned.replace(/[,"\'\}\]]+\s*$/g, '');
  
  return cleaned.trim();
};

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

  // 🎨 FEEDBACK TOAST - Show confirmation on feedback
  const { toastState: feedbackToastState, showFeedbackToast, hideFeedbackToast } = useFeedbackToast();

  // ⌨️ KEYBOARD SHORTCUTS - Global shortcuts for efficiency
  const { showShortcutsHelp, setShowShortcutsHelp } = useKeyboardShortcuts({
    onNewChat: () => handleNewChat(),
    onFocusInput: () => inputRef.current?.focus(),
    onToggleSidebar: () => setShowSidebar(prev => !prev),
    onSearch: () => {
      const searchInput = document.querySelector('[data-search-input]');
      searchInput?.focus();
    },
    onStopGeneration: () => {
      // Stop generation if streaming is active
      if (loading && apiAbortControllerRef.current) {
        handleStopGeneration();
      }
    },
    onEscape: () => {
      setShowUpgradeModal(false);
      setShowSidebar(false);
    }
  }, true);

  // 📡 OFFLINE DETECTION - Network status monitoring
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  // Visual polling abort controller ref
  const visualPollingAbortRef = useRef(null);
  
  // Main API request abort controller ref (for Stop button)
  const apiAbortControllerRef = useRef(null);
  const [isGeneratingVisual, setIsGeneratingVisual] = useState(false);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      // Cleanup any pending visual polling on unmount
      if (visualPollingAbortRef.current) {
        visualPollingAbortRef.current.abort();
      }
    };
  }, []);
  
  // Cancel visual generation
  const cancelVisualGeneration = useCallback(() => {
    if (visualPollingAbortRef.current) {
      visualPollingAbortRef.current.abort();
      visualPollingAbortRef.current = null;
    }
    setIsGeneratingVisual(false);
  }, []);

  // Core state
  const [messages, setMessages] = useState([]);
  
  // Follow-up suggestions (shown near input, not in response)
  const [floatingFollowUps, setFloatingFollowUps] = useState([]);
  
  // Poll for async visual generation with abort support
  const pollForVisual = async (taskId, messageId, retries = 0) => {
    const maxRetries = 30; // 30 seconds max (1s intervals)
    
    // Check if aborted
    if (visualPollingAbortRef.current?.signal?.aborted) {
      console.log('Visual polling cancelled by user');
      setIsGeneratingVisual(false);
      return;
    }
    
    if (retries >= maxRetries) {
      console.log('Visual generation timeout');
      setIsGeneratingVisual(false);
      return;
    }
    
    // Set generating state on first call
    if (retries === 0) {
      setIsGeneratingVisual(true);
      visualPollingAbortRef.current = new AbortController();
    }
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/ai/visual/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        signal: visualPollingAbortRef.current?.signal
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.status === 'completed' && data.visual_sketch) {
          // Debug: Log visual data structure
          console.log('🎨 Visual data received:', {
            hasSvg: !!data.visual_sketch?.svg,
            svgLength: data.visual_sketch?.svg?.length || 0,
            metaphors: data.visual_sketch?.metaphors,
            structure: Object.keys(data.visual_sketch || {}),
            blueprint: data.visual_sketch?.blueprint,
            template: data.visual_sketch?.template,
            mode: data.visual_sketch?.mode
          });
          
          // Ensure visual_sketch has proper structure
          const visualSketch = data.visual_sketch?.svg 
            ? data.visual_sketch  // Already has svg property
            : { svg: data.visual_sketch?.svg || '', ...data.visual_sketch }; // Ensure svg property exists
          
          // Update message with visual - CRITICAL: Preserve normalized structure
          // Also extract concept/subject from message for SmartBoard
          setMessages(prev => {
            const message = prev.find(m => m.message_id === messageId);
            
            // 🏫 CRITICAL: Update visualArtifact for SmartBoard
            // Extract concept and subject from the message
            const concept = visualSketch.concept || 
                           message?.concept ||
                           message?.user_question?.split(' ').slice(0, 3).join(' ') ||
                           'Concept';
            
            const subject = visualSketch.subject || 
                           message?.subject ||
                           data.detected_subject ||
                           'General';
            
            setVisualArtifact({
              ...visualSketch,
              concept,
              subject,
              // Preserve all visual formats
              svg: visualSketch.svg,
              blueprint: visualSketch.blueprint || data.visual_sketch?.blueprint,
              template: visualSketch.template || data.visual_sketch?.template,
              mode: visualSketch.mode || data.visual_sketch?.mode,
              visual_sketch: visualSketch,
              // Store original question for context-aware theming
              originalQuestion: message?.user_question || '',
            });
            
            return prev.map(msg => {
              if (msg.message_id === messageId) {
                // Ensure content is normalized before updating
                let normalizedContent = msg.content;
                if (typeof normalizedContent === 'string') {
                  normalizedContent = normalizeAIContent(normalizedContent);
                } else if (!normalizedContent || typeof normalizedContent !== 'object' || Array.isArray(normalizedContent)) {
                  normalizedContent = normalizeAIContent(normalizedContent);
                }
                
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
            });
          });
          console.log('✅ Visual loaded successfully and SmartBoard updated');
          setIsGeneratingVisual(false);
        } else if (data.status === 'generating') {
          // Continue polling
          setTimeout(() => pollForVisual(taskId, messageId, retries + 1), 1000);
        } else if (data.status === 'failed') {
          console.log('Visual generation failed:', data.error);
          setIsGeneratingVisual(false);
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Visual polling aborted');
        setIsGeneratingVisual(false);
        return;
      }
      console.error('Error polling for visual:', error);
      // Retry on error
      if (retries < maxRetries) {
        setTimeout(() => pollForVisual(taskId, messageId, retries + 1), 1000);
      } else {
        setIsGeneratingVisual(false);
      }
    }
  };
  const [inputMessage, setInputMessageRaw] = useState('');
  
  // 🛡️ GUARD: Ref to track if input was cleared by explicit user send
  // This prevents any race conditions or effects from accidentally clearing input
  const inputClearedByUserRef = useRef(false);
  const lastUserInputRef = useRef(''); // Track last typed value for debugging
  
  // Protected setInputMessage - logs any suspicious clears
  // ENHANCED: Track more context to debug input disappearing issue
  // NOTE: loadingRef is updated after loading state is declared (see below)
  const loadingRef = useRef(false);
  
  const setInputMessage = useCallback((newValue) => {
    const prevValue = lastUserInputRef.current;
    const timestamp = new Date().toISOString().substring(11, 23);
    
    // If clearing input and it wasn't from a user send, log warning
    if (newValue === '' && prevValue.length > 0 && !inputClearedByUserRef.current) {
      console.warn('⚠️ INPUT CLEAR DETECTED (not from send):', {
        timestamp,
        prevValue: prevValue.substring(0, 50),
        newValue: '(empty)',
        wasLoading: loadingRef.current,
        stack: new Error().stack?.split('\n').slice(1, 5).join('\n')
      });
    }
    
    // Log ANY change to input (not just clears) - helps trace the issue
    // Only log if value actually changes to reduce noise
    if (newValue !== prevValue) {
      console.log(`📝 INPUT CHANGE [${timestamp}]:`, {
        from: prevValue.length > 20 ? prevValue.substring(0, 20) + '...' : prevValue || '(empty)',
        to: newValue.length > 20 ? newValue.substring(0, 20) + '...' : newValue || '(empty)',
        intentional: inputClearedByUserRef.current
      });
    }
    
    // Reset the flag after any clear
    if (newValue === '') {
      inputClearedByUserRef.current = false;
    }
    
    // Track for next comparison
    if (newValue !== '') {
      lastUserInputRef.current = newValue;
    }
    
    setInputMessageRaw(newValue);
  }, []);
  const [loading, setLoading] = useState(false);
  loadingRef.current = loading; // Keep ref in sync for logging
  
  // 🎙️ VOICE INPUT INTEGRATION (ENHANCED)
  // Now includes: multi-language, audio feedback, confidence tracking, auto-retry
  const {
    isListening,
    transcript,
    interimTranscript,
    error: voiceError,
    isSupported: isVoiceSupported,
    startListening,
    stopListening,
    toggleListening,
    clearTranscript,
    clearError: clearVoiceError,
    // New features from enhanced hook
    language: voiceLanguage,
    supportedLanguages,
    changeLanguage,
    audioLevel,
    isLowVolume,
    confidence: voiceConfidence,
    getConfidenceStatus,
  } = useVoiceInput({ language: 'en-IN' }); // Default to Indian English
  
  // Track last applied transcript to prevent re-applying stale values
  const lastAppliedTranscriptRef = useRef('');
  
  // AUTO-POPULATE: Update input when voice transcript changes
  // FIX: Only apply if actively listening OR transcript is genuinely new
  useEffect(() => {
    if (transcript && transcript.trim()) {
      // Only apply if:
      // 1. User is actively listening (real-time updates), OR
      // 2. Transcript is different from last applied (prevents stale re-application)
      const isNewTranscript = transcript !== lastAppliedTranscriptRef.current;
      
      if (isListening || isNewTranscript) {
        console.log('🎙️ Voice transcript updated:', transcript.substring(0, 50));
        setInputMessage(transcript);
        lastAppliedTranscriptRef.current = transcript;
      }
    }
  }, [transcript, isListening]);
  
  // VOICE ERROR HANDLING: Show toast when voice error occurs (with auto-recovery message)
  useEffect(() => {
    if (voiceError) {
      // Don't show toast for auto-retry messages
      if (voiceError.includes('Retrying')) {
        console.log('🔄 Voice auto-retrying...');
        return;
      }
      toastError('Voice Input', voiceError);
      // Auto-clear error after showing
      setTimeout(() => clearVoiceError(), 4000);
    }
  }, [voiceError, toastError, clearVoiceError]);
  
  // LOW VOLUME WARNING: Alert user when mic level is too low
  useEffect(() => {
    if (isLowVolume && isListening) {
      // Only show once per listening session
      const key = 'lowVolumeWarned';
      if (!sessionStorage.getItem(key)) {
        toastError('Low Volume', 'Speak louder or move closer to your microphone');
        sessionStorage.setItem(key, 'true');
      }
    } else if (!isListening) {
      sessionStorage.removeItem('lowVolumeWarned');
    }
  }, [isLowVolume, isListening, toastError]);
  
  // 🎙️ Voice Input Handlers (Enhanced)
  const handleVoiceToggle = useCallback(() => {
    if (!isVoiceSupported) {
      toastError('Not Supported', 'Voice input requires Chrome, Edge, or Safari. You can still type your question!');
      return;
    }
    
    if (isListening) {
      console.log('🎙️ User clicked stop');
      stopListening();
      // Final transcript already applied via useEffect
      toastSuccess('Voice Captured', 'Your message is ready to send');
    } else {
      // Clear previous transcript before starting
      console.log('🎙️ User clicked start');
      clearTranscript();
      startListening();
      toastSuccess('Listening...', `Speak now in ${supportedLanguages[voiceLanguage]?.name || 'English'} 🎤`);
    }
  }, [isVoiceSupported, isListening, stopListening, startListening, clearTranscript, 
      toastSuccess, toastError, voiceLanguage, supportedLanguages]);
  
  // 🌐 Language Change Handler
  const handleVoiceLanguageChange = useCallback((newLang) => {
    changeLanguage(newLang);
    toastSuccess('Language Changed', `Voice input set to ${supportedLanguages[newLang]?.name}`);
  }, [changeLanguage, supportedLanguages, toastSuccess]);
  
  // DEBUG: Track inputMessage changes (REDUCED LOGGING)
  useEffect(() => {
    // Only log if input is significant (not every single character)
    if (inputMessage.length % 10 === 0 || inputMessage.length < 5) {
      console.log('📝 INPUT STATE:', inputMessage.substring(0, 50) + (inputMessage.length > 50 ? '...' : ''));
    }
  }, [inputMessage]);
  
  // CRITICAL FIX: Persist currentSession to localStorage for ChatGPT-style persistence
  const [currentSession, setCurrentSessionState] = useState(() => {
    // Initialize from localStorage on mount with try-catch for quota errors
    try {
      if (typeof window !== 'undefined') {
        return localStorage.getItem('dhruv_ai_current_session') || null;
      }
    } catch (error) {
      console.warn('Failed to read from localStorage:', error);
    }
    return null;
  });
  
  // Wrapper to persist session changes to localStorage with error handling
  const setCurrentSession = useCallback((sessionId) => {
    setCurrentSessionState(sessionId);
    try {
      if (typeof window !== 'undefined') {
        if (sessionId) {
          localStorage.setItem('dhruv_ai_current_session', sessionId);
        } else {
          localStorage.removeItem('dhruv_ai_current_session');
        }
      }
    } catch (error) {
      // Handle localStorage quota exceeded or other errors gracefully
      console.warn('Failed to persist session to localStorage:', error);
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
  
  // Search in chat history
  const [searchQuery, setSearchQuery] = useState('');
  
  // 🏫 Digital Classroom Layout state
  const [visualArtifact, setVisualArtifact] = useState(null);
  const [useClassroomLayout] = useState(true); // Use new ClassroomLayout UI
  const [currentUserQuestion, setCurrentUserQuestion] = useState(null); // Current question for fallback
  
  // Format sessions for ClassroomLayout's HistorySidebar
  const formattedChatHistory = formatSessionsForSidebar(sessions);
  
  // Header actions for ClassroomLayout
  const headerRightActions = (
    <>
      <NotificationBell 
        onStartStudy={(topic) => {
          setInputMessage(`Let's study ${topic}!`);
          inputRef.current?.focus();
        }}
      />
    </>
  );
  
  // Message editing state
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editingMessageContent, setEditingMessageContent] = useState('');
  
  // Messages loading state (for session load)
  const [messagesLoading, setMessagesLoading] = useState(false);
  
  // User mastery state (from backend memory system)
  const [userMastery, setUserMastery] = useState({
    subjects: {},
    weakAreas: [],
    recentTopics: []
  });

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
  
  // Ref to always have latest handleSend (initialized after handleSend is defined)
  const handleSendRef = useRef(null);
  
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
  
  // AUTO-SAVE DRAFT: Save input to localStorage as user types
  useEffect(() => {
    // Debounced save (only save after 500ms of no typing)
    const timeoutId = setTimeout(() => {
      // CRITICAL FIX: Don't save draft when loading (prevents overwriting user's new input during AI response)
      if (loading) return;
      
      if (inputMessage.trim()) {
        localStorage.setItem('sathi_draft_message', inputMessage);
        localStorage.setItem('sathi_draft_session', currentSession || '');
      } else {
        localStorage.removeItem('sathi_draft_message');
        localStorage.removeItem('sathi_draft_session');
      }
    }, 500);
    
    return () => clearTimeout(timeoutId);
  }, [inputMessage, currentSession, loading]);
  
  // RESTORE DRAFT: Load saved draft on mount
  // CRITICAL FIX: Use ref to prevent re-restoration and race conditions
  // Also check messages.length to ensure we don't restore draft in active chat
  const draftRestoredRef = useRef(false);
  useEffect(() => {
    // Only restore once per component lifecycle and only if no messages yet
    if (draftRestoredRef.current || messages.length > 0) return;
    
    const savedDraft = localStorage.getItem('sathi_draft_message');
    const savedSession = localStorage.getItem('sathi_draft_session');
    
    if (savedDraft) {
      // Only restore if we're in the same session or no session
      if (!savedSession || savedSession === currentSession || !currentSession) {
        setInputMessage(savedDraft);
        draftRestoredRef.current = true;
        // Show toast that draft was restored
        if (savedDraft.length > 10) {
          toastSuccess('Draft restored', 'Your unsent message was restored 📝');
        }
      }
    }
    // Only run once on mount - intentionally empty dependency array
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
    console.log('🧹 handleSend CLEARING input, was:', messageToSend);
    inputClearedByUserRef.current = true; // 🛡️ Mark as intentional clear
    setInputMessage('');
    // 🛡️ FIX: Clear voice transcript tracking to prevent ghost re-population
    lastAppliedTranscriptRef.current = '';
    if (typeof clearTranscript === 'function') clearTranscript();
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
    
    // 🎨 NEW: Set visual loading state for SmartBoard (optimistic loading)
    setIsGeneratingVisual(true);
    setCurrentUserQuestion(messageToSend);

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
      // ✅ ENABLED: Backend streaming endpoint is fully implemented
      // Features: <2s first token, graceful fallback, image support
      const USE_STREAMING = true; // Feature flag for streaming - NOW ENABLED ✅
      
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
        
        // Create AbortController for this request (allows Stop button to cancel)
        apiAbortControllerRef.current = new AbortController();
        
        try {
          // Use streaming endpoint with abort signal
          const response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(requestBody),
            signal: apiAbortControllerRef.current.signal
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let accumulatedText = '';
          let finalResponse = null;
          
          while (true) {
            // Check if aborted before reading
            if (apiAbortControllerRef.current?.signal?.aborted) {
              break;
            }
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
            // Update final message with COGNITO-OS transparency data
            const normalizedFinal = normalizeAIContent(finalResponse);
            setMessages(prev => prev.map(msg => 
              msg.message_id === streamingMsgId 
                ? {
                    ...msg,
                    content: {
                      ...normalizedFinal,
                      // COGNITO-OS v4.0: Include transparency data
                      metadata: finalResponse.metadata || {
                        cognito_os_enabled: true,
                        agents_used: ['mentor'],
                        tools_used: ['rag']
                      },
                      verification: finalResponse.verification || {},
                      rag: finalResponse.rag || {},
                      learning_path: finalResponse.learning_path || []
                    },
                    isStreaming: false,
                    user_question: messageToSend
                  }
                : msg
            ));
          } else if (accumulatedText.length > 0) {
            // Fallback - use accumulated text
            // CRITICAL FIX: Properly structure the content with accumulated text
            const fallbackContent = {
              default_view: { 
                main_content: { content: accumulatedText },
                greeting: '',
                metaphor: { text: '' }
              },
              progressive_sections: {}
            };
            data = { response: fallbackContent };
            streamingHandledFlag = true; // Mark as handled
            // FIX: Update BOTH content AND isStreaming flag
            setMessages(prev => prev.map(msg => 
              msg.message_id === streamingMsgId 
                ? { 
                    ...msg,
                    content: fallbackContent, // ✅ Now properly sets content
                    isStreaming: false,
                    user_question: messageToSend
                  }
                : msg
            ));
          }
          
        } catch (streamError) {
          // Handle abort gracefully (user clicked Stop)
          if (streamError.name === 'AbortError' || apiAbortControllerRef.current?.signal?.aborted) {
            console.log('🛑 User stopped generation');
            // Remove streaming message
            setMessages(prev => prev.filter(msg => msg.message_id !== streamingMsgId));
            setLoading(false);
            setIsGeneratingVisual(false);
            // Cancel visual polling if active
            if (visualPollingAbortRef.current) {
              visualPollingAbortRef.current.abort();
            }
            return; // Exit early - don't fall back to regular endpoint
          }
          console.warn('⚠️ Streaming failed, falling back to regular endpoint:', streamError);
          // Remove streaming message
          setMessages(prev => prev.filter(msg => msg.message_id !== streamingMsgId));
          // Fall through to regular endpoint
        }
      }
      
      // Fallback to non-streaming endpoint if streaming failed or disabled
      if (!data) {
        // Check if aborted before making fallback request
        if (apiAbortControllerRef.current?.signal?.aborted) {
          setLoading(false);
          setIsGeneratingVisual(false);
          return;
        }
        
        // Create new AbortController for fallback request
        apiAbortControllerRef.current = new AbortController();
        
        const response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(requestBody),
          signal: apiAbortControllerRef.current.signal
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
            visual_sketch: data.response?.visual_sketch || normalizedResponse?.visual_sketch || null,
            // COGNITO-OS v4.0: Include transparency data for UI components
            metadata: data.response?.metadata || normalizedResponse?.metadata || {
              cognito_os_enabled: true,
              agents_used: ['mentor'],
              tools_used: ['rag']
            },
            verification: data.response?.verification || normalizedResponse?.verification || {},
            rag: data.response?.rag || normalizedResponse?.rag || {},
            learning_path: data.response?.learning_path || normalizedResponse?.learning_path || []
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
        
        // 🏫 Extract visual artifact for SmartBoard (Digital Classroom)
        // Check ALL possible visual formats from backend
        // PRIORITY: NETRA v4 (teaching_visual) FIRST, then others
        const visualData = 
          // 🔮 NETRA v4.0 - Highest priority (AI-generated images)
          aiMsg.teaching_visual ||
          data.response?.teaching_visual ||
          normalizedResponse?.teaching_visual ||
          // Legacy/fallback visuals (lower priority)
          aiMsg.visual_sketch || 
          aiMsg.content?.visual_sketch ||
          aiMsg.whiteboard_visual ||
          data.response?.visual_sketch ||
          data.response?.whiteboard_visual ||
          data.response?.blueprint ||
          data.response?.visual_data ||
          normalizedResponse?.visual_sketch ||
          normalizedResponse?.whiteboard_visual ||
          normalizedResponse?.blueprint;
        
        if (visualData) {
          // Extract concept and subject from various sources
          const concept = visualData.concept || 
                         data.detected_subject || 
                         data.response?.concept ||
                         messageToSend.split(' ').slice(0, 3).join(' ');
          
          const subject = visualData.subject || 
                         data.detected_subject || 
                         data.response?.subject ||
                         'General';
          
          // Build visual artifact with all possible formats
          const artifact = {
            ...visualData,
            concept,
            subject,
            // Preserve all visual formats (SmartBoard checks for these)
            svg: visualData.svg || visualData.visual_sketch?.svg || data.response?.visual_sketch?.svg,
            blueprint: visualData.blueprint || data.response?.blueprint,
            template: visualData.template || data.response?.template,
            mode: visualData.mode || data.response?.mode,
            visual_sketch: visualData.visual_sketch || visualData,
            // Store original question for context-aware theming
            originalQuestion: messageToSend,
            // 🔮 NETRA v4.0 - AI-Generated Image Data
            netra_v4: visualData.netra_v4 || false,
            image_base64: visualData.image_base64 || null,
            image_format: visualData.image_format || null,
            width: visualData.width || null,
            height: visualData.height || null,
            teaching: visualData.teaching || null,
          };
          
          // Debug logging
          console.log('🎨 Setting visual artifact for SmartBoard:', {
            hasSvg: !!artifact.svg,
            hasBlueprint: !!artifact.blueprint,
            hasTemplate: !!artifact.template,
            hasMode: !!artifact.mode,
            hasNetraV4: !!artifact.netra_v4,
            hasImageBase64: !!artifact.image_base64,
            concept,
            subject,
            structure: Object.keys(artifact)
          });
          
          setVisualArtifact(artifact);
          setIsGeneratingVisual(false); // Visual arrived, stop loading
        } else {
          // Debug: Log when no visual data found
          console.log('⚠️ No visual data found in response:', {
            hasVisualSketch: !!aiMsg.visual_sketch,
            hasWhiteboardVisual: !!aiMsg.whiteboard_visual,
            hasBlueprint: !!data.response?.blueprint,
            responseKeys: Object.keys(data.response || {}),
            normalizedKeys: Object.keys(normalizedResponse || {})
          });
          
          // No visual in response - let SmartBoard timeout handle fallback
          // Don't stop loading yet - pollForVisual may still return a visual
          if (!aiMsg.visual_task_id) {
            // No async visual task either - stop loading immediately
            setIsGeneratingVisual(false);
          }
        }
        
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
      
      // Clear draft from localStorage after successful send
      localStorage.removeItem('sathi_draft_message');
      localStorage.removeItem('sathi_draft_session');
      
      // Update mastery from response if available
      if (data.response?.memory_context) {
        const memoryCtx = data.response.memory_context;
        setUserMastery(prev => ({
          subjects: {
            ...prev.subjects,
            [data.detected_subject || 'General']: memoryCtx.mastery_level || 0
          },
          weakAreas: memoryCtx.weak_topics || prev.weakAreas,
          recentTopics: memoryCtx.last_topic 
            ? [memoryCtx.last_topic, ...prev.recentTopics.filter(t => t !== memoryCtx.last_topic)].slice(0, 10)
            : prev.recentTopics
        }));
      }
      
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
      
      // 🛡️ UX FIX: Restore user input on error (so they can modify/resend easily)
      // Only restore if NOT user-initiated abort (they intentionally stopped)
      const isUserAbort = error.name === 'AbortError' || apiAbortControllerRef.current?.signal?.aborted;
      if (!isUserAbort && originalMessage) {
        setInputMessage(originalMessage);
        // Mark as intentional restore (not user typing)
        inputClearedByUserRef.current = false;
      }
      
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
      
      // 🎨 Stop visual loading on error
      setIsGeneratingVisual(false);
      
      // Handle abort errors gracefully (user clicked Stop)
      if (isUserAbort) {
        console.log('🛑 Request cancelled by user');
        // Cancel visual polling if active
        if (visualPollingAbortRef.current) {
          visualPollingAbortRef.current.abort();
        }
      }
    } finally {
      setLoading(false);
      // Clear abort controller ref
      apiAbortControllerRef.current = null;
    }
  };
  
  // Stop generation handler
  const handleStopGeneration = useCallback(() => {
    console.log('🛑 Stop generation clicked');
    
    // Abort streaming response
    if (apiAbortControllerRef.current) {
      apiAbortControllerRef.current.abort();
    }
    
    // Cancel visual polling
    if (visualPollingAbortRef.current) {
      visualPollingAbortRef.current.abort();
    }
    
    // Clear loading states
    setLoading(false);
    setIsGeneratingVisual(false);
    
    // Clear floating follow-ups (prevent auto follow-ups)
    setFloatingFollowUps([]);
    
    // Focus input after stop (cursor focus returns)
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
    
    // Input text is NEVER cleared - preserved automatically by state
  }, []);

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

  // Keep handleSendRef updated with latest handleSend
  useEffect(() => {
    handleSendRef.current = handleSend;
  });

  // Listen for follow-up question events from MentorResponseV2
  // FIX: Use ref pattern to avoid stale closure bug
  useEffect(() => {
    const handleFollowUpQuestion = (event) => {
      const { question } = event.detail;
      if (question && handleSendRef.current) {
        setInputMessage(question);
        handleSendRef.current(question);
      }
    };
    
    window.addEventListener('send-question', handleFollowUpQuestion);
    return () => window.removeEventListener('send-question', handleFollowUpQuestion);
  }, []);

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
    setVisualArtifact(null); // Clear SmartBoard
    inputRef.current?.focus();
    // Refresh sessions list to ensure it's up-to-date
    loadSessions();
  };

  // Helper function to normalize AI message content
  // CRITICAL: Never JSON.stringify - always extract clean text
  const normalizeAIContent = (content) => {
    // If content is already a proper object with default_view, return as is
    if (typeof content === 'object' && content !== null && !Array.isArray(content) && content.default_view) {
      return content;
    }
    
    // If content is a string, wrap it in proper structure
    if (typeof content === 'string') {
      // SANITIZE: Remove any embedded JSON blocks that look like internal traces
      const sanitizedContent = sanitizeResponseText(content);
      return {
        default_view: {
          greeting: sanitizedContent.substring(0, 100),
          main_content: {
            content: sanitizedContent
          }
        },
        progressive_sections: {}
      };
    }
    
    // If content is an object but missing default_view, try to extract meaningful data
    if (typeof content === 'object' && content !== null && !Array.isArray(content)) {
      // CRITICAL: Deep extraction - find actual text content, NEVER stringify
      const extractedText = deepExtractTextContent(content);
      
      // Check if it has any response-like structure
      if (content.explanation || content.answer || content.response || extractedText) {
        const rawText = content.explanation || content.answer || content.response || extractedText;
        const sanitizedText = sanitizeResponseText(rawText);
        return {
          default_view: {
            greeting: '',  // No hardcoded greeting - let AI provide it
            main_content: {
              content: sanitizedText
            }
          },
          progressive_sections: {},
          detected_subject: content.detected_subject || content.subject
        };
      }
      
      // If it's an object with visual_sketch but no default_view, wrap it
      if (content.visual_sketch) {
        const visualText = content.explanation || content.answer || deepExtractTextContent(content) || '';
        return {
          default_view: {
            greeting: '',
            main_content: {
              content: sanitizeResponseText(visualText)
            }
          },
          progressive_sections: {},
          visual_sketch: content.visual_sketch,
          detected_subject: content.detected_subject || content.subject
        };
      }
      
      // Last resort: NEVER stringify - extract any available text or show error
      // This prevents internal agent data from leaking to UI
      const lastResortText = deepExtractTextContent(content);
      if (lastResortText && lastResortText.length > 20) {
        return {
          default_view: {
            greeting: '',
            main_content: {
              content: sanitizeResponseText(lastResortText)
            }
          },
          progressive_sections: {},
          detected_subject: content?.detected_subject || content?.subject || 'General'
        };
      }
      
      // If still no text found, return error message (never stringify raw objects)
      console.warn('⚠️ normalizeAIContent: Could not extract text from response object', Object.keys(content || {}));
      return {
        default_view: {
          greeting: '',
          main_content: {
            content: 'I processed your question but had trouble formatting the response. Please try asking again!'
          }
        },
        progressive_sections: {}
      };
    }
    
    // Fallback for any other type - NEVER stringify
    console.warn('⚠️ normalizeAIContent: Unexpected content type', typeof content);
    return {
      default_view: {
        greeting: '',
        main_content: {
          content: 'Response received. Please try asking your question again for a better formatted answer.'
        }
      },
      progressive_sections: {}
    };
  };

  // Load session
  const loadSession = async (sessionId) => {
    try {
      setSessionLoadingId(sessionId);
      setMessagesLoading(true); // Show skeleton while loading
      const res = await apiClient.get(`/ai/chat/${sessionId}/messages`);

      if (res.status === 200) {
        const data = res.data;
        const parsed = [];
        const ids = new Set();
        const list = Array.isArray(data.messages) ? data.messages : [];
        list.forEach(msg => {
          // BUGFIX: Check for user_message OR message field to ensure user messages are never lost
          // The key issue was that empty/falsy user_message would skip adding the user message entirely
          const hasUserMessage = msg.user_message !== undefined || msg.message !== undefined;
          const aiPayload = msg.dual_response || msg.response || msg.ai_response;
          
          // Extract user content from any available field
          const extractUserContent = () => {
            if (msg.user_message !== undefined && msg.user_message !== null) {
              return typeof msg.user_message === 'string' 
                ? msg.user_message 
                : (msg.user_message?.message || String(msg.user_message));
            }
            if (msg.message !== undefined && msg.message !== null) {
              return typeof msg.message === 'string' 
                ? msg.message 
                : String(msg.message);
            }
            return ''; // Fallback to empty string if no user message found
          };
          
          // Always add user message if ANY user content field exists (even if empty)
          if (hasUserMessage) {
            const uid = (msg.message_id ? `${msg.message_id}_user` : `user_${Date.now()}_${crypto.randomUUID()}`);
            if (!ids.has(uid)) {
              const userContent = extractUserContent();
              // Only add if content is not empty (skip truly empty messages)
              if (userContent.trim()) {
                parsed.push({ 
                  type: 'user', 
                  content: userContent, 
                  timestamp: msg.timestamp || new Date().toISOString(), 
                  message_id: uid 
                });
                ids.add(uid);
              }
            }
          }
          
          // Add AI response if present
          if (aiPayload) {
            const aid = msg.message_id || `ai_${Date.now()}_${crypto.randomUUID()}`;
            if (!ids.has(aid)) {
              // CRITICAL: Normalize AI content to ensure it's always a proper object
              parsed.push({ 
                type: 'ai', 
                content: normalizeAIContent(aiPayload), 
                timestamp: msg.timestamp || new Date().toISOString(), 
                message_id: aid,
                // Preserve user_question for context (helps with history display)
                user_question: extractUserContent(),
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
      toastError('Failed to load chat', 'Please try again');
    } finally { 
      setSessionLoadingId(null); 
      setMessagesLoading(false);
    }
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

  // ========================================
  // MOBILE VIEWPORT HEIGHT FIX
  // Fixes 100vh issue on mobile browsers
  // where browser chrome (URL bar) is included
  // ========================================
  const [viewportHeight, setViewportHeight] = useState('100vh');
  
  useEffect(() => {
    const updateViewportHeight = () => {
      // Get the actual visible viewport height
      const vh = window.innerHeight;
      setViewportHeight(`${vh}px`);
      // Also set CSS variable for other elements
      document.documentElement.style.setProperty('--real-vh', `${vh}px`);
    };
    
    // Set initial value
    updateViewportHeight();
    
    // Update on resize, orientation change, and when keyboard opens/closes
    window.addEventListener('resize', updateViewportHeight);
    window.addEventListener('orientationchange', updateViewportHeight);
    
    // For iOS Safari - handle keyboard
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', updateViewportHeight);
    }
    
    return () => {
      window.removeEventListener('resize', updateViewportHeight);
      window.removeEventListener('orientationchange', updateViewportHeight);
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', updateViewportHeight);
      }
    };
  }, []);

  // Lock body scroll when in chat mode (prevents mobile bounce/scroll issues)
  useEffect(() => {
    // Only lock on mobile
    const isMobile = window.innerWidth <= 768;
    if (isMobile && messages.length > 0) {
      document.body.classList.add('chat-open');
    } else {
      document.body.classList.remove('chat-open');
    }
    return () => {
      document.body.classList.remove('chat-open');
    };
  }, [messages.length]);

  return (
    <div 
      className="cognito-tutor-container flex flex-col bg-gray-50 overflow-hidden relative"
      style={{ height: viewportHeight }}
    >
      {/* 📡 OFFLINE INDICATOR - Shows when no internet connection */}
      <AnimatePresence>
        {!isOnline && (
          <motion.div
            initial={{ y: -60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -60, opacity: 0 }}
            className="fixed top-0 left-0 right-0 z-[9999] bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-3 flex items-center justify-center gap-3 shadow-lg"
          >
            <span className="text-xl">📡</span>
            <span className="font-medium">You're offline. Some features may not work.</span>
            <button 
              onClick={() => window.location.reload()}
              className="ml-4 px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
            >
              Retry
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 🎨 VISUAL GENERATION INDICATOR - Shows when generating visual */}
      {/* REMOVED: Visual generation banner - per founder decision */}
      {/* Header should only contain brand/title, no heavy visuals */}
      
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
      
      {/* 🎨 FEEDBACK TOAST - Confirmation when user gives feedback */}
      <FeedbackToast
        type={feedbackToastState.type}
        show={feedbackToastState.show}
        onClose={hideFeedbackToast}
        autoHideDuration={3000}
      />

      {/* ⌨️ KEYBOARD SHORTCUTS HELP PANEL */}
      <ShortcutsHelpPanel
        show={showShortcutsHelp}
        onClose={() => setShowShortcutsHelp(false)}
      />

      {/* Onboarding Tour for First-Time Users */}
      <OnboardingTour onComplete={() => {
        console.log('Onboarding completed');
        // Refresh user progress after onboarding
        loadUserProgress();
      }} />

      {/* 🏫 NEW: ClassroomLayout UI (SathiClassroom style) */}
      {useClassroomLayout ? (
        <ClassroomLayout
          chatHistory={formattedChatHistory}
          activeSessionId={currentSession}
          onChatSelect={(chat) => loadSession(chat.id)}
          onNewChat={startNewChat}
          onRenameChat={(id, title) => {
            const session = sessions.find(s => s.session_id === id);
            if (session) renameSession(session, title);
          }}
          onDeleteChat={(id) => {
            const session = sessions.find(s => s.session_id === id);
            if (session) requestDeleteSession(session);
          }}
          onPinChat={(id) => {
            const session = sessions.find(s => s.session_id === id);
            if (session) togglePinSession(session);
          }}
          isLoadingHistory={sessionsLoading}
          visualArtifact={visualArtifact}
          headerTitle="DRON AI"
          headerRightActions={headerRightActions}
          hasStartedChat={messages.length > 0}
          isGeneratingVisual={isGeneratingVisual}
          userQuestion={currentUserQuestion}
        >
          {/* Chat Content - Messages + Input (ChatGPT/Gemini style) */}
          <div className={`flex flex-col h-full relative ${messages.length > 0 ? 'sathi-chat-wrapper' : ''}`}>
            {/* Scrollable Content Area */}
            <div 
              ref={chatContainerRef}
              className={`flex-1 overflow-y-auto ${messages.length > 0 ? 'sathi-chat-scroll' : ''}`}
            >
              {/* Welcome Screen - PREMIUM NEURAL AI MENTOR INTERFACE */}
              {showWelcome && messages.length === 0 ? (
                <PremiumWelcome 
                  onSendMessage={handleQuickSend}
                  userProfile={user}
                />
              ) : (
                /* Messages Container - Premium Dark Theme */
                <div className="max-w-4xl mx-auto px-4 py-6 w-full">
                {/* Memory Context Banner */}
                {messages.length > 0 && messages[messages.length - 1]?.content?.memory_context && (
                  <MemoryContextBanner memoryContext={messages[messages.length - 1].content.memory_context} />
                )}
                <div className="space-y-4">
                  <AnimatePresence>
                    {messages.map((message, index) => (
                      <motion.div
                        key={message.id || message.message_id || index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                      >
                        {message.type === 'user' && (
                          <div className="flex justify-end mb-5">
                            <div className="sathi-user-message">
                              <p>
                                {/* FIXED: Extract actual user message, NEVER show "Question" fallback */}
                                {(() => {
                                  if (typeof message.content === 'string' && message.content.trim()) {
                                    return message.content;
                                  }
                                  if (message.user_question && typeof message.user_question === 'string') {
                                    return message.user_question;
                                  }
                                  if (typeof message.content === 'object' && message.content) {
                                    return message.content.message || message.content.text || message.content.query || '';
                                  }
                                  return ''; // Never show "Question" - empty is better than misleading
                                })()}
                              </p>
                              {message.image_preview && (
                                <img src={message.image_preview} alt="Attached" className="mt-2 rounded-lg max-h-32 object-contain" />
                              )}
                            </div>
                          </div>
                        )}
                        
                        {message.type === 'ai' && (() => {
                          // PRODUCTION FIX: Single loading indicator strategy
                          // The "Thinking..." indicator (below) handles the loading state
                          // This prevents duplicate loading UIs
                          if (message.isStreaming) {
                            const hasRealContent = 
                              message.content?.default_view?.main_content?.content?.trim?.()?.length > 0 ||
                              message.content?.default_view?.greeting?.trim?.()?.length > 0 ||
                              (typeof message.content?.default_view?.main_content === 'string' && 
                               message.content.default_view.main_content.trim().length > 0);
                            // No content yet = don't render, let "Thinking..." indicator handle this phase
                            if (!hasRealContent) return null;
                          }
                          
                          return (
                            <div className="flex gap-3 mb-6 sathi-ai-message-row">
                              {/* Mini Avatar - Left side */}
                              <div className="sathi-ai-avatar-left">
                                <span>🧠</span>
                              </div>
                              {/* Response Content - Clean, readable */}
                              <div className="flex-1 sathi-ai-message-content">
                                <SmartResponse
                                  response={message.content}
                                  visualSketch={message.visual_sketch || message.content?.visual_sketch}
                                  question={message.user_question || ''}
                                  onFollowUp={(q) => { setInputMessage(q); inputRef.current?.focus(); }}
                                  isStreaming={message.isStreaming}
                                />
                              </div>
                            </div>
                          );
                        })()}
                        
                        {message.type === 'error' && (
                          <div className="flex justify-center mb-4">
                            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 max-w-md">
                              <p className="text-sm">{typeof message.content === 'string' ? message.content : 'An error occurred'}</p>
                              {message.canRetry && (
                                <button onClick={() => handleRetry(message)} className="mt-2 text-sm text-red-600 hover:underline">
                                  Retry
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              
                {/* Loading Indicator - Production Quality */}
                {loading && (
                  <div className="flex gap-3 mb-6 sathi-ai-message-row">
                    <div className="sathi-ai-avatar-left sathi-avatar-thinking">
                      <span>🧠</span>
                    </div>
                    <div className="sathi-thinking-indicator">
                      <span className="sathi-thinking-text">Thinking</span>
                      <span className="sathi-thinking-dots">
                        <span></span><span></span><span></span>
                      </span>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
                </div>
              )}
            </div>
            
            {/* Input Area - Premium Dark Theme */}
            <div className={`flex-shrink-0 ${messages.length > 0 ? 'sathi-chat-input-container' : 'bg-white border-t border-gray-200/80 shadow-[0_-4px_20px_-4px_rgba(0,0,0,0.04)]'}`}>
              <div className={messages.length > 0 ? 'sathi-chat-input-wrapper' : 'max-w-3xl mx-auto px-4 py-3'}>
              {/* Follow-up suggestions */}
              {floatingFollowUps.length > 0 && !loading && (
                <div className={messages.length > 0 ? 'sathi-chat-followups' : 'mb-2.5 flex flex-wrap gap-1.5'}>
                  {floatingFollowUps.map((suggestion, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      onClick={() => {
                        const message = typeof suggestion === 'string' ? suggestion : suggestion.text;
                        setInputMessage(message);
                        setFloatingFollowUps([]);
                        handleSend(message);
                      }}
                      className={messages.length > 0 ? 'sathi-chat-followup-chip' : 'px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg text-xs font-medium transition-colors border border-purple-100/50'}
                    >
                      {typeof suggestion === 'string' ? suggestion : suggestion.text}
                    </motion.button>
                  ))}
                </div>
              )}
              
              {/* Image Preview */}
              {imagePreview && (
                <div className="mb-3 relative inline-block">
                  <img src={imagePreview} alt="Upload preview" className="max-h-32 rounded-lg border-2 border-purple-300" />
                  <button onClick={handleRemoveImage} className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full">
                    <XCircle className="w-4 h-4" />
                  </button>
                </div>
              )}
              
              {/* Glow effect for dark theme */}
              {messages.length > 0 && <div className="sathi-chat-input-glow" />}
              
              {/* Input Form - Premium styling when in chat */}
              <form 
                onSubmit={(e) => { 
                  e.preventDefault(); 
                  if (loading) {
                    handleStopGeneration();
                  } else {
                    handleSend();
                  }
                }} 
                className={messages.length > 0 ? 'sathi-chat-input-form' : ''}
                onClick={(e) => {
                  // Make entire input area clickable to focus textarea
                  if (e.target === e.currentTarget && inputRef.current) {
                    inputRef.current.focus();
                  }
                }}
              >
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />
                {messages.length === 0 ? (
                  /* Welcome state - original styling */
                  <div className="flex items-end gap-2 bg-white rounded-xl border border-gray-200 shadow-sm focus-within:border-purple-400 focus-within:ring-2 focus-within:ring-purple-100/50 focus-within:shadow-md px-2 py-1.5 transition-all duration-200">
                    <button type="button" onClick={() => fileInputRef.current?.click()} disabled={loading} className="p-2 text-gray-400 hover:text-purple-600 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50">
                      <ImageIcon className="w-5 h-5" />
                    </button>
                    {/* 🎙️ VOICE INPUT BUTTON - Welcome State (Enhanced with audio level) */}
                    <div className="relative">
                      <motion.button
                        type="button"
                        onClick={handleVoiceToggle}
                        disabled={loading || !isVoiceSupported}
                        whileHover={isVoiceSupported ? { scale: 1.05 } : {}}
                        whileTap={isVoiceSupported ? { scale: 0.95 } : {}}
                        className={`p-2 rounded-lg transition-colors disabled:opacity-50 relative ${
                          isListening 
                            ? 'bg-red-100 text-red-600' 
                            : 'text-gray-400 hover:text-purple-600 hover:bg-gray-50'
                        }`}
                        title={!isVoiceSupported 
                          ? 'Voice input requires Chrome, Edge, or Safari' 
                          : isListening 
                            ? `Listening... (${supportedLanguages[voiceLanguage]?.name || 'English'})` 
                            : 'Voice input'
                        }
                      >
                        {isListening ? (
                          <>
                            {/* Audio Level Ring */}
                            <motion.div
                              className="absolute inset-0 rounded-lg border-2 border-red-400"
                              animate={{ 
                                scale: [1, 1 + (audioLevel / 100) * 0.3, 1],
                                opacity: [0.5, 0.8, 0.5]
                              }}
                              transition={{ repeat: Infinity, duration: 0.5 }}
                            />
                            <motion.div
                              animate={{ scale: [1, 1.15, 1] }}
                              transition={{ repeat: Infinity, duration: 1.2 }}
                            >
                              <Mic className="w-5 h-5 relative z-10" />
                            </motion.div>
                          </>
                        ) : (
                          isVoiceSupported ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />
                        )}
                      </motion.button>
                      {/* Low volume indicator */}
                      {isListening && isLowVolume && (
                        <motion.div 
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="absolute -top-8 left-1/2 -translate-x-1/2 bg-orange-500 text-white text-xs px-2 py-0.5 rounded whitespace-nowrap"
                        >
                          Speak louder
                        </motion.div>
                      )}
                    </div>
                    <textarea
                      ref={inputRef}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={(e) => { 
                        if (e.key === 'Enter' && !e.shiftKey) { 
                          e.preventDefault(); 
                          if (loading) {
                            handleStopGeneration();
                          } else {
                            handleSend();
                          }
                        } 
                      }}
                      placeholder="Ask anything... I'll explain like a friend 💪"
                      className="flex-1 px-2 py-2 bg-transparent border-0 focus:ring-0 outline-none resize-none text-gray-800 placeholder-gray-400 text-sm leading-relaxed"
                      rows={1}
                      disabled={false}
                      style={{ minHeight: '38px', maxHeight: '120px' }}
                    />
                    <motion.button
                      type={loading ? "button" : "submit"}
                      onClick={loading ? handleStopGeneration : undefined}
                      disabled={!loading && (!inputMessage.trim() && !selectedImage)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 ${
                        loading
                          ? 'bg-red-500 hover:bg-red-600 text-white shadow-sm'
                          : (inputMessage.trim() || selectedImage)
                          ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-sm'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      }`}
                      title={loading ? "Stop generation" : "Send message"}
                    >
                      {loading ? <X className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                    </motion.button>
                  </div>
                ) : (
                  /* Chat state - Premium dark styling */
                  <>
                    <button type="button" onClick={() => fileInputRef.current?.click()} disabled={loading} className="sathi-chat-attach-btn">
                      <ImageIcon className="w-5 h-5" />
                    </button>
                    {/* 🎙️ VOICE INPUT BUTTON (Enhanced with audio level & language) */}
                    <div className="relative">
                      <motion.button
                        type="button"
                        onClick={handleVoiceToggle}
                        disabled={loading || !isVoiceSupported}
                        whileHover={isVoiceSupported ? { scale: 1.05 } : {}}
                        whileTap={isVoiceSupported ? { scale: 0.95 } : {}}
                        className={`sathi-chat-attach-btn relative ${isListening ? 'sathi-voice-listening' : ''}`}
                        title={!isVoiceSupported 
                          ? 'Voice input requires Chrome, Edge, or Safari' 
                          : isListening 
                            ? `Listening in ${supportedLanguages[voiceLanguage]?.name || 'English'}... Click to stop` 
                            : `Voice input (${supportedLanguages[voiceLanguage]?.flag || '🎤'})`
                        }
                      >
                        {isListening ? (
                          <>
                            {/* Animated audio level ring */}
                            <motion.div
                              className="absolute inset-0 rounded-xl"
                              style={{
                                background: `radial-gradient(circle, rgba(239,68,68,${audioLevel/200}) 0%, transparent 70%)`
                              }}
                              animate={{ 
                                scale: [1, 1 + (audioLevel / 150), 1],
                              }}
                              transition={{ repeat: Infinity, duration: 0.3 }}
                            />
                            <motion.div
                              animate={{ scale: [1, 1.15, 1] }}
                              transition={{ repeat: Infinity, duration: 1.2 }}
                              className="relative z-10"
                            >
                              <Mic className="w-5 h-5" />
                            </motion.div>
                          </>
                        ) : (
                          isVoiceSupported ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5 opacity-40" />
                        )}
                      </motion.button>
                      {/* Low volume warning tooltip */}
                      {isListening && isLowVolume && (
                        <motion.div 
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="absolute -top-10 left-1/2 -translate-x-1/2 bg-orange-500 text-white text-xs px-2 py-1 rounded-lg whitespace-nowrap shadow-lg z-20"
                        >
                          📢 Speak louder
                        </motion.div>
                      )}
                      {/* Interim transcript preview */}
                      {isListening && interimTranscript && (
                        <motion.div 
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 0.7 }}
                          className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-800 text-gray-200 text-xs px-2 py-1 rounded-lg whitespace-nowrap max-w-[200px] truncate shadow-lg z-20"
                        >
                          {interimTranscript.substring(0, 30)}...
                        </motion.div>
                      )}
                    </div>
                    <textarea
                      ref={inputRef}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={(e) => { 
                        if (e.key === 'Enter' && !e.shiftKey) { 
                          e.preventDefault(); 
                          if (loading) {
                            handleStopGeneration();
                          } else {
                            handleSend();
                          }
                        } 
                      }}
                      placeholder="Ask a follow-up... I'm still here 💪"
                      className="sathi-chat-textarea"
                      rows={1}
                      disabled={false}
                      style={{ minHeight: '44px', maxHeight: '120px' }}
                      onClick={(e) => e.currentTarget.focus()}
                    />
                    <motion.button
                      type={loading ? "button" : "submit"}
                      onClick={loading ? handleStopGeneration : undefined}
                      disabled={!loading && (!inputMessage.trim() && !selectedImage)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`sathi-chat-send-btn ${
                        loading
                          ? 'bg-red-500 hover:bg-red-600 text-white'
                          : (!inputMessage.trim() && !selectedImage)
                          ? 'opacity-40'
                          : ''
                      }`}
                      title={loading ? "Stop generation" : "Send message"}
                    >
                      {loading ? <X className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                    </motion.button>
                  </>
                )}
              </form>
              </div>
            </div>
          </div>
        </ClassroomLayout>
      ) : (
      <>
      {/* OLD UI: Persistent Sidebar on large screens - PREMIUM DESIGN */}
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
          
          {/* Search Input */}
          <div className="relative mt-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-100 border-0 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:bg-white transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-200 rounded-full"
              >
                <X className="w-3 h-3 text-slate-400" />
              </button>
            )}
          </div>
        </div>
        
        {/* Chat list with custom scrollbar */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5" style={{ scrollbarWidth: 'thin', scrollbarColor: '#c4b5fd transparent' }}>
          {/* Filter sessions by search query */}
          {sessions
            .filter(session => {
              if (!searchQuery.trim()) return true;
              const query = searchQuery.toLowerCase();
              return (
                session.title?.toLowerCase().includes(query) ||
                session.subject?.toLowerCase().includes(query)
              );
            })
            .map((session, idx) => {
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
          className="bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm relative"
          style={{ overflow: 'visible', zIndex: 40 }}
        >
          <div className="max-w-5xl mx-auto px-6 h-full flex flex-col justify-center py-3" style={{ overflow: 'visible' }}>
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
                <div className="hidden lg:block" style={{ position: 'relative', zIndex: 50 }}>
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
                {/* Mastery Indicator - Compact */}
                {Object.keys(userMastery.subjects).length > 0 && (
                  <MasteryIndicator
                    mastery={userMastery.subjects}
                    weakAreas={userMastery.weakAreas}
                    recentTopics={userMastery.recentTopics}
                    compact={true}
                    onTopicClick={(topic) => {
                      setInputMessage(`Help me understand ${topic} better`);
                      inputRef.current?.focus();
                    }}
                  />
                )}
                
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
                
                {/* 🔔 Notification Bell - Shows reminder notifications */}
                <NotificationBell 
                  onStartStudy={(topic) => {
                    // Pre-fill input and optionally auto-send
                    const studyMessage = `Let's study ${topic}! Help me understand this topic.`;
                    setInputMessage(studyMessage);
                    // Focus the input
                    setTimeout(() => {
                      const inputEl = document.querySelector('textarea');
                      if (inputEl) inputEl.focus();
                    }, 100);
                  }}
                />
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
            {/* Messages Loading Skeleton */}
            {messagesLoading && (
              <div className="space-y-4 py-6 animate-pulse">
                {[1, 2, 3].map((i) => (
                  <div key={i} className={`flex ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
                    <div className={`${i % 2 === 0 ? 'max-w-[60%]' : 'max-w-[80%]'} space-y-2`}>
                      <div className={`h-4 ${i % 2 === 0 ? 'bg-gray-300' : 'bg-gray-200'} rounded-lg w-full`}></div>
                      <div className={`h-4 ${i % 2 === 0 ? 'bg-gray-300' : 'bg-gray-200'} rounded-lg w-3/4`}></div>
                      {i % 2 !== 0 && <div className="h-4 bg-gray-200 rounded-lg w-1/2"></div>}
                    </div>
                  </div>
                ))}
              </div>
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
                      <div className="flex justify-end group">
                        <motion.div
                          initial={{ opacity: 0, x: 10, scale: 0.95 }}
                          animate={{ opacity: 1, x: 0, scale: 1 }}
                          transition={{ type: "spring", stiffness: 300, damping: 25 }}
                          className="max-w-[75%] bg-gradient-to-br from-gray-900 to-gray-800 text-white rounded-2xl rounded-br-md px-5 py-3.5 shadow-lg shadow-gray-900/20 relative"
                          title={message.timestamp ? new Date(message.timestamp).toLocaleString() : ''}
                        >
                          {/* Timestamp on hover */}
                          {message.timestamp && (
                            <span className="absolute -top-6 right-0 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                              {formatRelativeTime(message.timestamp)}
                            </span>
                          )}
                          
                          {/* Edit Button - Show on hover */}
                          {!loading && (
                            <button
                              onClick={() => {
                                const content = typeof message.content === 'string' 
                                  ? message.content 
                                  : message.content?.message || message.content?.text || '';
                                setEditingMessageId(message.id);
                                setEditingMessageContent(content);
                                setInputMessage(content);
                                inputRef.current?.focus();
                              }}
                              className="absolute -left-10 top-1/2 -translate-y-1/2 p-2 bg-white rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity text-gray-600 hover:text-violet-600 hover:bg-violet-50"
                              title="Edit message"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                          )}
                          
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
                              // Priority 1: Direct string content
                              if (typeof message.content === 'string' && message.content.trim()) {
                                return message.content;
                              }
                              // Priority 2: user_question field (set when sending message)
                              if (message.user_question && typeof message.user_question === 'string' && message.user_question.trim()) {
                                return message.user_question;
                              }
                              // Priority 3: Extract from object content
                              if (typeof message.content === 'object' && message.content !== null) {
                                const question = message.content.message || 
                                                 message.content.text || 
                                                 message.content.query ||
                                                 message.content.question ||
                                                 message.content.user_message;
                                if (question && typeof question === 'string' && question.trim()) {
                                  return question;
                                }
                              }
                              // NEVER show generic "Question" - show nothing instead
                              // This prevents confusing UX
                              return '';
                            })()}
                          </p>
                        </motion.div>
                      </div>
                    )}

                    {message.type === 'ai' && (() => {
                      // FIX: Skip rendering placeholder messages during streaming
                      // The thinking indicator is shown separately via the `loading` state
                      // This prevents showing empty/placeholder AI cards before real content arrives
                      if (message.isStreaming) {
                        // Check if there's actual content to show (not just empty placeholders)
                        const hasRealContent = 
                          message.content?.default_view?.main_content?.content?.trim?.()?.length > 0 ||
                          message.content?.default_view?.greeting?.trim?.()?.length > 0;
                        
                        if (!hasRealContent) {
                          // Don't render empty placeholder - thinking indicator handles this
                          return null;
                        }
                      }
                      
                      return (
                      <div className="flex justify-start group">
                        <div className="max-w-3xl w-full relative">
                          {/* Timestamp on hover */}
                          {message.timestamp && (
                            <span className="absolute -top-6 left-0 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                              {formatRelativeTime(message.timestamp)}
                            </span>
                          )}
                          
                          {/* Premium Response Container - Glassmorphic Design */}
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ type: "spring", stiffness: 200, damping: 20 }}
                            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg shadow-gray-200/40 border border-gray-100/80"
                            title={message.timestamp ? new Date(message.timestamp).toLocaleString() : ''}
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
                                  handleSend(question);  // FIX: Pass directly, no setTimeout
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
                            
                            {/* Visual loading indicator removed - was adding noise */}
                            
                            {/* Action Buttons - Copy & Feedback - Mobile touch-friendly */}
                            <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center gap-1 sm:gap-1 flex-wrap">
                              {/* Copy Button - Touch friendly */}
                              <button
                                onClick={() => {
                                  const textContent = message.content?.default_view?.main_content?.content || 
                                                     message.content?.response || 
                                                     JSON.stringify(message.content);
                                  navigator.clipboard.writeText(textContent);
                                  toastSuccess('Copied!');
                                }}
                                className="p-2.5 sm:p-2 min-w-[40px] min-h-[40px] sm:min-w-0 sm:min-h-0 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all flex items-center justify-center"
                                title="Copy response"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              </button>
                              
                              <div className="w-px h-4 bg-gray-200 dark:bg-gray-600 mx-1 hidden sm:block" />
                              
                              {/* Thumbs Up - Touch friendly */}
                              <button
                                onClick={() => {
                                  toastSuccess('Thanks for your feedback!');
                                  console.log('Positive feedback for message:', message.id);
                                }}
                                className="p-2.5 sm:p-2 min-w-[40px] min-h-[40px] sm:min-w-0 sm:min-h-0 rounded-lg text-gray-400 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 transition-all flex items-center justify-center"
                                title="Good response"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                                </svg>
                              </button>
                              
                              {/* Thumbs Down - Touch friendly */}
                              <button
                                onClick={() => {
                                  toastSuccess('We\'ll improve!');
                                  console.log('Negative feedback for message:', message.id);
                                }}
                                className="p-2.5 sm:p-2 min-w-[40px] min-h-[40px] sm:min-w-0 sm:min-h-0 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 transition-all flex items-center justify-center"
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

              {/* Thinking Indicator */}
              <div className="flex justify-start">
                <NeuralThinkingIndicator isLoading={loading} />
              </div>

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
                            handleSend(suggestionText);  // FIX: Pass directly, no setTimeout
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
                      if (loading) {
                        handleStopGeneration();
                      } else {
                        handleSend();
                      }
                    }
                  }}
                  placeholder="Ask anything... I'll explain like a friend 💪"
                  className="flex-1 px-3 py-2.5 bg-transparent border-0 focus:ring-0 outline-none resize-none text-slate-800 dark:text-gray-100 placeholder-slate-400 dark:placeholder-gray-500 text-sm leading-relaxed max-h-[120px] font-medium"
                  rows="1"
                  disabled={false}
                  style={{ 
                    minHeight: '44px',
                    height: 'auto',
                    maxHeight: '120px'
                  }}
                />

                {/* Dynamic Send/Stop Button */}
                <div className="flex-shrink-0">
                  <motion.button
                    type={loading ? "button" : "submit"}
                    onClick={loading ? handleStopGeneration : undefined}
                    disabled={!loading && (!inputMessage.trim() && !selectedImage)}
                    whileHover={{ scale: (!loading && (inputMessage.trim() || selectedImage)) ? 1.05 : 1.02 }}
                    whileTap={{ scale: (!loading && (inputMessage.trim() || selectedImage)) ? 0.95 : 0.98 }}
                    className={`w-10 h-10 rounded-xl transition-all duration-200 flex items-center justify-center ${
                      loading
                        ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg'
                        : (inputMessage.trim() || selectedImage)
                        ? 'bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50'
                        : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    }`}
                    title={loading ? "Stop generating" : "Send message"}
                  >
                    {loading ? <X className="h-4 w-4" /> : <Send className="h-4 w-4" />}
                  </motion.button>
                </div>
              </div>
              
              {/* Helper Text - Clean Design with Character Count */}
              <div className="flex items-center justify-between mt-2 px-1">
                <p className="text-xs text-slate-500 font-medium">
                  Press <kbd className="px-1.5 py-0.5 bg-slate-100 rounded-md text-slate-600 font-mono text-[10px] border border-slate-200">Enter</kbd> to send
                </p>
                <div className="flex items-center gap-3">
                  {/* Character Count */}
                  {inputMessage.length > 0 && (
                    <span className={`text-xs font-medium ${inputMessage.length > 1800 ? 'text-red-500' : inputMessage.length > 1500 ? 'text-amber-500' : 'text-slate-400'}`}>
                      {inputMessage.length}/2000
                    </span>
                  )}
                  {loading && (
                    <span className="text-xs text-violet-600 flex items-center gap-1.5 font-medium">
                      <Loader className="w-3.5 h-3.5 animate-spin" />
                      Sathi is thinking...
                    </span>
                  )}
                </div>
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
      </>
      )}
      {/* End of ClassroomLayout conditional */}

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







