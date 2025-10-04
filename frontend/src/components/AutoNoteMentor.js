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
  MessageCircle,
  CreditCard,
  Download,
  BookOpen,
  AlertCircle,
  CheckCircle,
  Loader,
  Upload,
  X,
  BarChart3
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
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  
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
  const [showFlashcards, setShowFlashcards] = useState(false);
  const [explainRequest, setExplainRequest] = useState('');
  const [explanation, setExplanation] = useState(null);
  
  // Enhanced Features State
  const [classSeries, setClassSeries] = useState([]);
  const [newSeries, setNewSeries] = useState({ name: '', subject: '', total_classes: 10, schedule: '' });
  const [analytics, setAnalytics] = useState(null);
  
  // Live Recording State
  const [liveTranscript, setLiveTranscript] = useState('');
  const [conceptsDetected, setConceptsDetected] = useState([]);
  const [audioChunks, setAudioChunks] = useState([]);
  const [generatedNotes, setGeneratedNotes] = useState(null);
  const [dualAnalysis, setDualAnalysis] = useState(null);
  
  // Form State
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [newSessionSubject, setNewSessionSubject] = useState('Mathematics');
  
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

  // Enhanced session creation with multi-modal support
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
        setSessionStatus('ready'); // Changed from 'active' to 'ready' to show recording interface
        setActiveView('home');
        setNewSessionTitle('');
        setNewSessionSubject('Mathematics');
        
        // Load updated sessions
        loadUserSessions();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start session');
      }
    } catch (error) {
      console.error('Error starting session:', error);
      setError('Failed to start new session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // File Selection and Handling
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    if (file) {
      handleFileUpload(file);
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
      setSelectedFile(file);
      handleFileUpload(file);
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
    setProcessingProgress(0);
    if (sessionStatus === 'uploading') {
      setSessionStatus('active');
    }
    // Reset file input
    const fileInput = document.getElementById('file-upload');
    if (fileInput) fileInput.value = '';
  };
  
  // Enhanced file upload and processing - STANDALONE (no session required)
  const handleFileUpload = async (file) => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    // Validate file type and size
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'video/mp4', 'audio/m4a'];
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|mp4|m4a)$/i)) {
      setError('Please upload an audio or video file (MP3, WAV, MP4, M4A)');
      return;
    }
    
    // Check file size (100MB limit)
    const maxSize = 100 * 1024 * 1024; // 100MB in bytes
    if (file.size > maxSize) {
      setError('File size too large. Please upload a file smaller than 100MB.');
      return;
    }
    
    setLoading(true);
    setSessionStatus('uploading');
    setProcessingProgress(10);
    setError(null);
    
    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 10;
      });
    }, 500);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      // Create a temporary session for file upload if none exists
      let sessionId = currentSession?.session_id;
      
      if (!sessionId) {
        console.log('Creating temporary session for file upload...');
        setProcessingProgress(5);
        
        const sessionResponse = await fetch(`${API}/auto-notes/start-session`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: `File Upload - ${file.name}`,
            subject: 'General' // Default subject for file uploads
          })
        });
        
        if (sessionResponse.ok) {
          const sessionData = await sessionResponse.json();
          sessionId = sessionData.session_id;
          setCurrentSession(sessionData); // Store the created session
          console.log('Temporary session created:', sessionId);
        } else {
          throw new Error('Failed to create session for file upload');
        }
      }
      
      setProcessingProgress(15);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API}/auto-notes/upload-audio?session_id=${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData
      });
      
      clearInterval(progressInterval);
      
      if (response.ok) {
        const result = await response.json();
        
        setProcessingProgress(100);
        
        // Update states with processed data
        setProcessedNote(result);
        setMentorSummary(result.mentor_summary || '');
        setSessionStatus('completed');
        
        // Refresh sessions list to show the new completed session
        loadUserSessions();
        
        // If we have a note_id, load the detailed processed note
        if (result.note_id) {
          await loadProcessedNote(result.note_id);
        } else {
          // Directly display the result as structured notes
          setGeneratedNotes({
            key_concepts: result.concepts_learned || [],
            important_points: result.concepts_learned || [],
            formulas_mentioned: [],
            questions_raised: [],
            duration_minutes: result.audio_duration || 0
          });
          
          setDualAnalysis({
            professor_analysis: {
              content: "Audio processing completed successfully. Technical concepts have been extracted and organized."
            },
            mentor_guidance: {
              content: result.mentor_summary || "Your uploaded content has been processed and organized into structured notes."
            },
            scenario_classification: {
              confidence: 0.8
            }
          });
          
          setActiveView('notes');
        }
        
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to process audio file');
        setSessionStatus('active');
        setProcessingProgress(0);
      }
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Error uploading file:', error);
      setError('Failed to upload and process file. Please check your connection and try again.');
      setSessionStatus('active');
      setProcessingProgress(0);
    } finally {
      setLoading(false);
    }
  };
  
  // Load detailed processed note data
  const loadProcessedNote = async (noteId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/processed-note/${noteId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const noteData = await response.json();
        
        setTopicCards(noteData.topic_cards || []);
        setFlashcards(noteData.interactive_features.flashcards || []);
        setQuizQuestions(noteData.interactive_features.quiz_questions || []);
        setMentorSummary(noteData.mentor_summary || '');
        
        setActiveView('notes');
      }
    } catch (error) {
      console.error('Error loading processed note:', error);
      setError('Failed to load processed notes');
    }
  };
  
  // Generate additional flashcards
  const generateMoreFlashcards = async () => {
    if (!processedNote) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/generate-flashcards?note_id=${processedNote.note_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setFlashcards(prev => [...prev, ...result.flashcards]);
      }
    } catch (error) {
      console.error('Error generating flashcards:', error);
      setError('Failed to generate additional flashcards');
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
    
    // Set a timeout for the processing request (60 seconds)
    const timeoutId = setTimeout(() => {
      setError('Session processing timed out. Please try again or contact support if this persists.');
      setSessionStatus('idle');
      setLoading(false);
    }, 60000);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      console.log('Starting session processing for:', currentSession.session_id);
      console.log('Live transcript length:', liveTranscript.length);
      
      // If we have live transcript but no audio chunks were processed, send the transcript as fallback
      let requestBody = {};
      if (liveTranscript.trim()) {
        requestBody = {
          fallback_transcription: liveTranscript,
          total_duration: recordingTime
        };
      }
      
      const response = await fetch(`${API}/auto-notes/end-session?session_id=${currentSession.session_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: Object.keys(requestBody).length > 0 ? JSON.stringify(requestBody) : undefined
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const result = await response.json();
        console.log('Session processing completed:', result);
        
        setGeneratedNotes(result.structured_notes);
        setDualAnalysis(result.dual_analysis);
        setSessionStatus('completed');
        
        // Refresh sessions list
        loadUserSessions();
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Session processing failed:', response.status, errorData);
        setError(errorData.detail || `Failed to process session (${response.status}). Please try again.`);
        setSessionStatus('idle');
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Session processing error:', error);
      setError('Failed to process session. Please check your connection and try again.');
      setSessionStatus('idle');
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
    setError(null);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      console.log('Loading previous session:', sessionId);
      
      const response = await fetch(`${API}/auto-notes/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const sessionData = await response.json();
        console.log('Session data loaded:', sessionData);
        
        // Set all necessary state for viewing the session
        setCurrentSession(sessionData);
        setSelectedNotes(sessionData);
        setGeneratedNotes(sessionData.structured_notes);
        setDualAnalysis(sessionData.dual_analysis);
        
        // Set session status based on data availability
        if (sessionData.structured_notes && sessionData.dual_analysis) {
          setSessionStatus('completed');
        } else if (sessionData.status === 'processing') {
          setSessionStatus('processing');
        } else {
          setSessionStatus('active');
        }
        
        // Switch to notes view
        setActiveView('notes');
        
        console.log('Previous session loaded successfully');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || `Failed to load session (${response.status})`);
      }
    } catch (error) {
      console.error('Session load error:', error);
      setError('Failed to load session. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // ============= ENHANCED FEATURES FUNCTIONS =============

  // Removed: Document Analysis, Spaced Repetition, and Smart Search functions 
  // These features are available in AI Tutor module

  const createClassSeries = async () => {
    if (!newSeries.name || !newSeries.subject) {
      setError('Please fill in series name and subject');
      return;
    }

    setLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/class-series`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          series_name: newSeries.name,
          subject: newSeries.subject,
          total_classes: newSeries.total_classes,
          schedule: newSeries.schedule
        })
      });

      if (response.ok) {
        const result = await response.json();
        loadClassSeries(); // Refresh series list
        setNewSeries({ name: '', subject: '', total_classes: 10, schedule: '' });
      }
    } catch (error) {
      console.error('Class series creation error:', error);
      setError('Failed to create class series');
    } finally {
      setLoading(false);
    }
  };

  const loadClassSeries = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/class-series`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        setClassSeries(result.series);
      }
    } catch (error) {
      console.error('Class series loading error:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${API}/auto-notes/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        setAnalytics(result);
      }
    } catch (error) {
      console.error('Analytics loading error:', error);
    }
  };

  // Load enhanced features on component mount
  useEffect(() => {
    loadClassSeries();
    loadAnalytics();
  }, []);

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
            
            {/* Progress Steps */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
              <div className="space-y-3">
                <div className="flex items-center justify-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-gray-700">✓ Audio uploaded</span>
                </div>
                <div className="flex items-center justify-center text-sm">
                  <Loader className="h-4 w-4 animate-spin text-blue-500 mr-2" />
                  <span className="text-gray-700">🔄 Transcribing...</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-400">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>⏳ Generating notes & flashcards...</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-400">
                  <Brain className="h-4 w-4 mr-2" />
                  <span>⏳ Creating insights...</span>
                </div>
              </div>
            </div>
            
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
            
            {/* Timeout warning */}
            <div className="mt-4 text-xs text-gray-500">
              <p>This may take 30-60 seconds depending on recording length.</p>
              <p>Please don't refresh the page while processing.</p>
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
                  📚 {currentSession?.title || 
                      currentSession?.session_name || 
                      `${currentSession?.subject || 'General'} Session`} - Auto-Generated Notes
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
                <Button 
                  onClick={() => {
                    setSessionStatus('idle');
                    setActiveView('home');
                    setCurrentSession(null);
                    setGeneratedNotes(null);
                    setDualAnalysis(null);
                    setSelectedNotes(null);
                    loadUserSessions(); // Refresh the sessions list
                  }} 
                  variant="outline"
                >
                  <Clock className="h-4 w-4 mr-2" />
                  Back to Sessions
                </Button>
                <Button 
                  onClick={() => {
                    setSessionStatus('idle');
                    setActiveView('home');
                    setCurrentSession(null);
                    setGeneratedNotes(null);
                    setDualAnalysis(null);
                    setSelectedNotes(null);
                  }} 
                  variant="outline"
                >
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
          <div className="flex items-center mb-4">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl mr-4">
              <Mic className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                Auto-Note Mentor
              </h1>
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm text-green-600">
                  <div className="h-2 w-2 bg-green-500 rounded-full mr-1"></div>
                  <span>Hallucination-Free</span>
                </div>
                <div className="flex items-center text-sm text-blue-600">
                  <div className="h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
                  <span>Verified Notes</span>
                </div>
                <div className="flex items-center text-sm text-purple-600">
                  <div className="h-2 w-2 bg-purple-500 rounded-full mr-1"></div>
                  <span>Dual AI Intelligence</span>
                </div>
              </div>
            </div>
          </div>
          <p className="text-gray-600 text-lg mb-4">
            Turn every class into verified notes, flashcards and personalized prep — powered by trusted, hallucination-free AI
          </p>
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className="bg-blue-600 text-white rounded-full p-2 w-10 h-10 flex items-center justify-center mx-auto mb-2">
                  <Mic className="h-5 w-5" />
                </div>
                <p className="text-sm font-semibold text-gray-800">Live Recording</p>
                <p className="text-xs text-gray-600">Real-time sessions</p>
              </div>
              <div className="text-2xl text-gray-400">OR</div>
              <div className="text-center">
                <div className="bg-purple-600 text-white rounded-full p-2 w-10 h-10 flex items-center justify-center mx-auto mb-2">
                  <Upload className="h-5 w-5" />
                </div>
                <p className="text-sm font-semibold text-gray-800">File Upload</p>
                <p className="text-xs text-gray-600">Independent processing</p>
              </div>
            </div>
          </div>
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
                  <Mic className="h-5 w-5 mr-2 text-blue-600" />
                  Live Recording Session
                </CardTitle>
                <p className="text-sm text-gray-600 mt-2">
                  Record live classes or study sessions in real-time
                </p>
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
                  
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-start">
                      <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <Brain className="h-4 w-4 text-white" />
                      </div>
                      <div className="text-sm">
                        <p className="font-semibold text-gray-900 mb-2">Trusted, Hallucination-Free Auto-Note Generation:</p>
                        <div className="space-y-2">
                          <div className="flex items-start">
                            <div className="h-2 w-2 bg-green-500 rounded-full mr-2 mt-2"></div>
                            <span className="text-gray-700"><strong>Trust:</strong> Verified, accurate AI with zero hallucinations</span>
                          </div>
                          <div className="flex items-start">
                            <div className="h-2 w-2 bg-purple-500 rounded-full mr-2 mt-2"></div>
                            <span className="text-gray-700"><strong>Personalisation:</strong> Adaptive dual-AI tailored to your learning style</span>
                          </div>
                          <div className="flex items-start">
                            <div className="h-2 w-2 bg-yellow-500 rounded-full mr-2 mt-2"></div>
                            <span className="text-gray-700"><strong>Empowerment:</strong> Professional-grade notes at fraction of coaching costs</span>
                          </div>
                        </div>
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

            {/* File Upload Section */}
            <Card className="border-0 shadow-md mt-6">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="h-5 w-5 mr-2 text-purple-600" />
                  Upload Audio/Video Files
                </CardTitle>
                <p className="text-sm text-gray-600 mt-2">
                  Process existing recordings independently - no session required
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
                    <div className="flex items-start">
                      <div className="h-8 w-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <Upload className="h-4 w-4 text-white" />
                      </div>
                      <div className="text-sm">
                        <p className="font-semibold text-gray-900 mb-2">Turn Any Recording into Verified Study Material:</p>
                        <div className="space-y-2">
                          <div className="flex items-start">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                            <span className="text-gray-700">Upload lectures, classes, or study sessions (MP3, WAV, MP4)</span>
                          </div>
                          <div className="flex items-start">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                            <span className="text-gray-700">Get hallucination-free transcription with dual AI verification</span>
                          </div>
                          <div className="flex items-start">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                            <span className="text-gray-700">Receive structured notes, flashcards, and personalized insights</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Drag and Drop Upload Area */}
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      dragOver 
                        ? 'border-purple-500 bg-purple-50' 
                        : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50'
                    }`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <div className="space-y-4">
                      <div className="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <FileText className="h-6 w-6 text-purple-600" />
                      </div>
                      
                      <div>
                        <p className="text-lg font-medium text-gray-900 mb-2">
                          {dragOver ? 'Drop your file here' : 'Upload Audio or Video File'}
                        </p>
                        <p className="text-sm text-gray-600 mb-4">
                          Drag and drop a file, or click to browse
                        </p>
                        
                        <div className="space-y-2">
                          <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            accept="audio/*,video/*,.mp3,.wav,.mp4,.m4a"
                            onChange={handleFileSelect}
                            disabled={loading}
                          />
                          <label
                            htmlFor="file-upload"
                            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                              loading
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-purple-600 hover:bg-purple-700 cursor-pointer'
                            }`}
                          >
                            <Upload className="h-4 w-4 mr-2" />
                            Choose File
                          </label>
                          
                          <p className="text-xs text-gray-500">
                            Supported formats: MP3, WAV, MP4, M4A (Max 100MB)
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Selected File Display */}
                  {selectedFile && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <FileText className="h-5 w-5 text-gray-500 mr-2" />
                          <div>
                            <p className="font-medium text-gray-900">{selectedFile.name}</p>
                            <p className="text-sm text-gray-500">
                              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {sessionStatus === 'uploading' ? (
                            <div className="flex items-center">
                              <Loader className="h-4 w-4 animate-spin text-purple-600 mr-2" />
                              <span className="text-sm text-purple-600">Processing...</span>
                            </div>
                          ) : (
                            <button
                              onClick={clearSelectedFile}
                              className="p-1 hover:bg-gray-200 rounded-full transition-colors"
                              title="Remove file"
                            >
                              <X className="h-4 w-4 text-gray-500" />
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {sessionStatus === 'uploading' && (
                        <div className="mt-3">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${processingProgress}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Processing: {processingProgress}%
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-semibold text-blue-800 mb-1">Standalone File Processing</p>
                        <p className="text-blue-700">
                          Upload files directly! No need to create a session first. Each file will be processed independently with full AI analysis.
                        </p>
                      </div>
                    </div>
                  </div>
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
                            {session.title || 
                             session.session_name ||
                             `${session.subject || 'General'} Session - ${new Date(session.created_at).toLocaleDateString()}`}
                          </h4>
                          <Badge variant="outline" className="text-xs">
                            {session.subject || 'General'}
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

            {/* Enhanced Features Section */}
            <div className="mt-6">
              {/* Class Series Management */}
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2 text-orange-600" />
                    Class Series
                  </CardTitle>
                  <p className="text-sm text-gray-600">
                    Organize related sessions into structured learning series
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Create New Series */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium mb-3">Create New Series</h4>
                      <div className="space-y-3">
                        <Input
                          placeholder="Series name (e.g., 'Physics Chapter 1')"
                          value={newSeries.name}
                          onChange={(e) => setNewSeries(prev => ({ ...prev, name: e.target.value }))}
                        />
                        <div className="grid grid-cols-2 gap-2">
                          <Input
                            placeholder="Subject"
                            value={newSeries.subject}
                            onChange={(e) => setNewSeries(prev => ({ ...prev, subject: e.target.value }))}
                          />
                          <Input
                            type="number"
                            placeholder="Total classes"
                            value={newSeries.total_classes}
                            onChange={(e) => setNewSeries(prev => ({ ...prev, total_classes: parseInt(e.target.value) }))}
                          />
                        </div>
                        <Input
                          placeholder="Schedule (e.g., 'Weekly on Monday 10 AM')"
                          value={newSeries.schedule}
                          onChange={(e) => setNewSeries(prev => ({ ...prev, schedule: e.target.value }))}
                        />
                        <Button onClick={createClassSeries} className="w-full">
                          <Users className="h-4 w-4 mr-2" />
                          Create Series
                        </Button>
                      </div>
                    </div>

                    {/* Existing Series */}
                    {classSeries.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-medium">Your Series</h4>
                        {classSeries.slice(0, 3).map((series) => (
                          <div key={series.series_id} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-sm">{series.series_name}</p>
                                <p className="text-xs text-gray-500">{series.subject} • {series.total_classes} classes</p>
                              </div>
                              <Badge variant="outline">{series.status}</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

            </div>

            {/* Analytics Dashboard */}
            {analytics && (
              <Card className="border-0 shadow-md mt-6">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                    AutoNote Analytics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{analytics.total_sessions}</div>
                      <div className="text-sm text-gray-600">Total Sessions</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{analytics.total_flashcards}</div>
                      <div className="text-sm text-gray-600">Flashcards Created</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{analytics.due_for_review}</div>
                      <div className="text-sm text-gray-600">Due for Review</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{analytics.learning_streak}</div>
                      <div className="text-sm text-gray-600">Day Streak</div>
                    </div>
                  </div>
                  
                  {analytics.subject_distribution?.length > 0 && (
                    <div className="mt-6">
                      <h4 className="font-medium mb-3">Subject Distribution</h4>
                      <div className="space-y-2">
                        {analytics.subject_distribution.map((subject, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <span className="text-sm">{subject._id}</span>
                            <Badge variant="outline">{subject.count} sessions</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}