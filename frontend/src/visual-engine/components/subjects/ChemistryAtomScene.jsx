/**
 * Chemistry - Atom Structure Scene
 * Interactive atom with electrons orbiting
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, Maximize2, Play, ChevronDown, ChevronUp } from 'lucide-react';

const ChemistryAtomScene = ({ embedded = true }) => {
  const [protons, setProtons] = useState(6); // Carbon default
  const [electrons, setElectrons] = useState(6);
  const [neutrons, setNeutrons] = useState(6);
  const [isAnimating, setIsAnimating] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  const massNumber = protons + neutrons;
  const elementNames = { 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O' };

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* Scene */}
      <div className="relative bg-gradient-to-br from-indigo-900 via-purple-900 to-black" style={{ height: isExpanded ? '60vh' : '240px' }}>
        <svg viewBox="0 0 400 200" className="w-full h-full">
          <defs>
            <radialGradient id="nucleusGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#FF6B6B" />
              <stop offset="100%" stopColor="#C92A2A" />
            </radialGradient>
            <filter id="glowAtom">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Electron Orbits */}
          {[60, 85, 110].map((r, i) => (
            <ellipse
              key={i}
              cx="200" cy="100"
              rx={r} ry={r * 0.4}
              fill="none"
              stroke="rgba(100, 200, 255, 0.3)"
              strokeWidth="1"
              strokeDasharray="4 4"
              transform={`rotate(${i * 60} 200 100)`}
            />
          ))}

          {/* Nucleus */}
          <g transform="translate(200, 100)">
            <circle cx="0" cy="0" r="25" fill="url(#nucleusGrad)" filter="url(#glowAtom)" />
            
            {/* Protons & Neutrons visualization */}
            {[...Array(Math.min(protons, 4))].map((_, i) => (
              <circle
                key={`p${i}`}
                cx={-8 + (i % 2) * 16}
                cy={-8 + Math.floor(i / 2) * 16}
                r="6"
                fill="#FF6B6B"
              />
            ))}
            {[...Array(Math.min(neutrons, 4))].map((_, i) => (
              <circle
                key={`n${i}`}
                cx={-4 + (i % 2) * 8}
                cy={-4 + Math.floor(i / 2) * 8}
                r="4"
                fill="#868E96"
              />
            ))}
            
            {/* Nucleus label */}
            <text x="0" y="45" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">
              {elementNames[protons] || 'X'} ({protons}p, {neutrons}n)
            </text>
          </g>

          {/* Electrons */}
          {isAnimating && [...Array(Math.min(electrons, 8))].map((_, i) => {
            const orbit = i < 2 ? 0 : i < 8 ? 1 : 2;
            const radius = [60, 85, 110][orbit];
            const angle = (i * 137.5) % 360;
            
            return (
              <g key={i}>
                <circle
                  cx="200"
                  cy="100"
                  r="5"
                  fill="#4DABF7"
                  filter="url(#glowAtom)"
                >
                  <animateMotion
                    dur={`${2 + orbit}s`}
                    repeatCount="indefinite"
                    begin={`${i * 0.3}s`}
                  >
                    <mpath href={`#orbit${orbit}`} />
                  </animateMotion>
                </circle>
                <path
                  id={`orbit${orbit}`}
                  d={`M ${200 - radius} 100 A ${radius} ${radius * 0.4} 0 1 1 ${200 + radius} 100 A ${radius} ${radius * 0.4} 0 1 1 ${200 - radius} 100`}
                  fill="none"
                  transform={`rotate(${orbit * 60} 200 100)`}
                />
              </g>
            );
          })}

          {/* Legend */}
          <g transform="translate(20, 20)">
            <circle cx="8" cy="0" r="5" fill="#FF6B6B" />
            <text x="20" y="4" fontSize="10" fill="white">Proton (+)</text>
            
            <circle cx="8" cy="18" r="5" fill="#868E96" />
            <text x="20" y="22" fontSize="10" fill="white">Neutron (0)</text>
            
            <circle cx="8" cy="36" r="5" fill="#4DABF7" />
            <text x="20" y="40" fontSize="10" fill="white">Electron (-)</text>
          </g>

          {/* Mass Number */}
          <g transform="translate(320, 25)">
            <rect x="0" y="0" width="70" height="40" rx="6" fill="rgba(255,255,255,0.1)" />
            <text x="35" y="18" textAnchor="middle" fontSize="10" fill="#aaa">Mass Number</text>
            <text x="35" y="34" textAnchor="middle" fontSize="16" fill="white" fontWeight="bold">{massNumber}</text>
          </g>
        </svg>

        {/* Top UI */}
        <div className="absolute top-2 left-2 bg-white/10 backdrop-blur-sm rounded-lg px-3 py-1.5">
          <div className="text-lg font-bold text-white">Atom Structure</div>
        </div>

        <div className="absolute top-2 right-2 flex space-x-1.5">
          <button onClick={() => setIsAnimating(!isAnimating)} className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30">
            {isAnimating ? '⏸️' : '▶️'}
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30">
            <Maximize2 className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-50 border-t border-gray-100">
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-3 space-y-2">
            <div className="flex items-center justify-center py-2 bg-white rounded-lg border border-gray-100">
              <span className="text-red-500 font-bold">{protons}p</span>
              <span className="text-gray-400 mx-2">+</span>
              <span className="text-gray-500 font-bold">{neutrons}n</span>
              <span className="text-gray-400 mx-2">=</span>
              <span className="text-purple-600 font-bold text-lg">{massNumber}</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Protons</span>
                  <span className="font-medium text-red-500">{protons}</span>
                </div>
                <input
                  type="range" min="1" max="8" value={protons}
                  onChange={(e) => { setProtons(Number(e.target.value)); setElectrons(Number(e.target.value)); }}
                  className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer accent-red-500"
                />
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Neutrons</span>
                  <span className="font-medium text-gray-600">{neutrons}</span>
                </div>
                <input
                  type="range" min="0" max="10" value={neutrons}
                  onChange={(e) => setNeutrons(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer accent-gray-500"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ChemistryAtomScene;









