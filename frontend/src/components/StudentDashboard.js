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
  Circle,
  Smile,
  Meh,
  Frown,
  Plus,
  ArrowRight,
  TrendingUpIcon
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function StudentDashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [todayGoals, setTodayGoals] = useState([]);
  const [goalsLoading, setGoalsLoading] = useState(true);
  const [subjectProgress, setSubjectProgress] = useState([]);
  const [subjectsLoading, setSubjectsLoading] = useState(true);
  const [moodRating, setMoodRating] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Performance optimization: Set minimal loading time
  useEffect(() => {
    const timer = setTimeout(() => {
      if (loading) setLoading(false);
    }, 2000); // Max 2 seconds loading
    return () => clearTimeout(timer);
  }, [loading]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        // Set demo data immediately for better UX
        setAnalytics({
          total_study_time: 45,
          current_streak: 7,
          chat_sessions_count: 12,
          weekly_goals_progress: 78,
          recent_progress: []
        });
        setLoading(false);
        return;
      }

      // Set timeout for API call
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const analyticsResponse = await axios.get(`${API}/dashboard/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      setAnalytics(analyticsResponse.data);
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('API call timed out, using fallback data');
      } else {
        console.error('Failed to fetch dashboard data:', error);
      }
      
      // Always set fallback data for good UX
      setAnalytics({
        total_study_time: 45,
        current_streak: 7,
        chat_sessions_count: 12,
        weekly_goals_progress: 78,
        recent_progress: []
      });
    } finally {
      setLoading(false);
    }
  };

  const getStudentName = () => {
    if (user?.email) {
      return user.email.split('@')[0].charAt(0).toUpperCase() + user.email.split('@')[0].slice(1);
    }
    return 'Student';
  };

  const calculateExamCountdown = () => {
    if (!user?.target_year) return 200; // Default fallback
    const targetDate = new Date(`${user.target_year}-05-01`);
    const today = new Date();
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 200;
  };

  const getProgressMotivation = () => {
    const progress = analytics?.weekly_goals_progress || 78;
    if (progress >= 90) return `🔥 You're ${progress - 75}% ahead of your weekly goal!`;
    if (progress >= 75) return `⭐ You studied more than 70% of learners this week!`;
    return `💪 You're on track! ${progress}% of weekly goal completed.`;
  };

  const getTodayProgress = () => {
    const completed = todayGoals.filter(goal => goal.completed).length;
    return Math.round((completed / todayGoals.length) * 100);
  };

  const handleGoalToggle = (goalId) => {
    setTodayGoals(goals => 
      goals.map(goal => 
        goal.id === goalId ? { ...goal, completed: !goal.completed } : goal
      )
    );
  };

  const handleMoodSubmit = (mood) => {
    setMoodRating(mood);
    // In real app, this would send to analytics API
  };

  const examCountdown = calculateExamCountdown();
  const todayProgress = getTodayProgress();

  if (loading) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-8 bg-gray-300 rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="h-24 bg-gray-300 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header / Welcome Zone */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-white/20 backdrop-blur-lg p-3 rounded-xl">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Welcome back, {getStudentName()}! 👋</h1>
                <p className="text-blue-100 text-lg mt-1">{getProgressMotivation()}</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Badge className="bg-green-500 text-white px-3 py-1">✅ Trust</Badge>
              <Badge className="bg-purple-500 text-white px-3 py-1">🔄 Personalized</Badge>
              <Badge className="bg-yellow-500 text-white px-3 py-1">💡 Empowerment</Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Today's Focus (Mini-Plan) */}
        <Card className="border-2 border-blue-200 bg-blue-50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-blue-600" />
                Today's Focus
              </div>
              <div className="flex items-center space-x-2">
                <Progress value={todayProgress} className="w-24 h-2" />
                <span className="text-sm font-semibold">{todayProgress}%</span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3">
              {todayGoals.map((goal) => (
                <div key={goal.id} 
                     className={`flex items-center justify-between p-3 rounded-lg border-2 cursor-pointer transition-all
                       ${goal.completed 
                         ? 'bg-green-50 border-green-200' 
                         : 'bg-white border-gray-200 hover:border-blue-300'}`}
                     onClick={() => handleGoalToggle(goal.id)}
                >
                  <div className="flex items-center space-x-3">
                    {goal.completed ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <Circle className="h-5 w-5 text-gray-400" />
                    )}
                    <div>
                      <span className={`font-medium ${goal.completed ? 'line-through text-gray-600' : 'text-gray-900'}`}>
                        {goal.task}
                      </span>
                      <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                        <Clock className="h-3 w-3" />
                        <span>{goal.duration}</span>
                        <Badge variant="outline" className="text-xs">{goal.subject}</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Progress Snapshot */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Study Time Today</p>
                  <p className="text-xl font-bold text-gray-900">
                    {Math.floor((analytics?.total_study_time || 45) / 60)}h {(analytics?.total_study_time || 45) % 60}m
                  </p>
                  <p className="text-xs text-gray-500">of 2h goal</p>
                </div>
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Clock className="h-5 w-5 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Study Streak</p>
                  <div className="flex items-center space-x-1">
                    <p className="text-xl font-bold text-gray-900">{analytics?.current_streak || 7}</p>
                    <Flame className="h-4 w-4 text-orange-500" />
                  </div>
                  <p className="text-xs text-gray-500">days consistent</p>
                </div>
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Trophy className="h-5 w-5 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Weekly Progress</p>
                  <p className="text-xl font-bold text-gray-900">{analytics?.weekly_goals_progress || 78}%</p>
                  <p className="text-xs text-gray-500">vs target</p>
                </div>
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Doubts Resolved</p>
                  <p className="text-xl font-bold text-gray-900">{analytics?.chat_sessions_count || 12}</p>
                  <p className="text-xs text-gray-500">this week</p>
                </div>
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Brain className="h-5 w-5 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Exam Countdown</p>
                  <p className="text-xl font-bold text-gray-900">{examCountdown}</p>
                  <p className="text-xs text-gray-500">days to {user?.exam_type || 'JEE'}</p>
                </div>
                <div className="p-2 bg-red-100 rounded-lg">
                  <Timer className="h-5 w-5 text-red-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Subject & Chapter Progress */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border border-gray-200">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BookOpen className="h-5 w-5 mr-2 text-blue-600" />
                  Subject & Chapter Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {subjectProgress.map((subject, index) => (
                    <div key={index} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${
                            subject.status === 'strong' ? 'bg-green-500' :
                            subject.status === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <h4 className="font-semibold text-gray-900">{subject.subject}</h4>
                          <Badge variant="outline" className="text-xs">
                            {subject.completed}/{subject.chapters} chapters
                          </Badge>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-gray-900">{subject.mastery}%</div>
                          <div className="text-xs text-gray-500">mastery</div>
                        </div>
                      </div>
                      <Progress value={subject.mastery} className="h-2 mb-3" />
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="text-xs">
                          <BookMarked className="h-3 w-3 mr-1" />
                          Revise Notes
                        </Button>
                        <Button size="sm" variant="outline" className="text-xs">
                          <Brain className="h-3 w-3 mr-1" />
                          Ask Tutor
                        </Button>
                        <Button size="sm" variant="outline" className="text-xs">
                          <FileText className="h-3 w-3 mr-1" />
                          Practice Quiz
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="border border-gray-200">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-5 w-5 mr-2 text-blue-600" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full justify-start bg-blue-600 hover:bg-blue-700 text-white h-12"
                  onClick={() => window.location.href = '/ai-tutor'}
                >
                  <Brain className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Solve Doubts</div>
                    <div className="text-xs text-blue-100">Get instant AI help</div>
                  </div>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start h-12 hover:bg-gray-50"
                  onClick={() => window.location.href = '/mock-tests'}
                >
                  <FileText className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Practice Tests</div>
                    <div className="text-xs text-gray-600">Test your knowledge</div>
                  </div>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start h-12 hover:bg-gray-50"
                  onClick={() => window.location.href = '/auto-note-mentor'}
                >
                  <BookMarked className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Generate Notes</div>
                    <div className="text-xs text-gray-600">AI-powered notes</div>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* Wellness Widget */}
            <Card className="border border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="text-purple-900">How are you feeling today?</CardTitle>
              </CardHeader>
              <CardContent>
                {!moodRating ? (
                  <div className="space-y-4">
                    <div className="flex justify-center space-x-4">
                      <button 
                        onClick={() => handleMoodSubmit('happy')}
                        className="p-3 rounded-full hover:bg-purple-100 transition-colors"
                      >
                        <Smile className="h-8 w-8 text-green-600" />
                      </button>
                      <button 
                        onClick={() => handleMoodSubmit('neutral')}
                        className="p-3 rounded-full hover:bg-purple-100 transition-colors"
                      >
                        <Meh className="h-8 w-8 text-yellow-600" />
                      </button>
                      <button 
                        onClick={() => handleMoodSubmit('stressed')}
                        className="p-3 rounded-full hover:bg-purple-100 transition-colors"
                      >
                        <Frown className="h-8 w-8 text-red-600" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="p-3 bg-purple-100 rounded-lg mb-3">
                      <p className="text-sm text-purple-900">
                        {moodRating === 'happy' && "Great! Keep that positive energy! 🌟"}
                        {moodRating === 'neutral' && "That's okay. Try a 5-minute breathing exercise 🧘‍♂️"}
                        {moodRating === 'stressed' && "Take a break! Try some deep breathing exercises 🌸"}
                      </p>
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => setMoodRating(null)}
                      className="text-xs"
                    >
                      Update Mood
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Achievements */}
            <Card className="border border-yellow-200 bg-yellow-50">
              <CardHeader>
                <CardTitle className="flex items-center text-yellow-900">
                  <Trophy className="h-5 w-5 mr-2" />
                  Achievements
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-3 p-2 bg-yellow-100 rounded-lg">
                  <Flame className="h-5 w-5 text-orange-600" />
                  <div>
                    <div className="font-semibold text-yellow-900">7 Day Streak!</div>
                    <div className="text-xs text-yellow-700">Consistency Champion</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-2 bg-yellow-100 rounded-lg">
                  <Star className="h-5 w-5 text-yellow-600" />
                  <div>
                    <div className="font-semibold text-yellow-900">Math Mastery</div>
                    <div className="text-xs text-yellow-700">87% in Mathematics</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-medium text-gray-900">Today's Reflection</p>
                  <p className="text-sm text-gray-600">What did you find most challenging today?</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {user?.subscription_plan === 'free' && (
            <Card className="border border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Star className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-900">Unlock Pro Features</p>
                      <p className="text-sm text-blue-700">Unlimited doubts + advanced analytics</p>
                    </div>
                  </div>
                  <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                    Upgrade
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}