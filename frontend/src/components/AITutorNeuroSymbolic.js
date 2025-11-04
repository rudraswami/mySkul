/**
 * AI Tutor - Neuro-Symbolic v3.0
 * Indian Student-Centric, Karnataka-Friendly Learning Experience
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import {
  Brain,
  Send,
  Plus,
  Menu,
  ChevronLeft,
  Loader,
  Book,
  Sparkles
} from 'lucide-react';
import NeuroSymbolicResponse from './neuro-symbolic/NeuroSymbolicResponse';
import MentorResponseV2 from './mentor-v2/MentorResponseV2';
import UpgradeModal from './UpgradeModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function AITutorNeuroSymbolic() {
  const { user } = useAuth();
  const { checkFeatureAccess, trackFeatureUsage } = useSubscription();

  // Core state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);

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
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await fetch(`${BACKEND_URL}/api/ai/chat/sessions`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
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

      // Add AI response
      const aiMsg = {
        type: 'ai',
        content: data.response,
        timestamp: new Date().toISOString(),
        message_id: data.message_id,
        emotion_detected: data.emotion_detected,
        generation_time: data.generation_time
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
  };

  // Load session
  const loadSession = async (sessionId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(
        `${BACKEND_URL}/api/ai/chat/sessions/${sessionId}/messages`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        const formattedMessages = data.messages.map(msg => ({
          type: msg.type,
          content: msg.type === 'ai' ? msg.ai_response : msg.content,
          timestamp: msg.timestamp,
          message_id: msg.message_id
        }));
        setMessages(formattedMessages);
        setCurrentSession(sessionId);
        setShowSidebar(false);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-teal-50">
      {/* Overlay Sidebar - Chat History */}
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
                <button
                  onClick={() => setShowSidebar(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-2">
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => loadSession(session.session_id)}
                    className={`w-full text-left p-3 rounded-lg hover:bg-purple-50 transition-colors ${
                      currentSession === session.session_id
                        ? 'bg-purple-100 border border-purple-300'
                        : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className="font-medium text-sm text-gray-900 truncate">
                      {session.title || 'Untitled Chat'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {session.subject}
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

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
                            response={message.content}
                            onInteraction={(section) => {
                              console.log('User revealed section:', section);
                              // Can track engagement here
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
    </div>
  );
}
