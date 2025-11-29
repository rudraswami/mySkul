/**
 * BackgroundLayer - Scene Background Rendering
 * Supports: cricket_pitch, classroom, lab, street, village, space
 */

import React from 'react';
import { motion } from 'framer-motion';

const BackgroundLayer = ({ sceneType, width, height, groundLevel }) => {
  const groundY = height * groundLevel;

  const backgrounds = {
    cricket: <CricketPitchBackground width={width} height={height} groundY={groundY} />,
    classroom: <ClassroomBackground width={width} height={height} groundY={groundY} />,
    lab: <LabBackground width={width} height={height} groundY={groundY} />,
    street: <StreetBackground width={width} height={height} groundY={groundY} />,
    village: <VillageBackground width={width} height={height} groundY={groundY} />,
    space: <SpaceBackground width={width} height={height} />,
  };

  return backgrounds[sceneType] || backgrounds['classroom'];
};

/**
 * Cricket Pitch Background
 */
const CricketPitchBackground = ({ width, height, groundY }) => (
  <g id="background-cricket">
    {/* Sky */}
    <rect x="0" y="0" width={width} height={groundY} fill="url(#sky-gradient)" />
    
    {/* Grass field */}
    <rect x="0" y={groundY} width={width} height={height - groundY} fill="url(#ground-gradient)" />
    
    {/* Pitch (brown strip) */}
    <rect 
      x={width * 0.15} 
      y={groundY} 
      width={width * 0.7} 
      height={height - groundY - 10}
      fill="#D7CCC8"
      stroke="#8D6E63"
      strokeWidth="2"
    />
    
    {/* Crease lines */}
    <line 
      x1={width * 0.2} 
      y1={groundY} 
      x2={width * 0.2} 
      y2={height - 10}
      stroke="white"
      strokeWidth="3"
    />
    <line 
      x1={width * 0.8} 
      y1={groundY} 
      x2={width * 0.8} 
      y2={height - 10}
      stroke="white"
      strokeWidth="3"
    />
    
    {/* Boundary rope (dashed arc) */}
    <motion.ellipse
      cx={width / 2}
      cy={groundY + 20}
      rx={width * 0.45}
      ry={30}
      fill="none"
      stroke="#FFF"
      strokeWidth="2"
      strokeDasharray="10 5"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 2 }}
    />
    
    {/* Stadium lights (subtle) */}
    <circle cx={width * 0.1} cy={30} r="15" fill="#FFF9C4" opacity="0.5" />
    <circle cx={width * 0.9} cy={30} r="15" fill="#FFF9C4" opacity="0.5" />
  </g>
);

/**
 * Classroom Background
 */
const ClassroomBackground = ({ width, height, groundY }) => (
  <g id="background-classroom">
    {/* Wall */}
    <rect x="0" y="0" width={width} height={height} fill="#FFF8E1" />
    
    {/* Blackboard */}
    <rect 
      x={width * 0.1} 
      y={height * 0.1} 
      width={width * 0.8} 
      height={height * 0.4}
      fill="#2E7D32"
      rx="5"
      filter="url(#shadow)"
    />
    <rect 
      x={width * 0.1 + 5} 
      y={height * 0.1 + 5} 
      width={width * 0.8 - 10} 
      height={height * 0.4 - 10}
      fill="#1B5E20"
      rx="3"
    />
    
    {/* Chalk tray */}
    <rect 
      x={width * 0.1} 
      y={height * 0.5} 
      width={width * 0.8} 
      height={15}
      fill="#5D4037"
    />
    
    {/* Floor */}
    <rect x="0" y={groundY} width={width} height={height - groundY} fill="#D7CCC8" />
    
    {/* Floor tiles pattern */}
    {[...Array(8)].map((_, i) => (
      <line 
        key={i}
        x1={width * (i / 8)} 
        y1={groundY} 
        x2={width * (i / 8)} 
        y2={height}
        stroke="#BCAAA4"
        strokeWidth="1"
      />
    ))}
  </g>
);

/**
 * Lab Background
 */
const LabBackground = ({ width, height, groundY }) => (
  <g id="background-lab">
    {/* Wall */}
    <rect x="0" y="0" width={width} height={height} fill="#E3F2FD" />
    
    {/* Lab table */}
    <rect 
      x={width * 0.05} 
      y={height * 0.55} 
      width={width * 0.9} 
      height={20}
      fill="#37474F"
      rx="2"
    />
    <rect 
      x={width * 0.05} 
      y={height * 0.55 + 20} 
      width={width * 0.9} 
      height={height * 0.3}
      fill="#455A64"
    />
    
    {/* Shelves on wall */}
    <rect x={width * 0.7} y={height * 0.1} width={width * 0.25} height={10} fill="#795548" />
    <rect x={width * 0.7} y={height * 0.25} width={width * 0.25} height={10} fill="#795548" />
    
    {/* Beakers on shelf */}
    <ellipse cx={width * 0.75} cy={height * 0.08} rx="8" ry="12" fill="#90CAF9" opacity="0.7" />
    <ellipse cx={width * 0.85} cy={height * 0.08} rx="8" ry="12" fill="#A5D6A7" opacity="0.7" />
    
    {/* Floor */}
    <rect x="0" y={groundY} width={width} height={height - groundY} fill="#ECEFF1" />
  </g>
);

/**
 * Street Background
 */
const StreetBackground = ({ width, height, groundY }) => (
  <g id="background-street">
    {/* Sky */}
    <rect x="0" y="0" width={width} height={groundY * 0.6} fill="url(#sky-gradient)" />
    
    {/* Buildings */}
    <rect x={width * 0.02} y={height * 0.2} width={80} height={groundY * 0.6 - height * 0.2} fill="#90A4AE" />
    <rect x={width * 0.85} y={height * 0.15} width={90} height={groundY * 0.6 - height * 0.15} fill="#78909C" />
    
    {/* Road */}
    <rect x="0" y={groundY * 0.6} width={width} height={height - groundY * 0.6} fill="#424242" />
    
    {/* Road markings */}
    {[...Array(10)].map((_, i) => (
      <rect
        key={i}
        x={width * (i / 10) + 20}
        y={groundY * 0.6 + (height - groundY * 0.6) / 2 - 5}
        width={40}
        height={8}
        fill="#FFC107"
      />
    ))}
    
    {/* Sidewalk */}
    <rect x="0" y={groundY * 0.6 - 20} width={width} height={25} fill="#BDBDBD" />
    
    {/* Traffic signal pole */}
    <rect x={60} y={groundY * 0.3} width={6} height={groundY * 0.4} fill="#424242" />
    <rect x={50} y={groundY * 0.3} width={26} height={50} fill="#37474F" rx="3" />
    <circle cx={63} cy={groundY * 0.3 + 15} r="6" fill="#EF5350" />
    <circle cx={63} cy={groundY * 0.3 + 30} r="6" fill="#FFC107" />
    <circle cx={63} cy={groundY * 0.3 + 45} r="6" fill="#4CAF50" />
  </g>
);

/**
 * Village Background
 */
const VillageBackground = ({ width, height, groundY }) => (
  <g id="background-village">
    {/* Sky */}
    <rect x="0" y="0" width={width} height={groundY} fill="url(#sky-gradient)" />
    
    {/* Sun */}
    <motion.circle
      cx={width * 0.85}
      cy={50}
      r="30"
      fill="#FFD54F"
      animate={{ scale: [1, 1.05, 1] }}
      transition={{ repeat: Infinity, duration: 3 }}
    />
    
    {/* Hills in background */}
    <ellipse cx={width * 0.2} cy={groundY} rx={150} ry={60} fill="#81C784" />
    <ellipse cx={width * 0.7} cy={groundY} rx={180} ry={70} fill="#66BB6A" />
    
    {/* Ground */}
    <rect x="0" y={groundY} width={width} height={height - groundY} fill="url(#ground-gradient)" />
    
    {/* Hut in distance */}
    <polygon points={`${width * 0.15},${groundY - 20} ${width * 0.15 + 40},${groundY - 50} ${width * 0.15 + 80},${groundY - 20}`} fill="#8D6E63" />
    <rect x={width * 0.15 + 10} y={groundY - 20} width={60} height={30} fill="#A1887F" />
    
    {/* Path */}
    <path
      d={`M ${width * 0.3} ${height} Q ${width * 0.4} ${groundY + 30} ${width * 0.5} ${groundY + 10}`}
      fill="none"
      stroke="#D7CCC8"
      strokeWidth="20"
      strokeLinecap="round"
    />
  </g>
);

/**
 * Space Background
 */
const SpaceBackground = ({ width, height }) => (
  <g id="background-space">
    {/* Dark space */}
    <rect x="0" y="0" width={width} height={height} fill="#0D1B2A" />
    
    {/* Stars */}
    {[...Array(50)].map((_, i) => (
      <motion.circle
        key={i}
        cx={Math.random() * width}
        cy={Math.random() * height}
        r={Math.random() * 2 + 0.5}
        fill="white"
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ 
          repeat: Infinity, 
          duration: Math.random() * 2 + 1,
          delay: Math.random() * 2 
        }}
      />
    ))}
    
    {/* Earth in corner */}
    <motion.circle
      cx={width * 0.15}
      cy={height * 0.8}
      r="40"
      fill="#2196F3"
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, duration: 60, ease: 'linear' }}
    >
      <title>Earth</title>
    </motion.circle>
    <ellipse cx={width * 0.15 - 5} cy={height * 0.8} rx="30" ry="10" fill="#4CAF50" opacity="0.5" />
    
    {/* Moon */}
    <circle cx={width * 0.8} cy={height * 0.3} r="20" fill="#9E9E9E" />
    <circle cx={width * 0.8 - 5} cy={height * 0.3 - 3} r="4" fill="#757575" />
    <circle cx={width * 0.8 + 8} cy={height * 0.3 + 5} r="3" fill="#757575" />
  </g>
);

export default BackgroundLayer;









