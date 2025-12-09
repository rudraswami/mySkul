import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Flame, TrendingUp, Info, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Streak Heatmap - PROFESSIONAL REDESIGN
 * ======================================
 * 
 * Clean GitHub-style contribution calendar with:
 * - Better color visibility
 * - Clear legend
 * - Responsive layout
 */
const StreakHeatmap = ({ userId }) => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [longestStreak, setLongestStreak] = useState(0);
  const [hoveredDay, setHoveredDay] = useState(null);
  const [loading, setLoading] = useState(true);

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
        setHeatmapData(data.heatmap_data || generateMockData());
        setCurrentStreak(data.current_streak || 0);
        setLongestStreak(data.longest_streak || 0);
      } else {
        // Generate mock data for demo
        setHeatmapData(generateMockData());
      }
    } catch (error) {
      console.error('Failed to load streak data:', error);
      setHeatmapData(generateMockData());
    } finally {
      setLoading(false);
    }
  };

  // Generate mock data for 6 months
  const generateMockData = () => {
    const data = [];
    const today = new Date();
    for (let i = 180; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toISOString().split('T')[0],
        level: Math.floor(Math.random() * 5),
        minutes: Math.floor(Math.random() * 120)
      });
    }
    return data;
  };

  // Get level color
  const getLevelColor = (level) => {
    const colors = [
      'bg-slate-100 dark:bg-slate-700', // Level 0 - no activity
      'bg-emerald-200 dark:bg-emerald-900', // Level 1 - light
      'bg-emerald-400 dark:bg-emerald-700', // Level 2 - medium
      'bg-emerald-500 dark:bg-emerald-600', // Level 3 - high
      'bg-emerald-600 dark:bg-emerald-500', // Level 4 - max
    ];
    return colors[level] || colors[0];
  };

  // Organize into weeks (show last 26 weeks / 6 months)
  const recentData = heatmapData.slice(-182);
  const weeks = [];
  for (let i = 0; i < recentData.length; i += 7) {
    weeks.push(recentData.slice(i, i + 7));
  }

  // Get month labels
  const getMonthLabels = () => {
    const labels = [];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    let lastMonth = -1;
    
    weeks.forEach((week, idx) => {
      if (week[0]) {
        const month = new Date(week[0].date).getMonth();
        if (month !== lastMonth) {
          labels.push({ index: idx, label: months[month] });
          lastMonth = month;
        }
      }
    });
    return labels;
  };

  const monthLabels = getMonthLabels();

  // Motivational message
  const getMessage = () => {
    if (currentStreak === 0) return "Start your streak today! Consistency is key to success.";
    if (currentStreak < 3) return `Great start! ${currentStreak} day${currentStreak > 1 ? 's' : ''} strong. Keep going!`;
    if (currentStreak < 7) return `Amazing! ${currentStreak}-day streak. You're building momentum!`;
    if (currentStreak < 30) return `Incredible ${currentStreak}-day streak! You're on fire!`;
    return `Legendary ${currentStreak}-day streak! You're unstoppable!`;
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-5">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
          <div className="h-32 bg-slate-200 dark:bg-slate-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-slate-100 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
              <Flame className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white">Study Streak</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">Your learning journey</p>
            </div>
          </div>
          
          {/* Streak Stats */}
          <div className="flex items-center gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-orange-500">{currentStreak}</div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wide">Current</div>
            </div>
            <div className="w-px h-8 bg-slate-200 dark:bg-slate-700" />
            <div className="text-center">
              <div className="text-xl font-bold text-violet-500">{longestStreak}</div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wide">Best</div>
            </div>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div className="p-5">
        {/* Month labels */}
        <div className="flex mb-2 ml-8">
          {monthLabels.map(({ index, label }, i) => (
            <div 
              key={i}
              className="text-[10px] text-slate-400 dark:text-slate-500 font-medium"
              style={{ marginLeft: index * 14 - (i > 0 ? monthLabels[i-1].index * 14 : 0) }}
            >
              {label}
            </div>
          ))}
        </div>

        {/* Grid */}
        <div className="flex">
          {/* Day labels */}
          <div className="flex flex-col justify-around pr-2 text-[10px] text-slate-400 dark:text-slate-500 font-medium">
            <span>Mon</span>
            <span></span>
            <span>Wed</span>
            <span></span>
            <span>Fri</span>
            <span></span>
            <span></span>
          </div>

          {/* Cells */}
          <div className="flex gap-[3px] flex-1 overflow-x-auto">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-[3px]">
                {week.map((day, dayIndex) => (
                  <motion.div
                    key={dayIndex}
                    whileHover={{ scale: 1.3 }}
                    className={`w-3 h-3 rounded-sm cursor-pointer ${getLevelColor(day?.level || 0)} transition-colors`}
                    onMouseEnter={() => setHoveredDay(day)}
                    onMouseLeave={() => setHoveredDay(null)}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
          <span className="text-xs text-slate-500 dark:text-slate-400">Activity Level</span>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-slate-400">Less</span>
            {[0, 1, 2, 3, 4].map(level => (
              <div key={level} className={`w-3 h-3 rounded-sm ${getLevelColor(level)}`} />
            ))}
            <span className="text-[10px] text-slate-400">More</span>
          </div>
        </div>

        {/* Hover tooltip */}
        {hoveredDay && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 p-3 bg-slate-900 text-white text-sm rounded-lg"
          >
            <div className="font-medium">
              {new Date(hoveredDay.date).toLocaleDateString('en-US', { 
                weekday: 'short',
                month: 'short', 
                day: 'numeric'
              })}
            </div>
            <div className="text-slate-300 text-xs mt-0.5">
              {hoveredDay.minutes > 0 ? `${hoveredDay.minutes} minutes studied` : 'No activity'}
            </div>
          </motion.div>
        )}
      </div>

      {/* Motivational Message */}
      <div className="px-5 pb-5">
        <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 rounded-xl border border-orange-200 dark:border-orange-800">
          <div className="flex items-start gap-2">
            <TrendingUp className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
            <div>
              <span className="text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-wide">Streak Insight</span>
              <p className="text-sm text-orange-800 dark:text-orange-200 mt-1">{getMessage()} 💪</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreakHeatmap;
