import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Brain, Flame, Target, TrendingUp } from 'lucide-react';

const VitalSigns = ({ dashboardData }) => {
    const stats = [
        {
            id: 'study_time',
            label: 'Study Time',
            value: dashboardData?.study_time_today || '0h 0m',
            icon: Clock,
            color: 'text-blue-400',
            bg: 'bg-blue-500/10',
            border: 'border-blue-500/20'
        },
        {
            id: 'sessions',
            label: 'AI Sessions',
            value: dashboardData?.total_sessions || 0,
            icon: Brain,
            color: 'text-purple-400',
            bg: 'bg-purple-500/10',
            border: 'border-purple-500/20'
        },
        {
            id: 'streak',
            label: 'Day Streak',
            value: dashboardData?.current_streak || 0,
            icon: Flame,
            color: 'text-orange-400',
            bg: 'bg-orange-500/10',
            border: 'border-orange-500/20'
        },
        {
            id: 'goal',
            label: 'Weekly Goal',
            value: `${dashboardData?.weekly_progress || 0}%`,
            icon: Target,
            color: 'text-green-400',
            bg: 'bg-green-500/10',
            border: 'border-green-500/20'
        }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((stat, index) => (
                <motion.div
                    key={stat.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    className={`glass-panel rounded-2xl p-4 border ${stat.border} relative overflow-hidden group cursor-default`}
                >
                    {/* Background Glow on Hover */}
                    <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-br from-transparent via-${stat.color.split('-')[1]}-500/5 to-transparent pointer-events-none`}></div>

                    <div className="flex items-center justify-between mb-2">
                        <div className={`p-2 rounded-lg ${stat.bg}`}>
                            <stat.icon className={`w-5 h-5 ${stat.color}`} />
                        </div>
                        {stat.id === 'goal' && (
                            <TrendingUp className="w-4 h-4 text-gray-400 group-hover:text-green-400 transition-colors" />
                        )}
                    </div>

                    <div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1 tracking-tight">
                            {stat.value}
                        </h3>
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors">
                            {stat.label}
                        </p>
                    </div>

                    {/* Micro-interaction: Progress Bar for Goal */}
                    {stat.id === 'goal' && (
                        <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-200 dark:bg-gray-800">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: stat.value }}
                                transition={{ duration: 1, delay: 0.5 }}
                                className="h-full bg-green-500"
                            />
                        </div>
                    )}
                </motion.div>
            ))}
        </div>
    );
};

export default VitalSigns;
