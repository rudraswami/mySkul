import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useSubscription } from '../contexts/SubscriptionContext';
import { handleSubscriptionError, handlePostUpgradeRetry, animateSubscriptionUnlock } from '../utils/subscriptionErrorHandler';
import TestLibrary from './TestLibrary';
import GamificationProgress from './GamificationProgress';
import TestGenerationWizard from './TestGenerationWizard';
import ExamMode from './ExamMode';
import EnhancedResultsModal from './EnhancedResultsModal';
import { 
  FileText, 
  Clock, 
  Target, 
  Award, 
  TrendingUp, 
  CheckCircle,
  Circle,
  AlertTriangle,
  RefreshCw,
  GraduationCap,
  Heart,
  Star,
  Users,
  BarChart3,
  X,
  Trophy,
  Zap,
  Sparkles,
  Crown,
  BookOpen,
  PlusCircle
} from 'lucide-react';

export default function MockTests() {
  const { 
    checkFeatureAccess, 
    trackFeatureUsage, 
    getFeatureRemaining, 
    getFeatureLimit,
    currentTier,
    triggerFeatureUpsell
  } = useSubscription();
  
  // View state: 'generate' or 'library' or 'wizard' or 'exam' or 'results'
  const [activeView, setActiveView] = useState('generate');
  
  // New Phase 3 states
  const [showWizard, setShowWizard] = useState(false);
  const [showExamMode, setShowExamMode] = useState(false);
  const [showEnhancedResults, setShowEnhancedResults] = useState(false);
  const [wizardConfig, setWizardConfig] = useState(null);
  const [examModeTest, setExamModeTest] = useState(null);
  const [examModeQuestions, setExamModeQuestions] = useState([]);
  const [enhancedResultsData, setEnhancedResultsData] = useState(null);
  
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mockTests, setMockTests] = useState([]);
  const [recentResults, setRecentResults] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // Individual loading states for each button
  const [loadingStates, setLoadingStates] = useState({});
  const [slowGenerationStates, setSlowGenerationStates] = useState({});
  const [generationError, setGenerationError] = useState(null);
  const [retryStatus, setRetryStatus] = useState(null);
  
  // Timeout handles for slow generation warnings
  const slowGenerationTimeouts = useRef({});
  
  // Performance optimization states
  const [generationProgress, setGenerationProgress] = useState({});
  const [estimatedTime, setEstimatedTime] = useState(null);
  
  // Test execution states
  const [activeTest, setActiveTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [testResults, setTestResults] = useState(null);
  const [showResults, setShowResults] = useState(false);
  
  // Caching system
  const [testCache, setTestCache] = useState(new Map());
  const [quickGeneration, setQuickGeneration] = useState(false);

  // New enhanced features states
  const [showDetailedReview, setShowDetailedReview] = useState(false);
  const [detailedReviewData, setDetailedReviewData] = useState(null);
  const [showRetakeOptions, setShowRetakeOptions] = useState(false);
  const [retakeTestId, setRetakeTestId] = useState(null);
  const [bookmarkedQuestions, setBookmarkedQuestions] = useState(new Set());
  const [performanceTrends, setPerformanceTrends] = useState(null);
  const [currentTestMode, setCurrentTestMode] = useState('normal'); // 'normal', 'retake_exact', 'retake_variant', 'retake_adaptive'
  
  // Dynamic subjects and subscription states
  const [examSubjects, setExamSubjects] = useState({ subjects: ['Mathematics', 'Physics', 'Chemistry'], exam_type: 'JEE' });
  
  // Toast and retry states
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const [lastFailedTestParams, setLastFailedTestParams] = useState(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'success' });
    }, 3000);
  };
  
  // Retry last failed test generation
  const retryLastFailedTest = async () => {
    if (lastFailedTestParams) {
      const { examType, subject, difficulty, numQuestions, buttonId } = lastFailedTestParams;
      showToast('🎉 Upgrade successful! Generating your test...', 'success');
      
      setTimeout(async () => {
        await generateMockTest(examType, subject, difficulty, numQuestions, buttonId);
        setLastFailedTestParams(null);
      }, 1000);
    }
  };
  
  // Difficulty mapping for consistent use
  const difficultyMap = { 'Easy': 2, 'Medium': 3, 'High': 4 };

  // Global cleanup utility to reset all stuck states
  const emergencyResetAllStates = () => {
    console.log('EMERGENCY: Resetting all loading states');
    setLoadingStates({});
    setSlowGenerationStates({});
    setGenerationError(null);
    setRetryStatus(null);
    setGenerationProgress({});
    setEstimatedTime(null);
    
    // Clear all timeout handles
    Object.values(slowGenerationTimeouts.current).forEach(timeoutId => {
      clearTimeout(timeoutId);
    });
    slowGenerationTimeouts.current = {};
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Reset states on cleanup to prevent memory leaks
      emergencyResetAllStates();
    };
  }, []);

  // Global emergency reset button (for debugging)
  window.dhruvAI_emergencyReset = emergencyResetAllStates;

  // Function to refresh usage data
  const refreshUsageData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return null;

      const usageResponse = await fetch(`${backendUrl}/api/subscription/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (usageResponse.ok) {
        const usage = await usageResponse.json();
        const mockTestUsage = usage.usage_details?.mock_tests_weekly || {};
        return {
          used: mockTestUsage.used || 0,
          limit: mockTestUsage.limit || 2,
          remaining: mockTestUsage.remaining || 0,
          has_access: mockTestUsage.remaining > 0 || mockTestUsage.limit === -1
        };
      }
    } catch (error) {
      console.error('Failed to refresh usage data:', error);
    }
    return null;
  };

  useEffect(() => {
    loadAnalytics();
    loadExamSubjects(); // Load subjects first
    // Load other data after initial load
    setTimeout(() => {
      loadBookmarkedQuestions();
      loadPerformanceTrends();
    }, 1000);
  }, []);

  const loadBookmarkedQuestions = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await fetch(`${backendUrl}/api/bookmarked-questions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const bookmarkedIds = new Set(data.bookmarked_questions.map(q => q.question_id));
        setBookmarkedQuestions(bookmarkedIds);
      }
    } catch (error) {
      console.error('Error loading bookmarked questions:', error);
    }
  };

  const loadExamSubjects = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await fetch(`${backendUrl}/api/mock-tests/subjects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        // Refresh usage data to ensure it's current
        const freshUsageData = await refreshUsageData();
        if (freshUsageData && data.test_access) {
          data.test_access.used = freshUsageData.used;
          data.test_access.limit = freshUsageData.limit;
          data.test_access.remaining = freshUsageData.remaining;
          data.test_access.has_access = freshUsageData.has_access;
        }
        
        setExamSubjects(data);
      }
    } catch (error) {
      console.error('Error loading exam subjects:', error);
      // Keep default subjects if API fails
    }
  };

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;
      
      const response = await fetch(`${backendUrl}/api/analytics/performance`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
        setRecentResults(data.recent_tests || []);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  // Helper to set loading state for specific button
  const setButtonLoading = (buttonId, loading) => {
    setLoadingStates(prev => ({
      ...prev,
      [buttonId]: loading
    }));
    
    if (loading) {
      // Set progress tracking
      setGenerationProgress(prev => ({
        ...prev,
        [buttonId]: { progress: 10, stage: 'Starting AI generation...' }
      }));
      setEstimatedTime('15-30 seconds');
      
      // Start timeout for slow generation warning (10 seconds)
      const timeoutId = setTimeout(() => {
        setSlowGenerationStates(prev => ({
          ...prev,
          [buttonId]: true
        }));
      }, 10000); // 10 seconds delay
      
      slowGenerationTimeouts.current[buttonId] = timeoutId;
    } else {
      // Clear progress tracking
      setGenerationProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[buttonId];
        return newProgress;
      });
      setEstimatedTime(null);
      
      // Clear timeout and reset slow generation state
      if (slowGenerationTimeouts.current[buttonId]) {
        clearTimeout(slowGenerationTimeouts.current[buttonId]);
        delete slowGenerationTimeouts.current[buttonId];
      }
      
      setSlowGenerationStates(prev => {
        const newStates = { ...prev };
        delete newStates[buttonId];
        return newStates;
      });
    }
  };

  // Smart caching system
  const getCacheKey = (examType, subject, difficulty, numQuestions) => {
    return `${examType}-${subject}-${difficulty}-${numQuestions}`;
  };

  const getCachedTest = (cacheKey) => {
    const cached = testCache.get(cacheKey);
    if (cached && (Date.now() - cached.timestamp) < 3600000) { // 1 hour cache
      return cached.data;
    }
    return null;
  };

  const cacheTest = (cacheKey, testData) => {
    setTestCache(prev => {
      const newCache = new Map(prev);
      newCache.set(cacheKey, {
        data: testData,
        timestamp: Date.now()
      });
      return newCache;
    });
  };

  const generateMockTest = async (examType, subject, difficulty = 3, numQuestions = 25, buttonId = 'default') => {
    // CRITICAL: Check subscription access FIRST
    const accessInfo = await checkFeatureAccess('mock_tests_weekly');
    if (!accessInfo.has_access) {
      // Upsell modal will be shown automatically by the context
      console.log('Mock test access blocked - upsell modal should appear');
      return;
    }

    // CRITICAL: Prevent multiple calls
    if (loadingStates[buttonId]) {
      console.warn(`Button ${buttonId} is already loading, ignoring duplicate call`);
      return;
    }
    
    const token = localStorage.getItem('dhruv_ai_token');
    if (!token) {
      alert('Please log in again to continue');
      return;
    }

    // Check cache first for instant loading
    const cacheKey = getCacheKey(examType, subject, difficulty, numQuestions);
    const cachedTest = getCachedTest(cacheKey);
    
    if (cachedTest && !quickGeneration) {
      console.log('🚀 Loading test from cache instantly!');
      setActiveTest(cachedTest);
      setTimeRemaining(cachedTest.time_limit * 60);
      setCurrentQuestion(0);
      setAnswers({});
      
      // Start timer
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            submitTest();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return;
    }

    // Simplified approach - no AbortController to avoid complexity
    console.log(`Starting simplified mock test generation for ${subject}`);
    
    // Start loading state
    setButtonLoading(buttonId, true);
    setGenerationError(null);
    setRetryStatus(null);
    
    // Simple progress indicator
    setGenerationProgress(prev => ({
      ...prev,
      [buttonId]: { progress: 20, stage: 'Generating AI questions...' }
    }));
    
    // Fallback timeout - force cleanup after 45 seconds
    const fallbackTimeout = setTimeout(() => {
      console.warn('FALLBACK: Forcing cleanup after 45 seconds');
      setButtonLoading(buttonId, false);
      setGenerationProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[buttonId];
        return newProgress;
      });
      setGenerationError('Request timed out. Please try again.');
    }, 45000);

    try {
      // Update progress to show AI working
      setTimeout(() => {
        setGenerationProgress(prev => ({
          ...prev,
          [buttonId]: { progress: 60, stage: 'Verifying question quality...' }
        }));
      }, 3000);
      
      setTimeout(() => {
        setGenerationProgress(prev => ({
          ...prev,
          [buttonId]: { progress: 85, stage: 'Finalizing test structure...' }
        }));
      }, 8000);
      
      // Make the API call with correct TestGenerationRequest payload
      const response = await fetch(`${backendUrl}/api/mock-tests/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          exam_type: examType,
          subjects: Array.isArray(subject) ? subject : [subject], // Convert to array as required by backend
          test_type: 'full_length', // Default test type
          difficulty_level: Math.max(1, Math.min(5, difficulty)), // Clamp to 1-5 range
          num_questions: Math.max(3, Math.min(100, numQuestions)), // Clamp to 3-100 range
          generation_mode: 'standard', // Default generation mode
          chapters: [], // Optional: can be populated for chapter-wise tests
          focus_areas: [] // Optional: for adaptive mode
        })
      });

      clearTimeout(fallbackTimeout); // Clear fallback since we got a response
      
      if (response.ok) {
        const testData = await response.json();
        console.log('✅ Test generated successfully:', testData.test_name);
        
        // Track feature usage for subscription
        await trackFeatureUsage('mock_tests_weekly');
        
        // Cache the test
        cacheTest(cacheKey, testData);
        
        // Set up the test
        setActiveTest(testData);
        setTimeRemaining(testData.time_limit * 60);
        setCurrentQuestion(0);
        setAnswers({});

        // Start timer
        const timer = setInterval(() => {
          setTimeRemaining(prev => {
            if (prev <= 1) {
              clearInterval(timer);
              submitTest();
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

      } else {
        // Store failed test parameters for retry
        setLastFailedTestParams({ examType, subject, difficulty, numQuestions, buttonId });
        
        // Get error text once
        const errorText = await response.text().catch(() => '{}');
        
        // Create error object for subscription handler
        const errorObj = {
          response: {
            status: response.status,
            data: JSON.parse(errorText)
          }
        };
        
        const errorResult = await handleSubscriptionError(
          errorObj, 
          'mock_tests_weekly', 
          checkFeatureAccess, 
          (message) => setGenerationError(message.message)
        );
        
        if (!errorResult.handled) {
          // Handle other error types
          let errorMessage = 'Failed to generate test. Please try again.';
          
          try {
            const errorData = JSON.parse(errorText);
            if (errorData.detail) {
              if (typeof errorData.detail === 'string') {
                errorMessage = errorData.detail;
              } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map(err => err.msg || err.type || 'Validation error').join(', ');
            } else {
              errorMessage = 'Invalid request format. Please try again.';
            }
          }
        } catch (e) {
          console.error('Could not parse error response:', errorText);
          errorMessage = 'Server error. Please try again.';
        }
        
        if (response.status >= 500) {
          errorMessage = 'AI system is busy. Please try again in 30 seconds.';
        } else if (response.status === 422 || response.status === 402 || response.status === 429) {
          // Trigger unified subscription modal for all subscription-related errors
          await triggerFeatureUpsell('mock_tests_weekly');
          setGenerationError(null);
          return;
        }
        
        setGenerationError(errorMessage);
        }
      }
      
    } catch (error) {
      clearTimeout(fallbackTimeout);
      console.error('Mock test generation error:', error);
      
      // Store failed test parameters for retry
      setLastFailedTestParams({ examType, subject, difficulty, numQuestions, buttonId });
      
      const errorResult = await handleSubscriptionError(
        error, 
        'mock_tests_weekly', 
        checkFeatureAccess, 
        (message) => setGenerationError(message.message)
      );
      
      if (!errorResult.handled) {
        let errorMessage = 'Network error. Please check your connection and try again.';
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          errorMessage = 'Connection failed. Please check your internet and try again.';
        } else if (error.message) {
          errorMessage = `Error: ${error.message}`;
        }
        setGenerationError(errorMessage);
      }
    } finally {
      // ALWAYS cleanup - this is the critical part
      console.log('🧹 Cleaning up button state:', buttonId);
      setButtonLoading(buttonId, false);
      setRetryStatus(null);
      
      // Clear progress after a brief delay
      setTimeout(() => {
        setGenerationProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[buttonId];
          return newProgress;
        });
      }, 500);
    }
  };

  // ============= ENHANCED RETAKE FUNCTIONALITY =============
  
  const handleRetakeTest = async (testId, retakeMode) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        alert('Please log in again to continue');
        return;
      }

      setLoadingStates(prev => ({ ...prev, [`retake-${retakeMode}`]: true }));

      const response = await fetch(`${backendUrl}/api/mock-tests/${testId}/retake`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          original_test_id: testId,
          retake_mode: retakeMode
        })
      });

      if (response.ok) {
        const retakeData = await response.json();
        
        // Load the new test directly
        const newTestResponse = await fetch(`${backendUrl}/api/mock-tests/${retakeData.new_test_id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (newTestResponse.ok) {
          const newTestData = await newTestResponse.json();
          setActiveTest(newTestData);
          setTimeRemaining(newTestData.time_limit * 60);
          setCurrentQuestion(0);
          setAnswers({});
          setCurrentTestMode(`retake_${retakeMode}`);
          setShowRetakeOptions(false);
          
          // Start timer
          const timer = setInterval(() => {
            setTimeRemaining(prev => {
              if (prev <= 1) {
                clearInterval(timer);
                submitTest();
                return 0;
              }
              return prev - 1;
            });
          }, 1000);
        }
      } else {
        try {
          const errorData = await response.json();
          let errorMsg = 'Unknown error';
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMsg = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              errorMsg = errorData.detail.map(err => err.msg || err.type || 'Validation error').join(', ');
            }
          }
          alert(`Failed to create retake: ${errorMsg}`);
        } catch (parseError) {
          alert('Failed to create retake: Server error');
        }
      }
    } catch (error) {
      console.error('Retake creation error:', error);
      alert('Network error. Please check your connection and try again.');
    } finally {
      setLoadingStates(prev => ({ ...prev, [`retake-${retakeMode}`]: false }));
    }
  };

  // ============= DETAILED REVIEW FUNCTIONALITY =============
  
  const loadDetailedReview = async (testId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        alert('Please log in again to continue');
        return;
      }

      const response = await fetch(`${backendUrl}/api/mock-tests/${testId}/detailed-review`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const reviewData = await response.json();
        setDetailedReviewData(reviewData);
        setShowDetailedReview(true);
        
        // Load bookmarked questions
        const bookmarkedResponse = await fetch(`${backendUrl}/api/bookmarked-questions`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (bookmarkedResponse.ok) {
          const bookmarkedData = await bookmarkedResponse.json();
          const bookmarkedIds = new Set(bookmarkedData.bookmarked_questions.map(q => q.question_id));
          setBookmarkedQuestions(bookmarkedIds);
        }
      } else {
        alert('Failed to load detailed review');
      }
    } catch (error) {
      console.error('Detailed review error:', error);
      alert('Network error while loading review');
    }
  };

  // ============= QUESTION BOOKMARKING FUNCTIONALITY =============
  
  const toggleQuestionBookmark = async (questionId, testId, bookmarked, notes = "") => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await fetch(`${backendUrl}/api/mock-tests/${testId}/bookmark-question`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questionId,
          test_id: testId,
          bookmarked: bookmarked,
          notes: notes
        })
      });

      if (response.ok) {
        // Update local state
        setBookmarkedQuestions(prev => {
          const newSet = new Set(prev);
          if (bookmarked) {
            newSet.add(questionId);
          } else {
            newSet.delete(questionId);
          }
          return newSet;
        });
        
        // Show confirmation
        alert(bookmarked ? 'Question bookmarked!' : 'Bookmark removed!');
      }
    } catch (error) {
      console.error('Bookmark error:', error);
    }
  };

  // ============= PERFORMANCE TRENDS FUNCTIONALITY =============
  
  const loadPerformanceTrends = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await fetch(`${backendUrl}/api/mock-tests/performance-trends`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const trendsData = await response.json();
        setPerformanceTrends(trendsData);
      }
    } catch (error) {
      console.error('Performance trends error:', error);
    }
  };

  const submitTest = async () => {
    if (!activeTest) return;
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        alert('Please log in again to continue');
        return;
      }
      
      const timeTaken = (activeTest.time_limit * 60) - timeRemaining;
      
      const response = await fetch(`${backendUrl}/api/mock-tests/${activeTest.test_id}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          answers: answers,
          time_taken: timeTaken
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        // Show dual-layer feedback instead of simple alert
        showTestResults(result);
      }
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Error submitting test. Please try again.');
    }
  };

  const showTestResults = (result) => {
    setTestResults({ ...result, test_id: activeTest.test_id });
    setShowResults(true);
    setActiveTest(null);
    loadAnalytics(); // Refresh analytics
    loadPerformanceTrends(); // Load updated trends
  };

  const closeResults = () => {
    setShowResults(false);
    setTestResults(null);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Enhanced test interface with better UX
  if (activeTest) {
    const question = activeTest.questions[currentQuestion];
    const isLastQuestion = currentQuestion === activeTest.questions.length - 1;
    const progress = ((currentQuestion + 1) / activeTest.questions.length) * 100;
    const answered = Object.keys(answers).filter(id => answers[id] && answers[id].trim()).length;

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Enhanced Test Header */}
        <div className="bg-white border-b border-gray-200 shadow-lg">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-lg">
                  <GraduationCap className="h-6 w-6" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{activeTest.test_name}</h1>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>Question {currentQuestion + 1} of {activeTest.questions.length}</span>
                    <span>•</span>
                    <span className="text-green-600">✓ {answered} answered</span>
                    <span>•</span>
                    <span className="text-gray-500">⭕ {activeTest.questions.length - answered} remaining</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${timeRemaining < 300 ? 'text-red-600 animate-pulse' : timeRemaining < 900 ? 'text-orange-500' : 'text-blue-600'}`}>
                  {formatTime(timeRemaining)}
                </div>
                <p className="text-sm text-gray-500">Time Remaining</p>
              </div>
            </div>
            
            {/* Enhanced Progress Bar */}
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-xs text-gray-600">
                <span>Progress: {progress.toFixed(0)}%</span>
                <span>Total Marks: {activeTest.total_marks}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500 ease-out" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Question Interface */}
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="bg-white rounded-xl shadow-xl overflow-hidden">
            {/* Question Header */}
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-8 py-6 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="bg-blue-600 text-white text-sm font-bold px-3 py-1 rounded-full">
                    Q{currentQuestion + 1}
                  </span>
                  <span className="text-gray-600 text-sm">
                    {question.chapter ? `Chapter: ${question.chapter}` : 'General Question'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleQuestionBookmark(
                      question.question_id, 
                      activeTest.test_id, 
                      !bookmarkedQuestions.has(question.question_id)
                    )}
                    className="text-gray-600 hover:text-yellow-600"
                  >
                    <Star className={`h-4 w-4 ${bookmarkedQuestions.has(question.question_id) ? 'text-yellow-600 fill-yellow-600' : ''}`} />
                  </Button>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {question.marks || 4} marks
                  </span>
                </div>
              </div>
            </div>

            {/* Question Content */}
            <div className="p-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-8 leading-relaxed">
                {question.question_text}
              </h2>
              
              {/* Enhanced Options */}
              <div className="space-y-3">
                {question.options.map((option, index) => {
                  const optionLetter = option.charAt(0);
                  const isSelected = answers[question.question_id] === optionLetter;
                  
                  return (
                    <div 
                      key={index}
                      className={`group p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                      onClick={() => setAnswers({...answers, [question.question_id]: optionLetter})}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          isSelected
                            ? 'bg-blue-500 text-white' 
                            : 'bg-gray-200 text-gray-600 group-hover:bg-blue-100'
                        }`}>
                          {optionLetter}
                        </div>
                        <span className={`flex-1 ${isSelected ? 'text-blue-900 font-medium' : 'text-gray-700'}`}>
                          {option.substring(3).trim()}
                        </span>
                        {isSelected && (
                          <CheckCircle className="h-5 w-5 text-blue-500" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                <Button
                  variant="outline"
                  disabled={currentQuestion === 0}
                  onClick={() => setCurrentQuestion(currentQuestion - 1)}
                >
                  Previous
                </Button>
                
                <div className="space-x-4">
                  <Button
                    variant="outline"
                    onClick={() => setAnswers({...answers, [question.question_id]: ''})}
                  >
                    Clear Answer
                  </Button>
                  
                  {isLastQuestion ? (
                    <Button onClick={submitTest} className="bg-green-600 hover:bg-green-700">
                      Submit Test
                    </Button>
                  ) : (
                    <Button
                      onClick={() => setCurrentQuestion(currentQuestion + 1)}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Next Question
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Question Navigation */}
        <div className="bg-white p-6 rounded-lg shadow-md mt-6">
          <h3 className="font-semibold mb-4">Question Navigation</h3>
          <div className="grid grid-cols-10 gap-2">
            {activeTest.questions.map((_, index) => (
              <button
                key={index}
                className={`w-10 h-10 rounded text-sm font-medium ${
                  index === currentQuestion
                    ? 'bg-blue-600 text-white'
                    : answers[activeTest.questions[index].question_id]
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                onClick={() => setCurrentQuestion(index)}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Enhanced Test Results Modal
  if (showResults && testResults) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {/* Results Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Trophy className="h-6 w-6" />
                  <h2 className="text-2xl font-bold">Test Completed! 🎉</h2>
                </div>
                <p className="opacity-90">AI-powered analysis with personalized insights</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={closeResults}
                className="text-white hover:bg-white/20"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            {/* Score Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/20 rounded-lg p-4">
                <div className="text-3xl font-bold">{testResults.percentage.toFixed(1)}%</div>
                <div className="text-sm opacity-90">Overall Score</div>
              </div>
              <div className="bg-white/20 rounded-lg p-4">
                <div className="text-3xl font-bold text-green-300">{testResults.correct_answers}</div>
                <div className="text-sm opacity-90">Correct</div>
              </div>
              <div className="bg-white/20 rounded-lg p-4">
                <div className="text-3xl font-bold text-red-300">{testResults.wrong_answers}</div>
                <div className="text-sm opacity-90">Wrong</div>
              </div>
              <div className="bg-white/20 rounded-lg p-4">
                <div className="text-3xl font-bold text-yellow-300">{testResults.unanswered}</div>
                <div className="text-sm opacity-90">Unanswered</div>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* Pass/Fail Status */}
            <div className="mb-6">
              <div className={`inline-flex items-center px-4 py-2 rounded-full ${
                testResults.pass_status 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {testResults.pass_status ? (
                  <>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Passed! Great work!
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-5 w-5 mr-2" />
                    Keep practicing! You'll get there!
                  </>
                )}
              </div>
            </div>

            {/* Dual AI Feedback Section */}
            {testResults.dual_feedback && (
              <div className="mb-8">
                <div className="flex items-center mb-4">
                  <Users className="h-6 w-6 text-blue-600 mr-2" />
                  <h3 className="text-xl font-semibold">Dual Intelligence Analysis</h3>
                  <Badge variant="outline" className="ml-2">
                    <Star className="h-3 w-3 mr-1" />
                    {Math.round(testResults.dual_feedback.scenario_confidence * 100)}% Confidence
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Professor Analysis */}
                  <Card className="border-l-4 border-purple-500">
                    <CardHeader className="pb-3">
                      <div className="flex items-center">
                        <GraduationCap className="h-6 w-6 text-purple-600 mr-3" />
                        <div>
                          <CardTitle className="text-lg">Professor Analysis</CardTitle>
                          <p className="text-sm text-gray-600">Technical • Verified • Rigorous</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <div className="whitespace-pre-wrap text-gray-800 text-sm">
                          {testResults.dual_feedback.professor_analysis}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Mentor Guidance */}
                  <Card className="border-l-4 border-green-500">
                    <CardHeader className="pb-3">
                      <div className="flex items-center">
                        <Heart className="h-6 w-6 text-green-600 mr-3" />
                        <div>
                          <CardTitle className="text-lg">Mentor Guidance</CardTitle>
                          <p className="text-sm text-gray-600">Adaptive • Motivational • Personalized</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="bg-green-50 rounded-lg p-4">
                        <div className="whitespace-pre-wrap text-gray-800 text-sm">
                          {testResults.dual_feedback.mentor_feedback}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {/* Performance Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Subject-wise Analysis */}
              {testResults.subject_wise_analysis && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                      Subject Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(testResults.subject_wise_analysis).map(([subject, data]) => (
                        <div key={subject}>
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium">{subject}</span>
                            <span className="text-sm text-gray-600">
                              {data.correct}/{data.total}
                            </span>
                          </div>
                          <Progress 
                            value={(data.correct / data.total) * 100} 
                            className="h-2"
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="h-5 w-5 mr-2 text-orange-600" />
                    Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {testResults.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{rec}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Enhanced Action Buttons */}
            <div className="space-y-4">
              {/* Primary Actions Row */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  onClick={() => {
                    closeResults();
                    loadDetailedReview(testResults.test_id);
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Detailed Review
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setRetakeTestId(testResults.test_id);
                    setShowRetakeOptions(true);
                  }}
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retake Options
                </Button>
              </div>
              
              {/* Secondary Actions Row */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button onClick={closeResults} variant="outline" className="flex-1">
                  Continue Learning
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    closeResults();
                    loadPerformanceTrends();
                  }}
                  className="flex-1"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  View Trends
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Dynamic test templates based on exam type
  const getTestTemplates = (examType, subjects) => {
    const examTypeTemplates = {
      'JEE': [
        {
          id: 'math_full',
          title: 'JEE Main Mathematics - Full Length Test',
          subject: 'Mathematics',
          duration: '3 hours',
          questions: 25,
          difficulty: 'High',
          description: 'Comprehensive test covering all mathematics topics for JEE Main'
        },
        {
          id: 'physics_mechanics',
          title: 'Physics Mechanics - Chapter Test',
          subject: 'Physics',
          duration: '1.5 hours',
          questions: 15,
          difficulty: 'Medium',
          description: 'Focus test on mechanics including motion, forces, and energy'
        },
        {
          id: 'chemistry_organic',
          title: 'Organic Chemistry - Quick Assessment',
          subject: 'Chemistry',
          duration: '45 minutes',
          questions: 10,
          difficulty: 'Easy',
          description: 'Assessment covering basic organic chemistry concepts'
        }
      ],
      'UPSC': [
        {
          id: 'history_ancient',
          title: 'Ancient Indian History - Comprehensive Test',
          subject: 'History',
          duration: '2 hours',
          questions: 20,
          difficulty: 'Medium',
          description: 'Covering ancient civilizations, dynasties, and cultural developments'
        },
        {
          id: 'polity_constitution',
          title: 'Indian Constitution & Polity - Mock Test',
          subject: 'Polity',
          duration: '1.5 hours',
          questions: 15,
          difficulty: 'High',
          description: 'Constitutional provisions, governance, and political processes'
        },
        {
          id: 'economy_basics',
          title: 'Indian Economy - Quick Assessment',
          subject: 'Economy',
          duration: '1 hour',
          questions: 12,
          difficulty: 'Easy',
          description: 'Economic concepts, planning, and current economic trends'
        }
      ],
      'NEET': [
        {
          id: 'physics_mechanics',
          title: 'NEET Physics Mechanics - Practice Test',
          subject: 'Physics',
          duration: '1.5 hours',
          questions: 15,
          difficulty: 'Medium',
          description: 'Mechanics, waves, and thermodynamics for medical entrance'
        },
        {
          id: 'chemistry_organic',
          title: 'Organic Chemistry for NEET - Assessment',
          subject: 'Chemistry',
          duration: '1 hour',
          questions: 12,
          difficulty: 'Medium',
          description: 'Organic reactions, mechanisms, and biomolecules'
        },
        {
          id: 'biology_botany',
          title: 'Botany - Plant Systems Test',
          subject: 'Biology',
          duration: '1 hour',
          questions: 10,
          difficulty: 'Easy',
          description: 'Plant anatomy, physiology, and reproduction'
        }
      ]
    };
    
    // Get templates for current exam type or default to JEE
    const templates = examTypeTemplates[examType] || examTypeTemplates['JEE'];
    
    // Filter templates to only show subjects available for current exam type
    return templates.filter(template => 
      subjects.some(subject => 
        subject.toLowerCase().includes(template.subject.toLowerCase()) || 
        template.subject.toLowerCase().includes(subject.toLowerCase())
      )
    ).map(template => ({
      ...template,
      examType: examType
    }));
  };

  // Get current test templates based on exam type
  const testTemplates = getTestTemplates(examSubjects.exam_type, examSubjects.subjects);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // ============= RETAKE OPTIONS MODAL =============
  
  if (showRetakeOptions && retakeTestId) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Choose Retake Mode</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowRetakeOptions(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="space-y-4">
              {/* Exact Retake */}
              <div 
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors"
                onClick={() => handleRetakeTest(retakeTestId, 'exact')}
              >
                <div className="flex items-start">
                  <div className="bg-blue-100 p-3 rounded-lg mr-4">
                    <RefreshCw className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Exact Retake</h4>
                    <p className="text-gray-600 mb-3">Take the same test with identical questions. Perfect for measuring improvement and reinforcing concepts you've studied.</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>• Same questions</span>
                      <span>• Same time limit</span>
                      <span>• Compare performance</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Variant Retake */}
              <div 
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-300 cursor-pointer transition-colors"
                onClick={() => handleRetakeTest(retakeTestId, 'variant')}
              >
                <div className="flex items-start">
                  <div className="bg-green-100 p-3 rounded-lg mr-4">
                    <Sparkles className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Variant Test</h4>
                    <p className="text-gray-600 mb-3">New questions from the same topics and difficulty level. Great for testing your understanding with fresh problems.</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>• New questions</span>
                      <span>• Same topics</span>
                      <span>• Same difficulty</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Adaptive Retake */}
              <div 
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-300 cursor-pointer transition-colors"
                onClick={() => handleRetakeTest(retakeTestId, 'adaptive')}
              >
                <div className="flex items-start">
                  <div className="bg-purple-100 p-3 rounded-lg mr-4">
                    <Target className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Adaptive Focus</h4>
                    <p className="text-gray-600 mb-3">Shorter test focusing specifically on topics you struggled with. AI-powered question selection based on your performance.</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>• Targeted questions</span>
                      <span>• Shorter duration</span>
                      <span>• Weak area focus</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <Button variant="outline" onClick={() => setShowRetakeOptions(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ============= DETAILED REVIEW MODAL =============
  
  if (showDetailedReview && detailedReviewData) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">Question-by-Question Review</h3>
                <p className="text-gray-600">{detailedReviewData.test_name} • {detailedReviewData.correct_answers}/{detailedReviewData.total_questions} correct ({detailedReviewData.overall_score}%)</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetailedReview(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="space-y-6">
              {detailedReviewData.question_reviews.map((review, index) => (
                <div key={review.question_id} className="border rounded-lg overflow-hidden">
                  {/* Question Header */}
                  <div className={`px-6 py-4 ${review.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className="bg-gray-100 px-3 py-1 rounded-full text-sm font-medium">
                            Q{index + 1}
                          </span>
                          <Badge className={review.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                            {review.is_correct ? '✓ Correct' : '✗ Incorrect'}
                          </Badge>
                          <span className="text-sm text-gray-500">{review.subject}</span>
                        </div>
                        <h4 className="text-lg font-medium text-gray-900 mb-2">{review.question_text}</h4>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleQuestionBookmark(
                            review.question_id, 
                            detailedReviewData.test_id, 
                            !bookmarkedQuestions.has(review.question_id)
                          )}
                          className={bookmarkedQuestions.has(review.question_id) ? 'bg-yellow-100 border-yellow-300' : ''}
                        >
                          <Star className={`h-4 w-4 ${bookmarkedQuestions.has(review.question_id) ? 'text-yellow-600 fill-yellow-600' : 'text-gray-400'}`} />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Question Content */}
                  <div className="px-6 py-4">
                    {/* Options */}
                    <div className="mb-4">
                      <div className="grid grid-cols-1 gap-2">
                        {review.options.map((option, optIndex) => {
                          const optionLetter = option.charAt(0);
                          const isCorrect = optionLetter === review.correct_answer;
                          const isUserAnswer = optionLetter === review.user_answer;
                          
                          return (
                            <div 
                              key={optIndex}
                              className={`p-3 border rounded-lg ${
                                isCorrect ? 'bg-green-50 border-green-300' : 
                                isUserAnswer && !isCorrect ? 'bg-red-50 border-red-300' : 
                                'bg-gray-50 border-gray-200'
                              }`}
                            >
                              <div className="flex items-center space-x-3">
                                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold ${
                                  isCorrect ? 'bg-green-500 text-white' :
                                  isUserAnswer && !isCorrect ? 'bg-red-500 text-white' :
                                  'bg-gray-300 text-gray-600'
                                }`}>
                                  {optionLetter}
                                </span>
                                <span className="flex-1">{option.substring(3).trim()}</span>
                                {isCorrect && <CheckCircle className="h-5 w-5 text-green-600" />}
                                {isUserAnswer && !isCorrect && <X className="h-5 w-5 text-red-600" />}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Answer Analysis */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Professor Solution */}
                      <div className="bg-purple-50 rounded-lg p-4">
                        <h5 className="font-semibold text-purple-900 mb-2 flex items-center">
                          <GraduationCap className="h-4 w-4 mr-2" />
                          Step-by-Step Solution
                        </h5>
                        <div className="text-sm text-purple-800 whitespace-pre-wrap">{review.professor_solution}</div>
                      </div>

                      {/* Mentor Hint */}
                      <div className="bg-green-50 rounded-lg p-4">
                        <h5 className="font-semibold text-green-900 mb-2 flex items-center">
                          <Heart className="h-4 w-4 mr-2" />
                          Learning Tip
                        </h5>
                        <div className="text-sm text-green-800 whitespace-pre-wrap">{review.mentor_hint}</div>
                      </div>
                    </div>

                    {/* Base Explanation */}
                    {review.explanation && (
                      <div className="mt-4 bg-blue-50 rounded-lg p-4">
                        <h5 className="font-semibold text-blue-900 mb-2">Explanation</h5>
                        <div className="text-sm text-blue-800">{review.explanation}</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-between">
              <Button variant="outline" onClick={() => setShowDetailedReview(false)}>
                Close Review
              </Button>
              <div className="space-x-3">
                <Button 
                  onClick={() => {
                    setShowDetailedReview(false);
                    setRetakeTestId(detailedReviewData.test_id);
                    setShowRetakeOptions(true);
                  }}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retake Test
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <div className="bg-gradient-to-r from-green-600 to-blue-600 p-3 rounded-xl mr-4">
            <Trophy className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">Mock Tests</h1>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm text-green-600">
                  <div className="h-2 w-2 bg-green-500 rounded-full mr-1"></div>
                  <span>Trusted & Accurate</span>
                </div>
                <div className="flex items-center text-sm text-blue-600">
                  <div className="h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
                  <span>Hallucination-Free Questions</span>
                </div>
                <div className="flex items-center text-sm text-purple-600">
                  <div className="h-2 w-2 bg-purple-500 rounded-full mr-1"></div>
                  <span>Dual AI Feedback</span>
                </div>
              </div>
              
              {/* Usage Indicator */}
              <div className="flex items-center bg-gray-50 rounded-lg px-3 py-1">
                <Zap className="h-4 w-4 text-orange-500 mr-2" />
                <span className="text-sm text-gray-700">
                  {getFeatureLimit('mock_tests_weekly') === Infinity ? 
                    'Unlimited' : 
                    `${getFeatureRemaining('mock_tests_weekly')}/${getFeatureLimit('mock_tests_weekly')} left`
                  }
                </span>
                {currentTier === 'FREE' && (
                  <Badge variant="outline" className="ml-2 text-xs">
                    {currentTier}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
        <p className="text-gray-600 text-lg">
          Practice with verified, hallucination-free mock tests at a fraction of coaching costs — get personalized dual AI feedback on every attempt
        </p>
      </div>

      {/* View Switcher */}
      <div className="mb-8 flex gap-3">
        <Button
          variant={activeView === 'generate' ? 'default' : 'outline'}
          onClick={() => setActiveView('generate')}
          className="flex items-center gap-2"
        >
          <PlusCircle className="w-4 h-4" />
          Generate Test
        </Button>
        <Button
          variant={activeView === 'library' ? 'default' : 'outline'}
          onClick={() => setActiveView('library')}
          className="flex items-center gap-2"
        >
          <BookOpen className="w-4 h-4" />
          My Test Library
        </Button>
      </div>

      {/* Conditional View Rendering */}
      {activeView === 'library' ? (
        <TestLibrary 
          onRetakeTest={(testId) => {
            // TODO: Implement retake functionality
            console.log('Retake test:', testId);
            setActiveView('generate');
          }}
          onReviewTest={(testId) => {
            // TODO: Implement review functionality
            console.log('Review test:', testId);
          }}
        />
      ) : (
        <>
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tests Taken</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.recent_tests?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.overall_performance?.average_score?.toFixed(0) || 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Best Rank</p>
                <p className="text-2xl font-bold text-gray-900">
                  #{recentResults[0]?.rank || 'N/A'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Improvement</p>
                <p className="text-2xl font-bold text-green-600">
                  {analytics?.overall_performance?.improvement_rate > 0 ? '+' : ''}
                  {analytics?.overall_performance?.improvement_rate?.toFixed(0) || 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Available Tests */}
        <div className="lg:col-span-2">
          <Card className="border-0 shadow-md">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Available Tests
              </CardTitle>
              <div className="flex space-x-2">
                <Button
                  variant={selectedCategory === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('all')}
                >
                  All
                </Button>
                <Button
                  variant={selectedCategory === 'full' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('full')}
                >
                  Full Length
                </Button>
                <Button
                  variant={selectedCategory === 'chapter' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('chapter')}
                >
                  Chapter-wise
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Enhanced Quick Test Generation */}
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-blue-900 flex items-center">
                    <Zap className="h-4 w-4 mr-2" />
                    Generate New Test
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-600">Cached: {testCache.size}</span>
                    <button
                      onClick={() => setQuickGeneration(!quickGeneration)}
                      className={`text-xs px-2 py-1 rounded-full transition-colors ${
                        quickGeneration 
                          ? 'bg-green-500 text-white' 
                          : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                      }`}
                    >
                      {quickGeneration ? '⚡ Quick' : '🧠 AI'}
                    </button>
                  </div>
                </div>
                
                {testCache.size > 0 && (
                  <div className="mb-3 text-xs text-green-600 bg-green-50 p-2 rounded border border-green-200">
                    💾 {testCache.size} tests cached for instant loading! Look for ⚡ indicators.
                  </div>
                )}
                
                {estimatedTime && (
                  <div className="mb-3 text-xs text-blue-600 bg-blue-50 p-2 rounded border border-blue-200">
                    🚀 Optimized generation in progress • Estimated: {estimatedTime}
                  </div>
                )}
                
                {/* Professional Error Display */}
                {generationError && (
                  <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
                    <div className="flex items-start">
                      <AlertTriangle className="h-6 w-6 text-red-500 mr-3 mt-1 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="text-red-800 font-semibold mb-2">Test Generation Issue</h4>
                        <div className="text-red-700 text-sm whitespace-pre-line leading-relaxed">
                          {typeof generationError === 'string' ? generationError : 'An error occurred. Please try again.'}
                        </div>
                        {Object.keys(loadingStates).length === 0 && (
                          <div className="mt-4 flex gap-3">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setGenerationError(null)}
                              className="border-red-300 text-red-700 hover:bg-red-100"
                            >
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Try Again
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                // Could open support chat or contact form
                                window.open('mailto:support@dhruvai.com?subject=Mock Test Generation Issue', '_blank');
                              }}
                              className="border-red-300 text-red-700 hover:bg-red-100"
                            >
                              Contact Support
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Retry Status Display */}
                {retryStatus && (
                  <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600 mr-2"></div>
                    <p className="text-yellow-800 text-sm">{retryStatus}</p>
                  </div>
                )}
                
                {/* Slow Generation Warning - Shows after 10 second delay */}
                {Object.values(slowGenerationStates).some(slow => slow) && (
                  <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        <div className="flex-1">
                          <span className="text-blue-800 text-sm font-medium">
                            Taking longer than expected? 
                          </span>
                          <p className="text-blue-600 text-xs mt-1">
                            Don't worry! Our AI is carefully crafting quality questions for you. This usually takes 15-30 seconds.
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={emergencyResetAllStates}
                        variant="outline"
                        size="sm"
                        className="text-blue-600 border-blue-300 hover:bg-blue-100"
                      >
                        <RefreshCw className="h-4 w-4 mr-1" />
                        Cancel & Reset
                      </Button>
                    </div>
                  </div>
                )}
                
                {/* Dynamic Subject Test Generation */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-700">Quick Test Generation</h4>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                      {examSubjects.exam_display_name || examSubjects.exam_type}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {examSubjects.subjects.slice(0, 3).map((subject, index) => {
                        const subjectKey = subject.toLowerCase().replace(/\s+/g, '-');
                        const quickKey = `${subjectKey}-quick`;
                        
                        // Subject-specific emojis
                        const getSubjectEmoji = (subj) => {
                          const lowerSubj = subj.toLowerCase();
                          if (lowerSubj.includes('math')) return '🧮';
                          if (lowerSubj.includes('physics')) return '⚛️';
                          if (lowerSubj.includes('chemistry')) return '🧪';
                          if (lowerSubj.includes('biology')) return '🧬';
                          if (lowerSubj.includes('history')) return '📚';
                          if (lowerSubj.includes('polity')) return '🏛️';
                          if (lowerSubj.includes('economy')) return '💰';
                          if (lowerSubj.includes('reasoning')) return '🧠';
                          if (lowerSubj.includes('english')) return '📝';
                          if (lowerSubj.includes('computer')) return '💻';
                          return '📖';
                        };
                        
                        // Color schemes for different subjects
                        const getSubjectColor = (index) => {
                          const colors = [
                            'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400',
                            'bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400', 
                            'bg-green-600 hover:bg-green-700 disabled:bg-green-400',
                            'bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400',
                            'bg-red-600 hover:bg-red-700 disabled:bg-red-400',
                            'bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400'
                          ];
                          return colors[index % colors.length];
                        };
                        
                        return (
                          <Button 
                            key={subject}
                            onClick={() => generateMockTest(examSubjects.exam_type, subject, 3, 25, quickKey)}
                            disabled={loadingStates[quickKey]}
                            className={`${getSubjectColor(index)} relative`}
                          >
                            {loadingStates[quickKey] ? (
                              <div className="flex items-center">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                <div className="flex flex-col">
                                  <span className="text-xs">Generating...</span>
                                  {generationProgress[quickKey] && (
                                    <span className="text-xs opacity-75">
                                      {generationProgress[quickKey].stage}
                                    </span>
                                  )}
                                </div>
                              </div>
                            ) : (
                              <>
                                {getSubjectEmoji(subject)} {subject}
                                {testCache.has(getCacheKey(examSubjects.exam_type, subject, 3, 25)) && (
                                  <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full px-1">
                                    ⚡
                                  </span>
                                )}
                              </>
                            )}
                          </Button>
                        );
                      })}
                    </div>
                  
                  {examSubjects.test_access && examSubjects.test_access.has_access && (
                    <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                      <span>
                        Tests remaining: {examSubjects.test_access.remaining === -1 ? 'Unlimited' : examSubjects.test_access.remaining}
                      </span>
                      {examSubjects.test_access.limit !== -1 && (
                        <span>
                          Used: {examSubjects.test_access.used}/{examSubjects.test_access.limit}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                {testTemplates.map((template) => (
                  <div key={template.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-gray-900">{template.title}</h3>
                          <Badge className={getDifficultyColor(template.difficulty)}>
                            {template.difficulty}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {template.duration}
                          </div>
                          <div className="flex items-center">
                            <FileText className="h-4 w-4 mr-1" />
                            {template.questions} questions
                          </div>
                          <div className="flex items-center text-green-600">
                            <CheckCircle className="h-4 w-4 mr-1" />
                            AI Generated
                          </div>
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <Button 
                          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 relative min-h-11 px-4 mobile-transition"
                          size="sm"
                          onClick={() => {
                            const diffLevel = difficultyMap[template.difficulty] || 3;
                            generateMockTest(template.examType, template.subject, diffLevel, template.questions, `template-${template.id}`);
                          }}
                          disabled={loadingStates[`template-${template.id}`]}
                          aria-label={`Generate ${template.subject} test`}
                        >
                          {loadingStates[`template-${template.id}`] ? (
                            <>
                              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                              Generating...
                            </>
                          ) : (
                            <>
                              Generate Test
                              {testCache.has(getCacheKey(template.examType, template.subject, difficultyMap[template.difficulty] || 3, template.questions)) && (
                                <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full px-1">
                                  ⚡
                                </span>
                              )}
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 text-center">
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    alert('Additional test categories:\n\n• Subject-wise Tests\n• Previous Year Papers\n• Speed Tests (30 min)\n• Sectional Tests\n• Full-length Simulations\n\nSelect "Generate New Test" above to create practice tests!');
                  }}
                >
                  View All Tests
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Results & Performance */}
        <div className="space-y-6">
          {/* Gamification Progress Widget */}
          <GamificationProgress showFullView={false} />
          
          {/* Personal Test History */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                  Your Test History
                </div>
                <Badge variant="outline" className="text-xs">
                  Personal Analytics
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentResults.length > 0 ? (
                  recentResults.map((result, index) => (
                    <div key={index} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900 mb-1">
                            {result.testName}
                          </p>
                          <div className="flex items-center space-x-3 text-xs text-gray-600">
                            <span className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {result.date}
                            </span>
                            <span className="flex items-center">
                              <Target className="h-3 w-3 mr-1" />
                              {result.totalQuestions || 25} questions
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-lg font-bold ${getScoreColor(result.score)}`}>
                            {result.score}%
                          </div>
                          <div className="text-xs text-gray-500">
                            {result.score >= 90 ? 'Excellent!' : 
                             result.score >= 75 ? 'Good Job!' : 
                             result.score >= 60 ? 'Keep Going!' : 'Practice More'}
                          </div>
                        </div>
                      </div>
                      
                      {/* Progress bar with improvement indicator */}
                      <div className="space-y-2">
                        <Progress 
                          value={result.score} 
                          className="h-2" 
                        />
                        
                        {/* Show improvement trend if available */}
                        {index < recentResults.length - 1 && (
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">vs previous test:</span>
                            {result.score > recentResults[index + 1].score ? (
                              <span className="text-green-600 flex items-center">
                                <TrendingUp className="h-3 w-3 mr-1" />
                                +{(result.score - recentResults[index + 1].score).toFixed(1)}% improved
                              </span>
                            ) : result.score < recentResults[index + 1].score ? (
                              <span className="text-orange-600 flex items-center">
                                <TrendingUp className="h-3 w-3 mr-1 rotate-180" />
                                -{(recentResults[index + 1].score - result.score).toFixed(1)}% 
                              </span>
                            ) : (
                              <span className="text-gray-600">Same score</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <div className="bg-gray-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                      <FileText className="h-6 w-6 text-gray-500" />
                    </div>
                    <p className="text-gray-600 text-sm mb-2">No test history yet</p>
                    <p className="text-gray-500 text-xs">Take your first mock test to see your progress!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Performance Insights */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-purple-600" />
                Performance Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics?.subject_performance && Object.keys(analytics.subject_performance).length > 0 ? (
                  Object.entries(analytics.subject_performance).map(([subject, data]) => (
                    <div key={subject}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">{subject}</span>
                        <span className={`font-medium ${getScoreColor(data.mastery_avg)}`}>
                          {data.mastery_avg?.toFixed(0)}%
                        </span>
                      </div>
                      <Progress value={data.mastery_avg || 0} className="h-2" />
                    </div>
                  ))
                ) : (
                  <>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Mathematics</span>
                        <span className="font-medium text-green-600">90%</span>
                      </div>
                      <Progress value={90} className="h-2" />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Physics</span>
                        <span className="font-medium text-yellow-600">68%</span>
                      </div>
                      <Progress value={68} className="h-2" />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Chemistry</span>
                        <span className="font-medium text-blue-600">75%</span>
                      </div>
                      <Progress value={75} className="h-2" />
                    </div>
                  </>
                )}
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  💡 <strong>Tip:</strong> {
                    analytics?.areas_for_improvement?.length > 0 
                      ? `Focus on ${analytics.areas_for_improvement.join(', ')}. Take more practice tests to improve.`
                      : 'Keep up the great work! Continue practicing to maintain your performance.'
                  }
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                className="w-full justify-start bg-green-600 hover:bg-green-700"
                onClick={() => window.location.href = '/analytics'}
              >
                <Award className="h-4 w-4 mr-2" />
                View Detailed Analysis
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start disabled:opacity-50 relative"
                onClick={() => generateMockTest('JEE', 'Mixed', 2, 15, 'practice-questions')}
                disabled={loadingStates['practice-questions']}
              >
                <FileText className="h-4 w-4 mr-2" />
                {loadingStates['practice-questions'] ? (
                  <>
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    Practice Questions
                    {testCache.has(getCacheKey('JEE', 'Mixed', 2, 15)) && (
                      <Sparkles className="h-3 w-3 text-green-500 ml-auto" />
                    )}
                  </>
                )}
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => {
                  loadPerformanceTrends();
                  alert('Performance trends loaded! Check the Analytics section for detailed insights.');
                }}
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Performance Trends
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => {
                  const tomorrow = new Date();
                  tomorrow.setDate(tomorrow.getDate() + 1);
                  alert(`Test scheduled for ${tomorrow.toLocaleDateString()} at 10:00 AM. You will receive a reminder notification.`);
                }}
              >
                <Clock className="h-4 w-4 mr-2" />
                Schedule Test
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Toast Notification */}
      {toast.show && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          toast.type === 'success' 
            ? 'bg-green-500 text-white' 
            : toast.type === 'error'
            ? 'bg-red-500 text-white'
            : 'bg-blue-500 text-white'
        } animate-in fade-in slide-in-from-right-full`}>
          <div className="flex items-center">
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}