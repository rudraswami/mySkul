/**
 * 🚗 Vehicle Primitive
 * ====================
 * 
 * Configurable vehicle component for motion/race visualizations.
 * Supports: auto_rickshaw, car, scooter, bus, truck, cycle, train
 */

import React from 'react';
import { motion } from 'framer-motion';

const VEHICLE_TYPES = {
  auto_rickshaw: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Body */}
      <path
        d="M -30 0 L -30 -25 Q -25 -35 -10 -35 L 25 -35 Q 35 -35 35 -20 L 35 0 Z"
        fill={color}
        stroke={color === '#FF9933' ? '#D97706' : '#1D4ED8'}
        strokeWidth={2}
      />
      {/* Roof */}
      <path d="M -20 -35 L -15 -50 L 20 -50 L 25 -35" fill="#1F2937" strokeWidth={2} />
      {/* Windshield */}
      <path d="M -28 -10 L -28 -25 L -12 -33 L -12 -10 Z" fill="#93C5FD" stroke="#60A5FA" strokeWidth={1} />
      {/* Wheels */}
      <circle cx={-15} cy={8} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={25} cy={8} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={-15} cy={8} r={4} fill="#9CA3AF" />
      <circle cx={25} cy={8} r={4} fill="#9CA3AF" />
      {/* Driver */}
      <circle cx={-20} cy={-22} r={6} fill="#FBBF24" />
      <circle cx={-20} cy={-24} r={3} fill="#FEF3C7" />
    </g>
  ),
  
  car: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Body */}
      <path d="M -35 0 L -35 -15 L -25 -15 L -15 -30 L 20 -30 L 30 -15 L 35 -15 L 35 0 Z" fill={color} stroke="#374151" strokeWidth={2} />
      {/* Windows */}
      <path d="M -12 -15 L -5 -28 L 15 -28 L 22 -15 Z" fill="#BFDBFE" stroke="#60A5FA" strokeWidth={1} />
      {/* Wheels */}
      <circle cx={-20} cy={5} r={8} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={20} cy={5} r={8} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={-20} cy={5} r={3} fill="#9CA3AF" />
      <circle cx={20} cy={5} r={3} fill="#9CA3AF" />
      {/* Headlights */}
      <rect x={32} y={-8} width={5} height={6} rx={1} fill="#FEF08A" />
    </g>
  ),
  
  scooter: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Body */}
      <ellipse cx={0} cy={-5} rx={25} ry={12} fill={color} stroke="#374151" strokeWidth={2} />
      {/* Handlebar */}
      <line x1={-15} y1={-20} x2={-15} y2={-35} stroke="#374151" strokeWidth={3} />
      <line x1={-25} y1={-35} x2={-5} y2={-35} stroke="#374151" strokeWidth={3} />
      {/* Wheels */}
      <circle cx={-20} cy={10} r={12} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={20} cy={10} r={12} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={-20} cy={10} r={5} fill="#9CA3AF" />
      <circle cx={20} cy={10} r={5} fill="#9CA3AF" />
      {/* Rider */}
      <circle cx={0} cy={-25} r={8} fill="#FBBF24" />
    </g>
  ),
  
  cycle: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Frame */}
      <path d="M -20 0 L 0 -25 L 20 0" stroke={color} strokeWidth={3} fill="none" />
      <line x1={0} y1={-25} x2={0} y2={0} stroke={color} strokeWidth={3} />
      {/* Handlebar */}
      <line x1={-5} y1={-30} x2={5} y2={-30} stroke="#374151" strokeWidth={2} />
      <line x1={0} y1={-25} x2={0} y2={-30} stroke="#374151" strokeWidth={2} />
      {/* Wheels */}
      <circle cx={-20} cy={8} r={15} fill="none" stroke="#374151" strokeWidth={3} />
      <circle cx={20} cy={8} r={15} fill="none" stroke="#374151" strokeWidth={3} />
      {/* Spokes */}
      {[0, 60, 120, 180, 240, 300].map((angle) => (
        <line
          key={angle}
          x1={-20}
          y1={8}
          x2={-20 + 12 * Math.cos((angle * Math.PI) / 180)}
          y2={8 + 12 * Math.sin((angle * Math.PI) / 180)}
          stroke="#9CA3AF"
          strokeWidth={1}
        />
      ))}
    </g>
  ),
  
  train: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Engine */}
      <rect x={-40} y={-30} width={80} height={35} rx={5} fill={color} stroke="#374151" strokeWidth={2} />
      {/* Chimney */}
      <rect x={-30} y={-45} width={12} height={15} rx={2} fill="#374151" />
      {/* Windows */}
      <rect x={-20} y={-25} width={15} height={12} rx={2} fill="#BFDBFE" />
      <rect x={5} y={-25} width={15} height={12} rx={2} fill="#BFDBFE" />
      {/* Wheels */}
      <circle cx={-25} cy={10} r={12} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={25} cy={10} r={12} fill="#1F2937" stroke="#374151" strokeWidth={3} />
    </g>
  ),
  
  bus: ({ color, scale }) => (
    <g transform={`scale(${scale})`}>
      {/* Body */}
      <rect x={-50} y={-35} width={100} height={40} rx={5} fill={color} stroke="#374151" strokeWidth={2} />
      {/* Windows */}
      {[-35, -15, 5, 25].map((x, i) => (
        <rect key={i} x={x} y={-30} width={15} height={20} rx={2} fill="#BFDBFE" stroke="#60A5FA" strokeWidth={1} />
      ))}
      {/* Wheels */}
      <circle cx={-30} cy={10} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={30} cy={10} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
    </g>
  ),
};

const Vehicle = ({
  type = 'auto_rickshaw',
  x = 0,
  y = 0,
  scale = 1,
  color = '#FF9933',
  label = '',
  animate = false,
  animateX = 0,
  showSpeed = false,
  speed = 0,
}) => {
  const VehicleComponent = VEHICLE_TYPES[type] || VEHICLE_TYPES.auto_rickshaw;

  return (
    <motion.g
      initial={animate ? { x: 0 } : undefined}
      animate={animate ? { x: animateX } : undefined}
      transition={{ duration: 2, ease: 'easeOut' }}
    >
      <g transform={`translate(${x}, ${y})`}>
        <VehicleComponent color={color} scale={scale} />
        
        {/* Label */}
        {label && (
          <text
            x={0}
            y={35}
            fontSize={12}
            textAnchor="middle"
            fill="#374151"
            fontWeight="bold"
            fontFamily="'Caveat', cursive"
          >
            {label}
          </text>
        )}
        
        {/* Speed indicator */}
        {showSpeed && (
          <g transform="translate(0, -55)">
            <rect x={-25} y={-12} width={50} height={20} rx={5} fill={color} opacity={0.9} />
            <text x={0} y={3} fontSize={11} textAnchor="middle" fill="white" fontWeight="bold">
              {speed} m/s
            </text>
          </g>
        )}
      </g>
    </motion.g>
  );
};

export default Vehicle;

