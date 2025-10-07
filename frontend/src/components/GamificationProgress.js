import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Trophy, 
  Zap, 
  Star, 
  Award, 
  TrendingUp,
  Target,
  Flame,
  Crown,
  Sparkles,
  Medal,
  Gift
} from 'lucide-react';

export default function GamificationProgress({ showFullView = false }) {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBadgeModal, setShowBadgeModal] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchGamificationProgress();
  }, []);

  const fetchGamificationProgress = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/gamification/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProgress(data);
      }
    } catch (error) {
      console.error('Error fetching gamification progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelTitle = (level) => {
    if (level >= 50) return { title: 'Grand Master', color: 'text-purple-600', icon: '👑' };
    if (level >= 30) return { title: 'Master', color: 'text-yellow-600', icon: '🏆' };
    if (level >= 20) return { title: 'Expert', color: 'text-blue-600', icon: '⭐' };
    if (level >= 10) return { title: 'Advanced', color: 'text-green-600', icon: '🎯' };
    if (level >= 5) return { title: 'Intermediate', color: 'text-teal-600', icon: '📚' };
    return { title: 'Novice', color: 'text-gray-600', icon: '🌱' };
  };

  const getStreakEmoji = (streak) => {
    if (streak >= 30) return '🔥🔥🔥';
    if (streak >= 7) return '🔥🔥';
    if (streak >= 3) return '🔥';
    return '✨';
  };

  if (loading) {
    return (
      <Card className="bg-white">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!progress) {
    return null;
  }

  const levelInfo = getLevelTitle(progress.current_level);
  const xpPercentage = (progress.total_xp % 100);

  // Compact view for sidebar/dashboard
  if (!showFullView) {
    return (
      <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
        <CardContent className="p-4">
          {/* Level & XP */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="text-2xl">{levelInfo.icon}</div>
              <div>
                <p className="text-xs text-gray-600">Level {progress.current_level}</p>
                <p className={`text-sm font-bold ${levelInfo.color}`}>{levelInfo.title}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-1 text-yellow-600">
                <Zap className="w-4 h-4" />
                <span className="font-bold">{progress.total_xp}</span>
              </div>
              <p className="text-xs text-gray-500">Total XP</p>
            </div>
          </div>

          {/* XP Progress Bar */}
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Level Progress</span>
              <span>{progress.xp_for_next_level} XP to next</span>
            </div>
            <Progress value={xpPercentage} className="h-2" />
          </div>

          {/* Streak */}
          {progress.current_streak > 0 && (
            <div className="flex items-center justify-center gap-2 bg-orange-100 rounded-lg py-2">
              <Flame className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold text-orange-700">
                {progress.current_streak} Day Streak {getStreakEmoji(progress.current_streak)}
              </span>
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-2 mt-3">
            <div className="bg-white rounded-lg p-2 text-center">
              <Award className="w-4 h-4 text-purple-500 mx-auto mb-1" />
              <p className="text-xs text-gray-600">{progress.total_badges} Badges</p>
            </div>
            <div className="bg-white rounded-lg p-2 text-center">
              <Target className="w-4 h-4 text-green-500 mx-auto mb-1" />
              <p className="text-xs text-gray-600">{progress.stats.total_tests} Tests</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Full view for dedicated gamification page
  return (
    <div className="space-y-6">
      {/* Level & XP Card */}
      <Card className="bg-gradient-to-br from-purple-500 to-blue-600 text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="text-6xl">{levelInfo.icon}</div>
              <div>
                <h2 className="text-4xl font-bold">Level {progress.current_level}</h2>
                <p className="text-xl opacity-90">{levelInfo.title}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-yellow-300 mb-1">
                <Zap className="w-8 h-8" />
                <span className="text-4xl font-bold">{progress.total_xp}</span>
              </div>
              <p className="text-sm opacity-80">Total Experience Points</p>
            </div>
          </div>

          {/* XP Progress */}
          <div>
            <div className="flex justify-between text-sm mb-2 opacity-90">
              <span>Progress to Level {progress.current_level + 1}</span>
              <span>{progress.xp_for_next_level} XP remaining</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-4">
              <div
                className="bg-gradient-to-r from-yellow-300 to-orange-400 h-4 rounded-full transition-all duration-500"
                style={{ width: `${xpPercentage}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-orange-200">
          <CardContent className="p-6 text-center">
            <Flame className="w-12 h-12 text-orange-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-orange-600">{progress.current_streak}</p>
            <p className="text-sm text-gray-600">Day Streak {getStreakEmoji(progress.current_streak)}</p>
            <p className="text-xs text-gray-500 mt-1">Best: {progress.longest_streak}</p>
          </CardContent>
        </Card>

        <Card className="border-purple-200">
          <CardContent className="p-6 text-center">
            <Award className="w-12 h-12 text-purple-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-purple-600">{progress.total_badges}</p>
            <p className="text-sm text-gray-600">Badges Earned</p>
            <p className="text-xs text-gray-500 mt-1">{progress.available_badges - progress.total_badges} more to unlock</p>
          </CardContent>
        </Card>

        <Card className="border-green-200">
          <CardContent className="p-6 text-center">
            <Target className="w-12 h-12 text-green-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-green-600">{progress.stats.total_tests}</p>
            <p className="text-sm text-gray-600">Tests Completed</p>
            <p className="text-xs text-gray-500 mt-1">{progress.stats.average_accuracy}% avg accuracy</p>
          </CardContent>
        </Card>

        <Card className="border-yellow-200">
          <CardContent className="p-6 text-center">
            <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-yellow-600">{progress.stats.perfect_scores}</p>
            <p className="text-sm text-gray-600">Perfect Scores</p>
            <p className="text-xs text-gray-500 mt-1">100% accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Badges Showcase */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-6 h-6 text-purple-500" />
            Your Badges
          </CardTitle>
        </CardHeader>
        <CardContent>
          {progress.badges_earned.length === 0 ? (
            <div className="text-center py-8">
              <Medal className="w-16 h-16 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-600">No badges earned yet</p>
              <p className="text-sm text-gray-500 mt-1">Complete tests to earn your first badge!</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {progress.badges_earned.map((badge, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 text-center hover:shadow-lg transition-all cursor-pointer border border-purple-200"
                >
                  <div className="text-4xl mb-2">{badge.badge_icon}</div>
                  <p className="text-sm font-semibold text-gray-800">{badge.badge_name}</p>
                  <p className="text-xs text-gray-600 mt-1">{badge.description}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Motivational Message */}
      {progress.current_streak > 0 && (
        <Card className="bg-gradient-to-r from-orange-100 to-yellow-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <Sparkles className="w-12 h-12 text-orange-500" />
              <div>
                <p className="text-lg font-bold text-gray-800">
                  You're on fire! {getStreakEmoji(progress.current_streak)}
                </p>
                <p className="text-gray-700">
                  {progress.current_streak >= 7 
                    ? `Amazing ${progress.current_streak}-day streak! Keep the momentum going!`
                    : `${progress.current_streak} days in a row! Don't break the streak!`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
