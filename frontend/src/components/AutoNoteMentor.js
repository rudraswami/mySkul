import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { 
  Mic, 
  MicOff,
  Play,
  Square,
  FileText,
  Brain,
  GraduationCap,
  Heart,
  Clock,
  Users,
  Sparkles,
  MessageCircle,
  CreditCard,
  Download,
  BookOpen,
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AutoNoteMentor() {
  const { user } = useAuth();
  
  // Enhanced Session Management
  const [currentSession, setCurrentSession] = useState(null);
  const [sessionStatus, setSessionStatus] = useState('idle'); // idle, recording, processing, completed, uploading
  const [sessions, setSessions] = useState([]);
  
  // Enhanced Recording & Upload State
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(0);
  
  // Enhanced Notes & Features
  const [processedNote, setProcessedNote] = useState(null);
  const [topicCards, setTopicCards] = useState([]);
  const [flashcards, setFlashcards] = useState([]);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [mentorSummary, setMentorSummary] = useState('');
  
  // UI State
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('home'); // home, notes, flashcards, quiz
  
  // Interactive Features
  const [selectedNotes, setSelectedNotes] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [showFlashcards, setShowFlashcards] = useState(false);
  const [explainRequest, setExplainRequest] = useState('');
  const [explanation, setExplanation] = useState(null);
  
  // Form State
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [newSessionSubject, setNewSessionSubject] = useState('Mathematics');
  
  // Error & Loading
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Refs
  const mediaRecorderRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const chunkCounterRef = useRef(0);

  const subjects = {
    'JEE': ['Mathematics', 'Physics', 'Chemistry'],
    'NEET': ['Physics', 'Chemistry', 'Biology'], 
    'UPSC': ['General Studies', 'Current Affairs', 'History', 'Geography', 'Polity']
  };

  useEffect(() => {
    loadUserSessions();
  }, []);

  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(recordingTimerRef.current);
    }
    
    return () => clearInterval(recordingTimerRef.current);
  }, [isRecording]);

  const loadUserSessions = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      const response = await fetch(`${API}/auto-notes/sessions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
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

  const startNewSession = async () => {
    if (!newSessionTitle.trim()) {
      setError('Please enter a title for your class session');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        setError('Please log in again to continue');
        return;
      }
      
      const response = await fetch(`${API}/auto-notes/start-session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: newSessionTitle,
          subject: newSessionSubject
        })
      });
      
      if (response.ok) {
        const sessionData = await response.json();
        setCurrentSession(sessionData);
        setSessionStatus('ready');
        setNewSessionTitle('');
        setLiveTranscript('');
        setConceptsDetected([]);
        
        // Request microphone permission
        try {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (permissionError) {
          setError('Microphone access required for Auto-Note Mentor. Please allow microphone permission and try again.');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to start session');
      }
    } catch (error) {
      console.error('Session start error:', error);
      setError('Failed to start session. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    if (!currentSession) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });
      
      // Initialize MediaRecorder for audio capture
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunkCounterRef.current = 0;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          processAudioChunk(event.data);
        }
      };
      
      mediaRecorder.start(3000); // Capture data every 3 seconds
      setIsRecording(true);
      setRecordingTime(0);
      setSessionStatus('recording');
      
      // Initialize Web Speech API for real-time transcription
      if ('webkitSpeechRecognition' in window) {
        const recognition = new window.webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
          let finalTranscript = '';
          let interimTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
          
          if (finalTranscript) {
            setLiveTranscript(prev => prev + ' ' + finalTranscript);
            // Send to backend for processing
            sendTranscriptChunk(finalTranscript);
          }
        };
        
        recognition.start();
        mediaRecorderRef.current.speechRecognition = recognition;
      }
      
    } catch (error) {
      console.error('Recording start error:', error);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      
      // Stop speech recognition
      if (mediaRecorderRef.current.speechRecognition) {
        mediaRecorderRef.current.speechRecognition.stop();
      }
      
      // Stop media stream
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
      
      setIsRecording(false);
      setSessionStatus('processing');
      
      // Process the complete session
      processCompleteSession();
    }
  };

  const sendTranscriptChunk = async (transcriptText) => {
    if (!currentSession || !transcriptText.trim()) return;
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      chunkCounterRef.current++;
      
      const response = await fetch(`${API}/auto-notes/process-audio`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          transcription: transcriptText,
          timestamp: recordingTime,
          sequence_number: chunkCounterRef.current,
          confidence: 0.8
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.concepts_detected && result.concepts_detected.length > 0) {
          setConceptsDetected(prev => [...new Set([...prev, ...result.concepts_detected])]);
        }
      }
    } catch (error) {
      console.error('Transcript processing error:', error);
    }
  };

  const processAudioChunk = (audioBlob) => {
    // Store audio chunks for potential future use
    setAudioChunks(prev => [...prev, audioBlob]);
  };

  const processCompleteSession = async () => {
    if (!currentSession) return;
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/end-session?session_id=${currentSession.session_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setGeneratedNotes(result.structured_notes);
        setDualAnalysis(result.dual_analysis);
        setSessionStatus('completed');
        
        // Refresh sessions list
        loadUserSessions();
      } else {
        setError('Failed to process session. Please try again.');
      }
    } catch (error) {
      console.error('Session processing error:', error);
      setError('Failed to process session. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const generateFlashcards = async () => {
    if (!currentSession) return;
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/generate-flashcards`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          specific_concepts: conceptsDetected
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setFlashcards(result.flashcards);
        setShowFlashcards(true);
      }
    } catch (error) {
      console.error('Flashcard generation error:', error);
      setError('Failed to generate flashcards.');
    } finally {
      setLoading(false);
    }
  };

  const explainPoint = async () => {
    if (!currentSession || !explainRequest.trim()) return;
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/explain-point`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          point_reference: explainRequest,
          additional_context: null
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setExplanation(result);
      }
    } catch (error) {
      console.error('Explanation error:', error);
      setError('Failed to generate explanation.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreviousSession = async (sessionId) => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const sessionData = await response.json();
        setSelectedNotes(sessionData);
        setGeneratedNotes(sessionData.structured_notes);
        setDualAnalysis(sessionData.dual_analysis);
      }
    } catch (error) {
      console.error('Session load error:', error);
      setError('Failed to load session.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Main Recording Interface
  if (sessionStatus === 'recording' || sessionStatus === 'ready') {
    return (
      <div className="p-8 bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          {/* Session Header */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{currentSession?.title}</h1>
                <p className="text-gray-600">{currentSession?.subject} • {formatTime(recordingTime)}</p>
              </div>
              
              <div className="flex items-center space-x-4">
                <Badge variant={isRecording ? 'destructive' : 'secondary'} className="animate-pulse">
                  {isRecording ? (
                    <>
                      <Mic className="h-4 w-4 mr-1" />
                      Recording
                    </>
                  ) : (
                    <>
                      <MicOff className="h-4 w-4 mr-1" />
                      Ready
                    </>
                  )}
                </Badge>
                
                {conceptsDetected.length > 0 && (
                  <Badge variant="outline">
                    <Brain className="h-4 w-4 mr-1" />
                    {conceptsDetected.length} concepts detected
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Recording Controls */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="text-center">
              <div className="flex justify-center space-x-4 mb-6">
                {!isRecording ? (
                  <Button 
                    onClick={startRecording}
                    className="bg-red-600 hover:bg-red-700 text-white px-8 py-4 text-lg"
                    size="lg"
                  >
                    <Play className="h-6 w-6 mr-2" />
                    Start Recording Class
                  </Button>
                ) : (
                  <Button 
                    onClick={stopRecording}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-4 text-lg"
                    size="lg"
                  >
                    <Square className="h-6 w-6 mr-2" />
                    Stop & Process Notes
                  </Button>
                )}
              </div>
              
              <p className="text-sm text-gray-600">
                {isRecording 
                  ? "🎤 Listening and creating notes in real-time..."
                  : "Click 'Start Recording' to begin capturing your class or study session"
                }
              </p>
            </div>
          </div>

          {/* Live Transcript Display */}
          {isRecording && (
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-center mb-4">
                <MessageCircle className="h-5 w-5 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold">Live Transcript</h3>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                <p className="text-gray-800 whitespace-pre-wrap">
                  {liveTranscript || "Start speaking to see real-time transcription..."}
                </p>
              </div>
              
              {conceptsDetected.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Concepts Detected:</p>
                  <div className="flex flex-wrap gap-2">
                    {conceptsDetected.map((concept, index) => (
                      <Badge key={index} variant="outline">
                        {concept}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Processing State
  if (sessionStatus === 'processing') {
    return (
      <div className="p-8 bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
        <div className="max-w-2xl mx-auto text-center">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <Loader className="h-16 w-16 animate-spin text-blue-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Processing Your Notes</h2>
            <p className="text-gray-600 mb-4">
              Our dual-layer AI (Professor + Mentor) is analyzing your class recording...
            </p>
            
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-center space-x-6 text-sm">
                <div className="flex items-center">
                  <GraduationCap className="h-4 w-4 text-purple-600 mr-1" />
                  <span>Professor: Analyzing concepts</span>
                </div>
                <div className="flex items-center">
                  <Heart className="h-4 w-4 text-green-600 mr-1" />
                  <span>Mentor: Personalizing insights</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Generated Notes Display
  if (sessionStatus === 'completed' && generatedNotes && dualAnalysis) {
    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="max-w-6xl mx-auto">
          {/* Notes Header */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  📚 {currentSession?.title} - Auto-Generated Notes
                </h1>
                <p className="text-gray-600">
                  {currentSession?.subject} • {generatedNotes.duration_minutes?.toFixed(1)} minutes recorded
                </p>
              </div>
              
              <div className="flex space-x-3">
                <Button onClick={generateFlashcards} variant="outline">
                  <CreditCard className="h-4 w-4 mr-2" />
                  Generate Flashcards
                </Button>
                <Button onClick={() => setSessionStatus('idle')} variant="outline">
                  <FileText className="h-4 w-4 mr-2" />
                  New Session
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Notes Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Dual AI Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2 text-blue-600" />
                    Dual Intelligence Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Professor Analysis */}
                    <div className="border-l-4 border-purple-500 pl-4">
                      <div className="flex items-center mb-2">
                        <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                        <span className="font-semibold">Professor Analysis</span>
                        <Badge variant="outline" className="ml-2 text-xs">Technical</Badge>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <p className="text-gray-800 text-sm whitespace-pre-wrap">
                          {dualAnalysis.professor_analysis.content}
                        </p>
                      </div>
                    </div>

                    {/* Mentor Guidance */}
                    <div className="border-l-4 border-green-500 pl-4">
                      <div className="flex items-center mb-2">
                        <Heart className="h-5 w-5 text-green-600 mr-2" />
                        <span className="font-semibold">Mentor Guidance</span>
                        <Badge variant="outline" className="ml-2 text-xs">Personalized</Badge>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4">
                        <p className="text-gray-800 text-sm whitespace-pre-wrap">
                          {dualAnalysis.mentor_guidance.content}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Structured Notes */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BookOpen className="h-5 w-5 mr-2 text-green-600" />
                    Structured Notes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Key Concepts */}
                    {generatedNotes.key_concepts?.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">🎯 Key Concepts</h4>
                        <div className="grid grid-cols-2 gap-2">
                          {generatedNotes.key_concepts.map((concept, index) => (
                            <Badge key={index} variant="outline" className="justify-start">
                              {concept}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Important Points */}
                    {generatedNotes.important_points?.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">💡 Important Points</h4>
                        <ul className="space-y-2">
                          {generatedNotes.important_points.map((point, index) => (
                            <li key={index} className="flex items-start">
                              <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Formulas */}
                    {generatedNotes.formulas_mentioned?.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">📐 Formulas & Equations</h4>
                        <div className="space-y-2">
                          {generatedNotes.formulas_mentioned.map((formula, index) => (
                            <div key={index} className="bg-gray-50 rounded p-3 font-mono text-sm">
                              {formula}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Questions Raised */}
                    {generatedNotes.questions_raised?.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">🤔 Questions & Doubts</h4>
                        <ul className="space-y-2">
                          {generatedNotes.questions_raised.map((question, index) => (
                            <li key={index} className="flex items-start">
                              <AlertCircle className="h-4 w-4 text-orange-600 mr-2 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{question}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Interactive Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Interactive Features</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button onClick={generateFlashcards} className="w-full" variant="outline">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Generate Flashcards
                  </Button>
                  
                  <div className="space-y-2">
                    <Input
                      placeholder="Ask about any point... (e.g., 'Explain point #3')"
                      value={explainRequest}
                      onChange={(e) => setExplainRequest(e.target.value)}
                    />
                    <Button onClick={explainPoint} className="w-full" size="sm">
                      <MessageCircle className="h-4 w-4 mr-2" />
                      Get Explanation
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Session Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Session Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span>Duration:</span>
                      <span className="font-medium">{generatedNotes.duration_minutes?.toFixed(1)} min</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Concepts:</span>
                      <span className="font-medium">{generatedNotes.key_concepts?.length || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Formulas:</span>
                      <span className="font-medium">{generatedNotes.formulas_mentioned?.length || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Questions:</span>
                      <span className="font-medium">{generatedNotes.questions_raised?.length || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Confidence */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">AI Analysis Quality</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {Math.round((dualAnalysis.scenario_classification?.confidence || 0.8) * 100)}%
                    </div>
                    <p className="text-sm text-gray-600">Analysis Confidence</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Explanation Display */}
          {explanation && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>🤖 AI Explanation: {explanation.point_reference}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="border-l-4 border-purple-500 pl-4">
                    <div className="flex items-center mb-2">
                      <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                      <span className="font-semibold">Professor's Explanation</span>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm">{explanation.explanation.professor_explanation.content}</p>
                    </div>
                  </div>
                  
                  <div className="border-l-4 border-green-500 pl-4">
                    <div className="flex items-center mb-2">
                      <Heart className="h-5 w-5 text-green-600 mr-2" />
                      <span className="font-semibold">Mentor's Guidance</span>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm">{explanation.explanation.mentor_guidance.content}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Flashcards Display */}
          {showFlashcards && flashcards.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2" />
                    Generated Flashcards ({flashcards.length})
                  </span>
                  <Button variant="outline" size="sm" onClick={() => setShowFlashcards(false)}>
                    Close
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {flashcards.map((card, index) => (
                    <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="mb-2">
                        <Badge variant="outline" className="text-xs">{card.concept}</Badge>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-semibold text-gray-700">Question:</p>
                          <p className="text-sm">{card.question}</p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-700">Answer:</p>
                          <p className="text-sm">{card.answer}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    );
  }

  // Main Dashboard (Default View)
  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎤 Auto-Note Mentor
          </h1>
          <p className="text-gray-600">
            Revolutionary AI that listens to your classes and creates structured notes with dual intelligence
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5" />
              <div>
                <p className="text-red-800 text-sm">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-red-600 hover:text-red-800 text-xs underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* New Session Creation */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Sparkles className="h-5 w-5 mr-2 text-blue-600" />
                  Start New Auto-Note Session
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Class/Session Title
                      </label>
                      <Input
                        placeholder="e.g., Physics - Newton's Laws"
                        value={newSessionTitle}
                        onChange={(e) => setNewSessionTitle(e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Subject
                      </label>
                      <select
                        value={newSessionSubject}
                        onChange={(e) => setNewSessionSubject(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        {subjects[user?.exam_type]?.map(subject => (
                          <option key={subject} value={subject}>
                            {subject}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-start">
                      <Brain className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-semibold text-blue-900 mb-1">How Auto-Note Mentor Works:</p>
                        <ul className="text-blue-800 space-y-1">
                          <li>• Captures real-time audio from your class or study session</li>
                          <li>• Professor AI analyzes concepts, formulas, and academic accuracy</li>
                          <li>• Mentor AI personalizes insights and creates encouraging summaries</li>
                          <li>• Generates interactive notes with "explain point" and flashcard features</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={startNewSession}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    disabled={loading || !newSessionTitle.trim()}
                  >
                    {loading ? (
                      <>
                        <Loader className="h-4 w-4 mr-2 animate-spin" />
                        Starting Session...
                      </>
                    ) : (
                      <>
                        <Mic className="h-4 w-4 mr-2" />
                        Start Auto-Note Session
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Previous Sessions */}
          <div>
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-green-600" />
                  Previous Sessions
                </CardTitle>
              </CardHeader>
              <CardContent>
                {sessions.length > 0 ? (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {sessions.map((session) => (
                      <div
                        key={session.session_id}
                        onClick={() => loadPreviousSession(session.session_id)}
                        className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm text-gray-900 truncate">
                            {session.title}
                          </h4>
                          <Badge variant="outline" className="text-xs">
                            {session.subject}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{new Date(session.created_at).toLocaleDateString()}</span>
                          <Badge 
                            variant={session.status === 'completed' ? 'default' : 'secondary'}
                            className="text-xs"
                          >
                            {session.status}
                          </Badge>
                        </div>
                        
                        {session.audio_duration && (
                          <div className="mt-1 text-xs text-gray-600">
                            Duration: {Math.round(session.audio_duration / 60)} minutes
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No previous sessions</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}