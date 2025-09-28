import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import FormattedAIResponse, { DualResponseContainer } from './FormattedAIResponse';
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
  Sparkles
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

  const subjects = {
    'JEE': ['Mathematics', 'Physics', 'Chemistry'],
    'NEET': ['Physics', 'Chemistry', 'Biology'],
    'UPSC': ['General Studies', 'Current Affairs', 'History', 'Geography', 'Polity']
  };

  useEffect(() => {
    fetchChatSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Sidebar - Chat Sessions */}
      <div className="w-80 bg-white/90 backdrop-blur-sm border-r border-gray-200/60 flex flex-col shadow-lg">
        <div className="p-4 border-b border-gray-200/60 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
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

        {/* Enhanced Sessions List */}
        <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-transparent to-gray-50/30">
          <div className="space-y-3">
            {sessions.length > 0 ? (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => loadSession(session.session_id)}
                  className={`group p-4 rounded-xl cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
                    currentSession === session.session_id
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                      : 'bg-white hover:bg-gray-50 hover:shadow-md border border-gray-200/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2 rounded-lg ${
                      currentSession === session.session_id 
                        ? 'bg-white/20' 
                        : 'bg-gray-100 group-hover:bg-blue-100'
                    }`}>
                      <MessageCircle className={`h-4 w-4 ${
                        currentSession === session.session_id 
                          ? 'text-white' 
                          : 'text-gray-600 group-hover:text-blue-600'
                      }`} />
                    </div>
                    <Badge 
                      variant={currentSession === session.session_id ? "secondary" : "outline"} 
                      className={`text-xs ${
                        currentSession === session.session_id 
                          ? 'bg-white/20 text-white border-white/30' 
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {session.subject}
                    </Badge>
                  </div>
                  <p className={`text-sm font-medium mb-2 truncate ${
                    currentSession === session.session_id 
                      ? 'text-white' 
                      : 'text-gray-900'
                  }`}>
                    {session.title}
                  </p>
                  <div className="flex items-center space-x-2">
                    <Clock className={`h-3 w-3 ${
                      currentSession === session.session_id 
                        ? 'text-white/70' 
                        : 'text-gray-400'
                    }`} />
                    <p className={`text-xs ${
                      currentSession === session.session_id 
                        ? 'text-white/90' 
                        : 'text-gray-500'
                    }`}>
                      {formatTime(session.last_updated)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageCircle className="h-8 w-8 text-blue-500" />
                </div>
                <p className="text-sm text-gray-600 mb-2">No previous sessions</p>
                <p className="text-xs text-gray-400">Start a conversation to see your history</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Enhanced Chat Header */}
        <div className="bg-white/95 backdrop-blur-sm border-b border-gray-200/60 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  Dhruv AI - {selectedSubject} Tutor
                </h1>
                <div className="flex items-center mt-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
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
                <Badge className="flex items-center bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border-blue-200 shadow-sm">
                  <Users className="h-3 w-3 mr-1" />
                  Dual Intelligence
                </Badge>
              )}
              {aiMode === 'mentor' && (
                <Badge className="flex items-center bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border-green-200 shadow-sm">
                  <Heart className="h-3 w-3 mr-1" />
                  Mentor Mode
                </Badge>
              )}
              {aiMode === 'professor' && (
                <Badge className="flex items-center bg-gradient-to-r from-purple-100 to-violet-100 text-purple-800 border-purple-200 shadow-sm">
                  <GraduationCap className="h-3 w-3 mr-1" />
                  Professor Mode
                </Badge>
              )}
              <Badge className="flex items-center bg-gradient-to-r from-gray-100 to-slate-100 text-gray-700 border-gray-200 shadow-sm">
                <Shield className="h-3 w-3 mr-1" />
                Hallucination-Free AI
              </Badge>
            </div>
          </div>
        </div>

        {/* Enhanced Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20">
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
                
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Welcome to Your Trusted, Hallucination-Free AI Tutor!
                </h3>
                
                <p className="text-gray-600 mb-4 max-w-lg mx-auto">
                  Experience personalized, verified AI tutoring for {selectedSubject} at a fraction of coaching costs. Our dual intelligence ensures:
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

                {/* Sample Questions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
                  <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setCurrentMessage("Explain the concept of limits in calculus")}>
                    <CardContent className="p-4 text-left">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <GraduationCap className="h-4 w-4 text-purple-600 mr-2" />
                          <span className="text-sm font-medium text-purple-600">Professor Leads</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Fact/Concept</Badge>
                      </div>
                      <p className="text-sm text-gray-700">Explain the concept of limits in calculus</p>
                    </CardContent>
                  </Card>

                  <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setCurrentMessage("I'm feeling stressed about my upcoming JEE exam. Can you help me plan my studies?")}>
                    <CardContent className="p-4 text-left">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Heart className="h-4 w-4 text-green-600 mr-2" />
                          <span className="text-sm font-medium text-green-600">Mentor Leads</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Guidance</Badge>
                      </div>
                      <p className="text-sm text-gray-700">I'm feeling stressed about my upcoming JEE exam. Can you help me plan my studies?</p>
                    </CardContent>
                  </Card>

                  <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setCurrentMessage("Solve this quadratic equation step by step: x² - 5x + 6 = 0")}>
                    <CardContent className="p-4 text-left">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <GraduationCap className="h-4 w-4 text-purple-600 mr-2" />
                          <span className="text-sm font-medium text-purple-600">Professor Leads</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Problem Solving</Badge>
                      </div>
                      <p className="text-sm text-gray-700">Solve this quadratic equation step by step: x² - 5x + 6 = 0</p>
                    </CardContent>
                  </Card>

                  <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setCurrentMessage("What are some effective study techniques for competitive exams?")}>
                    <CardContent className="p-4 text-left">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Users className="h-4 w-4 text-blue-600 mr-2" />
                          <span className="text-sm font-medium text-blue-600">Both Contribute</span>
                        </div>
                        <Badge variant="outline" className="text-xs">General Inquiry</Badge>
                      </div>
                      <p className="text-sm text-gray-700">What are some effective study techniques for competitive exams?</p>
                    </CardContent>
                  </Card>
                </div>

                <div className="mt-8 p-4 bg-blue-50 rounded-lg max-w-2xl mx-auto">
                  <div className="flex items-center justify-center mb-2">
                    <Sparkles className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-blue-600">Intelligent Routing</span>
                  </div>
                  <p className="text-xs text-gray-600">
                    Our AI automatically determines whether you need technical expertise (Professor) or motivational guidance (Mentor) based on your question.
                  </p>
                </div>
              </div>
            ) : (
              // Chat Messages
              messages.map((message, index) => (
                <div key={index} className="space-y-4">
                  {/* User Message */}
                  <div className="flex justify-end">
                    <div className="max-w-2xl bg-blue-600 text-white rounded-lg p-4">
                      <p className="text-sm">{message.message}</p>
                      <p className="text-xs text-blue-100 mt-2">
                        {formatTime(message.timestamp)}
                      </p>
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
                              <div className="whitespace-pre-wrap text-gray-800">
                                {message.response}
                              </div>
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

                            {/* Feedback buttons */}
                            <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
                              <div className="flex items-center space-x-2">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="text-gray-500 hover:text-green-600"
                                >
                                  <ThumbsUp className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="text-gray-500 hover:text-red-600"
                                >
                                  <ThumbsDown className="h-4 w-4" />
                                </Button>
                              </div>
                              
                              <div className="flex items-center text-xs text-gray-500">
                                <Clock className="h-3 w-3 mr-1" />
                                {formatTime(message.timestamp)}
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

        {/* Enhanced Input Area */}
        <div className="bg-white/95 backdrop-blur-sm border-t border-gray-200/60 p-6 shadow-lg">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1 relative">
                <Textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={`Ask me anything about ${selectedSubject}... ✨`}
                  className="resize-none border-2 border-gray-200 focus:border-blue-500 rounded-xl bg-white/80 backdrop-blur-sm transition-all duration-200 shadow-sm hover:shadow-md focus:shadow-lg"
                  rows={3}
                  disabled={loading}
                />
                {currentMessage.trim() && (
                  <div className="absolute bottom-3 right-3 text-xs text-gray-400">
                    {currentMessage.length} characters
                  </div>
                )}
              </div>
              
              <Button 
                onClick={sendMessage}
                disabled={loading || !currentMessage.trim()}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-6 py-3 h-auto rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:transform-none"
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
            
            <div className="flex items-center justify-between mt-4 px-2">
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  <span>Press Enter to send, Shift+Enter for new line</span>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                {aiMode === 'dual' && (
                  <div className="flex items-center text-xs text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                    <Users className="h-3 w-3 mr-1" />
                    <span className="font-medium">Dual Intelligence Active</span>
                  </div>
                )}
                {aiMode === 'mentor' && (
                  <div className="flex items-center text-xs text-green-600 bg-green-50 px-3 py-1 rounded-full">
                    <Heart className="h-3 w-3 mr-1" />
                    <span className="font-medium">Mentor Mode</span>
                  </div>
                )}
                {aiMode === 'professor' && (
                  <div className="flex items-center text-xs text-purple-600 bg-purple-50 px-3 py-1 rounded-full">
                    <GraduationCap className="h-3 w-3 mr-1" />
                    <span className="font-medium">Professor Mode</span>
                  </div>
                )}
                <div className="flex items-center text-xs text-gray-500">
                  <Shield className="h-3 w-3 mr-1" />
                  <span>Hallucination-Free</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}