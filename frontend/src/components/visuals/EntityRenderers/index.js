/**
 * Entity Renderers - Domain-Specific SVG Components
 * Complete SVG components for Physics, Chemistry, Biology, Math entities
 * Used by AnimatedScene component for rendering animated elements
 */

import React from 'react';
import { motion } from 'framer-motion';

// ============================================================================
// PHYSICS ENTITIES
// ============================================================================

export const PhysicsEntities = {
  MetroTrainSVG: ({ size, color = '#7c3aed', ...props }) => {
    const width = size?.width || 120;
    const height = size?.height || 60;
    
    return (
      <svg width={width} height={height} viewBox="0 0 120 60" {...props}>
        {/* Metro train body */}
        <rect x="0" y="20" width="120" height="40" rx="8" fill={color} stroke="#5b21b6" strokeWidth="2"/>
        {/* Windows */}
        <rect x="10" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
        <rect x="45" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
        <rect x="85" y="28" width="25" height="18" rx="3" fill="#a5b4fc" opacity="0.8"/>
        {/* Wheels */}
        <circle cx="30" cy="62" r="6" fill="#1e293b"/>
        <circle cx="90" cy="62" r="6" fill="#1e293b"/>
        {/* Front nose */}
        <path d="M 0 30 L -10 40 L -10 50 L 0 60" fill="#5b21b6"/>
        {/* Label */}
        <text x="60" y="42" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">METRO</text>
      </svg>
    );
  },

  DirectionArrowSVG: ({ direction = 0, size, ...props }) => {
    const width = size?.width || 80;
    const height = size?.height || 80;
    
    return (
      <svg width={width} height={height} viewBox="0 0 80 80" style={{ transform: `rotate(${direction}deg)`, transformOrigin: 'center' }} {...props}>
        <defs>
          <marker id="arrowhead-dir" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#dc2626"/>
          </marker>
        </defs>
        {/* Arrow shaft */}
        <line x1="10" y1="40" x2="70" y2="40" stroke="#dc2626" strokeWidth="4" markerEnd="url(#arrowhead-dir)"/>
        {/* Label */}
        <text x="40" y="25" textAnchor="middle" fill="#dc2626" fontSize="10" fontWeight="bold">DIRECTION</text>
        {/* Circular guide */}
        <circle cx="40" cy="40" r="35" fill="none" stroke="#dc2626" strokeWidth="2" strokeDasharray="5,5" opacity="0.5"/>
      </svg>
    );
  },

  SpeedometerSVG: ({ speed = 60, size = { width: 100, height: 100 }, ...props }) => {
    const needleAngle = (speed / 120) * 180 - 90; // Map 0-120 to -90 to 90 degrees
    
    return (
      <svg width={size.width} height={size.height} viewBox="0 0 100 100" {...props}>
        {/* Outer circle */}
        <circle cx="50" cy="60" r="45" fill="white" stroke="#1e293b" strokeWidth="3"/>
        <circle cx="50" cy="60" r="38" fill="none" stroke="#e2e8f0" strokeWidth="2"/>
        
        {/* Speed marks */}
        <line x1="50" y1="25" x2="50" y2="30" stroke="#475569" strokeWidth="2"/>
        <line x1="78" y1="32" x2="74" y2="36" stroke="#475569" strokeWidth="2"/>
        <line x1="88" y1="60" x2="83" y2="60" stroke="#475569" strokeWidth="2"/>
        <line x1="22" y1="32" x2="26" y2="36" stroke="#475569" strokeWidth="2"/>
        <line x1="12" y1="60" x2="17" y2="60" stroke="#475569" strokeWidth="2"/>
        
        {/* Needle */}
        <motion.line
          x1="50"
          y1="60"
          x2="70"
          y2="45"
          stroke="#dc2626"
          strokeWidth="3"
          strokeLinecap="round"
          style={{ transformOrigin: '50px 60px' }}
          animate={{ rotate: needleAngle }}
          transition={{ duration: 0.5 }}
        />
        <circle cx="50" cy="60" r="5" fill="#dc2626"/>
        
        {/* Speed value */}
        <text x="50" y="80" textAnchor="middle" fill="#1e293b" fontSize="14" fontWeight="bold">{speed}</text>
        <text x="50" y="92" textAnchor="middle" fill="#64748b" fontSize="10">km/h</text>
      </svg>
    );
  },

  CricketBallSVG: ({ size = { width: 30, height: 30 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 30 30" {...props}>
      <circle cx="15" cy="15" r="14" fill="#dc2626" stroke="#991b1b" strokeWidth="2"/>
      {/* Seam stitches */}
      <path d="M 5 8 Q 15 12 25 8" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round"/>
      <path d="M 5 22 Q 15 18 25 22" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round"/>
      <circle cx="15" cy="15" r="14" fill="none" stroke="#991b1b" strokeWidth="1" opacity="0.3"/>
    </svg>
  ),

  CarSVG: ({ size = { width: 100, height: 50 }, color = '#3b82f6', ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 100 50" {...props}>
      {/* Car body */}
      <rect x="10" y="20" width="80" height="20" rx="4" fill={color} stroke="#1e40af" strokeWidth="2"/>
      {/* Windows */}
      <rect x="20" y="10" width="25" height="12" rx="3" fill="#60a5fa" opacity="0.7"/>
      <rect x="50" y="10" width="30" height="12" rx="3" fill="#60a5fa" opacity="0.7"/>
      {/* Wheels */}
      <circle cx="25" cy="42" r="6" fill="#1e293b"/>
      <circle cx="25" cy="42" r="3" fill="#64748b"/>
      <circle cx="75" cy="42" r="6" fill="#1e293b"/>
      <circle cx="75" cy="42" r="3" fill="#64748b"/>
      {/* Headlight */}
      <circle cx="88" cy="25" r="4" fill="#fef08a" opacity="0.9"/>
    </svg>
  )
};

// ============================================================================
// CHEMISTRY ENTITIES
// ============================================================================

export const ChemistryEntities = {
  AtomNucleusSVG: ({ element = 'C', size = { width: 60, height: 60 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 60 60" {...props}>
      <defs>
        <radialGradient id="nucleus-gradient">
          <stop offset="0%" stopColor="#34d399"/>
          <stop offset="100%" stopColor="#059669"/>
        </radialGradient>
      </defs>
      {/* Nucleus core */}
      <circle cx="30" cy="30" r="25" fill="url(#nucleus-gradient)" stroke="#059669" strokeWidth="3"/>
      {/* Protons/neutrons */}
      <circle cx="22" cy="24" r="8" fill="#10b981" opacity="0.7"/>
      <circle cx="38" cy="28" r="8" fill="#10b981" opacity="0.7"/>
      <circle cx="30" cy="36" r="8" fill="#10b981" opacity="0.7"/>
      {/* Element label */}
      <text x="30" y="35" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">{element}</text>
      {/* Glow effect */}
      <motion.circle
        cx="30"
        cy="30"
        r="28"
        fill="none"
        stroke="#6ee7b7"
        strokeWidth="1"
        opacity="0.4"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </svg>
  ),

  ElectronSVG: ({ size = { width: 20, height: 20 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 20 20" {...props}>
      <defs>
        <radialGradient id="electron-gradient">
          <stop offset="0%" stopColor="#93c5fd"/>
          <stop offset="100%" stopColor="#3b82f6"/>
        </radialGradient>
      </defs>
      <circle cx="10" cy="10" r="8" fill="#3b82f6" stroke="#1e40af" strokeWidth="2"/>
      <circle cx="10" cy="10" r="6" fill="url(#electron-gradient)"/>
      <text x="10" y="13" textAnchor="middle" fill="white" fontSize="9" fontWeight="bold">e⁻</text>
    </svg>
  ),

  ElectronShellsSVG: ({ shells = [2, 8, 4], size = { width: 300, height: 300 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 300 300" {...props}>
      {shells.map((electronCount, shellIndex) => {
        const radius = 60 + (shellIndex * 50);
        const isValenceShell = shellIndex === shells.length - 1;
        
        return (
          <g key={shellIndex}>
            {/* Shell orbit */}
            <circle
              cx="150"
              cy="150"
              r={radius}
              fill="none"
              stroke={isValenceShell ? "#10b981" : "#6b7280"}
              strokeWidth={isValenceShell ? "3" : "2"}
              strokeDasharray="5,5"
              opacity={isValenceShell ? "0.8" : "0.5"}
            />
            
            {/* Electrons on this shell */}
            {Array.from({ length: electronCount }).map((_, electronIndex) => {
              const angle = (360 / electronCount) * electronIndex;
              const x = 150 + radius * Math.cos((angle * Math.PI) / 180);
              const y = 150 + radius * Math.sin((angle * Math.PI) / 180);
              
              return (
                <motion.g
                  key={electronIndex}
                  animate={{
                    x: [x - 150, x - 150],
                    y: [y - 150, y - 150],
                    rotate: 360
                  }}
                  transition={{
                    duration: 4 + shellIndex,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                >
                  <circle cx={x} cy={y} r="6" fill="#3b82f6" stroke="#1e40af" strokeWidth="1"/>
                </motion.g>
              );
            })}
          </g>
        );
      })}
    </svg>
  ),

  ChemicalBondSVG: ({ type = 'single', from = {x: 250, y: 300}, to = {x: 450, y: 300}, ...props }) => {
    const bondCount = { 'single': 1, 'double': 2, 'triple': 3 }[type] || 1;
    const spacing = 8;
    
    return (
      <svg width="800" height="600" viewBox="0 0 800 600" style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }} {...props}>
        {Array.from({ length: bondCount }).map((_, i) => {
          const offset = (i - (bondCount - 1) / 2) * spacing;
          return (
            <motion.line
              key={i}
              x1={from.x}
              y1={from.y + offset}
              x2={to.x}
              y2={to.y + offset}
              stroke="#7c3aed"
              strokeWidth="4"
              strokeLinecap="round"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 1.5, delay: i * 0.2 }}
            />
          );
        })}
      </svg>
    );
  }
};

// ============================================================================
// BIOLOGY ENTITIES
// ============================================================================

export const BiologyEntities = {
  ChloroplastSVG: ({ active = true, size = { width: 120, height: 80 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 120 80" {...props}>
      <defs>
        <radialGradient id="chloroplast-gradient">
          <stop offset="0%" stopColor="#86efac"/>
          <stop offset="100%" stopColor="#22c55e"/>
        </radialGradient>
      </defs>
      {/* Chloroplast outer membrane */}
      <ellipse cx="60" cy="40" rx="55" ry="35" fill="#22c55e" stroke="#15803d" strokeWidth="3" opacity="0.9"/>
      <ellipse cx="60" cy="40" rx="50" ry="30" fill="url(#chloroplast-gradient)"/>
      
      {/* Grana stacks (thylakoids) */}
      <rect x="30" y="25" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
      <rect x="32" y="28" width="11" height="2" fill="#052e16" opacity="0.8"/>
      <rect x="55" y="32" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
      <rect x="57" y="35" width="11" height="2" fill="#052e16" opacity="0.8"/>
      <rect x="75" y="20" width="15" height="8" rx="2" fill="#15803d" opacity="0.6"/>
      <rect x="77" y="23" width="11" height="2" fill="#052e16" opacity="0.8"/>
      
      {/* Glow effect when active */}
      {active && (
        <motion.ellipse
          cx="60"
          cy="40"
          rx="58"
          ry="38"
          fill="none"
          stroke="#86efac"
          strokeWidth="2"
          opacity="0.6"
          animate={{ scale: [1, 1.05, 1], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </svg>
  ),

  MitochondriaSVG: ({ active = true, size = { width: 200, height: 150 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 200 150" {...props}>
      <defs>
        <radialGradient id="mitochondria-gradient">
          <stop offset="0%" stopColor="#fca5a5"/>
          <stop offset="100%" stopColor="#ef4444"/>
        </radialGradient>
      </defs>
      {/* Outer membrane */}
      <ellipse cx="100" cy="75" rx="95" ry="70" fill="#ef4444" stroke="#dc2626" strokeWidth="3" opacity="0.9"/>
      <ellipse cx="100" cy="75" rx="90" ry="65" fill="url(#mitochondria-gradient)"/>
      
      {/* Cristae folds (inner membrane) */}
      <path d="M 30 50 Q 40 60 30 70 Q 40 80 30 90" stroke="#991b1b" strokeWidth="2" fill="none" opacity="0.7"/>
      <path d="M 50 45 Q 60 55 50 65 Q 60 75 50 85 Q 60 95 50 105" stroke="#991b1b" strokeWidth="2" fill="none" opacity="0.7"/>
      <path d="M 70 50 Q 80 60 70 70 Q 80 80 70 90" stroke="#991b1b" strokeWidth="2" fill="none" opacity="0.7"/>
      <path d="M 120 50 Q 130 60 120 70 Q 130 80 120 90" stroke="#991b1b" strokeWidth="2" fill="none" opacity="0.7"/>
      <path d="M 150 45 Q 160 55 150 65 Q 160 75 150 85" stroke="#991b1b" strokeWidth="2" fill="none" opacity="0.7"/>
      
      {/* Glow when active */}
      {active && (
        <motion.ellipse
          cx="100"
          cy="75"
          rx="98"
          ry="73"
          fill="none"
          stroke="#fca5a5"
          strokeWidth="2"
          opacity="0.5"
          animate={{ scale: [1, 1.03, 1], opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </svg>
  ),

  MoleculeSVG: ({ type = 'glucose', size = { width: 60, height: 60 }, ...props }) => (
    <svg width={size.width} height={size.height} viewBox="0 0 60 60" {...props}>
      {type === 'glucose' && (
        <g>
          {/* Hexagonal glucose structure */}
          <polygon
            points="30,10 45,20 45,40 30,50 15,40 15,20"
            fill="#fcd34d"
            stroke="#f59e0b"
            strokeWidth="2"
          />
          <text x="30" y="35" textAnchor="middle" fill="#78350f" fontSize="12" fontWeight="bold">C₆H₁₂O₆</text>
        </g>
      )}
      {type === 'co2' && (
        <g>
          {/* CO2 linear molecule */}
          <circle cx="20" cy="30" r="8" fill="#9ca3af" stroke="#6b7280" strokeWidth="2"/>
          <circle cx="40" cy="30" r="10" fill="#ef4444" stroke="#dc2626" strokeWidth="2"/>
          <text x="20" y="34" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">C</text>
          <text x="40" y="34" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">O</text>
        </g>
      )}
      {type === 'o2' && (
        <g>
          {/* O2 double bond */}
          <circle cx="20" cy="30" r="10" fill="#60a5fa" stroke="#3b82f6" strokeWidth="2"/>
          <circle cx="40" cy="30" r="10" fill="#60a5fa" stroke="#3b82f6" strokeWidth="2"/>
          <line x1="20" y1="27" x2="40" y2="27" stroke="#1e40af" strokeWidth="2"/>
          <line x1="20" y1="33" x2="40" y2="33" stroke="#1e40af" strokeWidth="2"/>
        </g>
      )}
    </svg>
  )
};

// ============================================================================
// MATH ENTITIES
// ============================================================================

export const MathEntities = {
  ParabolaSVG: ({ a = 1, b = 0, c = 0, size = { width: 600, height: 400 }, ...props }) => {
    // Generate parabola path
    const points = [];
    for (let x = -10; x <= 10; x += 0.5) {
      const y = a * x * x + b * x + c;
      const screenX = 300 + x * 30;
      const screenY = 350 - y * 30;
      points.push(`${screenX},${screenY}`);
    }
    const pathData = `M ${points.join(' L ')}`;
    
    return (
      <svg width={size.width} height={size.height} viewBox="0 0 600 400" {...props}>
        {/* Axes */}
        <line x1="50" y1="350" x2="550" y2="350" stroke="#9ca3af" strokeWidth="2"/>
        <line x1="300" y1="50" x2="300" y2="380" stroke="#9ca3af" strokeWidth="2"/>
        
        {/* Parabola curve */}
        <motion.path
          d={pathData}
          stroke="#7c3aed"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: "easeInOut" }}
        />
        
        {/* Vertex point */}
        <circle cx={300 - (b / (2 * a)) * 30} cy={350 - (c - (b * b) / (4 * a)) * 30} r="6" fill="#dc2626"/>
      </svg>
    );
  },

  LineSVG: ({ slope = 1, intercept = 0, size = { width: 600, height: 400 }, ...props }) => {
    const x1 = 50, y1 = 350 - (slope * -8 + intercept) * 30;
    const x2 = 550, y2 = 350 - (slope * 8 + intercept) * 30;
    
    return (
      <svg width={size.width} height={size.height} viewBox="0 0 600 400" {...props}>
        {/* Axes */}
        <line x1="50" y1="350" x2="550" y2="350" stroke="#9ca3af" strokeWidth="2"/>
        <line x1="300" y1="50" x2="300" y2="380" stroke="#9ca3af" strokeWidth="2"/>
        
        {/* Line */}
        <motion.line
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="#3b82f6"
          strokeWidth="3"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5 }}
        />
        
        {/* Y-intercept point */}
        <circle cx="300" cy={350 - intercept * 30} r="6" fill="#dc2626"/>
      </svg>
    );
  },

  SlopeTriangleSVG: ({ slope = 1, size = { width: 100, height: 80 }, position = {x: 350, y: 280}, ...props }) => {
    const rise = -60 * slope;
    const run = 60;
    
    return (
      <svg width={size.width} height={size.height} viewBox="0 0 100 80" style={{ position: 'absolute', left: position.x, top: position.y }} {...props}>
        {/* Triangle */}
        <motion.path
          d={`M 0 60 L ${run} 60 L ${run} ${60 + rise} Z`}
          fill="#fde047"
          stroke="#eab308"
          strokeWidth="2"
          opacity="0.7"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        />
        
        {/* Rise label */}
        <text x={run + 10} y={60 + rise / 2} fill="#78350f" fontSize="12" fontWeight="bold">rise</text>
        {/* Run label */}
        <text x={run / 2} y={75} fill="#78350f" fontSize="12" fontWeight="bold">run</text>
      </svg>
    );
  }
};

// ============================================================================
// GENERIC/UTILITY ENTITIES
// ============================================================================

export const UtilityEntities = {
  BackgroundLayer: ({ layer, colors, dimensions = { width: 800, height: 600 } }) => {
    const layerColors = {
      'sky_blue': 'linear-gradient(to bottom, #87CEEB, #B0E0E6)',
      'buildings_silhouette': '#6B7280',
      'platform_floor': '#9CA3AF',
      'field_grass': 'linear-gradient(to bottom, #22C55E, #16A34A)',
      'grid_paper': '#F3F4F6'
    };
    
    const bgStyle = layerColors[layer] || '#F3F4F6';
    
    return (
      <div
        className={`layer-${layer}`}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: dimensions.width,
          height: dimensions.height,
          background: bgStyle,
          zIndex: -1
        }}
      />
    );
  },

  TrajectoryPathSVG: ({ path, color = '#dc2626', ...props }) => (
    <motion.path
      d={path}
      stroke={color}
      strokeWidth="2"
      fill="none"
      strokeDasharray="5,5"
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 0.7 }}
      transition={{ duration: 1, delay: 0.3 }}
      {...props}
    />
  ),

  VectorArrowSVG: ({ from, to, color = '#dc2626', label, ...props }) => {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);
    const length = Math.sqrt(dx * dx + dy * dy);
    
    return (
      <svg width="800" height="600" viewBox="0 0 800 600" style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }} {...props}>
        <defs>
          <marker id={`arrow-${label}`} markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill={color}/>
          </marker>
        </defs>
        <motion.line
          x1={from.x}
          y1={from.y}
          x2={to.x}
          y2={to.y}
          stroke={color}
          strokeWidth="3"
          markerEnd={`url(#arrow-${label})`}
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.8 }}
        />
        {label && (
          <text x={(from.x + to.x) / 2} y={(from.y + to.y) / 2 - 10} fill={color} fontSize="14" fontWeight="bold">
            {label}
          </text>
        )}
      </svg>
    );
  }
};

// ============================================================================
// EXPORT ALL
// ============================================================================

export default {
  Physics: PhysicsEntities,
  Chemistry: ChemistryEntities,
  Biology: BiologyEntities,
  Math: MathEntities,
  Utility: UtilityEntities
};

