/**
 * 📚 Study Plan Widget for Dashboard
 * ==================================
 * 
 * Quick overview of today's study plan
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Target, Zap, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { studyPlannerAPI } from '../../api/client';

const StudyPlanWidget = () => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completedBlocks, setCompletedBlocks] = useState([]);

  useEffect(() => {
    loadTodayPlan();
  }, []);

  const loadTodayPlan = async () => {
    try {
      const response = await studyPlannerAPI.getTodayPlan();
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

  const calculateProgress = () => {
    if (!plan) return 0;
    const totalBlocks = plan.blocks.filter(b => b.block_type !== 'break').length;
    return totalBlocks > 0 ? (completedBlocks.length / totalBlocks) * 100 : 0;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 shadow-sm border border-blue-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-800">Today's Study Plan</h3>
          </div>
        </div>
        <p className="text-gray-600 mb-4 text-sm">
          Let AI create your personalized study plan for today!
        </p>
        <Link
          to="/study-planner"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all text-sm"
        >
          Generate Plan
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const progress = calculateProgress();
  const nextBlock = plan.blocks.find((_, index) => !completedBlocks.includes(index));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-800">Today's Study Plan</h3>
        </div>
        <Link
          to="/study-planner"
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          View All
        </Link>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Progress</span>
          <span className="text-sm font-semibold text-gray-800">{Math.round(progress)}%</span>
        </div>
        <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-full rounded-full"
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <Clock className="w-4 h-4 text-blue-600 mb-1" />
          <p className="text-lg font-bold text-gray-800">{plan.total_duration_minutes}m</p>
          <p className="text-xs text-gray-500">Total Time</p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3">
          <Zap className="w-4 h-4 text-yellow-600 mb-1" />
          <p className="text-lg font-bold text-gray-800">{plan.goals.xp_target}</p>
          <p className="text-xs text-gray-500">XP Goal</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <CheckCircle2 className="w-4 h-4 text-green-600 mb-1" />
          <p className="text-lg font-bold text-gray-800">
            {completedBlocks.length}/{plan.blocks.filter(b => b.block_type !== 'break').length}
          </p>
          <p className="text-xs text-gray-500">Completed</p>
        </div>
      </div>

      {/* Next Block */}
      {nextBlock && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-blue-100">
          <p className="text-xs text-gray-500 mb-1">Up Next:</p>
          <p className="font-semibold text-gray-800 text-sm">{nextBlock.topic}</p>
          <p className="text-xs text-gray-500 mt-1">{nextBlock.duration_minutes} min • {nextBlock.subject}</p>
        </div>
      )}

      {/* Motivation Message */}
      {progress === 100 ? (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-700 font-medium">
            🎉 Awesome! You completed today's plan!
          </p>
        </div>
      ) : (
        plan.motivation_message && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-700">{plan.motivation_message}</p>
          </div>
        )
      )}
    </div>
  );
};

export default StudyPlanWidget;






























































