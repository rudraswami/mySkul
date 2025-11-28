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

  // === PHASE 3: NEW PHYSICS OBJECTS ===
  
  // Detailed Cricket Ball with seam
  cricket_ball_detailed: ({ style }) => (
    <g>
      {/* Ball shadow */}
      <ellipse cx="3" cy="15" rx="14" ry="4" fill="rgba(0,0,0,0.2)" />
      {/* Ball body */}
      <circle cx="0" cy="0" r="14" fill="#C62828" stroke="#8B0000" strokeWidth="1.5" />
      {/* Seam - main */}
      <path d="M -10 -10 Q 0 0 10 10" stroke="white" strokeWidth="2" fill="none" />
      {/* Seam stitches */}
      <path d="M -8 -8 L -6 -6" stroke="white" strokeWidth="1" />
      <path d="M -4 -4 L -2 -2" stroke="white" strokeWidth="1" />
      <path d="M 2 2 L 4 4" stroke="white" strokeWidth="1" />
      <path d="M 6 6 L 8 8" stroke="white" strokeWidth="1" />
      {/* Shine */}
      <circle cx="-5" cy="-6" r="4" fill="white" opacity="0.3" />
    </g>
  ),

  // Lens for optics
  lens_convex: ({ style }) => (
    <g>
      {/* Lens body */}
      <ellipse cx="0" cy="0" rx="8" ry="40" fill="rgba(135, 206, 235, 0.5)" stroke="#1976D2" strokeWidth="2" />
      {/* Center line */}
      <line x1="0" y1="-45" x2="0" y2="45" stroke="#1976D2" strokeWidth="1" strokeDasharray="4 2" />
      {/* Focal point markers */}
      <circle cx="30" cy="0" r="3" fill="#FF5722" />
      <text x="30" y="15" fontSize="8" fill="#FF5722" textAnchor="middle">F</text>
      <circle cx="-30" cy="0" r="3" fill="#FF5722" />
      <text x="-30" y="15" fontSize="8" fill="#FF5722" textAnchor="middle">F</text>
    </g>
  ),

  lens_concave: ({ style }) => (
    <g>
      {/* Lens body */}
      <path d="M -5 -40 Q -15 0 -5 40 L 5 40 Q 15 0 5 -40 Z" fill="rgba(135, 206, 235, 0.5)" stroke="#1976D2" strokeWidth="2" />
      {/* Center line */}
      <line x1="0" y1="-45" x2="0" y2="45" stroke="#1976D2" strokeWidth="1" strokeDasharray="4 2" />
    </g>
  ),

  // Prism for light refraction
  prism: ({ style }) => (
    <g>
      <polygon points="0,-35 -30,30 30,30" fill="rgba(200, 230, 255, 0.6)" stroke="#1565C0" strokeWidth="2" />
      {/* Light spectrum hint */}
      <line x1="20" y1="25" x2="40" y2="15" stroke="#FF0000" strokeWidth="2" />
      <line x1="20" y1="25" x2="42" y2="20" stroke="#FF9800" strokeWidth="2" />
      <line x1="20" y1="25" x2="44" y2="25" stroke="#FFEB3B" strokeWidth="2" />
      <line x1="20" y1="25" x2="42" y2="30" stroke="#4CAF50" strokeWidth="2" />
      <line x1="20" y1="25" x2="40" y2="35" stroke="#2196F3" strokeWidth="2" />
      <line x1="20" y1="25" x2="38" y2="40" stroke="#9C27B0" strokeWidth="2" />
    </g>
  ),

  // Magnet
  magnet: ({ style }) => (
    <g>
      {/* U-shape magnet */}
      <path d="M -25 -30 L -25 20 Q -25 35 -10 35 L -10 20 L -10 -20 L 10 -20 L 10 20 L 10 35 Q 25 35 25 20 L 25 -30 Z" 
        fill="#D32F2F" stroke="#B71C1C" strokeWidth="2" />
      {/* North pole */}
      <rect x="-25" y="-30" width="15" height="10" fill="#D32F2F" />
      <text x="-17" y="-22" fontSize="10" fill="white" fontWeight="bold">N</text>
      {/* South pole */}
      <rect x="10" y="-30" width="15" height="10" fill="#1976D2" />
      <text x="18" y="-22" fontSize="10" fill="white" fontWeight="bold">S</text>
      {/* Field lines hint */}
      <motion.path 
        d="M -17 35 Q 0 50 17 35" 
        stroke="#9E9E9E" 
        strokeWidth="1" 
        fill="none" 
        strokeDasharray="3 2"
        animate={{ opacity: [0.3, 0.8, 0.3] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
    </g>
  ),

  // Skateboard for Newton's laws
  skateboard: ({ style }) => (
    <g>
      {/* Board */}
      <rect x="-40" y="-8" width="80" height="8" fill="#8D6E63" rx="4" />
      <rect x="-38" y="-6" width="76" height="4" fill="#A1887F" rx="2" />
      {/* Grip tape pattern */}
      <rect x="-35" y="-8" width="70" height="2" fill="#424242" />
      {/* Wheels */}
      <motion.circle cx="-25" cy="5" r="8" fill="#FFC107" stroke="#F57F17" strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.3, ease: 'linear' }}
      />
      <motion.circle cx="25" cy="5" r="8" fill="#FFC107" stroke="#F57F17" strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.3, ease: 'linear' }}
      />
      {/* Trucks */}
      <rect x="-30" y="-2" width="10" height="5" fill="#78909C" />
      <rect x="20" y="-2" width="10" height="5" fill="#78909C" />
    </g>
  ),

  // Pendulum
  pendulum: ({ style }) => (
    <g>
      {/* Mount */}
      <rect x="-30" y="-60" width="60" height="8" fill="#5D4037" />
      {/* String */}
      <motion.line 
        x1="0" y1="-52" x2="0" y2="20" 
        stroke="#8D6E63" strokeWidth="2"
        animate={{ rotate: [-20, 20, -20] }}
        transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
        style={{ transformOrigin: '0 -52px' }}
      />
      {/* Bob */}
      <motion.circle 
        cx="0" cy="20" r="15" 
        fill="#FFC107" stroke="#F57F17" strokeWidth="2"
        animate={{ x: [-30, 30, -30] }}
        transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
      />
    </g>
  ),

  // Electric bulb
  bulb: ({ style }) => (
    <g>
      {/* Glass */}
      <ellipse cx="0" cy="-15" rx="20" ry="25" fill="rgba(255, 253, 231, 0.8)" stroke="#FFC107" strokeWidth="2" />
      {/* Filament */}
      <motion.path 
        d="M -8 -15 Q -5 -25 0 -15 Q 5 -5 8 -15" 
        stroke="#FF9800" strokeWidth="2" fill="none"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 1 }}
      />
      {/* Base */}
      <rect x="-12" y="10" width="24" height="15" fill="#424242" rx="2" />
      <rect x="-10" y="12" width="20" height="3" fill="#616161" />
      <rect x="-10" y="18" width="20" height="3" fill="#616161" />
      {/* Glow effect */}
      <motion.ellipse 
        cx="0" cy="-15" rx="30" ry="35" 
        fill="rgba(255, 235, 59, 0.2)"
        animate={{ opacity: [0.2, 0.5, 0.2], scale: [1, 1.1, 1] }}
        transition={{ repeat: Infinity, duration: 1 }}
      />
    </g>
  ),

  // Battery
  battery: ({ style }) => (
    <g>
      {/* Body */}
      <rect x="-15" y="-30" width="30" height="60" fill="#424242" rx="3" />
      {/* Positive terminal */}
      <rect x="-5" y="-35" width="10" height="8" fill="#757575" rx="1" />
      <text x="0" y="-38" fontSize="12" fill="#F44336" textAnchor="middle" fontWeight="bold">+</text>
      {/* Negative terminal */}
      <text x="0" y="38" fontSize="12" fill="#2196F3" textAnchor="middle" fontWeight="bold">−</text>
      {/* Charge indicator */}
      <rect x="-10" y="-20" width="20" height="35" fill="#4CAF50" rx="2" />
      {/* Label */}
      <text x="0" y="5" fontSize="8" fill="white" textAnchor="middle">1.5V</text>
    </g>
  ),

  // Wire/Resistor
  resistor: ({ style }) => (
    <g>
      {/* Wire ends */}
      <line x1="-40" y1="0" x2="-20" y2="0" stroke="#424242" strokeWidth="3" />
      <line x1="20" y1="0" x2="40" y2="0" stroke="#424242" strokeWidth="3" />
      {/* Zigzag resistor */}
      <path d="M -20 0 L -15 -8 L -5 8 L 5 -8 L 15 8 L 20 0" stroke="#FF9800" strokeWidth="3" fill="none" />
      {/* Label */}
      <text x="0" y="20" fontSize="8" fill="#666" textAnchor="middle">R</text>
    </g>
  ),

  // === BIOLOGY OBJECTS ===
  
  // Leaf with stomata
  leaf: ({ style }) => (
    <g>
      {/* Leaf body */}
      <path d="M 0 -40 Q 30 -20 25 20 Q 15 40 0 45 Q -15 40 -25 20 Q -30 -20 0 -40" 
        fill="#66BB6A" stroke="#2E7D32" strokeWidth="2" />
      {/* Main vein */}
      <path d="M 0 -35 L 0 40" stroke="#2E7D32" strokeWidth="2" />
      {/* Side veins */}
      <path d="M 0 -20 L 15 -10" stroke="#43A047" strokeWidth="1" />
      <path d="M 0 -20 L -15 -10" stroke="#43A047" strokeWidth="1" />
      <path d="M 0 0 L 18 10" stroke="#43A047" strokeWidth="1" />
      <path d="M 0 0 L -18 10" stroke="#43A047" strokeWidth="1" />
      <path d="M 0 20 L 12 28" stroke="#43A047" strokeWidth="1" />
      <path d="M 0 20 L -12 28" stroke="#43A047" strokeWidth="1" />
      {/* Stomata hint */}
      <ellipse cx="10" cy="5" rx="3" ry="1.5" fill="#1B5E20" />
      <ellipse cx="-8" cy="15" rx="3" ry="1.5" fill="#1B5E20" />
    </g>
  ),

  // Oxygen bubble
  oxygen_bubble: ({ style }) => (
    <motion.g
      animate={{ y: [0, -20, -40] }}
      transition={{ repeat: Infinity, duration: 3, ease: 'easeOut' }}
    >
      <circle cx="0" cy="0" r="8" fill="rgba(33, 150, 243, 0.4)" stroke="#1976D2" strokeWidth="1" />
      <text x="0" y="3" fontSize="6" fill="#1565C0" textAnchor="middle">O₂</text>
      {/* Shine */}
      <circle cx="-3" cy="-3" r="2" fill="white" opacity="0.6" />
    </motion.g>
  ),

  // Red blood cell
  rbc: ({ style }) => (
    <g>
      <ellipse cx="0" cy="0" rx="18" ry="8" fill="#EF5350" stroke="#C62828" strokeWidth="1" />
      {/* Biconcave shape hint */}
      <ellipse cx="0" cy="0" rx="8" ry="3" fill="#D32F2F" />
    </g>
  ),

  // White blood cell
  wbc: ({ style }) => (
    <g>
      {/* Cell body - irregular shape */}
      <circle cx="0" cy="0" r="15" fill="#E3F2FD" stroke="#1976D2" strokeWidth="1.5" />
      {/* Nucleus - multi-lobed */}
      <circle cx="-5" cy="-3" r="5" fill="#7986CB" />
      <circle cx="3" cy="2" r="4" fill="#7986CB" />
      <circle cx="-2" cy="5" r="4" fill="#7986CB" />
      {/* Granules */}
      <circle cx="8" cy="-5" r="2" fill="#9FA8DA" />
      <circle cx="-10" cy="5" r="1.5" fill="#9FA8DA" />
    </g>
  ),

  // Neuron
  neuron: ({ style }) => (
    <g>
      {/* Cell body */}
      <circle cx="0" cy="0" r="15" fill="#FFECB3" stroke="#FF9800" strokeWidth="2" />
      {/* Nucleus */}
      <circle cx="0" cy="0" r="6" fill="#FFB74D" />
      {/* Dendrites */}
      <path d="M -15 -5 L -30 -15 M -28 -12 L -35 -8 M -28 -18 L -32 -25" stroke="#FF9800" strokeWidth="2" fill="none" />
      <path d="M -12 10 L -25 20 M -22 18 L -28 28" stroke="#FF9800" strokeWidth="2" fill="none" />
      <path d="M 5 -14 L 10 -28 M 8 -22 L 18 -25" stroke="#FF9800" strokeWidth="2" fill="none" />
      {/* Axon */}
      <path d="M 15 0 L 60 0" stroke="#FF9800" strokeWidth="3" />
      {/* Myelin sheath */}
      <ellipse cx="28" cy="0" rx="5" ry="4" fill="#FFF3E0" stroke="#FFB74D" strokeWidth="1" />
      <ellipse cx="42" cy="0" rx="5" ry="4" fill="#FFF3E0" stroke="#FFB74D" strokeWidth="1" />
      {/* Axon terminal */}
      <circle cx="60" cy="-5" r="4" fill="#FF9800" />
      <circle cx="65" cy="0" r="4" fill="#FF9800" />
      <circle cx="60" cy="5" r="4" fill="#FF9800" />
    </g>
  ),

  // Heart (simplified)
  heart_organ: ({ style }) => (
    <motion.g
      animate={{ scale: [1, 1.05, 1] }}
      transition={{ repeat: Infinity, duration: 0.8 }}
    >
      <path d="M 0 15 C -25 -10 -25 -30 0 -15 C 25 -30 25 -10 0 15" 
        fill="#EF5350" stroke="#C62828" strokeWidth="2" />
      {/* Aorta hint */}
      <path d="M 0 -15 Q 5 -25 15 -20" stroke="#C62828" strokeWidth="3" fill="none" />
    </motion.g>
  ),

  // === CHEMISTRY OBJECTS ===
  
  // Test tube
  test_tube: ({ style }) => (
    <g>
      {/* Tube */}
      <path d="M -8 -40 L -8 25 Q -8 35 0 35 Q 8 35 8 25 L 8 -40" 
        fill="rgba(200, 230, 255, 0.5)" stroke="#1976D2" strokeWidth="2" />
      {/* Liquid */}
      <path d="M -6 0 L -6 25 Q -6 32 0 32 Q 6 32 6 25 L 6 0 Z" fill="#4CAF50" opacity="0.7" />
      {/* Bubbles */}
      <motion.circle cx="-2" cy="15" r="2" fill="white" opacity="0.6"
        animate={{ y: [15, 5, -5], opacity: [0.6, 0.3, 0] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
      <motion.circle cx="3" cy="20" r="1.5" fill="white" opacity="0.6"
        animate={{ y: [20, 10, 0], opacity: [0.6, 0.3, 0] }}
        transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
      />
      {/* Rim */}
      <ellipse cx="0" cy="-40" rx="10" ry="3" fill="#E3F2FD" stroke="#1976D2" strokeWidth="1" />
    </g>
  ),

  // Beaker
  beaker: ({ style }) => (
    <g>
      {/* Body */}
      <path d="M -25 -35 L -25 30 L 25 30 L 25 -35" fill="rgba(200, 230, 255, 0.4)" stroke="#1976D2" strokeWidth="2" />
      {/* Spout */}
      <path d="M -25 -35 L -30 -40 L -25 -35" stroke="#1976D2" strokeWidth="2" fill="none" />
      {/* Measurement lines */}
      <line x1="-25" y1="10" x2="-20" y2="10" stroke="#1976D2" strokeWidth="1" />
      <line x1="-25" y1="-10" x2="-20" y2="-10" stroke="#1976D2" strokeWidth="1" />
      {/* Liquid */}
      <rect x="-23" y="0" width="46" height="28" fill="#2196F3" opacity="0.5" rx="2" />
    </g>
  ),

  // Bunsen burner
  bunsen_burner: ({ style }) => (
    <g>
      {/* Base */}
      <rect x="-20" y="20" width="40" height="10" fill="#424242" rx="2" />
      {/* Tube */}
      <rect x="-8" y="-30" width="16" height="50" fill="#616161" />
      {/* Air hole */}
      <ellipse cx="0" cy="0" rx="4" ry="6" fill="#424242" />
      {/* Flame */}
      <motion.path 
        d="M 0 -30 Q -10 -50 0 -70 Q 10 -50 0 -30" 
        fill="#FF9800"
        animate={{ d: [
          "M 0 -30 Q -10 -50 0 -70 Q 10 -50 0 -30",
          "M 0 -30 Q -8 -55 0 -75 Q 8 -55 0 -30",
          "M 0 -30 Q -10 -50 0 -70 Q 10 -50 0 -30"
        ]}}
        transition={{ repeat: Infinity, duration: 0.5 }}
      />
      <motion.path 
        d="M 0 -30 Q -5 -45 0 -55 Q 5 -45 0 -30" 
        fill="#2196F3"
        animate={{ d: [
          "M 0 -30 Q -5 -45 0 -55 Q 5 -45 0 -30",
          "M 0 -30 Q -4 -48 0 -60 Q 4 -48 0 -30",
          "M 0 -30 Q -5 -45 0 -55 Q 5 -45 0 -30"
        ]}}
        transition={{ repeat: Infinity, duration: 0.5 }}
      />
    </g>
  ),

  // Atom model
  atom_model: ({ style }) => (
    <g>
      {/* Nucleus */}
      <circle cx="0" cy="0" r="10" fill="#F44336" />
      {/* Electron orbits */}
      <motion.ellipse cx="0" cy="0" rx="30" ry="10" fill="none" stroke="#2196F3" strokeWidth="1"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
      />
      <motion.ellipse cx="0" cy="0" rx="30" ry="10" fill="none" stroke="#4CAF50" strokeWidth="1" transform="rotate(60)"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 4, ease: 'linear' }}
      />
      <motion.ellipse cx="0" cy="0" rx="30" ry="10" fill="none" stroke="#FF9800" strokeWidth="1" transform="rotate(120)"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 5, ease: 'linear' }}
      />
      {/* Electrons */}
      <motion.circle cx="30" cy="0" r="4" fill="#2196F3"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
        style={{ transformOrigin: '0 0' }}
      />
    </g>
  ),

  // === MATH OBJECTS ===
  
  // Coordinate axes
  axes: ({ style }) => (
    <g>
      {/* X-axis */}
      <line x1="-60" y1="0" x2="60" y2="0" stroke="#333" strokeWidth="2" />
      <polygon points="60,0 50,-5 50,5" fill="#333" />
      <text x="65" y="5" fontSize="12" fill="#333">x</text>
      {/* Y-axis */}
      <line x1="0" y1="60" x2="0" y2="-60" stroke="#333" strokeWidth="2" />
      <polygon points="0,-60 -5,-50 5,-50" fill="#333" />
      <text x="5" y="-65" fontSize="12" fill="#333">y</text>
      {/* Origin */}
      <text x="-10" y="15" fontSize="10" fill="#333">O</text>
      {/* Grid lines */}
      {[-40, -20, 20, 40].map(v => (
        <g key={v}>
          <line x1={v} y1="-3" x2={v} y2="3" stroke="#333" strokeWidth="1" />
          <line x1="-3" y1={v} x2="3" y2={v} stroke="#333" strokeWidth="1" />
        </g>
      ))}
    </g>
  ),

  // Parabola curve
  parabola: ({ style }) => (
    <g>
      <path d="M -40 40 Q 0 -50 40 40" fill="none" stroke="#9C27B0" strokeWidth="2" />
      {/* Vertex marker */}
      <circle cx="0" cy="-10" r="4" fill="#9C27B0" />
      <text x="10" y="-5" fontSize="8" fill="#9C27B0">vertex</text>
    </g>
  ),

  // Right triangle
  right_triangle: ({ style }) => (
    <g>
      <polygon points="0,0 50,0 50,-40" fill="rgba(156, 39, 176, 0.2)" stroke="#9C27B0" strokeWidth="2" />
      {/* Right angle marker */}
      <path d="M 45 0 L 45 -5 L 50 -5" fill="none" stroke="#9C27B0" strokeWidth="1" />
      {/* Labels */}
      <text x="25" y="15" fontSize="10" fill="#9C27B0" textAnchor="middle">a</text>
      <text x="55" y="-20" fontSize="10" fill="#9C27B0">b</text>
      <text x="20" y="-25" fontSize="10" fill="#9C27B0">c</text>
    </g>
  ),

  // Circle with radius
  circle_with_radius: ({ style }) => (
    <g>
      <circle cx="0" cy="0" r="35" fill="rgba(33, 150, 243, 0.2)" stroke="#2196F3" strokeWidth="2" />
      {/* Center */}
      <circle cx="0" cy="0" r="3" fill="#2196F3" />
      {/* Radius line */}
      <line x1="0" y1="0" x2="35" y2="0" stroke="#F44336" strokeWidth="2" />
      <text x="17" y="-5" fontSize="10" fill="#F44336">r</text>
      {/* Diameter hint */}
      <line x1="-35" y1="0" x2="35" y2="0" stroke="#4CAF50" strokeWidth="1" strokeDasharray="4 2" />
    </g>
  ),

  // === REGIONAL/CULTURAL OBJECTS ===
  
  // Camel (Rajasthan)
  camel: ({ style }) => (
    <g>
      {/* Body */}
      <ellipse cx="0" cy="0" rx="35" ry="20" fill="#D2691E" />
      {/* Hump */}
      <ellipse cx="-5" cy="-25" rx="15" ry="15" fill="#D2691E" />
      {/* Head */}
      <ellipse cx="40" cy="-10" rx="12" ry="8" fill="#D2691E" />
      {/* Neck */}
      <path d="M 20 -10 Q 30 -20 40 -10" fill="#D2691E" />
      {/* Legs */}
      <rect x="-25" y="15" width="8" height="30" fill="#C4A484" />
      <rect x="-5" y="15" width="8" height="30" fill="#C4A484" />
      <rect x="10" y="15" width="8" height="30" fill="#C4A484" />
      {/* Eye */}
      <circle cx="45" cy="-12" r="2" fill="#333" />
      {/* Ear */}
      <ellipse cx="35" cy="-18" rx="3" ry="5" fill="#C4A484" />
    </g>
  ),

  // Local train (Mumbai)
  local_train: ({ style }) => (
    <g>
      {/* Body */}
      <rect x="-50" y="-30" width="100" height="45" fill="#1976D2" rx="5" />
      {/* Windows */}
      <rect x="-40" y="-25" width="15" height="15" fill="#81D4FA" rx="2" />
      <rect x="-20" y="-25" width="15" height="15" fill="#81D4FA" rx="2" />
      <rect x="5" y="-25" width="15" height="15" fill="#81D4FA" rx="2" />
      <rect x="25" y="-25" width="15" height="15" fill="#81D4FA" rx="2" />
      {/* Door */}
      <rect x="-5" y="-25" width="8" height="35" fill="#0D47A1" />
      {/* Stripe */}
      <rect x="-50" y="0" width="100" height="5" fill="#FFC107" />
      {/* Wheels */}
      <motion.circle cx="-30" cy="20" r="8" fill="#424242"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.5, ease: 'linear' }}
      />
      <motion.circle cx="30" cy="20" r="8" fill="#424242"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.5, ease: 'linear' }}
      />
    </g>
  ),

  // Tractor (Punjab)
  tractor: ({ style }) => (
    <g>
      {/* Body */}
      <rect x="-20" y="-30" width="50" height="35" fill="#4CAF50" rx="3" />
      {/* Hood */}
      <rect x="30" y="-20" width="25" height="20" fill="#388E3C" rx="2" />
      {/* Exhaust */}
      <rect x="50" y="-35" width="5" height="15" fill="#424242" />
      <motion.circle cx="52" cy="-40" r="3" fill="#9E9E9E" opacity="0.5"
        animate={{ y: [-40, -50], opacity: [0.5, 0] }}
        transition={{ repeat: Infinity, duration: 1 }}
      />
      {/* Big rear wheel */}
      <motion.circle cx="-5" cy="15" r="25" fill="#424242" stroke="#212121" strokeWidth="3"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
      />
      <circle cx="-5" cy="15" r="10" fill="#FFC107" />
      {/* Small front wheel */}
      <motion.circle cx="40" cy="10" r="12" fill="#424242" stroke="#212121" strokeWidth="2"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.5, ease: 'linear' }}
      />
      <circle cx="40" cy="10" r="5" fill="#FFC107" />
      {/* Seat */}
      <rect x="-15" y="-40" width="15" height="5" fill="#795548" rx="2" />
      <rect x="-12" y="-55" width="8" height="15" fill="#795548" rx="2" />
    </g>
  ),

  // Dosa (South India)
  dosa: ({ style }) => (
    <g>
      {/* Plate */}
      <ellipse cx="0" cy="5" rx="45" ry="15" fill="#8D6E63" />
      <ellipse cx="0" cy="3" rx="43" ry="13" fill="#EFEBE9" />
      {/* Dosa */}
      <ellipse cx="0" cy="0" rx="35" ry="8" fill="#FFE082" />
      <ellipse cx="0" cy="-2" rx="33" ry="6" fill="#FFD54F" />
      {/* Crispy texture */}
      <ellipse cx="-15" cy="-1" rx="5" ry="2" fill="#FFC107" opacity="0.5" />
      <ellipse cx="10" cy="0" rx="4" ry="1.5" fill="#FFC107" opacity="0.5" />
      {/* Chutney */}
      <ellipse cx="35" cy="0" rx="8" ry="5" fill="#66BB6A" />
      {/* Sambar */}
      <ellipse cx="-35" cy="0" rx="8" ry="5" fill="#FF7043" />
    </g>
  ),

  // Idli (South India)
  idli: ({ style }) => (
    <g>
      {/* Plate */}
      <ellipse cx="0" cy="10" rx="40" ry="12" fill="#EFEBE9" stroke="#8D6E63" strokeWidth="2" />
      {/* Idlis */}
      <ellipse cx="-15" cy="0" rx="12" ry="6" fill="#FAFAFA" />
      <ellipse cx="15" cy="0" rx="12" ry="6" fill="#FAFAFA" />
      <ellipse cx="0" cy="-8" rx="12" ry="6" fill="#FAFAFA" />
      {/* Chutney dots */}
      <circle cx="30" cy="5" r="5" fill="#66BB6A" />
    </g>
  ),
};

export default PropsLayer;




