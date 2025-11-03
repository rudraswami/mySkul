import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, 
  Sparkles, 
  TrendingUp,
  Target,
  MessageCircle,
  Calendar,
  Eye,
  EyeOff,
  Sun,
  Moon,
  Trophy
} from 'lucide-react';

// Import premium components
import QuickActionsToolbar from './QuickActionsToolbar';
import StreakHeatmap from './StreakHeatmap';
import AchievementBadges from './AchievementBadges';
import AIMentorChat from './AIMentorChat';
import RadialProgress from './RadialProgress';
import FocusMode from './FocusMode';
import SmartRecommendations from './SmartRecommendations';
import MoodTracker from './MoodTracker';
import LiveLeaderboard from './LiveLeaderboard';
import UsageMeter from '../UsageMeter';
import PlanBadge from '../PlanBadge';

// Import premium styles
import '../../styles/premium-dashboard.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Premium Dhruv AI Dashboard
 * Complete rebuild with glassmorphism, gamification, and AI-driven insights
 */
const PremiumDashboard = () => {
  const { user } = useAuth();
  const { subscriptionInfo } = useSubscription();
  const navigate = useNavigate();

  // Core State
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [usageData, setUsageData] = useState(null);
  
  // Feature States
  const [showAIMentor, setShowAIMentor] = useState(false);
  const [focusModeActive, setFocusModeActive] = useState(false);
  const [userMood, setUserMood] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // User Progress
  const [userXP, setUserXP] = useState(0);
  const [userLevel, setUserLevel] = useState(1);
  const [currentStreak, setCurrentStreak] = useState(0);

  useEffect(() => {
    loadDashboardData();
    loadUserProgress();
    loadUsageData();
  }, []);

  useEffect(() => {
    // Apply dark mode
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  /**
   * Load dashboard analytics from backend
   */
  const loadDashboardData = async () => {
    try {
      setLoading(true);
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
        setCurrentStreak(data.current_streak || 0);
      } else {
        // Fallback data structure if API not available yet
        setDashboardData({
          study_time_today: "0h 45m",
          total_sessions: 12,
          current_streak: 7,
          weekly_progress: 78,
          subjects: [
            { name: "Mathematics", progress: 75, recent_topic: "Quadratic Equations" },
            { name: "Physics", progress: 60, recent_topic: "Newton's Laws" },
            { name: "Chemistry", progress: 45, recent_topic: "Chemical Bonding" }
          ]
        });
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load user XP and level from backend
   */
  const loadUserProgress = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/user/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserXP(data.xp || 0);
        setUserLevel(data.level || 1);
      } else {
        // Demo data for new users
        setUserXP(150);
        setUserLevel(2);
      }
    } catch (error) {
      console.error('Failed to load user progress:', error);
      setUserXP(150);
      setUserLevel(2);
    }
  };

  /**
   * Get dynamic greeting based on time of day and user data
   */
  const getDynamicGreeting = () => {
    const hour = new Date().getHours();
    const firstName = user?.full_name?.split(' ')[0] || 'Student';
    
    let timeGreeting = '';
    let emoji = '';
    
    if (hour < 12) {
      timeGreeting = 'Good Morning';
      emoji = '☀️';
    } else if (hour < 17) {
      timeGreeting = 'Good Afternoon';
      emoji = '🌤️';
    } else {
      timeGreeting = 'Good Evening';
      emoji = '🌙';
    }

    // Add contextual message based on progress
    let contextMessage = '';
    if (dashboardData?.subjects && dashboardData.subjects.length > 0) {
      const lowestProgress = dashboardData.subjects.reduce((min, subject) => 
        subject.progress < min.progress ? subject : min
      );
      if (lowestProgress.progress < 50) {
        contextMessage = `Let's focus on ${lowestProgress.name} today!`;
      } else {
        contextMessage = `You're making great progress!`;
      }
    }

    return {
      greeting: `${timeGreeting}, ${firstName}! ${emoji}`,
      message: contextMessage
    };
  };

  const greeting = getDynamicGreeting();

  // Loading skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header Skeleton */}
          <div className="glass-card rounded-2xl p-8 h-48 skeleton"></div>
          
          {/* Stats Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="glass-card rounded-xl h-32 skeleton"></div>
            ))}
          </div>
          
          {/* Content Skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <div className="glass-card rounded-2xl h-96 skeleton"></div>
              <div className="glass-card rounded-2xl h-64 skeleton"></div>
            </div>
            <div className="space-y-6">
              <div className="glass-card rounded-2xl h-96 skeleton"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-4 md:p-8 transition-all duration-500 ${userMood?.id === 'tired' || userMood?.id === 'stressed' ? 'opacity-90' : ''}`}>
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Premium Header with Dynamic Greeting */}
        <div className="glass-card glass-hover rounded-3xl p-6 md:p-8 shadow-premium-lg animate-fade-in">
          <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg animate-pulse-glow">
                  <Brain className="h-8 w-8 md:h-10 md:w-10 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-400 rounded-full border-4 border-white"></div>
              </div>
              <div>
                <h1 className="text-2xl md:text-4xl font-bold gradient-text mb-2">
                  {greeting.greeting}
                </h1>
                <p className="text-gray-600 dark:text-gray-300 text-sm md:text-base">
                  {greeting.message}
                </p>
              </div>
            </div>

            {/* Quick Stats & Actions */}
            <div className="flex items-center space-x-3">
              <div className="text-right mr-4">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">Level {userLevel}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">{userXP} XP</div>
              </div>
              
              <button
                onClick={() => setShowAIMentor(true)}
                className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="AI Mentor"
              >
                <MessageCircle className="h-5 w-5" />
              </button>
              
              <button
                onClick={() => setFocusModeActive(true)}
                className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="Focus Mode"
              >
                <Target className="h-5 w-5" />
              </button>
              
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="Toggle Dark Mode"
              >
                {isDarkMode ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5 text-gray-700" />}
              </button>
            </div>
          </div>

          {/* XP Progress Bar */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                Progress to Level {userLevel + 1}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {userXP % 100}/100 XP
              </span>
            </div>
            <div className="xp-bar">
              <div className="xp-fill" style={{ width: `${(userXP % 100)}%` }}></div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
          {/* Study Time Card */}
          <div className="glass-card glass-hover rounded-xl p-6 shadow-premium animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg">
                <Calendar className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">TODAY</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {dashboardData?.study_time_today || '0h 0m'}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Study Time</div>
          </div>

          {/* Sessions Card */}
          <div className="glass-card glass-hover rounded-xl p-6 shadow-premium animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-semibold text-purple-600 dark:text-purple-400">TOTAL</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {dashboardData?.total_sessions || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">AI Sessions</div>
          </div>

          {/* Streak Card */}
          <div className="glass-card glass-hover rounded-xl p-6 shadow-premium animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">STREAK</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {currentStreak} 🔥
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Day Streak</div>
          </div>

          {/* Progress Card */}
          <div className="glass-card glass-hover rounded-xl p-6 shadow-premium animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-semibold text-green-600 dark:text-green-400">WEEK</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {dashboardData?.weekly_progress || 0}%
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Weekly Goal</div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
          
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6 md:space-y-8">
            
            {/* Subject Progress with Radial Progress */}
            <div className="glass-card rounded-2xl p-6 shadow-premium animate-slide-up">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
                <Target className="h-5 w-5 mr-2 text-purple-600" />
                Your Learning Progress
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {dashboardData?.subjects?.map((subject, index) => (
                  <div key={index} className="flex flex-col items-center space-y-3">
                    <RadialProgress
                      progress={subject.progress}
                      size={140}
                      strokeWidth={10}
                      color={index === 0 ? '#667eea' : index === 1 ? '#10b981' : '#f59e0b'}
                      label={subject.name}
                      animate={true}
                    />
                    <div className="text-center">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                        Recent: {subject.recent_topic}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Streak Heatmap */}
            <StreakHeatmap userId={user?.id} />

            {/* Smart Recommendations */}
            <SmartRecommendations userData={dashboardData} />
            
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6 md:space-y-8">
            
            {/* Achievement Badges */}
            <AchievementBadges userXP={userXP} userLevel={userLevel} />

            {/* Live Leaderboard */}
            <LiveLeaderboard />

            {/* Weekly Challenge Card */}
            <div className="glass-card rounded-2xl p-6 shadow-premium animate-fade-in">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <Trophy className="h-5 w-5 mr-2 text-yellow-500" />
                Weekly Challenge
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 rounded-xl border-2 border-yellow-200 dark:border-yellow-700">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                    🎯 Complete 10 AI Sessions
                  </h4>
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300 mb-2">
                    <span>Progress</span>
                    <span className="font-bold">{dashboardData?.total_sessions || 0}/10</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, ((dashboardData?.total_sessions || 0) / 10) * 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    Reward: 100 XP + Consistency Badge
                  </p>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

      {/* Floating Components */}
      <QuickActionsToolbar />
      <MoodTracker onMoodChange={setUserMood} />
      
      {/* Modals */}
      <AIMentorChat 
        isOpen={showAIMentor} 
        onClose={() => setShowAIMentor(false)} 
      />
      
      <FocusMode 
        isActive={focusModeActive}
        onClose={() => setFocusModeActive(false)}
        focusPlan={dashboardData}
      />
    </div>
  );
};

export default PremiumDashboard;
