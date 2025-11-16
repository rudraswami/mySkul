import React from 'react';

/**
 * Railway/Metro Track SVG Component
 */
export const Track = ({ x = 0, y = 0, length = 400, color = '#8B7355' }) => {
  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Left rail */}
      <line x1="0" y1="0" x2={length} y2="0" stroke={color} strokeWidth="6" />
      
      {/* Right rail */}
      <line x1="0" y1="24" x2={length} y2="24" stroke={color} strokeWidth="6" />

      {/* Sleepers (cross ties) */}
      {Array.from({ length: Math.floor(length / 40) }).map((_, i) => (
        <rect
          key={i}
          x={i * 40}
          y="6"
          width="32"
          height="12"
          fill="#D2691E"
          stroke="#8B4513"
          strokeWidth="1"
        />
      ))}

      {/* Decorative zigzag pattern */}
      {Array.from({ length: Math.floor(length / 60) }).map((_, i) => (
        <line
          key={`zigzag-${i}`}
          x1={i * 60 + 30}
          y1="-8"
          x2={i * 60 + 30}
          y2="32"
          stroke="#999"
          strokeWidth="1"
          strokeDasharray="4,4"
          opacity="0.3"
        />
      ))}
    </g>
  );
};

export default Track;


