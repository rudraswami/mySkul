/**
 * 🛤️ Track Primitive
 * ===================
 * 
 * Race track / path for motion visualizations.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Track = ({
  x = 0,
  y = 0,
  width = 300,
  height = 50,
  color = '#374151',
  markings = true,
  markers = [0, 25, 50, 75, 100],
  unit = 'm',
  animated = true,
  delay = 0,
  style = 'road', // road, grass, track, minimal
  finishLine = true,
}) => {
  const styles = {
    road: {
      fill: '#374151',
      markingColor: '#FCD34D',
      borderColor: '#1F2937',
    },
    grass: {
      fill: '#86EFAC',
      markingColor: 'white',
      borderColor: '#22C55E',
    },
    track: {
      fill: '#92400E',
      markingColor: 'white',
      borderColor: '#78350F',
    },
    minimal: {
      fill: '#F3F4F6',
      markingColor: '#D1D5DB',
      borderColor: '#9CA3AF',
    },
  };

  const trackStyle = styles[style] || styles.road;

  return (
    <motion.g
      initial={animated ? { opacity: 0, scaleX: 0 } : undefined}
      animate={animated ? { opacity: 1, scaleX: 1 } : undefined}
      transition={{ delay, duration: 0.8 }}
      style={{ originX: 0 }}
    >
      {/* Track base */}
      <rect
        x={x}
        y={y - height / 2}
        width={width}
        height={height}
        rx={5}
        fill={trackStyle.fill}
        stroke={trackStyle.borderColor}
        strokeWidth={2}
      />

      {/* Road markings (center dashes) */}
      {markings && style === 'road' && (
        <motion.g
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ delay: delay + 0.5 }}
        >
          {Array.from({ length: Math.floor(width / 40) }).map((_, i) => (
            <rect
              key={i}
              x={x + 20 + i * 40}
              y={y - 3}
              width={25}
              height={6}
              rx={2}
              fill={trackStyle.markingColor}
            />
          ))}
        </motion.g>
      )}

      {/* Distance markers */}
      <motion.g
        initial={animated ? { opacity: 0 } : undefined}
        animate={animated ? { opacity: 1 } : undefined}
        transition={{ delay: delay + 0.8 }}
      >
        {markers.map((m, i) => {
          const markerX = x + (width * i) / (markers.length - 1);
          return (
            <g key={m}>
              <line
                x1={markerX}
                y1={y - height / 2 - 5}
                x2={markerX}
                y2={y - height / 2 - 15}
                stroke="white"
                strokeWidth={2}
              />
              <text
                x={markerX}
                y={y - height / 2 - 20}
                fontSize={10}
                textAnchor="middle"
                fill="#636E72"
                fontFamily="sans-serif"
              >
                {m}{unit}
              </text>
            </g>
          );
        })}
      </motion.g>

      {/* Finish line */}
      {finishLine && (
        <motion.g
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ delay: delay + 1 }}
        >
          <line
            x1={x + width}
            y1={y - height / 2 - 5}
            x2={x + width}
            y2={y + height / 2 + 5}
            stroke="white"
            strokeWidth={4}
            strokeDasharray="8 4"
          />
          <text x={x + width + 5} y={y + 5} fontSize={16}>
            🏁
          </text>
        </motion.g>
      )}
    </motion.g>
  );
};

export default Track;

