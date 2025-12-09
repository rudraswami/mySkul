import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Brain, 
  MessageCircle,
  Sun,
  Moon,
  Zap,
  Flame,
  Trophy,
  Target,
  BookOpen,
  ChevronRight
} from 'lucide-react';

// Import dashboard components
import QuickActionsToolbar from './QuickActionsToolbar';
import StreakHeatmap from './StreakHeatmap';
import AchievementBadges from './AchievementBadges';
import StudyPlanner from './StudyPlanner';

// Gamification hook
import { useGamification } from '../../hooks/useGamification';

// Import styles
import '../../styles/premium-dashboard.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * 🎯 Premium Dashboard - PROFESSIONAL REDESIGN
 * =============================================
 * 
 * Design System:
 * - Primary: Indigo (#4F46E5)
 * - Accent: Violet (#7C3AED)  
 * - Success: Emerald (#10B981)
 * - Warning: Amber (#F59E0B)
 * - Background: Slate-50 to White gradient
 * 
 * Typography:
 * - Headings: 600-700 weight
 * - Body: 400-500 weight
 * - Sizes: 12px, 14px, 16px, 20px, 24px, 32px
 * 
 * Spacing: 8px increments (8, 16, 24, 32, 48)
 */
const PremiumDashboard = () => {
  const { user } = useAuth();
  const { subscriptionInfo } = useSubscription();
  const navigate = useNavigate();
  
  // Gamification stats
  const {
    level: currentLevel,
    xp: currentXP,
    streak: currentStreak,
  } = useGamification(user?.id);

  // State
  const [loading, setLoading] = useState(true);
  const [usageData, setUsageData] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // Fallbacks
  const [userXP, setUserXP] = useState(0);
  const [userLevel, setUserLevel] = useState(1);
  const [legacyStreak, setLegacyStreak] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      await Promise.allSettled([loadUserProgress(), loadUsageData()]);
      setLoading(false);
    };
    loadData();
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  const loadUserProgress = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/user/progress`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUserXP(data.xp || 0);
        setUserLevel(data.level || 1);
        setLegacyStreak(data.current_streak || 0);
      }
    } catch (err) {
      console.error('Failed to load progress:', err);
    }
  };

  const loadUsageData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/subscription/usage`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setUsageData(response.ok ? await response.json() : {
        usage: { ai_mentor: { used: 0, limit: 10, remaining: 10 } }
      });
    } catch (err) {
      setUsageData({ usage: { ai_mentor: { used: 0, limit: 10, remaining: 10 } } });
    }
  };

  // Dynamic greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    const name = user?.full_name?.split(' ')[0] || 'Student';
    if (hour < 12) return { text: `Good Morning, ${name}`, emoji: '☀️', period: 'morning' };
    if (hour < 17) return { text: `Good Afternoon, ${name}`, emoji: '🌤️', period: 'afternoon' };
    return { text: `Good Evening, ${name}`, emoji: '🌙', period: 'evening' };
  };

  const greeting = getGreeting();
  const streak = currentStreak || legacyStreak || 0;
  const xp = currentXP || userXP;
  const level = currentLevel || userLevel;
  const questionsUsed = usageData?.usage?.ai_mentor?.used || 0;
  const questionsLimit = usageData?.usage?.ai_mentor?.limit || 10;
  const questionsRemaining = Math.max(0, questionsLimit - questionsUsed);
  const usagePercent = questionsLimit > 0 ? (questionsUsed / questionsLimit) * 100 : 0;
  const tier = subscriptionInfo?.subscription_tier || user?.subscription_type || 'free';

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* ════════════════════════════════════════════════════════════
            HERO HEADER - Clean, Professional Design
        ════════════════════════════════════════════════════════════ */}
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden"
        >
          {/* Top accent line */}
          <div className="h-1 bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500" />
          
          <div className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              {/* Left: Greeting */}
              <div className="flex items-center gap-4">
                <motion.div 
                  className="relative"
                  whileHover={{ scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 400 }}
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/25">
                    <Brain className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-800 flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full" />
                  </div>
                </motion.div>
                
                <div>
                  <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
                    {greeting.text} <span className="inline-block">{greeting.emoji}</span>
                  </h1>
                  <p className="text-slate-500 dark:text-slate-400 mt-1">
                    Ready to continue your learning journey?
                  </p>
                </div>
              </div>

              {/* Right: Stats Badges */}
              <div className="flex items-center gap-3 flex-wrap">
                {/* 🔥 Streak */}
                <motion.div 
                  whileHover={{ scale: 1.02, y: -2 }}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all ${
                    streak > 0 
                      ? 'bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/50 dark:to-amber-950/50 border-orange-200 dark:border-orange-800' 
                      : 'bg-slate-50 dark:bg-slate-700/50 border-slate-200 dark:border-slate-600'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    streak > 0 ? 'bg-gradient-to-br from-orange-500 to-amber-500' : 'bg-slate-300 dark:bg-slate-600'
                  }`}>
                    <Flame className={`w-5 h-5 ${streak > 0 ? 'text-white' : 'text-slate-500'}`} />
                  </div>
                  <div>
                    <div className={`text-xl font-bold ${streak > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-slate-500'}`}>
                      {streak}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium">
                      Day Streak
                    </div>
                  </div>
                </motion.div>
                
                {/* ⚡ Level & XP */}
                <motion.div 
                  whileHover={{ scale: 1.02, y: -2 }}
                  className="flex items-center gap-3 px-4 py-3 bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-950/50 dark:to-violet-950/50 rounded-xl border border-indigo-200 dark:border-indigo-800"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                    <Trophy className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                      Level {level}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1 font-medium">
                      <Zap className="w-3 h-3 text-amber-500" />
                      {xp} XP
                    </div>
                  </div>
                </motion.div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigate('/tutor')}
                    className="p-3 bg-gradient-to-br from-indigo-500 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-shadow"
                    title="Start Learning"
                  >
                    <MessageCircle className="h-5 w-5" />
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="p-3 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                    title="Toggle Theme"
                  >
                    {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                  </motion.button>
                </div>
              </div>
            </div>
          </div>
        </motion.header>

        {/* ════════════════════════════════════════════════════════════
            USAGE & QUICK ACTION BAR
        ════════════════════════════════════════════════════════════ */}
        <motion.section 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4"
        >
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            {/* Usage Meter */}
            <div className="flex items-center gap-4 flex-1 w-full">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">AI Questions</span>
                    <span className="text-sm font-bold text-slate-900 dark:text-white">{questionsUsed}/{questionsLimit}</span>
                  </div>
                  <div className="h-2 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${usagePercent}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      className={`h-full rounded-full ${
                        usagePercent >= 80 ? 'bg-red-500' : usagePercent >= 50 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                    />
                  </div>
                </div>
              </div>
              
              {/* Plan Badge */}
              <span className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide ${
                tier === 'premium' || tier === 'pro' 
                  ? 'bg-gradient-to-r from-amber-400 to-orange-500 text-white' 
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
              }`}>
                {tier}
              </span>
            </div>
            
            {/* CTA Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(questionsRemaining > 0 ? '/tutor' : '/subscription')}
              className={`px-6 py-3 rounded-xl font-semibold text-white shadow-lg transition-all flex items-center gap-2 whitespace-nowrap ${
                questionsRemaining > 0
                  ? 'bg-gradient-to-r from-indigo-500 to-violet-600 hover:shadow-indigo-500/25'
                  : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:shadow-amber-500/25'
              }`}
            >
              {questionsRemaining > 0 ? (
                <>
                  <BookOpen className="w-5 h-5" />
                  Start Learning
                  <span className="px-2 py-0.5 bg-white/20 rounded-md text-sm">{questionsRemaining} left</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Upgrade Now
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </motion.button>
          </div>
        </motion.section>

        {/* ════════════════════════════════════════════════════════════
            MAIN CONTENT GRID
        ════════════════════════════════════════════════════════════ */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LEFT: Study Planner - Main Content */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <StudyPlanner 
              onStartStudy={(topic) => navigate(`/tutor?topic=${encodeURIComponent(topic)}`)}
            />
          </motion.div>

          {/* RIGHT: Sidebar */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            {/* Achievements */}
            <AchievementBadges userXP={xp} userLevel={level} />

            {/* Streak Heatmap */}
            <StreakHeatmap userId={user?.id} />
          </motion.div>
        </div>

      </div>

      {/* Floating Actions */}
      <QuickActionsToolbar />
    </div>
  );
};

export default PremiumDashboard;
