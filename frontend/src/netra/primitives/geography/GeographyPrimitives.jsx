/**
 * 🌍 GEOGRAPHY PRIMITIVES
 * =======================
 * 
 * Visual components for geography and earth science.
 * Natural, earth-toned representations.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PRIMITIVE_THEMES } from '../UniversalPrimitives';

const theme = PRIMITIVE_THEMES.geography;

/**
 * Mountain - Mountain range representation
 */
export const Mountain = ({
  x = 0,
  y = 100,
  width = 80,
  height = 60,
  snowCap = true,
  color = '#78716C',
  label = '',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, y: y + 20 } : false}
    animate={{ opacity: 1, y }}
  >
    {/* Mountain body */}
    <polygon
      points={`${x},${y} ${x + width / 2},${y - height} ${x + width},${y}`}
      fill={color}
      stroke="#57534E"
      strokeWidth={1}
    />
    
    {/* Snow cap */}
    {snowCap && (
      <polygon
        points={`${x + width * 0.35},${y - height * 0.6} ${x + width / 2},${y - height} ${x + width * 0.65},${y - height * 0.6}`}
        fill="white"
        stroke="#E5E7EB"
        strokeWidth={1}
      />
    )}
    
    {label && (
      <text x={x + width / 2} y={y + 15} textAnchor="middle" fontSize={10} fill="#64748B">
        {label}
      </text>
    )}
  </motion.g>
);

/**
 * River - Flowing water representation
 */
export const River = ({
  points = [[0, 50], [50, 60], [100, 55], [150, 70]], // [[x,y], ...]
  width = 8,
  color = theme.secondary,
  label = '',
  animate = true,
}) => {
  const pathData = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`
  ).join(' ');
  
  return (
    <motion.g>
      <motion.path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1 }}
      />
      {/* Subtle shine */}
      <motion.path
        d={pathData}
        fill="none"
        stroke="white"
        strokeWidth={width * 0.3}
        strokeLinecap="round"
        opacity={0.4}
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1, delay: 0.2 }}
      />
      {label && (
        <text
          x={points[Math.floor(points.length / 2)][0]}
          y={points[Math.floor(points.length / 2)][1] - 12}
          fontSize={10}
          fill={color}
          fontStyle="italic"
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

/**
 * Landmass - Continent or country shape
 */
export const Landmass = ({
  cx = 100,
  cy = 100,
  width = 120,
  height = 80,
  shape = 'organic', // organic, rectangle
  color = theme.primary,
  label = '',
  capital = '',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scale: 0.9 } : false}
    animate={{ opacity: 1, scale: 1 }}
  >
    {shape === 'organic' ? (
      <path
        d={`M ${cx - width * 0.4} ${cy - height * 0.2}
           Q ${cx - width * 0.5} ${cy - height * 0.4} ${cx - width * 0.1} ${cy - height * 0.45}
           Q ${cx + width * 0.3} ${cy - height * 0.5} ${cx + width * 0.45} ${cy - height * 0.15}
           Q ${cx + width * 0.5} ${cy + height * 0.2} ${cx + width * 0.3} ${cy + height * 0.4}
           Q ${cx} ${cy + height * 0.5} ${cx - width * 0.3} ${cy + height * 0.35}
           Q ${cx - width * 0.5} ${cy + height * 0.1} ${cx - width * 0.4} ${cy - height * 0.2} Z`}
        fill={`${color}30`}
        stroke={color}
        strokeWidth={2}
      />
    ) : (
      <rect
        x={cx - width / 2}
        y={cy - height / 2}
        width={width}
        height={height}
        rx={8}
        fill={`${color}30`}
        stroke={color}
        strokeWidth={2}
      />
    )}
    
    {/* Label */}
    <text x={cx} y={cy + 4} textAnchor="middle" fontSize={13} fontWeight={600} fill={color}>
      {label}
    </text>
    
    {/* Capital marker */}
    {capital && (
      <>
        <circle cx={cx} cy={cy - 15} r={4} fill={theme.accent} stroke="white" strokeWidth={1} />
        <text x={cx + 8} y={cy - 12} fontSize={9} fill={theme.accent}>{capital}</text>
      </>
    )}
  </motion.g>
);

/**
 * Climate Zone - For climate/biome representation
 */
export const ClimateZone = ({
  x = 0,
  y = 0,
  width = 100,
  height = 40,
  type = 'tropical', // tropical, temperate, polar, desert, etc.
  label = '',
  animate = true,
}) => {
  const climateColors = {
    tropical: '#22C55E',
    temperate: '#84CC16',
    polar: '#E0F2FE',
    desert: '#FCD34D',
    mediterranean: '#FB923C',
    continental: '#A3E635',
    oceanic: '#38BDF8',
  };
  
  const color = climateColors[type] || theme.primary;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scaleX: 0 } : false}
      animate={{ opacity: 1, scaleX: 1 }}
      style={{ transformOrigin: `${x}px ${y}px` }}
    >
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={color}
        opacity={0.6}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 + 4}
        textAnchor="middle"
        fontSize={11}
        fontWeight={600}
        fill="#1E293B"
      >
        {label || type.charAt(0).toUpperCase() + type.slice(1)}
      </text>
    </motion.g>
  );
};

/**
 * Compass Rose - Direction indicator
 */
export const CompassRose = ({
  cx = 50,
  cy = 50,
  size = 40,
  color = theme.primary,
  showLabels = true,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, rotate: -45 } : false}
    animate={{ opacity: 1, rotate: 0 }}
    style={{ transformOrigin: `${cx}px ${cy}px` }}
  >
    {/* Main star */}
    <polygon
      points={`${cx},${cy - size} ${cx + size * 0.15},${cy} ${cx},${cy + size} ${cx - size * 0.15},${cy}`}
      fill={color}
    />
    <polygon
      points={`${cx - size},${cy} ${cx},${cy - size * 0.15} ${cx + size},${cy} ${cx},${cy + size * 0.15}`}
      fill={`${color}80`}
    />
    
    {/* Center circle */}
    <circle cx={cx} cy={cy} r={size * 0.15} fill="white" stroke={color} strokeWidth={1} />
    
    {/* Direction labels */}
    {showLabels && (
      <>
        <text x={cx} y={cy - size - 8} textAnchor="middle" fontSize={12} fontWeight={700} fill={color}>N</text>
        <text x={cx + size + 8} y={cy + 4} textAnchor="middle" fontSize={10} fill={color}>E</text>
        <text x={cx} y={cy + size + 14} textAnchor="middle" fontSize={10} fill={color}>S</text>
        <text x={cx - size - 8} y={cy + 4} textAnchor="middle" fontSize={10} fill={color}>W</text>
      </>
    )}
  </motion.g>
);

/**
 * Scale Bar - Distance scale
 */
export const ScaleBar = ({
  x = 0,
  y = 0,
  length = 100,
  label = '100 km',
  color = '#64748B',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
  >
    <line x1={x} y1={y} x2={x + length} y2={y} stroke={color} strokeWidth={3} />
    <line x1={x} y1={y - 5} x2={x} y2={y + 5} stroke={color} strokeWidth={2} />
    <line x1={x + length} y1={y - 5} x2={x + length} y2={y + 5} stroke={color} strokeWidth={2} />
    <text x={x + length / 2} y={y + 15} textAnchor="middle" fontSize={10} fill={color}>
      {label}
    </text>
  </motion.g>
);

/**
 * Population Indicator - For demographic data
 */
export const PopulationIndicator = ({
  cx = 50,
  cy = 50,
  population = 1000000,
  maxPopulation = 10000000,
  label = '',
  color = theme.accent,
  animate = true,
}) => {
  const minSize = 15;
  const maxSize = 50;
  const size = minSize + (population / maxPopulation) * (maxSize - minSize);
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0 } : false}
      animate={{ opacity: 1, scale: 1 }}
    >
      <circle cx={cx} cy={cy} r={size} fill={`${color}50`} stroke={color} strokeWidth={2} />
      <text x={cx} y={cy + 4} textAnchor="middle" fontSize={10} fontWeight={600} fill={color}>
        {population >= 1000000 ? `${(population / 1000000).toFixed(1)}M` : `${(population / 1000).toFixed(0)}K`}
      </text>
      {label && (
        <text x={cx} y={cy + size + 12} textAnchor="middle" fontSize={9} fill="#64748B">
          {label}
        </text>
      )}
    </motion.g>
  );
};

// Registry
export const GEOGRAPHY_PRIMITIVES = {
  mountain: Mountain,
  river: River,
  landmass: Landmass,
  country: Landmass,
  continent: Landmass,
  climate_zone: ClimateZone,
  compass: CompassRose,
  compass_rose: CompassRose,
  scale_bar: ScaleBar,
  population: PopulationIndicator,
};

export default GEOGRAPHY_PRIMITIVES;

