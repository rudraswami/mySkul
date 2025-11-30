/**
 * 📊 Graph Primitive
 * ==================
 * 
 * Animated graph for mathematical/physics relationships.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

const Graph = ({
  x = 0,
  y = 0,
  width = 250,
  height = 180,
  data = [], // [{x: 0, y: 0}, {x: 1, y: 1}, ...]
  type = 'line', // line, bar, scatter, area
  xLabel = 'X',
  yLabel = 'Y',
  title = '',
  color = '#3B82F6',
  secondaryData = null,
  secondaryColor = '#EF4444',
  showGrid = true,
  showPoints = true,
  animated = true,
  equation = '', // y = mx + c, y = x², etc.
}) => {
  // Calculate scales
  const padding = { top: 30, right: 20, bottom: 35, left: 45 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const xRange = useMemo(() => {
    if (data.length === 0) return { min: 0, max: 10 };
    const values = data.map(d => d.x);
    return { min: Math.min(...values), max: Math.max(...values) };
  }, [data]);

  const yRange = useMemo(() => {
    if (data.length === 0) return { min: 0, max: 10 };
    const values = data.map(d => d.y);
    if (secondaryData) values.push(...secondaryData.map(d => d.y));
    return { min: Math.min(0, ...values), max: Math.max(...values) * 1.1 };
  }, [data, secondaryData]);

  const scaleX = (val) => padding.left + ((val - xRange.min) / (xRange.max - xRange.min)) * plotWidth;
  const scaleY = (val) => padding.top + plotHeight - ((val - yRange.min) / (yRange.max - yRange.min)) * plotHeight;

  // Generate path
  const linePath = useMemo(() => {
    if (data.length < 2) return '';
    return data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(d.x)} ${scaleY(d.y)}`).join(' ');
  }, [data, xRange, yRange]);

  const secondaryPath = useMemo(() => {
    if (!secondaryData || secondaryData.length < 2) return '';
    return secondaryData.map((d, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(d.x)} ${scaleY(d.y)}`).join(' ');
  }, [secondaryData, xRange, yRange]);

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Background */}
      <rect
        x={0}
        y={0}
        width={width}
        height={height}
        rx={8}
        fill="white"
        stroke="#E5E7EB"
        strokeWidth={2}
      />

      {/* Title */}
      {title && (
        <text
          x={width / 2}
          y={18}
          fontSize={14}
          fontWeight="bold"
          textAnchor="middle"
          fill="#1F2937"
        >
          {title}
        </text>
      )}

      {/* Grid */}
      {showGrid && (
        <g opacity={0.3}>
          {[0, 0.25, 0.5, 0.75, 1].map((t, i) => (
            <g key={i}>
              <line
                x1={padding.left}
                y1={padding.top + t * plotHeight}
                x2={padding.left + plotWidth}
                y2={padding.top + t * plotHeight}
                stroke="#9CA3AF"
                strokeWidth={1}
              />
              <line
                x1={padding.left + t * plotWidth}
                y1={padding.top}
                x2={padding.left + t * plotWidth}
                y2={padding.top + plotHeight}
                stroke="#9CA3AF"
                strokeWidth={1}
              />
            </g>
          ))}
        </g>
      )}

      {/* Axes */}
      <line
        x1={padding.left}
        y1={padding.top + plotHeight}
        x2={padding.left + plotWidth}
        y2={padding.top + plotHeight}
        stroke="#374151"
        strokeWidth={2}
      />
      <line
        x1={padding.left}
        y1={padding.top}
        x2={padding.left}
        y2={padding.top + plotHeight}
        stroke="#374151"
        strokeWidth={2}
      />

      {/* Axis labels */}
      <text
        x={padding.left + plotWidth / 2}
        y={height - 5}
        fontSize={12}
        textAnchor="middle"
        fill="#636E72"
      >
        {xLabel}
      </text>
      <text
        x={12}
        y={padding.top + plotHeight / 2}
        fontSize={12}
        textAnchor="middle"
        fill="#636E72"
        transform={`rotate(-90, 12, ${padding.top + plotHeight / 2})`}
      >
        {yLabel}
      </text>

      {/* Main data line */}
      {type === 'line' && linePath && (
        <motion.path
          d={linePath}
          stroke={color}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      )}

      {/* Secondary data line */}
      {secondaryPath && (
        <motion.path
          d={secondaryPath}
          stroke={secondaryColor}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
          strokeDasharray="8 4"
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
        />
      )}

      {/* Data points */}
      {showPoints && type !== 'bar' && data.map((d, i) => (
        <motion.circle
          key={i}
          cx={scaleX(d.x)}
          cy={scaleY(d.y)}
          r={5}
          fill={color}
          initial={animated ? { scale: 0 } : undefined}
          animate={animated ? { scale: 1 } : undefined}
          transition={{ delay: 0.5 + i * 0.1 }}
        />
      ))}

      {/* Bar chart */}
      {type === 'bar' && data.map((d, i) => {
        const barWidth = plotWidth / data.length - 10;
        return (
          <motion.rect
            key={i}
            x={scaleX(d.x) - barWidth / 2}
            y={scaleY(d.y)}
            width={barWidth}
            height={scaleY(0) - scaleY(d.y)}
            fill={color}
            rx={3}
            initial={animated ? { scaleY: 0 } : undefined}
            animate={animated ? { scaleY: 1 } : undefined}
            transition={{ delay: i * 0.1 }}
            style={{ originY: 1 }}
          />
        );
      })}

      {/* Equation display */}
      {equation && (
        <motion.g
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ delay: 1.5 }}
        >
          <rect
            x={width - 100}
            y={padding.top + 5}
            width={90}
            height={25}
            rx={5}
            fill="#FEF3C7"
            stroke={color}
            strokeWidth={1}
          />
          <text
            x={width - 55}
            y={padding.top + 22}
            fontSize={12}
            fontWeight="bold"
            textAnchor="middle"
            fill={color}
            fontFamily="'Caveat', cursive"
          >
            {equation}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default Graph;

