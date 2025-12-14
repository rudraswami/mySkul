/**
 * ✏️ SKETCH PRIMITIVES LIBRARY (SketchSense V6)
 * ==============================================
 * 
 * Hand-drawn, RoughJS-powered sketch components.
 * Each primitive uses RoughJS for wobbly, organic lines.
 * 
 * ALL primitives:
 * - Use RoughJS for hand-drawn effect
 * - Animate with Framer Motion pathLength
 * - Support wobble + jitter
 * - Support marker/highlighter colors
 * - Support dynamic resizing
 * 
 * The Magic Notebook comes alive here! ✨
 */

import React, { useRef, useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import rough from 'roughjs';

// ============================================
// MAGIC NOTEBOOK THEME
// ============================================
export const NOTEBOOK_THEME = {
  // Paper
  paperBg: '#FDFCF8',
  paperWarm: '#FBF9F3',
  dotColor: '#E2E8F0',
  lineColor: '#CBD5E1',
  
  // Pencil & Ink
  pencilGray: '#4B5563',
  penBlack: '#1F2937',
  inkBlue: '#2563EB',
  
  // Highlighters
  highlightYellow: '#fde047',
  highlightPink: '#f9a8d4',
  highlightBlue: '#93C5FD',
  highlightGreen: '#86EFAC',
  highlightOrange: '#FDBA74',
  
  // Markers
  markerRed: '#EF4444',
  markerBlue: '#3B82F6',
  markerGreen: '#22C55E',
  markerPurple: '#A855F7',
  
  // Fonts
  handwriting: "'Patrick Hand', 'Caveat', cursive",
  
  // RoughJS defaults
  roughness: 1.5,
  bowing: 1,
  strokeWidth: 2,
};

// ============================================
// ROUGHJS CANVAS HOOK
// ============================================
const useRoughCanvas = (svgRef) => {
  const [rc, setRc] = useState(null);
  
  useEffect(() => {
    if (svgRef.current) {
      const roughSvg = rough.svg(svgRef.current);
      setRc(roughSvg);
    }
  }, [svgRef]);
  
  return rc;
};

// ============================================
// LIVE DRAWING ANIMATION VARIANTS
// ============================================
export const drawVariants = {
  hidden: { 
    pathLength: 0, 
    opacity: 0 
  },
  visible: (delay = 0) => ({
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: { 
        type: 'spring', 
        duration: 1.5, 
        bounce: 0,
        delay 
      },
      opacity: { duration: 0.3, delay }
    }
  }),
};

export const fadeInVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: (delay = 0) => ({
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      delay,
      ease: 'easeOut'
    }
  }),
};

export const popVariants = {
  hidden: { opacity: 0, scale: 0 },
  visible: (delay = 0) => ({
    opacity: 1,
    scale: [0, 1.2, 1],
    transition: {
      duration: 0.4,
      delay,
      times: [0, 0.6, 1]
    }
  }),
};

// ============================================
// SKETCH CIRCLE
// ============================================
export const SketchCircle = ({
  cx = 100,
  cy = 100,
  radius = 50,
  fill = 'transparent',
  stroke = NOTEBOOK_THEME.pencilGray,
  strokeWidth = 2,
  roughness = 1.5,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [pathData, setPathData] = useState('');
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const circle = rc.circle(cx, cy, radius * 2, {
        stroke,
        strokeWidth,
        roughness,
        fill: fill !== 'transparent' ? fill : undefined,
        fillStyle: 'hachure',
      });
      
      // Extract path data from the generated element
      const paths = circle.querySelectorAll('path');
      if (paths.length > 0) {
        setPathData(paths[0].getAttribute('d') || '');
      }
    }
  }, [cx, cy, radius, fill, stroke, strokeWidth, roughness]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`sketch-circle ${className}`}
      style={{ overflow: 'visible' }}
    >
      {pathData && (
        <motion.path
          d={pathData}
          fill={fill}
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay}
        />
      )}
    </svg>
  );
};

// ============================================
// SKETCH RECTANGLE
// ============================================
export const SketchRect = ({
  x = 0,
  y = 0,
  width = 100,
  height = 60,
  fill = 'transparent',
  stroke = NOTEBOOK_THEME.pencilGray,
  strokeWidth = 2,
  roughness = 1.5,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [paths, setPaths] = useState([]);
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const rect = rc.rectangle(x, y, width, height, {
        stroke,
        strokeWidth,
        roughness,
        fill: fill !== 'transparent' ? fill : undefined,
        fillStyle: 'hachure',
      });
      
      const pathElements = rect.querySelectorAll('path');
      const pathDataList = [];
      pathElements.forEach(p => {
        const d = p.getAttribute('d');
        if (d) pathDataList.push(d);
      });
      setPaths(pathDataList);
    }
  }, [x, y, width, height, fill, stroke, strokeWidth, roughness]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`sketch-rect ${className}`}
      style={{ overflow: 'visible' }}
    >
      {paths.map((d, i) => (
        <motion.path
          key={i}
          d={d}
          fill={i === 0 ? fill : 'none'}
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay + i * 0.1}
        />
      ))}
    </svg>
  );
};

// ============================================
// SKETCH ARROW
// ============================================
export const SketchArrow = ({
  x1 = 0,
  y1 = 50,
  x2 = 100,
  y2 = 50,
  stroke = NOTEBOOK_THEME.markerBlue,
  strokeWidth = 3,
  roughness = 1,
  headSize = 15,
  delay = 0,
  animate = true,
  curved = false,
  curveOffset = -30, // Positive = curve down, Negative = curve up
  label = '',
  className = '',
}) => {
  const svgRef = useRef(null);
  const [linePath, setLinePath] = useState('');
  const [arrowHeadPaths, setArrowHeadPaths] = useState([]);
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      
      // Draw line
      let line;
      if (curved) {
        const midX = (x1 + x2) / 2;
        const midY = (y1 + y2) / 2 + curveOffset;
        line = rc.path(`M ${x1} ${y1} Q ${midX} ${midY} ${x2} ${y2}`, {
          stroke,
          strokeWidth,
          roughness,
        });
      } else {
        line = rc.line(x1, y1, x2, y2, {
          stroke,
          strokeWidth,
          roughness,
        });
      }
      
      // Extract line path
      const linePaths = line.querySelectorAll('path');
      if (linePaths.length > 0) {
        setLinePath(linePaths[0].getAttribute('d') || '');
      }
      
      // Calculate arrow head
      const angle = Math.atan2(y2 - y1, x2 - x1);
      const headX1 = x2 - headSize * Math.cos(angle - Math.PI / 6);
      const headY1 = y2 - headSize * Math.sin(angle - Math.PI / 6);
      const headX2 = x2 - headSize * Math.cos(angle + Math.PI / 6);
      const headY2 = y2 - headSize * Math.sin(angle + Math.PI / 6);
      
      const head1 = rc.line(x2, y2, headX1, headY1, { stroke, strokeWidth, roughness });
      const head2 = rc.line(x2, y2, headX2, headY2, { stroke, strokeWidth, roughness });
      
      const headPathList = [];
      head1.querySelectorAll('path').forEach(p => {
        const d = p.getAttribute('d');
        if (d) headPathList.push(d);
      });
      head2.querySelectorAll('path').forEach(p => {
        const d = p.getAttribute('d');
        if (d) headPathList.push(d);
      });
      setArrowHeadPaths(headPathList);
    }
  }, [x1, y1, x2, y2, stroke, strokeWidth, roughness, headSize, curved, curveOffset]);
  
  return (
    <g className={`sketch-arrow ${className}`}>
      {linePath && (
        <motion.path
          d={linePath}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay}
        />
      )}
      {arrowHeadPaths.map((d, i) => (
        <motion.path
          key={i}
          d={d}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay + 0.3}
        />
      ))}
      {label && (
        <motion.text
          x={(x1 + x2) / 2}
          y={(y1 + y2) / 2 - 10}
          textAnchor="middle"
          fill={stroke}
          fontFamily={NOTEBOOK_THEME.handwriting}
          fontSize="14"
          variants={fadeInVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay + 0.5}
        >
          {label}
        </motion.text>
      )}
    </g>
  );
};

// ============================================
// SKETCH LABEL (Handwritten Text)
// ============================================
export const SketchLabel = ({
  x = 0,
  y = 0,
  text = '',
  fontSize = 18,
  color = NOTEBOOK_THEME.penBlack,
  align = 'middle', // 'start', 'middle', 'end'
  rotate = 0,
  delay = 0,
  animate = true,
  underline = false,
  className = '',
}) => {
  return (
    <motion.g
      className={`sketch-label ${className}`}
      transform={`translate(${x}, ${y}) rotate(${rotate})`}
      variants={fadeInVariants}
      initial={animate ? "hidden" : "visible"}
      animate="visible"
      custom={delay}
    >
      <text
        textAnchor={align}
        fill={color}
        fontFamily={NOTEBOOK_THEME.handwriting}
        fontSize={fontSize}
        style={{ 
          filter: 'url(#pencil-texture)',
        }}
      >
        {text}
      </text>
      {underline && (
        <motion.line
          x1={align === 'middle' ? -text.length * 5 : 0}
          y1={5}
          x2={align === 'middle' ? text.length * 5 : text.length * 10}
          y2={6}
          stroke={color}
          strokeWidth={2}
          strokeLinecap="round"
          opacity={0.5}
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay + 0.2}
        />
      )}
    </motion.g>
  );
};

// ============================================
// SKETCH HIGHLIGHT (Marker Background)
// ============================================
export const SketchHighlight = ({
  x = 0,
  y = 0,
  width = 100,
  height = 30,
  color = NOTEBOOK_THEME.highlightYellow,
  opacity = 0.5,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [pathData, setPathData] = useState('');
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const highlight = rc.rectangle(x, y, width, height, {
        fill: color,
        fillStyle: 'solid',
        roughness: 2,
        stroke: 'none',
      });
      
      const paths = highlight.querySelectorAll('path');
      if (paths.length > 0) {
        setPathData(paths[0].getAttribute('d') || '');
      }
    }
  }, [x, y, width, height, color]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`sketch-highlight ${className}`}
      style={{ overflow: 'visible' }}
    >
      {pathData && (
        <motion.path
          d={pathData}
          fill={color}
          opacity={opacity}
          variants={fadeInVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay}
        />
      )}
    </svg>
  );
};

// ============================================
// SKETCH STICK FIGURE
// ============================================
export const SketchStickFigure = ({
  x = 100,
  y = 100,
  size = 60,
  pose = 'standing', // 'standing', 'pushing', 'running', 'thinking'
  stroke = NOTEBOOK_THEME.pencilGray,
  strokeWidth = 2,
  delay = 0,
  animate = true,
  expression = 'neutral', // 'happy', 'sad', 'surprised'
  className = '',
}) => {
  const headRadius = size * 0.15;
  const bodyLength = size * 0.35;
  const limbLength = size * 0.25;
  
  // Different poses
  const poses = {
    standing: {
      leftArm: { x1: 0, y1: bodyLength * 0.3, x2: -limbLength, y2: bodyLength * 0.5 },
      rightArm: { x1: 0, y1: bodyLength * 0.3, x2: limbLength, y2: bodyLength * 0.5 },
      leftLeg: { x1: 0, y1: bodyLength, x2: -limbLength * 0.6, y2: bodyLength + limbLength },
      rightLeg: { x1: 0, y1: bodyLength, x2: limbLength * 0.6, y2: bodyLength + limbLength },
    },
    pushing: {
      leftArm: { x1: 0, y1: bodyLength * 0.3, x2: limbLength * 1.2, y2: bodyLength * 0.2 },
      rightArm: { x1: 0, y1: bodyLength * 0.3, x2: limbLength * 1.2, y2: bodyLength * 0.4 },
      leftLeg: { x1: 0, y1: bodyLength, x2: -limbLength * 0.8, y2: bodyLength + limbLength },
      rightLeg: { x1: 0, y1: bodyLength, x2: limbLength * 0.3, y2: bodyLength + limbLength },
    },
    running: {
      leftArm: { x1: 0, y1: bodyLength * 0.3, x2: -limbLength, y2: bodyLength * 0.1 },
      rightArm: { x1: 0, y1: bodyLength * 0.3, x2: limbLength, y2: bodyLength * 0.5 },
      leftLeg: { x1: 0, y1: bodyLength, x2: limbLength, y2: bodyLength + limbLength * 0.8 },
      rightLeg: { x1: 0, y1: bodyLength, x2: -limbLength * 0.5, y2: bodyLength + limbLength },
    },
    thinking: {
      leftArm: { x1: 0, y1: bodyLength * 0.3, x2: -limbLength * 0.5, y2: -headRadius },
      rightArm: { x1: 0, y1: bodyLength * 0.3, x2: limbLength, y2: bodyLength * 0.5 },
      leftLeg: { x1: 0, y1: bodyLength, x2: -limbLength * 0.4, y2: bodyLength + limbLength },
      rightLeg: { x1: 0, y1: bodyLength, x2: limbLength * 0.4, y2: bodyLength + limbLength },
    },
  };
  
  const currentPose = poses[pose] || poses.standing;
  
  // Expression (simple face)
  const getExpression = () => {
    switch (expression) {
      case 'happy':
        return (
          <path
            d={`M ${-headRadius * 0.4} ${-headRadius * 0.1} Q ${0} ${headRadius * 0.4} ${headRadius * 0.4} ${-headRadius * 0.1}`}
            fill="none"
            stroke={stroke}
            strokeWidth={1.5}
          />
        );
      case 'sad':
        return (
          <path
            d={`M ${-headRadius * 0.4} ${headRadius * 0.2} Q ${0} ${-headRadius * 0.1} ${headRadius * 0.4} ${headRadius * 0.2}`}
            fill="none"
            stroke={stroke}
            strokeWidth={1.5}
          />
        );
      case 'surprised':
        return (
          <circle cx={0} cy={headRadius * 0.1} r={headRadius * 0.2} fill="none" stroke={stroke} strokeWidth={1.5} />
        );
      default:
        return (
          <line x1={-headRadius * 0.3} y1={headRadius * 0.1} x2={headRadius * 0.3} y2={headRadius * 0.1} stroke={stroke} strokeWidth={1.5} />
        );
    }
  };
  
  return (
    <motion.g
      className={`sketch-stick-figure ${className}`}
      transform={`translate(${x}, ${y})`}
      variants={popVariants}
      initial={animate ? "hidden" : "visible"}
      animate="visible"
      custom={delay}
    >
      {/* Head */}
      <motion.circle
        cx={0}
        cy={-headRadius}
        r={headRadius}
        fill="none"
        stroke={stroke}
        strokeWidth={strokeWidth}
        variants={drawVariants}
        custom={delay}
      />
      
      {/* Eyes */}
      <circle cx={-headRadius * 0.3} cy={-headRadius * 0.3} r={2} fill={stroke} />
      <circle cx={headRadius * 0.3} cy={-headRadius * 0.3} r={2} fill={stroke} />
      
      {/* Expression */}
      <g transform={`translate(0, ${-headRadius})`}>
        {getExpression()}
      </g>
      
      {/* Body */}
      <motion.line
        x1={0}
        y1={0}
        x2={0}
        y2={bodyLength}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        variants={drawVariants}
        custom={delay + 0.1}
      />
      
      {/* Arms */}
      <motion.line
        {...currentPose.leftArm}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        variants={drawVariants}
        custom={delay + 0.2}
      />
      <motion.line
        {...currentPose.rightArm}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        variants={drawVariants}
        custom={delay + 0.25}
      />
      
      {/* Legs */}
      <motion.line
        {...currentPose.leftLeg}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        variants={drawVariants}
        custom={delay + 0.3}
      />
      <motion.line
        {...currentPose.rightLeg}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        variants={drawVariants}
        custom={delay + 0.35}
      />
    </motion.g>
  );
};

// ============================================
// SKETCH DOODLE (Decorative Elements)
// ============================================
export const SketchDoodle = ({
  x = 0,
  y = 0,
  type = 'star', // 'star', 'sparkle', 'arrow', 'spiral', 'burst', 'cloud'
  size = 20,
  color = NOTEBOOK_THEME.highlightYellow,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const doodles = {
    star: `M ${size/2} 0 L ${size*0.6} ${size*0.35} L ${size} ${size*0.4} L ${size*0.7} ${size*0.6} L ${size*0.8} ${size} L ${size/2} ${size*0.75} L ${size*0.2} ${size} L ${size*0.3} ${size*0.6} L 0 ${size*0.4} L ${size*0.4} ${size*0.35} Z`,
    sparkle: `M ${size/2} 0 L ${size/2} ${size} M 0 ${size/2} L ${size} ${size/2} M ${size*0.15} ${size*0.15} L ${size*0.85} ${size*0.85} M ${size*0.85} ${size*0.15} L ${size*0.15} ${size*0.85}`,
    spiral: `M ${size/2} ${size/2} Q ${size*0.7} ${size*0.3} ${size*0.8} ${size*0.5} Q ${size*0.9} ${size*0.7} ${size*0.7} ${size*0.8} Q ${size*0.5} ${size*0.9} ${size*0.3} ${size*0.7} Q ${size*0.2} ${size*0.5} ${size*0.3} ${size*0.35}`,
    burst: `M ${size/2} ${size/2} L ${size/2} 0 M ${size/2} ${size/2} L ${size} ${size/2} M ${size/2} ${size/2} L ${size/2} ${size} M ${size/2} ${size/2} L 0 ${size/2} M ${size/2} ${size/2} L ${size*0.85} ${size*0.15} M ${size/2} ${size/2} L ${size*0.15} ${size*0.85} M ${size/2} ${size/2} L ${size*0.85} ${size*0.85} M ${size/2} ${size/2} L ${size*0.15} ${size*0.15}`,
    cloud: `M ${size*0.2} ${size*0.6} Q ${size*0.1} ${size*0.4} ${size*0.3} ${size*0.35} Q ${size*0.35} ${size*0.2} ${size*0.5} ${size*0.25} Q ${size*0.65} ${size*0.15} ${size*0.75} ${size*0.3} Q ${size*0.9} ${size*0.35} ${size*0.85} ${size*0.5} Q ${size*0.9} ${size*0.65} ${size*0.7} ${size*0.7} L ${size*0.3} ${size*0.7} Q ${size*0.1} ${size*0.65} ${size*0.2} ${size*0.6}`,
  };
  
  return (
    <motion.g
      className={`sketch-doodle ${className}`}
      transform={`translate(${x}, ${y})`}
      variants={popVariants}
      initial={animate ? "hidden" : "visible"}
      animate="visible"
      custom={delay}
    >
      <motion.path
        d={doodles[type] || doodles.star}
        fill={type === 'star' || type === 'cloud' ? color : 'none'}
        stroke={color}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        variants={drawVariants}
        custom={delay}
      />
    </motion.g>
  );
};

// ============================================
// SKETCH LINE (Simple Line)
// ============================================
export const SketchLine = ({
  x1 = 0,
  y1 = 0,
  x2 = 100,
  y2 = 0,
  stroke = NOTEBOOK_THEME.pencilGray,
  strokeWidth = 2,
  roughness = 1,
  dashed = false,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [pathData, setPathData] = useState('');
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const line = rc.line(x1, y1, x2, y2, {
        stroke,
        strokeWidth,
        roughness,
      });
      
      const paths = line.querySelectorAll('path');
      if (paths.length > 0) {
        setPathData(paths[0].getAttribute('d') || '');
      }
    }
  }, [x1, y1, x2, y2, stroke, strokeWidth, roughness]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`sketch-line ${className}`}
      style={{ overflow: 'visible' }}
    >
      {pathData && (
        <motion.path
          d={pathData}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={dashed ? '8 4' : undefined}
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay}
        />
      )}
    </svg>
  );
};

// ============================================
// SKETCH PATH (Custom Curves)
// ============================================
export const SketchPath = ({
  d = '',
  fill = 'none',
  stroke = NOTEBOOK_THEME.pencilGray,
  strokeWidth = 2,
  roughness = 1.5,
  dashed = false,
  delay = 0,
  animate = true,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [roughPath, setRoughPath] = useState('');
  
  useEffect(() => {
    if (svgRef.current && d) {
      const rc = rough.svg(svgRef.current);
      const path = rc.path(d, {
        stroke,
        strokeWidth,
        roughness,
        fill: fill !== 'none' ? fill : undefined,
        fillStyle: fill !== 'none' ? 'hachure' : undefined,
      });
      
      const paths = path.querySelectorAll('path');
      if (paths.length > 0) {
        setRoughPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [d, fill, stroke, strokeWidth, roughness]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`sketch-path ${className}`}
      style={{ overflow: 'visible' }}
    >
      {roughPath && (
        <motion.path
          d={roughPath}
          fill={fill}
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={dashed ? '8 4' : undefined}
          variants={drawVariants}
          initial={animate ? "hidden" : "visible"}
          animate="visible"
          custom={delay}
        />
      )}
    </svg>
  );
};

// ============================================
// TYPEWRITER LABEL (Character-by-Character)
// ============================================
export const TypewriterLabel = ({
  text = '',
  x = 0,
  y = 0,
  fontSize = 18,
  color = NOTEBOOK_THEME.penBlack,
  align = 'middle',
  delay = 0,
  speed = 0.05, // seconds per character
  animate = true,
  className = '',
}) => {
  const [visibleText, setVisibleText] = useState('');
  
  useEffect(() => {
    if (!animate) {
      setVisibleText(text);
      return;
    }
    
    let currentIndex = 0;
    const startTime = Date.now() + delay * 1000;
    
    const typeInterval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const targetIndex = Math.floor(elapsed / speed);
      
      if (targetIndex > currentIndex && currentIndex < text.length) {
        currentIndex = targetIndex;
        setVisibleText(text.slice(0, currentIndex + 1));
      }
      
      if (currentIndex >= text.length) {
        clearInterval(typeInterval);
      }
    }, speed * 1000);
    
    return () => clearInterval(typeInterval);
  }, [text, delay, speed, animate]);
  
  return (
    <motion.text
      x={x}
      y={y}
      textAnchor={align}
      fill={color}
      fontFamily={NOTEBOOK_THEME.handwriting}
      fontSize={fontSize}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.3 }}
      className={`typewriter-label ${className}`}
    >
      {visibleText}
      {animate && visibleText.length < text.length && (
        <tspan opacity={0.5}>|</tspan>
      )}
    </motion.text>
  );
};

// ============================================
// PULSE HIGHLIGHT (Emphasis Animation)
// ============================================
export const PulseHighlight = ({
  x = 0,
  y = 0,
  width = 100,
  height = 30,
  color = NOTEBOOK_THEME.highlightYellow,
  delay = 0,
  pulseCount = 3,
  className = '',
}) => {
  const svgRef = useRef(null);
  const [pathData, setPathData] = useState('');
  
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const highlight = rc.rectangle(x, y, width, height, {
        fill: color,
        fillStyle: 'solid',
        roughness: 2,
        stroke: 'none',
      });
      
      const paths = highlight.querySelectorAll('path');
      if (paths.length > 0) {
        setPathData(paths[0].getAttribute('d') || '');
      }
    }
  }, [x, y, width, height, color]);
  
  return (
    <svg 
      ref={svgRef} 
      className={`pulse-highlight ${className}`}
      style={{ overflow: 'visible' }}
    >
      {pathData && (
        <motion.path
          d={pathData}
          fill={color}
          opacity={0.5}
          animate={{
            opacity: [0.3, 0.7, 0.3],
            scale: [1, 1.05, 1],
          }}
          transition={{
            delay,
            duration: 1,
            repeat: pulseCount - 1,
            ease: 'easeInOut',
          }}
        />
      )}
    </svg>
  );
};

// ============================================
// GLOW EFFECT (Emphasis Glow)
// ============================================
export const GlowEffect = ({
  children,
  color = NOTEBOOK_THEME.highlightYellow,
  intensity = 10,
  delay = 0,
  duration = 1,
  className = '',
}) => {
  return (
    <motion.g
      className={`glow-effect ${className}`}
      initial={{ filter: 'drop-shadow(0 0 0px transparent)' }}
      animate={{
        filter: [
          `drop-shadow(0 0 0px ${color})`,
          `drop-shadow(0 0 ${intensity}px ${color})`,
          `drop-shadow(0 0 0px ${color})`,
        ],
      }}
      transition={{
        delay,
        duration,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      {children}
    </motion.g>
  );
};

// ============================================
// SVG FILTER DEFINITIONS
// ============================================
export const SketchFilters = () => (
  <defs>
    {/* Pencil Texture */}
    <filter id="pencil-texture" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1" xChannelSelector="R" yChannelSelector="G" />
    </filter>
    
    {/* Paper Grain */}
    <filter id="paper-grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="4" stitchTiles="stitch" result="noise"/>
      <feColorMatrix type="saturate" values="0"/>
      <feBlend in="SourceGraphic" in2="noise" mode="multiply"/>
    </filter>
    
    {/* Glow Effect */}
    <filter id="sketch-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    
    {/* Pulse Glow (Animated) */}
    <filter id="pulse-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur1"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur2"/>
      <feMerge>
        <feMergeNode in="blur2"/>
        <feMergeNode in="blur1"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    {/* Marker Effect */}
    <filter id="marker-effect" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="2" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    
    {/* Shadow Effect */}
    <filter id="sketch-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur"/>
      <feOffset in="blur" dx="2" dy="2" result="offsetBlur"/>
      <feMerge>
        <feMergeNode in="offsetBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
);

// ============================================
// EXPORTS
// ============================================
export default {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchHighlight,
  SketchStickFigure,
  SketchDoodle,
  SketchLine,
  SketchPath,
  TypewriterLabel,
  PulseHighlight,
  GlowEffect,
  SketchFilters,
  NOTEBOOK_THEME,
  drawVariants,
  fadeInVariants,
  popVariants,
};


