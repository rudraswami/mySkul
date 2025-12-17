/**
 * 🎬 SCENE PRIMITIVES
 * ====================
 * 
 * Rich visual components that render SCENES, not boxes.
 * 
 * These components create:
 * - Realistic environments (ground, sky, surfaces)
 * - Animated actors (sliding blocks, walking people, cars)
 * - Force visualizations (arrows with physics meaning)
 * - Effects (motion trails, heat glow, particle emission)
 * 
 * PRINCIPLE: Every visual tells a story. No rectangles with labels.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { VISUAL_FORMS, OBJECT_TYPES } from '../reasoning/SceneObjectResolver';

// ============================================
// THEME
// ============================================

const SCENE_THEME = {
  colors: {
    ground: '#8B7355',
    groundDark: '#5D4E37',
    sky: '#87CEEB',
    ice: '#B8E5F0',
    carpet: '#8B4513',
    surface: '#D4C4B5',
    force: {
      gravity: '#2C3E50',
      normal: '#3498DB',
      friction: '#E67E22',
      applied: '#E74C3C',
      tension: '#9B59B6',
    },
    actor: {
      block: '#6366F1',
      person: '#F59E0B',
      car: '#EF4444',
      ball: '#22C55E',
    },
    effect: {
      motion: 'rgba(59, 130, 246, 0.4)',
      heat: 'rgba(239, 68, 68, 0.3)',
      chaos: '#EF4444',
    },
  },
  fonts: {
    handwriting: "'Kalam', 'Caveat', cursive",
    technical: "'IBM Plex Mono', monospace",
  },
};

// ============================================
// ENVIRONMENT PRIMITIVES
// ============================================

/**
 * Outdoor Scene Background
 */
export const OutdoorEnvironment = ({
  width = 800,
  height = 600,
  variant = 'day',
  animate = true,
}) => {
  const skyGradient = variant === 'day' 
    ? ['#87CEEB', '#E0F4FF'] 
    : ['#1a1a2e', '#16213e'];
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="env-outdoor"
    >
      {/* Sky gradient */}
      <defs>
        <linearGradient id="sky-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={skyGradient[0]} />
          <stop offset="100%" stopColor={skyGradient[1]} />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={width} height={height * 0.7} fill="url(#sky-gradient)" />
      
      {/* Sun/Moon */}
      <motion.circle
        cx={width * 0.85}
        cy={height * 0.15}
        r={40}
        fill={variant === 'day' ? '#FCD34D' : '#F3F4F6'}
        filter="url(#glow)"
        animate={animate ? { scale: [1, 1.05, 1] } : false}
        transition={{ duration: 3, repeat: Infinity }}
      />
      
      {/* Clouds (day only) */}
      {variant === 'day' && (
        <g className="clouds">
          <Cloud x={100} y={60} scale={1} />
          <Cloud x={300} y={100} scale={0.7} />
          <Cloud x={500} y={50} scale={0.9} />
        </g>
      )}
      
      {/* Distant horizon line */}
      <line 
        x1={0} 
        y1={height * 0.7} 
        x2={width} 
        y2={height * 0.7} 
        stroke="#A5B4C3" 
        strokeWidth={1}
        opacity={0.5}
      />
    </motion.g>
  );
};

const Cloud = ({ x, y, scale = 1 }) => (
  <g transform={`translate(${x}, ${y}) scale(${scale})`}>
    <ellipse cx={0} cy={0} rx={40} ry={20} fill="white" opacity={0.9} />
    <ellipse cx={25} cy={-5} rx={30} ry={18} fill="white" opacity={0.9} />
    <ellipse cx={-20} cy={-3} rx={25} ry={15} fill="white" opacity={0.9} />
  </g>
);

/**
 * Lab/Indoor Background
 */
export const LabEnvironment = ({
  width = 800,
  height = 600,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    className="env-lab"
  >
    {/* Wall */}
    <rect x={0} y={0} width={width} height={height * 0.75} fill="#F1F5F9" />
    
    {/* Grid lines (like graph paper) */}
    <g className="grid-lines" opacity={0.15}>
      {Array.from({ length: Math.floor(width / 30) }).map((_, i) => (
        <line 
          key={`v-${i}`} 
          x1={i * 30} y1={0} 
          x2={i * 30} y2={height * 0.75}
          stroke="#64748B"
          strokeWidth={1}
        />
      ))}
      {Array.from({ length: Math.floor((height * 0.75) / 30) }).map((_, i) => (
        <line 
          key={`h-${i}`} 
          x1={0} y1={i * 30} 
          x2={width} y2={i * 30}
          stroke="#64748B"
          strokeWidth={1}
        />
      ))}
    </g>
    
    {/* Floor */}
    <rect x={0} y={height * 0.75} width={width} height={height * 0.25} fill="#E2E8F0" />
    
    {/* Floor tiles pattern */}
    <g className="floor-tiles" opacity={0.3}>
      {Array.from({ length: Math.floor(width / 60) }).map((_, i) => (
        <rect 
          key={i}
          x={i * 60} 
          y={height * 0.75} 
          width={60} 
          height={height * 0.25}
          fill={i % 2 === 0 ? '#CBD5E1' : 'transparent'}
        />
      ))}
    </g>
  </motion.g>
);

/**
 * Room Interior Background
 */
export const RoomEnvironment = ({
  width = 800,
  height = 600,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    className="env-room"
  >
    {/* Wall */}
    <rect x={0} y={0} width={width} height={height * 0.65} fill="#FEF3C7" />
    
    {/* Baseboard */}
    <rect x={0} y={height * 0.60} width={width} height={height * 0.05} fill="#92400E" />
    
    {/* Floor (wooden) */}
    <rect x={0} y={height * 0.65} width={width} height={height * 0.35} fill="#D97706" />
    
    {/* Wood grain pattern */}
    <g className="wood-grain" opacity={0.2}>
      {Array.from({ length: 6 }).map((_, i) => (
        <line 
          key={i}
          x1={0} 
          y1={height * 0.65 + i * 30} 
          x2={width} 
          y2={height * 0.65 + i * 30}
          stroke="#78350F"
          strokeWidth={1}
        />
      ))}
    </g>
  </motion.g>
);

// ============================================
// SURFACE PRIMITIVES
// ============================================

/**
 * Realistic Ground Surface - PROMINENT brown ground
 */
export const GroundSurface = ({
  y = 300,
  width = 800,
  height = 200,  // Height of ground area
  variant = 'rough',  // rough, smooth, grass
  animate = true,
  delay = 0,
}) => {
  const surfaceColor = {
    rough: '#8B4513',  // Rich brown for rough surface
    smooth: '#A0826D',  // Lighter brown for smooth
    grass: '#228B22',  // Forest green
  }[variant] || '#8B4513';
  
  const lighterColor = variant === 'rough' ? '#A0522D' : surfaceColor;
  const darkerColor = variant === 'rough' ? '#5D3A1A' : '#4A3728';
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, y: y + 20 } : false}
      animate={{ opacity: 1, y }}
      transition={{ delay, duration: 0.5 }}
      className="surface-ground"
    >
      {/* Solid ground fill - PROMINENT */}
      <rect
        x={0}
        y={y}
        width={width}
        height={height || 200}
        fill={surfaceColor}
      />
      
      {/* Top edge highlight */}
      <rect
        x={0}
        y={y}
        width={width}
        height={8}
        fill={lighterColor}
      />
      
      {/* Ground texture line */}
      <line
        x1={0}
        y1={y + 3}
        x2={width}
        y2={y + 3}
        stroke={darkerColor}
        strokeWidth={2}
        opacity={0.5}
      />
      
      {/* Hatching for depth effect */}
      <g className="ground-hatching" opacity={0.4}>
        {Array.from({ length: Math.floor(width / 15) }).map((_, i) => (
          <line
            key={i}
            x1={i * 15 + 5}
            y1={y + 10}
            x2={i * 15 - 10}
            y2={y + 35}
            stroke={darkerColor}
            strokeWidth={1.5}
          />
        ))}
      </g>
      
      {/* Surface texture based on variant */}
      {variant === 'rough' && (
        <g className="rough-texture">
          {/* Bumpy texture circles */}
          {Array.from({ length: 20 }).map((_, i) => (
            <circle
              key={i}
              cx={30 + i * 40}
              cy={y + 2}
              r={3 + (i % 3)}
              fill={lighterColor}
              opacity={0.6}
            />
          ))}
          {/* Small pebbles */}
          {Array.from({ length: 30 }).map((_, i) => (
            <ellipse
              key={`pebble-${i}`}
              cx={15 + i * 27}
              cy={y + 20 + (i % 4) * 8}
              rx={4 + (i % 3)}
              ry={3}
              fill={i % 2 === 0 ? lighterColor : darkerColor}
              opacity={0.3}
            />
          ))}
        </g>
      )}
      
      {variant === 'grass' && (
        <g className="grass-blades">
          {Array.from({ length: 50 }).map((_, i) => (
            <path
              key={i}
              d={`M ${i * 16} ${y} Q ${i * 16 + 4} ${y - 12} ${i * 16 + 2} ${y - 18}`}
              fill="none"
              stroke="#15803D"
              strokeWidth={2}
            />
          ))}
        </g>
      )}
    </motion.g>
  );
};

/**
 * Ice Surface (smooth, low friction)
 */
export const IceSurface = ({
  y = 500,
  width = 800,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ delay, duration: 0.5 }}
    className="surface-ice"
  >
    {/* Ice layer */}
    <rect
      x={0}
      y={y}
      width={width}
      height={30}
      fill={SCENE_THEME.colors.ice}
      opacity={0.8}
    />
    
    {/* Ice surface line */}
    <line
      x1={0}
      y1={y}
      x2={width}
      y2={y}
      stroke="#67E8F9"
      strokeWidth={3}
    />
    
    {/* Reflections */}
    <g className="ice-reflections">
      {Array.from({ length: 8 }).map((_, i) => (
        <line
          key={i}
          x1={50 + i * 100}
          y1={y + 5}
          x2={50 + i * 100 + 40}
          y2={y + 5}
          stroke="white"
          strokeWidth={2}
          opacity={0.6}
        />
      ))}
    </g>
    
    {/* Sparkles */}
    <g className="ice-sparkles">
      {Array.from({ length: 5 }).map((_, i) => (
        <motion.circle
          key={i}
          cx={100 + i * 150}
          cy={y - 3}
          r={2}
          fill="white"
          animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
        />
      ))}
    </g>
  </motion.g>
);

/**
 * Carpet Surface (high friction)
 */
export const CarpetSurface = ({
  y = 500,
  width = 800,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ delay, duration: 0.5 }}
    className="surface-carpet"
  >
    {/* Carpet base */}
    <rect
      x={0}
      y={y}
      width={width}
      height={25}
      fill={SCENE_THEME.colors.carpet}
    />
    
    {/* Carpet texture (fuzzy top) */}
    <g className="carpet-texture">
      {Array.from({ length: 80 }).map((_, i) => (
        <line
          key={i}
          x1={i * 10 + Math.random() * 5}
          y1={y}
          x2={i * 10 + Math.random() * 5}
          y2={y - 4 - Math.random() * 3}
          stroke="#A0522D"
          strokeWidth={3}
        />
      ))}
    </g>
  </motion.g>
);

/**
 * Microscopic Surface (zoomed view showing bumps)
 */
export const MicroscopicSurface = ({
  y = 400,
  width = 800,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scale: 0.9 } : false}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.6 }}
    className="surface-microscopic"
  >
    {/* Zoomed frame */}
    <rect
      x={50}
      y={y - 100}
      width={width - 100}
      height={200}
      fill="#F1F5F9"
      stroke="#64748B"
      strokeWidth={2}
      rx={8}
    />
    
    {/* Magnification indicator */}
    <text x={70} y={y - 80} fontSize={12} fill="#64748B" fontFamily={SCENE_THEME.fonts.technical}>
      100x Magnification
    </text>
    
    {/* Surface bumps (molecules) */}
    <g className="surface-bumps">
      {Array.from({ length: 12 }).map((_, i) => (
        <motion.g key={i} transform={`translate(${100 + i * 55}, ${y})`}>
          {/* Bump shape */}
          <ellipse
            cx={0}
            cy={-20}
            rx={20}
            ry={25}
            fill="#94A3B8"
            stroke="#64748B"
            strokeWidth={2}
          />
          {/* Molecules inside */}
          <circle cx={-8} cy={-15} r={5} fill="#3B82F6" opacity={0.7} />
          <circle cx={8} cy={-18} r={4} fill="#3B82F6" opacity={0.7} />
          <circle cx={0} cy={-25} r={4} fill="#3B82F6" opacity={0.7} />
        </motion.g>
      ))}
    </g>
    
    {/* Interlocking indicator */}
    <g className="interlocking">
      {Array.from({ length: 6 }).map((_, i) => (
        <motion.path
          key={i}
          d={`M ${180 + i * 100} ${y - 45} L ${180 + i * 100} ${y + 10}`}
          stroke="#EF4444"
          strokeWidth={2}
          strokeDasharray="4 2"
          opacity={0.6}
          animate={{ opacity: [0.3, 0.8, 0.3] }}
          transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
        />
      ))}
    </g>
    
    {/* Label */}
    <text x={width / 2} y={y + 80} textAnchor="middle" fontSize={14} fill="#374151" fontFamily={SCENE_THEME.fonts.handwriting}>
      Surface irregularities cause friction
    </text>
  </motion.g>
);

// ============================================
// ACTOR PRIMITIVES
// ============================================

/**
 * Sliding Block (classic physics) - PROMINENT wooden crate style
 */
export const SlidingBlock = ({
  x = 100,
  y = 250,
  width = 100,
  height = 70,
  label = 'Block',
  color = '#D2691E',  // Chocolate brown - crate color
  moving = false,
  direction = 'right',
  animate = true,
  delay = 0,
}) => {
  const darkerColor = '#8B4513';  // Darker brown for edges
  const lighterColor = '#DEB887';  // Light tan for highlights
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.8 } : false}
      animate={{ 
        opacity: 1, 
        scale: 1,
        x: moving ? [0, direction === 'right' ? 30 : -30, 0] : 0,
      }}
      transition={{ 
        delay, 
        duration: moving ? 2 : 0.5, 
        repeat: moving ? Infinity : 0,
        ease: 'easeInOut',
      }}
      className="actor-block"
    >
      {/* Shadow */}
      <ellipse
        cx={x + width / 2}
        cy={y + height + 5}
        rx={width / 2 - 5}
        ry={8}
        fill="rgba(0,0,0,0.2)"
      />
      
      {/* Block body - main crate */}
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={6}
        fill={color}
        stroke={darkerColor}
        strokeWidth={3}
      />
      
      {/* Crate texture - horizontal lines */}
      <line x1={x} y1={y + height * 0.33} x2={x + width} y2={y + height * 0.33} stroke={darkerColor} strokeWidth={2} opacity={0.5} />
      <line x1={x} y1={y + height * 0.66} x2={x + width} y2={y + height * 0.66} stroke={darkerColor} strokeWidth={2} opacity={0.5} />
      
      {/* 3D effect - top edge highlight */}
      <rect
        x={x + 3}
        y={y + 3}
        width={width - 6}
        height={12}
        rx={3}
        fill={lighterColor}
        opacity={0.4}
      />
      
      {/* 3D effect - side shadow */}
      <rect
        x={x + width - 8}
        y={y + 3}
        width={5}
        height={height - 6}
        fill={darkerColor}
        opacity={0.3}
      />
      
      {/* Label */}
      {label && (
        <text
          x={x + width / 2}
          y={y + height / 2 + 6}
          textAnchor="middle"
          fontSize={20}
          fontWeight={700}
          fill="white"
          fontFamily={SCENE_THEME.fonts.handwriting}
          stroke={darkerColor}
          strokeWidth={0.5}
        >
          {label}
        </text>
      )}
      
      {/* Mass indicator */}
      <text
        x={x + width / 2}
        y={y + height - 8}
        textAnchor="middle"
        fontSize={12}
        fill="white"
        opacity={0.8}
        fontFamily="sans-serif"
      >
        m
      </text>
    </motion.g>
  );
};

/**
 * Rolling Ball
 */
export const RollingBall = ({
  x = 100,
  y = 480,
  radius = 30,
  color = SCENE_THEME.colors.actor.ball,
  rolling = false,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scale: 0.5 } : false}
    animate={{ 
      opacity: 1, 
      scale: 1,
      x: rolling ? [0, 50, 0] : 0,
    }}
    transition={{ delay, duration: rolling ? 2 : 0.4, repeat: rolling ? Infinity : 0 }}
    className="actor-ball"
  >
    {/* Shadow */}
    <ellipse
      cx={x}
      cy={y + radius}
      rx={radius * 0.8}
      ry={radius * 0.2}
      fill="rgba(0,0,0,0.15)"
    />
    
    {/* Ball */}
    <circle
      cx={x}
      cy={y}
      r={radius}
      fill={color}
      stroke={`${color}CC`}
      strokeWidth={2}
    />
    
    {/* Highlight */}
    <circle
      cx={x - radius * 0.3}
      cy={y - radius * 0.3}
      r={radius * 0.2}
      fill="white"
      opacity={0.4}
    />
    
    {/* Rolling indicator (stripe) */}
    {rolling && (
      <motion.line
        x1={x - radius}
        y1={y}
        x2={x + radius}
        y2={y}
        stroke="white"
        strokeWidth={3}
        opacity={0.3}
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        style={{ transformOrigin: `${x}px ${y}px` }}
      />
    )}
  </motion.g>
);

/**
 * Person Figure (stick figure style)
 */
export const PersonFigure = ({
  x = 100,
  y = 500,  // Ground level
  action = 'standing',  // standing, walking, sliding
  color = SCENE_THEME.colors.actor.person,
  animate = true,
  delay = 0,
}) => {
  const headY = y - 80;
  const torsoEndY = y - 40;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, x: x - 20 } : false}
      animate={{ 
        opacity: 1, 
        x: action === 'sliding' ? [x, x + 60, x] : x,
      }}
      transition={{ delay, duration: action === 'sliding' ? 2 : 0.5, repeat: action === 'sliding' ? Infinity : 0 }}
      className="actor-person"
    >
      {/* Head */}
      <circle cx={x} cy={headY} r={12} fill={color} stroke={`${color}CC`} strokeWidth={2} />
      
      {/* Body */}
      <line x1={x} y1={headY + 12} x2={x} y2={torsoEndY} stroke={color} strokeWidth={4} strokeLinecap="round" />
      
      {/* Arms */}
      {action === 'standing' && (
        <>
          <line x1={x} y1={headY + 20} x2={x - 20} y2={headY + 35} stroke={color} strokeWidth={3} strokeLinecap="round" />
          <line x1={x} y1={headY + 20} x2={x + 20} y2={headY + 35} stroke={color} strokeWidth={3} strokeLinecap="round" />
        </>
      )}
      {(action === 'walking' || action === 'sliding') && (
        <>
          <motion.line 
            x1={x} y1={headY + 20} 
            x2={x - 25} y2={headY + 40}
            stroke={color} strokeWidth={3} strokeLinecap="round"
            animate={action === 'walking' ? { x2: [x - 25, x - 15, x - 25] } : false}
            transition={{ duration: 0.5, repeat: Infinity }}
          />
          <motion.line 
            x1={x} y1={headY + 20} 
            x2={x + 25} y2={headY + 40}
            stroke={color} strokeWidth={3} strokeLinecap="round"
            animate={action === 'walking' ? { x2: [x + 15, x + 25, x + 15] } : false}
            transition={{ duration: 0.5, repeat: Infinity }}
          />
        </>
      )}
      
      {/* Legs */}
      <motion.line 
        x1={x} y1={torsoEndY} 
        x2={x - 15} y2={y}
        stroke={color} strokeWidth={3} strokeLinecap="round"
        animate={action === 'walking' ? { x2: [x - 15, x - 5, x - 15] } : false}
        transition={{ duration: 0.5, repeat: Infinity }}
      />
      <motion.line 
        x1={x} y1={torsoEndY} 
        x2={x + 15} y2={y}
        stroke={color} strokeWidth={3} strokeLinecap="round"
        animate={action === 'walking' ? { x2: [x + 5, x + 15, x + 5] } : false}
        transition={{ duration: 0.5, repeat: Infinity }}
      />
      
      {/* Sliding effect */}
      {action === 'sliding' && (
        <motion.path
          d={`M ${x - 30} ${y - 5} Q ${x - 50} ${y - 5} ${x - 60} ${y - 10}`}
          stroke={SCENE_THEME.colors.effect.motion}
          strokeWidth={3}
          fill="none"
          opacity={0.6}
          strokeLinecap="round"
        />
      )}
    </motion.g>
  );
};

/**
 * Car Figure
 */
export const CarFigure = ({
  x = 100,
  y = 480,
  color = SCENE_THEME.colors.actor.car,
  moving = false,
  braking = false,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, x: x - 50 } : false}
    animate={{ 
      opacity: 1, 
      x: moving ? [x, x + 100, x] : x,
    }}
    transition={{ delay, duration: moving ? 3 : 0.6, repeat: moving ? Infinity : 0 }}
    className="actor-car"
  >
    {/* Shadow */}
    <ellipse cx={x + 60} cy={y + 15} rx={65} ry={8} fill="rgba(0,0,0,0.15)" />
    
    {/* Car body */}
    <path
      d={`M ${x} ${y} L ${x + 20} ${y - 25} L ${x + 100} ${y - 25} L ${x + 120} ${y} Z`}
      fill={color}
      stroke={`${color}CC`}
      strokeWidth={2}
    />
    
    {/* Cabin */}
    <path
      d={`M ${x + 30} ${y - 25} L ${x + 40} ${y - 45} L ${x + 80} ${y - 45} L ${x + 90} ${y - 25} Z`}
      fill="#64748B"
      stroke="#475569"
      strokeWidth={2}
    />
    
    {/* Windows */}
    <rect x={x + 42} y={y - 43} width={16} height={15} rx={2} fill="#A5F3FC" opacity={0.8} />
    <rect x={x + 62} y={y - 43} width={16} height={15} rx={2} fill="#A5F3FC" opacity={0.8} />
    
    {/* Wheels */}
    <circle cx={x + 25} cy={y + 5} r={12} fill="#1F2937" stroke="#374151" strokeWidth={2} />
    <circle cx={x + 95} cy={y + 5} r={12} fill="#1F2937" stroke="#374151" strokeWidth={2} />
    <circle cx={x + 25} cy={y + 5} r={5} fill="#6B7280" />
    <circle cx={x + 95} cy={y + 5} r={5} fill="#6B7280" />
    
    {/* Brake lights (when braking) */}
    {braking && (
      <>
        <rect x={x + 115} y={y - 15} width={8} height={10} rx={2} fill="#EF4444" />
        <motion.circle
          cx={x + 119}
          cy={y - 10}
          r={15}
          fill="#EF4444"
          opacity={0.3}
          animate={{ opacity: [0.3, 0.6, 0.3], scale: [1, 1.2, 1] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        />
      </>
    )}
    
    {/* Motion trail when moving */}
    {moving && (
      <motion.g
        animate={{ opacity: [0.2, 0.5, 0.2] }}
        transition={{ duration: 0.3, repeat: Infinity }}
      >
        <line x1={x - 10} y1={y - 10} x2={x - 40} y2={y - 10} stroke={SCENE_THEME.colors.effect.motion} strokeWidth={3} strokeLinecap="round" />
        <line x1={x - 10} y1={y} x2={x - 50} y2={y} stroke={SCENE_THEME.colors.effect.motion} strokeWidth={4} strokeLinecap="round" />
        <line x1={x - 10} y1={y + 10} x2={x - 35} y2={y + 10} stroke={SCENE_THEME.colors.effect.motion} strokeWidth={2} strokeLinecap="round" />
      </motion.g>
    )}
  </motion.g>
);

// ============================================
// FORCE PRIMITIVES
// ============================================

/**
 * Force Arrow with Physics Styling
 */
export const ForceArrow = ({
  x = 100,
  y = 100,
  length = 80,
  angle = 0,  // degrees
  variant = 'applied',  // gravitational, normal, friction, applied, tension
  label = 'F',
  animate = true,
  delay = 0,
}) => {
  const color = SCENE_THEME.colors.force[variant] || SCENE_THEME.colors.force.applied;
  const radians = (angle * Math.PI) / 180;
  const endX = x + length * Math.cos(radians);
  const endY = y + length * Math.sin(radians);
  
  // Arrow head
  const headLength = 15;
  const headAngle = 25 * Math.PI / 180;
  const headX1 = endX - headLength * Math.cos(radians - headAngle);
  const headY1 = endY - headLength * Math.sin(radians - headAngle);
  const headX2 = endX - headLength * Math.cos(radians + headAngle);
  const headY2 = endY - headLength * Math.sin(radians + headAngle);
  
  // Label position
  const midX = (x + endX) / 2;
  const midY = (y + endY) / 2;
  const labelOffset = 20;
  const labelX = midX + labelOffset * Math.cos(radians - Math.PI / 2);
  const labelY = midY + labelOffset * Math.sin(radians - Math.PI / 2);
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.5 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.4, type: 'spring' }}
      className={`force-${variant}`}
    >
      {/* Arrow shaft */}
      <motion.line
        x1={x}
        y1={y}
        x2={endX}
        y2={endY}
        stroke={color}
        strokeWidth={4}
        strokeLinecap="round"
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
        transition={{ delay, duration: 0.5 }}
      />
      
      {/* Arrow head */}
      <polygon
        points={`${endX},${endY} ${headX1},${headY1} ${headX2},${headY2}`}
        fill={color}
      />
      
      {/* Label */}
      {label && (
        <text
          x={labelX}
          y={labelY}
          textAnchor="middle"
          fontSize={16}
          fontWeight={700}
          fill={color}
          fontFamily={SCENE_THEME.fonts.handwriting}
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

// ============================================
// EFFECT PRIMITIVES
// ============================================

/**
 * Motion Trail Effect
 */
export const MotionTrail = ({
  startX = 100,
  startY = 100,
  length = 60,
  direction = 'right',
  animate = true,
  delay = 0,
}) => {
  const endX = direction === 'right' ? startX - length : startX + length;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: [0.2, 0.5, 0.2] }}
      transition={{ delay, duration: 0.8, repeat: Infinity }}
      className="effect-motion-trail"
    >
      {Array.from({ length: 5 }).map((_, i) => (
        <line
          key={i}
          x1={startX}
          y1={startY - 10 + i * 5}
          x2={endX + i * 8}
          y2={startY - 10 + i * 5}
          stroke={SCENE_THEME.colors.effect.motion}
          strokeWidth={4 - i * 0.5}
          strokeLinecap="round"
          opacity={1 - i * 0.15}
        />
      ))}
    </motion.g>
  );
};

/**
 * Chaos Scatter Effect (for "no friction" world)
 */
export const ChaosScatter = ({
  centerX = 400,
  centerY = 300,
  radius = 100,
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ delay, duration: 0.5 }}
    className="effect-chaos"
  >
    {/* Scattered objects flying around */}
    {Array.from({ length: 8 }).map((_, i) => {
      const angle = (i / 8) * Math.PI * 2;
      const dist = radius * (0.5 + Math.random() * 0.5);
      const objX = centerX + Math.cos(angle) * dist;
      const objY = centerY + Math.sin(angle) * dist;
      
      return (
        <motion.g
          key={i}
          animate={{
            x: [0, Math.cos(angle) * 20, 0],
            y: [0, Math.sin(angle) * 20, 0],
            rotate: [0, 360],
          }}
          transition={{ duration: 2 + Math.random(), repeat: Infinity, ease: 'linear' }}
        >
          <rect
            x={objX - 10}
            y={objY - 10}
            width={20}
            height={20}
            rx={3}
            fill={SCENE_THEME.colors.effect.chaos}
            opacity={0.6}
          />
        </motion.g>
      );
    })}
    
    {/* Warning spiral lines */}
    <motion.circle
      cx={centerX}
      cy={centerY}
      r={radius}
      fill="none"
      stroke={SCENE_THEME.colors.effect.chaos}
      strokeWidth={2}
      strokeDasharray="10 5"
      opacity={0.3}
      animate={{ rotate: 360 }}
      transition={{ duration: 5, repeat: Infinity, ease: 'linear' }}
      style={{ transformOrigin: `${centerX}px ${centerY}px` }}
    />
    
    {/* "No Control" indicator */}
    <text
      x={centerX}
      y={centerY + radius + 30}
      textAnchor="middle"
      fontSize={14}
      fill={SCENE_THEME.colors.effect.chaos}
      fontFamily={SCENE_THEME.fonts.handwriting}
    >
      No control! 🌀
    </text>
  </motion.g>
);

// ============================================
// COMPARISON PRIMITIVES
// ============================================

/**
 * VS Divider for Split Scenes
 */
export const SceneDivider = ({
  x = 400,
  height = 600,
  label = 'VS',
  animate = true,
  delay = 0,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scaleY: 0 } : false}
    animate={{ opacity: 1, scaleY: 1 }}
    transition={{ delay, duration: 0.5 }}
    className="scene-divider"
  >
    {/* Dashed line */}
    <line
      x1={x}
      y1={40}
      x2={x}
      y2={height - 40}
      stroke="#94A3B8"
      strokeWidth={3}
      strokeDasharray="10 6"
    />
    
    {/* VS badge */}
    <circle cx={x} cy={height / 2} r={30} fill="white" stroke="#94A3B8" strokeWidth={3} />
    <text
      x={x}
      y={height / 2 + 8}
      textAnchor="middle"
      fontSize={20}
      fontWeight={700}
      fill="#64748B"
      fontFamily={SCENE_THEME.fonts.technical}
    >
      {label}
    </text>
  </motion.g>
);

/**
 * Scene Label
 */
export const SceneLabel = ({
  x = 200,
  y = 50,
  text = '',
  variant = 'title',  // title, subtitle, annotation
  color = '#1F2937',
  animate = true,
  delay = 0,
}) => {
  const fontSize = variant === 'title' ? 24 : variant === 'subtitle' ? 18 : 14;
  const fontWeight = variant === 'title' ? 700 : variant === 'subtitle' ? 600 : 400;
  
  return (
    <motion.text
      x={x}
      y={y}
      textAnchor="middle"
      fontSize={fontSize}
      fontWeight={fontWeight}
      fill={color}
      fontFamily={SCENE_THEME.fonts.handwriting}
      initial={animate ? { opacity: 0, y: y - 10 } : false}
      animate={{ opacity: 1, y }}
      transition={{ delay, duration: 0.4 }}
    >
      {text}
    </motion.text>
  );
};

// ============================================
// PRIMITIVE REGISTRY
// ============================================

export const SCENE_PRIMITIVE_REGISTRY = {
  // Environments
  [VISUAL_FORMS.OUTDOOR_SCENE]: OutdoorEnvironment,
  [VISUAL_FORMS.LAB_BACKGROUND]: LabEnvironment,
  [VISUAL_FORMS.ROOM_INTERIOR]: RoomEnvironment,
  
  // Surfaces
  [VISUAL_FORMS.FLAT_GROUND]: GroundSurface,
  [VISUAL_FORMS.ROUGH_SURFACE]: (props) => <GroundSurface {...props} variant="rough" />,
  [VISUAL_FORMS.SMOOTH_ICE]: IceSurface,
  [VISUAL_FORMS.CARPET_TEXTURE]: CarpetSurface,
  [VISUAL_FORMS.MICROSCOPIC_BUMPS]: MicroscopicSurface,
  
  // Actors
  [VISUAL_FORMS.SLIDING_BLOCK]: SlidingBlock,
  [VISUAL_FORMS.ROLLING_BALL]: RollingBall,
  [VISUAL_FORMS.PERSON_WALKING]: (props) => <PersonFigure {...props} action="walking" />,
  [VISUAL_FORMS.PERSON_SLIDING]: (props) => <PersonFigure {...props} action="sliding" />,
  [VISUAL_FORMS.CAR_MOVING]: CarFigure,
  
  // Forces
  [VISUAL_FORMS.FORCE_ARROW]: ForceArrow,
  [VISUAL_FORMS.GRAVITATIONAL_PULL]: (props) => <ForceArrow {...props} variant="gravitational" angle={90} />,
  [VISUAL_FORMS.FRICTION_RESISTANCE]: (props) => <ForceArrow {...props} variant="friction" />,
  
  // Effects
  [VISUAL_FORMS.MOTION_TRAIL]: MotionTrail,
  [VISUAL_FORMS.CHAOS_SCATTER]: ChaosScatter,
  
  // UI
  VS_DIVIDER: SceneDivider,
  SCENE_LABEL: SceneLabel,
};

/**
 * Get scene primitive component by visual form
 */
export const getScenePrimitive = (visualForm) => {
  return SCENE_PRIMITIVE_REGISTRY[visualForm] || null;
};

export default SCENE_PRIMITIVE_REGISTRY;
