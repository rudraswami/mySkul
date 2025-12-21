/**
 * 📚 Smart Study Planner Component
 * ================================
 * 
 * AI-powered daily study plan with:
 * - Personalized time blocks
 * - Progress tracking
 * - XP rewards
 * - Timer integration
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  Clock,
  Target,
  Zap,
  CheckCircle2,
  Circle,
  ChevronDown,
  ChevronUp,
  Play,
  Pause,
  RefreshCw,
  TrendingUp,
  Coffee,
  BookOpen,
  Brain,
  Award,
  Settings
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Block type icons and colors
const BLOCK_CONFIG = {
  spaced_repetition: {
    icon: RefreshCw,
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    label: 'Review'
  },
  deep_practice: {
    icon: Target,
    color: 'from-orange-500 to-red-500',
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-700',
    label: 'Practice'
  },
  concept_introduction: {
    icon: BookOpen,
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-700',
    label: 'Learn'
  },
  break: {
    icon: Coffee,
    color: 'from-green-500 to-emerald-500',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    label: 'Break'
  },
  mock_test: {
    icon: Award,
    color: 'from-indigo-500 to-blue-500',
    bgColor: 'bg-indigo-50',
    textColor: 'text-indigo-700',
    label: 'Test'
  }
};

const StudyPlanner = () => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completedBlocks, setCompletedBlocks] = useState([]);
  const [expandedBlock, setExpandedBlock] = useState(null);
  const [activeTimer, setActiveTimer] = useState(null);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  
  // Load today's plan
  useEffect(() => {
    loadTodayPlan();
  }, []);
  
  // Timer countdown
  useEffect(() => {
    let interval;
    if (activeTimer !== null) {
      interval = setInterval(() => {
        setTimerSeconds(prev => {
          if (prev <= 0) {
            // Timer finished - mark block as complete
            handleCompleteBlock(activeTimer);
            setActiveTimer(null);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeTimer, timerSeconds]);
  
  const loadTodayPlan = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await axios.get(`${BACKEND_URL}/api/study-planner/today`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data.success) {
        setPlan(response.data.plan);
        setCompletedBlocks(response.data.completed_blocks || []);
      }
    } catch (error) {
      console.error('Failed to load study plan:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCompleteBlock = async (blockIndex) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const isCompleted = completedBlocks.includes(blockIndex);
      
      const response = await axios.post(
        `${BACKEND_URL}/api/study-planner/progress`,
        {
          block_index: blockIndex,
          completed: !isCompleted
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.data.success) {
        setCompletedBlocks(response.data.completed_blocks);
      }
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };
  
  const startBlockTimer = (blockIndex, durationMinutes) => {
    setActiveTimer(blockIndex);
    setTimerSeconds(durationMinutes * 60);
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const calculateProgress = () => {
    if (!plan) return 0;
    const totalBlocks = plan.blocks.filter(b => b.block_type !== 'break').length;
    return totalBlocks > 0 ? (completedBlocks.length / totalBlocks) * 100 : 0;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!plan) {
    return (
      <div className="text-center py-12">
        <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Study Plan Yet</h3>
        <p className="text-gray-500 mb-6">Let's create your personalized daily plan!</p>
        <button
          onClick={loadTodayPlan}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all"
        >
          Generate Today's Plan
        </button>
      </div>
    );
  }
  
  const progress = calculateProgress();
  
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header with Motivation */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-6 text-white shadow-lg"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Today's Study Plan</h2>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-lg opacity-90 mb-4">{plan.motivation_message}</p>
        
        {/* Progress Bar */}
        <div className="bg-white/20 rounded-full h-3 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
            className="bg-white h-full rounded-full"
          />
        </div>
        <p className="text-sm mt-2 opacity-80">
          {completedBlocks.length} / {plan.blocks.filter(b => b.block_type !== 'break').length} blocks completed • {Math.round(progress)}%
        </p>
      </motion.div>
      
      {/* Goals Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
        >
          <Clock className="w-8 h-8 text-blue-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">{plan.total_duration_minutes}m</p>
          <p className="text-sm text-gray-500">Total Time</p>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
        >
          <Zap className="w-8 h-8 text-yellow-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">{plan.goals.xp_target} XP</p>
          <p className="text-sm text-gray-500">Today's Goal</p>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
        >
          <Target className="w-8 h-8 text-orange-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">{plan.goals.topics_to_master}</p>
          <p className="text-sm text-gray-500">Topics</p>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
        >
          <TrendingUp className="w-8 h-8 text-green-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">{Math.round(progress)}%</p>
          <p className="text-sm text-gray-500">Progress</p>
        </motion.div>
      </div>
      
      {/* Adaptive Notes */}
      {plan.adaptive_notes && plan.adaptive_notes.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-2">
          {plan.adaptive_notes.map((note, index) => (
            <p key={index} className="text-blue-700 text-sm">{note}</p>
          ))}
        </div>
      )}
      
      {/* Study Blocks */}
      <div className="space-y-3">
        {plan.blocks.map((block, index) => {
          const config = BLOCK_CONFIG[block.block_type] || BLOCK_CONFIG.concept_introduction;
          const IconComponent = config.icon;
          const isCompleted = completedBlocks.includes(index);
          const isExpanded = expandedBlock === index;
          const isActive = activeTimer === index;
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`bg-white rounded-xl shadow-sm border ${
                isCompleted ? 'border-green-300 bg-green-50/30' : 'border-gray-200'
              } overflow-hidden`}
            >
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    {/* Completion Checkbox */}
                    <button
                      onClick={() => handleCompleteBlock(index)}
                      className="flex-shrink-0"
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-300 hover:text-gray-400" />
                      )}
                    </button>
                    
                    {/* Block Icon */}
                    <div className={`p-2 rounded-lg ${config.bgColor}`}>
                      <IconComponent className={`w-5 h-5 ${config.textColor}`} />
                    </div>
                    
                    {/* Block Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${config.bgColor} ${config.textColor}`}>
                          {config.label}
                        </span>
                        <span className="text-xs text-gray-500">{block.subject}</span>
                      </div>
                      <h3 className="font-semibold text-gray-800">{block.topic}</h3>
                      <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {block.duration_minutes} min
                        </span>
                        <span className="flex items-center gap-1">
                          <Zap className="w-4 h-4 text-yellow-500" />
                          +{block.xp_reward} XP
                        </span>
                      </div>
                    </div>
                    
                    {/* Timer */}
                    {block.block_type !== 'break' && (
                      <div className="flex items-center gap-2">
                        {isActive ? (
                          <>
                            <span className="text-lg font-mono font-bold text-blue-600">
                              {formatTime(timerSeconds)}
                            </span>
                            <button
                              onClick={() => setActiveTimer(null)}
                              className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                            >
                              <Pause className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => startBlockTimer(index, block.duration_minutes)}
                            className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    )}
                    
                    {/* Expand Button */}
                    {block.concepts && block.concepts.length > 0 && (
                      <button
                        onClick={() => setExpandedBlock(isExpanded ? null : index)}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Expanded Content */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-4 pt-4 border-t border-gray-200"
                    >
                      <h4 className="font-medium text-gray-700 mb-2">Concepts to cover:</h4>
                      <div className="flex flex-wrap gap-2">
                        {block.concepts.map((concept, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                          >
                            {concept}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          );
        })}
      </div>
      
      {/* Regenerate Button */}
      <button
        onClick={loadTodayPlan}
        className="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
      >
        <RefreshCw className="w-5 h-5" />
        Regenerate Plan
      </button>
    </div>
  );
};

export default StudyPlanner;




































