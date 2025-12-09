/**
 * Usage Meter Component
 * Shows current usage vs limit with visual progress bar
 * Supports both full and compact modes
 */
import React from 'react';
import { motion } from 'framer-motion';

export default function UsageMeter({ 
  feature, 
  used, 
  limit, 
  resetPeriod = 'daily',
  icon,
  compact = false  // NEW: compact mode for inline display
}) {
  // Calculate percentage
  const percentage = limit > 0 && limit !== -1 ? Math.min((used / limit) * 100, 100) : 0;
  const remaining = limit > 0 ? Math.max(limit - used, 0) : 0;
  
  // Determine color based on usage
  let barColor = 'bg-green-500';
  let textColor = 'text-green-600';
  let bgTint = 'bg-green-50 border-green-200';
  if (percentage >= 80) {
    barColor = 'bg-red-500';
    textColor = 'text-red-600';
    bgTint = 'bg-red-50 border-red-200';
  } else if (percentage >= 50) {
    barColor = 'bg-yellow-500';
    textColor = 'text-yellow-600';
    bgTint = 'bg-yellow-50 border-yellow-200';
  }
  
  // Unlimited access
  if (limit === -1) {
    return (
      <div className={`${compact ? 'flex items-center gap-2 px-3 py-2' : 'p-4'} bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200`}>
        <div className="flex items-center gap-2">
          {icon && <span className={compact ? 'text-lg' : 'text-2xl'}>{icon}</span>}
          <div className={compact ? 'flex items-center gap-2' : ''}>
            <p className={`${compact ? 'text-sm' : 'text-sm'} font-medium text-gray-900`}>{feature}</p>
            <p className={`${compact ? 'text-xs' : 'text-xs'} text-purple-600 font-semibold`}>✨ Unlimited</p>
          </div>
        </div>
      </div>
    );
  }
  
  // COMPACT MODE - inline single row display
  if (compact) {
    return (
      <div className={`flex items-center gap-3 px-3 py-2 ${bgTint} rounded-lg border flex-1`}>
        {icon && <span className="text-lg">{icon}</span>}
        <div className="flex items-center gap-3 flex-1">
          <span className="text-sm font-medium text-gray-800">{feature}</span>
          <div className="flex-1 max-w-[120px] bg-gray-200 dark:bg-gray-600 rounded-full h-2 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={`h-full ${barColor} rounded-full`}
            />
          </div>
          <span className={`text-sm font-semibold ${textColor}`}>{remaining}/{limit}</span>
        </div>
      </div>
    );
  }
  
  // FULL MODE - card display
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-xl">{icon}</span>}
          <p className="text-sm font-medium text-gray-900 dark:text-white">{feature}</p>
        </div>
        <div className="text-right">
          <p className={`text-sm font-semibold ${textColor}`}>
            {remaining} left
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {used}/{limit} used
          </p>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={`h-full ${barColor} rounded-full`}
        />
      </div>
      
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
        Resets {resetPeriod === 'daily' ? 'daily at midnight' : 'monthly on 1st'}
      </p>
    </div>
  );
}
