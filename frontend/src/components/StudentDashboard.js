import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Brain, 
  BookOpen, 
  Target, 
  Trophy, 
  Clock, 
  TrendingUp,
  Calendar,
  Users,
  Star,
  ChevronRight,
  Play,
  BookMarked,
  FileText,
  MessageCircle,
  BarChart3,
  Zap,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowUp,
  ArrowDown,
  Timer,
  Heart,
  Flame,
  Smile,
  Meh,
  Frown,
  X
} from 'lucide-react';

// Import backend URL
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function StudentDashboard() {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [todayGoals, setTodayGoals] = useState([
    { id: 1, text: 'Study for 120 minutes total', progress: 75, target: 120 },
    { id: 2, text: 'Ask AI Tutor for help with doubts', progress: 30, target: 100 }
  ]);
  
  // Dynamic Focus Engine States
  const [dailyFocusPlan, setDailyFocusPlan] = useState(null);
  const [focusLoading, setFocusLoading] = useState(true);
  const [celebrationModal, setCelebrationModal] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [userMood, setUserMood] = useState('neutral');
  
  // Wellness Modal States
  const [showWellnessModal, setShowWellnessModal] = useState(false);
  const [wellnessLoading, setWellnessLoading] = useState(false);
  const [currentMood, setCurrentMood] = useState(null);
  const [showWellnessToast, setShowWellnessToast] = useState(false);
  
  // Dynamic Ranking System States
  const [leaderboard, setLeaderboard] = useState([]);
  const [userRank, setUserRank] = useState(5);
  const [totalUsers, setTotalUsers] = useState(20);
  const [rankingUpdating, setRankingUpdating] = useState(false);
  
  // AI Insights Widget States
  const [aiInsights, setAiInsights] = useState(null);
  const [insightsLoading, setInsightsLoading] = useState(true);
  
  // Recent Notes Preview States
  const [recentNotes, setRecentNotes] = useState(null);
  const [notesLoading, setNotesLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    initializeRanking();
    loadDailyFocusPlan();
    loadAiInsights();
    loadRecentNotes();
    
    // Set up auto-refresh for rankings every 12 seconds
    const rankingInterval = setInterval(() => {
      updateRankings();
    }, 12000);
    
    return () => clearInterval(rankingInterval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/dashboard/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Set some demo data if API fails
      setDashboardData({
        study_time_today: "0h 30m",
        total_sessions: 6,
        current_streak: 7,
        weekly_progress: 75,
        recent_subjects: [
          { name: "Mathematics", progress: 75, topic: "Quadratic Equations" },
          { name: "Physics", progress: 60, topic: "Newton's Laws" },
          { name: "Chemistry", progress: 45, topic: "Chemical Bonding" }
        ]
      });
    } finally {
      setLoading(false);
    }
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
      description: 'Energized and ready to learn',
      emoji: '😊'
    },
    { 
      id: 'good', 
      label: 'Pretty Good', 
      icon: Heart, 
      color: 'bg-blue-500', 
      bgColor: 'bg-blue-50', 
      textColor: 'text-blue-700',
      description: 'Focused and motivated',
      emoji: '😌'
    },
    { 
      id: 'okay', 
      label: 'Just Okay', 
      icon: Meh, 
      color: 'bg-yellow-500', 
      bgColor: 'bg-yellow-50', 
      textColor: 'text-yellow-700',
      description: 'Could use some motivation',
      emoji: '😐'
    },
    { 
      id: 'stressed', 
      label: 'Feeling Stressed', 
      icon: Frown, 
      color: 'bg-red-500', 
      bgColor: 'bg-red-50', 
      textColor: 'text-red-700',
      description: 'Need to take it easy',
      emoji: '😟'
    }
  ];

  const handleWellnessCheck = async (moodId) => {
    setWellnessLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
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

  // Dynamic Ranking System Functions
  const dummyNames = [
    'Arjun Sharma', 'Priya Patel', 'Rohit Kumar', 'Sneha Singh', 'Vikram Joshi',
    'Ananya Gupta', 'Karan Mehta', 'Isha Verma', 'Aditya Rao', 'Riya Agarwal',
    'Nikhil Bansal', 'Pooja Reddy', 'Harsh Malhotra', 'Divya Nair', 'Siddharth Shah',
    'Kavya Iyer', 'Rahul Saxena', 'Meera Jain', 'Aryan Khanna', 'Tanya Sood'
  ];

  const generateInitialRanking = () => {
    const ranking = [];
    const usedNames = new Set();
    
    // User's position (will be at rank 5 initially)
    const userProgress = 78; // User's current progress percentage
    
    // Generate competitors around user's rank
    for (let i = 1; i <= totalUsers; i++) {
      if (i === userRank) {
        // User's entry
        ranking.push({
          id: 'user',
          name: user?.full_name || 'You',
          progress: userProgress,
          rank: i,
          isUser: true,
          change: 0
        });
      } else {
        // Generate dummy competitor
        let name;
        do {
          name = dummyNames[Math.floor(Math.random() * dummyNames.length)];
        } while (usedNames.has(name));
        usedNames.add(name);

        // Progress based on rank (higher ranks have higher progress)
        let baseProgress;
        if (i < userRank) {
          baseProgress = userProgress + (userRank - i) * (2 + Math.random() * 3);
        } else {
          baseProgress = userProgress - (i - userRank) * (1 + Math.random() * 2);
        }
        
        const progress = Math.min(Math.max(baseProgress + (Math.random() - 0.5) * 10, 30), 95);
        
        ranking.push({
          id: `dummy-${i}`,
          name: name,
          progress: Math.round(progress),
          rank: i,
          isUser: false,
          change: 0
        });
      }
    }
    
    return ranking.sort((a, b) => b.progress - a.progress);
  };

  const initializeRanking = () => {
    const initialRanking = generateInitialRanking();
    setLeaderboard(initialRanking);
  };

  const updateRankings = () => {
    setRankingUpdating(true);
    
    setTimeout(() => {
      setLeaderboard(prevLeaderboard => {
        return prevLeaderboard.map(entry => {
          if (entry.isUser) {
            // User progress can change slightly based on recent activity
            const newProgress = Math.min(Math.max(entry.progress + (Math.random() - 0.4) * 2, 40), 98);
            return { ...entry, progress: Math.round(newProgress) };
          } else {
            // Dummy users have more dynamic changes
            const changeAmount = (Math.random() - 0.5) * 4; // -2 to +2 change
            const newProgress = Math.min(Math.max(entry.progress + changeAmount, 25), 95);
            const change = newProgress > entry.progress ? 1 : newProgress < entry.progress ? -1 : 0;
            
            return { 
              ...entry, 
              progress: Math.round(newProgress),
              change: change
            };
          }
        }).sort((a, b) => b.progress - a.progress).map((entry, index) => ({
          ...entry,
          rank: index + 1
        }));
      });
      
      setRankingUpdating(false);
    }, 800); // Short delay for smooth animation
  };

  // Get visible ranks (user's rank ± 2 positions)
  const getVisibleRanks = () => {
    const userEntry = leaderboard.find(entry => entry.isUser);
    if (!userEntry) return leaderboard.slice(0, 5);
    
    const userPosition = userEntry.rank;
    const start = Math.max(0, userPosition - 3);
    const end = Math.min(leaderboard.length, userPosition + 2);
    
    return leaderboard.slice(start, end);
  };
  // Dynamic Focus Engine Functions
  const loadDailyFocusPlan = async () => {
    try {
      setFocusLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/focusEngine/generate`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const plan = await response.json();
        setDailyFocusPlan(plan);
      } else {
        console.error('Failed to load focus plan');
      }
    } catch (error) {
      console.error('Focus plan loading error:', error);
    } finally {
      setFocusLoading(false);
    }
  };

  const regenerateFocusPlan = async () => {
    try {
      setRegenerating(true);
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(
        `${BACKEND_URL}/api/focusEngine/generate?regenerate=true&mood=${userMood}`, 
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const plan = await response.json();
        setDailyFocusPlan(plan);
      }
    } catch (error) {
      console.error('Focus plan regeneration error:', error);
    } finally {
      setRegenerating(false);
    }
  };

  const completeTask = async (taskId) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/focusEngine/complete-task`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task_id: taskId })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update local state
        setDailyFocusPlan(prev => {
          const updatedTasks = prev.tasks.map(task =>
            task.task_id === taskId
              ? { ...task, completed: true, progress: 100 }
              : task
          );
          return { ...prev, tasks: updatedTasks };
        });

        // Show celebration if all tasks completed
        if (result.celebration_triggered) {
          setCelebrationModal(true);
          setTimeout(() => setCelebrationModal(false), 3000);
        }

        return result;
      }
    } catch (error) {
      console.error('Task completion error:', error);
    }
  };

  const calculateOverallProgress = () => {
    if (!dailyFocusPlan?.tasks) return 0;
    const completedTasks = dailyFocusPlan.tasks.filter(task => task.completed).length;
    return Math.round((completedTasks / dailyFocusPlan.tasks.length) * 100);
  };

  const getTotalEarnedXP = () => {
    if (!dailyFocusPlan?.tasks) return 0;
    return dailyFocusPlan.tasks
      .filter(task => task.completed)
      .reduce((sum, task) => sum + task.completion_xp, 0);
  };

  if (loading) {
    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="bg-gray-200 rounded-lg h-48 w-full"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-gray-200 rounded-lg h-32"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="bg-white bg-opacity-20 p-3 rounded-xl mr-4">
                <Brain className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
                </h1>
                <p className="text-blue-100 text-lg">
                  ⭐ You studied more than 70% of learners this week!
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Badge className="bg-green-500 text-white border-0">Trust</Badge>
              <Badge className="bg-purple-500 text-white border-0">Personalized</Badge>
              <Badge className="bg-yellow-500 text-white border-0">Empowerment</Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* AI-Driven Today's Focus */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-blue-600" />
                  AI-Powered Today's Focus
                  {dailyFocusPlan?.adaptation_reason && (
                    <Badge variant="outline" className="ml-2 text-xs">
                      AI Adapted
                    </Badge>
                  )}
                </CardTitle>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-500">
                    {calculateOverallProgress()}%
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={regenerateFocusPlan}
                    disabled={regenerating}
                    className="text-xs"
                  >
                    {regenerating ? <div className="animate-spin h-3 w-3 border border-blue-500 border-t-transparent rounded-full"></div> : <Zap className="h-3 w-3" />}
                    {regenerating ? 'Regenerating...' : 'Regenerate'}
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Mood Selector */}
                <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">How are you feeling today?</span>
                  <div className="flex space-x-1">
                    {[
                      { mood: 'energetic', icon: Smile, label: 'Great!', color: 'text-green-600' },
                      { mood: 'neutral', icon: Meh, label: 'OK', color: 'text-blue-600' },
                      { mood: 'low', icon: Frown, label: 'Tired', color: 'text-orange-600' }
                    ].map(({ mood, icon: Icon, label, color }) => (
                      <Button
                        key={mood}
                        variant={userMood === mood ? "default" : "ghost"}
                        size="sm"
                        onClick={() => setUserMood(mood)}
                        className={`px-2 py-1 ${userMood === mood ? 'bg-blue-600 text-white' : color}`}
                      >
                        <Icon className="h-4 w-4 mr-1" />
                        {label}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* AI Adaptation Message */}
                {dailyFocusPlan?.adaptation_reason && (
                  <div className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                    <div className="flex items-start space-x-2">
                      <Brain className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-blue-900">AI Insight</p>
                        <p className="text-xs text-blue-700 mt-1">{dailyFocusPlan.adaptation_reason}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Task List */}
                {focusLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map(i => (
                      <div key={i} className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-2 bg-gray-200 rounded w-full"></div>
                      </div>
                    ))}
                  </div>
                ) : dailyFocusPlan?.tasks ? (
                  <div className="space-y-4">
                    {dailyFocusPlan.tasks.map((task, index) => {
                      const priorityColors = {
                        high: 'border-red-200 bg-red-50',
                        medium: 'border-yellow-200 bg-yellow-50',
                        low: 'border-green-200 bg-green-50'
                      };
                      const priorityTextColors = {
                        high: 'text-red-700',
                        medium: 'text-yellow-700',
                        low: 'text-green-700'
                      };

                      return (
                        <div
                          key={task.task_id}
                          className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                            task.completed 
                              ? 'border-green-300 bg-green-50' 
                              : priorityColors[task.priority]
                          } ${task.completed ? 'opacity-75' : 'hover:shadow-md'}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-start space-x-3 flex-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => !task.completed && completeTask(task.task_id)}
                                disabled={task.completed}
                                className={`p-0 h-6 w-6 rounded-full ${
                                  task.completed 
                                    ? 'bg-green-500 text-white' 
                                    : 'border-2 border-gray-300 hover:border-blue-500'
                                }`}
                              >
                                {task.completed && <CheckCircle className="h-4 w-4" />}
                              </Button>
                              
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-1">
                                  <h4 className={`font-medium text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                    {task.title}
                                  </h4>
                                  <Badge 
                                    variant="outline" 
                                    className={`text-xs px-2 py-0 ${priorityTextColors[task.priority]}`}
                                  >
                                    {task.priority}
                                  </Badge>
                                </div>
                                
                                <p className="text-xs text-gray-600 mb-2">{task.description}</p>
                                
                                <div className="flex items-center space-x-4 text-xs text-gray-500">
                                  <div className="flex items-center">
                                    <Clock className="h-3 w-3 mr-1" />
                                    <span>{task.estimated_time} mins</span>
                                  </div>
                                  <div className="flex items-center">
                                    <BookOpen className="h-3 w-3 mr-1" />
                                    <span className="font-medium">{task.subject}</span>
                                  </div>
                                  <div className="flex items-center">
                                    <Star className="h-3 w-3 mr-1 text-yellow-500" />
                                    <span>{task.completion_xp} XP</span>
                                  </div>
                                </div>
                                
                                {/* Progress Bar */}
                                <div className="mt-2">
                                  <Progress 
                                    value={task.completed ? 100 : task.progress} 
                                    className="h-2"
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <Brain className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm">Loading your personalized focus plan...</p>
                  </div>
                )}

                {/* Focus Plan Summary */}
                {dailyFocusPlan && (
                  <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-lg font-bold text-green-600">{getTotalEarnedXP()}</div>
                        <div className="text-xs text-gray-600">XP Earned</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-blue-600">
                          {dailyFocusPlan.tasks?.filter(t => t.completed).length || 0}/{dailyFocusPlan.tasks?.length || 0}
                        </div>
                        <div className="text-xs text-gray-600">Tasks Done</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-indigo-600">
                          {Math.round((dailyFocusPlan.tasks?.filter(t => t.completed).reduce((sum, t) => sum + t.estimated_time, 0) || 0))}m
                        </div>
                        <div className="text-xs text-gray-600">Time Studied</div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Performance Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-blue-600">0h 30m</div>
                  <p className="text-sm text-gray-600">of 2h goal</p>
                  <div className="mt-2">
                    <Clock className="h-4 w-4 inline text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-yellow-600">7 🔥</div>
                  <p className="text-sm text-gray-600">days consistent</p>
                  <div className="mt-2">
                    <Trophy className="h-4 w-4 inline text-yellow-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-green-600">75%</div>
                  <p className="text-sm text-gray-600">vs target</p>
                  <div className="mt-2">
                    <TrendingUp className="h-4 w-4 inline text-green-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-purple-600">14</div>
                  <p className="text-sm text-gray-600">this week</p>
                  <div className="mt-2">
                    <Brain className="h-4 w-4 inline text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Study Progress */}
            <Card className="border border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Subject & Chapter Progress</h3>
                    <p className="text-sm text-gray-600">Track your learning across different topics</p>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-blue-100">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                      <div>
                        <div className="font-semibold text-gray-900">Mathematics</div>
                        <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                          1/15 chapters
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">0%</div>
                      <div className="text-sm text-gray-500">mastery</div>
                    </div>
                  </div>
                  
                  <div className="text-center py-8">
                    <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Ready to boost your learning?</p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <Button 
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700"
                        onClick={() => window.location.href = '/tutor'}
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        Revise Notes
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.location.href = '/tutor'}
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Ask Tutor
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Today's Learning Path */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-purple-600" />
                  Today's Learning Path
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                      1
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">Quick Warm-up</div>
                      <div className="text-sm text-gray-600">Review yesterday's concepts</div>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      5 mins
                    </Badge>
                  </div>
                  
                  <div className="flex items-center p-3 bg-gray-50 rounded-lg opacity-60">
                    <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                      2
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">New Chapter Introduction</div>
                      <div className="text-sm text-gray-600">Mathematics • Quadratic Equations</div>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      15 mins
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-5 w-5 mr-2 text-blue-600" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className={`w-full justify-start h-12 transition-all duration-200 ${
                    isCurrentRoute('/tutor') 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                      : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                  }`}
                  onClick={() => navigate('/tutor')}
                >
                  <MessageCircle className={`h-5 w-5 mr-3 ${isCurrentRoute('/tutor') ? 'text-white' : 'text-blue-600'}`} />
                  <div className="text-left">
                    <div className="font-semibold">Solve Doubts</div>
                    <div className={`text-xs ${isCurrentRoute('/tutor') ? 'text-blue-100' : 'text-gray-600'}`}>
                      Get instant AI help
                    </div>
                  </div>
                </Button>
                
                <Button 
                  className={`w-full justify-start h-12 transition-all duration-200 ${
                    isCurrentRoute('/tests') 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                      : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                  }`}
                  onClick={() => navigate('/tests')}
                >
                  <Trophy className={`h-5 w-5 mr-3 ${isCurrentRoute('/tests') ? 'text-white' : 'text-blue-600'}`} />
                  <div className="text-left">
                    <div className="font-semibold">Practice Tests</div>
                    <div className={`text-xs ${isCurrentRoute('/tests') ? 'text-blue-100' : 'text-gray-600'}`}>
                      Test your knowledge
                    </div>
                  </div>
                </Button>
                
                <Button 
                  className={`w-full justify-start h-12 transition-all duration-200 ${
                    isCurrentRoute('/auto-notes') 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                      : 'bg-white hover:bg-blue-50 text-gray-900 border border-gray-300'
                  }`}
                  onClick={() => navigate('/auto-notes')}
                >
                  <BookMarked className={`h-5 w-5 mr-3 ${isCurrentRoute('/auto-notes') ? 'text-white' : 'text-blue-600'}`} />
                  <div className="text-left">
                    <div className="font-semibold">Generate Notes</div>
                    <div className={`text-xs ${isCurrentRoute('/auto-notes') ? 'text-blue-100' : 'text-gray-600'}`}>
                      AI-powered notes
                    </div>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* Wellness Check */}
            <Card className="border border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-purple-800">
                  <div className="flex items-center">
                    <Heart className="h-5 w-5 mr-2" />
                    Wellness Check
                  </div>
                  {currentMood && (
                    <Badge className={`${currentMood.bgColor} ${currentMood.textColor} border-0`}>
                      {currentMood.label}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {currentMood ? (
                  <div className="text-center py-4">
                    <div className="text-2xl mb-2">{currentMood.emoji}</div>
                    <p className="text-purple-700 font-medium mb-2">{currentMood.label}</p>
                    <p className="text-sm text-purple-600 mb-4">{currentMood.description}</p>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="border-purple-300 text-purple-700 hover:bg-purple-100"
                      onClick={() => setShowWellnessModal(true)}
                    >
                      Update Check-in
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-2xl mb-2">💝</div>
                    <p className="text-purple-700 font-medium mb-2">How are you feeling today?</p>
                    <p className="text-sm text-purple-600 mb-4">
                      Take a moment to check in with yourself
                    </p>
                    <Button 
                      size="sm" 
                      className="bg-purple-600 hover:bg-purple-700 text-white"
                      onClick={() => setShowWellnessModal(true)}
                    >
                      Take Wellness Check
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Dynamic Practice Leaderboard */}
            <Card className="border border-yellow-200 bg-gradient-to-br from-yellow-50 to-orange-50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-yellow-800">
                  <div className="flex items-center">
                    <Trophy className="h-5 w-5 mr-2 text-yellow-600" />
                    Practice Leaderboard
                  </div>
                  <div className="flex items-center space-x-1">
                    {rankingUpdating && (
                      <div className="w-3 h-3 bg-yellow-600 rounded-full animate-pulse"></div>
                    )}
                    <Badge className="bg-yellow-100 text-yellow-700 border-0 text-xs">
                      Live
                    </Badge>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {leaderboard.length > 0 && (
                  <>
                    {/* User's Overall Rank Display */}
                    <div className="bg-white rounded-lg p-3 border-2 border-yellow-300 mb-4">
                      <div className="text-center">
                        <div className="text-lg font-bold text-yellow-700">
                          You're Rank #{leaderboard.find(entry => entry.isUser)?.rank || userRank}
                        </div>
                        <div className="text-sm text-yellow-600">
                          of {totalUsers} students
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          {leaderboard.find(entry => entry.isUser)?.progress || 78}% overall progress
                        </div>
                      </div>
                    </div>

                    {/* Nearby Ranks */}
                    <div className="space-y-2">
                      {getVisibleRanks().map((entry, index) => {
                        const isUser = entry.isUser;
                        const rankChange = entry.change;
                        
                        return (
                          <div
                            key={entry.id}
                            className={`flex items-center justify-between p-3 rounded-lg transition-all duration-500 ${
                              isUser 
                                ? 'bg-blue-100 border-2 border-blue-300 shadow-md' 
                                : 'bg-white border border-gray-200 hover:bg-gray-50'
                            }`}
                          >
                            <div className="flex items-center space-x-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                                entry.rank === 1 ? 'bg-yellow-500 text-white' :
                                entry.rank === 2 ? 'bg-gray-400 text-white' :
                                entry.rank === 3 ? 'bg-orange-500 text-white' :
                                isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                              }`}>
                                #{entry.rank}
                              </div>
                              <div className="flex-1">
                                <div className={`font-medium ${isUser ? 'text-blue-900' : 'text-gray-900'}`}>
                                  {isUser ? `${entry.name} (You)` : entry.name}
                                </div>
                                <div className="flex items-center space-x-2 mt-1">
                                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                                    <div 
                                      className={`h-2 rounded-full transition-all duration-1000 ease-out ${
                                        isUser ? 'bg-blue-500' : 'bg-green-500'
                                      }`}
                                      style={{ width: `${entry.progress}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-xs font-medium text-gray-600 w-10">
                                    {entry.progress}%
                                  </span>
                                </div>
                              </div>
                              {rankChange !== 0 && (
                                <div className={`text-xs flex items-center ${
                                  rankChange > 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {rankChange > 0 ? (
                                    <ArrowUp className="h-3 w-3" />
                                  ) : (
                                    <ArrowDown className="h-3 w-3" />
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Motivational Messages */}
                    <div className="mt-4 p-3 bg-white rounded-lg border border-yellow-200">
                      <div className="text-center">
                        {(() => {
                          const userEntry = leaderboard.find(entry => entry.isUser);
                          const userRankPosition = userEntry?.rank || userRank;
                          
                          if (userRankPosition === 1) {
                            return (
                              <div>
                                <div className="text-sm font-medium text-yellow-700 mb-1">🏆 Amazing!</div>
                                <div className="text-xs text-gray-600">You're leading the pack! Keep it up!</div>
                              </div>
                            );
                          } else if (userRankPosition <= 3) {
                            return (
                              <div>
                                <div className="text-sm font-medium text-orange-700 mb-1">🔥 So close!</div>
                                <div className="text-xs text-gray-600">You're in the top 3! Push for #1!</div>
                              </div>
                            );
                          } else if (userRankPosition <= 5) {
                            return (
                              <div>
                                <div className="text-sm font-medium text-blue-700 mb-1">💪 Great progress!</div>
                                <div className="text-xs text-gray-600">You're in the top 5! Keep studying!</div>
                              </div>
                            );
                          } else {
                            return (
                              <div>
                                <div className="text-sm font-medium text-purple-700 mb-1">⭐ Keep going!</div>
                                <div className="text-xs text-gray-600">Every practice session moves you up!</div>
                              </div>
                            );
                          }
                        })()}
                      </div>
                    </div>

                    <div className="text-center pt-2">
                      <div className="text-xs text-gray-500">
                        🤖 Practice data • Updates every 12 seconds
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-green-600" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                      <span>Completed Math practice</span>
                    </div>
                    <span className="text-gray-500">2h ago</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      <span>Asked AI Tutor query</span>
                    </div>
                    <span className="text-gray-500">4h ago</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Wellness Check Modal */}
      {showWellnessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl max-w-md w-full mx-4 shadow-2xl transform transition-all duration-300 scale-100">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <Heart className="h-5 w-5 text-purple-600" />
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
                    className="w-full justify-start p-4 h-auto hover:bg-gray-50 border-2 hover:border-purple-200 transition-all duration-200"
                    onClick={() => handleWellnessCheck(mood.id)}
                    disabled={wellnessLoading}
                  >
                    <div className="flex items-center space-x-4 w-full">
                      <div className="text-2xl">{mood.emoji}</div>
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
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
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
              <div className="text-2xl">{currentMood.emoji}</div>
              <div>
                <p className="font-medium text-gray-900">Wellness check saved!</p>
                <p className="text-sm text-gray-600">You're feeling {currentMood.label.toLowerCase()}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Celebration Modal */}
      {celebrationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center">
            <div className="mb-4">
              <div className="w-20 h-20 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full mx-auto flex items-center justify-center mb-4 animate-bounce">
                <Trophy className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">🎉 All Tasks Complete!</h3>
              <p className="text-gray-600 mb-6">
                Incredible work! You've completed all your focus tasks for today. 
                Your dedication is building unstoppable learning momentum!
              </p>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-blue-600">{getTotalEarnedXP()}</div>
                  <div className="text-sm text-blue-700">XP Earned</div>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-600">
                    {dailyFocusPlan?.tasks?.filter(t => t.completed).length || 0}
                  </div>
                  <div className="text-sm text-green-700">Tasks Completed</div>
                </div>
              </div>
              
              <Button
                onClick={() => setCelebrationModal(false)}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200"
              >
                Continue Learning! 🚀
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}