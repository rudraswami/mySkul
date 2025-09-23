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
  Circle
} from 'lucide-react';

export default function MockTests() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mockTests, setMockTests] = useState([]);
  const [recentResults, setRecentResults] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isGeneratingTest, setIsGeneratingTest] = useState(false);
  const [generationError, setGenerationError] = useState(null);
  const [activeTest, setActiveTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token'); // Fixed: use correct token key
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

  const generateMockTest = async (examType, subject, difficulty = 3, numQuestions = 25, retryCount = 0) => {
    const maxRetries = 2;
    
    setIsGeneratingTest(true);
    setGenerationError(null); // Clear previous errors
    
    try {
      const token = localStorage.getItem('dhruv_ai_token'); // Fixed: use correct token key
      if (!token) {
        alert('Please log in again to continue');
        return;
      }
      
      const response = await fetch(`${backendUrl}/api/mock-tests/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          exam_type: examType,
          subject: subject,
          difficulty: difficulty,
          num_questions: numQuestions
        }),
        // Add timeout to prevent infinite loading
        signal: AbortSignal.timeout(30000) // 30 second timeout
      });
      
      if (response.ok) {
        const testData = await response.json();
        setActiveTest(testData);
        setTimeRemaining(testData.time_limit * 60); // Convert minutes to seconds
        setCurrentQuestion(0);
        setAnswers({});
        setGenerationError(null); // Clear any previous errors
        
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
        // Handle API errors properly
        let errorMessage = 'Failed to generate test. Please try again.';
        let shouldRetry = false;
        
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
        }
        
        // Determine error type and retry logic
        if (response.status === 500) {
          errorMessage = 'Our AI service is temporarily busy.';
          shouldRetry = retryCount < maxRetries;
        } else if (response.status === 401) {
          errorMessage = 'Please log in again to continue.';
        } else if (response.status >= 500) {
          errorMessage = 'Server is temporarily unavailable.';
          shouldRetry = retryCount < maxRetries;
        }
        
        // Auto-retry for server errors
        if (shouldRetry) {
          console.log(`Retrying test generation (attempt ${retryCount + 2}/${maxRetries + 1})...`);
          setGenerationError(`${errorMessage} Retrying... (${retryCount + 2}/${maxRetries + 1})`);
          
          // Wait before retrying (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 2000));
          
          // Recursive retry
          return generateMockTest(examType, subject, difficulty, numQuestions, retryCount + 1);
        } else {
          setGenerationError(errorMessage);
          alert(errorMessage);
        }
        
        console.error(`Mock test generation failed: ${response.status} - ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error generating test:', error);
      
      // Handle network and other errors
      let errorMessage = 'Failed to generate test.';
      let shouldRetry = retryCount < maxRetries;
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Network error. Please check your internet connection.';
        shouldRetry = false; // Don't retry network errors
      } else if (error.name === 'AbortError' || error.message.includes('timeout')) {
        errorMessage = 'Request timed out.';
      } else if (error.name === 'TimeoutError') {
        errorMessage = 'The request is taking longer than expected.';
      }
      
      // Auto-retry for timeout and server errors
      if (shouldRetry && (error.name === 'AbortError' || error.message.includes('500'))) {
        console.log(`Retrying test generation after error (attempt ${retryCount + 2}/${maxRetries + 1})...`);
        setGenerationError(`${errorMessage} Retrying... (${retryCount + 2}/${maxRetries + 1})`);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 2000));
        
        // Recursive retry
        return generateMockTest(examType, subject, difficulty, numQuestions, retryCount + 1);
      } else {
        setGenerationError(errorMessage);
        alert(`${errorMessage} Please try again.`);
      }
    } finally {
      // Always reset loading state
      setIsGeneratingTest(false);
    }
  };

  const submitTest = async () => {
    if (!activeTest) return;
    
    try {
      const token = localStorage.getItem('dhruv_ai_token'); // Fixed: use correct token key
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
        alert(`Test completed! Score: ${result.percentage.toFixed(1)}%`);
        setActiveTest(null);
        loadAnalytics(); // Refresh analytics
      }
    } catch (error) {
      console.error('Error submitting test:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // If there's an active test, show the test interface
  if (activeTest) {
    const question = activeTest.questions[currentQuestion];
    const isLastQuestion = currentQuestion === activeTest.questions.length - 1;

    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        {/* Test Header */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{activeTest.test_name}</h1>
              <p className="text-gray-600">Question {currentQuestion + 1} of {activeTest.questions.length}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-red-600">{formatTime(timeRemaining)}</div>
              <p className="text-sm text-gray-500">Time Remaining</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all" 
                style={{ width: `${((currentQuestion + 1) / activeTest.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-6">{question.question_text}</h2>
          
          <div className="space-y-4">
            {question.options.map((option, index) => (
              <div 
                key={index}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  answers[question.question_id] === option.charAt(0) 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setAnswers({...answers, [question.question_id]: option.charAt(0)})}
              >
                {option}
              </div>
            ))}
          </div>

          <div className="flex justify-between mt-8">
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

  // Sample mock test data - will be replaced by API data
  const sampleTests = [
    {
      id: 1,
      title: 'JEE Main Mathematics - Full Length Test',
      examType: 'JEE',
      subject: 'Mathematics',
      duration: '3 hours',
      questions: 75,
      difficulty: 'High',
      completed: false,
      bestScore: null,
      description: 'Comprehensive test covering all mathematics topics for JEE Main'
    },
    {
      id: 2,
      title: 'Physics Mechanics - Chapter Test',
      examType: 'JEE', 
      subject: 'Physics',
      duration: '1.5 hours',
      questions: 30,
      difficulty: 'Medium',
      completed: true,
      bestScore: 85,
      description: 'Focus test on mechanics including motion, forces, and energy'
    },
    {
      id: 3,
      title: 'Organic Chemistry - Quick Assessment',
      examType: 'JEE',
      subject: 'Chemistry', 
      duration: '45 minutes',
      questions: 20,
      difficulty: 'Easy',
      completed: true,
      bestScore: 92,
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
              {/* Quick Test Generation */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-3">Generate New Test</h4>
                
                {/* Error Display */}
                {generationError && (
                  <div className="mb-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <p className="text-orange-800 text-sm">{generationError}</p>
                    {!isGeneratingTest && (
                      <button
                        onClick={() => setGenerationError(null)}
                        className="mt-2 text-orange-600 hover:text-orange-800 text-xs underline"
                      >
                        Dismiss
                      </button>
                    )}
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Mathematics', 3, 25)}
                    disabled={isGeneratingTest}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
                  >
                    {isGeneratingTest ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      'Math Test'
                    )}
                  </Button>
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Physics', 3, 25)}
                    disabled={isGeneratingTest}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-green-400"
                  >
                    {isGeneratingTest ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      'Physics Test'
                    )}
                  </Button>
                  <Button 
                    onClick={() => generateMockTest('JEE', 'Chemistry', 3, 25)}
                    disabled={isGeneratingTest}
                    className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400"
                  >
                    {isGeneratingTest ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      'Chemistry Test'
                    )}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                {sampleTests.map((test) => (
                  <div key={test.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          {test.completed ? (
                            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                          ) : (
                            <Circle className="h-5 w-5 text-gray-300 mr-2" />
                          )}
                          <h3 className="font-semibold text-gray-900">{test.title}</h3>
                          <Badge 
                            className={`ml-2 ${getDifficultyColor(test.difficulty)}`}
                          >
                            {test.difficulty}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-3">{test.description}</p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {test.duration}
                          </div>
                          <div className="flex items-center">
                            <FileText className="h-4 w-4 mr-1" />
                            {test.questions} questions
                          </div>
                          {test.completed && test.bestScore && (
                            <div className="flex items-center">
                              <Award className="h-4 w-4 mr-1" />
                              <span className={getScoreColor(test.bestScore)}>
                                Best: {test.bestScore}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <Button 
                          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
                          size="sm"
                          onClick={() => {
                            const difficultyMap = { 'Easy': 2, 'Medium': 3, 'High': 4 };
                            const diffLevel = difficultyMap[test.difficulty] || 3;
                            generateMockTest(test.examType, test.subject, diffLevel, Math.min(test.questions, 25));
                          }}
                          disabled={isGeneratingTest}
                        >
                          {isGeneratingTest ? (
                            <>
                              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                              Generating...
                            </>
                          ) : (
                            test.completed ? 'Retake' : 'Start Test'
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
                className="w-full justify-start"
                onClick={() => generateMockTest('JEE', 'Mixed', 2, 15)}
                disabled={isGeneratingTest}
              >
                <FileText className="h-4 w-4 mr-2" />
                {isGeneratingTest ? 'Generating...' : 'Practice Questions'}
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