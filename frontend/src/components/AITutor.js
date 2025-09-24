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
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar - Chat Sessions */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Dhruv AI</h2>
            <Button 
              size="sm" 
              onClick={startNewSession}
              className="bg-blue-600 hover:bg-blue-700"
            >
              New Chat
            </Button>
          </div>
          
          <div className="space-y-3">
            <Select value={selectedSubject} onValueChange={setSelectedSubject}>
              <SelectTrigger>
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

            {/* AI Mode Selection */}
            <div className="bg-gray-50 rounded-lg p-3">
              <label className="text-xs font-medium text-gray-700 mb-2 block">AI Mode</label>
              <Select value={aiMode} onValueChange={setAiMode}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dual">
                    <div className="flex items-center">
                      <Users className="h-3 w-3 mr-2" />
                      Dual Layer (Mentor + Professor)
                    </div>
                  </SelectItem>
                  <SelectItem value="mentor">
                    <div className="flex items-center">
                      <Heart className="h-3 w-3 mr-2" />
                      Mentor Only (Motivational)
                    </div>
                  </SelectItem>
                  <SelectItem value="professor">
                    <div className="flex items-center">
                      <GraduationCap className="h-3 w-3 mr-2" />
                      Professor Only (Technical)
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
              
              {aiMode === 'dual' && (
                <div className="mt-2 text-xs text-gray-600">
                  Adaptive intelligence: The right persona leads based on your question type
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {sessions.length > 0 ? (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => loadSession(session.session_id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    currentSession === session.session_id
                      ? 'bg-blue-50 border-blue-200 border'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <MessageCircle className="h-4 w-4 text-gray-400" />
                    <Badge variant="outline" className="text-xs">
                      {session.subject}
                    </Badge>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mt-1 truncate">
                    {session.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatTime(session.last_updated)}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <MessageCircle className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No previous sessions</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Brain className="h-6 w-6 text-blue-600 mr-3" />
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Dhruv AI - {selectedSubject} Tutor
                </h1>
                <p className="text-sm text-gray-600">
                  {aiMode === 'dual' && 'Dual-layer AI: Mentor + Professor intelligence'}
                  {aiMode === 'mentor' && 'Mentor mode: Adaptive, friendly, motivational'}
                  {aiMode === 'professor' && 'Professor mode: Rule-based, verified reasoning'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {aiMode === 'dual' && (
                <Badge variant="outline" className="flex items-center">
                  <Users className="h-3 w-3 mr-1" />
                  Dual Intelligence
                </Badge>
              )}
              {aiMode === 'mentor' && (
                <Badge variant="outline" className="flex items-center bg-green-50 text-green-700 border-green-200">
                  <Heart className="h-3 w-3 mr-1" />
                  Mentor Mode
                </Badge>
              )}
              {aiMode === 'professor' && (
                <Badge variant="outline" className="flex items-center bg-purple-50 text-purple-700 border-purple-200">
                  <GraduationCap className="h-3 w-3 mr-1" />
                  Professor Mode
                </Badge>
              )}
              <Badge variant="secondary" className="flex items-center">
                <Shield className="h-3 w-3 mr-1" />
                Neuro-Symbolic AI
              </Badge>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          <div className="max-w-4xl mx-auto space-y-6">
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
                  Welcome to Dhruv AI - Dual Intelligence System!
                </h3>
                
                <p className="text-gray-600 mb-6 max-w-lg mx-auto">
                  Experience revolutionary dual-layer AI for {selectedSubject}. Our system combines:
                </p>

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
                    <div className="max-w-4xl w-full">
                      {message.dual_response ? (
                        /* Dual Response Layout */
                        <div className="space-y-4">
                          {/* Scenario indicator */}
                          <div className="flex items-center justify-center">
                            <Badge variant="outline" className="text-xs">
                              <Target className="h-3 w-3 mr-1" />
                              {message.dual_response.scenario_type.replace('_', ' ')} scenario detected
                            </Badge>
                          </div>
                          
                          {/* Primary Response */}
                          <div className="relative">
                            <div className="flex items-center mb-2">
                              {message.dual_response.primary.persona === 'professor' ? (
                                <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                              ) : (
                                <Heart className="h-5 w-5 text-green-600 mr-2" />
                              )}
                              <span className="text-sm font-medium text-gray-700">
                                {message.dual_response.primary.persona === 'professor' ? 'Professor' : 'Mentor'} (Leading)
                              </span>
                              <Badge 
                                variant="outline" 
                                className={`ml-2 text-xs ${
                                  message.dual_response.primary.persona === 'professor' 
                                    ? 'bg-purple-50 text-purple-700 border-purple-200' 
                                    : 'bg-green-50 text-green-700 border-green-200'
                                }`}
                              >
                                Primary
                              </Badge>
                            </div>
                            
                            <div className={`bg-white rounded-lg p-4 shadow-sm border-l-4 ${
                              message.dual_response.primary.persona === 'professor' 
                                ? 'border-purple-500' 
                                : 'border-green-500'
                            }`}>
                              <div className="prose prose-sm max-w-none">
                                <div className="whitespace-pre-wrap text-gray-800">
                                  {message.dual_response.primary.response}
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Secondary Response (if exists) */}
                          {message.dual_response.secondary.response && (
                            <div className="relative">
                              <div className="flex items-center mb-2">
                                {message.dual_response.secondary.persona === 'professor' ? (
                                  <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                                ) : (
                                  <Heart className="h-5 w-5 text-green-600 mr-2" />
                                )}
                                <span className="text-sm font-medium text-gray-700">
                                  {message.dual_response.secondary.persona === 'professor' ? 'Professor' : 'Mentor'} (Supporting)
                                </span>
                                <Badge variant="outline" className="ml-2 text-xs">
                                  <Sparkles className="h-3 w-3 mr-1" />
                                  Additional Insights
                                </Badge>
                              </div>
                              
                              <div className={`bg-gray-50 rounded-lg p-4 border-l-4 ${
                                message.dual_response.secondary.persona === 'professor' 
                                  ? 'border-purple-300' 
                                  : 'border-green-300'
                              }`}>
                                <div className="prose prose-sm max-w-none">
                                  <div className="whitespace-pre-wrap text-gray-700">
                                    {message.dual_response.secondary.response}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Confidence & Feedback */}
                          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                            <div className="flex items-center space-x-4">
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
                              
                              {message.dual_response.confidence && (
                                <Badge variant="outline" className="text-xs">
                                  {Math.round(message.dual_response.confidence * 100)}% confidence
                                </Badge>
                              )}
                            </div>
                            
                            <div className="flex items-center text-xs text-gray-500">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatTime(message.timestamp)}
                            </div>
                          </div>
                        </div>
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
            
            {/* Loading indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex items-center">
                    <Brain className="h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm text-gray-700">Dhruv AI is thinking...</span>
                    <div className="ml-2 flex space-x-1">
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <Textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={`Ask me anything about ${selectedSubject}...`}
                  className="resize-none"
                  rows={2}
                  disabled={loading}
                />
              </div>
              
              <Button 
                onClick={sendMessage}
                disabled={loading || !currentMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <span>Press Enter to send, Shift+Enter for new line</span>
              <div className="flex items-center">
                {aiMode === 'dual' && <span className="mr-2">🧠 Dual Intelligence Active</span>}
                {aiMode === 'mentor' && <span className="mr-2">💚 Mentor Mode</span>}
                {aiMode === 'professor' && <span className="mr-2">🎓 Professor Mode</span>}
                <span>Neuro-Symbolic AI</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}