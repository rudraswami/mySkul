import React, { useState, useEffect } from 'react';
import { Flame, TrendingUp } from 'lucide-react';

/**
 * GitHub-style Streak Heatmap Calendar
 * Shows daily study activity for the past year
 */
const StreakHeatmap = ({ userId }) => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [longestStreak, setLongestStreak] = useState(0);
  const [hoveredDay, setHoveredDay] = useState(null);

  useEffect(() => {
    generateHeatmapData();
  }, []);

  const generateHeatmapData = () => {
    // Generate 365 days of data
    const data = [];
    const today = new Date();
    let streak = 0;
    let maxStreak = 0;
    let tempStreak = 0;

    for (let i = 364; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Simulate activity level (0-4)
      // In production, fetch from backend
      const activity = Math.random() > 0.3 ? Math.floor(Math.random() * 5) : 0;
      
      if (activity > 0) {
        tempStreak++;
        if (i === 0) streak = tempStreak;
      } else {
        if (tempStreak > maxStreak) maxStreak = tempStreak;
        tempStreak = 0;
      }
      
      data.push({
        date: date.toISOString().split('T')[0],
        level: activity,
        count: activity * 5 // sessions count
      });
    }

    setHeatmapData(data);
    setCurrentStreak(streak);
    setLongestStreak(Math.max(maxStreak, tempStreak));
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

  return (
    <div className="bg-white rounded-2xl p-6 shadow-premium glass-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl">
            <Flame className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Study Streak</h3>
            <p className="text-sm text-gray-500">Your learning journey</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-2xl font-bold text-orange-600">{currentStreak} days</div>
            <div className="text-xs text-gray-500">Current streak</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">{longestStreak} days</div>
            <div className="text-xs text-gray-500">Longest streak</div>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Month labels */}
          <div className="flex mb-2">
            <div className="w-10"></div>
            {weeks.map((_, index) => (
              <div key={index} className="flex-shrink-0 w-3 text-xs text-gray-400 text-center">
                {getMonthLabel(index)}
              </div>
            ))}
          </div>

          {/* Heatmap grid */}
          <div className="flex">
            {/* Weekday labels */}
            <div className="flex flex-col justify-around w-10 pr-2">
              {[0, 1, 2, 3, 4, 5, 6].map((day) => (
                <div key={day} className="text-xs text-gray-400 h-3 flex items-center">
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
                  />
                ))}
              </div>
            ))}
          </div>

          {/* Hover tooltip */}
          {hoveredDay && (
            <div className="mt-4 p-3 bg-gray-800 text-white text-sm rounded-lg inline-block">
              <div className="font-semibold">{new Date(hoveredDay.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</div>
              <div className="text-gray-300">{hoveredDay.count} study sessions</div>
            </div>
          )}

          {/* Legend */}
          <div className="flex items-center justify-end space-x-2 mt-4 text-xs text-gray-500">
            <span>Less</span>
            {[0, 1, 2, 3, 4].map((level) => (
              <div key={level} className={`heatmap-cell heatmap-level-${level}`}></div>
            ))}
            <span>More</span>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border border-orange-200">
        <div className="flex items-center space-x-2 mb-2">
          <TrendingUp className="h-4 w-4 text-orange-600" />
          <span className="text-sm font-semibold text-orange-900">Streak Insight</span>
        </div>
        <p className="text-sm text-orange-800">
          {currentStreak > 0 
            ? `Amazing! You've been consistent for ${currentStreak} days. Keep it up! 🔥`
            : "Start your streak today! Consistency is key to success. 💪"
          }
        </p>
      </div>
    </div>
  );
};

export default StreakHeatmap;
