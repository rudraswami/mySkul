/**
 * 📊 GRAPH MODE
 * ==============
 * 
 * Mathematical plots and function graphs
 * Best for: Functions, data plots, relationships
 * 
 * Examples:
 * - y = x²
 * - Linear functions
 * - Trigonometric functions
 * - Data visualization
 */

import React from 'react';
import {
  SketchLine,
  SketchLabel,
  SketchPath,
  SketchCircle,
} from '../sketch/SketchPrimitives';

export const GraphMode = ({ blueprint, animationState = {} }) => {
  const {
    xAxis = { min: -10, max: 10 },
    yAxis = { min: -10, max: 10 },
    functions = [],
    points = [],
    labels = [],
  } = blueprint;
  
  // Graph dimensions
  const graphWidth = 300;
  const graphHeight = 240;
  const originX = 50;
  const originY = 270;
  
  // Scaling
  const xScale = graphWidth / (xAxis.max - xAxis.min);
  const yScale = graphHeight / (yAxis.max - yAxis.min);
  
  // Convert graph coordinates to SVG coordinates
  const toSvgX = (x) => originX + (x - xAxis.min) * xScale;
  const toSvgY = (y) => originY - (y - yAxis.min) * yScale;
  
  return (
    <g id="graph-mode">
      {/* Axes */}
      <Axes
        originX={originX}
        originY={originY}
        width={graphWidth}
        height={graphHeight}
        xAxis={xAxis}
        yAxis={yAxis}
        toSvgX={toSvgX}
        toSvgY={toSvgY}
      />
      
      {/* Grid (optional) */}
      <Grid
        originX={originX}
        originY={originY}
        width={graphWidth}
        height={graphHeight}
        xScale={xScale}
        yScale={yScale}
      />
      
      {/* Function plots */}
      {functions.map((func, i) => (
        <FunctionPlot
          key={`func-${i}`}
          func={func}
          xAxis={xAxis}
          toSvgX={toSvgX}
          toSvgY={toSvgY}
          delay={0.5 + i * 0.3}
        />
      ))}
      
      {/* Points */}
      {points.map((point, i) => (
        <SketchCircle
          key={`point-${i}`}
          cx={toSvgX(point.x)}
          cy={toSvgY(point.y)}
          radius={4}
          fill={point.color || '#EF4444'}
          label={point.label}
          delay={1 + i * 0.2}
        />
      ))}
      
      {/* Labels */}
      {labels.map((label, i) => (
        <SketchLabel
          key={`label-${i}`}
          x={label.x}
          y={label.y}
          text={label.text}
          fontSize={label.fontSize}
          delay={i * 0.2}
        />
      ))}
    </g>
  );
};

// Helper: Axes
const Axes = ({ originX, originY, width, height, xAxis, yAxis, toSvgX, toSvgY }) => {
  return (
    <g id="axes">
      {/* X-axis */}
      <SketchLine
        x1={originX}
        y1={originY}
        x2={originX + width}
        y2={originY}
        strokeWidth={2}
        delay={0}
      />
      
      {/* Y-axis */}
      <SketchLine
        x1={originX}
        y1={originY}
        x2={originX}
        y2={originY - height}
        strokeWidth={2}
        delay={0.1}
      />
      
      {/* X-axis arrow */}
      <polygon
        points={`${originX + width},${originY} ${originX + width - 8},${originY - 4} ${originX + width - 8},${originY + 4}`}
        fill="#333"
      />
      
      {/* Y-axis arrow */}
      <polygon
        points={`${originX},${originY - height} ${originX - 4},${originY - height + 8} ${originX + 4},${originY - height + 8}`}
        fill="#333"
      />
      
      {/* Axis labels */}
      <text x={originX + width + 10} y={originY + 5} fontSize="14" fill="#666">x</text>
      <text x={originX - 10} y={originY - height - 10} fontSize="14" fill="#666">y</text>
      
      {/* Origin label */}
      <text x={originX - 15} y={originY + 15} fontSize="12" fill="#999">0</text>
    </g>
  );
};

// Helper: Grid
const Grid = ({ originX, originY, width, height, xScale, yScale }) => {
  const gridLines = [];
  
  // Vertical grid lines
  for (let i = 1; i <= 10; i++) {
    const x = originX + (width / 10) * i;
    gridLines.push(
      <line
        key={`v-${i}`}
        x1={x}
        y1={originY}
        x2={x}
        y2={originY - height}
        stroke="#E0E0E0"
        strokeWidth="1"
        strokeDasharray="2,2"
      />
    );
  }
  
  // Horizontal grid lines
  for (let i = 1; i <= 10; i++) {
    const y = originY - (height / 10) * i;
    gridLines.push(
      <line
        key={`h-${i}`}
        x1={originX}
        y1={y}
        x2={originX + width}
        y2={y}
        stroke="#E0E0E0"
        strokeWidth="1"
        strokeDasharray="2,2"
      />
    );
  }
  
  return <g id="grid" opacity="0.5">{gridLines}</g>;
};

// Helper: Function plot
const FunctionPlot = ({ func, xAxis, toSvgX, toSvgY, delay }) => {
  // Generate points
  const points = [];
  const steps = 100;
  const step = (xAxis.max - xAxis.min) / steps;
  
  for (let i = 0; i <= steps; i++) {
    const x = xAxis.min + i * step;
    let y;
    
    // Evaluate function
    try {
      if (typeof func.fn === 'function') {
        y = func.fn(x);
      } else {
        // Simple expression evaluation (for demo)
        y = eval(func.expression.replace(/x/g, x));
      }
      
      if (isFinite(y)) {
        points.push({ x, y });
      }
    } catch (e) {
      // Skip invalid points
    }
  }
  
  // Create path
  if (points.length === 0) return null;
  
  const pathData = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${toSvgX(p.x)} ${toSvgY(p.y)}`)
    .join(' ');
  
  return (
    <g>
      <SketchPath
        d={pathData}
        stroke={func.color || '#3B82F6'}
        strokeWidth={2.5}
        fill="none"
        delay={delay}
      />
      {func.label && (
        <text
          x={toSvgX(xAxis.max) - 50}
          y={toSvgY(func.fn ? func.fn(xAxis.max) : 0) - 10}
          fontSize="14"
          fill={func.color || '#3B82F6'}
        >
          {func.label}
        </text>
      )}
    </g>
  );
};

export default GraphMode;

