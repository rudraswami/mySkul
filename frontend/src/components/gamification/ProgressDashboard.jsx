/**
 * 📊 Progress Dashboard Component
 * 
 * Visual progress tracking with:
 * - XP and Level progress
 * - Streak display
 * - Daily stats
 * - Badges
 * - Recommendations
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Flame, Trophy, Target, Zap, Star, 
  TrendingUp, Clock, CheckCircle, Award,
  ChevronRight, Sparkles
} from 'lucide-react';

// Level configurations
const LEVEL_CONFIG = {
  Explorer: {
    color: 'from-green-400 to-emerald-500',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
    textColor: 'text-green-600 dark:text-green-400',
    emoji: '🔭',
    description: 'Just starting your journey'
  },
  Analyst: {
    color: 'from-blue-400 to-cyan-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    textColor: 'text-blue-600 dark:text-blue-400',
    emoji: '🔬',
    description: 'Building strong foundations'
  },
  Tactician: {
    color: 'from-purple-400 to-violet-500',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    borderColor: 'border-purple-200 dark:border-purple-800',
    textColor: 'text-purple-600 dark:text-purple-400',
    emoji: '🎯',
    description: 'Strategic problem solver'
  },
  Scientist: {
    color: 'from-orange-400 to-amber-500',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    borderColor: 'border-orange-200 dark:border-orange-800',
    textColor: 'text-orange-600 dark:text-orange-400',
    emoji: '🧪',
    description: 'Deep understanding achieved'
  },
  Master: {
    color: 'from-yellow-400 to-amber-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    textColor: 'text-yellow-600 dark:text-yellow-400',
    emoji: '👑',
    description: 'True mastery unlocked'
  }
};

/**
 * Main Progress Dashboard
 */
const ProgressDashboard = ({ stats, compact = false }) => {
  if (!stats) return null;
  
  const levelConfig = LEVEL_CONFIG[stats.level?.level_name] || LEVEL_CONFIG.Explorer;
  
  if (compact) {
    return <CompactProgress stats={stats} levelConfig={levelConfig} />;
  }
  
  return (
    <div className="space-y-4">
      {/* Level & XP Card */}
      <LevelCard stats={stats} levelConfig={levelConfig} />
      
      {/* Streak Card */}
      <StreakCard streak={stats.streak} />
      
      {/* Today's Stats */}
      <TodayStats today={stats.today} />
      
      {/* Badges */}
      {stats.badges?.length > 0 && (
        <BadgesCard badges={stats.badges} />
      )}
      
      {/* Recommendations */}
      {stats.recommendations?.length > 0 && (
        <RecommendationsCard recommendations={stats.recommendations} />
      )}
    </div>
  );
};

/**
 * Compact Progress (for sidebar/header)
 */
const CompactProgress = ({ stats, levelConfig }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center space-x-4 bg-white dark:bg-gray-800 rounded-xl px-4 py-2 shadow-sm border border-gray-100 dark:border-gray-700"
    >
      {/* Level Badge */}
      <div className={`flex items-center space-x-2 ${levelConfig.textColor}`}>
        <span className="text-xl">{levelConfig.emoji}</span>
        <span className="font-bold text-sm">{stats.level?.level_name}</span>
      </div>
      
      {/* XP Progress */}
      <div className="flex-1 max-w-32">
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${stats.level?.progress_percent || 0}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className={`h-full bg-gradient-to-r ${levelConfig.color}`}
          />
        </div>
        <p className="text-xs text-gray-500 mt-0.5">
          {stats.level?.level_xp}/{stats.level?.next_level_xp} XP
        </p>
      </div>
      
      {/* Streak */}
      <div className="flex items-center space-x-1">
        <Flame className="w-4 h-4 text-orange-500" />
        <span className="font-bold text-orange-500">{stats.streak?.current || 0}</span>
      </div>
    </motion.div>
  );
};

/**
 * Level & XP Card
 */
const LevelCard = ({ stats, levelConfig }) => {
  const level = stats.level || {};
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`rounded-2xl p-6 ${levelConfig.bgColor} border ${levelConfig.borderColor}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <motion.span 
            className="text-4xl"
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ repeat: Infinity, duration: 3 }}
          >
            {levelConfig.emoji}
          </motion.span>
          <div>
            <h3 className={`text-xl font-bold ${levelConfig.textColor}`}>
              {level.level_name || 'Explorer'}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {levelConfig.description}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <p className={`text-2xl font-bold ${levelConfig.textColor}`}>
            {level.current_xp?.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-500">Total XP</p>
        </div>
      </div>
      
      {/* Progress Bar */}
      {!level.is_max_level && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">
              Progress to {level.next_level_name}
            </span>
            <span className={`font-medium ${levelConfig.textColor}`}>
              {level.progress_percent}%
            </span>
          </div>
          
          <div className="h-4 bg-white dark:bg-gray-800 rounded-full overflow-hidden shadow-inner">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${level.progress_percent || 0}%` }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
              className={`h-full bg-gradient-to-r ${levelConfig.color} relative`}
            >
              <motion.div
                className="absolute right-0 top-0 h-full w-8 bg-white/30"
                animate={{ x: [-32, 200] }}
                transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
              />
            </motion.div>
          </div>
          
          <p className="text-center text-sm text-gray-500">
            <span className="font-medium">{level.xp_to_next}</span> XP to next level
          </p>
        </div>
      )}
      
      {level.is_max_level && (
        <div className="text-center py-4">
          <Sparkles className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
          <p className="text-yellow-600 font-bold">Maximum Level Achieved!</p>
        </div>
      )}
    </motion.div>
  );
};

/**
 * Streak Card
 */
const StreakCard = ({ streak }) => {
  const currentStreak = streak?.current || 0;
  const longestStreak = streak?.longest || 0;
  
  // Determine streak status
  const getStreakColor = () => {
    if (currentStreak >= 30) return 'from-yellow-400 to-amber-500';
    if (currentStreak >= 7) return 'from-blue-400 to-cyan-500';
    if (currentStreak >= 3) return 'from-orange-400 to-red-500';
    return 'from-gray-400 to-gray-500';
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-2xl p-5 border border-orange-200 dark:border-orange-800"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Flame Animation */}
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ repeat: Infinity, duration: 1.5 }}
            className="relative"
          >
            <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${getStreakColor()} flex items-center justify-center shadow-lg`}>
              <Flame className="w-8 h-8 text-white" />
            </div>
            {currentStreak > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-md"
              >
                <span className="text-xs font-bold text-orange-500">{currentStreak}</span>
              </motion.div>
            )}
          </motion.div>
          
          <div>
            <h4 className="font-bold text-gray-900 dark:text-white text-lg">
              {currentStreak > 0 ? `${currentStreak} Day Streak!` : 'Start Your Streak!'}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {streak?.motivation || 'Learn daily to build your streak'}
            </p>
          </div>
        </div>
        
        {/* Longest Streak */}
        <div className="text-right">
          <div className="flex items-center space-x-1 text-gray-500">
            <Trophy className="w-4 h-4" />
            <span className="text-sm">Best</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">
            {longestStreak}
          </p>
        </div>
      </div>
      
      {/* Streak Progress to next badge */}
      {currentStreak > 0 && currentStreak < 7 && (
        <div className="mt-4 pt-4 border-t border-orange-200 dark:border-orange-800">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">
              💙 Blue Streak Badge
            </span>
            <span className="text-orange-600 font-medium">
              {7 - currentStreak} days to go
            </span>
          </div>
          <div className="h-2 bg-white dark:bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(currentStreak / 7) * 100}%` }}
              className="h-full bg-gradient-to-r from-orange-400 to-red-500"
            />
          </div>
        </div>
      )}
    </motion.div>
  );
};

/**
 * Today's Stats Card
 */
const TodayStats = ({ today }) => {
  const stats = [
    {
      icon: <CheckCircle className="w-5 h-5" />,
      label: 'Questions',
      value: today?.questions || 0,
      color: 'text-blue-600'
    },
    {
      icon: <Target className="w-5 h-5" />,
      label: 'Accuracy',
      value: `${Math.round(today?.accuracy || 0)}%`,
      color: 'text-green-600'
    },
    {
      icon: <Clock className="w-5 h-5" />,
      label: 'Time',
      value: `${today?.time_spent || 0}m`,
      color: 'text-purple-600'
    },
    {
      icon: <Zap className="w-5 h-5" />,
      label: 'Correct',
      value: today?.correct || 0,
      color: 'text-orange-600'
    }
  ];
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700"
    >
      <h4 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
        <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
        Today's Progress
      </h4>
      
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="text-center"
          >
            <div className={`${stat.color} mb-1 flex justify-center`}>
              {stat.icon}
            </div>
            <p className="text-xl font-bold text-gray-900 dark:text-white">
              {stat.value}
            </p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </motion.div>
        ))}
      </div>
      
      {/* Daily Goal Progress */}
      {(today?.questions || 0) < 5 && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">
              🎯 Daily Goal (5 questions)
            </span>
            <span className="text-blue-600 font-medium">
              {today?.questions || 0}/5
            </span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${((today?.questions || 0) / 5) * 100}%` }}
              className="h-full bg-gradient-to-r from-blue-400 to-purple-500"
            />
          </div>
        </div>
      )}
    </motion.div>
  );
};

/**
 * Badges Card
 */
const BadgesCard = ({ badges }) => {
  const BADGE_INFO = {
    flame_starter: { emoji: '🔥', name: 'Flame Starter', desc: '3-day streak' },
    blue_streak: { emoji: '💙', name: 'Blue Streak', desc: '7-day streak' },
    golden_streak: { emoji: '🏆', name: 'Golden Streak', desc: '30-day streak' },
    legendary_streak: { emoji: '👑', name: 'Legendary', desc: '100-day streak' },
    first_question: { emoji: '🌟', name: 'First Step', desc: 'Asked first question' },
    concept_crusher: { emoji: '💪', name: 'Concept Crusher', desc: '10 concepts mastered' },
    speed_demon: { emoji: '⚡', name: 'Speed Demon', desc: 'Fast answers' },
    deep_diver: { emoji: '🤿', name: 'Deep Diver', desc: 'Asked follow-ups' },
    night_owl: { emoji: '🦉', name: 'Night Owl', desc: 'Late night study' },
    early_bird: { emoji: '🐦', name: 'Early Bird', desc: 'Morning study' },
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700"
    >
      <h4 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
        <Award className="w-5 h-5 mr-2 text-yellow-500" />
        Badges Earned ({badges.length})
      </h4>
      
      <div className="flex flex-wrap gap-3">
        {badges.map((badge, i) => {
          const info = BADGE_INFO[badge] || { emoji: '🏅', name: badge };
          return (
            <motion.div
              key={badge}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center space-x-2 bg-yellow-50 dark:bg-yellow-900/20 px-3 py-2 rounded-xl border border-yellow-200 dark:border-yellow-800"
              title={info.desc}
            >
              <span className="text-2xl">{info.emoji}</span>
              <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                {info.name}
              </span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

/**
 * Recommendations Card
 */
const RecommendationsCard = ({ recommendations }) => {
  const priorityColors = {
    high: 'border-red-200 bg-red-50 dark:bg-red-900/20',
    medium: 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20',
    low: 'border-blue-200 bg-blue-50 dark:bg-blue-900/20'
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700"
    >
      <h4 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
        <Star className="w-5 h-5 mr-2 text-purple-500" />
        Recommended for You
      </h4>
      
      <div className="space-y-3">
        {recommendations.map((rec, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`p-3 rounded-xl border ${priorityColors[rec.priority] || priorityColors.low} flex items-center justify-between`}
          >
            <p className="text-sm text-gray-800 dark:text-gray-200">
              {rec.message}
            </p>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default ProgressDashboard;
export { CompactProgress, LevelCard, StreakCard, TodayStats, BadgesCard };



