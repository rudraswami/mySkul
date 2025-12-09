/**
 * 📚 Smart Study Planner Component
 * =================================
 * 
 * AI-powered daily study plan display with:
 * - Personalized study blocks
 * - Progress tracking
 * - XP rewards
 * - Motivational elements
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  Target, 
  Brain, 
  Coffee, 
  CheckCircle, 
  Clock, 
  Sparkles,
  ChevronRight,
  RefreshCw,
  Calendar,
  Flame,
  Award,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Moon,
  Sun,
  Loader
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Block type icons and colors
const BLOCK_CONFIG = {
  revision: {
    icon: RotateCcw,
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    label: 'Revision'
  },
  deep_focus: {
    icon: Target,
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    label: 'Deep Focus'
  },
  new_learning: {
    icon: BookOpen,
    color: 'from-green-500 to-emerald-500',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'New Learning'
  },
  practice: {
    icon: Brain,
    color: 'from-orange-500 to-amber-500',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    label: 'Practice'
  },
  break: {
    icon: Coffee,
    color: 'from-gray-400 to-gray-500',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    label: 'Break'
  },
  quick_review: {
    icon: Moon,
    color: 'from-indigo-500 to-violet-500',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    label: 'Quick Review'
  }
};

/**
 * Individual Study Block Card
 */
const StudyBlockCard = ({ block, index, onComplete, isActive }) => {
  const config = BLOCK_CONFIG[block.block_type] || BLOCK_CONFIG.practice;
  const Icon = config.icon;
  const isCompleted = block.completed;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${
        isCompleted 
          ? 'bg-green-50 border-green-300 opacity-75' 
          : isActive 
            ? `${config.bgColor} ${config.borderColor} ring-2 ring-offset-2 ring-${config.color.split('-')[1]}-400`
            : `${config.bgColor} ${config.borderColor} hover:shadow-md`
      }`}
    >
      {/* Completion Badge */}
      {isCompleted && (
        <div className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full p-1">
          <CheckCircle className="w-4 h-4" />
        </div>
      )}
      
      {/* Active Indicator */}
      {isActive && !isCompleted && (
        <motion.div 
          className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-8 bg-gradient-to-b rounded-full"
          style={{ background: `linear-gradient(to bottom, var(--tw-gradient-stops))` }}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
      
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${config.color} text-white shadow-sm`}>
          <Icon className="w-5 h-5" />
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full bg-gradient-to-r ${config.color} text-white`}>
              {config.label}
            </span>
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {block.duration_minutes} min
            </span>
          </div>
          
          <h4 className={`font-semibold text-gray-800 ${isCompleted ? 'line-through' : ''}`}>
            {block.topic}
          </h4>
          
          <p className="text-sm text-gray-600 mt-1">
            {block.description}
          </p>
          
          {/* Tips (collapsed by default) */}
          {block.tips && block.tips.length > 0 && (
            <div className="mt-2 text-xs text-gray-500">
              💡 {block.tips[0]}
            </div>
          )}
          
          {/* XP Reward */}
          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs font-medium text-amber-600 flex items-center gap-1">
              <Zap className="w-3 h-3" />
              +{block.xp_reward} XP
            </span>
            
            {/* Complete Button */}
            {!isCompleted && (
              <button
                onClick={() => onComplete(index)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg bg-gradient-to-r ${config.color} text-white hover:shadow-md transition-all flex items-center gap-1`}
              >
                <CheckCircle className="w-3 h-3" />
                Complete
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Progress Ring Component
 */
const ProgressRing = ({ progress, size = 120 }) => {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
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
          style={{
            strokeDasharray: circumference,
          }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-gray-800">{Math.round(progress)}%</span>
        <span className="text-xs text-gray-500">Complete</span>
      </div>
    </div>
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
  
  // Fetch today's plan
  const fetchPlan = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/today`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlan(data);
        
        // Find first incomplete block
        const firstIncomplete = data.blocks?.findIndex(b => !b.completed) ?? 0;
        setActiveBlockIndex(Math.max(0, firstIncomplete));
      } else {
        throw new Error('Failed to fetch plan');
      }
    } catch (err) {
      console.error('Error fetching plan:', err);
      setError('Failed to load study plan');
    } finally {
      setLoading(false);
    }
  }, []);
  
  // Fetch recommendations
  const fetchRecommendations = useCallback(async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/recommendations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    }
  }, []);
  
  // Generate new plan
  const generateNewPlan = async (hours = 4) => {
    try {
      setGenerating(true);
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
        setPlan(data);
        setActiveBlockIndex(0);
      } else {
        throw new Error('Failed to generate plan');
      }
    } catch (err) {
      console.error('Error generating plan:', err);
      setError('Failed to generate new plan');
    } finally {
      setGenerating(false);
    }
  };
  
  // Mark block as complete
  const handleCompleteBlock = async (blockIndex) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/study-planner/complete-block`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ block_index: blockIndex })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update local state
        setPlan(prev => ({
          ...prev,
          blocks: prev.blocks.map((b, i) => 
            i === blockIndex ? { ...b, completed: true } : b
          ),
          completion_percentage: ((prev.blocks.filter((b, i) => b.completed || i === blockIndex).length) / prev.blocks.length) * 100
        }));
        
        // Move to next block
        setActiveBlockIndex(prev => Math.min(prev + 1, plan.blocks.length - 1));
        
        // Show XP toast (you can integrate with your toast system)
        console.log(`🎉 ${result.message}`);
      }
    } catch (err) {
      console.error('Error completing block:', err);
    }
  };
  
  // Load data on mount
  useEffect(() => {
    fetchPlan();
    fetchRecommendations();
  }, [fetchPlan, fetchRecommendations]);
  
  // Loading state
  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-center h-48">
          <Loader className="w-8 h-8 animate-spin text-cyan-500" />
        </div>
      </div>
    );
  }
  
  // Error state - Show helpful UI instead of blank
  if (error && !plan) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-cyan-100 to-purple-100 rounded-full flex items-center justify-center">
            <Calendar className="w-8 h-8 text-cyan-500" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Study Plan</h3>
          <p className="text-gray-500 mb-4 text-sm">Generate your personalized daily study plan</p>
          <button
            onClick={() => generateNewPlan(4)}
            disabled={generating}
            className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2 mx-auto"
          >
            {generating ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Create Today's Plan
              </>
            )}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Today's Study Plan
            </h2>
            <p className="text-white/80 text-sm mt-1">
              {plan?.date ? new Date(plan.date).toLocaleDateString('en-IN', { 
                weekday: 'long', 
                day: 'numeric', 
                month: 'long' 
              }) : 'Loading...'}
            </p>
          </div>
          
          <button
            onClick={() => generateNewPlan(4)}
            disabled={generating}
            className="px-3 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
          >
            {generating ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Regenerate
          </button>
        </div>
        
        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">{Math.round((plan?.total_study_minutes || 0) / 60 * 10) / 10}h</div>
            <div className="text-xs text-white/70">Study Time</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">{plan?.blocks?.length || 0}</div>
            <div className="text-xs text-white/70">Sessions</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold flex items-center justify-center gap-1">
              <Zap className="w-4 h-4" />
              {plan?.xp_target || 0}
            </div>
            <div className="text-xs text-white/70">XP Target</div>
          </div>
        </div>
        
        {/* Exam Countdown */}
        {plan?.exam_countdown && (
          <div className="mt-4 bg-red-500/30 rounded-lg p-3 flex items-center gap-3">
            <Flame className="w-5 h-5 text-yellow-300 animate-pulse" />
            <span className="font-medium">
              {plan.exam_countdown} days until exam - Stay focused! 🎯
            </span>
          </div>
        )}
      </div>
      
      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Progress & Goals */}
          <div className="lg:col-span-1 space-y-6">
            {/* Progress Ring */}
            <div className="flex flex-col items-center">
              <ProgressRing progress={plan?.completion_percentage || 0} />
              <p className="text-sm text-gray-500 mt-2">Daily Progress</p>
            </div>
            
            {/* Daily Goals */}
            <div>
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Target className="w-4 h-4 text-purple-500" />
                Today's Goals
              </h3>
              <ul className="space-y-2">
                {plan?.daily_goals?.map((goal, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                    <span>{goal}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Motivational Quote */}
            {plan?.motivational_quote && (
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-200">
                <Sparkles className="w-5 h-5 text-amber-500 mb-2" />
                <p className="text-sm text-gray-700 italic">
                  "{plan.motivational_quote}"
                </p>
              </div>
            )}
            
            {/* Quick Recommendations */}
            {recommendations.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-cyan-500" />
                  AI Recommendations
                </h3>
                <div className="space-y-2">
                  {recommendations.slice(0, 2).map((rec, i) => (
                    <div 
                      key={i}
                      className="p-3 bg-gray-50 rounded-lg text-sm"
                    >
                      <span className="mr-2">{rec.icon}</span>
                      <span className="font-medium">{rec.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Study Blocks */}
          <div className="lg:col-span-2">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-cyan-500" />
              Study Sessions
            </h3>
            
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
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
