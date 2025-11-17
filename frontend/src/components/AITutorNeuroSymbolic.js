/**
 * AI Tutor - Neuro-Symbolic v3.0
 * Indian Student-Centric, Karnataka-Friendly Learning Experience
 */
import React, { useState, useEffect, useRef } from 'react';
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
  MoreVertical
} from 'lucide-react';
import NeuroSymbolicResponse from './neuro-symbolic/NeuroSymbolicResponse';
import MentorResponseV2 from './mentor-v2/MentorResponseV2';
import UpgradeModal from './UpgradeModal';
import apiClient from '../api/client';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function AITutorNeuroSymbolic() {
  const { user } = useAuth();
  const { checkFeatureAccess, trackFeatureUsage } = useSubscription();
  const { success: toastSuccess, error: toastError } = useToast();

  // Core state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [sessionLoadingId, setSessionLoadingId] = useState(null);
  const [editing, setEditing] = useState({ id: null, title: '' });
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [confirmDlg, setConfirmDlg] = useState({ open: false, title: '', message: '', onConfirm: null });

  // UI state
  const [showSidebar, setShowSidebar] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState('Mathematics');
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalData, setUpgradeModalData] = useState(null);

  // Welcome state
  const [showWelcome, setShowWelcome] = useState(true);
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  const [hasInteraction, setHasInteraction] = useState(false);

  // Default quick prompts (subject-specific)
  const [defaultPrompts, setDefaultPrompts] = useState([]);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

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

  // Load default prompts when subject changes
  useEffect(() => {
    loadDefaultPrompts();
  }, [selectedSubject]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Collapse header when chat starts
  useEffect(() => {
    setHeaderCollapsed(messages.length > 0);
    setShowWelcome(messages.length === 0);
  }, [messages.length]);

  // Load default prompts for subject
  const loadDefaultPrompts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai/subjects/${selectedSubject}/defaultPrompts`);
      if (response.ok) {
        const data = await response.json();
        setDefaultPrompts(data.prompts || []);
      }
    } catch (error) {
      console.error('Error loading default prompts:', error);
      // Fallback prompts
      setDefaultPrompts([
        `Explain key concepts in ${selectedSubject}`,
        `Common mistakes in ${selectedSubject}`,
        `Exam strategies for ${selectedSubject}`
      ]);
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

    // Check feature access
    const access = await checkFeatureAccess('ai_mentor');
    if (!access.has_access) {
      setUpgradeModalData(access);
      setShowUpgradeModal(true);
      return;
    }

    // Clear input immediately
    setInputMessage('');
    setHasInteraction(true);
    setShowWelcome(false);

    // Add user message optimistically
    const userMsg = {
      type: 'user',
      content: messageToSend,
      timestamp: new Date().toISOString(),
      id: Date.now() + Math.random()
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
            subject: selectedSubject,
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

      // Call neuro-symbolic endpoint
      const response = await fetch(`${BACKEND_URL}/api/ai/neuro-symbolic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId,
          exam_mode: examMode
        })
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
        throw new Error(`Failed to get response: ${response.status}`);
      }

      const data = await response.json();

      // Debug: Log full response to check for teaching_visual
      console.log('🎨 FULL API RESPONSE:', data);
      console.log('🎨 Teaching Visual:', data.response?.teaching_visual);
      console.log('🎨 Visual Data:', data.response?.visual_data);

      // Add AI response
      const aiMsg = {
        type: 'ai',
        content: data.response,
        timestamp: new Date().toISOString(),
        message_id: data.message_id,
        emotion_detected: data.emotion_detected,
        generation_time: data.generation_time,
        // CRITICAL: Extract teaching_visual from response
        teaching_visual: data.response?.teaching_visual || null,
        visual_data: data.response?.visual_data || null
      };

      setMessages(prev => [...prev, aiMsg]);

      // Track usage
      await trackFeatureUsage('ai_mentor');

    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [
        ...prev,
        {
          type: 'error',
          content: 'Failed to get response. Please try again.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Quick send from default prompts
  const handleQuickSend = (prompt) => {
    handleSend(prompt);
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
            const uid = (msg.message_id ? `${msg.message_id}_user` : `user_${Date.now()}_${Math.random()}`);
            if (!ids.has(uid)) {
              parsed.push({ type: 'user', content: msg.user_message, timestamp: msg.timestamp || new Date().toISOString(), message_id: uid });
              ids.add(uid);
            }
            const aiPayload = msg.dual_response || msg.response || msg.ai_response;
            if (aiPayload) {
              const aid = msg.message_id || `ai_${Date.now()}_${Math.random()}`;
              if (!ids.has(aid)) {
                parsed.push({ type: 'ai', content: aiPayload, timestamp: msg.timestamp || new Date().toISOString(), message_id: aid });
                ids.add(aid);
              }
            }
          } else if (msg.message && !msg.response && !msg.ai_response) {
            // Separate user message
            const uid = msg.message_id || `user_${Date.now()}_${Math.random()}`;
            if (!ids.has(uid)) {
              parsed.push({ type: 'user', content: msg.message, timestamp: msg.timestamp || new Date().toISOString(), message_id: uid });
              ids.add(uid);
            }
          } else if (msg.response || msg.ai_response) {
            // Separate AI response
            const aid = msg.message_id || `ai_${Date.now()}_${Math.random()}`;
            if (!ids.has(aid)) {
              parsed.push({ type: 'ai', content: msg.response || msg.ai_response, timestamp: msg.timestamp || new Date().toISOString(), message_id: aid });
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
    <div className="flex h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-teal-50">
      {/* Persistent Sidebar on large screens */}
      <div className="hidden lg:flex lg:flex-col lg:w-72 bg-white border-r border-gray-200 shadow-sm">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-purple-50 to-indigo-50">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <MessageCircle className="h-5 w-5 text-purple-600" />
            Chat History
          </h2>
          <button
            onClick={() => loadSessions()}
            className="text-xs px-3 py-1.5 rounded-lg bg-white hover:bg-purple-50 border border-purple-200 text-purple-700 flex items-center gap-1.5 transition-all hover:shadow-sm"
            title="Refresh chat history"
          >
            <RefreshCw className={sessionsLoading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
            <span className="font-medium">Refresh</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {sessions.map(session => (
            <motion.div
              key={session.session_id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`group w-full p-3 rounded-lg transition-all border cursor-pointer hover:shadow-md ${currentSession === session.session_id ? 'bg-gradient-to-r from-purple-100 to-indigo-100 border-purple-300 shadow-sm' : 'bg-white border-gray-200 hover:border-purple-200'}`}
            >
              <div className="flex items-start justify-between gap-2">
                <button onClick={() => loadSession(session.session_id)} className="text-left flex-1 min-w-0">
                  {editing.id === session.session_id ? (
                    <div className="flex items-center gap-2">
                      <input
                        className="flex-1 text-sm border rounded px-2 py-1"
                        value={editing.title}
                        onChange={(e) => setEditing(prev => ({ ...prev, title: e.target.value }))}
                        autoFocus
                        onClick={(e) => e.stopPropagation()}
                      />
                      <button title="Save" onClick={(e) => { e.stopPropagation(); commitInlineRename(session); }} className="p-1 bg-green-50 hover:bg-green-100 rounded"><span className="text-green-700 text-xs font-semibold">✓</span></button>
                      <button title="Cancel" onClick={(e) => { e.stopPropagation(); cancelInlineRename(); }} className="p-1 bg-gray-50 hover:bg-gray-100 rounded"><span className="text-gray-700 text-xs font-semibold">×</span></button>
                    </div>
                  ) : (
                    <div className="font-medium text-sm text-gray-900 truncate flex items-center gap-2" title={session.title || 'Untitled Chat'}>
                      {session.title || 'Untitled Chat'}
                      {session.pinned ? <span className="text-yellow-600">📌</span> : null}
                      {session.bookmarked ? <span className="text-green-600">🔖</span> : null}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1 flex items-center justify-between min-w-0">
                    <span className="truncate" title={session.subject}>{session.subject}</span>
                    <span className="flex items-center gap-2">
                      {sessionLoadingId === session.session_id ? (<Loader className="h-3 w-3 animate-spin" />) : null}
                      <span className="truncate" title={`${session.message_count || 0} msgs • ${formatLastUpdated(session.last_updated)}`}>{(session.message_count || 0)} msgs • {formatLastUpdated(session.last_updated)}</span>
                    </span>
                  </div>
                </button>
                <div className="relative">
                  <button
                    title="More"
                    onClick={(e) => { e.stopPropagation(); setMenuOpenId(prev => prev === session.session_id ? null : session.session_id); }}
                    className="px-2 py-1 hover:bg-gray-100 rounded text-gray-600 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                    aria-label="More options"
                  >
                    {/* Fallback kebab icon */}
                    <span style={{fontSize:'16px', lineHeight: 1}}>⋮</span>
                  </button>
                  <AnimatePresence>
                  {menuOpenId === session.session_id && (
                    <motion.div
                      initial={{ opacity: 0, y: -4, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -4, scale: 0.98 }}
                      transition={{ duration: 0.12 }}
                      className="absolute right-0 mt-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
                    >
                      <button className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50" onClick={(e) => { e.stopPropagation(); setEditing({ id: session.session_id, title: session.title || '' }); setMenuOpenId(null); }}>Rename</button>
                      <button className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50" onClick={(e) => { e.stopPropagation(); togglePinSession(session); setMenuOpenId(null); }}>{session.pinned ? 'Unpin' : 'Pin'}</button>
                      <button className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50" onClick={(e) => { e.stopPropagation(); toggleBookmarkSession(session); setMenuOpenId(null); }}>{session.bookmarked ? 'Unbookmark' : 'Bookmark'}</button>
                      <button className="w-full text-left px-3 py-2 text-sm hover:bg-red-50 text-red-600 border-t border-gray-100" onClick={(e) => { e.stopPropagation(); requestDeleteSession(session); setMenuOpenId(null); }}>Delete</button>
                    </motion.div>
                  )}
                  </AnimatePresence>
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
              <MessageCircle className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="text-sm font-medium text-gray-600">No chat sessions yet</p>
              <p className="text-xs mt-2 text-gray-500">Start a new conversation to begin learning!</p>
            </motion.div>
          )}
          {sessionsLoading && sessions.length === 0 && (
            <div className="text-center py-12">
              <Loader className="h-6 w-6 mx-auto animate-spin text-purple-600" />
              <p className="text-xs mt-2 text-gray-500">Loading chat history...</p>
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

              {/* Sidebar */}
              <motion.div
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: 'spring', damping: 25 }}
                className="fixed left-0 top-0 h-full w-72 bg-white shadow-2xl z-50 p-6 overflow-y-auto"
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-bold text-gray-900">Chat History</h2>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => loadSessions()}
                      className="text-xs px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 border border-purple-200 text-purple-700 flex items-center gap-1.5 transition-all"
                      title="Refresh chat history"
                    >
                      <RefreshCw className={sessionsLoading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
                      <span className="font-medium">Refresh</span>
                    </button>
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
                  {sessions.map((session) => (
                    <motion.div
                      key={session.session_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2 }}
                      className={`w-full p-3 rounded-lg border transition-all ${
                        currentSession === session.session_id ? 'bg-gradient-to-r from-purple-100 to-indigo-100 border-purple-300 shadow-sm' : 'bg-white border-gray-200 hover:border-purple-200 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <button
                          onClick={() => loadSession(session.session_id)}
                          className="text-left flex-1"
                        >
                          <div className="font-medium text-sm text-gray-900 truncate">{session.title || 'Untitled Chat'}</div>
                          <div className="text-xs text-gray-500 mt-0.5 flex items-center justify-between">
                            <span>{session.subject}</span>
                            <span className="flex items-center gap-2">
                              {sessionLoadingId === session.session_id ? (<Loader className="h-3 w-3 animate-spin" />) : null}
                              <span>{(session.message_count || 0)} msgs • {formatLastUpdated(session.last_updated)}</span>
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
                      <MessageCircle className="h-12 w-12 mx-auto mb-3 opacity-40" />
                      <p className="text-sm font-medium text-gray-600">No chat sessions yet</p>
                      <p className="text-xs mt-2 text-gray-500">Start a new conversation to begin learning!</p>
                    </motion.div>
                  )}
                  {sessionsLoading && sessions.length === 0 && (
                    <div className="text-center py-12">
                      <Loader className="h-6 w-6 mx-auto animate-spin text-purple-600" />
                      <p className="text-xs mt-2 text-gray-500">Loading chat history...</p>
                    </div>
                  )}
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <motion.div
          animate={{
            height: headerCollapsed ? '80px' : '140px'
          }}
          transition={{ duration: 0.3 }}
          className="bg-white border-b border-gray-200 shadow-sm overflow-hidden"
        >
          <div className="max-w-5xl mx-auto px-6 h-full flex flex-col justify-center">
            {/* Top row - Always visible */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowSidebar(true)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
                >
                  <Menu className="h-6 w-6 text-gray-600" />
                </button>
                
                <div className="flex items-center space-x-3">
                  <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-3 rounded-xl">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">AI Tutor</h1>
                    {headerCollapsed && (
                      <p className="text-xs text-gray-500">Neuro-Symbolic Learning</p>
                    )}
                  </div>
                </div>

                {headerCollapsed && (
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="ml-4 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {SUBJECTS.map((subj) => (
                      <option key={subj} value={subj}>
                        {subj}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <button
                onClick={startNewChat}
                className="hidden lg:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all"
              >
                <Plus className="h-4 w-4" />
                <span>New Chat</span>
              </button>
            </div>

            {/* Expanded header content */}
            {!headerCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4"
              >
                <p className="text-gray-600 text-sm mb-3">
                  Your personal learning companion - practical, verified, student-centric
                </p>

                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent w-64"
                >
                  {SUBJECTS.map((subj) => (
                    <option key={subj} value={subj}>
                      {subj}
                    </option>
                  ))}
                </select>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {/* Welcome Screen */}
            {showWelcome && messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12"
              >
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 mb-6">
                  <Brain className="h-10 w-10 text-white" />
                </div>

                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  Welcome to AI Tutor 3.0
                </h2>
                <p className="text-gray-600 mb-2">
                  Neuro-Symbolic Learning • Indian Student-Centric
                </p>
                <p className="text-sm text-gray-500 mb-8">
                  Real-life examples • Karnataka context • Practical learning
                </p>

                {/* Quick prompts */}
                {defaultPrompts.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    {defaultPrompts.map((prompt, index) => {
                      // Handle both string prompts and object prompts {text, type}
                      const promptText = typeof prompt === 'string' ? prompt : prompt.text || prompt;
                      return (
                        <motion.button
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          onClick={() => handleQuickSend(promptText)}
                          className="p-4 bg-white rounded-xl border-2 border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all text-left group"
                        >
                          <div className="flex items-start space-x-3">
                            <Sparkles className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {promptText}
                            </p>
                          </div>
                        </motion.button>
                      );
                    })}
                  </div>
                )}
              </motion.div>
            )}

            {/* Messages */}
            <div className="space-y-6">
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
                        <div className="max-w-2xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-2xl px-6 py-4 shadow-lg">
                          <p className="leading-relaxed">{message.content}</p>
                          <p className="text-xs text-purple-200 mt-2">
                            {new Date(message.timestamp).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    )}

                    {message.type === 'ai' && (
                      <div className="flex justify-start">
                        <div className="max-w-4xl w-full">
                          <div className="flex items-start space-x-3 mb-2">
                            <div className="bg-gradient-to-r from-green-500 to-teal-500 p-2 rounded-lg">
                              <Brain className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">Dhruv AI Mentor</p>
                              <p className="text-xs text-gray-500">
                                {new Date(message.timestamp).toLocaleTimeString([], {
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                                {message.generation_time && (
                                  <span className="ml-2">
                                    • {message.generation_time.toFixed(1)}s
                                  </span>
                                )}
                              </p>
                            </div>
                          </div>
                          
                          <MentorResponseV2 
                            response={{
                              ...message.content,
                              // CRITICAL: Pass teaching_visual and visual_data from message
                              teaching_visual: message.teaching_visual || message.content?.teaching_visual,
                              visual_data: message.visual_data || message.content?.visual_data
                            }}
                            onInteraction={(action, data) => {
                              console.log('User interaction:', action, data);
                              
                              // Handle follow-up question suggestions
                              if (action === 'followup') {
                                const followUpMap = {
                                  'practice': 'Give me a practice problem on this',
                                  'example': 'Show me more examples',
                                  'application': 'Where is this used in real life?',
                                  'related': 'What other concepts are related to this?'
                                };
                                const followUpQuestion = followUpMap[data];
                                if (followUpQuestion) {
                                  setInputMessage(followUpQuestion);
                                  inputRef.current?.focus();
                                }
                              }
                              
                              // Track feedback
                              if (action === 'feedback_positive' || action === 'feedback_negative') {
                                // TODO: Send to analytics
                                console.log('Feedback:', action);
                              }
                            }}
                          />
                        </div>
                      </div>
                    )}

                    {message.type === 'error' && (
                      <div className="flex justify-center">
                        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-6 py-4 max-w-2xl">
                          <p className="text-sm">{message.content}</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* AI Typing Indicator */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-white rounded-2xl px-6 py-4 shadow-md border border-gray-200">
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-sm text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        {/* Input Bar */}
        <div className="border-t border-gray-200 bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-end space-x-3"
            >
              <div className="flex-1">
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
                  placeholder="Ask anything — I'll explain & mentor you 💡"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none resize-none transition-all"
                  rows="2"
                  disabled={loading}
                />
                <div className="flex items-center justify-between mt-2 px-2">
                  <p className="text-xs text-gray-500">
                    Subject: <span className="font-medium text-purple-600">{selectedSubject}</span>
                  </p>
                  <p className="text-xs text-gray-500">
                    Press Enter to send • Shift+Enter for new line
                  </p>
                </div>
              </div>

              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <Loader className="h-5 w-5 animate-spin" />
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    <span className="hidden sm:inline">Send</span>
                  </>
                )}
              </button>
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







