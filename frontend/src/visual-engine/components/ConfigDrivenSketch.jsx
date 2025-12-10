/**
 * 🚀 CONFIG-DRIVEN SKETCH ENGINE V5.0 (SketchSense Universal)
 * =============================================================
 * 
 * THE ULTIMATE UNIVERSAL VISUAL ENGINE
 * 
 * EVOLUTION from V4.0:
 * - Multi-mode rendering (auto-detected from artifact)
 * - Dynamic layout engine (vertical, radial, horizontal)
 * - Math plot support (inline parsing)
 * - Physics trajectory rendering
 * - Concept map rendering
 * - Balance/scale relationships
 * - Intelligent styling based on context
 * - Professor output integration
 * 
 * RENDERING MODES:
 * - concept_map: Radial node layout with relationships
 * - process_flow: Vertical/horizontal step sequences
 * - math_plot: Function graphs with expression parsing
 * - trajectory: Projectile motion with vector arrows
 * - balance_scale: Comparison visualizations
 * - classic: Original template-based rendering (default)
 * 
 * BACKWARDS COMPATIBLE:
 * - All V4.0 configurations still work
 * - Template system intact
 * - Falls back gracefully if mode unknown
 * 
 * Architecture:
 * Backend sends blueprint → detectModeFromArtifact → Route to renderer
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';

// Import all templates
import {
  RaceTemplate,
  ProcessTemplate,
  CycleTemplate,
  GraphTemplate,
  StructureTemplate,
  CauseEffectTemplate,
  ScaleTemplate,
  TimelineTemplate,
  TEMPLATE_TYPES,
} from '../templates';

// Import primitives
import { COLORS, SUBJECT_THEMES } from '../primitives';

// ============ RENDERING MODES ============
const RENDER_MODES = {
  CLASSIC: 'classic',           // Original template-based (default)
  CONCEPT_MAP: 'concept_map',   // Radial node layout
  PROCESS_FLOW: 'process_flow', // Linear step flow
  MATH_PLOT: 'math_plot',       // Mathematical function graphs
  TRAJECTORY: 'trajectory',     // Physics projectile paths
  BALANCE_SCALE: 'balance_scale', // Comparison scales
  TIMELINE: 'timeline',         // Chronological events
  STRUCTURE: 'structure',       // Anatomy/component diagrams
};

// ============ MODE DETECTION ============
/**
 * Intelligent mode detection from artifact/blueprint
 * Analyzes structure to determine best rendering approach
 */
function detectModeFromArtifact(artifact) {
  if (!artifact) return RENDER_MODES.CLASSIC;
  
  // Explicit mode in blueprint
  if (artifact.mode && RENDER_MODES[artifact.mode.toUpperCase()]) {
    return artifact.mode.toLowerCase();
  }
  
  // Check render_directives
  if (artifact.render_directives?.mode) {
    return artifact.render_directives.mode;
  }
  
  // Auto-detect from structure
  const config = artifact.config || artifact;
  
  // Math plot: has expression, formula, or function
  if (artifact.expression || artifact.formula_plot || config.function || 
      config.math_expression || artifact.plot_type === 'function') {
    return RENDER_MODES.MATH_PLOT;
  }
  
  // Trajectory: has motion, velocity vectors, or trajectory_points
  if (config.motion || config.vx !== undefined || config.vy !== undefined ||
      config.trajectory_points || config.projectile || artifact.type === 'trajectory') {
    return RENDER_MODES.TRAJECTORY;
  }
  
  // Concept map: has nodes with relationships
  if (config.nodes && config.relationships) {
    return RENDER_MODES.CONCEPT_MAP;
  }
  
  // Process flow: has steps array with sequential structure
  if (config.steps && Array.isArray(config.steps) && config.steps.length > 0) {
    const hasInputsOutputs = config.inputs || config.outputs;
    if (hasInputsOutputs) return RENDER_MODES.PROCESS_FLOW;
  }
  
  // Balance/scale: has left/right items or comparison
  if (config.left_items && config.right_items) {
    return RENDER_MODES.BALANCE_SCALE;
  }
  
  // Timeline: has events with dates/times
  if (config.events && config.events.some(e => e.time || e.date || e.order)) {
    return RENDER_MODES.TIMELINE;
  }
  
  // Structure: has components with positions
  if (config.components && config.components.some(c => c.x !== undefined || c.y !== undefined)) {
    return RENDER_MODES.STRUCTURE;
  }
  
  // Default: use classic template-based
  return RENDER_MODES.CLASSIC;
}

// ============ LAYOUT HELPERS ============
/**
 * Generate radial positions for concept map nodes
 */
function getRadialPositions(nodeCount, centerX = 250, centerY = 200, radius = 120) {
  const positions = [];
  for (let i = 0; i < nodeCount; i++) {
    const angle = (2 * Math.PI * i / nodeCount) - Math.PI / 2;
    positions.push({
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    });
  }
  return positions;
}

/**
 * Generate vertical layout positions
 */
function getVerticalPositions(nodeCount, startY = 80, spacing = 70, centerX = 250) {
  return Array.from({ length: nodeCount }, (_, i) => ({
    x: centerX,
    y: startY + i * spacing,
  }));
}

/**
 * Generate horizontal layout positions
 */
function getHorizontalPositions(nodeCount, startX = 60, spacing = 90, centerY = 200) {
  return Array.from({ length: nodeCount }, (_, i) => ({
    x: startX + i * spacing,
    y: centerY,
  }));
}

/**
 * Generate Bezier curve path between two points
 */
function getBezierPath(x1, y1, x2, y2, curvature = 0.3) {
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const ctrl1X = x1 + dx * 0.25;
  const ctrl1Y = y1 + dy * 0.25 - Math.abs(dx) * curvature;
  const ctrl2X = x2 - dx * 0.25;
  const ctrl2Y = y2 - dy * 0.25 - Math.abs(dx) * curvature;
  return `M ${x1} ${y1} C ${ctrl1X} ${ctrl1Y}, ${ctrl2X} ${ctrl2Y}, ${x2} ${y2}`;
}

// ============ MATH EXPRESSION PARSER ============
/**
 * Parse simple math expression and generate plot points
 * Supports: x^2, sin(x), cos(x), sqrt(x), abs(x), linear
 */
function parseMathExpression(expression, xMin = -5, xMax = 5, steps = 50) {
  const points = [];
  const step = (xMax - xMin) / steps;
  
  // Clean expression
  const expr = expression
    .toLowerCase()
    .replace(/\s/g, '')
    .replace(/\^/g, '**');
  
  for (let x = xMin; x <= xMax; x += step) {
    let y;
    try {
      // Safe math evaluation
      if (expr.includes('sin')) {
        y = Math.sin(x);
      } else if (expr.includes('cos')) {
        y = Math.cos(x);
      } else if (expr.includes('tan')) {
        y = Math.tan(x);
      } else if (expr.includes('sqrt')) {
        y = x >= 0 ? Math.sqrt(x) : NaN;
      } else if (expr.includes('abs')) {
        y = Math.abs(x);
      } else if (expr.includes('x**2') || expr.includes('x^2') || expr === 'x²') {
        y = x * x;
      } else if (expr.includes('x**3') || expr.includes('x^3') || expr === 'x³') {
        y = x * x * x;
      } else if (expr.includes('2x') || expr.includes('2*x')) {
        y = 2 * x;
      } else if (expr.includes('3x') || expr.includes('3*x')) {
        y = 3 * x;
      } else if (expr === 'x' || expr === 'y=x') {
        y = x;
      } else if (expr.includes('log') || expr.includes('ln')) {
        y = x > 0 ? Math.log(x) : NaN;
      } else if (expr.includes('exp') || expr.includes('e^x')) {
        y = Math.exp(x);
      } else {
        // Linear fallback
        y = x;
      }
      
      if (!isNaN(y) && isFinite(y)) {
        points.push({ x, y });
      }
    } catch (e) {
      // Skip invalid points
    }
  }
  
  return points;
}

// ============ TRAJECTORY CALCULATOR ============
/**
 * Calculate projectile trajectory points
 */
function calculateTrajectory(vx = 10, vy = 15, g = 9.8, steps = 30, scale = 8) {
  const points = [];
  const totalTime = (2 * vy) / g;
  const dt = totalTime / steps;
  
  for (let i = 0; i <= steps; i++) {
    const t = i * dt;
    const x = vx * t;
    const y = vy * t - 0.5 * g * t * t;
    if (y >= 0) {
      points.push({
        x: 80 + x * scale,
        y: 320 - y * scale,
        t,
      });
    }
  }
  
  return points;
}

// ============ INTELLIGENT STYLING ============
/**
 * Get adaptive styling based on diagram complexity
 */
function getAdaptiveStyle(nodeCount, theme, context = {}) {
  const isLongDiagram = nodeCount > 6;
  const isComplexDiagram = context.relationships?.length > 10;
  
  return {
    strokeWidth: isLongDiagram ? 2 : 3,
    nodeSize: isLongDiagram ? 35 : 45,
    fontSize: isLongDiagram ? 11 : 14,
    arrowSize: isLongDiagram ? 6 : 8,
    lineStyle: context.indirect ? 'dashed' : 'solid',
    emphasisColor: theme.accent || theme.primary,
    glowIntensity: context.important ? 0.6 : 0.3,
  };
}

// Template mapping (original V4.0 - preserved)
const TEMPLATE_MAP = {
  [TEMPLATE_TYPES.RACE]: RaceTemplate,
  [TEMPLATE_TYPES.PROCESS]: ProcessTemplate,
  [TEMPLATE_TYPES.CYCLE]: CycleTemplate,
  [TEMPLATE_TYPES.GRAPH]: GraphTemplate,
  [TEMPLATE_TYPES.STRUCTURE]: StructureTemplate,
  [TEMPLATE_TYPES.CAUSE_EFFECT]: CauseEffectTemplate,
  [TEMPLATE_TYPES.SCALE]: ScaleTemplate,
  [TEMPLATE_TYPES.TIMELINE]: TimelineTemplate,
  // Aliases for flexibility
  'race_comparison': RaceTemplate,
  'process_flow': ProcessTemplate,
  'cycle': CycleTemplate,
  'graph_relationship': GraphTemplate,
  'structure_anatomy': StructureTemplate,
  'cause_effect': CauseEffectTemplate,
  'scale_spectrum': ScaleTemplate,
  'sequence_timeline': TimelineTemplate,
};

// ============ UNIVERSAL RENDERERS (V5.0 NEW) ============

/**
 * Concept Map Renderer - Radial node layout with relationships
 */
const ConceptMapRenderer = ({ config, step, theme }) => {
  const nodes = config.nodes || [];
  const relationships = config.relationships || [];
  const centerNode = config.center_node || nodes[0];
  const title = config.title || 'Concept Map';
  
  // Calculate positions
  const outerNodes = nodes.filter(n => n.id !== centerNode?.id);
  const positions = getRadialPositions(outerNodes.length, 250, 200, 130);
  
  const styles = getAdaptiveStyle(nodes.length, theme, { relationships });
  
  // Map node IDs to positions
  const nodePositions = {};
  nodePositions[centerNode?.id || 'center'] = { x: 250, y: 200 };
  outerNodes.forEach((n, i) => {
    nodePositions[n.id] = positions[i];
  });
  
  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={35}
        fontSize={20}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        🕸️ {title}
      </motion.text>
      
      {/* Relationships (curved connectors) */}
      {step >= 1 && relationships.map((rel, i) => {
        const from = nodePositions[rel.from];
        const to = nodePositions[rel.to];
        if (!from || !to) return null;
        
        const isDashed = rel.type === 'indirect' || rel.type === 'weak';
        const path = getBezierPath(from.x, from.y, to.x, to.y, 0.2);
        
        return (
          <motion.g key={i}>
            <motion.path
              d={path}
              stroke={isDashed ? COLORS.chalkLight : theme.secondary}
              strokeWidth={styles.strokeWidth}
              strokeDasharray={isDashed ? '5,5' : 'none'}
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }}
            />
            {/* Arrow head */}
            <circle
              cx={to.x}
              cy={to.y}
              r={4}
              fill={theme.secondary}
            />
            {/* Relationship label */}
            {rel.label && (
              <text
                x={(from.x + to.x) / 2}
                y={(from.y + to.y) / 2 - 10}
                fontSize={10}
                textAnchor="middle"
                fill={COLORS.chalkLight}
              >
                {rel.label}
              </text>
            )}
          </motion.g>
        );
      })}
      
      {/* Center Node */}
      {step >= 2 && centerNode && (
        <motion.g
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', delay: 0.3 }}
        >
          <circle
            cx={250} cy={200}
            r={styles.nodeSize + 10}
            fill={theme.primary}
            opacity={0.2}
          />
          <circle
            cx={250} cy={200}
            r={styles.nodeSize}
            fill={theme.primary}
            stroke="white"
            strokeWidth={3}
          />
          <text
            x={250} y={200}
            fontSize={styles.fontSize + 2}
            fontWeight="bold"
            textAnchor="middle"
            dominantBaseline="middle"
            fill="white"
          >
            {centerNode.emoji || '🎯'} {centerNode.label}
          </text>
        </motion.g>
      )}
      
      {/* Outer Nodes */}
      {step >= 2 && outerNodes.map((node, i) => {
        const pos = positions[i];
        const isImportant = node.important || node.key;
        
        return (
          <motion.g
            key={node.id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.5 + i * 0.15 }}
          >
            <circle
              cx={pos.x} cy={pos.y}
              r={styles.nodeSize}
              fill={node.color || theme.secondary}
              stroke={isImportant ? theme.accent : 'white'}
              strokeWidth={isImportant ? 3 : 2}
            />
            <text
              x={pos.x} y={pos.y - 5}
              fontSize={styles.fontSize}
              fontWeight="bold"
              textAnchor="middle"
              fill="white"
            >
              {node.emoji || '📌'}
            </text>
            <text
              x={pos.x} y={pos.y + 12}
              fontSize={styles.fontSize - 2}
              textAnchor="middle"
              fill="white"
            >
              {node.label}
            </text>
          </motion.g>
        );
      })}
      
      {/* Memory Hook */}
      {step >= 4 && config.memory_hook && (
        <motion.g
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          <rect x={80} y={365} width={340} height={38} rx={19} fill="#FEF3C7" stroke={theme.primary} strokeWidth={2} />
          <text x={250} y={390} fontSize={13} textAnchor="middle" fill={theme.primary} fontWeight="bold">
            💡 {config.memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

/**
 * Math Plot Renderer - Function graphs with expression parsing
 */
const MathPlotRenderer = ({ config, step, theme }) => {
  const expression = config.expression || config.function || 'x^2';
  const title = config.title || `Graph: ${expression}`;
  const xRange = config.x_range || { min: -5, max: 5 };
  const yRange = config.y_range || { min: -5, max: 5 };
  const highlightRange = config.highlight_range;
  
  // Parse expression and generate points
  const points = useMemo(() => 
    parseMathExpression(expression, xRange.min, xRange.max, 60),
    [expression, xRange]
  );
  
  // Scale functions
  const padding = { top: 60, right: 50, bottom: 60, left: 60 };
  const WIDTH = 500;
  const HEIGHT = 400;
  const plotWidth = WIDTH - padding.left - padding.right;
  const plotHeight = HEIGHT - padding.top - padding.bottom;
  
  const scaleX = (x) => padding.left + ((x - xRange.min) / (xRange.max - xRange.min)) * plotWidth;
  const scaleY = (y) => {
    const yMin = config.y_range?.min ?? Math.min(...points.map(p => p.y), -5);
    const yMax = config.y_range?.max ?? Math.max(...points.map(p => p.y), 5);
    return padding.top + plotHeight - ((y - yMin) / (yMax - yMin)) * plotHeight;
  };
  
  // Generate path
  const pathData = useMemo(() => {
    if (points.length < 2) return '';
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.y)}`).join(' ');
  }, [points]);
  
  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={30}
        fontSize={20}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        📈 {title}
      </motion.text>
      
      {/* Grid */}
      {step >= 1 && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 0.2 }}>
          {Array.from({ length: 11 }).map((_, i) => (
            <g key={i}>
              <line
                x1={padding.left}
                y1={padding.top + (i / 10) * plotHeight}
                x2={padding.left + plotWidth}
                y2={padding.top + (i / 10) * plotHeight}
                stroke="#9CA3AF"
              />
              <line
                x1={padding.left + (i / 10) * plotWidth}
                y1={padding.top}
                x2={padding.left + (i / 10) * plotWidth}
                y2={padding.top + plotHeight}
                stroke="#9CA3AF"
              />
            </g>
          ))}
        </motion.g>
      )}
      
      {/* Axes */}
      <line x1={padding.left} y1={scaleY(0)} x2={padding.left + plotWidth} y2={scaleY(0)} stroke="#374151" strokeWidth={2} />
      <line x1={scaleX(0)} y1={padding.top} x2={scaleX(0)} y2={padding.top + plotHeight} stroke="#374151" strokeWidth={2} />
      
      {/* Axis labels */}
      <text x={padding.left + plotWidth + 15} y={scaleY(0) + 5} fontSize={14} fill="#374151" fontWeight="bold">x</text>
      <text x={scaleX(0) - 5} y={padding.top - 10} fontSize={14} fill="#374151" fontWeight="bold">y</text>
      
      {/* Highlight range */}
      {step >= 2 && highlightRange && (
        <motion.rect
          x={scaleX(highlightRange.start)}
          y={padding.top}
          width={scaleX(highlightRange.end) - scaleX(highlightRange.start)}
          height={plotHeight}
          fill={theme.accent}
          opacity={0.2}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.2 }}
        />
      )}
      
      {/* Function curve */}
      {step >= 2 && pathData && (
        <motion.path
          d={pathData}
          stroke={theme.primary}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeOut' }}
        />
      )}
      
      {/* Expression label */}
      {step >= 3 && (
        <motion.g
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          <rect
            x={padding.left + plotWidth - 110}
            y={padding.top + 10}
            width={100}
            height={35}
            rx={8}
            fill="#FEF3C7"
            stroke={theme.primary}
            strokeWidth={2}
          />
          <text
            x={padding.left + plotWidth - 60}
            y={padding.top + 33}
            fontSize={15}
            fontWeight="bold"
            textAnchor="middle"
            fill={theme.primary}
            fontFamily="'Caveat', cursive"
          >
            y = {expression}
          </text>
        </motion.g>
      )}
      
      {/* Memory Hook */}
      {step >= 4 && config.memory_hook && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 2 }}>
          <rect x={80} y={365} width={340} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={390} fontSize={13} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {config.memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

/**
 * Trajectory Renderer - Physics projectile motion
 */
const TrajectoryRenderer = ({ config, step, theme }) => {
  const vx = config.vx || 15;
  const vy = config.vy || 20;
  const g = config.gravity || 9.8;
  const title = config.title || 'Projectile Motion';
  
  // Calculate trajectory
  const points = useMemo(() => calculateTrajectory(vx, vy, g, 40, 6), [vx, vy, g]);
  
  // Path data
  const pathData = points.length > 1 
    ? points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
    : '';
  
  // Ghost trail points (last N)
  const ghostPoints = points.slice(-10);
  
  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={30}
        fontSize={20}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        🚀 {title}
      </motion.text>
      
      {/* Ground */}
      <line x1={50} y1={320} x2={450} y2={320} stroke="#8B7355" strokeWidth={3} />
      <rect x={50} y={320} width={400} height={30} fill="#D4C4A8" opacity={0.5} />
      
      {/* Velocity vectors at launch point */}
      {step >= 1 && (
        <motion.g
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {/* Horizontal velocity */}
          <line x1={80} y1={320} x2={80 + vx * 3} y2={320} stroke={COLORS.blue} strokeWidth={3} />
          <polygon
            points={`${80 + vx * 3 + 8},320 ${80 + vx * 3},316 ${80 + vx * 3},324`}
            fill={COLORS.blue}
          />
          <text x={80 + vx * 1.5} y={340} fontSize={12} fill={COLORS.blue} textAnchor="middle" fontWeight="bold">
            vₓ = {vx} m/s
          </text>
          
          {/* Vertical velocity */}
          <line x1={80} y1={320} x2={80} y2={320 - vy * 3} stroke={COLORS.green} strokeWidth={3} />
          <polygon
            points={`80,${320 - vy * 3 - 8} 76,${320 - vy * 3} 84,${320 - vy * 3}`}
            fill={COLORS.green}
          />
          <text x={55} y={320 - vy * 1.5} fontSize={12} fill={COLORS.green} textAnchor="middle" fontWeight="bold">
            vᵧ = {vy} m/s
          </text>
        </motion.g>
      )}
      
      {/* Ghost trail */}
      {step >= 2 && ghostPoints.map((p, i) => (
        <motion.circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={3}
          fill={theme.primary}
          opacity={0.2 + (i / ghostPoints.length) * 0.3}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1 + i * 0.05 }}
        />
      ))}
      
      {/* Trajectory arc */}
      {step >= 2 && pathData && (
        <motion.path
          d={pathData}
          stroke={theme.primary}
          strokeWidth={3}
          strokeDasharray="8,4"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2 }}
        />
      )}
      
      {/* Projectile */}
      {step >= 3 && points.length > 0 && (
        <motion.circle
          cx={points[Math.floor(points.length * (step / 5))].x}
          cy={points[Math.floor(points.length * (step / 5))].y}
          r={10}
          fill={theme.primary}
          stroke="white"
          strokeWidth={2}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
        />
      )}
      
      {/* Max height marker */}
      {step >= 3 && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }}>
          <line
            x1={80 + vx * vy / g * 6}
            y1={320 - (vy * vy / (2 * g)) * 6}
            x2={80 + vx * vy / g * 6}
            y2={320}
            stroke={COLORS.amber}
            strokeWidth={2}
            strokeDasharray="4,4"
          />
          <text
            x={80 + vx * vy / g * 6 + 10}
            y={320 - (vy * vy / (2 * g)) * 3}
            fontSize={11}
            fill={COLORS.amber}
            fontWeight="bold"
          >
            H_max = {(vy * vy / (2 * g)).toFixed(1)} m
          </text>
        </motion.g>
      )}
      
      {/* Formulas */}
      {step >= 4 && (
        <motion.g initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 2 }}>
          <rect x={300} y={60} width={180} height={70} rx={10} fill="#FEF3C7" stroke={theme.primary} strokeWidth={2} />
          <text x={390} y={85} fontSize={12} textAnchor="middle" fill={theme.primary} fontWeight="bold">
            H = v²ᵧ / 2g
          </text>
          <text x={390} y={105} fontSize={12} textAnchor="middle" fill={theme.primary} fontWeight="bold">
            R = vₓ × T
          </text>
          <text x={390} y={125} fontSize={12} textAnchor="middle" fill={theme.primary} fontWeight="bold">
            T = 2vᵧ / g
          </text>
        </motion.g>
      )}
    </g>
  );
};

/**
 * Balance Scale Renderer - Comparison visualizations
 */
const BalanceScaleRenderer = ({ config, step, theme }) => {
  const leftItems = config.left_items || [];
  const rightItems = config.right_items || [];
  const title = config.title || 'Comparison';
  const leftLabel = config.left_label || 'Left';
  const rightLabel = config.right_label || 'Right';
  
  // Calculate balance (for animation)
  const leftWeight = leftItems.reduce((sum, item) => sum + (item.weight || 1), 0);
  const rightWeight = rightItems.reduce((sum, item) => sum + (item.weight || 1), 0);
  const tilt = Math.min(15, Math.max(-15, (rightWeight - leftWeight) * 3));
  
  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={35}
        fontSize={20}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        ⚖️ {title}
      </motion.text>
      
      {/* Fulcrum/Base */}
      <polygon points="250,350 220,400 280,400" fill="#8B7355" />
      
      {/* Balance beam */}
      {step >= 1 && (
        <motion.g
          initial={{ rotate: 0 }}
          animate={{ rotate: tilt }}
          style={{ transformOrigin: '250px 350px' }}
          transition={{ delay: 1, duration: 1, type: 'spring' }}
        >
          <rect x={50} y={340} width={400} height={20} rx={5} fill={theme.primary} />
          
          {/* Left pan */}
          <rect x={60} y={280} width={120} height={60} rx={10} fill="#F3F4F6" stroke={theme.secondary} strokeWidth={2} />
          <text x={120} y={265} fontSize={14} fontWeight="bold" textAnchor="middle" fill={theme.secondary}>
            {leftLabel}
          </text>
          
          {/* Left items */}
          {leftItems.map((item, i) => (
            <motion.g
              key={i}
              initial={{ y: -30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1.5 + i * 0.2 }}
            >
              <circle
                cx={80 + i * 35}
                cy={310}
                r={15}
                fill={item.color || theme.secondary}
              />
              <text x={80 + i * 35} y={315} fontSize={16} textAnchor="middle" fill="white">
                {item.emoji || '⚪'}
              </text>
            </motion.g>
          ))}
          
          {/* Right pan */}
          <rect x={320} y={280} width={120} height={60} rx={10} fill="#F3F4F6" stroke={theme.accent} strokeWidth={2} />
          <text x={380} y={265} fontSize={14} fontWeight="bold" textAnchor="middle" fill={theme.accent}>
            {rightLabel}
          </text>
          
          {/* Right items */}
          {rightItems.map((item, i) => (
            <motion.g
              key={i}
              initial={{ y: -30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1.5 + i * 0.2 }}
            >
              <circle
                cx={340 + i * 35}
                cy={310}
                r={15}
                fill={item.color || theme.accent}
              />
              <text x={340 + i * 35} y={315} fontSize={16} textAnchor="middle" fill="white">
                {item.emoji || '⚪'}
              </text>
            </motion.g>
          ))}
        </motion.g>
      )}
      
      {/* Comparison result */}
      {step >= 3 && (
        <motion.g
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.5 }}
        >
          <rect x={150} y={80} width={200} height={40} rx={20} fill={theme.primary} />
          <text x={250} y={106} fontSize={14} fontWeight="bold" textAnchor="middle" fill="white">
            {leftWeight === rightWeight ? '⚖️ Balanced!' : 
             leftWeight > rightWeight ? `⬅️ ${leftLabel} is heavier` : `${rightLabel} is heavier ➡️`}
          </text>
        </motion.g>
      )}
      
      {/* Memory Hook */}
      {step >= 4 && config.memory_hook && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 3 }}>
          <rect x={80} y={145} width={340} height={38} rx={19} fill="#FEF3C7" stroke={theme.primary} strokeWidth={2} />
          <text x={250} y={170} fontSize={13} textAnchor="middle" fill={theme.primary} fontWeight="bold">
            💡 {config.memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

// Fallback configs for common concepts
const FALLBACK_CONFIGS = {
  velocity: {
    template: 'race_comparison',
    subject: 'physics',
    title: 'Velocity Race',
    title_hindi: 'वेग दौड़',
    config: {
      object_a: { type: 'auto_rickshaw', label: 'FAST', color: '#FF9933', speed: 20 },
      object_b: { type: 'auto_rickshaw', label: 'SLOW', color: '#3B82F6', speed: 10 },
      track_length: 100,
      formula: 'v = d / t',
      memory_hook: 'More distance in same time = More velocity! 🚀',
    },
  },
  force: {
    template: 'race_comparison',
    subject: 'physics',
    title: 'Force & Acceleration',
    title_hindi: 'बल और त्वरण',
    config: {
      object_a: { type: 'ball', label: 'LIGHT (1kg)', color: '#10B981', speed: 20 },
      object_b: { type: 'ball', label: 'HEAVY (5kg)', color: '#EF4444', speed: 5 },
      track_length: 100,
      formula: 'F = ma',
      memory_hook: 'Same force, less mass = More acceleration! 🏏',
    },
  },
  photosynthesis: {
    template: 'process_flow',
    subject: 'biology',
    title: 'Photosynthesis',
    title_hindi: 'प्रकाश संश्लेषण',
    config: {
      inputs: [
        { name: 'Sunlight', emoji: '☀️', color: '#FCD34D' },
        { name: 'Water', emoji: '💧', color: '#3B82F6' },
        { name: 'CO₂', emoji: '💨', color: '#6B7280' },
      ],
      process: { name: 'Chloroplast', emoji: '🌿', color: '#22C55E' },
      outputs: [
        { name: 'Glucose', emoji: '🍬', color: '#F59E0B' },
        { name: 'Oxygen', emoji: '💨', color: '#06B6D4' },
      ],
      formula: '6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂',
      memory_hook: 'Plants are food factories! ☀️ + 💧 + 💨 = 🍬 + O₂',
    },
  },
  cell: {
    template: 'structure_anatomy',
    subject: 'biology',
    title: 'Cell Structure',
    title_hindi: 'कोशिका संरचना',
    config: {
      components: [
        { name: 'Nucleus', x: 0, y: 0, size: 40, color: '#8B5CF6', emoji: '🟣', description: 'Control center' },
        { name: 'Mitochondria', x: -60, y: -30, size: 22, color: '#EF4444', emoji: '🔴', description: 'Powerhouse' },
        { name: 'Ribosome', x: 50, y: 40, size: 15, color: '#3B82F6', emoji: '🔵', description: 'Protein maker' },
        { name: 'ER', x: 40, y: -40, size: 25, color: '#10B981', emoji: '🟢', description: 'Transport' },
      ],
      memory_hook: 'Each part has a special job! 🏭',
    },
  },
  ph_scale: {
    template: 'scale_spectrum',
    subject: 'chemistry',
    title: 'pH Scale',
    title_hindi: 'pH स्केल',
    config: {
      min: 0,
      max: 14,
      current_value: 7,
      markers: [
        { value: 0, label: 'Strong Acid', emoji: '🍋', color: '#EF4444' },
        { value: 7, label: 'Neutral', emoji: '💧', color: '#10B981' },
        { value: 14, label: 'Strong Base', emoji: '🧼', color: '#3B82F6' },
      ],
      memory_hook: 'pH 7 is neutral, below = acid, above = base! 📏',
    },
  },
  water_cycle: {
    template: 'cycle',
    subject: 'biology',
    title: 'Water Cycle',
    title_hindi: 'जल चक्र',
    config: {
      steps: [
        { name: 'Evaporation', emoji: '☀️', color: '#F59E0B', description: 'Water → Vapor' },
        { name: 'Condensation', emoji: '☁️', color: '#6B7280', description: 'Vapor → Clouds' },
        { name: 'Precipitation', emoji: '🌧️', color: '#3B82F6', description: 'Rain/Snow' },
        { name: 'Collection', emoji: '🌊', color: '#06B6D4', description: 'Rivers/Oceans' },
      ],
      center_label: 'WATER',
      memory_hook: 'Round and round the water goes! 💧',
    },
  },
  
  // ============ V5.0 NEW MODE FALLBACKS ============
  
  // Concept Map Examples
  newtons_laws: {
    mode: 'concept_map',
    subject: 'physics',
    title: "Newton's Laws of Motion",
    title_hindi: 'न्यूटन के गति के नियम',
    config: {
      center_node: { id: 'main', label: "Newton's Laws", emoji: '🍎' },
      nodes: [
        { id: 'main', label: "Newton's Laws", emoji: '🍎' },
        { id: 'first', label: 'Inertia', emoji: '🛑', color: '#EF4444' },
        { id: 'second', label: 'F = ma', emoji: '💪', color: '#3B82F6' },
        { id: 'third', label: 'Action-Reaction', emoji: '🔄', color: '#10B981' },
        { id: 'app1', label: 'Seatbelts', emoji: '🚗', color: '#F59E0B' },
        { id: 'app2', label: 'Rockets', emoji: '🚀', color: '#8B5CF6' },
      ],
      relationships: [
        { from: 'main', to: 'first', label: '1st Law' },
        { from: 'main', to: 'second', label: '2nd Law' },
        { from: 'main', to: 'third', label: '3rd Law' },
        { from: 'first', to: 'app1', type: 'indirect' },
        { from: 'third', to: 'app2', type: 'indirect' },
      ],
      memory_hook: 'Newton saw an apple fall and changed physics forever! 🍎',
    },
  },
  
  periodic_table_groups: {
    mode: 'concept_map',
    subject: 'chemistry',
    title: 'Periodic Table Groups',
    title_hindi: 'आवर्त सारणी समूह',
    config: {
      center_node: { id: 'main', label: 'Periodic Table', emoji: '⚗️' },
      nodes: [
        { id: 'main', label: 'Periodic Table', emoji: '⚗️' },
        { id: 'alkali', label: 'Alkali Metals', emoji: 'Na', color: '#EF4444', important: true },
        { id: 'halogen', label: 'Halogens', emoji: 'Cl', color: '#10B981', important: true },
        { id: 'noble', label: 'Noble Gases', emoji: 'He', color: '#3B82F6' },
        { id: 'transition', label: 'Transition', emoji: 'Fe', color: '#F59E0B' },
      ],
      relationships: [
        { from: 'main', to: 'alkali', label: 'Group 1' },
        { from: 'main', to: 'halogen', label: 'Group 17' },
        { from: 'main', to: 'noble', label: 'Group 18' },
        { from: 'main', to: 'transition', label: 'D-Block' },
        { from: 'alkali', to: 'halogen', label: 'React!', type: 'weak' },
      ],
      memory_hook: 'Groups have similar properties - like family members! 👨‍👩‍👧‍👦',
    },
  },
  
  // Math Plot Examples
  quadratic: {
    mode: 'math_plot',
    subject: 'mathematics',
    title: 'Quadratic Function',
    title_hindi: 'द्विघात फलन',
    config: {
      expression: 'x^2',
      x_range: { min: -4, max: 4 },
      y_range: { min: -2, max: 16 },
      memory_hook: 'x² makes a beautiful parabola - like a fountain! ⛲',
    },
  },
  
  sine_wave: {
    mode: 'math_plot',
    subject: 'physics',
    title: 'Sine Wave',
    title_hindi: 'साइन तरंग',
    config: {
      expression: 'sin(x)',
      x_range: { min: -6.28, max: 6.28 },
      y_range: { min: -1.5, max: 1.5 },
      memory_hook: 'Sine waves are everywhere - sound, light, AC current! 🌊',
    },
  },
  
  // Trajectory Examples
  projectile_motion: {
    mode: 'trajectory',
    subject: 'physics',
    title: 'Projectile Motion',
    title_hindi: 'प्रक्षेप्य गति',
    config: {
      vx: 15,
      vy: 20,
      gravity: 9.8,
      memory_hook: 'Cricket ball, Diwali rocket - same physics! 🏏🚀',
    },
  },
  
  rocket_launch: {
    mode: 'trajectory',
    subject: 'physics',
    title: 'Rocket Launch Trajectory',
    title_hindi: 'रॉकेट प्रक्षेपण',
    config: {
      vx: 20,
      vy: 30,
      gravity: 9.8,
      memory_hook: 'ISRO rockets follow these same equations! 🇮🇳🚀',
    },
  },
  
  // Balance Scale Examples
  chemical_equation_balance: {
    mode: 'balance_scale',
    subject: 'chemistry',
    title: 'Balancing Chemical Equations',
    title_hindi: 'रासायनिक समीकरण संतुलन',
    config: {
      left_label: 'Reactants',
      right_label: 'Products',
      left_items: [
        { emoji: '💧', label: 'H₂O', weight: 2 },
        { emoji: '⚡', label: 'Energy', weight: 1, color: '#F59E0B' },
      ],
      right_items: [
        { emoji: '💨', label: 'H₂', weight: 1 },
        { emoji: '💨', label: 'O₂', weight: 1 },
      ],
      memory_hook: 'Atoms are conserved - nothing is created or destroyed! ⚖️',
    },
  },
  
  redox_balance: {
    mode: 'balance_scale',
    subject: 'chemistry',
    title: 'Oxidation vs Reduction',
    title_hindi: 'ऑक्सीकरण बनाम अवकरण',
    config: {
      left_label: 'Oxidation (OIL)',
      right_label: 'Reduction (RIG)',
      left_items: [
        { emoji: '➖', label: 'Loses e⁻', weight: 1, color: '#EF4444' },
        { emoji: '⬆️', label: '+Ox. State', weight: 1, color: '#EF4444' },
      ],
      right_items: [
        { emoji: '➕', label: 'Gains e⁻', weight: 1, color: '#10B981' },
        { emoji: '⬇️', label: '-Ox. State', weight: 1, color: '#10B981' },
      ],
      memory_hook: 'OIL RIG: Oxidation Is Loss, Reduction Is Gain! 🛢️',
    },
  },
};

const ConfigDrivenSketch = ({
  blueprint = null, // Full blueprint from backend
  concept = 'velocity', // Fallback concept name
  subject = 'physics',
  question = '',
  onComplete,
  // V5.0 NEW: Professor output integration
  professorOutput = null,
  renderDirectives = null,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const totalSteps = 5;

  // V5.0: Merge blueprint with professor output
  const effectiveBlueprint = useMemo(() => {
    if (professorOutput && professorOutput.visual_config) {
      return {
        ...blueprint,
        ...professorOutput.visual_config,
        render_directives: renderDirectives || professorOutput.render_directives,
      };
    }
    return blueprint;
  }, [blueprint, professorOutput, renderDirectives]);

  // V5.0: Detect rendering mode
  const renderMode = useMemo(() => {
    return detectModeFromArtifact(effectiveBlueprint);
  }, [effectiveBlueprint]);

  // Determine configuration
  const getConfig = useCallback(() => {
    // Priority 1: Use blueprint from backend (with professor output merged)
    if (effectiveBlueprint && (effectiveBlueprint.template || effectiveBlueprint.mode)) {
      return effectiveBlueprint;
    }
    
    // Priority 2: Use fallback config for known concepts
    const conceptKey = concept?.toLowerCase().replace(/\s+/g, '_');
    if (FALLBACK_CONFIGS[conceptKey]) {
      return FALLBACK_CONFIGS[conceptKey];
    }
    
    // Priority 3: Default velocity race
    return FALLBACK_CONFIGS.velocity;
  }, [effectiveBlueprint, concept]);

  const config = getConfig();
  const templateType = config.template || 'race_comparison';
  const TemplateComponent = TEMPLATE_MAP[templateType] || RaceTemplate;
  const theme = SUBJECT_THEMES[config.subject || subject] || SUBJECT_THEMES.physics;

  // Auto-advance steps
  useEffect(() => {
    if (!isPlaying || currentStep >= totalSteps) return;
    
    const durations = [1500, 2500, 3000, 2500, 2000];
    const timer = setTimeout(() => {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }, durations[currentStep] || 2000);
    
    return () => clearTimeout(timer);
  }, [currentStep, isPlaying, totalSteps]);

  // Handle replay
  const handleReplay = useCallback(() => {
    setCurrentStep(0);
    setIsPlaying(true);
  }, []);

  // Get title with Hindi
  const title = config.title || concept;
  const titleHindi = config.title_hindi || '';

  return (
    <div className="config-driven-sketch rounded-2xl overflow-hidden shadow-2xl border-2" style={{ borderColor: theme.primary }}>
      {/* Header */}
      <div 
        className="px-5 py-3 flex items-center justify-between"
        style={{ background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` }}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🎬</span>
          <div>
            <span className="font-bold text-white text-lg">Watch & Learn</span>
            {titleHindi && (
              <span className="ml-2 text-white/80 text-sm">({titleHindi})</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-white/30 backdrop-blur-sm px-4 py-1.5 rounded-full text-white text-sm font-bold capitalize">
            {config.subject || subject}
          </span>
          <button
            onClick={handleReplay}
            className="p-2 bg-white/30 rounded-full hover:bg-white/50 transition-all"
            title="Replay"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Main Canvas */}
      <svg
        viewBox="0 0 500 420"
        className="w-full"
        style={{ 
          minHeight: '420px',
          background: `linear-gradient(180deg, ${theme.background || COLORS.paper} 0%, #FEF3C7 100%)`
        }}
      >
        {/* Background grid */}
        <defs>
          <pattern id="sketchPaper" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke={COLORS.paperLines} strokeWidth="0.5" opacity="0.5"/>
          </pattern>
          {/* Glow filter for emphasis */}
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <rect width="500" height="420" fill="url(#sketchPaper)"/>
        
        {/* V5.0: Mode-based rendering */}
        {renderMode === RENDER_MODES.CONCEPT_MAP ? (
          <ConceptMapRenderer 
            config={config.config || config} 
            step={currentStep}
            theme={theme}
          />
        ) : renderMode === RENDER_MODES.MATH_PLOT ? (
          <MathPlotRenderer 
            config={config.config || config} 
            step={currentStep}
            theme={theme}
          />
        ) : renderMode === RENDER_MODES.TRAJECTORY ? (
          <TrajectoryRenderer 
            config={config.config || config} 
            step={currentStep}
            theme={theme}
          />
        ) : renderMode === RENDER_MODES.BALANCE_SCALE ? (
          <BalanceScaleRenderer 
            config={config.config || config} 
            step={currentStep}
            theme={theme}
          />
        ) : (
          /* Classic template-based rendering (default) */
          <TemplateComponent 
            config={config.config || {}} 
            step={currentStep}
            subject={config.subject || subject}
          />
        )}
      </svg>

      {/* Footer */}
      <div 
        className="px-5 py-2.5 flex items-center justify-between border-t"
        style={{ 
          background: `linear-gradient(90deg, ${theme.background}, white)`,
          borderColor: theme.primary + '40'
        }}
      >
        <div className="flex items-center gap-3">
          {currentStep >= totalSteps ? (
            <motion.div 
              initial={{ scale: 0 }} 
              animate={{ scale: 1 }} 
              className="flex items-center gap-2"
              style={{ color: theme.primary }}
            >
              <span className="text-lg">✅</span>
              <span className="font-medium text-sm">Complete!</span>
            </motion.div>
          ) : (
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: theme.primary }} />
              <span className="text-sm" style={{ color: theme.primary }}>Playing...</span>
            </div>
          )}
          
          {/* V5.0: Mode indicator badge */}
          <span 
            className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600"
            title={`Rendering mode: ${renderMode}`}
          >
            {renderMode === RENDER_MODES.CLASSIC ? '📋' : 
             renderMode === RENDER_MODES.CONCEPT_MAP ? '🕸️' :
             renderMode === RENDER_MODES.MATH_PLOT ? '📈' :
             renderMode === RENDER_MODES.TRAJECTORY ? '🚀' :
             renderMode === RENDER_MODES.BALANCE_SCALE ? '⚖️' :
             renderMode === RENDER_MODES.TIMELINE ? '📅' :
             renderMode === RENDER_MODES.STRUCTURE ? '🔬' : '✨'}
            {' '}{renderMode.replace('_', ' ')}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Step indicator */}
          <div className="flex items-center gap-1">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i}
                className="w-1.5 h-1.5 rounded-full transition-all"
                style={{
                  backgroundColor: i <= currentStep ? theme.primary : '#D1D5DB',
                  transform: i === currentStep ? 'scale(1.3)' : 'scale(1)',
                }}
              />
            ))}
          </div>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleReplay}
            className="px-4 py-1.5 text-white text-sm font-medium rounded-full transition-all flex items-center gap-1.5 shadow-md"
            style={{ backgroundColor: theme.primary }}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Replay
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default ConfigDrivenSketch;

