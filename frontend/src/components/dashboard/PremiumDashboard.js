import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, Sparkles, Zap, Flame, Target, MessageCircle, Camera,
  Clock, Play, BookOpen, TrendingUp, TrendingDown, 
  Battery, Coffee, AlertCircle, ChevronRight, Star,
  BarChart2, Calendar, Award, Heart, Loader2, Rocket,
  Trophy, CheckCircle2, AlertTriangle, Info
} from 'lucide-react';

import { useGamification } from '../../hooks/useGamification';
import { BrandLoadingScreen } from '../ui/BrandLogo';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * 🧠 Cognito OS — Progress Screen
 * ==================================================
 * 
 * Philosophy: "The AI is quietly supporting the student when they are not chatting."
 * 
 * This is NOT a gamified dashboard. It's a calm, supportive presence
 * that shows the student their learning journey without pressure.
 * 
 * Design Principles:
 * - Minimal, calming UI
 * - No commanding language ("must", "complete", "deadline")
 * - Supportive, encouraging tone
 * - Information when needed, not overwhelming
 * 
 * DATA SOURCES:
 * - /api/user/progress → XP, Level, Streak
 * - /api/analytics/subject-progress → Subject understanding
 * - /api/study-planner/today → Gentle suggestions
 * - /api/subscription/usage → Chat availability
 */

// ============================================================================
// API FETCHER HELPER
// ============================================================================
const fetchWithAuth = async (endpoint) => {
  const token = localStorage.getItem('dhruv_ai_token');
  try {
    const res = await fetch(`${BACKEND_URL}${endpoint}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) return await res.json();
    return null;
  } catch (e) {
    console.error(`Failed to fetch ${endpoint}:`, e);
    return null;
  }
};

// Helper to format relative time
const formatTimeAgo = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================
const PremiumDashboard = () => {
  const { user } = useAuth();
  const { subscriptionInfo } = useSubscription();
  const navigate = useNavigate();
  const { level: curLevel, xp: curXP, streak: curStreak } = useGamification(user?.id);

  // State
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(null);
  const [subjectMastery, setSubjectMastery] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [recentChats, setRecentChats] = useState([]);

  // Fetch ALL data from APIs
  useEffect(() => {
    const loadAllData = async () => {
      const [progressData, masteryData, planData, usageRes, recsData, chatsData] = await Promise.all([
        fetchWithAuth('/api/user/progress'),
        fetchWithAuth('/api/analytics/subject-progress'),
        fetchWithAuth('/api/study-planner/today'),
        fetchWithAuth('/api/subscription/usage'),
        fetchWithAuth('/api/cognitive/recommendations'),
        fetchWithAuth('/api/ai/chat/sessions')
      ]);

      setProgress(progressData);
      setSubjectMastery(masteryData);
      if (planData?.blocks?.length > 0) setStudyPlan(planData);
      setUsageData(usageRes);
      setAiRecommendation(recsData);
      // Get last 3 conversations
      if (chatsData?.sessions) {
        setRecentChats(chatsData.sessions.slice(0, 3));
      }
      setLoading(false);
    };
    loadAllData();
  }, []);

  // Computed values
  const firstName = user?.full_name?.split(' ')[0] || 'there';
  const tier = subscriptionInfo?.subscription_tier || user?.subscription_type || 'Free';
  
  // Stats from API (with fallbacks)
  const xp = curXP || progress?.xp || progress?.total_xp || 0;
  const level = curLevel || progress?.level || progress?.current_level || 1;
  const streak = curStreak || progress?.current_streak || 0;
  const badgesEarned = progress?.badges_earned || progress?.badges || [];
  
  // AI chats remaining
  const aiChatsLimit = usageData?.usage?.ai_mentor?.limit || 10;
  const aiChatsUsed = usageData?.usage?.ai_mentor?.used || 0;
  const aiChatsLeft = Math.max(0, aiChatsLimit - aiChatsUsed);

  // Subject mastery from API
  const subjects = useMemo(() => {
    if (subjectMastery?.subjects) {
      return Object.entries(subjectMastery.subjects).map(([name, data]) => ({
        name,
        score: Math.round((data.mastery || data.score || 0) * 100) / 100,
        trend: data.trend || (data.change > 0 ? 'up' : data.change < 0 ? 'down' : 'stable'),
        change: data.change ? `${data.change > 0 ? '+' : ''}${data.change}%` : '—',
        color: name.toLowerCase().includes('physics') ? 'violet' : 
               name.toLowerCase().includes('chem') ? 'amber' : 'emerald'
      }));
    }
    // Default subjects if no API data
    return [
      { name: 'Physics', score: 0, trend: 'stable', change: '—', color: 'violet' },
      { name: 'Chemistry', score: 0, trend: 'stable', change: '—', color: 'amber' },
      { name: 'Mathematics', score: 0, trend: 'stable', change: '—', color: 'emerald' },
    ];
  }, [subjectMastery]);

  // Smart greeting
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return { text: 'Good morning', emoji: '☀️' };
    if (hour >= 12 && hour < 17) return { text: 'Good afternoon', emoji: '🌤️' };
    if (hour >= 17 && hour < 21) return { text: 'Good evening', emoji: '🌅' };
    return { text: 'Burning the midnight oil', emoji: '🌙' };
  }, []);

  // Focus recommendation (from study plan or AI)
  const focus = useMemo(() => {
    // Try study plan first
    if (studyPlan?.blocks) {
      const nextBlock = studyPlan.blocks.find(b => !b.completed && b.block_type !== 'break');
      if (nextBlock) {
        return {
          subject: nextBlock.subject || 'General',
          topic: nextBlock.topic || 'Study Session',
          duration: nextBlock.duration_minutes || 45,
          xpReward: Math.round((nextBlock.duration_minutes || 45) * 2.5),
          reason: `Based on your study plan for today.`,
          source: 'study_plan'
        };
      }
    }

    // Try AI recommendations
    if (aiRecommendation?.data?.recommendations?.[0]) {
      const rec = aiRecommendation.data.recommendations[0];
      return {
        subject: rec.subject || 'General',
        topic: rec.topic || rec.title || 'Recommended Focus',
        duration: rec.duration || 45,
        xpReward: 120,
        reason: rec.reason || 'DRON AI detected this needs attention.',
        source: 'ai'
      };
    }

    // Fallback based on weakest subject
    const weakest = [...subjects].sort((a, b) => a.score - b.score)[0];
    return {
      subject: weakest?.name || 'Physics',
      topic: 'Core Concepts Review',
      duration: 30,
      xpReward: 80,
      reason: weakest?.score > 0 
        ? `${weakest.name} is at ${weakest.score}% - let's strengthen it!`
        : `Start building your ${weakest?.name || 'Physics'} foundation.`,
      source: 'analysis'
    };
  }, [studyPlan, aiRecommendation, subjects]);

  // Wellness state
  const wellness = useMemo(() => {
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 5) {
      return { status: 'Rest Mode', message: "It's late! Rest is part of learning.", icon: Coffee, color: 'amber', tip: 'Sleep consolidates memory' };
    }
    if (aiChatsUsed > 15) {
      return { status: 'High Activity', message: "You've been working hard today!", icon: Heart, color: 'rose', tip: 'Consider a short break' };
    }
    if (streak >= 7) {
      return { status: 'On Fire', message: `${streak} day streak! You're unstoppable!`, icon: Flame, color: 'orange', tip: 'Keep the momentum!' };
    }
    return { status: 'Ready', message: "You're in a great flow state!", icon: Battery, color: 'emerald', tip: 'Perfect time for deep learning' };
  }, [aiChatsUsed, streak]);

  // AI Check-In - Calm, supportive insight (not commanding)
  const aiCheckIn = useMemo(() => {
    const hour = new Date().getHours();
    const isLateNight = hour >= 23 || hour < 5;
    const isMorning = hour >= 5 && hour < 12;
    
    // Late night - gentle care
    if (isLateNight) {
      return {
        message: "It's late. Your brain consolidates learning during sleep.",
        suggestion: "Consider resting. I'll be here tomorrow.",
        mood: 'calm'
      };
    }
    
    // Based on activity
    if (streak >= 7) {
      return {
        message: `You've shown up ${streak} days in a row. That consistency matters more than any single session.`,
        suggestion: null,
        mood: 'proud'
      };
    }
    
    if (aiChatsUsed > 10) {
      return {
        message: "You've been learning actively today. That's wonderful.",
        suggestion: "Take a break if you need one. Learning continues even when you rest.",
        mood: 'caring'
      };
    }
    
    // Morning encouragement
    if (isMorning) {
      return {
        message: "Fresh day, fresh mind. No pressure—just curiosity.",
        suggestion: null,
        mood: 'gentle'
      };
    }
    
    // Default - always supportive
    return {
      message: "I'm here whenever you need me. No rush.",
      suggestion: null,
      mood: 'present'
    };
  }, [streak, aiChatsUsed]);

  // Learning Momentum - Presence-based, not score-based
  const learningMomentum = useMemo(() => {
    // Calculate based on recent activity, not scores
    const hasRecentActivity = aiChatsUsed > 0;
    const hasStreak = streak > 0;
    const hasProgress = subjects.some(s => s.score > 0);
    
    if (!hasRecentActivity && !hasStreak && !hasProgress) {
      return { status: 'starting', label: 'Just Beginning', description: "Every expert was once a beginner." };
    }
    if (hasStreak && streak >= 3) {
      return { status: 'building', label: 'Building Momentum', description: "You're showing up consistently. That's what matters." };
    }
    if (hasRecentActivity) {
      return { status: 'active', label: 'Actively Learning', description: "You're engaged today. Keep going at your pace." };
    }
    return { status: 'present', label: 'Present', description: "You're here. That's the first step." };
  }, [aiChatsUsed, streak, subjects]);

  // Loading State - Calm loading
  if (loading) {
    return <BrandLoadingScreen message="Preparing your progress..." />;
  }

  // Check if new user (zero state)
  const isNewUser = xp === 0 && streak === 0 && badgesEarned.length === 0;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Subtle Background - Calmer, less intense */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-slate-800/30 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-slate-800/20 blur-[120px] rounded-full" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 p-6 lg:p-10 max-w-5xl mx-auto space-y-8">
        
        {/* ============ HEADER - Calm, Supportive ============ */}
        <header className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl lg:text-2xl font-medium text-white">
                {greeting.text}, {firstName}
              </h1>
              <p className="text-slate-500 text-sm mt-1">
                Your learning journey
              </p>
            </div>

            {/* Minimal Stats - Small, non-dominant */}
            <div className="flex items-center gap-2 text-sm">
              {streak > 0 && (
                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800/50 text-slate-400">
                  <Flame className="w-3.5 h-3.5 text-orange-400" />
                  {streak} {streak === 1 ? 'day' : 'days'}
                </span>
              )}
              {xp > 0 && (
                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800/50 text-slate-400">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  {xp} XP
                </span>
              )}
            </div>
          </div>
        </header>

        {/* ============ AI CHECK-IN - The Companion Presence ============ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/40"
        >
          <div className="flex items-start gap-4">
            <div className="p-2.5 rounded-xl bg-violet-500/10 flex-shrink-0">
              <Brain className="w-5 h-5 text-violet-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-slate-300 text-sm leading-relaxed">
                {aiCheckIn.message}
              </p>
              {aiCheckIn.suggestion && (
                <p className="text-slate-500 text-xs mt-2">
                  {aiCheckIn.suggestion}
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* ============ RESUME LEARNING - Single Primary CTA ============ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-900/60 border border-slate-800/50"
        >
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1">
              <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Continue where you left off</p>
              <h2 className="text-lg font-medium text-white">
                {focus.topic}
              </h2>
              <p className="text-slate-500 text-sm mt-1">{focus.subject}</p>
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/tutor')}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-medium transition-colors"
            >
              <MessageCircle className="w-4 h-4" />
              Talk to AI
            </motion.button>
          </div>
        </motion.div>

        {/* ============ LEARNING MOMENTUM - Presence-based ============ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="p-5 rounded-2xl bg-slate-900/30 border border-slate-800/30"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-xs uppercase tracking-wide">Learning Momentum</p>
              <p className="text-white font-medium mt-1">{learningMomentum.label}</p>
              <p className="text-slate-500 text-sm mt-0.5">{learningMomentum.description}</p>
            </div>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div 
                  key={i}
                  className={`w-2 h-8 rounded-full transition-colors ${
                    (learningMomentum.status === 'building' && i <= 4) ||
                    (learningMomentum.status === 'active' && i <= 3) ||
                    (learningMomentum.status === 'present' && i <= 2) ||
                    (learningMomentum.status === 'starting' && i <= 1)
                      ? 'bg-violet-500/60'
                      : 'bg-slate-800'
                  }`}
                />
              ))}
            </div>
          </div>
        </motion.div>

        {/* ============ RECENT CONVERSATIONS ============ */}
        {recentChats.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.18 }}
            className="p-5 rounded-2xl bg-slate-900/30 border border-slate-800/30"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-slate-400">Recent Conversations</h3>
              <button 
                onClick={() => navigate('/tutor')}
                className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
              >
                View all
              </button>
            </div>
            <div className="space-y-2">
              {recentChats.map((chat, i) => (
                <div 
                  key={chat.session_id || i}
                  className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/20 hover:bg-slate-800/40 transition-colors cursor-pointer"
                  onClick={() => navigate(`/tutor?session=${chat.session_id}`)}
                >
                  <div className="p-2 rounded-lg bg-violet-500/10">
                    <MessageCircle className="w-4 h-4 text-violet-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-300 truncate">
                      {chat.title || 'Untitled chat'}
                    </p>
                    <p className="text-xs text-slate-600">
                      {chat.subject || 'General'} • {formatTimeAgo(chat.updated_at || chat.created_at)}
                    </p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ============ MAIN CONTENT GRID ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* SUBJECT UNDERSTANDING */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-5 rounded-2xl bg-slate-900/30 border border-slate-800/30"
          >
            <h3 className="text-sm font-medium text-slate-400 mb-4">Subject Understanding</h3>
            <div className="space-y-4">
              {subjects.map((subject, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-300">{subject.name}</span>
                    <span className="text-slate-500">
                      {subject.score > 0 ? `${subject.score}%` : 'Just starting'}
                    </span>
                  </div>
                  <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(subject.score, 5)}%` }}
                      transition={{ duration: 1, delay: i * 0.1 }}
                      className="h-full rounded-full bg-gradient-to-r from-violet-600 to-violet-400"
                    />
                  </div>
                </div>
              ))}
            </div>
            
            {subjects.every(s => s.score === 0) && (
              <p className="text-slate-600 text-xs text-center mt-4">
                Understanding builds with each conversation
              </p>
            )}
          </motion.div>

          {/* GENTLE SUGGESTIONS - Optional, not commanding */}
          {studyPlan?.blocks && studyPlan.blocks.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="p-5 rounded-2xl bg-slate-900/30 border border-slate-800/30"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-slate-400">Gentle Suggestions</h3>
                <span className="text-xs text-slate-600">Optional</span>
              </div>
              
              <div className="space-y-2">
                {studyPlan.blocks.slice(0, 3).filter(b => !b.completed && b.block_type !== 'break').map((block, i) => (
                  <div 
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/20 hover:bg-slate-800/40 transition-colors cursor-pointer"
                    onClick={() => navigate(`/tutor?topic=${encodeURIComponent(block.topic || block.subject)}`)}
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-violet-400/50" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-300 truncate">
                        {block.topic || block.block_type?.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-slate-600">{block.subject}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-600" />
                  </div>
                ))}
              </div>
              
              <p className="text-xs text-slate-600 text-center mt-3">
                These are just ideas. Follow your curiosity.
              </p>
            </motion.div>
          )}

          {/* ACHIEVEMENTS - Simplified, not gamified */}
          {badgesEarned.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="p-5 rounded-2xl bg-slate-900/30 border border-slate-800/30"
            >
              <h3 className="text-sm font-medium text-slate-400 mb-4">Milestones</h3>
              <div className="flex flex-wrap gap-2">
                {badgesEarned.slice(0, 4).map((badge, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/30"
                  >
                    <span className="text-base">{badge.emoji || '✨'}</span>
                    <span className="text-xs text-slate-400">{badge.name || badge}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* NEW USER - Warm Welcome */}
          {isNewUser && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40"
            >
              <div className="text-center max-w-md mx-auto">
                <div className="w-12 h-12 rounded-full bg-violet-500/10 flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-6 h-6 text-violet-400" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Welcome to DRON AI</h3>
                <p className="text-slate-400 text-sm mb-4">
                  I'm your AI learning companion. I'm here to help you understand anything, 
                  at your pace, without judgment. Ask me anything—there are no dumb questions.
                </p>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigate('/tutor')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-medium transition-colors"
                >
                  Start a Conversation
                  <ChevronRight className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          )}
        </div>

        {/* ============ FOOTER - Minimal ============ */}
        <footer className="flex items-center justify-center py-8">
          <span className="text-xs text-slate-600">DRON AI • Your Learning Companion</span>
        </footer>
      </div>
    </div>
  );
};

// ============================================================================
// STAT PILL COMPONENT
// ============================================================================
const StatPill = ({ icon: Icon, value, label, color, highlight, warning }) => (
  <div className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all ${
    warning 
      ? 'bg-rose-500/10 border-rose-500/30' 
      : highlight 
        ? `bg-${color}-500/10 border-${color}-500/30` 
        : 'bg-slate-900/80 border-slate-800/60'
  }`}>
    <Icon className={`w-4 h-4 ${warning ? 'text-rose-400' : `text-${color}-400`}`} strokeWidth={2} />
    <span className={`font-bold ${warning ? 'text-rose-400' : 'text-white'}`}>{value}</span>
    <span className={`text-xs ${warning ? 'text-rose-400/70' : 'text-slate-500'}`}>{label}</span>
  </div>
);

export default PremiumDashboard;
