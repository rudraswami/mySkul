import React, { useState, useEffect } from 'react';
import { Trophy, Star, Flame, Zap, Target, Award, Crown, Heart, Book, CheckCircle } from 'lucide-react';

/**
 * Achievement Badges System
 * Displays earned and locked badges with XP progress
 */
const AchievementBadges = ({ userXP = 0, userLevel = 1 }) => {
  const [badges, setBadges] = useState([]);
  const [showDetails, setShowDetails] = useState(null);

  useEffect(() => {
    initializeBadges();
  }, [userXP]);

  const badgeDefinitions = [
    {
      id: 'first-session',
      name: 'First Steps',
      description: 'Complete your first AI Tutor session',
      icon: Star,
      color: 'from-blue-400 to-blue-600',
      xpRequired: 0,
      unlocked: true
    },
    {
      id: 'streak-3',
      name: '3-Day Streak',
      description: 'Study for 3 consecutive days',
      icon: Flame,
      color: 'from-orange-400 to-red-600',
      xpRequired: 50,
      unlocked: userXP >= 50
    },
    {
      id: 'streak-7',
      name: 'Week Warrior',
      description: 'Maintain a 7-day study streak',
      icon: Flame,
      color: 'from-red-500 to-pink-600',
      xpRequired: 150,
      unlocked: userXP >= 150
    },
    {
      id: 'fast-learner',
      name: 'Fast Learner',
      description: 'Complete 10 sessions in one day',
      icon: Zap,
      color: 'from-yellow-400 to-orange-500',
      xpRequired: 100,
      unlocked: userXP >= 100
    },
    {
      id: 'consistency-champ',
      name: 'Consistency Champion',
      description: 'Study every day for a month',
      icon: Target,
      color: 'from-green-400 to-emerald-600',
      xpRequired: 500,
      unlocked: userXP >= 500
    },
    {
      id: 'ai-scholar',
      name: 'AI Scholar',
      description: 'Ask 100 questions to AI Tutor',
      icon: Book,
      color: 'from-purple-400 to-indigo-600',
      xpRequired: 200,
      unlocked: userXP >= 200
    },
    {
      id: 'mock-master',
      name: 'Mock Test Master',
      description: 'Complete 10 mock tests',
      icon: CheckCircle,
      color: 'from-teal-400 to-cyan-600',
      xpRequired: 300,
      unlocked: userXP >= 300
    },
    {
      id: 'perfectionist',
      name: 'Perfectionist',
      description: 'Score 100% on a mock test',
      icon: Crown,
      color: 'from-yellow-500 to-amber-600',
      xpRequired: 250,
      unlocked: userXP >= 250
    },
    {
      id: 'dedication',
      name: 'Dedicated Learner',
      description: 'Study for 100 total hours',
      icon: Heart,
      color: 'from-pink-400 to-rose-600',
      xpRequired: 1000,
      unlocked: userXP >= 1000
    },
    {
      id: 'legend',
      name: 'Legend',
      description: 'Reach Level 10',
      icon: Award,
      color: 'from-indigo-500 to-purple-700',
      xpRequired: 2000,
      unlocked: userXP >= 2000
    }
  ];

  const initializeBadges = () => {
    setBadges(badgeDefinitions);
  };

  const unlockedBadges = badges.filter(b => b.unlocked);
  const lockedBadges = badges.filter(b => !b.unlocked);

  const xpToNextLevel = (userLevel + 1) * 100;
  const xpProgress = (userXP % 100) / 100 * 100;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-premium glass-card">
      {/* Header with XP Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl animate-pulse-glow">
              <Trophy className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">Achievements</h3>
              <p className="text-sm text-gray-500">{unlockedBadges.length}/{badges.length} unlocked</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold gradient-text">Level {userLevel}</div>
            <div className="text-xs text-gray-500">{userXP} XP</div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="relative">
          <div className="xp-bar">
            <div 
              className="xp-fill" 
              style={{ width: `${xpProgress}%` }}
            ></div>
          </div>
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>{userXP % 100} XP</span>
            <span>{xpToNextLevel} XP to Level {userLevel + 1}</span>
          </div>
        </div>
      </div>

      {/* Unlocked Badges */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Earned Badges</h4>
        <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
          {unlockedBadges.length > 0 ? (
            unlockedBadges.map((badge) => {
              const Icon = badge.icon;
              return (
                <div
                  key={badge.id}
                  className="badge-container cursor-pointer animate-scale-in"
                  onClick={() => setShowDetails(badge)}
                  onMouseEnter={() => setShowDetails(badge)}
                  onMouseLeave={() => setShowDetails(null)}
                >
                  <div className="badge-glow"></div>
                  <div className={`relative p-4 bg-gradient-to-br ${badge.color} rounded-xl shadow-lg hover:scale-110 transition-transform duration-300`}>
                    <Icon className="h-8 w-8 text-white mx-auto" />
                    <div className="badge-shine"></div>
                  </div>
                  <div className="text-center mt-2">
                    <p className="text-xs font-medium text-gray-900 truncate">{badge.name}</p>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-3 md:col-span-5 text-center py-8 text-gray-400">
              <Trophy className="h-12 w-12 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Start earning badges!</p>
            </div>
          )}
        </div>
      </div>

      {/* Locked Badges */}
      {lockedBadges.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Locked Badges</h4>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
            {lockedBadges.map((badge) => {
              const Icon = badge.icon;
              return (
                <div
                  key={badge.id}
                  className="cursor-pointer"
                  onClick={() => setShowDetails(badge)}
                  onMouseEnter={() => setShowDetails(badge)}
                  onMouseLeave={() => setShowDetails(null)}
                >
                  <div className="relative p-4 bg-gray-200 rounded-xl opacity-60 hover:opacity-80 transition-opacity duration-300">
                    <Icon className="h-8 w-8 text-gray-400 mx-auto" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-6 h-6 border-2 border-gray-400 rounded-full"></div>
                    </div>
                  </div>
                  <div className="text-center mt-2">
                    <p className="text-xs font-medium text-gray-500 truncate">{badge.name}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Badge Details Tooltip */}
      {showDetails && (
        <div className="fixed z-50 bottom-20 left-1/2 transform -translate-x-1/2 max-w-xs animate-scale-in">
          <div className="bg-gray-900 text-white rounded-xl p-4 shadow-2xl">
            <div className="flex items-center space-x-3 mb-2">
              <div className={`p-2 bg-gradient-to-br ${showDetails.color} rounded-lg`}>
                {React.createElement(showDetails.icon, { className: "h-5 w-5 text-white" })}
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">{showDetails.name}</h4>
                {!showDetails.unlocked && (
                  <p className="text-xs text-gray-400">{showDetails.xpRequired} XP required</p>
                )}
              </div>
            </div>
            <p className="text-xs text-gray-300">{showDetails.description}</p>
            {!showDetails.unlocked && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-400">
                  Progress: {Math.min(100, (userXP / showDetails.xpRequired * 100)).toFixed(0)}%
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5 mt-1">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, (userXP / showDetails.xpRequired * 100))}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  );
};

export default AchievementBadges;
