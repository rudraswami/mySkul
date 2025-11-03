/**
 * Usage Meter Component
 * Shows current usage vs limit with visual progress bar
 */
import React from 'react';
import { motion } from 'framer-motion';

export default function UsageMeter({ 
  feature, 
  used, 
  limit, 
  resetPeriod = 'daily',
  icon 
}) {
  // Calculate percentage
  const percentage = limit > 0 && limit !== -1 ? Math.min((used / limit) * 100, 100) : 0;
  const remaining = limit > 0 ? Math.max(limit - used, 0) : 0;
  
  // Unlimited access
  if (limit === -1) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {icon && <span className="text-2xl">{icon}</span>}
            <div>
              <p className="text-sm font-medium text-gray-900">{feature}</p>
              <p className="text-xs text-purple-600 font-semibold">✨ Unlimited</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Determine color based on usage
  let barColor = 'bg-green-500';
  let textColor = 'text-green-600';
  if (percentage >= 80) {
    barColor = 'bg-red-500';
    textColor = 'text-red-600';
  } else if (percentage >= 50) {
    barColor = 'bg-yellow-500';
    textColor = 'text-yellow-600';
  }
  
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-xl">{icon}</span>}
          <p className="text-sm font-medium text-gray-900">{feature}</p>
        </div>
        <div className="text-right">
          <p className={`text-sm font-semibold ${textColor}`}>
            {remaining} left
          </p>
          <p className="text-xs text-gray-500">
            {used}/{limit} used
          </p>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={`h-full ${barColor} rounded-full`}
        />
      </div>
      
      <p className="text-xs text-gray-500 mt-1">
        Resets {resetPeriod === 'daily' ? 'daily at midnight' : 'monthly on 1st'}
      </p>
    </div>
  );
}
