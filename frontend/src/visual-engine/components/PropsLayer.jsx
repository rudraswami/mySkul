/**
 * PropsLayer - Scene Objects Rendering
 * Supports: cricket_ball, bat, stumps, auto_rickshaw, mango, box, etc.
 */

import React from 'react';
import { motion } from 'framer-motion';

const PropsLayer = ({ props, width, height, onPropClick }) => {
  return (
    <g id="props-layer">
      {props.map(prop => (
        <Prop
          key={prop.id}
          {...prop}
          width={width}
          height={height}
          onClick={() => onPropClick?.(prop.id)}
        />
      ))}
    </g>
  );
};

const Prop = ({ 
  id, 
  type, 
  position, 
  animatedPosition,
  animatedRotation = 0,
  animatedScale = 1,
  size = 'medium',
  style = {},
  width, 
  height,
  onClick 
}) => {
  const pos = animatedPosition || position || { x: 0.5, y: 0.5 };
  const x = pos.x * width;
  const y = pos.y * height;
  
  const sizeMultiplier = { small: 0.5, medium: 1, large: 1.5 }[size] || 1;

  const PropComponent = propComponents[type] || propComponents['box'];

  return (
    <motion.g
      id={`prop-${id}`}
      transform={`translate(${x}, ${y}) rotate(${animatedRotation}) scale(${animatedScale * sizeMultiplier})`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <PropComponent style={style} />
    </motion.g>
  );
};

/**
 * Prop Components Library
 */
const propComponents = {
  // === SPORTS ===
  cricket_ball: ({ style }) => (
    <g>
      <motion.circle
        cx="0"
        cy="0"
        r="12"
        fill="#D32F2F"
        stroke="#8B0000"
        strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.5, ease: 'linear' }}
      />
      {/* Seam */}
      <path d="M -8 -8 Q 0 0 8 8" stroke="#FFF" strokeWidth="1.5" fill="none" />
    </g>
  ),

  bat: ({ style }) => (
    <g>
      {/* Handle */}
      <rect x="-4" y="-60" width="8" height="25" fill="#4E342E" rx="2" />
      <rect x="-3" y="-58" width="6" height="20" fill="#6D4C41" rx="1" />
      {/* Blade */}
      <rect x="-12" y="-35" width="24" height="70" fill="#D7CCC8" rx="3" />
      <rect x="-10" y="-33" width="20" height="65" fill="#EFEBE9" rx="2" />
    </g>
  ),

  stumps: ({ style }) => (
    <g>
      {/* Three stumps */}
      <rect x="-15" y="-50" width="5" height="55" fill="#8D6E63" rx="1" />
      <rect x="-2" y="-50" width="5" height="55" fill="#8D6E63" rx="1" />
      <rect x="10" y="-50" width="5" height="55" fill="#8D6E63" rx="1" />
      {/* Bails */}
      <rect x="-13" y="-52" width="12" height="4" fill="#FFC107" rx="1" />
      <rect x="1" y="-52" width="12" height="4" fill="#FFC107" rx="1" />
    </g>
  ),

  // === VEHICLES ===
  auto_rickshaw: ({ style }) => (
    <g>
      {/* Body */}
      <path
        d="M -30 0 L -30 -30 L -20 -45 L 25 -45 L 35 -30 L 35 0 Z"
        fill="#81C784"
        stroke="#2E7D32"
        strokeWidth="2"
      />
      {/* Roof */}
      <path
        d="M -25 -45 L -20 -60 L 20 -60 L 25 -45"
        fill="#FDD835"
        stroke="#F9A825"
        strokeWidth="2"
      />
      {/* Windows */}
      <rect x="-25" y="-40" width="15" height="15" fill="#81D4FA" rx="2" />
      <rect x="5" y="-40" width="25" height="15" fill="#81D4FA" rx="2" />
      {/* Wheels */}
      <motion.circle
        cx="-20"
        cy="5"
        r="10"
        fill="#37474F"
        stroke="#263238"
        strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.3, ease: 'linear' }}
      />
      <motion.circle
        cx="25"
        cy="5"
        r="10"
        fill="#37474F"
        stroke="#263238"
        strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.3, ease: 'linear' }}
      />
      {/* Headlight */}
      <circle cx="-32" cy="-15" r="5" fill="#FFF59D" />
    </g>
  ),

  scooter: ({ style }) => (
    <g>
      {/* Body */}
      <ellipse cx="0" cy="-15" rx="25" ry="12" fill="#42A5F5" />
      {/* Handle */}
      <path d="M -5 -30 L -5 -45 L 5 -45 L 5 -30" stroke="#424242" strokeWidth="3" fill="none" />
      <rect x="-15" y="-48" width="30" height="5" fill="#424242" rx="2" />
      {/* Seat */}
      <ellipse cx="10" cy="-25" rx="15" ry="6" fill="#263238" />
      {/* Wheels */}
      <motion.circle cx="-20" cy="5" r="12" fill="#424242" stroke="#212121" strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.4, ease: 'linear' }}
      />
      <motion.circle cx="20" cy="5" r="12" fill="#424242" stroke="#212121" strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.4, ease: 'linear' }}
      />
    </g>
  ),

  // === NATURE ===
  mango: ({ style }) => (
    <g>
      <motion.ellipse
        cx="0"
        cy="0"
        rx="12"
        ry="16"
        fill="#FF9800"
        stroke="#E65100"
        strokeWidth="1.5"
        animate={{ rotate: [-5, 5, -5] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
      {/* Stem */}
      <path d="M 0 -16 Q 3 -20 2 -24" stroke="#4E342E" strokeWidth="2" fill="none" />
      {/* Leaf */}
      <ellipse cx="6" cy="-22" rx="8" ry="4" fill="#66BB6A" transform="rotate(30 6 -22)" />
    </g>
  ),

  tree: ({ style }) => (
    <g>
      {/* Trunk */}
      <rect x="-15" y="0" width="30" height="80" fill="#5D4037" />
      {/* Crown */}
      <circle cx="0" cy="-40" r="60" fill="#4CAF50" />
      <circle cx="-30" cy="-20" r="35" fill="#66BB6A" />
      <circle cx="30" cy="-20" r="35" fill="#43A047" />
      <circle cx="0" cy="-70" r="40" fill="#81C784" />
    </g>
  ),

  // === PHYSICS OBJECTS ===
  box: ({ style }) => (
    <g>
      <rect x="-25" y="-25" width="50" height="50" fill="#8D6E63" stroke="#5D4037" strokeWidth="2" />
      <rect x="-23" y="-23" width="46" height="46" fill="#A1887F" />
      {/* Tape lines */}
      <line x1="-25" y1="0" x2="25" y2="0" stroke="#6D4C41" strokeWidth="3" />
      <line x1="0" y1="-25" x2="0" y2="25" stroke="#6D4C41" strokeWidth="3" />
    </g>
  ),

  spring: ({ style }) => (
    <g>
      <path
        d="M 0 -40 Q 15 -35 0 -30 Q -15 -25 0 -20 Q 15 -15 0 -10 Q -15 -5 0 0 Q 15 5 0 10 Q -15 15 0 20 Q 15 25 0 30 Q -15 35 0 40"
        fill="none"
        stroke="#607D8B"
        strokeWidth="4"
      />
      <rect x="-10" y="-45" width="20" height="8" fill="#455A64" />
      <rect x="-10" y="37" width="20" height="8" fill="#455A64" />
    </g>
  ),

  pulley: ({ style }) => (
    <g>
      {/* Mount */}
      <rect x="-5" y="-50" width="10" height="20" fill="#424242" />
      {/* Wheel */}
      <circle cx="0" cy="-25" r="20" fill="#78909C" stroke="#455A64" strokeWidth="3" />
      <circle cx="0" cy="-25" r="5" fill="#455A64" />
      {/* Rope */}
      <path d="M -18 -25 L -18 30" stroke="#8D6E63" strokeWidth="3" />
      <path d="M 18 -25 L 18 30" stroke="#8D6E63" strokeWidth="3" />
    </g>
  ),

  // === INDIAN OBJECTS ===
  matka: ({ style }) => (
    <g>
      {/* Pot body */}
      <ellipse cx="0" cy="0" rx="25" ry="30" fill="#8D6E63" />
      <ellipse cx="0" cy="-25" rx="15" ry="8" fill="#6D4C41" />
      {/* Neck */}
      <rect x="-10" y="-35" width="20" height="12" fill="#8D6E63" />
      {/* Opening */}
      <ellipse cx="0" cy="-35" rx="10" ry="4" fill="#4E342E" />
      {/* Decoration */}
      <ellipse cx="0" cy="0" rx="22" ry="5" fill="none" stroke="#5D4037" strokeWidth="2" />
    </g>
  ),

  tiffin: ({ style }) => (
    <g>
      {/* Container stack */}
      <ellipse cx="0" cy="20" rx="18" ry="5" fill="#B0BEC5" />
      <rect x="-18" y="-10" width="36" height="30" fill="#CFD8DC" rx="2" />
      <ellipse cx="0" cy="-10" rx="18" ry="5" fill="#ECEFF1" />
      <rect x="-18" y="-35" width="36" height="25" fill="#CFD8DC" rx="2" />
      <ellipse cx="0" cy="-35" rx="18" ry="5" fill="#ECEFF1" />
      {/* Handle */}
      <path d="M -5 -40 Q 0 -55 5 -40" stroke="#78909C" strokeWidth="3" fill="none" />
    </g>
  ),

  chai_cup: ({ style }) => (
    <g>
      {/* Cup */}
      <path
        d="M -15 -20 L -12 20 L 12 20 L 15 -20 Z"
        fill="#EFEBE9"
        stroke="#8D6E63"
        strokeWidth="2"
      />
      {/* Tea */}
      <ellipse cx="0" cy="-15" rx="12" ry="4" fill="#6D4C41" />
      {/* Handle */}
      <path d="M 15 -10 Q 25 0 15 10" stroke="#8D6E63" strokeWidth="3" fill="none" />
      {/* Steam */}
      <motion.path
        d="M -5 -25 Q -8 -35 -3 -40"
        stroke="#B0BEC5"
        strokeWidth="2"
        fill="none"
        animate={{ opacity: [0, 1, 0], y: [0, -5, -10] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
      <motion.path
        d="M 5 -25 Q 8 -35 3 -40"
        stroke="#B0BEC5"
        strokeWidth="2"
        fill="none"
        animate={{ opacity: [0, 1, 0], y: [0, -5, -10] }}
        transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
      />
    </g>
  ),

  gas_cylinder: ({ style }) => (
    <g>
      {/* Body */}
      <rect x="-20" y="-40" width="40" height="70" fill="#D32F2F" rx="10" />
      {/* Top */}
      <ellipse cx="0" cy="-40" rx="20" ry="8" fill="#C62828" />
      {/* Valve */}
      <rect x="-5" y="-55" width="10" height="15" fill="#424242" rx="2" />
      <circle cx="0" cy="-55" r="6" fill="#616161" />
      {/* Base */}
      <ellipse cx="0" cy="30" rx="20" ry="8" fill="#B71C1C" />
      {/* Label */}
      <ellipse cx="0" cy="0" rx="15" ry="20" fill="none" stroke="#FFCDD2" strokeWidth="2" />
    </g>
  ),
};

export default PropsLayer;


