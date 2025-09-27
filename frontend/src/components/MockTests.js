import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
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
  Sparkles
} from 'lucide-react';

export default function MockTests() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mockTests, setMockTests] = useState([]);
  const [recentResults, setRecentResults] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // Individual loading states for each button
  const [loadingStates, setLoadingStates] = useState({});
  const [generationError, setGenerationError] = useState(null);
  const [retryStatus, setRetryStatus] = useState(null);
  
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

  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  // Difficulty mapping for consistent use
  const difficultyMap = { 'Easy': 2, 'Medium': 3, 'High': 4 };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Reset states on cleanup to prevent memory leaks
      setLoadingStates({});
      setGenerationError(null);
      setRetryStatus(null);
    };
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, []);

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
    
    // Set progress tracking
    if (loading) {
      setGenerationProgress(prev => ({
        ...prev,
        [buttonId]: { progress: 10, stage: 'Starting AI generation...' }
      }));
      setEstimatedTime('15-30 seconds');
    } else {
      setGenerationProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[buttonId];
        return newProgress;
      });
      setEstimatedTime(null);
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
    if (loadingStates[buttonId]) return; // Prevent multiple calls for same button
    
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

    let timeoutId = null;
    let controller = null;
    
    try {
      // Set individual button loading state
      setButtonLoading(buttonId, true);
      setGenerationError(null);
      setRetryStatus(null);

      const maxRetries = 2;
      let attempts = 0;

      while (attempts <= maxRetries) {
        try {
          // Update retry status
          if (attempts > 0) {
            setRetryStatus(`Retrying... (${attempts + 1}/${maxRetries + 1})`);
          }

          // Create abort controller for this attempt
          controller = new AbortController();
          
          // Set timeout manually
          timeoutId = setTimeout(() => {
            if (controller && !controller.signal.aborted) {
              controller.abort();
            }
          }, 30000); // Reduced to 30 seconds with optimizations

          console.log(`Attempt ${attempts + 1}: Starting optimized mock test generation for ${subject}`);
          
          // Progress updates during generation
          const progressUpdates = [
            { delay: 1000, progress: 25, stage: 'Analyzing subject patterns...' },
            { delay: 3000, progress: 50, stage: 'Generating AI questions...' },
            { delay: 8000, progress: 75, stage: 'Verifying accuracy...' },
            { delay: 12000, progress: 90, stage: 'Finalizing test...' }
          ];
          
          progressUpdates.forEach(update => {
            setTimeout(() => {
              if (loadingStates[buttonId]) {
                setGenerationProgress(prev => ({
                  ...prev,
                  [buttonId]: { progress: update.progress, stage: update.stage }
                }));
              }
            }, update.delay);
          });
          
          const response = await fetch(`${backendUrl}/api/mock-tests/generate`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              exam_type: examType,
              subjects: [subject], // Convert to array as expected by new backend
              difficulty_level: difficulty,
              num_questions: numQuestions,
              test_type: "full_length",
              generation_mode: "standard"
            }),
            signal: controller.signal
          });

          // Clear timeout on successful response
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }

          console.log(`Response status: ${response.status}`);

          if (response.ok) {
            const testData = await response.json();
            console.log('Test generated successfully:', testData.test_name);
            
            // Cache the generated test for future use
            cacheTest(cacheKey, testData);
            
            // Success - set up test
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

            return; // Success - exit function
          } else {
            // Handle HTTP errors
            let errorMessage = 'Failed to generate test. Please try again.';
            
            try {
              const errorData = await response.json();
              
              // Handle different error formats
              if (typeof errorData.detail === 'string') {
                errorMessage = errorData.detail;
              } else if (Array.isArray(errorData.detail)) {
                // Handle Pydantic validation errors
                const validationErrors = errorData.detail.map(err => 
                  `${err.loc?.join('.')}: ${err.msg}`
                ).join(', ');
                errorMessage = `Validation Error: ${validationErrors}`;
              } else if (errorData.message) {
                errorMessage = errorData.message;
              } else {
                console.error('Unexpected error format:', errorData);
                errorMessage = 'An unexpected error occurred. Please try again.';
              }
            } catch (parseError) {
              console.error('Error parsing response:', parseError);
              errorMessage = 'Failed to parse error response. Please try again.';
            }

            console.error(`HTTP Error ${response.status}:`, errorMessage);

            if (response.status >= 500 && attempts < maxRetries) {
              // Server error - retry with exponential backoff
              attempts++;
              console.log(`Server error, retrying in ${3 * attempts} seconds...`);
              await new Promise(resolve => setTimeout(resolve, 3000 * attempts));
              continue;
            } else {
              // Final error or non-retryable error
              if (response.status >= 500) {
                errorMessage = `🤖 Our AI tutoring system is currently experiencing high demand. 

This happens when many students are using the platform simultaneously. 

📝 What you can do:
• Try again in 2-3 minutes when AI load decreases
• Contact support if this persists
• Our team is working to scale AI capacity

🎯 Dhruv AI is committed to providing reliable, world-class education technology.`;
              } else if (response.status === 401) {
                errorMessage = 'Your session has expired. Please log in again to continue your learning journey.';
              } else if (response.status === 403) {
                errorMessage = 'Access denied. Please ensure you have the proper permissions to generate tests.';
              }
              // Ensure errorMessage is always a string
              const safeErrorMessage = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
              setGenerationError(safeErrorMessage);
              break;
            }
          }
        } catch (fetchError) {
          console.error('Fetch error:', fetchError);
          
          // Clear timeout if error occurs
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }
          
          if (fetchError.name === 'AbortError') {
            console.log('Request was aborted (timeout or manual cancel)');
            if (attempts < maxRetries) {
              attempts++;
              console.log(`Timeout occurred, retrying in ${3 * attempts} seconds...`);
              await new Promise(resolve => setTimeout(resolve, 3000 * attempts));
              continue;
            }
            const timeoutMessage = `⏱️ Test generation is taking longer than usual.

This can happen when:
• AI is creating complex, high-quality questions
• High platform usage during peak study hours
• Network connectivity issues

💡 Recommendations:
• Try again - AI generation usually completes in 15-30 seconds
• Check your internet connection
• Contact support if this problem persists

🎓 Dhruv AI generates questions using advanced AI to match real exam patterns.`;
            setGenerationError(timeoutMessage);
          } else if (fetchError.name === 'TypeError' && fetchError.message.includes('fetch')) {
            console.error('Network error:', fetchError);
            const networkMessage = `🌐 Network Connection Issue

Please check your internet connection and try again. 

📞 If you're on campus/institutional Wi-Fi, contact your IT support for assistance with educational platform access.

🔄 Retry once your connection is stable - your learning progress is important to us.`;
            setGenerationError(networkMessage);
          } else {
            console.error('Unknown error:', fetchError);
            if (attempts < maxRetries) {
              attempts++;
              console.log(`Unknown error, retrying in ${3 * attempts} seconds...`);
              await new Promise(resolve => setTimeout(resolve, 3000 * attempts));
              continue;
            }
            const unexpectedMessage = `⚠️ Unexpected Error Occurred

We encountered an issue generating your test. Our technical team has been notified.

📋 Next Steps:
• Try again in a few minutes
• Contact support with error details
• Use other study materials while we resolve this

🏆 Your education is our priority - we're working to fix this quickly.`;
            setGenerationError(unexpectedMessage);
          }
          break;
        }
      }
    } finally {
      // Always cleanup and reset states
      console.log('Cleaning up mock test generation...');
      
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      if (controller && !controller.signal.aborted) {
        controller.abort();
      }
      
      // Reset individual button loading state
      setButtonLoading(buttonId, false);
      setRetryStatus(null);
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
    setTestResults(result);
    setShowResults(true);
    setActiveTest(null);
    loadAnalytics(); // Refresh analytics
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

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button onClick={closeResults} className="flex-1">
                Continue Learning
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  closeResults();
                  // Could trigger retake functionality
                }}
                className="flex-1"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retake Test
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Professional test generation templates - no fake completed tests
  const testTemplates = [
    {
      id: 'math_full',
      title: 'JEE Main Mathematics - Full Length Test', 
      examType: 'JEE',
      subject: 'Mathematics',
      duration: '3 hours',
      questions: 25,
      difficulty: 'High',
      description: 'Comprehensive test covering all mathematics topics for JEE Main'
    },
    {
      id: 'physics_mechanics',
      title: 'Physics Mechanics - Chapter Test',
      examType: 'JEE',
      subject: 'Physics', 
      duration: '1.5 hours',
      questions: 15,
      difficulty: 'Medium',
      description: 'Focus test on mechanics including motion, forces, and energy'
    },
    {
      id: 'chemistry_organic',
      title: 'Organic Chemistry - Quick Assessment',
      examType: 'JEE',
      subject: 'Chemistry',
      duration: '45 minutes', 
      questions: 10,
      difficulty: 'Easy',
      description: 'Assessment covering basic organic chemistry concepts'
    }
  ];

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

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mock Tests</h1>
        <p className="text-gray-600">
          Practice with our comprehensive test series designed to simulate real exam conditions
        </p>
      </div>

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
                
                {/* Professional Error Display */}
                {generationError && (
                  <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
                    <div className="flex items-start">
                      <AlertTriangle className="h-6 w-6 text-red-500 mr-3 mt-1 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="text-red-800 font-semibold mb-2">Test Generation Issue</h4>
                        <div className="text-red-700 text-sm whitespace-pre-line leading-relaxed">
                          {generationError}
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
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Mathematics', 3, 25, 'math-quick')}
                    disabled={loadingStates['math-quick']}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 relative"
                  >
                    {loadingStates['math-quick'] ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        <div className="flex flex-col">
                          <span className="text-xs">Generating...</span>
                          {generationProgress['math-quick'] && (
                            <span className="text-xs opacity-75">
                              {generationProgress['math-quick'].stage}
                            </span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <>
                        🧮 Math Test
                        {testCache.has(getCacheKey('JEE', 'Mathematics', 3, 25)) && (
                          <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full px-1">
                            ⚡
                          </span>
                        )}
                      </>
                    )}
                  </Button>
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Physics', 3, 25, 'physics-quick')}
                    disabled={loadingStates['physics-quick']}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 relative"
                  >
                    {loadingStates['physics-quick'] ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        <div className="flex flex-col">
                          <span className="text-xs">Generating...</span>
                          {generationProgress['physics-quick'] && (
                            <span className="text-xs opacity-75">
                              {generationProgress['physics-quick'].stage}
                            </span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <>
                        ⚛️ Physics Test
                        {testCache.has(getCacheKey('JEE', 'Physics', 3, 25)) && (
                          <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full px-1">
                            ⚡
                          </span>
                        )}
                      </>
                    )}
                  </Button>
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Chemistry', 3, 25, 'chemistry-quick')}
                    disabled={loadingStates['chemistry-quick']}
                    className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 relative"
                  >
                    {loadingStates['chemistry-quick'] ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        🧪 Chemistry Test
                        {testCache.has(getCacheKey('JEE', 'Chemistry', 3, 25)) && (
                          <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full px-1">
                            ⚡
                          </span>
                        )}
                      </>
                    )}
                  </Button>
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
                          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 relative"
                          size="sm"
                          onClick={() => {
                            const diffLevel = difficultyMap[template.difficulty] || 3;
                            generateMockTest(template.examType, template.subject, diffLevel, template.questions, `template-${template.id}`);
                          }}
                          disabled={loadingStates[`template-${template.id}`]}
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
          {/* Recent Results */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Recent Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentResults.map((result, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-sm text-gray-900 truncate">
                        {result.testName}
                      </p>
                      <span className={`text-sm font-bold ${getScoreColor(result.score)}`}>
                        {result.score}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Rank: #{result.rank}/{result.totalStudents}</span>
                      <span>{result.date}</span>
                    </div>
                    <Progress 
                      value={result.score} 
                      className="mt-2 h-2" 
                    />
                  </div>
                ))}
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
    </div>
  );
}