/**
 * 🧠 Cognito OS — Living Cognitive Plan
 * =====================================
 * 
 * Philosophy: Adaptive, not fixed. Supportive, not demanding.
 * 
 * This is NOT a rigid schedule. It's a gentle guide that adapts
 * to the student's pace and energy.
 * 
 * Principles:
 * - No pressure language ("must", "deadline", "stay focused")
 * - AI may say "Nothing urgent today" or "You're safe to go slow"
 * - Today's suggestions are optional, not mandatory
 * - Near-term adapts based on learning gaps
 * - Long-term is tracked silently, surfaced only when helpful
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  Target, 
  Brain, 
  Coffee, 
  CheckCircle, 
  Clock, 
  Sparkles,
  RefreshCw,
  Calendar,
  Flame,
  RotateCcw,
  Zap,
  Loader,
  ChevronRight,
  Lightbulb,
  TrendingUp,
  Play
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Block type configuration - Professional color scheme
const BLOCK_CONFIG = {
  revision: {
    icon: RotateCcw,
    gradient: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-700 dark:text-blue-300',
    badge: 'bg-blue-500',
    label: 'Revision'
  },
  deep_focus: {
    icon: Target,
    gradient: 'from-violet-500 to-purple-500',
    bg: 'bg-violet-50 dark:bg-violet-950/30',
    border: 'border-violet-200 dark:border-violet-800',
    text: 'text-violet-700 dark:text-violet-300',
    badge: 'bg-violet-500',
    label: 'Deep Focus'
  },
  new_learning: {
    icon: BookOpen,
    gradient: 'from-emerald-500 to-teal-500',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30',
    border: 'border-emerald-200 dark:border-emerald-800',
    text: 'text-emerald-700 dark:text-emerald-300',
    badge: 'bg-emerald-500',
    label: 'New Learning'
  },
  practice: {
    icon: Brain,
    gradient: 'from-orange-500 to-amber-500',
    bg: 'bg-orange-50 dark:bg-orange-950/30',
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-700 dark:text-orange-300',
    badge: 'bg-orange-500',
    label: 'Practice'
  },
  break: {
    icon: Coffee,
    gradient: 'from-slate-400 to-slate-500',
    bg: 'bg-slate-50 dark:bg-slate-800/50',
    border: 'border-slate-200 dark:border-slate-700',
    text: 'text-slate-600 dark:text-slate-400',
    badge: 'bg-slate-500',
    label: 'Break'
  },
  quick_review: {
    icon: Sparkles,
    gradient: 'from-indigo-500 to-blue-500',
    bg: 'bg-indigo-50 dark:bg-indigo-950/30',
    border: 'border-indigo-200 dark:border-indigo-800',
    text: 'text-indigo-700 dark:text-indigo-300',
    badge: 'bg-indigo-500',
    label: 'Quick Review'
  }
};

/**
 * Progress Ring - Clean SVG circle
 */
const ProgressRing = ({ progress, size = 140 }) => {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-700"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{ strokeDasharray: circumference }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{Math.round(progress)}%</span>
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Complete</span>
      </div>
    </div>
  );
};

/**
 * Study Block Card - Professional design
 */
const StudyBlockCard = ({ block, index, onComplete, isActive }) => {
  const config = BLOCK_CONFIG[block.block_type] || BLOCK_CONFIG.practice;
  const Icon = config.icon;
  const isCompleted = block.completed;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`relative p-4 rounded-xl border transition-all duration-200 ${
        isCompleted 
          ? 'bg-emerald-950/40 border-emerald-700/50' 
          : isActive 
            ? `bg-slate-800/80 border-indigo-500/50 ring-2 ring-indigo-500/20`
            : `bg-slate-800/50 border-slate-700/50 hover:border-slate-600`
      }`}
    >
      {/* Completed badge */}
      {isCompleted && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg">
          <CheckCircle className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${config.gradient} flex items-center justify-center flex-shrink-0 shadow-sm`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className={`px-2 py-0.5 rounded-md text-xs font-semibold text-white ${config.badge}`}>
              {config.label}
            </span>
            <span className="flex items-center gap-1 text-sm text-slate-400">
              <Clock className="w-3.5 h-3.5" />
              {block.duration_minutes} min
            </span>
            {block.subject && (
              <span className="text-xs text-slate-500">• {block.subject}</span>
            )}
          </div>
          
          {/* Title */}
          <h4 className={`font-semibold text-white ${isCompleted ? 'line-through opacity-60' : ''}`}>
            {block.topic}
          </h4>
          
          {/* Description */}
          {block.description && (
            <p className="text-sm text-slate-400 mt-1 line-clamp-2">
              {block.description}
            </p>
          )}
          
          {/* Tip */}
          {block.tips && block.tips.length > 0 && !isCompleted && (
            <div className="mt-3 p-2.5 bg-amber-950/30 border border-amber-700/30 rounded-lg flex items-start gap-2">
              <Lightbulb className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-amber-200">{block.tips[0]}</p>
            </div>
          )}
          
          {/* Footer */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-700/50">
            <span className="flex items-center gap-1.5 text-sm font-semibold text-amber-400">
              <Zap className="w-4 h-4" />
              +{block.xp_reward || 0} XP
            </span>
            
            {!isCompleted && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onComplete(index)}
                className={`px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r ${config.gradient} shadow-sm hover:shadow-md transition-shadow flex items-center gap-1.5`}
              >
                <CheckCircle className="w-4 h-4" />
                Complete
              </motion.button>
            )}
            
            {isCompleted && (
              <span className="flex items-center gap-1.5 text-sm font-semibold text-emerald-400">
                <CheckCircle className="w-4 h-4" />
                Completed
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Main Study Planner Component
 */
const StudyPlanner = ({ onStartStudy }) => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [activeBlockIndex, setActiveBlockIndex] = useState(0);
  const [recommendations, setRecommendations] = useState([]);
  const [initialized, setInitialized] = useState(false);
  
  // Study plan customization options
  const [studyHoursOption, setStudyHoursOption] = useState(4);
  const [selectedSubject, setSelectedSubject] = useState('All');
  
  const SUBJECT_OPTIONS = ['All', 'Physics', 'Chemistry', 'Mathematics', 'Biology'];
  const HOURS_OPTIONS = [2, 3, 4, 5, 6];
  
  // Generate new plan with customization options
  const generateNewPlan = useCallback(async (hours = null, subject = null) => {
    try {
      setGenerating(true);
      setError(null);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const finalHours = hours || studyHoursOption;
      const finalSubject = subject || selectedSubject;
      
      const requestBody = {
        available_hours: finalHours,
        energy_pattern: new Date().getHours() < 12 ? 'morning' : 'evening'
      };
      
      // Add subject filter if not "All"
      if (finalSubject && finalSubject !== 'All') {
        requestBody.preferred_subjects = [finalSubject];
      }
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data && data.blocks) {
          setPlan(data);
          setActiveBlockIndex(0);
          return true;
        }
      }
    } catch (err) {
      console.error('Error generating plan:', err);
      setError('Failed to generate plan');
    } finally {
      setGenerating(false);
    }
    return false;
  }, [studyHoursOption, selectedSubject]);
  
  // Fetch today's plan
  const fetchPlan = useCallback(async (autoGenerate = true) => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/today`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data && data.blocks && data.blocks.length > 0) {
          setPlan(data);
          const firstIncomplete = data.blocks?.findIndex(b => !b.completed) ?? 0;
          setActiveBlockIndex(Math.max(0, firstIncomplete));
          setLoading(false);
          return true;
        } else if (autoGenerate && !initialized) {
          setInitialized(true);
          setLoading(false);
          await generateNewPlan(4);
          return true;
        }
      } else if (response.status === 404 && autoGenerate && !initialized) {
        setInitialized(true);
        setLoading(false);
        await generateNewPlan(4);
        return true;
      }
    } catch (err) {
      console.error('Error fetching plan:', err);
      setError('Failed to load plan');
    } finally {
      setLoading(false);
    }
    return false;
  }, [initialized, generateNewPlan]);
  
  // Fetch recommendations
  const fetchRecommendations = useCallback(async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/study-planner/recommendations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    }
  }, []);
  
  // Handle block completion
  const handleCompleteBlock = async (blockIndex) => {
    if (!plan || !plan.blocks) return;
    
    // Optimistic update
    const updatedBlocks = plan.blocks.map((b, i) => 
      i === blockIndex ? { ...b, completed: true } : b
    );
    const completedCount = updatedBlocks.filter(b => b.completed).length;
    const newCompletion = (completedCount / updatedBlocks.length) * 100;
    
    setPlan(prev => ({
      ...prev,
      blocks: updatedBlocks,
      completion_percentage: newCompletion
    }));
    
    const nextIncomplete = updatedBlocks.findIndex((b, i) => i > blockIndex && !b.completed);
    if (nextIncomplete !== -1) setActiveBlockIndex(nextIncomplete);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      await fetch(`${BACKEND_URL}/api/study-planner/complete-block`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ block_index: blockIndex })
      });
    } catch (err) {
      fetchPlan(false);
    }
  };
  
  // Load on mount
  useEffect(() => {
    fetchPlan(true);
    fetchRecommendations();
  }, []);
  
  // Loading state
  if (loading || generating) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700/50 p-8">
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-14 h-14 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin mb-4" />
              <p className="text-slate-300 font-medium">
                {generating ? 'Preparing some gentle suggestions...' : 'Loading your plan...'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Error/Empty state
  if (error || !plan || !plan.blocks || plan.blocks.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700/50 p-8">
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-gradient-to-br from-violet-500/20 to-indigo-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-violet-500/30">
                <Calendar className="w-10 h-10 text-violet-400" />
              </div>
              <h3 className="text-xl font-medium text-white mb-3">Nothing urgent today</h3>
              <p className="text-slate-400 mb-8 max-w-md mx-auto">
                You're safe to go at your own pace. When you're ready, I can suggest some gentle study ideas based on where you are in your learning journey.
              </p>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => generateNewPlan(4)}
                disabled={generating}
                className="px-6 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-medium transition-colors flex items-center gap-2 mx-auto"
              >
                <Sparkles className="w-4 h-4" />
                Show me some ideas
              </motion.button>
              {error && (
                <p className="mt-4 text-red-400 text-sm">{error}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  const studyHours = Math.round((plan?.total_study_minutes || 0) / 60 * 10) / 10;
  const sessionCount = plan?.blocks?.length || 0;
  const xpTarget = plan?.xp_target || 0;
  const progress = plan?.completion_percentage || 0;
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700/50 overflow-hidden">
          {/* Header - Premium gradient */}
          <div className="bg-gradient-to-r from-violet-600 via-indigo-600 to-purple-600 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 text-white/80 text-sm mb-1">
              <Calendar className="w-4 h-4" />
              {plan?.date ? new Date(plan.date).toLocaleDateString('en-IN', { 
                weekday: 'long', 
                day: 'numeric', 
                month: 'long' 
              }) : 'Today'}
            </div>
            <h2 className="text-xl font-medium text-white">Gentle Suggestions for Today</h2>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Subject Filter */}
            <select
              value={selectedSubject}
              onChange={(e) => {
                setSelectedSubject(e.target.value);
                // Auto-regenerate with new subject
                generateNewPlan(studyHoursOption, e.target.value);
              }}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium border border-white/20 focus:outline-none focus:ring-2 focus:ring-violet-500/50 backdrop-blur-sm cursor-pointer"
            >
              {SUBJECT_OPTIONS.map(subj => (
                <option key={subj} value={subj} className="bg-slate-800 text-white">
                  {subj === 'All' ? '📚 All Subjects' : `${subj}`}
                </option>
              ))}
            </select>
            
            {/* Hours Selector */}
            <select
              value={studyHoursOption}
              onChange={(e) => {
                const hours = parseInt(e.target.value);
                setStudyHoursOption(hours);
                generateNewPlan(hours, selectedSubject);
              }}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium border border-white/20 focus:outline-none focus:ring-2 focus:ring-violet-500/50 backdrop-blur-sm cursor-pointer"
            >
              {HOURS_OPTIONS.map(h => (
                <option key={h} value={h} className="bg-slate-800 text-white">
                  {h} hours
                </option>
              ))}
            </select>
            
            {/* Regenerate Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => generateNewPlan()}
              disabled={generating}
              className="px-4 py-2 bg-white/15 hover:bg-white/25 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors backdrop-blur-sm"
            >
              <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              Regenerate
            </motion.button>
          </div>
        </div>
        
        {/* Stats - Minimal, calmer language */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
            <div className="text-lg font-medium text-white">{studyHours}h</div>
            <div className="text-xs text-white/60">suggested time</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
            <div className="text-lg font-medium text-white">{sessionCount}</div>
            <div className="text-xs text-white/60">ideas</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
            <div className="text-lg font-medium text-white flex items-center justify-center gap-1">
              <Zap className="w-4 h-4" />{xpTarget}
            </div>
            <div className="text-xs text-white/60">potential XP</div>
          </div>
        </div>
        
        {/* Note: Exam countdown removed - pressure language not aligned with Cognito OS philosophy */}
      </div>
      
      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Progress & Goals */}
          <div className="space-y-6">
            {/* Progress Ring with Encouragement */}
            <div className="flex flex-col items-center p-4 bg-slate-900/50 rounded-xl border border-slate-700/50">
              <ProgressRing progress={progress} size={140} />
              <p className="text-sm font-medium text-slate-400 mt-2">Daily Progress</p>
              {/* Gentle, non-pressure encouragement */}
              <p className="text-xs text-center mt-2 px-2 text-slate-500">
                {progress === 0 && (
                  <span>Take your time. I'm here when you're ready.</span>
                )}
                {progress > 0 && progress < 25 && (
                  <span>You've started. That's what matters.</span>
                )}
                {progress >= 25 && progress < 50 && (
                  <span>Making good progress. Keep going if you'd like.</span>
                )}
                {progress >= 50 && progress < 75 && (
                  <span>You're doing well. No rush to finish.</span>
                )}
                {progress >= 75 && progress < 100 && (
                  <span>Nearly there, if you want to continue.</span>
                )}
                {progress >= 100 && (
                  <span>You've completed today's suggestions. Well done.</span>
                )}
              </p>
            </div>
            
            {/* Today's Ideas - Optional, not goals */}
            {plan?.daily_goals && plan.daily_goals.length > 0 && (
              <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                <h3 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-violet-400" />
                  <span>Today's Ideas</span>
                  <span className="text-xs text-slate-600 font-normal ml-1">(optional)</span>
                </h3>
                <ul className="space-y-2.5">
                  {plan.daily_goals.map((goal, i) => {
                    // Determine if goal is completed based on related blocks
                    const isCompleted = (() => {
                      const goalLower = goal.toLowerCase();
                      if (goalLower.includes('revision') && plan.blocks?.some(b => b.block_type === 'revision' && b.completed)) return true;
                      if (goalLower.includes('mastery') && plan.blocks?.some(b => b.block_type === 'deep_focus' && b.completed)) return true;
                      if (goalLower.includes('learn') && plan.blocks?.some(b => b.block_type === 'new_learning' && b.completed)) return true;
                      if (goalLower.includes('practice') && plan.blocks?.some(b => b.block_type === 'practice' && b.completed)) return true;
                      if (goalLower.includes('streak') && progress > 0) return true;
                      return false;
                    })();
                    
                    return (
                      <li 
                        key={i} 
                        className={`flex items-start gap-2.5 text-sm transition-all duration-300 ${
                          isCompleted ? 'text-emerald-400' : 'text-slate-300'
                        }`}
                      >
                        <CheckCircle 
                          className={`w-4 h-4 flex-shrink-0 mt-0.5 transition-colors ${
                            isCompleted 
                              ? 'text-emerald-400' 
                              : 'text-slate-600'
                          }`} 
                        />
                        <span className={isCompleted ? 'line-through opacity-70' : ''}>
                          {goal}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
            
            {/* Motivational Quote */}
            {plan?.motivational_quote && (
              <div className="p-4 bg-gradient-to-br from-amber-950/40 to-orange-950/40 rounded-xl border border-amber-700/30">
                <Sparkles className="w-5 h-5 text-amber-400 mb-2" />
                <p className="text-sm text-slate-300 italic leading-relaxed">
                  "{plan.motivational_quote}"
                </p>
              </div>
            )}
            
            {/* AI Recommendations - Enhanced with actions */}
            {recommendations.length > 0 && (
              <div className="bg-gradient-to-br from-indigo-950/30 to-violet-950/30 rounded-xl p-4 border border-indigo-700/30">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  AI Insights
                  <span className="ml-auto text-xs text-indigo-400/70 font-normal">
                    Personalized for you
                  </span>
                </h3>
                <div className="space-y-2.5">
                  {recommendations.slice(0, 4).map((rec, i) => (
                    <motion.div 
                      key={i} 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className={`flex items-start gap-3 p-3 rounded-lg border transition-all cursor-pointer hover:scale-[1.02] ${
                        rec.type === 'urgent' || rec.type === 'exam_countdown'
                          ? 'bg-red-950/40 border-red-700/40 hover:bg-red-950/60'
                          : rec.type === 'focus'
                          ? 'bg-amber-950/30 border-amber-700/30 hover:bg-amber-950/50'
                          : rec.type === 'achievement'
                          ? 'bg-emerald-950/30 border-emerald-700/30 hover:bg-emerald-950/50'
                          : 'bg-slate-800/50 border-slate-700/30 hover:bg-slate-800/70'
                      }`}
                      onClick={() => {
                        // Handle recommendation action
                        if (rec.action && onStartStudy) {
                          onStartStudy(rec.action);
                        }
                      }}
                    >
                      <span className="text-xl">{rec.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{rec.title}</p>
                        {rec.description && (
                          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{rec.description}</p>
                        )}
                      </div>
                      {rec.action && (
                        <span className="text-xs text-indigo-400 font-medium whitespace-nowrap">
                          {rec.action} →
                        </span>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Right: Study Sessions */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-indigo-400" />
                Study Sessions
                <span className="ml-2 text-xs text-slate-500 font-normal">
                  {plan?.blocks?.filter(b => b.block_type !== 'break').length || 0} sessions
                </span>
              </h3>
              
              {/* Start Study CTA when nothing completed */}
              {progress === 0 && plan?.blocks?.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    // Find first non-break block
                    const firstSession = plan.blocks?.find(b => b.block_type !== 'break');
                    if (onStartStudy && firstSession) {
                      onStartStudy({
                        topic: firstSession.topic,
                        subject: firstSession.subject,
                        duration: firstSession.duration_minutes
                      });
                    }
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <Play className="w-4 h-4" />
                  Start First Session
                </motion.button>
              )}
            </div>
            
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {plan?.blocks?.map((block, index) => (
                <StudyBlockCard
                  key={index}
                  block={block}
                  index={index}
                  isActive={index === activeBlockIndex}
                  onComplete={handleCompleteBlock}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
        </div>
      </div>
    </div>
  );
};

export default StudyPlanner;
