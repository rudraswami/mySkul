/**
 * Scene Vectors Component
 * Renders force arrows, motion paths, and physics vectors
 */

import React from 'react';

const SceneVectors = ({ vectors = [] }) => {
  return (
    <g id="vectors-layer">
      {vectors.filter(v => v.visible !== false && v.magnitude > 0).map(vector => (
        <VectorArrow
          key={vector.id}
          {...vector}
        />
      ))}
    </g>
  );
};

const VectorArrow = ({
  id,
  x = 50,
  y = 30,
  direction = 'right',
  magnitude = 50,
  opacity = 1,
  color = '#FF5722',
  label,
  animated = true,
}) => {
  const directionAngles = {
    right: 0,
    left: 180,
    up: -90,
    down: 90,
    'forward': 0,
    'backward': 180,
  };

  const angle = typeof direction === 'number' ? direction : (directionAngles[direction] || 0);
  const arrowLength = magnitude * 0.2; // Scale factor
  const arrowHead = 3;

  return (
    <g
      id={`vector-${id}`}
      transform={`translate(${x}, ${y}) rotate(${angle})`}
      opacity={opacity}
    >
      {/* Main arrow shaft */}
      <line
        x1="0"
        y1="0"
        x2={arrowLength}
        y2="0"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
      />

      {/* Arrow head */}
      <polygon
        points={`${arrowLength},0 ${arrowLength - arrowHead},-${arrowHead * 0.6} ${arrowLength - arrowHead},${arrowHead * 0.6}`}
        fill={color}
      />

      {/* Glow effect for emphasis */}
      {animated && (
        <line
          x1="0"
          y1="0"
          x2={arrowLength}
          y2="0"
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          opacity="0.3"
        >
          <animate
            attributeName="opacity"
            values="0.3;0.6;0.3"
            dur="1.5s"
            repeatCount="indefinite"
          />
        </line>
      )}

      {/* Label */}
      {label && (
        <text
          x={arrowLength / 2}
          y="-3"
          textAnchor="middle"
          fontSize="2.5"
          fill={color}
          fontWeight="bold"
        >
          {label}
        </text>
      )}

      {/* Motion lines (for movement indication) */}
      {direction === 'right' || direction === 'forward' ? (
        <g opacity="0.5">
          <line x1="-3" y1="-2" x2="-6" y2="-2" stroke={color} strokeWidth="0.5" />
          <line x1="-3" y1="0" x2="-8" y2="0" stroke={color} strokeWidth="0.5" />
          <line x1="-3" y1="2" x2="-6" y2="2" stroke={color} strokeWidth="0.5" />
        </g>
      ) : null}
    </g>
  );
};

/**
 * Curved motion path (for projectile motion)
 */
export const MotionPath = ({
  startX = 20,
  startY = 40,
  endX = 80,
  endY = 40,
  peakY = 20,
  color = '#2196F3',
  opacity = 1,
  dashed = true,
}) => {
  const controlX = (startX + endX) / 2;
  const pathD = `M ${startX} ${startY} Q ${controlX} ${peakY} ${endX} ${endY}`;

  return (
    <g opacity={opacity}>
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="0.8"
        strokeDasharray={dashed ? "2 1" : "none"}
      />
      {/* Direction arrow at end */}
      <polygon
        points={`${endX},${endY} ${endX - 3},${endY - 2} ${endX - 3},${endY + 2}`}
        fill={color}
      />
    </g>
  );
};

export default SceneVectors;









