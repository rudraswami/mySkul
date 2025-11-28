/**
 * LiveGraph.jsx
 * Phase 4.2: Real-time graph visualization
 * 
 * Features:
 * - Multiple graph types (line, bar, area, scatter)
 * - Real-time value updates
 * - Animated transitions
 * - Interactive tooltips
 * - Axis labels and grid
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Graph type configurations
const GRAPH_TYPES = {
  line: { name: 'Line', icon: '📈' },
  area: { name: 'Area', icon: '📊' },
  bar: { name: 'Bar', icon: '📉' },
  scatter: { name: 'Scatter', icon: '⚬' },
};

const LiveGraph = ({
  data = [],
  type = 'line',
  width = 300,
  height = 180,
  xLabel = 'X',
  yLabel = 'Y',
  xUnit = '',
  yUnit = '',
  color = '#2196F3',
  secondaryColor = '#4CAF50',
  showGrid = true,
  showTooltip = true,
  showLegend = false,
  animated = true,
  highlightPoint = null,
  onPointClick,
  title,
  formula,
}) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [graphType, setGraphType] = useState(type);
  const svgRef = useRef(null);

  // Calculate bounds
  const bounds = useMemo(() => {
    if (data.length === 0) return { minX: 0, maxX: 10, minY: 0, maxY: 10 };
    
    const xValues = data.map(d => d.x);
    const yValues = data.map(d => d.y);
    
    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);
    const minY = Math.min(0, Math.min(...yValues));
    const maxY = Math.max(...yValues) * 1.1; // Add 10% padding
    
    return { minX, maxX, minY, maxY };
  }, [data]);

  // Padding for axes
  const padding = { top: 20, right: 20, bottom: 35, left: 45 };
  const graphWidth = width - padding.left - padding.right;
  const graphHeight = height - padding.top - padding.bottom;

  // Scale functions
  const scaleX = useCallback((x) => {
    const range = bounds.maxX - bounds.minX || 1;
    return padding.left + ((x - bounds.minX) / range) * graphWidth;
  }, [bounds, graphWidth, padding.left]);

  const scaleY = useCallback((y) => {
    const range = bounds.maxY - bounds.minY || 1;
    return padding.top + graphHeight - ((y - bounds.minY) / range) * graphHeight;
  }, [bounds, graphHeight, padding.top]);

  // Generate path for line/area graph
  const linePath = useMemo(() => {
    if (data.length === 0) return '';
    
    return data.map((point, i) => {
      const x = scaleX(point.x);
      const y = scaleY(point.y);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
  }, [data, scaleX, scaleY]);

  // Generate area path
  const areaPath = useMemo(() => {
    if (data.length === 0) return '';
    
    const baseline = scaleY(bounds.minY);
    const firstX = scaleX(data[0].x);
    const lastX = scaleX(data[data.length - 1].x);
    
    return `${linePath} L ${lastX} ${baseline} L ${firstX} ${baseline} Z`;
  }, [linePath, data, scaleX, scaleY, bounds.minY]);

  // Generate grid lines
  const gridLines = useMemo(() => {
    const lines = [];
    const xTicks = 5;
    const yTicks = 4;
    
    // X grid lines
    for (let i = 0; i <= xTicks; i++) {
      const x = padding.left + (i / xTicks) * graphWidth;
      const value = bounds.minX + (i / xTicks) * (bounds.maxX - bounds.minX);
      lines.push({
        type: 'x',
        x1: x, y1: padding.top,
        x2: x, y2: padding.top + graphHeight,
        label: value.toFixed(1),
        labelX: x,
        labelY: height - 10,
      });
    }
    
    // Y grid lines
    for (let i = 0; i <= yTicks; i++) {
      const y = padding.top + (i / yTicks) * graphHeight;
      const value = bounds.maxY - (i / yTicks) * (bounds.maxY - bounds.minY);
      lines.push({
        type: 'y',
        x1: padding.left, y1: y,
        x2: padding.left + graphWidth, y2: y,
        label: value.toFixed(1),
        labelX: padding.left - 5,
        labelY: y + 4,
      });
    }
    
    return lines;
  }, [bounds, graphWidth, graphHeight, padding, height]);

  // Handle point hover
  const handlePointHover = useCallback((point, index) => {
    if (showTooltip) {
      setHoveredPoint({ ...point, index });
    }
  }, [showTooltip]);

  // Render based on graph type
  const renderGraph = () => {
    switch (graphType) {
      case 'line':
        return (
          <motion.path
            d={linePath}
            fill="none"
            stroke={color}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={animated ? { pathLength: 0 } : {}}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        );
      
      case 'area':
        return (
          <>
            <motion.path
              d={areaPath}
              fill={`${color}40`}
              stroke="none"
              initial={animated ? { opacity: 0 } : {}}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            />
            <motion.path
              d={linePath}
              fill="none"
              stroke={color}
              strokeWidth="2"
              initial={animated ? { pathLength: 0 } : {}}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </>
        );
      
      case 'bar':
        const barWidth = Math.max(10, graphWidth / data.length - 5);
        return data.map((point, i) => {
          const x = scaleX(point.x) - barWidth / 2;
          const y = scaleY(point.y);
          const barHeight = scaleY(bounds.minY) - y;
          
          return (
            <motion.rect
              key={i}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={hoveredPoint?.index === i ? secondaryColor : color}
              rx="2"
              initial={animated ? { height: 0, y: scaleY(bounds.minY) } : {}}
              animate={{ height: barHeight, y }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              onMouseEnter={() => handlePointHover(point, i)}
              onMouseLeave={() => setHoveredPoint(null)}
              onClick={() => onPointClick?.(point, i)}
              style={{ cursor: onPointClick ? 'pointer' : 'default' }}
            />
          );
        });
      
      case 'scatter':
        return data.map((point, i) => (
          <motion.circle
            key={i}
            cx={scaleX(point.x)}
            cy={scaleY(point.y)}
            r={hoveredPoint?.index === i ? 8 : 5}
            fill={hoveredPoint?.index === i ? secondaryColor : color}
            initial={animated ? { scale: 0 } : {}}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3, delay: i * 0.03 }}
            onMouseEnter={() => handlePointHover(point, i)}
            onMouseLeave={() => setHoveredPoint(null)}
            onClick={() => onPointClick?.(point, i)}
            style={{ cursor: onPointClick ? 'pointer' : 'default' }}
          />
        ));
      
      default:
        return null;
    }
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      {(title || formula) && (
        <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            {title && <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">{title}</h4>}
            {formula && <p className="text-xs text-gray-500 dark:text-gray-400">{formula}</p>}
          </div>
          
          {/* Graph type selector */}
          <div className="flex gap-1">
            {Object.entries(GRAPH_TYPES).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setGraphType(key)}
                className={`w-7 h-7 rounded flex items-center justify-center text-xs transition-colors ${
                  graphType === key
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'
                }`}
                title={config.name}
              >
                {config.icon}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* SVG Graph */}
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="block"
      >
        {/* Grid */}
        {showGrid && (
          <g className="grid">
            {gridLines.map((line, i) => (
              <g key={i}>
                <line
                  x1={line.x1}
                  y1={line.y1}
                  x2={line.x2}
                  y2={line.y2}
                  stroke="#E5E7EB"
                  strokeWidth="1"
                  strokeDasharray={line.type === 'y' ? '4 2' : 'none'}
                />
                <text
                  x={line.labelX}
                  y={line.labelY}
                  fontSize="9"
                  fill="#9CA3AF"
                  textAnchor={line.type === 'y' ? 'end' : 'middle'}
                >
                  {line.label}
                </text>
              </g>
            ))}
          </g>
        )}

        {/* Axes */}
        <g className="axes">
          {/* X-axis */}
          <line
            x1={padding.left}
            y1={padding.top + graphHeight}
            x2={padding.left + graphWidth}
            y2={padding.top + graphHeight}
            stroke="#374151"
            strokeWidth="1.5"
          />
          {/* Y-axis */}
          <line
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={padding.top + graphHeight}
            stroke="#374151"
            strokeWidth="1.5"
          />
          
          {/* Axis labels */}
          <text
            x={padding.left + graphWidth / 2}
            y={height - 2}
            fontSize="10"
            fill="#6B7280"
            textAnchor="middle"
          >
            {xLabel}{xUnit && ` (${xUnit})`}
          </text>
          <text
            x={12}
            y={padding.top + graphHeight / 2}
            fontSize="10"
            fill="#6B7280"
            textAnchor="middle"
            transform={`rotate(-90, 12, ${padding.top + graphHeight / 2})`}
          >
            {yLabel}{yUnit && ` (${yUnit})`}
          </text>
        </g>

        {/* Graph content */}
        <g className="graph-content">
          {renderGraph()}
        </g>

        {/* Data points for line/area graphs */}
        {(graphType === 'line' || graphType === 'area') && data.map((point, i) => (
          <motion.circle
            key={i}
            cx={scaleX(point.x)}
            cy={scaleY(point.y)}
            r={hoveredPoint?.index === i || highlightPoint === i ? 6 : 4}
            fill={hoveredPoint?.index === i || highlightPoint === i ? secondaryColor : color}
            stroke="white"
            strokeWidth="2"
            initial={animated ? { scale: 0 } : {}}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3, delay: 0.5 + i * 0.05 }}
            onMouseEnter={() => handlePointHover(point, i)}
            onMouseLeave={() => setHoveredPoint(null)}
            onClick={() => onPointClick?.(point, i)}
            style={{ cursor: onPointClick ? 'pointer' : 'default' }}
          />
        ))}

        {/* Highlight point marker */}
        {highlightPoint !== null && data[highlightPoint] && (
          <motion.circle
            cx={scaleX(data[highlightPoint].x)}
            cy={scaleY(data[highlightPoint].y)}
            r="12"
            fill="none"
            stroke={secondaryColor}
            strokeWidth="2"
            strokeDasharray="4 2"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          />
        )}
      </svg>

      {/* Tooltip */}
      <AnimatePresence>
        {hoveredPoint && (
          <motion.div
            className="absolute bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg pointer-events-none z-10"
            style={{
              left: Math.min(scaleX(hoveredPoint.x) + 10, width - 100),
              top: Math.max(scaleY(hoveredPoint.y) - 40, 10),
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            <div className="font-semibold">{hoveredPoint.label || `Point ${hoveredPoint.index + 1}`}</div>
            <div className="text-gray-300">
              {xLabel}: {hoveredPoint.x.toFixed(2)}{xUnit && ` ${xUnit}`}
            </div>
            <div className="text-gray-300">
              {yLabel}: {hoveredPoint.y.toFixed(2)}{yUnit && ` ${yUnit}`}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legend */}
      {showLegend && (
        <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700 flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-600 dark:text-gray-400">{yLabel}</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper component: Mini graph for inline display
export const MiniGraph = ({ data, width = 80, height = 30, color = '#2196F3' }) => {
  if (data.length < 2) return null;
  
  const minY = Math.min(...data.map(d => d.y));
  const maxY = Math.max(...data.map(d => d.y));
  const range = maxY - minY || 1;
  
  const path = data.map((point, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((point.y - minY) / range) * height;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');
  
  return (
    <svg width={width} height={height} className="inline-block">
      <motion.path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5 }}
      />
    </svg>
  );
};

// Helper: Generate data points for a function
export const generateFunctionData = (fn, xMin, xMax, steps = 50) => {
  const data = [];
  const step = (xMax - xMin) / steps;
  
  for (let x = xMin; x <= xMax; x += step) {
    try {
      const y = fn(x);
      if (isFinite(y)) {
        data.push({ x, y });
      }
    } catch (e) {
      // Skip invalid points
    }
  }
  
  return data;
};

export default LiveGraph;



