import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Star, Flame, Zap, Target, Award, Crown, Heart, Book, CheckCircle, Lock } from 'lucide-react';

/**
 * Achievement Badges - PROFESSIONAL REDESIGN
 * ==========================================
 * 
 * Clean design with:
 * - Larger, more readable badges
 * - Clear progress indicators
 * - No truncated text
 * - Distinct locked/unlocked states
 */
const AchievementBadges = ({ userXP = 0, userLevel = 1 }) => {
  const [selectedBadge, setSelectedBadge] = useState(null);

  const badgeDefinitions = [
    {
      id: 'first-session',
      name: 'First Steps',
      description: 'Complete your first AI session',
      icon: Star,
      gradient: 'from-blue-500 to-cyan-500',
      xpRequired: 0,
    },
    {
      id: 'streak-3',
      name: '3-Day Streak',
      description: 'Study for 3 consecutive days',
      icon: Flame,
      gradient: 'from-orange-500 to-red-500',
      xpRequired: 50,
    },
    {
      id: 'streak-7',
      name: 'Week Warrior',
      description: 'Maintain a 7-day streak',
      icon: Flame,
      gradient: 'from-red-500 to-pink-500',
      xpRequired: 150,
    },
    {
      id: 'fast-learner',
      name: 'Fast Learner',
      description: 'Complete 10 sessions in a day',
      icon: Zap,
      gradient: 'from-amber-500 to-orange-500',
      xpRequired: 100,
    },
    {
      id: 'consistency',
      name: 'Consistent',
      description: 'Study every day for a month',
      icon: Target,
      gradient: 'from-emerald-500 to-teal-500',
      xpRequired: 500,
    },
    {
      id: 'scholar',
      name: 'AI Scholar',
      description: 'Ask 100 questions',
      icon: Book,
      gradient: 'from-violet-500 to-purple-500',
      xpRequired: 200,
    },
    {
      id: 'mock-master',
      name: 'Mock Master',
      description: 'Complete 10 mock tests',
      icon: CheckCircle,
      gradient: 'from-teal-500 to-cyan-500',
      xpRequired: 300,
    },
    {
      id: 'perfectionist',
      name: 'Perfectionist',
      description: 'Score 100% on a test',
      icon: Crown,
      gradient: 'from-yellow-500 to-amber-500',
      xpRequired: 250,
    },
    {
      id: 'dedicated',
      name: 'Dedicated',
      description: 'Study for 100 hours total',
      icon: Heart,
      gradient: 'from-pink-500 to-rose-500',
      xpRequired: 1000,
    },
    {
      id: 'legend',
      name: 'Legend',
      description: 'Reach Level 10',
      icon: Award,
      gradient: 'from-indigo-500 to-purple-600',
      xpRequired: 2000,
    }
  ];

  const badges = badgeDefinitions.map(b => ({
    ...b,
    unlocked: userXP >= b.xpRequired,
    progress: b.xpRequired > 0 ? Math.min(100, (userXP / b.xpRequired) * 100) : 100
  }));

  const unlockedBadges = badges.filter(b => b.unlocked);
  const lockedBadges = badges.filter(b => !b.unlocked);
  
  const xpForNextLevel = (userLevel + 1) * 100;
  const xpInCurrentLevel = userXP % 100;
  const levelProgress = (xpInCurrentLevel / 100) * 100;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-slate-100 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white">Achievements</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{unlockedBadges.length}/{badges.length} unlocked</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">Level {userLevel}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">{userXP} XP</div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="mt-4">
          <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${levelProgress}%` }}
              transition={{ duration: 0.5 }}
              className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
            />
          </div>
          <div className="flex justify-between mt-1.5 text-xs text-slate-500 dark:text-slate-400">
            <span>{xpInCurrentLevel} XP</span>
            <span>{xpForNextLevel} XP to Level {userLevel + 1}</span>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* Earned Badges */}
        <div>
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Earned Badges</h4>
          {unlockedBadges.length > 0 ? (
            <div className="grid grid-cols-4 gap-3">
              {unlockedBadges.map((badge) => {
                const Icon = badge.icon;
                return (
                  <motion.button
                    key={badge.id}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setSelectedBadge(selectedBadge?.id === badge.id ? null : badge)}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${badge.gradient} flex items-center justify-center shadow-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-xs font-medium text-slate-700 dark:text-slate-300 text-center leading-tight">
                      {badge.name}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-6 bg-slate-50 dark:bg-slate-900/50 rounded-xl">
              <Trophy className="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-500 dark:text-slate-400">Complete tasks to earn badges!</p>
            </div>
          )}
        </div>

        {/* Locked Badges */}
        {lockedBadges.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Locked Badges</h4>
            <div className="grid grid-cols-4 gap-3">
              {lockedBadges.slice(0, 8).map((badge) => {
                const Icon = badge.icon;
                const questionsAway = Math.ceil((badge.xpRequired - userXP) / 10);
                
                return (
                  <motion.button
                    key={badge.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setSelectedBadge(selectedBadge?.id === badge.id ? null : badge)}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className="relative">
                      <div className="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                        <Icon className="w-6 h-6 text-slate-400 dark:text-slate-500" />
                      </div>
                      {/* Progress ring */}
                      <svg className="absolute inset-0 w-12 h-12 -rotate-90">
                        <circle
                          cx="24"
                          cy="24"
                          r="22"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          className="text-slate-300 dark:text-slate-600"
                        />
                        <circle
                          cx="24"
                          cy="24"
                          r="22"
                          fill="none"
                          stroke="url(#lockGradient)"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeDasharray={`${badge.progress * 1.38} 138`}
                        />
                        <defs>
                          <linearGradient id="lockGradient">
                            <stop offset="0%" stopColor="#6366f1" />
                            <stop offset="100%" stopColor="#8b5cf6" />
                          </linearGradient>
                        </defs>
                      </svg>
                      {/* Lock icon */}
                      <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-slate-300 dark:bg-slate-600 rounded-full flex items-center justify-center">
                        <Lock className="w-3 h-3 text-slate-500 dark:text-slate-400" />
                      </div>
                    </div>
                    <div className="text-center">
                      <span className="text-xs font-medium text-slate-500 dark:text-slate-400 block leading-tight">
                        {badge.name}
                      </span>
                      <span className="text-[10px] text-slate-400 dark:text-slate-500">
                        {questionsAway}q away
                      </span>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Badge Detail Popup */}
      {selectedBadge && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-slate-100 dark:border-slate-700 p-4 bg-slate-50 dark:bg-slate-900/50"
        >
          <div className="flex items-start gap-3">
            <div className={`w-10 h-10 rounded-lg ${selectedBadge.unlocked ? `bg-gradient-to-br ${selectedBadge.gradient}` : 'bg-slate-300 dark:bg-slate-600'} flex items-center justify-center flex-shrink-0`}>
              {React.createElement(selectedBadge.icon, { className: "w-5 h-5 text-white" })}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-slate-900 dark:text-white">{selectedBadge.name}</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">{selectedBadge.description}</p>
              {!selectedBadge.unlocked && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
                    <span>Progress</span>
                    <span>{Math.round(selectedBadge.progress)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
                      style={{ width: `${selectedBadge.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {Math.ceil((selectedBadge.xpRequired - userXP) / 10)} questions to unlock
                  </p>
                </div>
              )}
              {selectedBadge.unlocked && (
                <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Unlocked!
                </p>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AchievementBadges;
