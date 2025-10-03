import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import FormattedAIResponse, { DualResponseContainer, formatMathExpressions } from './FormattedAIResponse';
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
  History
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AITutor() {
  const { user } = useAuth();
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

  // Phase A: Complete Input Methods states
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [showContextPin, setShowContextPin] = useState(false);
  const [contextPinData, setContextPinData] = useState([]);
  const [selectedContext, setSelectedContext] = useState(null);
  const [availableContexts, setAvailableContexts] = useState([]);
  const fileInputRef = useRef(null);

  const subjects = {
    'JEE': ['Mathematics', 'Physics', 'Chemistry'],
    'NEET': ['Physics', 'Chemistry', 'Biology'],
    'UPSC': ['General Studies', 'Current Affairs', 'History', 'Geography', 'Polity']
  };

  useEffect(() => {
    fetchChatSessions();
    initializeSpeechRecognition();
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
      const response = await axios.get(`${API}/chat/sessions`);
      setSessions(response.data.sessions);
    } catch (error) {
      console.error('Failed to fetch chat sessions:', error);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/chat/${sessionId}/messages`);
      setMessages(response.data.messages);
      setCurrentSession(sessionId);
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    setLoading(true);
    const messageToSend = currentMessage;
    setCurrentMessage('');

    try {
      let response;
      
      // Choose API endpoint based on AI mode
      if (aiMode === 'dual') {
        response = await axios.post(`${API}/ai/dual-response`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: currentSession
        });
      } else if (aiMode === 'mentor') {
        response = await axios.post(`${API}/ai/mentor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: currentSession
        });
      } else { // professor
        response = await axios.post(`${API}/ai/professor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: currentSession
        });
      }

      const newMessage = response.data;
      
      // Update current session if it's a new one
      if (!currentSession) {
        setCurrentSession(newMessage.session_id);
        fetchChatSessions(); // Refresh sessions list
      }

      // Track scenario type for dual mode
      if (aiMode === 'dual' && newMessage.dual_response?.scenario_type) {
        setLastScenarioType(newMessage.dual_response.scenario_type);
      }

      // Add message to current conversation
      setMessages(prev => [...prev, newMessage]);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      // Re-add message back to input on error
      setCurrentMessage(messageToSend);
    } finally {
      setLoading(false);
    }
  };

  const startNewSession = () => {
    setCurrentSession(null);
    setMessages([]);
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

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100">
      {/* Sidebar - Chat Sessions */}
      <div className="w-80 bg-white/95 backdrop-blur-sm border-r border-gray-200/60 flex flex-col shadow-lg">
        <div className="p-4 border-b border-gray-200/60 bg-gradient-to-r from-gray-800 to-slate-700 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold">Dhruv AI</h2>
            </div>
            <Button 
              size="sm" 
              onClick={startNewSession}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm border-white/30 text-white hover:text-white transition-all duration-200"
              variant="outline"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
          
          <div className="space-y-3">
            <div className="relative">
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger className="bg-white/50 border-white/30 text-white placeholder:text-white/70">
                  <BookOpen className="h-4 w-4 mr-2" />
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

            {/* Enhanced Session Search */}
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-3 border border-white/20 mb-3">
              <div className="flex items-center space-x-2">
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search conversations..."
                  className="bg-white/30 border-white/20 text-white placeholder:text-white/70 text-sm h-8"
                />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={exportConversation}
                  disabled={messages.length === 0}
                  className="text-white/80 hover:text-white hover:bg-white/20 h-8 w-8 p-0"
                  title="Export conversation"
                >
                  <FileText className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Enhanced AI Mode Selection */}
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 border border-white/20">
              <label className="text-xs font-medium text-white/90 mb-3 block flex items-center">
                <Sparkles className="h-3 w-3 mr-1" />
                AI Intelligence Mode
              </label>
              <Select value={aiMode} onValueChange={setAiMode}>
                <SelectTrigger className="bg-white/30 border-white/20 text-white h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dual">
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-2 text-blue-600" />
                      <div>
                        <div className="font-medium">Dual Intelligence</div>
                        <div className="text-xs text-gray-500">Mentor + Professor</div>
                      </div>
                    </div>
                  </SelectItem>
                  <SelectItem value="mentor">
                    <div className="flex items-center">
                      <Heart className="h-4 w-4 mr-2 text-green-600" />
                      <div>
                        <div className="font-medium">Mentor Mode</div>
                        <div className="text-xs text-gray-500">Motivational & Adaptive</div>
                      </div>
                    </div>
                  </SelectItem>
                  <SelectItem value="professor">
                    <div className="flex items-center">
                      <GraduationCap className="h-4 w-4 mr-2 text-purple-600" />
                      <div>
                        <div className="font-medium">Professor Mode</div>
                        <div className="text-xs text-gray-500">Technical & Rigorous</div>
                      </div>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
              
              {aiMode === 'dual' && (
                <div className="mt-3 p-2 bg-white/20 rounded-lg">
                  <div className="flex items-center text-xs text-white/90">
                    <Target className="h-3 w-3 mr-1" />
                    Smart routing: AI selects the best persona for your question
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Simplified Sessions List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-700">
              {searchQuery ? `Found ${filteredSessions.length}` : 'Chat History'}
            </h3>
            {sessions.length > 0 && (
              <span className="text-xs text-gray-500">{sessions.length} total</span>
            )}
          </div>
          <div className="space-y-1">
            {filteredSessions.length > 0 ? (
              filteredSessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => loadSession(session.session_id)}
                  className={`flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition-colors text-sm ${
                    currentSession === session.session_id
                      ? 'bg-gray-100 text-gray-900 border-l-3 border-gray-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center flex-1 min-w-0">
                    <MessageCircle className="h-3 w-3 mr-2 flex-shrink-0 text-gray-400" />
                    <span className="truncate font-medium">{session.title}</span>
                    <Badge variant="outline" className="ml-2 text-xs bg-gray-50 text-gray-600 border-gray-200 flex-shrink-0">
                      {session.subject}
                    </Badge>
                  </div>
                  <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
                    {formatTime(session.last_updated)}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <MessageCircle className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No conversations yet</p>
                <p className="text-xs text-gray-400">Start chatting to see your history</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Professional Chat Header */}
        <div className="bg-white border-b border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-r from-gray-700 to-gray-800 rounded-lg flex items-center justify-center mr-4 shadow-md">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Dhruv AI - {selectedSubject} Tutor
                </h1>
                <div className="flex items-center mt-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <p className="text-sm text-gray-600">
                    {aiMode === 'dual' && 'Dual-layer AI: Mentor + Professor intelligence'}
                    {aiMode === 'mentor' && 'Mentor mode: Adaptive, friendly, motivational'}
                    {aiMode === 'professor' && 'Professor mode: Rule-based, verified reasoning'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {aiMode === 'dual' && (
                <Badge variant="outline" className="flex items-center bg-gray-50 text-gray-700 border-gray-300">
                  <Users className="h-3 w-3 mr-1" />
                  Dual Intelligence
                </Badge>
              )}
              {aiMode === 'mentor' && (
                <Badge variant="outline" className="flex items-center bg-green-50 text-green-700 border-green-300">
                  <Heart className="h-3 w-3 mr-1" />
                  Mentor Mode
                </Badge>
              )}
              {aiMode === 'professor' && (
                <Badge variant="outline" className="flex items-center bg-purple-50 text-purple-700 border-purple-300">
                  <GraduationCap className="h-3 w-3 mr-1" />
                  Professor Mode
                </Badge>
              )}
              <Badge variant="outline" className="flex items-center bg-gray-50 text-gray-600 border-gray-300">
                <Shield className="h-3 w-3 mr-1" />
                Verified AI
              </Badge>
            </div>
          </div>
        </div>

        {/* Professional Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <div className="max-w-5xl mx-auto space-y-8">
            {messages.length === 0 ? (
              // Welcome Message
              <div className="text-center py-12">
                <div className="flex justify-center items-center mb-6 space-x-4">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                    <Heart className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                    <Brain className="h-10 w-10 text-blue-600" />
                  </div>
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                    <GraduationCap className="h-8 w-8 text-purple-600" />
                  </div>
                </div>
                
                <h3 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-800 bg-clip-text text-transparent mb-3">
                  Welcome to Your Trusted, Hallucination-Free AI Tutor! ✨
                </h3>
                
                <p className="text-gray-700 mb-6 max-w-2xl mx-auto text-lg leading-relaxed">
                  Experience personalized, verified AI tutoring for <span className="font-semibold text-blue-600">{selectedSubject}</span> at a fraction of coaching costs. Our revolutionary dual intelligence ensures:
                </p>
                
                <div className="flex justify-center items-center space-x-6 mb-6 text-sm">
                  <div className="flex items-center text-green-600">
                    <div className="h-2 w-2 bg-green-500 rounded-full mr-1"></div>
                    <span>Zero Hallucinations</span>
                  </div>
                  <div className="flex items-center text-blue-600">
                    <div className="h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
                    <span>Verified Accuracy</span>
                  </div>
                  <div className="flex items-center text-purple-600">
                    <div className="h-2 w-2 bg-purple-500 rounded-full mr-1"></div>
                    <span>Personalized Learning</span>
                  </div>
                </div>

                <div className="flex justify-center space-x-6 mb-8">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <Heart className="h-6 w-6 text-green-600" />
                    </div>
                    <h4 className="text-sm font-semibold text-gray-900">Mentor</h4>
                    <p className="text-xs text-gray-600">Adaptive • Motivational</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <GraduationCap className="h-6 w-6 text-purple-600" />
                    </div>
                    <h4 className="text-sm font-semibold text-gray-900">Professor</h4>
                    <p className="text-xs text-gray-600">Verified • Rigorous</p>
                  </div>
                </div>

                {/* Enhanced Sample Questions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  <Card className="group cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-purple-50 to-violet-50 hover:from-purple-100 hover:to-violet-100" onClick={() => setCurrentMessage("Explain the concept of limits in calculus")}>
                    <CardContent className="p-6 text-left">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-violet-600 rounded-lg flex items-center justify-center mr-3">
                            <GraduationCap className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-sm font-semibold text-purple-700">Professor Leads</span>
                        </div>
                        <Badge className="text-xs bg-purple-100 text-purple-700 border-purple-200">Fact/Concept</Badge>
                      </div>
                      <p className="text-sm text-gray-800 leading-relaxed group-hover:text-gray-900">Explain the concept of limits in calculus</p>
                      <div className="mt-4 flex items-center text-xs text-purple-600">
                        <Sparkles className="h-3 w-3 mr-1" />
                        <span>Click to ask this question</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="group cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100" onClick={() => setCurrentMessage("I'm feeling stressed about my upcoming JEE exam. Can you help me plan my studies?")}>
                    <CardContent className="p-6 text-left">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mr-3">
                            <Heart className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-sm font-semibold text-green-700">Mentor Leads</span>
                        </div>
                        <Badge className="text-xs bg-green-100 text-green-700 border-green-200">Guidance</Badge>
                      </div>
                      <p className="text-sm text-gray-800 leading-relaxed group-hover:text-gray-900">I'm feeling stressed about my upcoming JEE exam. Can you help me plan my studies?</p>
                      <div className="mt-4 flex items-center text-xs text-green-600">
                        <Sparkles className="h-3 w-3 mr-1" />
                        <span>Click to ask this question</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="group cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-purple-50 to-violet-50 hover:from-purple-100 hover:to-violet-100" onClick={() => setCurrentMessage("Solve this quadratic equation step by step: x² - 5x + 6 = 0")}>
                    <CardContent className="p-6 text-left">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-violet-600 rounded-lg flex items-center justify-center mr-3">
                            <GraduationCap className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-sm font-semibold text-purple-700">Professor Leads</span>
                        </div>
                        <Badge className="text-xs bg-purple-100 text-purple-700 border-purple-200">Problem Solving</Badge>
                      </div>
                      <p className="text-sm text-gray-800 leading-relaxed group-hover:text-gray-900">Solve this quadratic equation step by step: x² - 5x + 6 = 0</p>
                      <div className="mt-4 flex items-center text-xs text-purple-600">
                        <Sparkles className="h-3 w-3 mr-1" />
                        <span>Click to ask this question</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="group cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100" onClick={() => setCurrentMessage("What are some effective study techniques for competitive exams?")}>
                    <CardContent className="p-6 text-left">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mr-3">
                            <Users className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-sm font-semibold text-blue-700">Both Contribute</span>
                        </div>
                        <Badge className="text-xs bg-blue-100 text-blue-700 border-blue-200">General Inquiry</Badge>
                      </div>
                      <p className="text-sm text-gray-800 leading-relaxed group-hover:text-gray-900">What are some effective study techniques for competitive exams?</p>
                      <div className="mt-4 flex items-center text-xs text-blue-600">
                        <Sparkles className="h-3 w-3 mr-1" />
                        <span>Click to ask this question</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div className="mt-10 p-6 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 rounded-2xl max-w-3xl mx-auto border border-blue-200/50 shadow-lg">
                  <div className="flex items-center justify-center mb-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mr-3">
                      <Sparkles className="h-4 w-4 text-white" />
                    </div>
                    <span className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Intelligent Question Routing</span>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed text-center">
                    Our advanced AI automatically analyzes your question and routes it to the most appropriate persona—whether you need 
                    <span className="font-semibold text-purple-600"> technical expertise (Professor)</span> or 
                    <span className="font-semibold text-green-600"> motivational guidance (Mentor)</span>—ensuring you always get the perfect response for your learning needs.
                  </p>
                  <div className="mt-4 flex items-center justify-center space-x-6 text-xs">
                    <div className="flex items-center text-purple-600">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                      <span>Technical Questions → Professor</span>
                    </div>
                    <div className="flex items-center text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span>Guidance Questions → Mentor</span>
                    </div>
                    <div className="flex items-center text-blue-600">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      <span>Complex Questions → Both</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              // Chat Messages
              messages.map((message, index) => (
                <div key={index} className="space-y-4">
                  {/* Enhanced User Message */}
                  <div className="flex justify-end">
                    <div className="max-w-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl rounded-br-md p-5 shadow-lg transform hover:scale-[1.02] transition-transform duration-200">
                      <div className="flex items-start space-x-3">
                        <div className="flex-1">
                          <p className="text-sm leading-relaxed">{message.message}</p>
                        </div>
                        <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-xs font-semibold">You</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-white/20">
                        <div className="flex items-center space-x-2 text-xs text-blue-100">
                          <Clock className="h-3 w-3" />
                          <span>{formatTime(message.timestamp)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                          <span className="text-xs text-blue-100">Delivered</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Response */}
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
                          
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="prose prose-sm max-w-none">
                              <div 
                                className="whitespace-pre-wrap text-gray-800"
                                dangerouslySetInnerHTML={{
                                  __html: formatMathExpressions(message.response)
                                }}
                              />
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
                </div>
              ))
            )}
            
            {/* Enhanced Loading indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gradient-to-r from-white to-blue-50 rounded-2xl p-6 shadow-lg border border-blue-100 max-w-md">
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center animate-pulse">
                        <Brain className="h-5 w-5 text-white" />
                      </div>
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm font-medium text-gray-800">Dhruv AI is thinking</span>
                        <div className="flex space-x-1">
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                      <div className="flex items-center text-xs text-gray-500">
                        {aiMode === 'dual' && (
                          <>
                            <Users className="h-3 w-3 mr-1" />
                            <span>Coordinating Mentor + Professor responses...</span>
                          </>
                        )}
                        {aiMode === 'mentor' && (
                          <>
                            <Heart className="h-3 w-3 mr-1" />
                            <span>Crafting personalized guidance...</span>
                          </>
                        )}
                        {aiMode === 'professor' && (
                          <>
                            <GraduationCap className="h-3 w-3 mr-1" />
                            <span>Analyzing with academic precision...</span>
                          </>
                        )}
                      </div>
                      <div className="mt-2 bg-gray-200 rounded-full h-1 overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* File Type Support Information */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 p-3 mx-6 rounded-lg">
          <div className="flex items-start space-x-3">
            <div className="bg-green-100 rounded-full p-1">
              <Sparkles className="h-4 w-4 text-green-600" />
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-green-800 mb-1">🚀 Cutting-Edge AI File Analysis</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                <div className="flex items-center space-x-2">
                  <ImageIcon className="h-4 w-4 text-blue-500" />
                  <span className="text-gray-700"><strong>Images:</strong> JPEG, JPG, PNG, WebP</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FileIcon className="h-4 w-4 text-red-500" />
                  <span className="text-gray-700"><strong>Documents:</strong> PDF files</span>
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                ✨ <strong>GPT-4o Vision</strong> instantly extracts text, solves math problems, analyzes diagrams • 
                📏 <strong>Max:</strong> 25MB • 
                ⚡ <strong>Processing:</strong> 5-15 seconds
              </p>
            </div>
          </div>
        </div>

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
                        🚀 AI-Powered Document Analysis
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">
                        Upload any image or PDF for instant AI analysis using cutting-edge GPT-4o Vision
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 mb-3">
                        <div className="flex items-center justify-center space-x-1">
                          <ImageIcon className="h-4 w-4 text-green-500" />
                          <span>JPEG, PNG, WebP</span>
                        </div>
                        <div className="flex items-center justify-center space-x-1">
                          <FileIcon className="h-4 w-4 text-red-500" />
                          <span>PDF Documents</span>
                        </div>
                      </div>
                      <p className="text-xs text-blue-600 font-medium">Max size: 25MB • Instant processing</p>
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
                          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.type}
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

        {/* Professional Input Area */}
        <div className="bg-white border-t border-gray-200 p-6 shadow-sm">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
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
                      ? '🎯 Drop your file here for instant AI analysis!' 
                      : loading 
                        ? '🤖 AI is processing...' 
                        : `💬 Ask me anything about ${selectedSubject} or drag & drop files...`
                  }
                  className={`resize-none border-2 ${
                    dragOver 
                      ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg scale-[1.01]' 
                      : isListening 
                        ? 'border-red-400 bg-red-50' 
                        : loading
                          ? 'border-blue-300 bg-blue-50'
                          : 'border-gray-300 focus:border-blue-500 hover:border-gray-400'
                  } rounded-lg transition-all duration-300 shadow-sm focus:shadow-md`}
                  rows={3}
                  disabled={loading}
                />
                {currentMessage.trim() && (
                  <div className="absolute bottom-3 right-16 text-xs text-gray-400">
                    {currentMessage.length} characters
                  </div>
                )}
                
                {/* Input Control Buttons */}
                <div className="absolute bottom-3 right-3 flex items-center space-x-1">
                  {/* Enhanced File Upload Button */}
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => fileInputRef.current?.click()}
                    className="h-8 w-8 p-0 text-gray-500 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                    title="📁 Upload Image or PDF (JPEG, PNG, WebP, PDF - Max 25MB)"
                    disabled={loading}
                  >
                    <Upload className="h-4 w-4" />
                  </Button>
                  
                  {/* Context Pin Button */}
                  <Button
                    type="button"
                    size="sm"
                    variant={selectedContext ? "default" : "ghost"}
                    onClick={() => {
                      if (showContextPin) {
                        setShowContextPin(false);
                      } else {
                        loadAvailableContexts();
                        setShowContextPin(true);
                      }
                    }}
                    className={`h-8 w-8 p-0 ${selectedContext ? 'bg-purple-600 text-white' : 'text-gray-500 hover:text-purple-600'}`}
                    title="Connect with previous content"
                    disabled={loading}
                  >
                    <Pin className="h-4 w-4" />
                  </Button>

                  {recognition && (
                    <Button
                      type="button"
                      size="sm"
                      variant={isListening ? "destructive" : "ghost"}
                      onClick={isListening ? stopVoiceInput : startVoiceInput}
                      className={`h-8 w-8 p-0 ${isListening ? 'animate-pulse bg-red-500 text-white' : 'hover:bg-gray-100'}`}
                      title={isListening ? 'Stop recording' : 'Voice input'}
                      disabled={loading}
                    >
                      {isListening ? (
                        <MicOff className="h-4 w-4" />
                      ) : (
                        <Mic className="h-4 w-4 text-gray-600" />
                      )}
                    </Button>
                  )}
                  
                  {/* Quick Suggestions Toggle */}
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowQuickSuggestions(!showQuickSuggestions)}
                    className="h-8 w-8 p-0 text-gray-500 hover:text-gray-700"
                    title="Quick suggestions"
                    disabled={loading}
                  >
                    <Lightbulb className="h-3 w-3" />
                  </Button>
                </div>

                {/* Enhanced Hidden File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp,application/pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  multiple={false}
                />
              </div>
              
              <Button 
                onClick={sendMessage}
                disabled={loading || !currentMessage.trim()}
                className="bg-gray-800 hover:bg-gray-900 px-6 py-3 h-auto rounded-lg shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span className="text-sm">Sending...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Send className="h-4 w-4" />
                    <span className="text-sm font-medium">Send</span>
                  </div>
                )}
              </Button>
            </div>

            {/* Quick Suggestions Panel */}
            {showQuickSuggestions && (
              <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-gray-800 flex items-center">
                    <Lightbulb className="h-4 w-4 mr-2 text-blue-600" />
                    Quick Questions for {selectedSubject}
                  </h4>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowQuickSuggestions(false)}
                    className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </Button>
                </div>
                <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto">
                  {getSubjectSuggestions().map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setCurrentMessage(suggestion);
                        setShowQuickSuggestions(false);
                      }}
                      className="text-left text-xs p-2 bg-white rounded-lg hover:bg-blue-50 transition-colors border border-gray-200 hover:border-blue-300"
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex items-center justify-between mt-4 px-2">
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  <span>Press Enter to send, Shift+Enter for new line</span>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                {aiMode === 'dual' && (
                  <div className="flex items-center text-xs text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
                    <Users className="h-3 w-3 mr-1" />
                    <span className="font-medium">Dual Intelligence Active</span>
                  </div>
                )}
                {aiMode === 'mentor' && (
                  <div className="flex items-center text-xs text-green-700 bg-green-100 px-3 py-1 rounded-full">
                    <Heart className="h-3 w-3 mr-1" />
                    <span className="font-medium">Mentor Mode</span>
                  </div>
                )}
                {aiMode === 'professor' && (
                  <div className="flex items-center text-xs text-purple-700 bg-purple-100 px-3 py-1 rounded-full">
                    <GraduationCap className="h-3 w-3 mr-1" />
                    <span className="font-medium">Professor Mode</span>
                  </div>
                )}
                <div className="flex items-center text-xs text-gray-500 space-x-4">
                  <div className="flex items-center">
                    <Shield className="h-3 w-3 mr-1" />
                    <span>Verified AI</span>
                  </div>
                  <div className="hidden md:flex items-center space-x-2 text-gray-400">
                    <span>Shortcuts:</span>
                    <code className="bg-gray-100 px-1 rounded text-xs">Ctrl+/</code>
                    <span>Suggestions</span>
                    <code className="bg-gray-100 px-1 rounded text-xs">Ctrl+N</code>
                    <span>New Chat</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}