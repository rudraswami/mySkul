import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Trophy, 
  Medal, 
  Crown, 
  TrendingUp,
  Zap,
  Award,
  Star,
  Users,
  Filter
} from 'lucide-react';

export default function Leaderboard({ showFullView = false }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [filter, setFilter] = useState('global'); // 'global', 'friends', 'school'
  const [timeframe, setTimeframe] = useState('all'); // 'all', 'month', 'week'
  const [loading, setLoading] = useState(true);
  const [userRank, setUserRank] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchLeaderboard();
  }, [filter, timeframe]);

  const fetchLeaderboard = async () => {
    try:
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/gamification/leaderboard?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard || []);
        setUserRank(data.your_rank);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <Crown className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Medal className="w-6 h-6 text-orange-600" />;
    return <span className="text-gray-600 font-bold">#{rank}</span>;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white';
    if (rank === 2) return 'bg-gradient-to-r from-gray-300 to-gray-400 text-white';
    if (rank === 3) return 'bg-gradient-to-r from-orange-400 to-red-400 text-white';
    return 'bg-white';
  };

  const getLevelBadgeColor = (level) => {
    if (level >= 50) return 'bg-purple-500 text-white';
    if (level >= 30) return 'bg-yellow-500 text-white';
    if (level >= 20) return 'bg-blue-500 text-white';
    if (level >= 10) return 'bg-green-500 text-white';
    return 'bg-gray-400 text-white';
  };

  // Compact view for sidebar
  if (!showFullView) {
    return (
      <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-600" />
              <h3 className="font-bold text-gray-800">Leaderboard</h3>
            </div>
            {userRank && (
              <Badge className="bg-blue-500 text-white">
                #{userRank}
              </Badge>
            )}
          </div>

          {loading ? (
            <div className="text-center text-sm text-gray-600">Loading...</div>
          ) : (
            <div className="space-y-2">
              {leaderboard.slice(0, 5).map((entry, idx) => (
                <div
                  key={idx}
                  className={`flex items-center gap-2 p-2 rounded-lg ${
                    entry.is_current_user ? 'bg-blue-100 border border-blue-300' : 'bg-white'
                  }`}
                >
                  <div className="flex-shrink-0 w-6 text-center">
                    {getRankIcon(entry.rank)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {entry.username}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Zap className="w-3 h-3 text-yellow-500" />
                      <span>{entry.total_xp} XP</span>
                      <span className="mx-1">•</span>
                      <span>L{entry.level}</span>
                    </div>
                  </div>
                  <Badge className={getLevelBadgeColor(entry.level)} size="sm">
                    {entry.badges_count}
                  </Badge>
                </div>
              ))}
            </div>
          )}

          {leaderboard.length > 5 && (
            <button 
              className="w-full mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
              onClick={() => window.location.href = '/leaderboard'}
            >
              View Full Leaderboard →
            </button>
          )}
        </CardContent>
      </Card>
    );
  }

  // Full view for dedicated leaderboard page
  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8 text-center">
        <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Leaderboard</h1>
        <p className="text-gray-600">Compete with top performers across India</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('global')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'global'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🌍 Global
          </button>
          <button
            onClick={() => setFilter('friends')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'friends'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            👥 Friends
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setTimeframe('all')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              timeframe === 'all'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Time
          </button>
          <button
            onClick={() => setTimeframe('month')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              timeframe === 'month'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            This Month
          </button>
          <button
            onClick={() => setTimeframe('week')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              timeframe === 'week'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            This Week
          </button>
        </div>
      </div>

      {/* User's Rank Card */}
      {userRank && (
        <Card className="mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-white text-blue-600 rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg">
                  #{userRank}
                </div>
                <div>
                  <p className="text-sm opacity-90">Your Rank</p>
                  <p className="text-2xl font-bold">You're in the top {Math.ceil((userRank / leaderboard.length) * 100)}%!</p>
                </div>
              </div>
              <TrendingUp className="w-12 h-12 opacity-50" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading leaderboard...</p>
        </div>
      ) : leaderboard.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No rankings yet</h3>
            <p className="text-gray-500">Be the first to complete tests and climb the leaderboard!</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {leaderboard.map((entry, idx) => (
            <Card
              key={idx}
              className={`transition-all hover:shadow-lg ${
                entry.is_current_user ? 'border-2 border-blue-500 bg-blue-50' : ''
              } ${getRankColor(entry.rank)}`}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  {/* Rank */}
                  <div className="flex-shrink-0 w-12 text-center">
                    <div className="text-2xl">
                      {getRankIcon(entry.rank)}
                    </div>
                  </div>

                  {/* User Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className={`font-bold text-lg truncate ${entry.rank <= 3 ? 'text-white' : 'text-gray-800'}`}>
                        {entry.username}
                      </p>
                      {entry.is_current_user && (
                        <Badge className="bg-blue-500 text-white">You</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Zap className={`w-4 h-4 ${entry.rank <= 3 ? 'text-white' : 'text-yellow-500'}`} />
                        <span className={entry.rank <= 3 ? 'text-white font-semibold' : 'text-gray-700'}>
                          {entry.total_xp.toLocaleString()} XP
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className={`w-4 h-4 ${entry.rank <= 3 ? 'text-white' : 'text-blue-500'}`} />
                        <span className={entry.rank <= 3 ? 'text-white font-semibold' : 'text-gray-700'}>
                          Level {entry.level}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Award className={`w-4 h-4 ${entry.rank <= 3 ? 'text-white' : 'text-purple-500'}`} />
                        <span className={entry.rank <= 3 ? 'text-white font-semibold' : 'text-gray-700'}>
                          {entry.badges_count} Badges
                        </span>
                      </div>
                      {entry.streak > 0 && (
                        <div className="flex items-center gap-1">
                          <span className={entry.rank <= 3 ? 'text-white font-semibold' : 'text-orange-600'}>
                            🔥 {entry.streak} day streak
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Level Badge */}
                  <Badge className={getLevelBadgeColor(entry.level)} size="lg">
                    L{entry.level}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
