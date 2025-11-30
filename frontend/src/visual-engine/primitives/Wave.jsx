/**
 * 🌊 Wave Primitive
 * =================
 * 
 * Animated wave for sound, light, electromagnetic concepts.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

const Wave = ({
  x = 0,
  y = 0,
  width = 200,
  amplitude = 30,
  wavelength = 50,
  color = '#3B82F6',
  strokeWidth = 3,
  animated = true,
  animationDuration = 2,
  showLabels = true,
  showAmplitude = true,
  showWavelength = true,
  type = 'sine', // sine, square, triangle, sawtooth
}) => {
  // Generate wave path
  const wavePath = useMemo(() => {
    const points = [];
    const numPoints = 100;
    
    for (let i = 0; i <= numPoints; i++) {
      const px = x + (i / numPoints) * width;
      let py;
      
      const phase = (i / numPoints) * (width / wavelength) * 2 * Math.PI;
      
      switch (type) {
        case 'square':
          py = y - amplitude * (Math.sin(phase) >= 0 ? 1 : -1);
          break;
        case 'triangle':
          py = y - amplitude * (2 / Math.PI) * Math.asin(Math.sin(phase));
          break;
        case 'sawtooth':
          py = y - amplitude * ((phase / Math.PI) % 2 - 1);
          break;
        default: // sine
          py = y - amplitude * Math.sin(phase);
      }
      
      points.push(`${i === 0 ? 'M' : 'L'} ${px} ${py}`);
    }
    
    return points.join(' ');
  }, [x, y, width, amplitude, wavelength, type]);

  return (
    <g>
      {/* Center line */}
      <line
        x1={x}
        y1={y}
        x2={x + width}
        y2={y}
        stroke="#D1D5DB"
        strokeWidth={1}
        strokeDasharray="4 2"
      />

      {/* Animated wave */}
      <motion.path
        d={wavePath}
        stroke={color}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
        initial={animated ? { pathLength: 0 } : undefined}
        animate={animated ? { pathLength: 1 } : undefined}
        transition={{ duration: animationDuration, ease: 'linear' }}
      />

      {/* Amplitude marker */}
      {showAmplitude && (
        <g>
          <line
            x1={x + 10}
            y1={y}
            x2={x + 10}
            y2={y - amplitude}
            stroke="#EF4444"
            strokeWidth={2}
            markerEnd="url(#arrowhead)"
          />
          <line
            x1={x + 10}
            y1={y}
            x2={x + 10}
            y2={y + amplitude}
            stroke="#EF4444"
            strokeWidth={2}
          />
          {showLabels && (
            <text x={x - 5} y={y - amplitude / 2} fontSize={10} fill="#EF4444" textAnchor="end">
              A
            </text>
          )}
        </g>
      )}

      {/* Wavelength marker */}
      {showWavelength && (
        <g>
          <line
            x1={x + wavelength * 0.25}
            y1={y + amplitude + 15}
            x2={x + wavelength * 1.25}
            y2={y + amplitude + 15}
            stroke="#10B981"
            strokeWidth={2}
          />
          {showLabels && (
            <text
              x={x + wavelength * 0.75}
              y={y + amplitude + 30}
              fontSize={10}
              fill="#10B981"
              textAnchor="middle"
            >
              λ (wavelength)
            </text>
          )}
        </g>
      )}
    </g>
  );
};

export default Wave;

