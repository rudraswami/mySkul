import React from 'react';

/**
 * Cricket Ball SVG Component
 * Used for projectile motion, velocity examples
 */
export const CricketBall = ({ x = 0, y = 0, size = 40, color = '#8B0000' }) => {
  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Main ball */}
      <circle
        cx="0"
        cy="0"
        r={size / 2}
        fill={color}
        stroke="#5C0000"
        strokeWidth="1"
      />

      {/* Seam - distinctive red cricket ball stitching */}
      <path
        d={`M ${-size / 4},${-size / 6} Q 0,${-size / 3} ${size / 4},${-size / 6}`}
        stroke="#FFD700"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />

      {/* Highlight for 3D effect */}
      <ellipse
        cx={-size / 5}
        cy={-size / 5}
        rx={size / 8}
        ry={size / 12}
        fill="white"
        opacity="0.4"
      />
    </g>
  );
};

export default CricketBall;


