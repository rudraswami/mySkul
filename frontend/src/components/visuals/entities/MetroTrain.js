import React from 'react';

/**
 * Delhi Metro Train SVG Component
 * Simple, clear, scalable metro train illustration
 */
export const MetroTrain = ({ x = 0, y = 0, size = 60, color = '#C41E3A' }) => {
  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Pantograph (electrical connector) */}
      <line x1="20" y1="0" x2="20" y2="-15" stroke={color} strokeWidth="2" />
      <polygon
        points="15,-15 25,-15 20,-10"
        fill={color}
      />
      
      {/* Main train body */}
      <rect
        x="0"
        y="0"
        width={size}
        height={size * 0.6}
        rx="8"
        fill={color}
        stroke="#8B0000"
        strokeWidth="2"
      />

      {/* Windows */}
      <rect x="8" y="8" width="12" height="12" fill="#87CEEB" stroke="#333" strokeWidth="1" />
      <rect x="24" y="8" width="12" height="12" fill="#87CEEB" stroke="#333" strokeWidth="1" />
      <rect x="40" y="8" width="12" height="12" fill="#87CEEB" stroke="#333" strokeWidth="1" />

      {/* Wheels */}
      <circle cx="12" cy={size * 0.6 + 4} r="6" fill="#333" />
      <circle cx="48" cy={size * 0.6 + 4} r="6" fill="#333" />

      {/* Wheel detail */}
      <circle cx="12" cy={size * 0.6 + 4} r="3" fill="none" stroke="#666" strokeWidth="1" />
      <circle cx="48" cy={size * 0.6 + 4} r="3" fill="none" stroke="#666" strokeWidth="1" />
    </g>
  );
};

export default MetroTrain;


