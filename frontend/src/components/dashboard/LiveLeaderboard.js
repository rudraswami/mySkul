import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Crown, Medal, Award } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Live Leaderboard Component
 * Shows top 10 users with gamified rankings
 */
const LiveLeaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [userRank, setUserRank] = useState(null);
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
        setLeaderboard(data.leaderboard || []);
        setUserRank(data.user_rank);
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
            <div className="text-2xl font-bold gradient-text">#{userRank}</div>
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
                    <span className="ml-2 px-2 py-0.5 bg-purple-500 text-white text-xs rounded-full">You</span>
                  )}
                  {entry.is_pseudo && (
                    <span className="ml-2 text-xs text-gray-400 dark:text-gray-500">(Demo)</span>
                  )}
                </h4>
              </div>
              <div className="flex items-center space-x-3 mt-1">
                <span className="text-xs text-gray-500 dark:text-gray-400">
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

      {/* Motivational Footer */}
      <div className="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 rounded-xl border border-yellow-200 dark:border-yellow-700">
        <div className="flex items-center space-x-2 mb-2">
          <TrendingUp className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          <span className="text-sm font-semibold text-yellow-900 dark:text-yellow-100">Keep Climbing!</span>
        </div>
        <p className="text-sm text-yellow-800 dark:text-yellow-200">
          {userRank && userRank <= 3 
            ? "Amazing! You're in the top 3! Keep up the fantastic work! 🎆"
            : userRank && userRank <= 10
            ? "Great job! You're in the top 10! Study more to reach the podium! 🚀"
            : "Study consistently to climb the leaderboard and earn your spot! 💪"
          }
        </p>
      </div>
    </div>
  );
};

export default LiveLeaderboard;