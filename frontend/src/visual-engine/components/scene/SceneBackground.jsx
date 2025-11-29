/**
 * Scene Background Component
 * Renders various Indian-themed backgrounds
 */

import React from 'react';

const SceneBackground = ({ scene = 'classroom' }) => {
  const backgrounds = {
    cricket_pitch: <CricketPitchBg />,
    cricket: <CricketPitchBg />,
    classroom: <ClassroomBg />,
    lab: <LabBg />,
    street: <StreetBg />,
    village: <VillageBg />,
    space: <SpaceBg />,
  };

  return backgrounds[scene] || backgrounds.classroom;
};

const CricketPitchBg = () => (
  <g id="bg-cricket">
    {/* Sky gradient */}
    <defs>
      <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#87CEEB" />
        <stop offset="100%" stopColor="#E0F7FA" />
      </linearGradient>
      <linearGradient id="grass" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#7CB342" />
        <stop offset="100%" stopColor="#558B2F" />
      </linearGradient>
    </defs>
    
    {/* Sky */}
    <rect x="0" y="0" width="100" height="42" fill="url(#sky)" />
    
    {/* Grass field */}
    <rect x="0" y="42" width="100" height="18" fill="url(#grass)" />
    
    {/* Cricket pitch */}
    <rect x="15" y="44" width="70" height="12" fill="#D7CCC8" rx="1" />
    
    {/* Pitch markings */}
    <line x1="22" y1="44" x2="22" y2="56" stroke="white" strokeWidth="0.5" />
    <line x1="78" y1="44" x2="78" y2="56" stroke="white" strokeWidth="0.5" />
    
    {/* Boundary rope */}
    <ellipse cx="50" cy="50" rx="45" ry="8" fill="none" stroke="white" strokeWidth="0.3" strokeDasharray="2 1" />
    
    {/* Stadium lights */}
    <circle cx="10" cy="8" r="3" fill="#FFF9C4" opacity="0.6" />
    <circle cx="90" cy="8" r="3" fill="#FFF9C4" opacity="0.6" />
  </g>
);

const ClassroomBg = () => (
  <g id="bg-classroom">
    <defs>
      <linearGradient id="wall" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#FFF8E1" />
        <stop offset="100%" stopColor="#FFECB3" />
      </linearGradient>
    </defs>
    
    {/* Wall */}
    <rect x="0" y="0" width="100" height="60" fill="url(#wall)" />
    
    {/* Blackboard */}
    <rect x="10" y="5" width="80" height="25" fill="#2E7D32" rx="1" />
    <rect x="11" y="6" width="78" height="23" fill="#1B5E20" rx="0.5" />
    
    {/* Chalk tray */}
    <rect x="10" y="30" width="80" height="2" fill="#5D4037" />
    
    {/* Floor */}
    <rect x="0" y="45" width="100" height="15" fill="#D7CCC8" />
    
    {/* Floor lines */}
    {[0, 20, 40, 60, 80, 100].map(x => (
      <line key={x} x1={x} y1="45" x2={x} y2="60" stroke="#BCAAA4" strokeWidth="0.3" />
    ))}
  </g>
);

const LabBg = () => (
  <g id="bg-lab">
    <defs>
      <linearGradient id="labwall" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#E3F2FD" />
        <stop offset="100%" stopColor="#BBDEFB" />
      </linearGradient>
    </defs>
    
    {/* Wall */}
    <rect x="0" y="0" width="100" height="60" fill="url(#labwall)" />
    
    {/* Lab table */}
    <rect x="5" y="35" width="90" height="3" fill="#37474F" rx="0.5" />
    <rect x="5" y="38" width="90" height="22" fill="#455A64" />
    
    {/* Shelves */}
    <rect x="70" y="8" width="25" height="1.5" fill="#795548" />
    <rect x="70" y="18" width="25" height="1.5" fill="#795548" />
    
    {/* Beakers on shelf */}
    <ellipse cx="75" cy="6" rx="2" ry="3" fill="#90CAF9" opacity="0.7" />
    <ellipse cx="82" cy="6" rx="2" ry="3" fill="#A5D6A7" opacity="0.7" />
    <ellipse cx="89" cy="6" rx="2" ry="3" fill="#FFCC80" opacity="0.7" />
  </g>
);

const StreetBg = () => (
  <g id="bg-street">
    <defs>
      <linearGradient id="streetsky" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#81D4FA" />
        <stop offset="100%" stopColor="#E1F5FE" />
      </linearGradient>
      <linearGradient id="road" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#424242" />
        <stop offset="100%" stopColor="#212121" />
      </linearGradient>
    </defs>
    
    {/* Sky */}
    <rect x="0" y="0" width="100" height="35" fill="url(#streetsky)" />
    
    {/* Buildings */}
    <rect x="2" y="15" width="12" height="20" fill="#90A4AE" />
    <rect x="86" y="12" width="14" height="23" fill="#78909C" />
    
    {/* Road */}
    <rect x="0" y="35" width="100" height="25" fill="url(#road)" />
    
    {/* Road markings */}
    {[10, 30, 50, 70, 90].map(x => (
      <rect key={x} x={x} y="46" width="8" height="1.5" fill="#FFC107" />
    ))}
    
    {/* Sidewalk */}
    <rect x="0" y="33" width="100" height="4" fill="#BDBDBD" />
    
    {/* Traffic signal */}
    <rect x="12" y="20" width="1" height="15" fill="#424242" />
    <rect x="10" y="20" width="5" height="10" fill="#37474F" rx="0.5" />
    <circle cx="12.5" cy="23" r="1.2" fill="#EF5350" />
    <circle cx="12.5" cy="26" r="1.2" fill="#FFC107" />
    <circle cx="12.5" cy="29" r="1.2" fill="#4CAF50" />
  </g>
);

const VillageBg = () => (
  <g id="bg-village">
    <defs>
      <linearGradient id="villagesky" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#64B5F6" />
        <stop offset="100%" stopColor="#E3F2FD" />
      </linearGradient>
      <linearGradient id="villageground" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#8BC34A" />
        <stop offset="100%" stopColor="#558B2F" />
      </linearGradient>
    </defs>
    
    {/* Sky */}
    <rect x="0" y="0" width="100" height="42" fill="url(#villagesky)" />
    
    {/* Sun */}
    <circle cx="85" cy="10" r="5" fill="#FFD54F">
      <animate attributeName="r" values="5;5.5;5" dur="3s" repeatCount="indefinite" />
    </circle>
    
    {/* Hills */}
    <ellipse cx="20" cy="42" rx="25" ry="10" fill="#81C784" />
    <ellipse cx="70" cy="42" rx="30" ry="12" fill="#66BB6A" />
    
    {/* Ground */}
    <rect x="0" y="42" width="100" height="18" fill="url(#villageground)" />
    
    {/* Hut */}
    <polygon points="15,35 20,28 25,35" fill="#8D6E63" />
    <rect x="16" y="35" width="8" height="7" fill="#A1887F" />
    <rect x="18" y="37" width="3" height="5" fill="#5D4037" />
    
    {/* Tree */}
    <rect x="75" y="35" width="3" height="10" fill="#5D4037" />
    <circle cx="76.5" cy="30" r="8" fill="#4CAF50" />
  </g>
);

const SpaceBg = () => (
  <g id="bg-space">
    {/* Dark space */}
    <rect x="0" y="0" width="100" height="60" fill="#0D1B2A" />
    
    {/* Stars */}
    {[...Array(30)].map((_, i) => (
      <circle
        key={i}
        cx={Math.random() * 100}
        cy={Math.random() * 60}
        r={Math.random() * 0.4 + 0.2}
        fill="white"
        opacity={Math.random() * 0.5 + 0.3}
      >
        <animate
          attributeName="opacity"
          values={`${Math.random() * 0.3 + 0.3};${Math.random() * 0.5 + 0.5};${Math.random() * 0.3 + 0.3}`}
          dur={`${Math.random() * 2 + 1}s`}
          repeatCount="indefinite"
        />
      </circle>
    ))}
    
    {/* Earth */}
    <circle cx="15" cy="48" r="8" fill="#2196F3">
      <animateTransform
        attributeName="transform"
        type="rotate"
        from="0 15 48"
        to="360 15 48"
        dur="60s"
        repeatCount="indefinite"
      />
    </circle>
    <ellipse cx="14" cy="48" rx="6" ry="2" fill="#4CAF50" opacity="0.5" />
    
    {/* Moon */}
    <circle cx="80" cy="20" r="4" fill="#9E9E9E" />
    <circle cx="79" cy="19" r="0.8" fill="#757575" />
    <circle cx="81" cy="21" r="0.6" fill="#757575" />
  </g>
);

export default SceneBackground;







