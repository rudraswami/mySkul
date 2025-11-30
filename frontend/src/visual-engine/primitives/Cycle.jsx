/**
 * 🔄 Cycle Primitive
 * ==================
 * 
 * Circular cycle diagram for biology/chemistry processes.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Cycle = ({
  x = 0,
  y = 0,
  steps = [
    { name: 'Step 1', color: '#3B82F6', emoji: '1️⃣' },
    { name: 'Step 2', color: '#10B981', emoji: '2️⃣' },
    { name: 'Step 3', color: '#F59E0B', emoji: '3️⃣' },
    { name: 'Step 4', color: '#EF4444', emoji: '4️⃣' },
  ],
  radius = 100,
  title = 'Cycle',
  animated = true,
  currentStep = -1, // -1 = show all, 0+ = highlight specific step
  showArrows = true,
  clockwise = true,
}) => {
  const numSteps = steps.length;
  const angleStep = (2 * Math.PI) / numSteps;
  const startAngle = -Math.PI / 2; // Start from top

  // Calculate positions
  const getPosition = (index) => {
    const angle = startAngle + index * angleStep * (clockwise ? 1 : -1);
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
    };
  };

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Center circle with title */}
      <motion.circle
        cx={0}
        cy={0}
        r={radius * 0.35}
        fill="#F3F4F6"
        stroke="#D1D5DB"
        strokeWidth={2}
        initial={animated ? { scale: 0 } : undefined}
        animate={animated ? { scale: 1 } : undefined}
        transition={{ duration: 0.5 }}
      />
      <text
        x={0}
        y={5}
        fontSize={12}
        fontWeight="bold"
        textAnchor="middle"
        fill="#374151"
      >
        {title}
      </text>

      {/* Connecting arrows */}
      {showArrows && steps.map((_, i) => {
        const pos1 = getPosition(i);
        const pos2 = getPosition((i + 1) % numSteps);
        
        // Calculate control point for curved arrow
        const midAngle = startAngle + (i + 0.5) * angleStep * (clockwise ? 1 : -1);
        const controlRadius = radius * 1.15;
        const ctrl = {
          x: Math.cos(midAngle) * controlRadius,
          y: Math.sin(midAngle) * controlRadius,
        };

        return (
          <motion.path
            key={`arrow-${i}`}
            d={`M ${pos1.x * 0.7} ${pos1.y * 0.7} Q ${ctrl.x * 0.65} ${ctrl.y * 0.65} ${pos2.x * 0.7} ${pos2.y * 0.7}`}
            stroke="#9CA3AF"
            strokeWidth={2}
            fill="none"
            markerEnd="url(#arrowhead)"
            initial={animated ? { pathLength: 0, opacity: 0 } : undefined}
            animate={animated ? { pathLength: 1, opacity: 1 } : undefined}
            transition={{ delay: 0.5 + i * 0.2, duration: 0.5 }}
          />
        );
      })}

      {/* Step nodes */}
      {steps.map((step, i) => {
        const pos = getPosition(i);
        const isActive = currentStep === -1 || currentStep === i;
        const nodeSize = radius * 0.28;

        return (
          <motion.g
            key={i}
            initial={animated ? { scale: 0, opacity: 0 } : undefined}
            animate={animated ? { scale: 1, opacity: isActive ? 1 : 0.4 } : undefined}
            transition={{ delay: i * 0.15, type: 'spring' }}
          >
            {/* Node circle */}
            <motion.circle
              cx={pos.x}
              cy={pos.y}
              r={nodeSize}
              fill={step.color}
              stroke={isActive ? '#1F2937' : 'transparent'}
              strokeWidth={3}
              animate={currentStep === i ? { scale: [1, 1.1, 1] } : undefined}
              transition={currentStep === i ? { repeat: Infinity, duration: 1 } : undefined}
            />

            {/* Emoji */}
            {step.emoji && (
              <text
                x={pos.x}
                y={pos.y - 8}
                fontSize={18}
                textAnchor="middle"
              >
                {step.emoji}
              </text>
            )}

            {/* Step name */}
            <text
              x={pos.x}
              y={pos.y + 12}
              fontSize={10}
              fontWeight="bold"
              textAnchor="middle"
              fill="white"
            >
              {step.name.length > 10 ? step.name.slice(0, 10) + '...' : step.name}
            </text>

            {/* External label */}
            {step.description && (
              <text
                x={pos.x * 1.45}
                y={pos.y * 1.45}
                fontSize={9}
                textAnchor="middle"
                fill="#636E72"
              >
                {step.description}
              </text>
            )}
          </motion.g>
        );
      })}

      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#9CA3AF" />
        </marker>
      </defs>
    </g>
  );
};

export default Cycle;

