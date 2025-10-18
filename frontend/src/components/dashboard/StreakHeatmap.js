import React, { useState, useEffect } from 'react';
import { Flame, TrendingUp, Info } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * GitHub-style Streak Heatmap Calendar with Dynamic API Data
 * Shows daily study activity for the past year
 */
const StreakHeatmap = ({ userId }) => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [longestStreak, setLongestStreak] = useState(0);
  const [hoveredDay, setHoveredDay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInfo, setShowInfo] = useState(false);

  useEffect(() => {
    loadStreakData();
  }, []);

  const loadStreakData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/dashboard/streak`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setHeatmapData(data.heatmap_data || []);
        setCurrentStreak(data.current_streak || 0);
        setLongestStreak(data.longest_streak || 0);
      }
    } catch (error) {
      console.error('Failed to load streak data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getWeekdayLabel = (index) => {
    const days = ['Mon', '', 'Wed', '', 'Fri', '', ''];
    return days[index];
  };

  const getMonthLabel = (weekIndex) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const dataIndex = weekIndex * 7;
    if (dataIndex >= heatmapData.length) return '';
    const date = new Date(heatmapData[dataIndex].date);
    return weekIndex % 4 === 0 ? months[date.getMonth()] : '';
  };

  // Organize data into weeks
  const weeks = [];
  for (let i = 0; i < heatmapData.length; i += 7) {
    weeks.push(heatmapData.slice(i, i + 7));
  }

  // Get motivational message
  const getMotivationalMessage = () => {
    if (currentStreak === 0) return "Start your streak today! Consistency is key to success. 💪";
    if (currentStreak < 3) return `Great start! You've studied ${currentStreak} day${currentStreak > 1 ? 's' : ''} in a row. Keep it up! 🌟`;
    if (currentStreak < 7) return `Amazing! You've studied ${currentStreak} days in a row. You're building a strong habit! 🔥`;
    if (currentStreak < 30) return `Incredible! ${currentStreak}-day streak! You're on fire! 🚀`;
    return `Legendary! ${currentStreak}-day streak! You're a learning machine! 👑`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-premium glass-card">
        <div className="animate-shimmer h-64 rounded-xl"></div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-premium glass-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl">
            <Flame className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Study Streak</h3>
              <button
                onClick={() => setShowInfo(!showInfo)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="What this means"
              >
                <Info className="h-4 w-4 text-gray-500" />
              </button>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Your learning journey</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-2xl font-bold text-orange-600">{currentStreak} days</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Current streak</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">{longestStreak} days</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Longest streak</div>
          </div>
        </div>
      </div>

      {/* Info Tooltip */}
      {showInfo && (
        <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900 rounded-xl border border-blue-200 dark:border-blue-700">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">ℹ️ How Streaks Work</h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>• Study at least once per day to maintain your streak</li>
            <li>• Each day of studying adds to your current streak</li>
            <li>• Missing a day resets your current streak to 0</li>
            <li>• Your longest streak is saved forever</li>
            <li>• Consistency is more important than long sessions!</li>
          </ul>
        </div>
      )}

      {/* Heatmap */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Month labels */}
          <div className="flex mb-2">
            <div className="w-10"></div>
            {weeks.map((_, index) => (
              <div key={index} className="flex-shrink-0 w-3 text-xs text-gray-400 dark:text-gray-500 text-center">
                {getMonthLabel(index)}
              </div>
            ))}
          </div>

          {/* Heatmap grid */}
          <div className="flex">
            {/* Weekday labels */}
            <div className="flex flex-col justify-around w-10 pr-2">
              {[0, 1, 2, 3, 4, 5, 6].map((day) => (
                <div key={day} className="text-xs text-gray-400 dark:text-gray-500 h-3 flex items-center">
                  {getWeekdayLabel(day)}
                </div>
              ))}
            </div>

            {/* Cells */}
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1 mr-1">
                {week.map((day, dayIndex) => (
                  <div
                    key={dayIndex}
                    className={`heatmap-cell heatmap-level-${day.level}`}
                    onMouseEnter={() => setHoveredDay(day)}
                    onMouseLeave={() => setHoveredDay(null)}
                    title={`${day.date}: ${day.minutes} minutes`}
                  />
                ))}
              </div>
            ))}
          </div>

          {/* Hover tooltip */}
          {hoveredDay && (
            <div className="mt-4 p-3 bg-gray-900 text-white text-sm rounded-lg inline-block animate-scale-in">
              <div className="font-semibold">
                {new Date(hoveredDay.date).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric', 
                  year: 'numeric' 
                })}
              </div>
              <div className="text-gray-300 mt-1">
                {hoveredDay.minutes > 0 
                  ? `${hoveredDay.minutes} minutes studied`
                  : 'No study session'
                }
              </div>
              {hoveredDay.subjects && hoveredDay.subjects.length > 0 && (
                <div className="text-gray-400 text-xs mt-1">
                  Subjects: {hoveredDay.subjects.join(', ')}
                </div>
              )}
            </div>
          )}

          {/* Color Legend - Always Visible */}
          <div className="flex items-center justify-between mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
            <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">Activity Level:</div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">Less</span>
              <div className="flex items-center space-x-1">
                <div className="heatmap-cell heatmap-level-0" title="Missed Day"></div>
                <div className="heatmap-cell heatmap-level-1" title="<30 mins"></div>
                <div className="heatmap-cell heatmap-level-2" title="30-60 mins"></div>
                <div className="heatmap-cell heatmap-level-3" title="60-90 mins"></div>
                <div className="heatmap-cell heatmap-level-4" title=">90 mins"></div>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">More</span>
            </div>
          </div>
        </div>
      </div>

      {/* Motivational Insights */}
      <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900 dark:to-red-900 rounded-xl border border-orange-200 dark:border-orange-700">
        <div className="flex items-center space-x-2 mb-2">
          <TrendingUp className="h-4 w-4 text-orange-600 dark:text-orange-400" />
          <span className="text-sm font-semibold text-orange-900 dark:text-orange-100">Streak Insight</span>
        </div>
        <p className="text-sm text-orange-800 dark:text-orange-200">
          {getMotivationalMessage()}
        </p>
      </div>
    </div>
  );
};

export default StreakHeatmap;