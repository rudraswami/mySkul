/**
 * 📊 Graph Template
 * =================
 * 
 * Mathematical relationship visualization.
 * Line graphs, bar charts, scatter plots.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const GraphTemplate = ({
  config = {},
  step = 0,
  subject = 'mathematics',
}) => {
  const {
    data = [
      { x: 0, y: 0 },
      { x: 1, y: 2 },
      { x: 2, y: 4 },
      { x: 3, y: 6 },
      { x: 4, y: 8 },
    ],
    secondary_data = null,
    x_label = 'Time (s)',
    y_label = 'Distance (m)',
    title = 'Graph Analysis',
    subtitle = 'See the relationship!',
    equation = 'y = 2x',
    graph_type = 'line', // line, bar, scatter
    memory_hook = 'The slope tells the story! 📈',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.physics;
  
  const padding = { top: 80, right: 60, bottom: 60, left: 70 };
  const WIDTH = 500;
  const HEIGHT = 400;
  const plotWidth = WIDTH - padding.left - padding.right;
  const plotHeight = HEIGHT - padding.top - padding.bottom;

  const xRange = useMemo(() => {
    if (data.length === 0) return { min: 0, max: 10 };
    const values = data.map(d => d.x);
    return { min: Math.min(...values), max: Math.max(...values) };
  }, [data]);

  const yRange = useMemo(() => {
    if (data.length === 0) return { min: 0, max: 10 };
    const values = data.map(d => d.y);
    return { min: 0, max: Math.max(...values) * 1.1 };
  }, [data]);

  const scaleX = (val) => padding.left + ((val - xRange.min) / (xRange.max - xRange.min)) * plotWidth;
  const scaleY = (val) => padding.top + plotHeight - ((val - yRange.min) / (yRange.max - yRange.min)) * plotHeight;

  const linePath = useMemo(() => {
    if (data.length < 2) return '';
    return data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(d.x)} ${scaleY(d.y)}`).join(' ');
  }, [data]);

  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={30}
        fontSize={22}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        📊 {title}
      </motion.text>
      <motion.text
        x={250} y={52}
        fontSize={14}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {subtitle}
      </motion.text>

      {/* Graph background */}
      <rect
        x={padding.left}
        y={padding.top}
        width={plotWidth}
        height={plotHeight}
        fill="white"
        stroke="#E5E7EB"
        strokeWidth={1}
      />

      {/* Grid */}
      {step >= 1 && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 0.3 }}>
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
        </motion.g>
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

      {/* Axis arrows */}
      <polygon points={`${padding.left + plotWidth + 8},${padding.top + plotHeight} ${padding.left + plotWidth},${padding.top + plotHeight - 5} ${padding.left + plotWidth},${padding.top + plotHeight + 5}`} fill="#374151" />
      <polygon points={`${padding.left},${padding.top - 8} ${padding.left - 5},${padding.top} ${padding.left + 5},${padding.top}`} fill="#374151" />

      {/* Axis labels */}
      <text
        x={padding.left + plotWidth / 2}
        y={HEIGHT - 15}
        fontSize={14}
        textAnchor="middle"
        fill="#374151"
        fontWeight="bold"
      >
        {x_label}
      </text>
      <text
        x={20}
        y={padding.top + plotHeight / 2}
        fontSize={14}
        textAnchor="middle"
        fill="#374151"
        fontWeight="bold"
        transform={`rotate(-90, 20, ${padding.top + plotHeight / 2})`}
      >
        {y_label}
      </text>

      {/* Axis values */}
      {[0, 0.5, 1].map((t, i) => {
        const xVal = xRange.min + t * (xRange.max - xRange.min);
        const yVal = yRange.min + (1 - t) * (yRange.max - yRange.min);
        return (
          <g key={i}>
            <text x={scaleX(xVal)} y={padding.top + plotHeight + 20} fontSize={11} textAnchor="middle" fill="#636E72">
              {xVal.toFixed(0)}
            </text>
            <text x={padding.left - 10} y={padding.top + t * plotHeight + 4} fontSize={11} textAnchor="end" fill="#636E72">
              {yVal.toFixed(0)}
            </text>
          </g>
        );
      })}

      {/* Data line */}
      {step >= 2 && graph_type === 'line' && linePath && (
        <motion.path
          d={linePath}
          stroke={theme.primary}
          strokeWidth={4}
          fill="none"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      )}

      {/* Data points */}
      {step >= 2 && data.map((d, i) => (
        <motion.circle
          key={i}
          cx={scaleX(d.x)}
          cy={scaleY(d.y)}
          r={6}
          fill={theme.primary}
          stroke="white"
          strokeWidth={2}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5 + i * 0.1 }}
        />
      ))}

      {/* Equation box */}
      {step >= 3 && equation && (
        <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.5 }}>
          <rect
            x={padding.left + plotWidth - 100}
            y={padding.top + 10}
            width={95}
            height={35}
            rx={8}
            fill="#FEF3C7"
            stroke={theme.primary}
            strokeWidth={2}
          />
          <text
            x={padding.left + plotWidth - 52}
            y={padding.top + 33}
            fontSize={16}
            fontWeight="bold"
            textAnchor="middle"
            fill={theme.primary}
            fontFamily="'Caveat', cursive"
          >
            {equation}
          </text>
        </motion.g>
      )}

      {/* Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={100} y={365} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={390} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default GraphTemplate;

