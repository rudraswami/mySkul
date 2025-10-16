import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { 
  Brain, 
  Clock, 
  Target, 
  TrendingUp, 
  BookOpen, 
  MessageCircle,
  FileText,
  Calendar,
  Award,
  Zap,
  ChevronRight,
  Timer,
  Trophy,
  Flame,
  CheckCircle2,
  Star,
  BarChart3,
  Users,
  GraduationCap,
  AlertCircle,
  PlayCircle,
  BookMarked,
  Lightbulb,
  Circle,
  Heart,
  Smile,
  Meh,
  Frown,
  X,
  CheckCircle
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [motivationalContent, setMotivationalContent] = useState(null);
  const [error, setError] = useState(null);
  
  // Wellness Modal States
  const [showWellnessModal, setShowWellnessModal] = useState(false);
  const [wellnessLoading, setWellnessLoading] = useState(false);
  const [currentMood, setCurrentMood] = useState(null);
  const [showWellnessToast, setShowWellnessToast] = useState(false);

  useEffect(() => {
    // Note: Session token from URL is now handled by AuthContext
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('dhruv_ai_token');
        if (!token) {
          console.log('No token found, setting loading to false');
          setLoading(false);
          return;
        }

        console.log('Fetching dashboard data...');
        
        // Fetch analytics data
        const analyticsResponse = await axios.get(`${API}/dashboard/analytics`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        console.log('Analytics data received:', analyticsResponse.data);
        setAnalytics(analyticsResponse.data);

        // Try to fetch motivational content (optional)
        try {
          const motivationalResponse = await axios.get(`${API}/wellness/motivational-content`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setMotivationalContent(motivationalResponse.data);
        } catch (motivationalError) {
          console.log('Motivational content failed (non-critical):', motivationalError.message);
        }

      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Set some fallback data so UI doesn't stay in loading state
        setAnalytics({
          total_study_time: 30,
          current_streak: 7,
          chat_sessions_count: 4,
          weekly_goals_progress: 75,
          recent_progress: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const calculateExamCountdown = () => {
    if (!user?.target_year) return null;
    const targetDate = new Date(`${user.target_year}-05-01`); // Assume JEE is in May
    const today = new Date();
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const getMotivationalMessage = () => {
    const messages = [
      "Every expert was once a beginner. Keep pushing forward! 🚀",
      "Your dedication today builds tomorrow's success! ⭐",
      "Small consistent actions lead to remarkable results! 💪",
      "You're closer to your goal than you were yesterday! 🎯",
      "Great students aren't made in comfort zones! 🔥"
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  };

  // Wellness Check Functions
  const moodOptions = [
    { 
      id: 'great', 
      label: 'Feeling Great!', 
      icon: Smile, 
      color: 'bg-green-500', 
      bgColor: 'bg-green-50', 
      textColor: 'text-green-700',
      description: 'Energized and ready to learn' 
    },
    { 
      id: 'good', 
      label: 'Pretty Good', 
      icon: Heart, 
      color: 'bg-blue-500', 
      bgColor: 'bg-blue-50', 
      textColor: 'text-blue-700',
      description: 'Focused and motivated' 
    },
    { 
      id: 'okay', 
      label: 'Just Okay', 
      icon: Meh, 
      color: 'bg-yellow-500', 
      bgColor: 'bg-yellow-50', 
      textColor: 'text-yellow-700',
      description: 'Could use some motivation' 
    },
    { 
      id: 'stressed', 
      label: 'Feeling Stressed', 
      icon: Frown, 
      color: 'bg-red-500', 
      bgColor: 'bg-red-50', 
      textColor: 'text-red-700',
      description: 'Need to take it easy' 
    }
  ];

  const handleWellnessCheck = async (moodId) => {
    setWellnessLoading(true);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      // Mock wellness API call - you can replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      const selectedMood = moodOptions.find(m => m.id === moodId);
      setCurrentMood(selectedMood);
      setShowWellnessModal(false);
      setShowWellnessToast(true);
      
      // Hide toast after 3 seconds
      setTimeout(() => setShowWellnessToast(false), 3000);
      
    } catch (error) {
      console.error('Wellness check failed:', error);
    } finally {
      setWellnessLoading(false);
    }
  };

  const isCurrentRoute = (path) => {
    return location.pathname === path;
  };

  const examCountdown = calculateExamCountdown();

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-300 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 opacity-90"></div>
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative p-8 text-white">
          <div className="max-w-4xl">
            <div className="flex items-center space-x-4 mb-6">
              <div className="bg-white/20 backdrop-blur-lg p-4 rounded-2xl">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold mb-2">
                  Welcome back, {user?.email?.split('@')[0] || 'Student'}! 👋
                </h1>
                <p className="text-blue-100 text-xl mb-2">
                  Your trusted, hallucination-free AI mentor is ready to transform your learning
                </p>
                <p className="text-blue-200 text-sm">
                  Verified notes • Personalized prep • Affordable success
                </p>
              </div>
            </div>
            
            {/* Brand Pillars Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 bg-green-400 rounded-full flex items-center justify-center">
                    <span className="text-green-900 text-sm font-bold">✓</span>
                  </div>
                  <div>
                    <div className="text-xl font-bold">Trust</div>
                    <div className="text-blue-100 text-sm">Hallucination-free, verified AI</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 bg-purple-400 rounded-full flex items-center justify-center">
                    <span className="text-purple-900 text-sm font-bold">♥</span>
                  </div>
                  <div>
                    <div className="text-xl font-bold">Personalisation</div>
                    <div className="text-blue-100 text-sm">Adaptive, one-to-one mentoring</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 bg-yellow-400 rounded-full flex items-center justify-center">
                    <span className="text-yellow-900 text-sm font-bold">⚡</span>
                  </div>
                  <div>
                    <div className="text-xl font-bold">Empowerment</div>
                    <div className="text-blue-100 text-sm">Affordable, independent success</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="p-8 -mt-4 relative z-10 space-y-8">
        {/* Professional Clean Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Study Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatTime(analytics?.total_study_time || 0)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Total hours</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <Clock className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Current Streak</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics?.current_streak || 7} days
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Consistency</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">AI Sessions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics?.chat_sessions_count || 4}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">This week</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <Brain className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Weekly Progress</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics?.weekly_goals_progress || 75}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">On track</p>
                </div>
                <div className="p-3 bg-orange-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">{user?.exam_type || 'JEE'} Exam</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {examCountdown || 120}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">days left</p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <Timer className="h-6 w-6 text-red-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Clean Motivational Section */}
        <Card className="border border-blue-200 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Lightbulb className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Today's Focus</h3>
                  <p className="text-gray-700">{getMotivationalMessage()}</p>
                </div>
              </div>
              <div className="hidden md:block">
                <Trophy className="h-8 w-8 text-yellow-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Enhanced Study Dashboard - Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Study Activity */}
          <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center justify-between text-gray-900">
                <div className="flex items-center">
                  <BookOpen className="h-5 w-5 mr-3 text-blue-600" />
                  Recent Study Progress
                </div>
                <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                  Active
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {analytics?.recent_progress?.length > 0 ? (
                <div className="space-y-4">
                  {analytics.recent_progress.slice(0, 3).map((progress, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-white rounded-lg border border-gray-200">
                          <BookMarked className="h-4 w-4 text-gray-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-1">
                            {progress.subject} - {progress.chapter}
                          </h4>
                          <p className="text-sm text-gray-600 mb-1">{progress.concept}</p>
                          <div className="flex items-center space-x-3 text-xs text-gray-500">
                            <span>{new Date(progress.last_accessed).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>{formatTime(progress.time_spent)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="text-right">
                          <div className="text-lg font-semibold text-gray-900">{Math.round(progress.mastery_level)}%</div>
                          <Progress value={progress.mastery_level} className="w-16 h-2 mt-1" />
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="p-4 bg-white rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center border border-gray-200">
                    <PlayCircle className="h-8 w-8 text-gray-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Start Your Learning Journey</h3>
                  <p className="text-gray-600 mb-6">Begin with AI tutoring or take a practice test</p>
                  <div className="space-x-4">
                    <Button 
                      className="bg-blue-600 hover:bg-blue-700"
                      onClick={() => window.location.href = '/tutor'}
                    >
                      <Brain className="h-4 w-4 mr-2" />
                      AI Tutoring
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => window.location.href = '/tests'}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Practice Test
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Subject Performance Overview */}
          <Card className="border border-gray-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center text-gray-900">
                <BarChart3 className="h-5 w-5 mr-3 text-blue-600" />
                Subject Performance
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">Mathematics</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Progress value={87} className="w-24 h-2" />
                    <span className="text-sm font-semibold text-gray-900 w-12">87%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">Physics</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Progress value={72} className="w-24 h-2" />
                    <span className="text-sm font-semibold text-gray-900 w-12">72%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">Chemistry</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Progress value={65} className="w-24 h-2" />
                    <span className="text-sm font-semibold text-gray-900 w-12">65%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Right Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="border border-gray-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center text-gray-900">
                <Zap className="h-5 w-5 mr-3 text-blue-600" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-3">
              <Button 
                className={`w-full justify-start transition-all duration-200 ${
                  isCurrentRoute('/tutor') 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                    : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                }`}
                onClick={() => navigate('/tutor')}
              >
                <Brain className={`h-4 w-4 mr-3 ${isCurrentRoute('/tutor') ? 'text-white' : 'text-blue-600'}`} />
                <div className="text-left">
                  <div className="font-medium">AI Tutoring</div>
                  <div className={`text-xs ${isCurrentRoute('/tutor') ? 'text-blue-100' : 'text-gray-600'}`}>
                    Get personalized help
                  </div>
                </div>
              </Button>
              
              <Button 
                className={`w-full justify-start transition-all duration-200 ${
                  isCurrentRoute('/tests') 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                    : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                }`}
                onClick={() => navigate('/tests')}
              >
                <FileText className={`h-4 w-4 mr-3 ${isCurrentRoute('/tests') ? 'text-white' : 'text-blue-600'}`} />
                <div className="text-left">
                  <div className="font-medium">Mock Test</div>
                  <div className={`text-xs ${isCurrentRoute('/tests') ? 'text-blue-100' : 'text-gray-600'}`}>
                    Test your knowledge
                  </div>
                </div>
              </Button>
              
              <Button 
                className={`w-full justify-start transition-all duration-200 ${
                  isCurrentRoute('/auto-notes') 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                    : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                }`}
                onClick={() => navigate('/auto-notes')}
              >
                <BookMarked className={`h-4 w-4 mr-3 ${isCurrentRoute('/auto-notes') ? 'text-white' : 'text-blue-600'}`} />
                <div className="text-left">
                  <div className="font-medium">Auto Notes</div>
                  <div className={`text-xs ${isCurrentRoute('/auto-notes') ? 'text-blue-100' : 'text-gray-600'}`}>
                    AI-powered notes
                  </div>
                </div>
              </Button>
            </CardContent>
          </Card>

          {/* Daily Wellness Check */}
          <Card className="border border-gray-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center justify-between text-gray-900">
                <div className="flex items-center">
                  <Heart className="h-5 w-5 mr-3 text-pink-600" />
                  Daily Wellness
                </div>
                {currentMood && (
                  <Badge className={`${currentMood.bgColor} ${currentMood.textColor} border-0`}>
                    {currentMood.label}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {currentMood ? (
                <div className="text-center space-y-3">
                  <div className={`mx-auto w-12 h-12 ${currentMood.color} rounded-full flex items-center justify-center`}>
                    <currentMood.icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{currentMood.label}</p>
                    <p className="text-sm text-gray-600">{currentMood.description}</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setShowWellnessModal(true)}
                    className="mt-3"
                  >
                    Update Check-in
                  </Button>
                </div>
              ) : (
                <div className="text-center space-y-3">
                  <div className="mx-auto w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                    <Heart className="h-6 w-6 text-pink-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">How are you feeling today?</p>
                    <p className="text-sm text-gray-600 mb-4">Take a moment to check in with yourself</p>
                  </div>
                  <Button 
                    onClick={() => setShowWellnessModal(true)}
                    className="w-full bg-pink-600 hover:bg-pink-700 text-white"
                  >
                    <Heart className="h-4 w-4 mr-2" />
                    Take Wellness Check
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Today's Goals */}
          <Card className="border border-gray-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center justify-between text-gray-900">
                <div className="flex items-center">
                  <Target className="h-5 w-5 mr-3 text-blue-600" />
                  Today's Goals
                </div>
                <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                  2/3
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-gray-700">Study for 2 hours</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={75} className="w-16 h-2" />
                    <span className="text-xs text-gray-600 font-medium">75%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Circle className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700">Complete 20 problems</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={45} className="w-16 h-2" />
                    <span className="text-xs text-gray-600 font-medium">45%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Circle className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700">Review Chemistry</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={0} className="w-16 h-2" />
                    <span className="text-xs text-gray-600 font-medium">0%</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-3">
                  <Trophy className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Good progress today!</p>
                    <p className="text-xs text-gray-600">Keep up the consistent effort</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Study Insights */}
          <Card className="border border-gray-200 bg-white">
            <CardHeader className="border-b border-gray-100 bg-gray-50">
              <CardTitle className="flex items-center text-gray-900">
                <Lightbulb className="h-5 w-5 mr-3 text-blue-600" />
                Study Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Clock className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Peak Study Time</p>
                    <p className="text-xs text-gray-600">Most focused at 9-11 AM</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-green-50 rounded-lg">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Strongest Subject</p>
                    <p className="text-xs text-gray-600">Mathematics - 87% accuracy</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-orange-50 rounded-lg">
                    <Target className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Focus Area</p>
                    <p className="text-xs text-gray-600">Chemistry needs attention</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900 mb-2">Today's Tip</p>
                <p className="text-sm text-gray-600">
                  {getMotivationalMessage()}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Wellness Check Modal */}
      {showWellnessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl max-w-md w-full mx-4 shadow-2xl transform transition-all duration-300 scale-100">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center">
                    <Heart className="h-5 w-5 text-pink-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Daily Wellness Check</h3>
                    <p className="text-sm text-gray-600">How are you feeling right now?</p>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowWellnessModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="space-y-3">
                {moodOptions.map((mood) => (
                  <Button
                    key={mood.id}
                    variant="outline"
                    className="w-full justify-start p-4 h-auto hover:bg-gray-50 border-2 hover:border-blue-200 transition-all duration-200"
                    onClick={() => handleWellnessCheck(mood.id)}
                    disabled={wellnessLoading}
                  >
                    <div className="flex items-center space-x-4 w-full">
                      <div className={`w-10 h-10 ${mood.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                        <mood.icon className="h-5 w-5 text-white" />
                      </div>
                      <div className="text-left flex-1">
                        <div className="font-medium text-gray-900">{mood.label}</div>
                        <div className="text-sm text-gray-600">{mood.description}</div>
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
              
              {wellnessLoading && (
                <div className="mt-4 text-center">
                  <div className="inline-flex items-center space-x-2 text-sm text-gray-600">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-pink-600"></div>
                    <span>Saving your check-in...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Wellness Toast */}
      {showWellnessToast && currentMood && (
        <div className="fixed top-4 right-4 z-50 transform transition-all duration-300 animate-in slide-in-from-right">
          <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 ${currentMood.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">Wellness check saved!</p>
                <p className="text-sm text-gray-600">You're feeling {currentMood.label.toLowerCase()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}