import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
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
  MessageCircle,
  CreditCard,
  Download,
  BookOpen,
  AlertCircle,
  CheckCircle,
  Loader,
  Upload,
  X,
  ChevronUp,
  ChevronDown,
  ArrowLeft,
  Star,
  TrendingUp,
  Award
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AutoNoteMentor() {
  const { user } = useAuth();
  const { 
    checkFeatureAccess, 
    trackFeatureUsage, 
    getFeatureRemaining, 
    getFeatureLimit,
    currentTier 
  } = useSubscription();
  
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
  const [activeView, setActiveView] = useState('home'); // home, notes, library, flashcards, quiz
  const [showExplanationModal, setShowExplanationModal] = useState(false);
  const [expandMentorView, setExpandMentorView] = useState(false);
  
  // Interactive Features
  const [selectedNotes, setSelectedNotes] = useState(null);
  const [showFlashcards, setShowFlashcards] = useState(false);
  const [explainRequest, setExplainRequest] = useState('');
  const [explanation, setExplanation] = useState(null);
  
  // Notes Library State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, quality
  
  // Removed: Enhanced Features State (Analytics, Class Series) - not essential for core note-taking functionality
  
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
    // CRITICAL: Check subscription access FIRST
    const accessInfo = await checkFeatureAccess('auto_note_uploads_daily');
    if (!accessInfo.has_access) {
      // Upsell modal will be shown automatically by the context
      return;
    }

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
        
        // Track feature usage for subscription
        await trackFeatureUsage('auto_note_uploads_daily');
        
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
    if (!currentSession || !explainRequest.trim()) {
      setError('Please enter a question or topic to explain');
      return;
    }
    
    setLoading(true);
    setError(null);
    
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
        setShowExplanationModal(true);
        setExplainRequest(''); // Clear the input
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to generate explanation. Please try again.');
      }
    } catch (error) {
      console.error('Explanation error:', error);
      setError('Failed to generate explanation. Please check your connection and try again.');
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

  // Notes Library Functions
  const getFilteredSessions = () => {
    let filtered = [...sessions];
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(session =>
        session.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        session.subject?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Subject filter
    if (selectedSubject !== 'all') {
      filtered = filtered.filter(session => session.subject === selectedSubject);
    }
    
    // Status filter
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(session => session.status === selectedStatus);
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'quality':
          return (b.ai_confidence || 0.8) - (a.ai_confidence || 0.8);
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });
    
    return filtered;
  };

  const getRecentSessions = () => {
    return sessions
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);
  };

  const getStatusBadge = (status, aiConfidence = 0.8) => {
    switch (status) {
      case 'completed':
        return {
          icon: '✅',
          text: 'Completed',
          color: 'bg-green-100 text-green-800 border-green-200'
        };
      case 'processing':
        return {
          icon: '⏳',
          text: 'Processing',
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200'
        };
      case 'active':
        return {
          icon: '🟡',
          text: 'Uploaded',
          color: 'bg-blue-100 text-blue-800 border-blue-200'
        };
      default:
        return {
          icon: '📝',
          text: 'Ready',
          color: 'bg-gray-100 text-gray-800 border-gray-200'
        };
    }
  };

  const getQualityScore = (session) => {
    return Math.round((session.ai_confidence || 0.8) * 100);
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      'Mathematics': '📐',
      'Physics': '⚛️',
      'Chemistry': '🧪',
      'Biology': '🧬',
      'General Studies': '📚',
      'Current Affairs': '📰',
      'History': '🏛️',
      'Geography': '🌍',
      'Polity': '🏛️',
      'General': '📝'
    };
    return icons[subject] || '📝';
  };

  // Enhanced formatting function for Professor content (Academic Style)
  const formatProfessorContent = (content) => {
    if (!content) return null;
    
    // Clean the content first - remove all special characters and normalize
    const cleanContent = content
      .replace(/\*\*/g, '') // Remove ** markdown
      .replace(/###\s*/g, '') // Remove ### headers
      .replace(/^\s*[\-\*•]\s*/gm, '') // Remove bullet markers
      .replace(/\\/g, '') // Remove backslashes
      .replace(/^\s*\d+\.\s*/gm, '') // Remove existing numbering
      .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
      .trim();
    
    // Split into logical sections
    const sections = cleanContent.split('\n\n').filter(section => section.trim().length > 0);
    let sectionCounter = 1;
    let pointCounter = 1;
    
    return sections.map((section, sectionIdx) => {
      const lines = section.split('\n').filter(line => line.trim().length > 0);
      
      return (
        <div key={sectionIdx} className="mb-7">
          {lines.map((line, lineIdx) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return null;
            
            // Main section headers (academic style)
            if (lineIdx === 0 && (trimmedLine.length > 30 || trimmedLine.toLowerCase().includes('educational notes') || 
                trimmedLine.toLowerCase().includes('key concepts') || trimmedLine.toLowerCase().includes('important') ||
                trimmedLine.includes(':'))) {
              const displayTitle = trimmedLine.replace(/:/g, '').trim();
              const currentSection = sectionCounter++;
              
              return (
                <div key={lineIdx} className="mb-5">
                  <div className="flex items-center mb-3">
                    <div className="w-6 h-6 bg-slate-600 text-white rounded-md flex items-center justify-center mr-3 text-sm font-semibold">
                      {currentSection}
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800 leading-snug">
                      {displayTitle}
                    </h3>
                  </div>
                </div>
              );
            }
            
            // Sub-concepts or definitions (refined academic style)
            if (trimmedLine.includes(':') && trimmedLine.length < 200) {
              const [term, ...definitionParts] = trimmedLine.split(':');
              const definition = definitionParts.join(':').trim();
              const currentPoint = pointCounter++;
              
              return (
                <div key={lineIdx} className="mb-4 ml-6">
                  <div className="flex items-start">
                    <span className="inline-flex items-center justify-center w-5 h-5 bg-slate-500 text-white rounded text-xs font-medium mr-3 mt-0.5 flex-shrink-0">
                      {currentPoint}
                    </span>
                    <div className="flex-1">
                      <h4 className="text-base font-medium text-slate-700 mb-1.5 leading-relaxed">
                        {term.trim()}
                      </h4>
                      {definition && (
                        <p className="text-slate-600 leading-relaxed text-sm pl-3 border-l-2 border-slate-200">
                          {definition}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            }
            
            // Regular content points (clean bullet style)
            if (trimmedLine.length > 20) {
              return (
                <div key={lineIdx} className="mb-3 ml-6">
                  <div className="flex items-start">
                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-2.5 mr-3 flex-shrink-0"></span>
                    <p className="text-slate-700 leading-relaxed text-sm">
                      {trimmedLine}
                    </p>
                  </div>
                </div>
              );
            }
            
            return null;
          })}
        </div>
      );
    });
  };

  // Enhanced formatting function for Mentor content (Refined Supportive Style)
  const formatMentorContent = (content) => {
    if (!content) return null;
    
    // Clean the mentor content - remove special characters and normalize
    const cleanContent = content
      .replace(/\*\*/g, '') // Remove ** markdown
      .replace(/###\s*/g, '') // Remove ### headers
      .replace(/^\s*[\-\*•]\s*/gm, '') // Remove bullet markers
      .replace(/\\/g, '') // Remove backslashes
      .replace(/^\s*\d+\.\s*/gm, '') // Remove existing numbering
      .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
      .trim();
    
    // Split into logical sections for mentor guidance
    const sections = cleanContent.split('\n\n').filter(section => section.trim().length > 0);
    let tipCounter = 1;
    
    return sections.map((section, sectionIdx) => {
      const lines = section.split('\n').filter(line => line.trim().length > 0);
      
      return (
        <div key={sectionIdx} className="mb-5">
          {lines.map((line, lineIdx) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return null;
            
            // Mentor section headers (subtle academic style)
            if (lineIdx === 0 && (trimmedLine.length > 25 || trimmedLine.toLowerCase().includes('enhanced') || 
                trimmedLine.toLowerCase().includes('encouragement') || trimmedLine.toLowerCase().includes('advice'))) {
              const displayTitle = trimmedLine.replace(/:/g, '').trim();
              
              return (
                <div key={lineIdx} className="mb-3">
                  <div className="flex items-center mb-2">
                    <Heart className="h-4 w-4 text-emerald-600 mr-2" />
                    <h4 className="text-base font-medium text-emerald-700">
                      {displayTitle}
                    </h4>
                  </div>
                </div>
              );
            }
            
            // Encouragement and motivational content (refined style)
            if (trimmedLine.includes('!') || /\b(great|excellent|good|keep|continue|progress|kudos|perfect|amazing|wonderful)\b/i.test(trimmedLine)) {
              return (
                <div key={lineIdx} className="bg-emerald-50 rounded-md p-3 mb-3 border-l-3 border-emerald-300">
                  <div className="flex items-start">
                    <span className="text-lg mr-2 mt-0.5">💡</span>
                    <p className="text-emerald-800 text-sm leading-relaxed">
                      {trimmedLine}
                    </p>
                  </div>
                </div>
              );
            }
            
            // Study tips and advice (clean numbered style)
            if (trimmedLine.length > 30 && (trimmedLine.includes(':') || /\b(tip|advice|remember|strategy|approach)\b/i.test(trimmedLine))) {
              const currentTip = tipCounter++;
              
              return (
                <div key={lineIdx} className="mb-3">
                  <div className="flex items-start">
                    <span className="inline-flex items-center justify-center w-5 h-5 bg-emerald-600 text-white rounded text-xs font-medium mr-3 mt-0.5 flex-shrink-0">
                      {currentTip}
                    </span>
                    <div className="flex-1">
                      <p className="text-slate-700 leading-relaxed text-sm">
                        {trimmedLine.replace(/:/g, ' –').trim()}
                      </p>
                    </div>
                  </div>
                </div>
              );
            }
            
            // Regular supportive content (minimalist bullets)
            if (trimmedLine.length > 15) {
              return (
                <div key={lineIdx} className="mb-2 ml-4">
                  <div className="flex items-start">
                    <span className="w-1 h-1 bg-emerald-400 rounded-full mt-2.5 mr-3 flex-shrink-0"></span>
                    <p className="text-slate-600 leading-relaxed text-sm">
                      {trimmedLine}
                    </p>
                  </div>
                </div>
              );
            }
            
            return null;
          })}
        </div>
      );
    });
  };
  // Enhanced formatting function for Student-Friendly content (Beautiful & Accessible)
  const formatStudentFriendlyContent = (content, colorTheme = 'purple') => {
    if (!content) return null;
    
    // Clean the content first - remove all special characters and normalize
    const cleanContent = content
      .replace(/\*\*/g, '') // Remove ** markdown
      .replace(/###\s*/g, '') // Remove ### headers
      .replace(/^\s*[\-\*•]\s*/gm, '') // Remove bullet markers
      .replace(/\\/g, '') // Remove backslashes
      .replace(/^\s*\d+\.\s*/gm, '') // Remove existing numbering
      .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
      .trim();
    
    // Color theme mapping
    const themes = {
      purple: {
        primary: 'purple-500',
        secondary: 'purple-600',
        light: 'purple-50',
        border: 'purple-200'
      },
      emerald: {
        primary: 'emerald-500',
        secondary: 'emerald-600', 
        light: 'emerald-50',
        border: 'emerald-200'
      },
      blue: {
        primary: 'blue-500',
        secondary: 'blue-600',
        light: 'blue-50', 
        border: 'blue-200'
      }
    };
    
    const theme = themes[colorTheme] || themes.purple;
    
    // Split into logical sections
    const sections = cleanContent.split('\n\n').filter(section => section.trim().length > 0);
    let pointCounter = 1;
    
    return sections.map((section, sectionIdx) => {
      const lines = section.split('\n').filter(line => line.trim().length > 0);
      
      return (
        <div key={sectionIdx} className="mb-6">
          {lines.map((line, lineIdx) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return null;
            
            // Main section headers (student-friendly style)
            if (lineIdx === 0 && (trimmedLine.length > 25 || trimmedLine.toLowerCase().includes('notes') || 
                trimmedLine.toLowerCase().includes('concepts') || trimmedLine.toLowerCase().includes('important') ||
                trimmedLine.includes(':'))) {
              const displayTitle = trimmedLine.replace(/:/g, '').trim();
              
              return (
                <div key={lineIdx} className="mb-4">
                  <div className="flex items-center mb-3">
                    <div className={`w-2 h-8 bg-${theme.primary} rounded-full mr-3`}></div>
                    <h3 className="text-lg font-semibold text-gray-800 leading-snug">
                      {displayTitle}
                    </h3>
                  </div>
                </div>
              );
            }
            
            // Key points with beautiful formatting
            if (trimmedLine.includes(':') && trimmedLine.length < 200) {
              const [term, ...definitionParts] = trimmedLine.split(':');
              const definition = definitionParts.join(':').trim();
              const currentPoint = pointCounter++;
              
              return (
                <div key={lineIdx} className="mb-4">
                  <div className={`bg-${theme.light} rounded-lg p-4 border-l-4 border-${theme.primary}`}>
                    <div className="flex items-start">
                      <span className={`inline-flex items-center justify-center w-6 h-6 bg-${theme.secondary} text-white rounded-full text-sm font-medium mr-3 mt-0.5 flex-shrink-0`}>
                        {currentPoint}
                      </span>
                      <div className="flex-1">
                        <h4 className="text-base font-semibold text-gray-800 mb-2 leading-relaxed">
                          {term.trim()}
                        </h4>
                        {definition && (
                          <p className="text-gray-700 leading-relaxed text-sm">
                            {definition}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            }
            
            // Bullet points (student-friendly style)
            if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-') || trimmedLine.match(/^\d+\./)) {
              const cleanText = trimmedLine.replace(/^[•\-\d\.]\s*/, '').trim();
              
              return (
                <div key={lineIdx} className="mb-3 ml-4">
                  <div className="flex items-start">
                    <span className={`w-2 h-2 bg-${theme.primary} rounded-full mt-2.5 mr-3 flex-shrink-0`}></span>
                    <p className="text-gray-700 leading-relaxed text-sm">
                      {cleanText}
                    </p>
                  </div>
                </div>
              );
            }
            
            // Regular content (clean paragraph style)
            if (trimmedLine.length > 15) {
              return (
                <div key={lineIdx} className="mb-3">
                  <p className="text-gray-700 leading-relaxed text-sm pl-4 border-l-2 border-gray-200">
                    {trimmedLine}
                  </p>
                </div>
              );
            }
            
            return null;
          })}
        </div>
      );
    });
  };

  // ============= ENHANCED FEATURES FUNCTIONS =============

  // Removed: Unnecessary features (Document Analysis, Spaced Repetition, Smart Search, Class Series, Analytics)
  // These features either exist in AI Tutor or are not essential for core note-taking functionality

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
                <Button 
                  onClick={() => {
                    // Navigate back to sessions list view
                    setSessionStatus('idle');
                    setActiveView('home');
                    setCurrentSession(null);
                    setGeneratedNotes(null);
                    setDualAnalysis(null);
                    setSelectedNotes(null);
                    setExplanation(null);
                    loadUserSessions(); // Refresh the sessions list
                  }} 
                  variant="outline"
                >
                  <Clock className="h-4 w-4 mr-2" />
                  Back to Sessions
                </Button>
                <Button 
                  onClick={() => {
                    // Start completely fresh session
                    setSessionStatus('idle');
                    setActiveView('home');
                    setCurrentSession(null);
                    setGeneratedNotes(null);
                    setDualAnalysis(null);
                    setSelectedNotes(null);
                    setExplanation(null);
                    setNewSessionTitle('');
                    setNewSessionSubject('Mathematics');
                    setSelectedFile(null);
                    setLiveTranscript('');
                    setConceptsDetected([]);
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
              {/* Professor Analysis - Primary (Academic Style) */}
              <Card className="shadow-sm border border-slate-200">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center text-lg font-medium">
                      <GraduationCap className="h-5 w-5 mr-2.5 text-slate-600" />
                      Professor's Academic Notes
                    </CardTitle>
                    <Badge variant="secondary" className="bg-slate-100 text-slate-700 text-xs px-2.5 py-1">
                      Primary
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-600 mt-1.5">Structured educational content and key concepts</p>
                </CardHeader>
                <CardContent className="pt-0 px-6 pb-6">
                  <div className="bg-white rounded-md p-4 shadow-inner border border-purple-100">
                    <div className="text-gray-800 leading-relaxed space-y-3">
                      {formatStudentFriendlyContent(dualAnalysis.professor_analysis.content, 'purple')}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Mentor Guidance - Supportive (Refined Collapsible) */}
              <Card className="shadow-sm border border-slate-200">
                <CardHeader 
                  className="cursor-pointer hover:bg-slate-50 transition-colors pb-4"
                  onClick={() => setExpandMentorView(!expandMentorView)}
                >
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center text-base font-medium">
                      <Heart className="h-4 w-4 mr-2.5 text-emerald-600" />
                      Study Tips & Learning Guidance
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-emerald-700 border-emerald-300 text-xs">
                        Supportive
                      </Badge>
                      {expandMentorView ? (
                        <ChevronUp className="h-4 w-4 text-slate-500" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-slate-500" />
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">
                    {expandMentorView ? 'Hide' : 'View'} personalized study recommendations
                  </p>
                </CardHeader>
                
                {expandMentorView && (
                  <CardContent className="pt-0 px-6 pb-6 border-t border-slate-100">
                    <div className="bg-emerald-50/30 rounded-lg p-4 border border-emerald-200">
                      <div className="text-slate-700 leading-relaxed">
                        {formatStudentFriendlyContent(dualAnalysis.mentor_guidance.content, 'emerald')}
                      </div>
                    </div>
                  </CardContent>
                )}
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
                      <div className="bg-yellow-50 rounded-lg p-4">
                        <h4 className="font-semibold mb-3 text-gray-900">🎯 Key Concepts</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {generatedNotes.key_concepts.map((concept, index) => (
                            <div key={index} className="bg-white rounded-md p-2 border border-yellow-200">
                              <span className="text-gray-800 font-medium">{concept}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Important Points */}
                    {generatedNotes.important_points?.length > 0 && (
                      <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-semibold mb-3 text-gray-900">💡 Important Points</h4>
                        <ul className="space-y-3">
                          {generatedNotes.important_points.map((point, index) => (
                            <li key={index} className="flex items-start">
                              <CheckCircle className="h-4 w-4 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700 leading-relaxed">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Formulas */}
                    {generatedNotes.formulas_mentioned?.length > 0 && (
                      <div className="bg-indigo-50 rounded-lg p-4">
                        <h4 className="font-semibold mb-3 text-gray-900">📐 Formulas & Equations</h4>
                        <div className="space-y-3">
                          {generatedNotes.formulas_mentioned.map((formula, index) => (
                            <div key={index} className="bg-white rounded-md p-4 border border-indigo-200 shadow-sm">
                              <code className="text-gray-800 text-sm font-mono block">{formula}</code>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Questions Raised */}
                    {generatedNotes.questions_raised?.length > 0 && (
                      <div className="bg-orange-50 rounded-lg p-4">
                        <h4 className="font-semibold mb-3 text-gray-900">🤔 Questions & Doubts</h4>
                        <ul className="space-y-3">
                          {generatedNotes.questions_raised.map((question, index) => (
                            <li key={index} className="flex items-start">
                              <AlertCircle className="h-4 w-4 text-orange-600 mr-3 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700 leading-relaxed">{question}</span>
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
                  <Button 
                    onClick={generateFlashcards} 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
                    disabled={loading}
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    {loading ? 'Generating...' : 'Generate Flashcards'}
                  </Button>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Ask AI for Explanation
                      </label>
                      <Input
                        placeholder="e.g., 'Explain Newton's first law' or 'What is photosynthesis?'"
                        value={explainRequest}
                        onChange={(e) => setExplainRequest(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && explainRequest.trim()) {
                            explainPoint();
                          }
                        }}
                      />
                    </div>
                    <Button 
                      onClick={explainPoint} 
                      className="w-full bg-green-600 hover:bg-green-700 text-white" 
                      size="sm"
                      disabled={loading || !explainRequest.trim()}
                    >
                      <MessageCircle className="h-4 w-4 mr-2" />
                      {loading ? 'Getting Explanation...' : 'Get Explanation'}
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

          {/* Explanation Modal */}
          {showExplanationModal && explanation && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900">
                      🤖 AI Explanation: {explanation.point_reference}
                    </h3>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setShowExplanationModal(false)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="border-l-4 border-purple-500 pl-4">
                      <div className="flex items-center mb-3">
                        <GraduationCap className="h-5 w-5 text-purple-600 mr-2" />
                        <span className="font-semibold">Professor's Explanation</span>
                        <Badge variant="outline" className="ml-2 text-xs">Technical</Badge>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <div className="text-gray-800 text-sm leading-relaxed space-y-2">
                          {explanation.explanation.professor_explanation.content.split('\n\n').map((paragraph, idx) => (
                            <p key={idx} className="mb-2">
                              {paragraph.split('\n').map((line, lineIdx) => (
                                <span key={lineIdx}>
                                  {line}
                                  {lineIdx < paragraph.split('\n').length - 1 && <br />}
                                </span>
                              ))}
                            </p>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="border-l-4 border-green-500 pl-4">
                      <div className="flex items-center mb-3">
                        <Heart className="h-5 w-5 text-green-600 mr-2" />
                        <span className="font-semibold">Mentor's Guidance</span>
                        <Badge variant="outline" className="ml-2 text-xs">Personalized</Badge>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4">
                        <div className="text-gray-800 text-sm leading-relaxed space-y-2">
                          {explanation.explanation.mentor_guidance.content.split('\n\n').map((paragraph, idx) => (
                            <p key={idx} className="mb-2">
                              {paragraph.split('\n').map((line, lineIdx) => (
                                <span key={lineIdx}>
                                  {line}
                                  {lineIdx < paragraph.split('\n').length - 1 && <br />}
                                </span>
                              ))}
                            </p>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex justify-end space-x-3">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowExplanationModal(false)}
                    >
                      Close
                    </Button>
                    <Button 
                      onClick={() => {
                        navigator.clipboard.writeText(
                          `Professor: ${explanation.explanation.professor_explanation.content}\n\nMentor: ${explanation.explanation.mentor_guidance.content}`
                        );
                      }}
                      variant="default"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Copy Explanation
                    </Button>
                  </div>
                </div>
              </div>
            </div>
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

  // Notes Library Screen
  if (activeView === 'library') {
    const filteredSessions = getFilteredSessions();
    const subjectsInSessions = [...new Set(sessions.map(s => s.subject).filter(Boolean))];
    
    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          {/* Enhanced Professional Header */}
          <div className="mb-8">
            {/* Navigation Bar */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Button 
                    onClick={() => setActiveView('home')} 
                    className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-2.5 rounded-lg font-medium shadow-md transition-all duration-200 hover:shadow-lg"
                  >
                    <ArrowLeft className="h-5 w-5 mr-2" />
                    Back to Home
                  </Button>
                  
                  <div className="h-8 w-px bg-gray-300"></div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-3 rounded-xl shadow-lg">
                      <BookOpen className="h-7 w-7 text-white" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                        My Notes Library
                      </h1>
                      <p className="text-sm text-gray-600 font-medium">
                        📚 Your AI-Generated Study Collection
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">
                      {filteredSessions.length}
                    </div>
                    <div className="text-xs text-gray-500 font-medium">
                      of {sessions.length} notes
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-green-700">All systems active</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Search and Filters */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">🔍 Find Your Notes</h2>
                  <div className="text-sm text-gray-600">
                    Smart search & filtering powered by AI
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-6">
                  {/* Enhanced Search */}
                  <div className="lg:col-span-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      🔍 Search Notes
                    </label>
                    <div className="relative">
                      <Input
                        placeholder="Type to search by title, subject, or content..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                      />
                      {searchTerm && (
                        <button
                          onClick={() => setSearchTerm('')}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* Subject Filter */}
                  <div className="lg:col-span-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📚 Subject
                    </label>
                    <select
                      value={selectedSubject}
                      onChange={(e) => setSelectedSubject(e.target.value)}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white transition-all duration-200"
                    >
                      <option value="all">All Subjects ({subjectsInSessions.length})</option>
                      {subjectsInSessions.map(subject => (
                        <option key={subject} value={subject}>
                          {getSubjectIcon(subject)} {subject}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Status Filter */}
                  <div className="lg:col-span-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      ⚡ Status
                    </label>
                    <select
                      value={selectedStatus}
                      onChange={(e) => setSelectedStatus(e.target.value)}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white transition-all duration-200"
                    >
                      <option value="all">All Status</option>
                      <option value="completed">✅ Completed</option>
                      <option value="processing">⏳ Processing</option>
                      <option value="active">🟡 Uploaded</option>
                    </select>
                  </div>
                </div>
                
                {/* Enhanced Sort Options */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-4">
                    <span className="text-sm font-semibold text-gray-700 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2 text-blue-600" />
                      Sort by:
                    </span>
                    <div className="flex space-x-2">
                      {[
                        { value: 'newest', label: '🕒 Newest First', icon: Clock },
                        { value: 'oldest', label: '📅 Oldest First', icon: Clock },
                        { value: 'quality', label: '⭐ AI Quality', icon: Star }
                      ].map(option => (
                        <Button
                          key={option.value}
                          onClick={() => setSortBy(option.value)}
                          variant={sortBy === option.value ? 'default' : 'outline'}
                          size="sm"
                          className={`transition-all duration-200 ${
                            sortBy === option.value 
                              ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md' 
                              : 'hover:bg-blue-50 hover:border-blue-300'
                          }`}
                        >
                          {option.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Enhanced Clear Filters */}
                  {(searchTerm || selectedSubject !== 'all' || selectedStatus !== 'all') && (
                    <Button
                      onClick={() => {
                        setSearchTerm('');
                        setSelectedSubject('all');
                        setSelectedStatus('all');
                      }}
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 border border-red-200 hover:border-red-300 transition-all duration-200"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Clear All Filters
                    </Button>
                  )}
                </div>
                
                {/* Filter Results Summary */}
                <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <Award className="h-4 w-4 inline mr-1" />
                    Showing <span className="font-semibold">{filteredSessions.length}</span> of <span className="font-semibold">{sessions.length}</span> notes
                    {searchTerm && ` matching "${searchTerm}"`}
                    {selectedSubject !== 'all' && ` in ${selectedSubject}`}
                    {selectedStatus !== 'all' && ` with ${selectedStatus} status`}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Notes Grid */}
          {filteredSessions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredSessions.map((session) => {
                const statusBadge = getStatusBadge(session.status, session.ai_confidence);
                const qualityScore = getQualityScore(session);
                
                return (
                  <div key={session.session_id} className="group">
                    <Card className="h-full hover:shadow-xl transition-all duration-300 cursor-pointer border-0 shadow-lg bg-white overflow-hidden hover:scale-[1.02] transform">
                      <CardContent className="p-0 h-full">
                        <div 
                          onClick={() => loadPreviousSession(session.session_id)}
                          className="h-full flex flex-col"
                        >
                          {/* Enhanced Header with Gradient */}
                          <div className="bg-gradient-to-r from-blue-50 via-white to-purple-50 p-5 border-b border-gray-100">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-start space-x-4 flex-1">
                                <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-lg flex-shrink-0">
                                  <span className="text-white text-xl">
                                    {getSubjectIcon(session.subject)}
                                  </span>
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h3 className="font-bold text-gray-900 group-hover:text-blue-700 line-clamp-2 mb-2 text-base leading-snug">
                                    {session.title || session.session_name || `${session.subject || 'General'} Session`}
                                  </h3>
                                  <div className="flex items-center space-x-2">
                                    <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-700 border-blue-200">
                                      {session.subject || 'General'}
                                    </Badge>
                                  </div>
                                </div>
                              </div>
                              
                              <Badge className={`text-xs border flex-shrink-0 ml-2 shadow-sm ${statusBadge.color}`}>
                                <span className="mr-1">{statusBadge.icon}</span>
                                {statusBadge.text}
                              </Badge>
                            </div>
                          </div>

                          {/* Enhanced Content Body */}
                          <div className="flex-1 p-5 space-y-4">
                            {/* Metadata Row */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2 text-sm text-gray-600">
                                <Clock className="h-4 w-4 text-blue-500" />
                                <span className="font-medium">
                                  {session.audio_duration ? 
                                    `${Math.round(session.audio_duration / 60)} min` : 
                                    'Unknown'
                                  }
                                </span>
                              </div>
                              
                              {session.status === 'completed' && (
                                <div className="flex items-center space-x-2">
                                  <div className="flex items-center">
                                    <Star className={`h-4 w-4 mr-1 ${
                                      qualityScore >= 80 ? 'text-green-500' : 
                                      qualityScore >= 60 ? 'text-yellow-500' : 'text-red-500'
                                    }`} />
                                    <span className="text-sm font-semibold text-gray-700">{qualityScore}%</span>
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-2">
                              📅 Created {new Date(session.created_at).toLocaleDateString(undefined, {
                                month: 'short', 
                                day: 'numeric',
                                year: 'numeric'
                              })}
                            </div>
                            
                            {/* Enhanced Preview Content */}
                            {session.structured_notes && (
                              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                                <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center">
                                  <Brain className="h-3 w-3 mr-1 text-green-600" />
                                  AI Analysis Preview
                                </div>
                                <div className="grid grid-cols-3 gap-2 text-xs">
                                  <div className="text-center bg-white rounded p-2 border">
                                    <div className="font-bold text-blue-600">
                                      {session.structured_notes.key_concepts?.length || 0}
                                    </div>
                                    <div className="text-gray-600">Concepts</div>
                                  </div>
                                  <div className="text-center bg-white rounded p-2 border">
                                    <div className="font-bold text-green-600">
                                      {session.structured_notes.important_points?.length || 0}
                                    </div>
                                    <div className="text-gray-600">Points</div>
                                  </div>
                                  <div className="text-center bg-white rounded p-2 border">
                                    <div className="font-bold text-purple-600">
                                      {session.structured_notes.formulas_mentioned?.length || 0}
                                    </div>
                                    <div className="text-gray-600">Formulas</div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Enhanced Action Footer */}
                          <div className="p-4 bg-gray-50 border-t border-gray-100">
                            <Button 
                              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium py-2.5 rounded-lg shadow-md transition-all duration-200 hover:shadow-lg group-hover:scale-105 transform"
                            >
                              <BookOpen className="h-4 w-4 mr-2" />
                              Open Study Notes
                              <ArrowLeft className="h-4 w-4 ml-2 rotate-180" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="max-w-md mx-auto">
                <div className="bg-gradient-to-br from-blue-100 to-purple-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8 shadow-lg">
                  {sessions.length === 0 ? (
                    <BookOpen className="h-16 w-16 text-blue-600" />
                  ) : (
                    <AlertCircle className="h-16 w-16 text-blue-600" />
                  )}
                </div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  {sessions.length === 0 ? '📚 Welcome to Your Notes Library!' : '🔍 No Notes Found'}
                </h3>
                
                <p className="text-gray-600 text-lg mb-8 leading-relaxed">
                  {sessions.length === 0 
                    ? "Ready to transform your learning? Create your first AI-powered notes by recording a class or uploading an audio file."
                    : "No notes match your current search. Try adjusting your filters or search terms to find what you're looking for."
                  }
                </p>
                
                {sessions.length === 0 ? (
                  <div className="space-y-4">
                    <Button 
                      onClick={() => setActiveView('home')}
                      className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                    >
                      <Mic className="h-5 w-5 mr-2" />
                      Start Creating Notes
                    </Button>
                    
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
                      <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
                        <div className="text-2xl mb-2">🎤</div>
                        <div className="text-sm font-medium text-gray-900">Live Recording</div>
                        <div className="text-xs text-gray-600">Record classes in real-time</div>
                      </div>
                      <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
                        <div className="text-2xl mb-2">📁</div>
                        <div className="text-sm font-medium text-gray-900">File Upload</div>
                        <div className="text-xs text-gray-600">Upload existing recordings</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Button
                      onClick={() => {
                        setSearchTerm('');
                        setSelectedSubject('all');
                        setSelectedStatus('all');
                      }}
                      variant="outline"
                      className="border-blue-300 text-blue-600 hover:bg-blue-50 px-6 py-2"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Clear All Filters
                    </Button>
                    
                    <Button 
                      onClick={() => setActiveView('home')}
                      className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-2 ml-4"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Create New Notes
                    </Button>
                  </div>
                )}
              </div>
            </div>
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
                        {(subjects[user?.exam_type] || subjects['JEE'] || ['Mathematics', 'Physics', 'Chemistry'])?.map(subject => (
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

          {/* Recent Notes Widget */}
          <div>
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <BookOpen className="h-5 w-5 mr-2 text-blue-600" />
                    Recent Notes
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {sessions.length} Total
                  </Badge>
                </CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Quick access to your latest AI-generated notes
                </p>
              </CardHeader>
              <CardContent>
                {getRecentSessions().length > 0 ? (
                  <div className="space-y-3">
                    {getRecentSessions().map((session) => {
                      const statusBadge = getStatusBadge(session.status, session.ai_confidence);
                      const qualityScore = getQualityScore(session);
                      
                      return (
                        <div
                          key={session.session_id}
                          onClick={() => loadPreviousSession(session.session_id)}
                          className="group p-4 border rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-200 transition-all duration-200 hover:shadow-md"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-start space-x-3 flex-1">
                              <span className="text-xl mt-0.5 flex-shrink-0">
                                {getSubjectIcon(session.subject)}
                              </span>
                              <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-sm text-gray-900 truncate group-hover:text-blue-700">
                                  {session.title || 
                                   session.session_name ||
                                   `${session.subject || 'General'} Session`}
                                </h4>
                                <p className="text-xs text-gray-500 mt-0.5">
                                  {session.subject || 'General'} • {new Date(session.created_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                            
                            <div className="flex flex-col items-end space-y-1 flex-shrink-0 ml-3">
                              <Badge className={`text-xs border ${statusBadge.color}`}>
                                <span className="mr-1">{statusBadge.icon}</span>
                                {statusBadge.text}
                              </Badge>
                              
                              {session.status === 'completed' && (
                                <div className="flex items-center text-xs">
                                  <div className={`w-2 h-2 rounded-full mr-1 ${
                                    qualityScore >= 80 ? 'bg-green-500' : 
                                    qualityScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}></div>
                                  <span className="text-gray-500">{qualityScore}% Quality</span>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {session.audio_duration ? 
                                `${Math.round(session.audio_duration / 60)} min` : 
                                'Duration unknown'
                              }
                            </span>
                            
                            <span className="group-hover:text-blue-600 font-medium">
                              View Notes →
                            </span>
                          </div>
                        </div>
                      );
                    })}
                    
                    {/* View All Notes Button */}
                    <Button 
                      onClick={() => setActiveView('library')}
                      variant="outline" 
                      className="w-full mt-4 border-dashed border-blue-300 text-blue-600 hover:bg-blue-50 hover:border-blue-400"
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      View All Notes ({sessions.length})
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BookOpen className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No notes created yet</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Record a session or upload a file to get started
                    </p>
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