/**
 * 📜 HISTORY PRIMITIVES
 * =====================
 * 
 * Visual components for history and social studies.
 * Vintage, timeline-oriented representations.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PRIMITIVE_THEMES } from '../UniversalPrimitives';

const theme = PRIMITIVE_THEMES.history;

/**
 * Era Block - Represents a historical period
 */
export const EraBlock = ({
  x = 0,
  y = 0,
  width = 120,
  height = 60,
  era = '',
  years = '',
  color = theme.primary,
  icon = '', // Optional emoji
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, y: y + 20 } : false}
    animate={{ opacity: 1, y }}
    transition={{ duration: 0.4 }}
  >
    {/* Parchment-style background */}
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      rx={4}
      fill={`${color}15`}
      stroke={color}
      strokeWidth={2}
    />
    {/* Decorative corner */}
    <path
      d={`M ${x + width - 15} ${y} L ${x + width} ${y + 15} L ${x + width} ${y}`}
      fill={`${color}30`}
    />
    
    {/* Era name */}
    <text
      x={x + width / 2}
      y={y + height / 2 - 5}
      textAnchor="middle"
      fontSize={13}
      fontWeight={700}
      fill={color}
    >
      {icon} {era}
    </text>
    
    {/* Years */}
    <text
      x={x + width / 2}
      y={y + height / 2 + 12}
      textAnchor="middle"
      fontSize={10}
      fill="#78716C"
    >
      {years}
    </text>
  </motion.g>
);

/**
 * Historical Timeline - Horizontal timeline with events
 */
export const HistoricalTimeline = ({
  x = 30,
  y = 100,
  length = 400,
  events = [], // [{year, label, type: 'event'|'era'}]
  color = theme.primary,
  animate = true,
}) => {
  const minYear = Math.min(...events.map(e => e.year));
  const maxYear = Math.max(...events.map(e => e.year));
  const range = maxYear - minYear || 1;
  
  const getX = (year) => x + ((year - minYear) / range) * length;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
    >
      {/* Main line (rope style) */}
      <line
        x1={x}
        y1={y}
        x2={x + length}
        y2={y}
        stroke={color}
        strokeWidth={4}
        strokeLinecap="round"
      />
      
      {/* Year markers */}
      <text x={x} y={y + 20} fontSize={10} fill="#78716C">{minYear}</text>
      <text x={x + length} y={y + 20} fontSize={10} fill="#78716C" textAnchor="end">{maxYear}</text>
      
      {/* Events */}
      {events.map((event, i) => (
        <motion.g
          key={i}
          initial={animate ? { opacity: 0, scale: 0 } : false}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 + i * 0.1 }}
        >
          <circle
            cx={getX(event.year)}
            cy={y}
            r={event.type === 'major' ? 10 : 6}
            fill={event.type === 'major' ? theme.secondary : color}
            stroke="white"
            strokeWidth={2}
          />
          <text
            x={getX(event.year)}
            y={y - 15}
            textAnchor="middle"
            fontSize={10}
            fontWeight={event.type === 'major' ? 700 : 400}
            fill={color}
          >
            {event.year}
          </text>
          <text
            x={getX(event.year)}
            y={y + 35}
            textAnchor="middle"
            fontSize={9}
            fill="#64748B"
            style={{ maxWidth: 60 }}
          >
            {event.label?.slice(0, 15)}
          </text>
        </motion.g>
      ))}
    </motion.g>
  );
};

/**
 * Map Region - Simplified territory/region
 */
export const MapRegion = ({
  cx = 100,
  cy = 100,
  size = 80,
  label = '',
  color = theme.primary,
  shape = 'blob', // blob, rectangle, oval
  animate = true,
}) => {
  const renderShape = () => {
    switch (shape) {
      case 'rectangle':
        return <rect x={cx - size * 0.6} y={cy - size * 0.4} width={size * 1.2} height={size * 0.8} rx={4} fill={`${color}30`} stroke={color} strokeWidth={2} />;
      case 'oval':
        return <ellipse cx={cx} cy={cy} rx={size * 0.6} ry={size * 0.4} fill={`${color}30`} stroke={color} strokeWidth={2} />;
      default: // blob
        return (
          <path
            d={`M ${cx - size * 0.5} ${cy} 
               Q ${cx - size * 0.4} ${cy - size * 0.4} ${cx} ${cy - size * 0.35}
               Q ${cx + size * 0.4} ${cy - size * 0.4} ${cx + size * 0.5} ${cy}
               Q ${cx + size * 0.4} ${cy + size * 0.4} ${cx} ${cy + size * 0.35}
               Q ${cx - size * 0.4} ${cy + size * 0.4} ${cx - size * 0.5} ${cy} Z`}
            fill={`${color}30`}
            stroke={color}
            strokeWidth={2}
          />
        );
    }
  };
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.9 } : false}
      animate={{ opacity: 1, scale: 1 }}
    >
      {renderShape()}
      <text x={cx} y={cy + 4} textAnchor="middle" fontSize={12} fontWeight={600} fill={color}>
        {label}
      </text>
    </motion.g>
  );
};

/**
 * Figure Icon - Historical figure representation
 */
export const FigureIcon = ({
  cx = 50,
  cy = 50,
  name = '',
  role = '',
  color = theme.primary,
  size = 40,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
  >
    {/* Simple figure silhouette */}
    <circle cx={cx} cy={cy - size * 0.2} r={size * 0.25} fill={color} />
    <ellipse cx={cx} cy={cy + size * 0.2} rx={size * 0.3} ry={size * 0.25} fill={color} />
    
    {/* Name and role */}
    <text x={cx} y={cy + size * 0.6} textAnchor="middle" fontSize={11} fontWeight={600} fill={color}>
      {name}
    </text>
    {role && (
      <text x={cx} y={cy + size * 0.75} textAnchor="middle" fontSize={9} fill="#78716C">
        {role}
      </text>
    )}
  </motion.g>
);

/**
 * Cause Effect Chain - For historical cause-effect
 */
export const CauseEffectChain = ({
  x = 0,
  y = 0,
  items = [], // [{label, type: 'cause'|'effect'}]
  color = theme.primary,
  animate = true,
}) => (
  <motion.g initial={animate ? { opacity: 0 } : false} animate={{ opacity: 1 }}>
    {items.map((item, i) => (
      <motion.g
        key={i}
        initial={animate ? { opacity: 0, x: x - 20 } : false}
        animate={{ opacity: 1, x: x + i * 120 }}
        transition={{ delay: i * 0.15 }}
      >
        <rect
          x={x + i * 120}
          y={y}
          width={100}
          height={50}
          rx={item.type === 'cause' ? 25 : 8}
          fill={item.type === 'cause' ? `${theme.secondary}20` : `${color}20`}
          stroke={item.type === 'cause' ? theme.secondary : color}
          strokeWidth={2}
        />
        <text
          x={x + i * 120 + 50}
          y={y + 28}
          textAnchor="middle"
          fontSize={10}
          fill={item.type === 'cause' ? theme.secondary : color}
        >
          {item.label?.slice(0, 12)}
        </text>
        
        {/* Arrow to next */}
        {i < items.length - 1 && (
          <polygon
            points={`${x + (i + 1) * 120 - 15},${y + 25} ${x + (i + 1) * 120 - 5},${y + 20} ${x + (i + 1) * 120 - 5},${y + 30}`}
            fill={color}
          />
        )}
      </motion.g>
    ))}
  </motion.g>
);

// Registry
export const HISTORY_PRIMITIVES = {
  era: EraBlock,
  era_block: EraBlock,
  timeline: HistoricalTimeline,
  historical_timeline: HistoricalTimeline,
  region: MapRegion,
  map_region: MapRegion,
  figure: FigureIcon,
  figure_icon: FigureIcon,
  cause_effect_chain: CauseEffectChain,
};

export default HISTORY_PRIMITIVES;

