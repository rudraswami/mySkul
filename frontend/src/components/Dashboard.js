import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
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
  Circle
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [motivationalContent, setMotivationalContent] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('dhruv_ai_token');
        if (!token) return;

        // Fetch analytics and motivational content in parallel
        const [analyticsResponse, motivationalResponse] = await Promise.all([
          axios.get(`${API}/dashboard/analytics`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/wellness/motivational-content`, {
            headers: { Authorization: `Bearer ${token}` }
          }).catch(() => null) // Don't fail if motivational content fails
        ]);

        setAnalytics(analyticsResponse.data);
        if (motivationalResponse) {
          setMotivationalContent(motivationalResponse.data);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
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
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center">
                <BarChart3 className="h-6 w-6 mr-3" />
                Performance Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl">
                  <div className="text-2xl font-bold text-green-600 mb-1">87%</div>
                  <p className="text-sm text-green-700 font-medium">Mathematics</p>
                  <p className="text-xs text-green-600">Strong 💪</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl">
                  <div className="text-2xl font-bold text-yellow-600 mb-1">72%</div>
                  <p className="text-sm text-yellow-700 font-medium">Physics</p>
                  <p className="text-xs text-yellow-600">Improving 📈</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-red-50 to-red-100 rounded-xl">
                  <div className="text-2xl font-bold text-red-600 mb-1">65%</div>
                  <p className="text-sm text-red-700 font-medium">Chemistry</p>
                  <p className="text-xs text-red-600">Focus needed 🎯</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Right Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center">
                <Zap className="h-6 w-6 mr-3" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <Button 
                className="w-full justify-start bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transition-all duration-300" 
                onClick={() => window.location.href = '/tutor'}
              >
                <Brain className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-semibold">AI Tutoring</div>
                  <div className="text-xs text-blue-100">Get personalized help</div>
                </div>
              </Button>
              
              <Button 
                className="w-full justify-start bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg hover:shadow-xl transition-all duration-300" 
                onClick={() => window.location.href = '/tests'}
              >
                <FileText className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-semibold">Mock Test</div>
                  <div className="text-xs text-green-100">Test your knowledge</div>
                </div>
              </Button>
              
              <Button 
                className="w-full justify-start bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white shadow-lg hover:shadow-xl transition-all duration-300"
                onClick={() => window.location.href = '/notes'}
              >
                <BookMarked className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-semibold">Auto Notes</div>
                  <div className="text-xs text-orange-100">AI-powered notes</div>
                </div>
              </Button>
            </CardContent>
          </Card>

          {/* Today's Goals */}
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Target className="h-6 w-6 mr-3" />
                  Today's Goals
                </div>
                <Badge variant="secondary" className="bg-white/20 text-white">
                  3/5
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                  <div className="flex items-center space-x-3">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <span className="text-sm font-medium text-gray-700">Study for 2 hours</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={75} className="w-16 h-2" />
                    <span className="text-xs text-green-600 font-medium">75%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                  <div className="flex items-center space-x-3">
                    <Circle className="h-5 w-5 text-yellow-600" />
                    <span className="text-sm font-medium text-gray-700">Complete 20 problems</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={45} className="w-16 h-2" />
                    <span className="text-xs text-yellow-600 font-medium">45%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
                  <div className="flex items-center space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="text-sm font-medium text-gray-700">Review Chemistry</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress value={0} className="w-16 h-2" />
                    <span className="text-xs text-red-600 font-medium">0%</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border border-green-200">
                <div className="flex items-center space-x-3">
                  <Trophy className="h-8 w-8 text-yellow-500" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900">Great progress today! 🎉</p>
                    <p className="text-xs text-gray-600">You're 75% towards your daily goal</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Study Insights */}
          <Card className="border-0 shadow-lg bg-gradient-to-br from-indigo-50 to-purple-50">
            <CardHeader>
              <CardTitle className="flex items-center text-indigo-700">
                <Lightbulb className="h-6 w-6 mr-3" />
                Study Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
                  <div className="p-2 bg-blue-100 rounded-full">
                    <Users className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Peak Study Time</p>
                    <p className="text-xs text-gray-600">You're most focused at 9-11 AM</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
                  <div className="p-2 bg-green-100 rounded-full">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Strength Subject</p>
                    <p className="text-xs text-gray-600">Mathematics - 87% accuracy</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
                  <div className="p-2 bg-orange-100 rounded-full">
                    <Target className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Focus Area</p>
                    <p className="text-xs text-gray-600">Chemistry needs attention</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 text-center">
                <p className="text-sm font-semibold text-indigo-700 mb-2">💡 Today's Tip</p>
                <p className="text-sm text-gray-600">
                  {getMotivationalMessage()}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}