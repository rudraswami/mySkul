/**
 * 📚 Study Planner - PROFESSIONAL REDESIGN
 * =========================================
 * 
 * Clean, modern design with:
 * - Subtle gradients (not garish)
 * - Consistent typography
 * - Better visual hierarchy
 * - Professional card styling
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
  TrendingUp
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
          className="text-slate-200 dark:text-slate-700"
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
        <span className="text-3xl font-bold text-slate-900 dark:text-white">{Math.round(progress)}%</span>
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Complete</span>
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
      className={`relative p-4 rounded-xl border-2 transition-all duration-200 ${
        isCompleted 
          ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-700' 
          : isActive 
            ? `${config.bg} ${config.border} ring-2 ring-indigo-500/20`
            : `bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600`
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
            <span className="flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400">
              <Clock className="w-3.5 h-3.5" />
              {block.duration_minutes} min
            </span>
            {block.subject && (
              <span className="text-xs text-slate-400 dark:text-slate-500">• {block.subject}</span>
            )}
          </div>
          
          {/* Title */}
          <h4 className={`font-semibold text-slate-900 dark:text-white ${isCompleted ? 'line-through opacity-60' : ''}`}>
            {block.topic}
          </h4>
          
          {/* Description */}
          {block.description && (
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
              {block.description}
            </p>
          )}
          
          {/* Tip */}
          {block.tips && block.tips.length > 0 && !isCompleted && (
            <div className="mt-3 p-2.5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg flex items-start gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800 dark:text-amber-200">{block.tips[0]}</p>
            </div>
          )}
          
          {/* Footer */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
            <span className="flex items-center gap-1.5 text-sm font-semibold text-amber-600 dark:text-amber-400">
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
              <span className="flex items-center gap-1.5 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
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
  
  // Generate new plan
  const generateNewPlan = useCallback(async (hours = 4) => {
    try {
      setGenerating(true);
      setError(null);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          available_hours: hours,
          energy_pattern: new Date().getHours() < 12 ? 'morning' : 'evening'
        })
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
  }, []);
  
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
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
          <p className="text-slate-600 dark:text-slate-400 font-medium">
            {generating ? 'Creating your study plan...' : 'Loading study plan...'}
          </p>
        </div>
      </div>
    );
  }
  
  // Error/Empty state
  if (error || !plan || !plan.blocks || plan.blocks.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Calendar className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Today's Study Plan</h3>
          <p className="text-slate-500 dark:text-slate-400 mb-6">Let's create your personalized study schedule</p>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => generateNewPlan(4)}
            disabled={generating}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-600 text-white rounded-xl font-semibold shadow-lg shadow-indigo-500/25 hover:shadow-xl transition-shadow flex items-center gap-2 mx-auto"
          >
            <Sparkles className="w-5 h-5" />
            Generate Study Plan
          </motion.button>
        </div>
      </div>
    );
  }
  
  const studyHours = Math.round((plan?.total_study_minutes || 0) / 60 * 10) / 10;
  const sessionCount = plan?.blocks?.length || 0;
  const xpTarget = plan?.xp_target || 0;
  const progress = plan?.completion_percentage || 0;
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Header - Clean gradient */}
      <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 p-6">
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
            <h2 className="text-2xl font-bold text-white">Today's Study Plan</h2>
          </div>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => generateNewPlan(4)}
            disabled={generating}
            className="px-4 py-2 bg-white/15 hover:bg-white/25 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors backdrop-blur-sm"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
            Regenerate
          </motion.button>
        </div>
        
        {/* Stats - Clean cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white">{studyHours}h</div>
            <div className="text-xs text-white/70 font-medium uppercase tracking-wide">Study Time</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white">{sessionCount}</div>
            <div className="text-xs text-white/70 font-medium uppercase tracking-wide">Sessions</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white flex items-center justify-center gap-1">
              <Zap className="w-5 h-5" />{xpTarget}
            </div>
            <div className="text-xs text-white/70 font-medium uppercase tracking-wide">XP Target</div>
          </div>
        </div>
        
        {/* Exam countdown */}
        {plan?.exam_countdown && (
          <div className="mt-4 bg-red-500/20 backdrop-blur-sm rounded-lg p-3 flex items-center gap-3">
            <Flame className="w-5 h-5 text-amber-300 animate-pulse" />
            <span className="text-white font-medium">{plan.exam_countdown} days until exam - Stay focused!</span>
          </div>
        )}
      </div>
      
      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Progress & Goals */}
          <div className="space-y-6">
            {/* Progress Ring */}
            <div className="flex flex-col items-center p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl">
              <ProgressRing progress={progress} size={140} />
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mt-2">Daily Progress</p>
            </div>
            
            {/* Today's Goals */}
            {plan?.daily_goals && plan.daily_goals.length > 0 && (
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-violet-500" />
                  Today's Goals
                </h3>
                <ul className="space-y-2">
                  {plan.daily_goals.map((goal, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <CheckCircle className="w-4 h-4 text-slate-300 dark:text-slate-600 flex-shrink-0 mt-0.5" />
                      <span>{goal}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Motivational Quote */}
            {plan?.motivational_quote && (
              <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 rounded-xl border border-amber-200 dark:border-amber-800">
                <Sparkles className="w-5 h-5 text-amber-500 mb-2" />
                <p className="text-sm text-slate-700 dark:text-slate-300 italic leading-relaxed">
                  "{plan.motivational_quote}"
                </p>
              </div>
            )}
            
            {/* AI Recommendations */}
            {recommendations.length > 0 && (
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-500" />
                  AI Insights
                </h3>
                <div className="space-y-2">
                  {recommendations.slice(0, 3).map((rec, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
                      <span className="text-lg">{rec.icon}</span>
                      <div>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{rec.title}</p>
                        {rec.description && (
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{rec.description}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Right: Study Sessions */}
          <div className="lg:col-span-2">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-500" />
              Study Sessions
            </h3>
            
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
  );
};

export default StudyPlanner;
