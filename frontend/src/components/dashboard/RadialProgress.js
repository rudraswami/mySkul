import React, { useEffect, useState } from 'react';

/**
 * Radial Progress Ring Component
 * Animated circular progress indicator
 */
const RadialProgress = ({ 
  progress = 0, 
  size = 120, 
  strokeWidth = 8,
  color = '#667eea',
  backgroundColor = '#e5e7eb',
  label = '',
  subLabel = '',
  animate = true
}) => {
  const [animatedProgress, setAnimatedProgress] = useState(0);
  
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (animatedProgress / 100) * circumference;

  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimatedProgress(progress);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setAnimatedProgress(progress);
    }
  }, [progress, animate]);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="progress-ring transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="progress-ring-circle"
          strokeLinecap="round"
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-2xl font-bold text-gray-900">
          {Math.round(animatedProgress)}%
        </div>
        {label && (
          <div className="text-xs text-gray-500 font-medium mt-1 text-center px-2">
            {label}
          </div>
        )}
        {subLabel && (
          <div className="text-xs text-gray-400 mt-0.5">
            {subLabel}
          </div>
        )}
      </div>
    </div>
  );
};

export default RadialProgress;
