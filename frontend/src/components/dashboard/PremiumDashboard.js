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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * 🚀 DRON AI — Intelligence Dashboard v1.0
 * ==================================================
 * 
 * Design System Compliant:
 * - Brand: DRON AI (Sathi is AI persona)
 * - Theme: Dark with calm content areas
 * - All data API-wired
 * 
 * DATA SOURCES:
 * - /api/user/progress → XP, Level, Streak, Badges
 * - /api/analytics/subject-progress → Subject Mastery
 * - /api/cognitive/recommendations → AI Recommendations  
 * - /api/study-planner/today → Today's Plan
 * - /api/subscription/usage → AI Chat Limits
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

  // Fetch ALL data from APIs
  useEffect(() => {
    const loadAllData = async () => {
      const [progressData, masteryData, planData, usageRes, recsData] = await Promise.all([
        fetchWithAuth('/api/user/progress'),
        fetchWithAuth('/api/analytics/subject-progress'),
        fetchWithAuth('/api/study-planner/today'),
        fetchWithAuth('/api/subscription/usage'),
        fetchWithAuth('/api/cognitive/recommendations')
      ]);

      setProgress(progressData);
      setSubjectMastery(masteryData);
      if (planData?.blocks?.length > 0) setStudyPlan(planData);
      setUsageData(usageRes);
      setAiRecommendation(recsData);
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

  // Sathi contextual message
  const sathiMessage = useMemo(() => {
    if (streak === 0) return "Let's start your learning streak today! 🚀";
    if (streak >= 7) return `${streak} days strong! I'm proud of you! 💪`;
    if (aiChatsLeft < 3) return "Running low on chats - make them count!";
    if (focus.source === 'ai') return "I found something important for you!";
    return "I'm here whenever you need help! 🧠";
  }, [streak, aiChatsLeft, focus.source]);

  // Exam countdown (configurable - for now showing JEE date)
  const examCountdown = useMemo(() => {
    const jeeDate = new Date('2025-04-15'); // JEE Mains approximate
    const today = new Date();
    const diff = Math.ceil((jeeDate - today) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : null;
  }, []);

  // Loading State
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-4">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}>
          <Loader2 className="w-10 h-10 text-violet-500" />
        </motion.div>
        <p className="text-slate-400 text-sm">Loading your intelligence dashboard...</p>
      </div>
    );
  }

  // Check if new user (zero state)
  const isNewUser = xp === 0 && streak === 0 && badgesEarned.length === 0;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Subtle Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-600/10 blur-[120px] rounded-full" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 p-6 lg:p-10 max-w-7xl mx-auto space-y-8">
        
        {/* ============ HEADER ============ */}
        <header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{greeting.emoji}</span>
              <h1 className="text-2xl lg:text-3xl font-bold text-white">
                {greeting.text}, <span className="text-violet-400">{firstName}</span>
              </h1>
            </div>
            <p className="text-slate-400">
              {isNewUser 
                ? "Welcome to DRON AI! Let's start your learning journey."
                : "Let's continue building your knowledge today."
              }
            </p>
          </div>

          {/* Stats Pills */}
          <div className="flex items-center gap-3 flex-wrap">
            <StatPill 
              icon={Zap} 
              value={xp} 
              label={isNewUser ? "Start earning!" : "XP"} 
              color="amber" 
              highlight={xp > 0}
            />
            <StatPill 
              icon={Flame} 
              value={streak} 
              label={streak === 1 ? "day" : "days"} 
              color="orange"
              highlight={streak > 0}
            />
            <StatPill 
              icon={MessageCircle} 
              value={aiChatsLeft} 
              label="AI chats" 
              color="violet"
              warning={aiChatsLeft < 3}
            />
          </div>
        </header>

        {/* ============ EXAM COUNTDOWN (if applicable) ============ */}
        {examCountdown && examCountdown < 120 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20"
          >
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-amber-400" />
              <span className="text-sm text-amber-200">
                <strong>JEE Mains</strong> in <span className="font-bold text-amber-400">{examCountdown} days</span>
              </span>
            </div>
            <button 
              onClick={() => navigate('/study-planner')}
              className="text-xs text-amber-400 hover:text-amber-300 font-medium"
            >
              View Study Plan →
            </button>
          </motion.div>
        )}

        {/* ============ AI ATTRIBUTION BANNER ============ */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-800/60"
        >
          <div className="p-2 rounded-lg bg-violet-500/10">
            <Brain className="w-4 h-4 text-violet-400" />
          </div>
          <p className="text-sm text-slate-400">
            <span className="text-violet-400 font-medium">DRON AI</span>
            {' '}analyzed your learning patterns
            {focus.source === 'study_plan' && ' and synced with your study plan'}
            {focus.source === 'ai' && ' and found an important focus area'}
            {focus.source === 'analysis' && ' to suggest your next focus'}
          </p>
        </motion.div>

        {/* ============ MAIN GRID ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          
          {/* LEFT COLUMN: Focus + Quick Actions */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* PRIMARY FOCUS CARD */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative p-6 lg:p-8 rounded-3xl bg-gradient-to-br from-slate-900 to-slate-900/50 border border-slate-800/60 overflow-hidden"
            >
              {/* Accent Border */}
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500" />
              
              {/* Content */}
              <div className="relative z-10 flex flex-col lg:flex-row lg:items-center gap-6 lg:gap-10">
                
                {/* Text Content */}
                <div className="flex-1 space-y-5">
                  {/* Badge Row */}
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="px-3 py-1.5 rounded-full bg-violet-500/15 text-violet-400 text-xs font-semibold border border-violet-500/30">
                      🎯 Recommended Focus
                    </span>
                    <span className="flex items-center gap-1.5 text-slate-500 text-sm">
                      <Clock className="w-4 h-4" />
                      {focus.duration} min
                    </span>
                    <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-medium">
                      +{focus.xpReward} XP
                    </span>
                  </div>

                  {/* Title */}
                  <div>
                    <p className="text-violet-400 text-sm font-medium mb-1">{focus.subject}</p>
                    <h2 className="text-2xl lg:text-3xl font-bold text-white leading-tight">
                      {focus.topic}
                    </h2>
                  </div>

                  {/* AI Reason - THE INTELLIGENCE */}
                  <div className="flex items-start gap-3 p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                    <Info className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
                    <p className="text-slate-300 text-sm leading-relaxed">
                      {focus.reason}
                    </p>
                  </div>

                  {/* CTA Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => navigate(`/tutor?topic=${encodeURIComponent(focus.topic)}&subject=${encodeURIComponent(focus.subject)}`)}
                    className="inline-flex items-center gap-3 px-6 py-3.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-violet-500/25 transition-all"
                  >
                    <Play className="w-5 h-5" fill="currentColor" />
                    Start Learning
                    <ChevronRight className="w-4 h-4" />
                  </motion.button>
                </div>

                {/* Sathi Co-Pilot */}
                <div className="hidden lg:flex flex-col items-center gap-4">
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    className="relative cursor-pointer group"
                    onClick={() => navigate('/tutor')}
                  >
                    <div className="absolute inset-0 bg-violet-500 blur-2xl opacity-30 group-hover:opacity-50 transition-opacity rounded-full" />
                    <div className="relative w-28 h-28 rounded-3xl bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 flex items-center justify-center backdrop-blur-sm group-hover:border-violet-500/50 transition-colors">
                      <Brain className="w-14 h-14 text-violet-400 group-hover:text-violet-300 transition-colors" strokeWidth={1} />
                    </div>
                  </motion.div>
                  <p className="text-sm text-slate-400 text-center max-w-[140px]">
                    {sathiMessage}
                  </p>
                </div>
              </div>
            </motion.div>

            {/* QUICK ACTIONS */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { icon: MessageCircle, label: 'Ask Sathi', desc: 'AI Tutor', color: 'violet', path: '/tutor' },
                { icon: Camera, label: 'Scan', desc: 'Photo Solve', color: 'blue', path: '/tutor?mode=scan' },
                { icon: BookOpen, label: 'Materials', desc: 'Study Notes', color: 'emerald', path: '/materials' },
                { icon: Target, label: 'Practice', desc: 'Mock Tests', color: 'rose', path: '/practice' },
              ].map((action, i) => (
                <motion.button
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.05 }}
                  whileHover={{ y: -4 }}
                  onClick={() => navigate(action.path)}
                  className="flex flex-col items-center gap-3 p-5 rounded-2xl bg-slate-900/50 border border-slate-800/60 hover:border-slate-700/60 hover:bg-slate-900/80 transition-all group"
                >
                  <div className={`p-3 rounded-xl bg-${action.color}-500/10 group-hover:bg-${action.color}-500/20 transition-colors`}>
                    <action.icon className={`w-5 h-5 text-${action.color}-400`} strokeWidth={1.5} />
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-white text-sm">{action.label}</p>
                    <p className="text-xs text-slate-500">{action.desc}</p>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* TODAY'S SCHEDULE */}
            {studyPlan?.blocks && studyPlan.blocks.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/60"
              >
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-violet-400" />
                    <h3 className="font-semibold text-white">Today's Schedule</h3>
                  </div>
                  <button 
                    onClick={() => navigate('/study-planner')}
                    className="text-xs text-violet-400 hover:text-violet-300"
                  >
                    View Full Plan
                  </button>
                </div>
                
                <div className="space-y-3">
                  {studyPlan.blocks.slice(0, 4).map((block, i) => (
                    <div 
                      key={i}
                      className={`flex items-center gap-4 p-3 rounded-xl transition-all ${
                        block.completed 
                          ? 'bg-emerald-500/5 border border-emerald-500/20' 
                          : i === 0 
                            ? 'bg-violet-500/10 border border-violet-500/30' 
                            : 'bg-slate-800/30 border border-transparent'
                      }`}
                    >
                      <div className={`w-2 h-2 rounded-full ${
                        block.completed ? 'bg-emerald-400' : i === 0 ? 'bg-violet-400 animate-pulse' : 'bg-slate-600'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium truncate ${block.completed ? 'text-emerald-400 line-through' : 'text-white'}`}>
                          {block.topic || block.block_type?.replace('_', ' ')}
                        </p>
                        <p className="text-xs text-slate-500">{block.subject} • {block.duration_minutes}min</p>
                      </div>
                      {block.completed && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                      {i === 0 && !block.completed && (
                        <span className="px-2 py-1 text-[10px] font-semibold text-violet-400 bg-violet-500/20 rounded-full">
                          NOW
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* NEW USER ONBOARDING (Zero State) */}
            {isNewUser && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-6 rounded-2xl bg-gradient-to-br from-violet-600/10 to-indigo-600/10 border border-violet-500/20"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-violet-500/20">
                    <Rocket className="w-6 h-6 text-violet-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1">Welcome to DRON AI! 🎉</h3>
                    <p className="text-sm text-slate-400 mb-4">
                      Complete your first study session to start earning XP and building your streak.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { icon: '📚', text: 'Complete 1 session', done: false },
                        { icon: '🔥', text: 'Start a streak', done: false },
                        { icon: '🏆', text: 'Earn first badge', done: false },
                      ].map((task, i) => (
                        <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 text-xs text-slate-400">
                          <span>{task.icon}</span>
                          <span>{task.text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* RIGHT COLUMN: Stats & Wellness */}
          <div className="space-y-6">
            
            {/* WELLNESS CARD */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/60"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <Heart className="w-4 h-4 text-rose-400" />
                  How You're Doing
                </h3>
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold bg-${wellness.color}-500/15 text-${wellness.color}-400`}>
                  {wellness.status}
                </span>
              </div>
              
              <div className="flex items-start gap-4">
                <div className={`p-4 rounded-xl bg-${wellness.color}-500/10`}>
                  <wellness.icon className={`w-8 h-8 text-${wellness.color}-400`} strokeWidth={1.5} />
                </div>
                <div className="flex-1">
                  <p className="text-slate-300 text-sm mb-1">{wellness.message}</p>
                  <p className="text-xs text-slate-500">💡 {wellness.tip}</p>
                </div>
              </div>
            </motion.div>

            {/* SUBJECT PROGRESS - FROM API */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/60"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-violet-400" />
                  Subject Progress
                </h3>
                <button 
                  onClick={() => navigate('/progress')}
                  className="text-xs text-violet-400 hover:text-violet-300"
                >
                  Details
                </button>
              </div>
              
              <div className="space-y-5">
                {subjects.map((subject, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-300">{subject.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-white">
                          {subject.score > 0 ? `${subject.score}%` : '—'}
                        </span>
                        {subject.score > 0 && (
                          <>
                            <span className={`text-xs ${subject.trend === 'up' ? 'text-emerald-400' : subject.trend === 'down' ? 'text-amber-400' : 'text-slate-500'}`}>
                              {subject.change}
                            </span>
                            {subject.trend === 'up' && <TrendingUp className="w-3 h-3 text-emerald-400" />}
                            {subject.trend === 'down' && <TrendingDown className="w-3 h-3 text-amber-400" />}
                          </>
                        )}
                      </div>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.max(subject.score, 0)}%` }}
                        transition={{ duration: 1, delay: i * 0.2, ease: "easeOut" }}
                        className={`h-full rounded-full ${
                          subject.color === 'violet' ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500' :
                          subject.color === 'amber' ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
                          'bg-gradient-to-r from-emerald-500 to-teal-500'
                        }`}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* No data state */}
              {subjects.every(s => s.score === 0) && (
                <div className="mt-4 p-3 rounded-xl bg-slate-800/30 border border-slate-700/30">
                  <p className="text-xs text-slate-500 text-center">
                    Complete study sessions to track your progress
                  </p>
                </div>
              )}
            </motion.div>

            {/* ACHIEVEMENTS - FROM API */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/60"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  Achievements
                </h3>
                <span className="text-xs text-slate-500">{badgesEarned.length} earned</span>
              </div>
              
              {badgesEarned.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {badgesEarned.slice(0, 6).map((badge, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/30"
                      title={badge.name || badge}
                    >
                      <span className="text-lg">{badge.emoji || '🏆'}</span>
                      <span className="text-xs text-slate-400">{badge.name || badge}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <Trophy className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                  <p className="text-xs text-slate-500">
                    Complete sessions to earn badges!
                  </p>
                </div>
              )}
            </motion.div>

            {/* UPGRADE PROMPT (only for free users with low chats) */}
            {tier === 'Free' && aiChatsLeft < 5 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-violet-500/20 blur-2xl rounded-full" />
                <div className="relative z-10">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-violet-400" />
                    <span className="text-sm font-semibold text-white">Need More AI Chats?</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-3">
                    Only {aiChatsLeft} chats left. Upgrade for unlimited access.
                  </p>
                  <button 
                    onClick={() => navigate('/subscription')}
                    className="w-full py-2.5 text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 rounded-xl transition-colors"
                  >
                    Upgrade Plan
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* ============ FOOTER ============ */}
        <footer className="flex items-center justify-center gap-6 py-6 opacity-40">
          <span className="text-xs text-slate-500">DRON AI • Your Intelligent Study Partner</span>
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
