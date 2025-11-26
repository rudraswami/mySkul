import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, TrendingDown, Crown, Medal, Award, ArrowUp, ArrowDown, Target } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Live Leaderboard Component - Enhanced for Engagement
 * Shows top 10 users with gamified rankings, rank changes, and motivational messaging
 * Research-backed: Social comparison theory, FOMO, competition drives engagement
 */
const LiveLeaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [userRank, setUserRank] = useState(null);
  const [previousRank, setPreviousRank] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/dashboard/leaderboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const newRank = data.user_rank;
        
        // Store previous rank for comparison
        if (userRank !== null && newRank !== userRank) {
          setPreviousRank(userRank);
        }
        
        setLeaderboard(data.leaderboard || []);
        setUserRank(newRank);
      }
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <Crown className="h-5 w-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
    if (rank === 3) return <Award className="h-5 w-5 text-orange-500" />;
    return <span className="text-sm font-bold text-gray-500">#{rank}</span>;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'from-yellow-400 to-orange-500';
    if (rank === 2) return 'from-gray-300 to-gray-400';
    if (rank === 3) return 'from-orange-400 to-red-500';
    return 'from-gray-200 to-gray-300';
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-premium glass-card">
        <div className="animate-shimmer h-96 rounded-xl"></div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-premium glass-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl animate-pulse-glow">
            <Trophy className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Live Leaderboard</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Top learners this week</p>
          </div>
        </div>
        {userRank && (
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">Your rank</div>
            <div className="flex items-center justify-end space-x-2">
              <div className="text-2xl font-bold gradient-text">#{userRank}</div>
              {previousRank && previousRank !== userRank && (
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg ${
                  userRank < previousRank 
                    ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' 
                    : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
                }`}>
                  {userRank < previousRank ? (
                    <>
                      <ArrowUp className="h-4 w-4" />
                      <span className="text-xs font-semibold">+{previousRank - userRank}</span>
                    </>
                  ) : (
                    <>
                      <ArrowDown className="h-4 w-4" />
                      <span className="text-xs font-semibold">-{userRank - previousRank}</span>
                    </>
                  )}
                </div>
              )}
            </div>
            {/* Distance to next rank */}
            {userRank > 1 && leaderboard.length > 0 && (
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {(() => {
                  const userEntry = leaderboard.find(e => e.is_current_user);
                  const nextRankEntry = leaderboard.find(e => e.rank === userRank - 1);
                  if (userEntry && nextRankEntry) {
                    const xpNeeded = nextRankEntry.score - userEntry.score;
                    return xpNeeded > 0 ? `${xpNeeded} XP to rank up!` : 'Almost there!';
                  }
                  return null;
                })()}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Leaderboard List */}
      <div className="space-y-3">
        {leaderboard.map((entry, index) => (
          <div
            key={entry.user_id}
            className={`flex items-center space-x-4 p-4 rounded-xl transition-all hover:scale-102 ${
              entry.is_current_user
                ? 'bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900 dark:to-indigo-900 border-2 border-purple-300 dark:border-purple-600'
                : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
            } ${index === 0 ? 'rank-up animate-scale-in' : ''}`}
          >
            {/* Rank Badge */}
            <div className={`flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br ${getRankColor(entry.rank)} flex items-center justify-center shadow-md`}>
              {getRankIcon(entry.rank)}
            </div>

            {/* User Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                  {entry.name}
                  {entry.is_current_user && (
                    <span className="ml-2 px-2 py-0.5 bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-xs rounded-full font-semibold animate-pulse">You</span>
                  )}
                  {entry.is_pseudo && (
                    <span className="ml-2 text-xs text-gray-400 dark:text-gray-500">(Demo)</span>
                  )}
                </h4>
              </div>
              <div className="flex items-center space-x-3 mt-1">
                <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                  <Crown className="h-3 w-3 mr-1 text-yellow-500" />
                  Level {entry.level}
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">•</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {entry.sessions} sessions
                </span>
              </div>
            </div>

            {/* Score */}
            <div className="text-right">
              <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                {entry.score}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">XP</div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Note */}
      {leaderboard.some(e => e.is_pseudo) && (
        <div className="mt-6 p-3 bg-blue-50 dark:bg-blue-900 rounded-xl border border-blue-200 dark:border-blue-700">
          <p className="text-xs text-blue-800 dark:text-blue-200">
            <strong>💡 Note:</strong> Demo profiles shown for motivation. They'll be replaced with real learners as more students join!
          </p>
        </div>
      )}

      {/* Enhanced Motivational Footer */}
      <div className="mt-6 space-y-3">
        {/* Rank-specific messaging */}
        <div className={`p-4 rounded-xl border-2 ${
          userRank && userRank <= 3
            ? 'bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 border-yellow-300 dark:border-yellow-600'
            : userRank && userRank <= 10
            ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 border-blue-300 dark:border-blue-600'
            : 'bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900 dark:to-pink-900 border-purple-300 dark:border-purple-600'
        }`}>
          <div className="flex items-center space-x-2 mb-2">
            {userRank && userRank <= 3 ? (
              <Crown className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            ) : userRank && userRank <= 10 ? (
              <TrendingUp className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            ) : (
              <Target className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            )}
            <span className={`text-sm font-semibold ${
              userRank && userRank <= 3
                ? 'text-yellow-900 dark:text-yellow-100'
                : userRank && userRank <= 10
                ? 'text-blue-900 dark:text-blue-100'
                : 'text-purple-900 dark:text-purple-100'
            }`}>
              {userRank && userRank <= 3 
                ? "🏆 Top 3 Champion!"
                : userRank && userRank <= 10
                ? "🚀 Top 10 Achiever!"
                : "💪 Climb Higher!"
              }
            </span>
          </div>
          <p className={`text-sm ${
            userRank && userRank <= 3
              ? 'text-yellow-800 dark:text-yellow-200'
              : userRank && userRank <= 10
              ? 'text-blue-800 dark:text-blue-200'
              : 'text-purple-800 dark:text-purple-200'
          }`}>
            {userRank && userRank <= 3 
              ? "Amazing! You're dominating the leaderboard! Keep up the fantastic work! 🎆"
              : userRank && userRank <= 10
              ? `Great job! You're in the top 10! ${userRank > 3 ? `Just ${userRank - 3} spots away from the podium!` : 'Study more to reach the podium!'} 🚀`
              : userRank && userRank <= 20
              ? `You're rank #${userRank}! Study consistently to break into the top 10! 💪`
              : `You're rank #${userRank}! Every question brings you closer to the top! Keep going! 🔥`
            }
          </p>
        </div>
        
        {/* Beat your friends CTA */}
        {userRank && userRank > 1 && (
          <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900 dark:to-emerald-900 rounded-xl border border-green-200 dark:border-green-700">
            <p className="text-xs text-green-800 dark:text-green-200">
              <strong>💡 Pro Tip:</strong> Ask 3 more questions today to beat {leaderboard.find(e => e.rank === userRank - 1)?.name || 'the person above you'}! 
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveLeaderboard;