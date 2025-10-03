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
  History,
  Plus,
  TrendingDown,
  TrendingUp,
  AlertCircle
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
      
      // Generate session ID if not exists
      const sessionId = currentSession || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Choose API endpoint based on AI mode
      if (aiMode === 'dual') {
        response = await axios.post(`${API}/ai/dual-response`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        });
      } else if (aiMode === 'mentor') {
        response = await axios.post(`${API}/ai/mentor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        });
      } else { // professor
        response = await axios.post(`${API}/ai/professor-only`, {
          message: messageToSend,
          subject: selectedSubject,
          session_id: sessionId
        });
      }

      const newMessage = response.data;
      
      // Update current session if it's a new one
      if (!currentSession) {
        setCurrentSession(sessionId);
        fetchChatSessions(); // Refresh sessions list
      }

      // Track scenario type for dual mode
      if (aiMode === 'dual' && newMessage.dual_response?.scenario_type) {
        setLastScenarioType(newMessage.dual_response.scenario_type);
      }

      // Add personalization info to the message
      const enhancedMessage = {
        ...newMessage,
        personalized: newMessage.dual_response?.personalized || false,
        difficulty_level: newMessage.dual_response?.user_difficulty_level || personalizedDifficulty,
        topic_detected: newMessage.topic_detected || 'General'
      };

      // Add message to current conversation
      setMessages(prev => [...prev, enhancedMessage]);
      
      // Update personalized difficulty if provided
      if (newMessage.dual_response?.user_difficulty_level) {
        setPersonalizedDifficulty(newMessage.dual_response.user_difficulty_level);
      }
      
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

  // Phase D: Enhanced Action Button Handlers
  const handlePracticeMore = async (originalQuestion, subject, topic) => {
    try {
      const response = await axios.post(`${API}/actions/practice-more`, {
        original_question: originalQuestion,
        subject: subject || selectedSubject,
        topic: topic || 'General',
        education_standard: 'JEE', // This should come from user profile
        difficulty_level: 'similar'
      });
      
      // You could display the practice problems in a modal or new section
      console.log('Practice problems generated:', response.data);
      // For now, we'll just log - you can implement a modal to show the problems
      
    } catch (error) {
      console.error('Failed to generate practice problems:', error);
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
      
      console.log('Note saved:', response.data);
      // You could show a success message here
      
    } catch (error) {
      console.error('Failed to save note:', error);
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

  // Group sessions by subject automatically
  const groupedSessions = React.useMemo(() => {
    const groups = {};
    filteredSessions.forEach(session => {
      const subject = session.subject || 'General';
      if (!groups[subject]) {
        groups[subject] = [];
      }
      groups[subject].push(session);
    });
    return groups;
  }, [filteredSessions]);

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar - Chat Sessions */}
      <div className="w-80 bg-white border-r border-gray-100 flex flex-col">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-teal-500 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Dhruv AI</h2>
            </div>
            <Button 
              size="sm" 
              onClick={startNewSession}
              className="bg-teal-50 hover:bg-teal-100 text-teal-700 border-teal-200"
              variant="outline"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
          
          <div className="space-y-3">
            <div className="relative">
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger className="bg-gray-50 border-gray-200 text-gray-900">
                  <BookOpen className="h-4 w-4 mr-2 text-teal-600" />
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

            {/* Clean Session Search */}
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

        {/* Chat History - Grouped by Subject */}
        <div className="flex-1 overflow-y-auto p-4">
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
                  className="text-gray-400 hover:text-teal-600 h-6 w-6 p-0"
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
                    <BookOpen className="h-3 w-3 text-teal-600" />
                    <h4 className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                      {subject}
                    </h4>
                    <div className="flex-1 h-px bg-gray-100"></div>
                    <span className="text-xs text-gray-400">{subjectSessions.length}</span>
                  </div>
                  
                  {subjectSessions.map((session) => (
                    <div
                      key={session.session_id}
                      onClick={() => loadSession(session.session_id)}
                      className={`flex items-center justify-between px-3 py-2 ml-4 rounded-lg cursor-pointer transition-colors text-sm ${
                        currentSession === session.session_id
                          ? 'bg-teal-50 text-teal-900 border border-teal-200'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <div className="flex items-center flex-1 min-w-0">
                        <MessageCircle className="h-3 w-3 mr-2 flex-shrink-0 text-gray-400" />
                        <span className="truncate font-medium">{session.title}</span>
                      </div>
                      <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
                        {formatTime(session.last_updated)}
                      </span>
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

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Clean Header */}
        <div className="bg-white border-b border-gray-100 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 mr-6">
                AI Tutor – Mentor | Professor | Both
              </h1>
              
              {/* Trust Badges */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center text-teal-600">
                  <div className="w-5 h-5 bg-teal-100 rounded-full flex items-center justify-center mr-2">
                    <Shield className="h-3 w-3" />
                  </div>
                  <span>Verified</span>
                </div>
                <div className="flex items-center text-teal-600">
                  <div className="w-5 h-5 bg-teal-100 rounded-full flex items-center justify-center mr-2">
                    <Target className="h-3 w-3" />
                  </div>
                  <span>Personalized</span>
                </div>
                <div className="flex items-center text-teal-600">
                  <div className="w-5 h-5 bg-teal-100 rounded-full flex items-center justify-center mr-2">
                    <Lightbulb className="h-3 w-3" />
                  </div>
                  <span>Empowering</span>
                </div>
              </div>
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

        {/* Phase B: Personalization Status Bar */}
        {studentProfile && (
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 p-4 mx-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-purple-100 rounded-full p-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium text-purple-800 mb-1">🎯 Personalized Learning Active</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Language:</span>
                      <span className="font-medium text-purple-700 capitalize">{studentProfile.preferred_language}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Style:</span>
                      <span className="font-medium text-purple-700 capitalize">{studentProfile.learning_style}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Difficulty:</span>
                      <span className={`font-medium flex items-center space-x-1`}>
                        <span>{getDifficultyDisplay(personalizedDifficulty).emoji}</span>
                        <span className="text-purple-700">{getDifficultyDisplay(personalizedDifficulty).label}</span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Sessions:</span>
                      <span className="font-medium text-purple-700">{studentProfile.total_interactions || 0}</span>
                    </div>
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
    </div>
  );
}