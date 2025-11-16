import React from 'react';

/**
 * Direction Arrow SVG Component
 * Shows speed/velocity direction
 */
export const DirectionArrow = ({ x = 0, y = 0, direction = 'right', length = 80, color = '#FF6B35', strokeWidth = 4 }) => {
  // Calculate angle based on direction
  const angles = {
    right: 0,
    left: 180,
    up: -90,
    down: 90,
  };

  const angle = angles[direction] || 0;

  return (
    <g transform={`translate(${x}, ${y}) rotate(${angle})`}>
      {/* Arrow shaft */}
      <line
        x1="0"
        y1="0"
        x2={length}
        y2="0"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />

      {/* Arrow head */}
      <polygon
        points={`${length},0 ${length - 15},−8 ${length - 15},8`}
        fill={color}
        stroke={color}
        strokeWidth="1"
      />

      {/* Optional: Speed indicator labels */}
      <text
        x={length / 2}
        y={-15}
        textAnchor="middle"
        fontSize="12"
        fontWeight="bold"
        fill={color}
        fontFamily="Arial, sans-serif"
      >
        v
      </text>
    </g>
  );
};

export default DirectionArrow;


