/**
 * 🧪 CHEMISTRY PRIMITIVES
 * =======================
 * 
 * Visual components for chemistry concepts.
 * Built on universal primitives with chemistry-specific styling.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PRIMITIVE_THEMES } from '../UniversalPrimitives';

const theme = PRIMITIVE_THEMES.chemistry;

/**
 * Atom - Nucleus with electron shells
 */
export const Atom = ({
  cx = 50,
  cy = 50,
  symbol = 'X',
  atomicNumber = 0,
  shells = [2, 8], // Electrons per shell
  color = theme.primary,
  size = 'medium', // small, medium, large
  animate = true,
}) => {
  const sizes = { small: 30, medium: 50, large: 70 };
  const nucleusR = sizes[size] * 0.3;
  const shellSpacing = sizes[size] * 0.35;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, type: 'spring' }}
    >
      {/* Electron shells */}
      {shells.map((electrons, i) => (
        <g key={i}>
          {/* Shell circle */}
          <circle
            cx={cx}
            cy={cy}
            r={nucleusR + shellSpacing * (i + 1)}
            fill="none"
            stroke={`${color}40`}
            strokeWidth={1}
            strokeDasharray="4,4"
          />
          {/* Electrons on shell */}
          {Array.from({ length: electrons }).map((_, j) => {
            const angle = (j / electrons) * Math.PI * 2 - Math.PI / 2;
            const r = nucleusR + shellSpacing * (i + 1);
            return (
              <motion.circle
                key={j}
                cx={cx + r * Math.cos(angle)}
                cy={cy + r * Math.sin(angle)}
                r={4}
                fill={theme.secondary}
                initial={animate ? { scale: 0 } : false}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 + i * 0.1 + j * 0.02 }}
              />
            );
          })}
        </g>
      ))}
      
      {/* Nucleus */}
      <circle
        cx={cx}
        cy={cy}
        r={nucleusR}
        fill={color}
      />
      <text
        x={cx}
        y={cy + 4}
        textAnchor="middle"
        fontSize={nucleusR * 0.8}
        fontWeight={700}
        fill="white"
      >
        {symbol}
      </text>
    </motion.g>
  );
};

/**
 * Molecule - Connected atoms
 */
export const Molecule = ({
  x = 0,
  y = 0,
  atoms = [{ symbol: 'H' }, { symbol: 'O' }, { symbol: 'H' }],
  bonds = [[0, 1], [1, 2]], // Pairs of atom indices
  bondTypes = [1, 1], // 1=single, 2=double, 3=triple
  layout = 'linear', // linear, bent, tetrahedral
  color = theme.primary,
  animate = true,
}) => {
  const atomSpacing = 60;
  
  // Calculate atom positions based on layout
  const getAtomPosition = (index, total) => {
    switch (layout) {
      case 'bent':
        const angle = index === 1 ? 0 : (index === 0 ? -0.4 : 0.4) * Math.PI;
        const dist = index === 1 ? 0 : atomSpacing;
        return {
          x: x + Math.cos(angle) * dist + atomSpacing,
          y: y + Math.sin(angle) * dist + 40,
        };
      case 'linear':
      default:
        return { x: x + index * atomSpacing + 20, y: y + 40 };
    }
  };
  
  const positions = atoms.map((_, i) => getAtomPosition(i, atoms.length));
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
    >
      {/* Bonds */}
      {bonds.map(([from, to], i) => {
        const p1 = positions[from];
        const p2 = positions[to];
        const bondType = bondTypes[i] || 1;
        const offset = bondType > 1 ? 4 : 0;
        
        return (
          <g key={`bond-${i}`}>
            {Array.from({ length: bondType }).map((_, j) => (
              <line
                key={j}
                x1={p1.x}
                y1={p1.y + (j - (bondType - 1) / 2) * offset * 2}
                x2={p2.x}
                y2={p2.y + (j - (bondType - 1) / 2) * offset * 2}
                stroke={color}
                strokeWidth={3}
              />
            ))}
          </g>
        );
      })}
      
      {/* Atoms */}
      {atoms.map((atom, i) => (
        <g key={i}>
          <circle
            cx={positions[i].x}
            cy={positions[i].y}
            r={20}
            fill={i === Math.floor(atoms.length / 2) ? theme.secondary : color}
          />
          <text
            x={positions[i].x}
            y={positions[i].y + 5}
            textAnchor="middle"
            fontSize={14}
            fontWeight={700}
            fill="white"
          >
            {atom.symbol}
          </text>
        </g>
      ))}
    </motion.g>
  );
};

/**
 * Reaction Arrow - For chemical equations
 */
export const ReactionArrow = ({
  x1 = 0,
  y1 = 50,
  x2 = 100,
  y2 = 50,
  reversible = false,
  catalyst = '',
  conditions = '', // e.g., "heat", "pressure"
  color = theme.primary,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.4 }}
  >
    {/* Main arrow */}
    <line x1={x1} y1={y1} x2={x2 - 10} y2={y2} stroke={color} strokeWidth={2} />
    <polygon
      points={`${x2},${y2} ${x2 - 12},${y2 - 6} ${x2 - 12},${y2 + 6}`}
      fill={color}
    />
    
    {/* Reverse arrow for equilibrium */}
    {reversible && (
      <>
        <line x1={x2} y1={y1 + 10} x2={x1 + 10} y2={y2 + 10} stroke={color} strokeWidth={2} />
        <polygon
          points={`${x1},${y2 + 10} ${x1 + 12},${y2 + 4} ${x1 + 12},${y2 + 16}`}
          fill={color}
        />
      </>
    )}
    
    {/* Conditions above arrow */}
    {(catalyst || conditions) && (
      <text
        x={(x1 + x2) / 2}
        y={y1 - 10}
        textAnchor="middle"
        fontSize={11}
        fill={theme.accent}
      >
        {catalyst || conditions}
      </text>
    )}
  </motion.g>
);

/**
 * Orbital - Electron orbital representation
 */
export const Orbital = ({
  cx = 50,
  cy = 50,
  type = 's', // s, p, d, f
  orientation = 'x', // x, y, z for p orbitals
  color = theme.primary,
  size = 40,
  animate = true,
}) => {
  const renderOrbital = () => {
    switch (type) {
      case 's':
        return <circle cx={cx} cy={cy} r={size} fill={`${color}30`} stroke={color} strokeWidth={2} />;
      case 'p':
        // Dumbbell shape
        return (
          <g>
            <ellipse cx={cx - size * 0.6} cy={cy} rx={size * 0.5} ry={size * 0.3} fill={`${color}30`} stroke={color} strokeWidth={2} />
            <ellipse cx={cx + size * 0.6} cy={cy} rx={size * 0.5} ry={size * 0.3} fill={`${theme.secondary}30`} stroke={theme.secondary} strokeWidth={2} />
          </g>
        );
      default:
        return <circle cx={cx} cy={cy} r={size} fill={`${color}30`} stroke={color} strokeWidth={2} />;
    }
  };
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.5 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      {renderOrbital()}
      <text x={cx} y={cy + size + 16} textAnchor="middle" fontSize={12} fill={color}>
        {type} orbital
      </text>
    </motion.g>
  );
};

/**
 * Beaker - Lab equipment
 */
export const Beaker = ({
  x = 0,
  y = 0,
  width = 60,
  height = 80,
  fillLevel = 0.6, // 0 to 1
  liquidColor = theme.accent,
  label = '',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
  >
    {/* Beaker outline */}
    <path
      d={`M ${x} ${y + 10} L ${x} ${y + height} L ${x + width} ${y + height} L ${x + width} ${y + 10}`}
      fill="none"
      stroke="#64748B"
      strokeWidth={2}
    />
    {/* Lip */}
    <path
      d={`M ${x - 5} ${y + 10} L ${x} ${y} L ${x} ${y + 10}`}
      fill="none"
      stroke="#64748B"
      strokeWidth={2}
    />
    <path
      d={`M ${x + width + 5} ${y + 10} L ${x + width} ${y} L ${x + width} ${y + 10}`}
      fill="none"
      stroke="#64748B"
      strokeWidth={2}
    />
    
    {/* Liquid */}
    <motion.rect
      x={x + 2}
      y={y + height - (height - 12) * fillLevel}
      width={width - 4}
      height={(height - 12) * fillLevel}
      fill={`${liquidColor}60`}
      initial={animate ? { height: 0, y: y + height } : false}
      animate={{ height: (height - 12) * fillLevel, y: y + height - (height - 12) * fillLevel }}
      transition={{ duration: 0.8, delay: 0.2 }}
    />
    
    {/* Label */}
    {label && (
      <text x={x + width / 2} y={y + height + 16} textAnchor="middle" fontSize={11} fill="#64748B">
        {label}
      </text>
    )}
  </motion.g>
);

// Registry
export const CHEMISTRY_PRIMITIVES = {
  atom: Atom,
  molecule: Molecule,
  reaction_arrow: ReactionArrow,
  orbital: Orbital,
  beaker: Beaker,
};

export default CHEMISTRY_PRIMITIVES;

