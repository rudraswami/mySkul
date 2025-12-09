import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  Trophy,
  Flame,
  Zap,
  Award
} from 'lucide-react';

// Import premium components
import QuickActionsToolbar from './QuickActionsToolbar';
import StreakHeatmap from './StreakHeatmap';
import AchievementBadges from './AchievementBadges';
import RadialProgress from './RadialProgress';
import SmartRecommendations from './SmartRecommendations';
import StudyPlanner from './StudyPlanner';
// V1: Leaderboard hidden - will enable in V2 with Mock Tests
// import LiveLeaderboard from './LiveLeaderboard';
import UsageMeter from '../UsageMeter';
import PlanBadge from '../PlanBadge';

// 🎮 GAMIFICATION: Import progress dashboard components
import ProgressDashboard, { StreakCard, LevelCard, TodayStats, BadgesCard } from '../gamification/ProgressDashboard';
import { useGamification } from '../../hooks/useGamification';

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
  
  // 🎮 GAMIFICATION: Use the gamification hook for real-time stats
  const {
    stats: gamificationStats,
    loading: gamificationLoading,
    level: currentLevel,
    xp: currentXP,
    streak: currentStreak,
    todayQuestions,
    todayAccuracy,
    badges
  } = useGamification(user?.id);

  // Core State
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [error, setError] = useState(null);
  
  // Feature States - Simplified for V1
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // Legacy User Progress (fallback if gamification fails)
  const [userXP, setUserXP] = useState(0);
  const [userLevel, setUserLevel] = useState(1);
  const [legacyStreak, setLegacyStreak] = useState(0);

  useEffect(() => {
    // Batch all API calls with Promise.allSettled to avoid race conditions
    const loadAllData = async () => {
      const results = await Promise.allSettled([
        loadDashboardData(),
        loadUserProgress(),
        loadUsageData()
      ]);
      
      // Log any failures for debugging
      results.forEach((result, index) => {
        if (result.status === 'rejected') {
          console.warn(`Dashboard API call ${index} failed:`, result.reason);
        }
      });
    };
    
    loadAllData();
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
   * Uses AbortController for 10s timeout to prevent hanging
   */
  const loadDashboardData = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
    
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/dashboard/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setLegacyStreak(data.current_streak || 0);
        setError(null);
      } else {
        // Return empty state for new users
        setDashboardData({
          study_time_today: "0h 0m",
          total_sessions: 0,
          current_streak: 0,
          weekly_progress: 0,
          subjects: []
        });
        if (response.status !== 404) {
          setError('Failed to load dashboard data. Please refresh the page.');
        }
      }
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        console.error('Dashboard data request timed out');
        setError('Request timed out. Please check your connection and try again.');
      } else {
        console.error('Failed to load dashboard data:', error);
        setError('Unable to connect to server. Please check your internet connection.');
      }
      // Set safe defaults
      setDashboardData({
        study_time_today: "0h 0m",
        total_sessions: 0,
        current_streak: 0,
        weekly_progress: 0,
        subjects: []
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load user XP and level from backend
   * Uses AbortController for 10s timeout
   */
  const loadUserProgress = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/user/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setUserXP(data.xp || data.total_xp || 0);
        setUserLevel(data.level || data.current_level || 1);
      } else {
        // For new users, start at 0 XP, Level 1
        setUserXP(0);
        setUserLevel(1);
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Failed to load user progress:', error);
      // Default to 0 for new users
      setUserXP(0);
      setUserLevel(1);
    }
  };

  /**
   * Load usage data for subscription meters
   * Uses AbortController for 10s timeout
   */
  const loadUsageData = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/subscription/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        // Normalize API response to expected format
        // Handle both { usage: { ai_mentor: {...} } } and { usage: { 'ai_mentor': {...} } }
        setUsageData(data);
      } else {
        // Default usage data for new users (free tier)
        setUsageData({
          subscription_tier: 'free',
          usage: {
            ai_mentor: { used: 0, limit: 10, remaining: 10 }
          }
        });
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Failed to load usage data:', error);
      // Default usage data on error
      setUsageData({
        subscription_tier: 'free',
        usage: {
          ai_mentor: { used: 0, limit: 10, remaining: 10 }
        }
      });
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
    <div className={`min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-4 md:p-8 transition-all duration-500`}>
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Error Banner */}
        {error && (
          <div className="glass-card rounded-xl p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 animate-fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-red-500 rounded-lg">
                  <span className="text-white text-lg">⚠️</span>
                </div>
                <div>
                  <p className="font-semibold text-red-900 dark:text-red-100">Connection Issue</p>
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setError(null);
                  loadDashboardData();
                  loadUserProgress();
                  loadUsageData();
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
              >
                Retry
              </button>
            </div>
          </div>
        )}
        
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

            {/* 🎮 GAMIFICATION: Quick Stats & Actions */}
            <div className="flex items-center space-x-3">
              {/* Streak Badge */}
              <motion.div 
                className={`flex items-center gap-2 px-4 py-2 rounded-xl ${
                  (currentStreak || legacyStreak) > 0 
                    ? 'bg-gradient-to-r from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 border-2 border-orange-300' 
                    : 'bg-gray-100 dark:bg-gray-800 border-2 border-gray-200'
                }`}
                whileHover={{ scale: 1.05 }}
              >
                <motion.span 
                  className="text-2xl"
                  animate={(currentStreak || legacyStreak) > 0 ? { scale: [1, 1.2, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 2 }}
                >
                  🔥
                </motion.span>
                <div>
                  <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
                    {currentStreak || legacyStreak || 0}
                  </div>
                  <div className="text-xs text-orange-500">Day Streak</div>
                </div>
              </motion.div>
              
              {/* Level & XP */}
              <motion.div 
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-purple-300"
                whileHover={{ scale: 1.05 }}
              >
                <span className="text-2xl">
                  {currentLevel === 'Master' ? '👑' : 
                   currentLevel === 'Scientist' ? '🧪' :
                   currentLevel === 'Tactician' ? '🎯' :
                   currentLevel === 'Analyst' ? '🔬' : '🔭'}
                </span>
                <div>
                  <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                    {currentLevel || `Level ${userLevel}`}
                  </div>
                  <div className="text-xs text-purple-500 flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    {currentXP || userXP} XP
                  </div>
                </div>
              </motion.div>
              
              {/* V1: Direct navigation to AI Tutor instead of modal */}
              <button
                onClick={() => navigate('/tutor')}
                className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="Start Learning"
              >
                <MessageCircle className="h-5 w-5" />
              </button>
              
              {/* V1: Focus Mode hidden */}
              {/* <button
                onClick={() => setFocusModeActive(true)}
                className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="Focus Mode"
              >
                <Target className="h-5 w-5" />
              </button> */}
              
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-110"
                title="Toggle Dark Mode"
              >
                {isDarkMode ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5 text-gray-700" />}
              </button>
            </div>
          </div>

          {/* 🎮 GAMIFICATION: XP Progress Bar with Level Info */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                {gamificationStats?.level?.is_max_level 
                  ? '👑 Maximum Level Achieved!' 
                  : `Progress to ${gamificationStats?.level?.next_level_name || `Level ${userLevel + 1}`}`}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {gamificationStats?.level?.level_xp || (userXP % 100)}/{gamificationStats?.level?.next_level_xp || 100} XP
              </span>
            </div>
            <div className="xp-bar relative overflow-hidden">
              <motion.div 
                className="xp-fill"
                initial={{ width: 0 }}
                animate={{ width: `${gamificationStats?.level?.progress_percent || (userXP % 100)}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
              {/* Shimmer effect */}
              <motion.div
                className="absolute top-0 h-full w-16 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                animate={{ x: [-64, 400] }}
                transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
              />
            </div>
            
            {/* Today's Quick Stats */}
            {gamificationStats?.today && (
              <div className="flex items-center gap-4 mt-3 text-sm">
                <div className="flex items-center gap-1 text-blue-600 dark:text-blue-400">
                  <MessageCircle className="w-4 h-4" />
                  <span>{gamificationStats.today.questions || 0} questions today</span>
                </div>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <Target className="w-4 h-4" />
                  <span>{Math.round(gamificationStats.today.accuracy || 0)}% accuracy</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Usage Meters - Subscription Limits */}
        <div className="glass-card rounded-2xl p-6 shadow-premium animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Your Usage Today
            </h2>
            <PlanBadge tier={subscriptionInfo?.subscription_tier || user?.subscription_type || 'free'} />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* AI Questions Usage */}
            <UsageMeter
              feature="AI Questions"
              used={usageData?.usage?.ai_mentor?.used || usageData?.usage?.['ai_mentor']?.used || 0}
              limit={usageData?.usage?.ai_mentor?.limit || usageData?.usage?.['ai_mentor']?.limit || 10}
              resetPeriod="daily"
              icon="🤖"
            />
            
            {/* Quick Start CTA - Only show if user has usage remaining */}
            {((usageData?.usage?.ai_mentor?.remaining || usageData?.usage?.['ai_mentor']?.remaining || 10) > 0) && (
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white flex flex-col justify-center items-center cursor-pointer hover:shadow-xl transition-all hover:scale-105" onClick={() => navigate('/tutor')}>
                <div className="text-3xl mb-2 animate-bounce-slow">🚀</div>
                <h3 className="text-lg font-bold mb-1">Start Learning Now</h3>
                <p className="text-sm text-blue-100 text-center">Ask your first question and begin your learning journey!</p>
                <div className="mt-3 text-xs text-blue-200">
                  {(usageData?.usage?.ai_mentor?.remaining || usageData?.usage?.['ai_mentor']?.remaining || 10)} questions remaining today
                </div>
              </div>
            )}
            
            {/* Upgrade CTA - Show if usage limit reached */}
            {((usageData?.usage?.ai_mentor?.remaining || usageData?.usage?.['ai_mentor']?.remaining || 10) === 0) && (
              <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-lg p-6 text-white flex flex-col justify-center items-center cursor-pointer hover:shadow-xl transition-all hover:scale-105" onClick={() => navigate('/subscription')}>
                <div className="text-3xl mb-2">⭐</div>
                <h3 className="text-lg font-bold mb-1">Upgrade to Continue Learning</h3>
                <p className="text-sm text-orange-100 text-center">You've used all your free questions today. Upgrade for unlimited access!</p>
                <div className="mt-3 px-4 py-2 bg-white/20 rounded-lg text-sm font-semibold">
                  View Plans →
                </div>
              </div>
            )}
            
            {/* Mock Tests Usage - Hidden for V1 */}
            {/* <UsageMeter
              feature="Mock Tests"
              used={usageData?.usage?.mock_tests?.used || 0}
              limit={usageData?.usage?.mock_tests?.limit || 2}
              resetPeriod="weekly"
              icon="📝"
            /> */}
            
            {/* Auto Notes Usage - Hidden for V1 */}
            {/* <UsageMeter
              feature="Auto Notes"
              used={usageData?.usage?.auto_notes?.used || 0}
              limit={usageData?.usage?.auto_notes?.limit || 5}
              resetPeriod="monthly"
              icon="📔"
            /> */}
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

          {/* 🎮 GAMIFICATION: Streak Card with Animation */}
          <motion.div 
            className="glass-card glass-hover rounded-xl p-6 shadow-premium animate-fade-in" 
            style={{ animationDelay: '0.2s' }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg">
                <Flame className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">STREAK</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1 flex items-center gap-2">
              <motion.span
                animate={(currentStreak || legacyStreak) > 0 ? { scale: [1, 1.1, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              >
                {currentStreak || legacyStreak || 0}
              </motion.span>
              <motion.span
                animate={(currentStreak || legacyStreak) > 0 ? { rotate: [0, 10, -10, 0] } : {}}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                🔥
              </motion.span>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {gamificationStats?.streak?.motivation || 'Day Streak'}
            </div>
          </motion.div>

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
              
              {dashboardData?.subjects && dashboardData.subjects.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {dashboardData.subjects.map((subject, index) => (
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
              ) : (
                <div className="text-center py-12">
                  {/* Animated Illustration */}
                  <div className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-purple-100 via-indigo-100 to-pink-100 dark:from-purple-900 dark:via-indigo-900 dark:to-pink-900 rounded-full mb-6 relative overflow-hidden">
                    <div className="absolute inset-0 animate-pulse bg-gradient-to-br from-purple-400/20 to-indigo-400/20"></div>
                    <Target className="h-16 w-16 text-purple-600 dark:text-purple-400 relative z-10 animate-bounce-slow" />
                  </div>
                  <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    Your Learning Journey Starts Here! 🚀
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                    Ask your first question to the AI Tutor and watch your progress grow. Every question brings you closer to mastery!
                  </p>
                  
                  {/* Quick Start Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 max-w-2xl mx-auto">
                    <button
                      onClick={() => navigate('/tutor')}
                      className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 rounded-xl border-2 border-blue-200 dark:border-blue-700 hover:shadow-lg transition-all hover:scale-105 text-left"
                    >
                      <div className="text-2xl mb-2">📐</div>
                      <div className="font-semibold text-gray-900 dark:text-white text-sm">Math Problem</div>
                      <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">Get step-by-step solutions</div>
                    </button>
                    <button
                      onClick={() => navigate('/tutor')}
                      className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 rounded-xl border-2 border-green-200 dark:border-green-700 hover:shadow-lg transition-all hover:scale-105 text-left"
                    >
                      <div className="text-2xl mb-2">🔬</div>
                      <div className="font-semibold text-gray-900 dark:text-white text-sm">Science Question</div>
                      <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">Understand concepts deeply</div>
                    </button>
                    <button
                      onClick={() => navigate('/tutor')}
                      className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 rounded-xl border-2 border-purple-200 dark:border-purple-700 hover:shadow-lg transition-all hover:scale-105 text-left"
                    >
                      <div className="text-2xl mb-2">📚</div>
                      <div className="font-semibold text-gray-900 dark:text-white text-sm">Exam Prep</div>
                      <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">Prepare for your exams</div>
                    </button>
                  </div>
                  
                  <button
                    onClick={() => navigate('/tutor')}
                    className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all hover:scale-105 text-lg"
                  >
                    Ask Your First Question →
                  </button>
                </div>
              )}
            </div>

            {/* 📚 AI Study Planner - Daily personalized study plan */}
            <StudyPlanner 
              onStartStudy={(topic) => {
                // Navigate to Sathi with the topic
                window.location.href = `/sathi?topic=${encodeURIComponent(topic)}`;
              }}
            />

            {/* Streak Heatmap */}
            <StreakHeatmap userId={user?.id} />

            {/* Smart Recommendations */}
            <SmartRecommendations userData={dashboardData} />
            
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6 md:space-y-8">
            
            {/* Achievement Badges */}
            <AchievementBadges userXP={userXP} userLevel={userLevel} />

            {/* V1: Leaderboard Hidden - Will enable in V2 when Mock Tests are available
                Leaderboard makes more sense with competitive content (test scores, accuracy rates)
                For V1, focusing on personal progress and achievements */}
            {/* <LiveLeaderboard /> */}

            {/* Weekly Challenge Card - Enhanced */}
            <div className="glass-card rounded-2xl p-6 shadow-premium animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
                  <Trophy className="h-5 w-5 mr-2 text-yellow-500" />
                  Weekly Challenge
                </h3>
                {/* Countdown Timer */}
                <div className="text-right">
                  <div className="text-xs text-gray-500 dark:text-gray-400">Time left</div>
                  <div className="text-sm font-bold text-orange-600 dark:text-orange-400">
                    {(() => {
                      const now = new Date();
                      const dayOfWeek = now.getDay();
                      const daysUntilSunday = dayOfWeek === 0 ? 7 : 7 - dayOfWeek;
                      return daysUntilSunday === 7 ? 'Today!' : `${daysUntilSunday}d left`;
                    })()}
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 rounded-xl border-2 border-yellow-200 dark:border-yellow-700 relative overflow-hidden">
                  {/* Celebration overlay when completed */}
                  {(dashboardData?.total_sessions || 0) >= 10 && (
                    <div className="absolute inset-0 bg-gradient-to-r from-green-400/20 to-emerald-400/20 animate-pulse"></div>
                  )}
                  
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center relative z-10">
                    🎯 Complete 10 AI Sessions
                    {(dashboardData?.total_sessions || 0) >= 10 && (
                      <span className="ml-2 text-xs bg-green-500 text-white px-2 py-0.5 rounded-full animate-bounce">Completed! 🎉</span>
                    )}
                  </h4>
                  
                  {/* Milestone Indicators */}
                  <div className="flex items-center justify-between mb-2 relative z-10">
                    {[3, 5, 7, 10].map((milestone) => {
                      const sessions = dashboardData?.total_sessions || 0;
                      const reached = sessions >= milestone;
                      return (
                        <div key={milestone} className="flex flex-col items-center">
                          <div className={`w-2 h-2 rounded-full ${reached ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'}`}></div>
                          <span className={`text-xs mt-1 ${reached ? 'text-green-600 dark:text-green-400 font-semibold' : 'text-gray-400'}`}>
                            {milestone}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300 mb-2 relative z-10">
                    <span>Progress</span>
                    <span className="font-bold">{dashboardData?.total_sessions || 0}/10</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden relative z-10">
                    <div 
                      className={`h-2.5 rounded-full transition-all duration-500 ${
                        (dashboardData?.total_sessions || 0) >= 10
                          ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                          : 'bg-gradient-to-r from-yellow-500 to-orange-500'
                      }`}
                      style={{ width: `${Math.min(100, ((dashboardData?.total_sessions || 0) / 10) * 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 relative z-10">
                    {(dashboardData?.total_sessions || 0) >= 10 
                      ? "🎉 Challenge completed! You earned 100 XP + Consistency Badge. Amazing work!"
                      : `Reward: 100 XP + Consistency Badge (${Math.max(0, 10 - (dashboardData?.total_sessions || 0))} more sessions needed)`
                    }
                  </p>
                  
                  {/* Next milestone indicator */}
                  {(dashboardData?.total_sessions || 0) < 10 && (
                    <div className="mt-2 pt-2 border-t border-yellow-300 dark:border-yellow-700 relative z-10">
                      <p className="text-xs text-yellow-700 dark:text-yellow-300">
                        {(() => {
                          const sessions = dashboardData?.total_sessions || 0;
                          const nextMilestone = [3, 5, 7, 10].find(m => m > sessions);
                          return nextMilestone 
                            ? `🎯 ${nextMilestone - sessions} more to reach ${nextMilestone} sessions milestone!`
                            : '';
                        })()}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Daily Goal Card - Enhanced with Streak */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-xl border border-blue-200 dark:border-blue-700">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900 dark:text-white flex items-center">
                      ⭐ Daily Goal: Ask 3 Questions
                    </h4>
                    {/* Streak Multiplier */}
                    {currentStreak > 0 && (
                      <div className="px-2 py-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs font-bold rounded-full">
                        {currentStreak >= 7 ? '3x' : currentStreak >= 3 ? '2x' : '1.5x'} XP
                      </div>
                    )}
                  </div>
                  
                  {/* Streak Counter */}
                  {currentStreak > 0 && (
                    <div className="mb-2 flex items-center space-x-2">
                      <span className="text-lg">🔥</span>
                      <span className="text-sm font-semibold text-orange-600 dark:text-orange-400">
                        {currentStreak} day{currentStreak !== 1 ? 's' : ''} in a row!
                      </span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300 mb-2">
                    <span>Today's Progress</span>
                    <span className="font-bold">
                      {(() => {
                        // Estimate based on study_time_today - if there's activity, assume at least 1 question
                        const hasActivity = dashboardData?.study_time_today && dashboardData.study_time_today !== "0h 0m";
                        return hasActivity ? '1+' : '0';
                      })()}/3
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, (dashboardData?.study_time_today && dashboardData.study_time_today !== "0h 0m" ? 33 : 0))}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    {(() => {
                      const hasActivity = dashboardData?.study_time_today && dashboardData.study_time_today !== "0h 0m";
                      const remaining = hasActivity ? 2 : 3;
                      if (currentStreak >= 7) {
                        return `Perfect week! Keep it up! ${remaining} more questions today for 3x XP bonus! 🔥`;
                      } else if (currentStreak >= 3) {
                        return `Great streak! ${remaining} more questions today for 2x XP bonus! 💪`;
                      } else if (currentStreak > 0) {
                        return `Streak alive! ${remaining} more questions today to maintain it! ⚡`;
                      }
                      return `Keep your streak alive! Ask ${remaining} more questions today to earn XP.`;
                    })()}
                  </p>
                  
                  {/* Next reward preview */}
                  {(() => {
                    const hasActivity = dashboardData?.study_time_today && dashboardData.study_time_today !== "0h 0m";
                    const questionsDone = hasActivity ? 1 : 0;
                    if (questionsDone < 3) {
                      return (
                        <div className="mt-2 pt-2 border-t border-blue-300 dark:border-blue-700">
                          <p className="text-xs text-blue-700 dark:text-blue-300">
                            💰 Complete today's goal to earn {currentStreak >= 7 ? '30' : currentStreak >= 3 ? '20' : '15'} XP bonus!
                          </p>
                        </div>
                      );
                    }
                    return null;
                  })()}
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

      {/* Floating Components */}
      <QuickActionsToolbar />
      
      {/* V1: Simplified - MoodTracker and FocusMode hidden for cleaner V1 experience */}
      {/* <MoodTracker onMoodChange={setUserMood} /> */}
      
      {/* Modals - Simplified for V1 */}
      {/* <AIMentorChat 
        isOpen={showAIMentor} 
        onClose={() => setShowAIMentor(false)} 
      /> */}
      
      {/* <FocusMode 
        isActive={focusModeActive}
        onClose={() => setFocusModeActive(false)}
        focusPlan={dashboardData}
      /> */}
    </div>
  );
};

export default PremiumDashboard;
