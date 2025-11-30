/**
 * ⚛️ Atom Primitive
 * =================
 * 
 * Animated atom model for chemistry/physics.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Atom = ({
  x = 0,
  y = 0,
  protons = 1,
  neutrons = 0,
  electrons = 1,
  size = 80,
  animated = true,
  showLabels = true,
  element = '',
  showOrbitals = true,
}) => {
  const nucleusRadius = size * 0.2;
  const orbitalRadii = [size * 0.4, size * 0.6, size * 0.8];
  
  // Distribute electrons across orbitals (simplified 2-8-8 rule)
  const electronConfig = [];
  let remaining = electrons;
  const maxPerShell = [2, 8, 8, 18];
  
  for (let i = 0; i < maxPerShell.length && remaining > 0; i++) {
    const inShell = Math.min(remaining, maxPerShell[i]);
    electronConfig.push(inShell);
    remaining -= inShell;
  }

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Electron orbitals */}
      {showOrbitals && electronConfig.map((_, shellIndex) => (
        <motion.ellipse
          key={shellIndex}
          cx={0}
          cy={0}
          rx={orbitalRadii[shellIndex]}
          ry={orbitalRadii[shellIndex] * 0.4}
          fill="none"
          stroke="#94A3B8"
          strokeWidth={1}
          strokeDasharray="4 2"
          initial={animated ? { opacity: 0, scale: 0 } : undefined}
          animate={animated ? { opacity: 1, scale: 1 } : undefined}
          transition={{ delay: 0.2 + shellIndex * 0.1 }}
        />
      ))}

      {/* Electrons */}
      {electronConfig.map((count, shellIndex) => 
        Array.from({ length: count }).map((_, electronIndex) => {
          const angle = (electronIndex / count) * 2 * Math.PI;
          const radius = orbitalRadii[shellIndex];
          const ex = Math.cos(angle) * radius;
          const ey = Math.sin(angle) * radius * 0.4;
          
          return (
            <motion.g
              key={`${shellIndex}-${electronIndex}`}
              animate={animated ? {
                x: [ex, -ex, ex],
                y: [ey, -ey, ey],
              } : undefined}
              transition={{
                duration: 2 + shellIndex * 0.5,
                repeat: Infinity,
                ease: 'linear',
              }}
            >
              <circle
                cx={0}
                cy={0}
                r={5}
                fill="#3B82F6"
              />
              <text x={0} y={2} fontSize={6} textAnchor="middle" fill="white" fontWeight="bold">
                e⁻
              </text>
            </motion.g>
          );
        })
      )}

      {/* Nucleus */}
      <motion.g
        initial={animated ? { scale: 0 } : undefined}
        animate={animated ? { scale: 1 } : undefined}
        transition={{ type: 'spring', delay: 0.1 }}
      >
        {/* Protons */}
        {Array.from({ length: Math.min(protons, 6) }).map((_, i) => {
          const angle = (i / Math.min(protons, 6)) * 2 * Math.PI;
          const pr = nucleusRadius * 0.4;
          return (
            <circle
              key={`p-${i}`}
              cx={Math.cos(angle) * pr}
              cy={Math.sin(angle) * pr}
              r={nucleusRadius * 0.35}
              fill="#EF4444"
              stroke="#B91C1C"
              strokeWidth={1}
            />
          );
        })}
        
        {/* Neutrons */}
        {Array.from({ length: Math.min(neutrons, 6) }).map((_, i) => {
          const angle = (i / Math.min(neutrons, 6)) * 2 * Math.PI + 0.5;
          const nr = nucleusRadius * 0.25;
          return (
            <circle
              key={`n-${i}`}
              cx={Math.cos(angle) * nr}
              cy={Math.sin(angle) * nr}
              r={nucleusRadius * 0.3}
              fill="#6B7280"
              stroke="#4B5563"
              strokeWidth={1}
            />
          );
        })}
      </motion.g>

      {/* Element symbol */}
      {element && showLabels && (
        <text
          x={0}
          y={size + 20}
          fontSize={16}
          fontWeight="bold"
          textAnchor="middle"
          fill="#1F2937"
        >
          {element}
        </text>
      )}

      {/* Legend */}
      {showLabels && (
        <g transform={`translate(${size + 10}, ${-size * 0.3})`}>
          <circle cx={0} cy={0} r={5} fill="#EF4444" />
          <text x={10} y={4} fontSize={10} fill="#636E72">Protons: {protons}</text>
          
          <circle cx={0} cy={20} r={5} fill="#6B7280" />
          <text x={10} y={24} fontSize={10} fill="#636E72">Neutrons: {neutrons}</text>
          
          <circle cx={0} cy={40} r={5} fill="#3B82F6" />
          <text x={10} y={44} fontSize={10} fill="#636E72">Electrons: {electrons}</text>
        </g>
      )}
    </g>
  );
};

export default Atom;

