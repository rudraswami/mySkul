/**
 * PersonalizationPanel Component
 * 
 * Displays user XP, level, streaks, and topic mastery
 * Gamified UI with animations and progress bars
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, Flame, Star, TrendingUp, Award, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';

const PersonalizationPanel = ({ 
  xpInfo = { total_xp: 0, current_level: 1, progress_percentage: 0, xp_for_next_level: 100 },
  streakInfo = { current_streak: 0, longest_streak: 0 },
  topicMastery = {},
  loading = false
}) => {
  /**
   * Get level color based on level
   */
  const getLevelColor = (level) => {
    if (level >= 10) return 'from-purple-500 to-pink-500';
    if (level >= 7) return 'from-blue-500 to-cyan-500';
    if (level >= 5) return 'from-green-500 to-emerald-500';
    return 'from-gray-500 to-gray-600';
  };

  /**
   * Get mastery badge color
   */
  const getMasteryColor = (score) => {
    if (score >= 90) return 'bg-purple-600 text-white';
    if (score >= 75) return 'bg-blue-600 text-white';
    if (score >= 50) return 'bg-green-600 text-white';
    return 'bg-gray-600 text-white';
  };

  /**
   * Get mastery level text
   */
  const getMasteryLevel = (score) => {
    if (score >= 90) return 'Expert';
    if (score >= 75) return 'Advanced';
    if (score >= 50) return 'Intermediate';
    return 'Beginner';
  };

  /**
   * Get top 3 topics by mastery
   */
  const topTopics = Object.entries(topicMastery)
    .sort(([, a], [, b]) => (b.score || 0) - (a.score || 0))
    .slice(0, 3);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* XP & Level Card */}
      <Card className="border-0 shadow-md bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700">
        <CardContent className="p-4">
          {/* Level Badge */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className={`w-16 h-16 rounded-full bg-gradient-to-br ${getLevelColor(xpInfo.current_level)} flex items-center justify-center shadow-lg`}
              >
                <span className="text-2xl font-bold text-white">
                  {xpInfo.current_level}
                </span>
              </motion.div>
              <div>
                <div className="text-sm font-medium text-gray-600 dark:text-gray-300">
                  Level {xpInfo.current_level}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {xpInfo.total_xp.toLocaleString()} XP
                </div>
              </div>
            </div>
            <Trophy className="h-8 w-8 text-yellow-500" />
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Progress to Level {xpInfo.current_level + 1}
              </span>
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {xpInfo.progress_percentage}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${xpInfo.progress_percentage}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full"
              />
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {xpInfo.xp_for_next_level - (xpInfo.total_xp % xpInfo.xp_for_next_level)} XP to next level
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Streak Card */}
      {streakInfo.current_streak > 0 && (
        <Card className="border-0 shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Flame className="h-10 w-10 text-orange-500" />
                </motion.div>
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-orange-600">
                    {streakInfo.current_streak}
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    day streak
                  </span>
                </div>
                {streakInfo.longest_streak > streakInfo.current_streak && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Best: {streakInfo.longest_streak} days
                  </div>
                )}
              </div>
              <Zap className="h-6 w-6 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Topic Mastery */}
      {topTopics.length > 0 && (
        <Card className="border-0 shadow-md">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Top Topics
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3">
              {topTopics.map(([topic, data]) => (
                <div key={topic} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {topic}
                    </span>
                    <Badge className={`${getMasteryColor(data.score)} text-xs`}>
                      {getMasteryLevel(data.score)}
                    </Badge>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-green-500 to-emerald-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${data.score}%` }}
                    />
                  </div>
                  {data.attempts && (
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {data.attempts} {data.attempts === 1 ? 'attempt' : 'attempts'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Achievements Preview */}
      <Card className="border-0 shadow-md bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-gray-800 dark:to-gray-700">
        <CardContent className="p-4">
          <div className="flex items-center space-x-3">
            <Award className="h-8 w-8 text-yellow-600" />
            <div>
              <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Keep Learning!
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-300">
                Unlock achievements as you progress
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default React.memo(PersonalizationPanel);
